from __future__ import annotations

from app.domain import FullUserInput
from app.llm.abacus_llm import abacus_llm_client
from app.llm.llm_client import ChatPrompt


class RefinementEngine:
    def __init__(self) -> None:
        self._llm = abacus_llm_client

    async def refine_master(self, user_input: FullUserInput, draft_sop: str) -> str:
        """
        Stage 5 – global coherence and depth enhancer.

        Takes the drafted SOP and performs a single global pass to:
        - increase intellectual density,
        - improve transitions,
        - enforce school-centric gravity,
        - tighten word count while preserving core content.
        """
        pt = user_input.target_program
        ra = user_input.research_alignment

        system = (
            "You are refining a graduate Statement of Purpose that is already structured "
            "around research fit. Your job is to improve clarity, intellectual density, "
            "and coherence, NOT to change the applicant's story or add new facts. "
            "Keep the SOP school-centric and research-focused, avoid clichés, and do "
            "not exceed roughly the original length by more than 10%."
        )

        context_lines: list[str] = [
            f"University: {pt.university_name}",
            f"Degree type: {pt.degree_type}",
            f"Department: {pt.department or 'N/A'}",
        ]
        if ra and ra.intended_research_area:
            context_lines.append(f"Intended research area: {ra.intended_research_area}")

        user_prompt = "\n".join(
            context_lines
            + [
                "",
                "Here is the current full SOP draft between <SOP> tags. "
                "Return ONLY the refined SOP text, with no explanations.",
                "<SOP>",
                draft_sop,
                "</SOP>",
            ]
        )

        response = await self._llm.chat(
            ChatPrompt(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ]
            )
        )
        refined = response["content"]
        usage = response["usage"]
        return refined.strip(), usage["total_tokens"]

