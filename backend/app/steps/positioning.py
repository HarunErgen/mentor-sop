from __future__ import annotations

import json

from pydantic import BaseModel

from app.steps.alignment import AlignmentMap
from app.domain import FullUserInput, StrategicPositioningInsight
from app.llm.abacus_llm import abacus_llm_client
from app.llm.llm_client import ChatPrompt


class ResearchPositioningBrief(BaseModel):
    refined_research_questions: list[str] = []
    thesis_direction: str | None = None
    narrative_hook: str | None = None


class PositioningEngine:
    def __init__(self) -> None:
        self._llm = abacus_llm_client

    async def build_brief(self, user_input: FullUserInput, alignment_map: AlignmentMap) -> ResearchPositioningBrief:
        """
        Stage 2 – Research Positioning.

        Uses the LLM to turn the alignment map and user goals into a
        small set of concrete research questions and a thesis direction.
        """
        pt = user_input.target_program
        ra = user_input.research_alignment

        has_substantive_ra = False
        if ra:
            has_substantive_ra = bool(
                ra.intended_research_area or
                ra.research_problems or
                ra.why_these_problems_matter or
                ra.long_term_goal
            )

        if not has_substantive_ra:
            return ResearchPositioningBrief()

        system = (
            "You are designing a research agenda for a graduate applicant. "
            "Your job is to sharpen their research direction, not to rewrite "
            "their full SOP. Be specific, technically grounded, and concise."
        )

        context_lines = [
            f"University: {pt.university_name}",
            f"Degree type: {pt.degree_type}",
            f"Department: {pt.department or 'N/A'}",
        ]
        if ra:
            if ra.intended_research_area:
                context_lines.append(f"Intended research area: {ra.intended_research_area}")
            if ra.research_problems:
                context_lines.append("Raw research problems list: " + "; ".join(ra.research_problems))
            if ra.why_these_problems_matter:
                context_lines.append(f"Why these problems matter: {ra.why_these_problems_matter}")
            if ra.long_term_goal:
                context_lines.append(f"Long-term goal: {ra.long_term_goal}")

        if alignment_map.core_overlap_area:
            context_lines.append(f"Core overlap area (from alignment engine): {alignment_map.core_overlap_area}")
        if alignment_map.research_synergy_points:
            context_lines.append(
                "Research synergy points (from alignment engine): "
                + "; ".join(alignment_map.research_synergy_points)
            )

        instructions = (
            "Based on this information, produce a tight research positioning brief.\n"
            "Return a JSON object with keys:\n"
            "{\n"
            '  \"refined_research_questions\": string[] (3–5 concise, technically meaningful questions),\n'
            '  \"thesis_direction\": string | null,\n'
            '  \"narrative_hook\": string | null\n'
            "}\n"
            "Refine and cluster the raw problems instead of repeating them verbatim. "
            "Focus on problems that clearly intersect with the described lab/program. "
            "Output ONLY valid JSON, no commentary."
        )

        user_prompt = "\n".join(context_lines + ["", instructions])

        response = await self._llm.chat(
            ChatPrompt(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ]
            )
        )
        raw = response["content"]
        usage = response["usage"]

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse positioning JSON from LLM: {exc} - raw: {raw!r}") from exc

        return ResearchPositioningBrief(**data), usage["total_tokens"]

    async def to_insight(self, brief: ResearchPositioningBrief) -> StrategicPositioningInsight:
        """
        Convert a ResearchPositioningBrief into the higher-level
        StrategicPositioningInsight used in the public report.
        """
        differentiation_angle = None
        intellectual_identity = None
        strength_profile = None

        if brief.thesis_direction:
            differentiation_angle = f"You bring a clear thesis direction: {brief.thesis_direction}"

        if brief.narrative_hook:
            intellectual_identity = f"Your intellectual identity centers on {brief.narrative_hook}"

        if brief.refined_research_questions:
            strength_profile = (
                "You articulate concrete research questions such as "
                + "; ".join(brief.refined_research_questions)
            )

        return StrategicPositioningInsight(
            differentiation_angle=differentiation_angle,
            intellectual_identity=intellectual_identity,
            strength_profile=strength_profile,
        )


