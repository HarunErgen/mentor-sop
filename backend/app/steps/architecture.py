from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from app.steps.alignment import AlignmentMap
from app.domain import FullUserInput
from app.steps.positioning import ResearchPositioningBrief


class SOPSectionName(str, Enum):
    INTRO = "introductory_frame_narrative"
    WHY_PROGRAM = "why_this_program"
    WHY_YOU = "why_you_are_qualified"
    CLOSING = "closing_frame_narrative"


class SOPSectionPlan(BaseModel):
    name: SOPSectionName
    purpose: str
    key_claims: List[str]
    evidence: List[str]
    transition_logic: Optional[str] = None
    emotional_arc: Optional[str] = None


class SOPArchitecturePlan(BaseModel):
    sections: List[SOPSectionPlan]


class ArchitectureBuilder:
    def build_plan(
        self,
        user_input: FullUserInput,
        alignment_map: AlignmentMap,
        positioning_brief: ResearchPositioningBrief,
    ) -> SOPArchitecturePlan:
        """
        Deterministic, non-LLM outline of the 4-section SOP structure
        based on the alignment map, positioning brief, and user input.
        """
        sections: List[SOPSectionPlan] = []
        tp = user_input.personal_turning_points
        ra = user_input.research_alignment

        # 1. Introductory frame narrative
        intro_evidence = []
        if tp and (tp.direction_moment or tp.intellectual_shift or tp.failure_or_obstacle):
            intro_evidence.append("Personal turning point connected to the ongoing trajectory.")
        else:
            intro_evidence.append("Overview of applicant's core motivation.")

        if ra and ra.research_problems:
            intro_evidence.append("Reference to at least one research problem of interest.")

        intro_claims = [
            "You are motivated by specific goals or concrete problems, not generic interest.",
            "Your intellectual path naturally leads toward the target program."
        ]

        sections.append(
            SOPSectionPlan(
                name=SOPSectionName.INTRO,
                purpose="Introduce the applicant through a concise opening statement or defining moment.",
                key_claims=intro_claims,
                evidence=intro_evidence,
                transition_logic="Lead from the opening into a clear statement of overarching direction.",
                emotional_arc="Curiosity and focus, avoiding melodrama.",
            )
        )

        # 2. Why this program
        why_program_evidence = []
        if alignment_map.core_overlap_area:
            why_program_evidence.append("Core overlap area from the alignment map.")
        if alignment_map.research_synergy_points or alignment_map.shared_problems:
            why_program_evidence.append("Synergy points and shared problems with the lab's work.")
        if user_input.target_program.target_professors:
            why_program_evidence.append("Specific connections to targeted professors' work.")

        if not why_program_evidence:
            why_program_evidence.append("Alignment with the university and program resources.")

        why_program_claims = [
            "The program's themes directly support your goals.",
        ]
        if user_input.target_program.target_professors or user_input.target_program.labs:
            why_program_claims.append("Specific professors or labs are natural homes for your questions.")

        sections.append(
            SOPSectionPlan(
                name=SOPSectionName.WHY_PROGRAM,
                purpose="Anchor the narrative around the program and specific resources or advisors.",
                key_claims=why_program_claims,
                evidence=why_program_evidence,
                transition_logic="Move from general program fit into specific lab/professor/resource connections.",
                emotional_arc="Conviction and respect for the program's offerings.",
            )
        )

        # 3. Why you are qualified
        sections.append(
            SOPSectionPlan(
                name=SOPSectionName.WHY_YOU,
                purpose="Demonstrate that you can execute on the proposed direction.",
                key_claims=[
                    "You have the technical preparation to contribute quickly.",
                    "Your track record shows relevant experience.",
                ],
                evidence=[
                    "Academic background and relevant coursework.",
                    "Projects, publications, or professional experience.",
                ],
                transition_logic="Connect past preparation directly to upcoming goals.",
                emotional_arc="Competence and grounded confidence.",
            )
        )

        # 4. Closing frame narrative
        sections.append(
            SOPSectionPlan(
                name=SOPSectionName.CLOSING,
                purpose="Close the loop with a forward-looking vision tied to the program.",
                key_claims=[
                    "Your long-term trajectory aligns with the program value.",
                    "Joining this program is a natural next step.",
                ],
                evidence=[
                    "Long-term career goal drawn from user input (if available).",
                    "Reinforcement of the opening direction.",
                ],
                transition_logic="Echo the opening frame while pointing toward future growth at the program.",
                emotional_arc="Calm ambition and clarity about next steps.",
            )
        )

        return SOPArchitecturePlan(sections=sections)

