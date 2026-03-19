from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.domain import SOPReport


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStep(str, Enum):
    PENDING = "pending"
    ALIGNMENT = "alignment"
    ALIGNMENT_SUMMARY = "alignment_summary"
    POSITIONING_BRIEF = "positioning_brief"
    POSITIONING_INSIGHT = "positioning_insight"
    ARCHITECTURE = "architecture"
    DRAFTING_INTRO = "drafting_intro"
    DRAFTING_WHY_PROGRAM = "drafting_why_program"
    DRAFTING_WHY_YOU = "drafting_why_you"
    DRAFTING_CLOSING = "drafting_closing"
    COMBINING = "combining"
    COMPLETED = "completed"


class JobCreateResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    current_step: str = Field(..., description="Pipeline step in progress or last completed")
    result: Optional[SOPReport] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None


class JobSummary(BaseModel):
    job_id: str
    status: JobStatus
    current_step: str
    university_name: str
    degree_type: str
    created_at: datetime


class ListJobsResponse(BaseModel):
    jobs: list[JobSummary]
