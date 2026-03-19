from __future__ import annotations

import json

from pydantic import BaseModel

from app.domain import FullUserInput, ResearchAlignmentSummary
from app.llm.abacus_llm import abacus_llm_client
from app.llm.llm_client import ChatPrompt


class AlignmentMap(BaseModel):
    core_overlap_area: str | None = None
    research_synergy_points: list[str] = []
    shared_problems: list[str] = []
    technical_alignment: list[str] = []
    differentiation_angle: str | None = None
    risk_flags: list[str] = []


class AlignmentEngine:
    def __init__(self) -> None:
        self._llm = abacus_llm_client

    async def run(self, user_input: FullUserInput) -> AlignmentMap:
        """
        Stage 1 – Alignment Engine.

        Uses the LLM to produce a structured AlignmentMap focused strictly
        on user-provided descriptions of professors, labs, and interests.
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
            return AlignmentMap()

        system = (
            "You are helping a graduate applicant reason about research fit. "
            "ONLY use the professor, lab, and problem descriptions provided below. "
            "Do NOT invent or hallucinate any new facts about professors, labs, "
            "or universities. If something is unclear or missing, mark it as a "
            "risk flag instead of guessing."
        )

        context_lines = [
            f"University: {pt.university_name}",
            f"Degree type: {pt.degree_type}",
            f"Department: {pt.department or 'N/A'}",
        ]

        if pt.target_professors:
            prof_lines: list[str] = []
            for prof in pt.target_professors:
                line_parts: list[str] = [prof.name]
                if prof.research_areas:
                    line_parts.append("areas: " + "; ".join(prof.research_areas))
                if prof.research_projects:
                    line_parts.append("projects: " + "; ".join(prof.research_projects))
                if prof.other_relevant_info:
                    line_parts.append("notes: " + prof.other_relevant_info)
                prof_lines.append(" | ".join(line_parts))
            context_lines.append("Target professors (from user):")
            context_lines.extend(f"- {p}" for p in prof_lines)

        if pt.labs:
            context_lines.append("Target labs: " + ", ".join(pt.labs))

        if ra:
            if ra.intended_research_area:
                context_lines.append(f"Intended research area: {ra.intended_research_area}")
            if ra.research_problems:
                context_lines.append("Applicant research problems of interest: " + "; ".join(ra.research_problems))
            if ra.why_these_problems_matter:
                context_lines.append(f"Why these problems matter: {ra.why_these_problems_matter}")

        instructions = (
            "From this information, identify the intellectual intersection between "
            "the applicant and the target program/lab.\n"
            "Return a JSON object with the following keys exactly:\n"
            "{\n"
            '  "core_overlap_area": string | null,\n'
            '  "research_synergy_points": string[],\n'
            '  "shared_problems": string[],\n'
            '  "technical_alignment": string[],\n'
            '  "differentiation_angle": string | null,\n'
            '  "risk_flags": string[]\n'
            "}\n"
            "Do not include any extra keys or commentary. Output ONLY valid JSON."
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
            raise ValueError(f"Failed to parse alignment JSON from LLM: {exc} - raw: {raw!r}") from exc

        return AlignmentMap(**data), usage["total_tokens"]

    async def summarize_for_report(self, alignment_map: AlignmentMap) -> ResearchAlignmentSummary:
        """
        Convert an AlignmentMap into a user-facing summary structure.
        """
        school_fit = None
        lab_fit = None

        if alignment_map.core_overlap_area:
            school_fit = f"Your work sits at the core overlap area of {alignment_map.core_overlap_area}."

        if alignment_map.research_synergy_points:
            lab_fit = (
                "You share interest in the following research problems: "
                + "; ".join(alignment_map.research_synergy_points)
            )

        return ResearchAlignmentSummary(
            why_school_fits_you=school_fit,
            why_you_fit_lab=lab_fit,
        )

