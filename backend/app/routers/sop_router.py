import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.steps.alignment import AlignmentEngine
from app.steps.architecture import ArchitectureBuilder, SOPSectionName
from app.steps.drafting import DraftingEngine
from app.domain import FullUserInput, SOPReport
from app.jobs import JobCreateResponse, JobStatusResponse, JobStep, ListJobsResponse, JobSummary
from app.db.database import get_db
from app.llm.abacus_llm import AbacusLLMClient
from app.steps.positioning import PositioningEngine
from app.steps.refine import RefinementEngine
from app.routers.auth_router import get_current_user, SECRET_KEY, ALGORITHM, jwt, InvalidTokenError
from app.db.models import User, SOPJob, JobStatus as DBJobStatus
from sqlalchemy import select, update
from app.db.database import async_session_maker

router = APIRouter(prefix="/api/sop", tags=["sop"])

active_subscribers: dict[str, list[asyncio.Queue[dict]]] = {}

SSE_HEARTBEAT_INTERVAL = 15.0

alignment_engine = AlignmentEngine()
positioning_engine = PositioningEngine()
architecture_builder = ArchitectureBuilder()
drafting_engine = DraftingEngine()
refinement_engine = RefinementEngine()

def _section_name_to_step(section_name: SOPSectionName) -> str:
    mapping = {
        SOPSectionName.INTRO: JobStep.DRAFTING_INTRO.value,
        SOPSectionName.WHY_PROGRAM: JobStep.DRAFTING_WHY_PROGRAM.value,
        SOPSectionName.WHY_YOU: JobStep.DRAFTING_WHY_YOU.value,
        SOPSectionName.CLOSING: JobStep.DRAFTING_CLOSING.value,
    }
    return mapping.get(section_name, f"drafting_{section_name.value}")


async def run_sop_pipeline(job_id: uuid.UUID, input_data: FullUserInput, user_id: int, db_factory) -> None:
    async def set_step(step: str) -> None:
        async with db_factory() as db:
            await db.execute(
                update(SOPJob)
                .where(SOPJob.id == job_id)
                .values(status=DBJobStatus.RUNNING, current_step=step, updated_at=datetime.now(timezone.utc).replace(tzinfo=None))
            )
            await db.commit()
        
        if str(job_id) in active_subscribers:
            msg = {
                "job_id": str(job_id),
                "status": DBJobStatus.RUNNING.value,
                "current_step": step,
            }
            for q in active_subscribers[str(job_id)]:
                q.put_nowait(msg)

    try:
        await set_step(JobStep.ALIGNMENT.value)
        alignment_map, tokens = await alignment_engine.run(input_data)
        await _update_user_tokens(user_id, tokens, db_factory)

        await set_step(JobStep.ALIGNMENT_SUMMARY.value)
        alignment_summary = await alignment_engine.summarize_for_report(alignment_map)

        await set_step(JobStep.POSITIONING_BRIEF.value)
        positioning_brief, tokens = await positioning_engine.build_brief(input_data, alignment_map)
        await _update_user_tokens(user_id, tokens, db_factory)

        await set_step(JobStep.POSITIONING_INSIGHT.value)
        positioning_insight = await positioning_engine.to_insight(positioning_brief)

        await set_step(JobStep.ARCHITECTURE.value)
        architecture_plan = architecture_builder.build_plan(input_data, alignment_map, positioning_brief)

        async def on_section_start(section_name: SOPSectionName) -> None:
            await set_step(_section_name_to_step(section_name))

        drafts, tokens = await drafting_engine.draft_sections(
            architecture_plan,
            input_data,
            alignment_map,
            positioning_brief,
            on_section_start=on_section_start,
        )
        await _update_user_tokens(user_id, tokens, db_factory)

        await set_step(JobStep.COMBINING.value)
        draft_master_sop = drafting_engine.combine_into_master(drafts)

        report = SOPReport(
            research_alignment_summary=alignment_summary,
            strategic_positioning_insight=positioning_insight,
            master_sop=draft_master_sop,
            sections=[d.text for d in drafts],
            school_specific_sops=[],
            risk_assessment=None,
        )

        async with db_factory() as db:
            await db.execute(
                update(SOPJob)
                .where(SOPJob.id == job_id)
                .values(
                    status=DBJobStatus.COMPLETED,
                    current_step=JobStep.COMPLETED.value,
                    result_report=report.model_dump(),
                    updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
                )
            )
            await db.commit()

        if str(job_id) in active_subscribers:
            msg = {
                "job_id": str(job_id),
                "status": DBJobStatus.COMPLETED.value,
                "current_step": JobStep.COMPLETED.value,
                "result": report.model_dump(),
            }
            for q in active_subscribers[str(job_id)]:
                q.put_nowait(msg)

    except Exception as e:  # noqa: BLE001
        async with db_factory() as db:
            await db.execute(
                update(SOPJob)
                .where(SOPJob.id == job_id)
                .values(
                    status=DBJobStatus.FAILED,
                    error_message=str(e),
                    updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
                )
            )
            await db.commit()
        
        if str(job_id) in active_subscribers:
            msg = {
                "job_id": str(job_id),
                "status": DBJobStatus.FAILED.value,
                "error": str(e),
            }
            for q in active_subscribers[str(job_id)]:
                q.put_nowait(msg)

async def _update_user_tokens(user_id: int, tokens_used: int, db_factory) -> None:
    async with db_factory() as db:
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(tokens_used=User.tokens_used + tokens_used)
        )
        await db.commit()


@router.post("/generate", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_sop(
    input_data: FullUserInput, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> JobCreateResponse:
    if current_user.tokens_used >= current_user.token_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Token limit exceeded ({current_user.tokens_used}/{current_user.token_limit}). Please contact support or wait for monthly reset."
        )

    job_id = uuid.uuid4()
    new_job = SOPJob(
        id=job_id,
        user_id=current_user.id,
        status=DBJobStatus.PENDING,
        current_step=JobStep.PENDING.value,
        input_data=input_data.model_dump()
    )
    db.add(new_job)
    await db.commit()

    asyncio.create_task(run_sop_pipeline(job_id, input_data, current_user.id, async_session_maker))
    return JobCreateResponse(job_id=str(job_id))


@router.get("/jobs", response_model=ListJobsResponse)
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ListJobsResponse:
    result = await db.execute(
        select(SOPJob)
        .where(SOPJob.user_id == current_user.id)
        .order_by(SOPJob.created_at.desc())
    )
    jobs = result.scalars().all()
    
    summaries = []
    for job in jobs:
        input_data = job.input_data or {}
        target_program = input_data.get("target_program") or {}
        university_name = target_program.get("university_name", "Unknown")
        degree_type = target_program.get("degree_type", "Unknown")
        
        summaries.append(JobSummary(
            job_id=str(job.id),
            status=job.status,
            current_step=job.current_step,
            university_name=university_name,
            degree_type=degree_type,
            created_at=job.created_at
        ))
    
    return ListJobsResponse(jobs=summaries)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> JobStatusResponse:
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    result = await db.execute(select(SOPJob).where(SOPJob.id == job_uuid))
    job = result.scalar_one_or_none()
    
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=str(job.id),
        status=job.status.value,
        current_step=job.current_step,
        result=job.result_report,
        error=job.error_message,
        created_at=job.created_at
    )


async def _sse_event_generator(job_id: str, db_factory) -> AsyncGenerator[str, None]:
    async with db_factory() as db:
        try:
            job_uuid = uuid.UUID(job_id)
        except ValueError:
            return
        result = await db.execute(select(SOPJob).where(SOPJob.id == job_uuid))
        job = result.scalar_one_or_none()
        if job is None:
            return
        
        initial_snapshot = {
            "job_id": str(job.id),
            "status": job.status.value,
            "current_step": job.current_step,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
        if job.result_report:
            initial_snapshot["result"] = job.result_report
        if job.error_message:
            initial_snapshot["error"] = job.error_message

    queue: asyncio.Queue[dict] = asyncio.Queue()
    if job_id not in active_subscribers:
        active_subscribers[job_id] = []
    active_subscribers[job_id].append(queue)
    
    try:
        yield f"data: {json.dumps(initial_snapshot)}\n\n"
        if initial_snapshot.get("status") in (DBJobStatus.COMPLETED.value, DBJobStatus.FAILED.value):
            return
            
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=SSE_HEARTBEAT_INTERVAL)
            except asyncio.TimeoutError:
                yield ": heartbeat\n\n"
                continue
            yield f"data: {json.dumps(msg)}\n\n"
            if msg.get("status") in (DBJobStatus.COMPLETED.value, DBJobStatus.FAILED.value):
                break
    finally:
        if job_id in active_subscribers:
            if queue in active_subscribers[job_id]:
                active_subscribers[job_id].remove(queue)
            if not active_subscribers[job_id]:
                del active_subscribers[job_id]


@router.get("/jobs/{job_id}/events")
async def job_events(job_id: str, token: str) -> StreamingResponse:
    credentials_exception = HTTPException(status_code=401, detail="Invalid token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    return StreamingResponse(
        _sse_event_generator(job_id, async_session_maker),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
