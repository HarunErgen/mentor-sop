from __future__ import annotations

from typing import Awaitable, Callable, List

from app.steps.alignment import AlignmentMap
from app.steps.architecture import SOPArchitecturePlan, SOPSectionName
from app.domain import FullUserInput, LanguageComplexity, WritingPreferences
from app.llm.llm_client import ChatPrompt, LLMClient
from app.steps.positioning import ResearchPositioningBrief
from app.llm.abacus_llm import abacus_llm_client

class SOPSectionDraft:
    def __init__(self, name: SOPSectionName, text: str) -> None:
        self.name = name
        self.text = text


class DraftingEngine:
    def __init__(self) -> None:
        self._llm = abacus_llm_client

    def _target_words_per_section(self, prefs: WritingPreferences | None) -> int:
        if prefs is None or prefs.target_word_count is None:
            return 200
        # simple even split across four sections
        return max(80, prefs.target_word_count // 4)

    def _system_message_for_prefs(self, prefs: WritingPreferences | None) -> str:
        """
        Shape the global system behavior based on writing preferences.

        In particular, avoid forcing highly complex prose when the user
        explicitly asks for basic language.
        """
        base = (
            "You are an expert graduate admissions writing assistant following a four-part, "
            "WriteIvy-style SOP structure (introductory frame, why this program, why you "
            "are qualified, closing frame). "
            "Each section you draft has a specific purpose, transition logic, and emotional arc "
            "that MUST be respected. "
            "Write school-centric, research-aligned SOP sections that are tightly grounded in the "
            "user-provided details. "
            "Avoid generic statements, clichés, and resume-style listing. Focus on the intellectual "
            "intersection between the applicant and the program, citing concrete details such as "
            "courses, projects, research problems, professors, labs, and publications whenever "
            "they are available. "
        )

        if not prefs or not prefs.language_complexity:
            # Default to clear but reasonably sophisticated prose.
            return (
                base
                + "Use clear, professional academic English with moderate complexity. "
                "Prefer concrete details over buzzwords. "
                "Avoid boilerplate phrases such as 'I have always been passionate' or "
                "'cutting-edge research environment'. "
                "When multiple specific details are provided (e.g., professors, labs, projects), "
                "choose the 2–4 most relevant ones for each section instead of listing everything."
            )

        complexity = prefs.language_complexity.value.lower().strip()
        if complexity == LanguageComplexity.BASIC.value:
            return (
                base
                + "Use simple, accessible English. "
                "Prefer short sentences, common vocabulary, and B2-level language. "
                "Avoid heavy jargon, ornate phrasing, and unnecessary clauses. "
                "Even with simple language, always anchor the writing in specific details "
                "from the applicant's background, research problems, and target program."
            )
        if complexity == LanguageComplexity.NORMAL.value:
            return (
                base
                + "Use a narrative tone with smooth transitions, "
                "but keep sentences readable and avoid purple prose. "
                "Weave in concrete details (courses, projects, professors, labs) as part of the "
                "story rather than listing them mechanically."
            )
        if complexity == LanguageComplexity.ADVANCED.value:
            return (
                base
                + "Use advanced, technical English with complex sentence structures. "
                "Prefer long sentences, complex vocabulary, and C2-level language. "
                "Avoid heavy jargon, ornate phrasing, and unnecessary clauses. "
                "Prioritize precise, research-specific detail over grandiose claims."
            )

        # Fallback for other custom descriptors.
        return (
            base
            + f"Follow this style description from the user: '{prefs.language_complexity}'. "
            "When in doubt, choose clarity over complexity. "
            "Always ground claims in specific facts from the provided data instead of vague praise."
        )

    async def draft_sections(
        self,
        plan: SOPArchitecturePlan,
        user_input: FullUserInput,
        alignment_map: AlignmentMap,
        positioning_brief: ResearchPositioningBrief,
        *,
        on_section_start: Callable[[SOPSectionName], Awaitable[None]] | None = None,
    ) -> List[SOPSectionDraft]:
        """
        LLM-backed drafting: generate each section independently using
        the alignment map, positioning brief, and architecture plan.
        """
        prefs = user_input.writing_preferences
        target_words = self._target_words_per_section(prefs)

        drafts: List[SOPSectionDraft] = []
        cumulative_text_parts: List[str] = []
        total_tokens = 0
        for section in plan.sections:
            if on_section_start is not None:
                await on_section_start(section.name)
            system = self._system_message_for_prefs(prefs)

            user_context_parts: List[str] = []

            # PROGRAM DETAILS BLOCK
            pt = user_input.target_program
            program_lines: List[str] = [
                "PROGRAM DETAILS:",
                f"- University: {pt.university_name}",
                f"- Degree type: {pt.degree_type}",
                f"- Department or program: {pt.department or 'N/A'}",
            ]
            if pt.labs:
                program_lines.append("- Target labs: " + "; ".join(pt.labs))
            if pt.target_professors:
                program_lines.append("- Target professors (from user):")
                for prof in pt.target_professors:
                    prof_bits: List[str] = [prof.name]
                    if prof.research_areas:
                        prof_bits.append("areas: " + "; ".join(prof.research_areas))
                    if prof.research_projects:
                        prof_bits.append("projects: " + "; ".join(prof.research_projects))
                    if prof.publications:
                        pub_summaries: List[str] = []
                        for pub in prof.publications[:3]:
                            parts: List[str] = [pub.title]
                            if pub.publication_date:
                                parts.append(pub.publication_date)
                            pub_summaries.append(" – ".join(parts))
                        prof_bits.append("publications: " + "; ".join(pub_summaries))
                    if prof.other_relevant_info:
                        prof_bits.append("notes: " + prof.other_relevant_info)
                    program_lines.append("  • " + " | ".join(prof_bits))
            user_context_parts.extend(program_lines)

            # RESEARCH ALIGNMENT BLOCK
            ra = user_input.research_alignment
            ra_lines: List[str] = ["", "RESEARCH ALIGNMENT:"]
            if ra:
                if ra.intended_research_area:
                    ra_lines.append(f"- Intended research area: {ra.intended_research_area}")
                if ra.research_problems:
                    ra_lines.append("- Research problems of interest:")
                    for p in ra.research_problems:
                        ra_lines.append(f"  • {p}")
                if ra.why_these_problems_matter:
                    ra_lines.append(f"- Why these problems matter: {ra.why_these_problems_matter}")
                if ra.long_term_goal:
                    ra_lines.append(f"- Long-term goal: {ra.long_term_goal}")
            else:
                ra_lines.append("- (No explicit research alignment provided.)")
            user_context_parts.extend(ra_lines)

            # ALIGNMENT MAP + POSITIONING BRIEF BLOCK
            alignment_lines: List[str] = ["", "ALIGNMENT AND POSITIONING:"]
            if alignment_map.core_overlap_area:
                alignment_lines.append(f"- Core overlap area: {alignment_map.core_overlap_area}")
            if alignment_map.research_synergy_points:
                alignment_lines.append(
                    "- Research synergy points: " + "; ".join(alignment_map.research_synergy_points)
                )
            if alignment_map.shared_problems:
                alignment_lines.append("- Shared problems with lab: " + "; ".join(alignment_map.shared_problems))
            if alignment_map.technical_alignment:
                alignment_lines.append(
                    "- Technical alignment highlights: " + "; ".join(alignment_map.technical_alignment)
                )
            if alignment_map.differentiation_angle:
                alignment_lines.append(f"- Differentiation angle: {alignment_map.differentiation_angle}")
            if alignment_map.risk_flags:
                alignment_lines.append("- Risk flags or gaps: " + "; ".join(alignment_map.risk_flags))
            if positioning_brief.thesis_direction:
                alignment_lines.append(f"- Thesis direction: {positioning_brief.thesis_direction}")
            if positioning_brief.narrative_hook:
                alignment_lines.append(f"- Narrative hook: {positioning_brief.narrative_hook}")
            user_context_parts.extend(alignment_lines)

            # ACADEMIC BACKGROUND BLOCK
            ab_lines: List[str] = ["", "ACADEMIC BACKGROUND:"]
            if user_input.academic_background:
                ab = user_input.academic_background
                if ab.school_name:
                    ab_lines.append(f"- Institution: {ab.school_name}")
                if ab.undergraduate_degree:
                    ab_lines.append(f"- Degree: {ab.undergraduate_degree}")
                if ab.gpa:
                    ab_lines.append(f"- GPA: {ab.gpa}")
                if ab.relevant_coursework:
                    ab_lines.append("- Relevant coursework:")
                    for c in ab.relevant_coursework:
                        ab_lines.append(f"  • {c}")
                if ab.research_projects:
                    ab_lines.append("- Academic research projects:")
                    for proj in ab.research_projects:
                        ab_lines.append(f"  • {proj}")
                if ab.publications:
                    ab_lines.append("- Publications:")
                    for pub in ab.publications:
                        ab_lines.append(f"  • {pub}")
            else:
                ab_lines.append("- (No academic background details provided.)")
            user_context_parts.extend(ab_lines)

            # PROFESSIONAL EXPERIENCE BLOCK
            pe_lines: List[str] = ["", "PROFESSIONAL EXPERIENCE:"]
            if user_input.professional_experiences:
                for exp in user_input.professional_experiences:
                    line = f"- {exp.title}"
                    if exp.company:
                        line += f" at {exp.company}"
                    date_bits: List[str] = []
                    if exp.start_date:
                        date_bits.append(exp.start_date)
                    if exp.end_date:
                        date_bits.append(exp.end_date)
                    if date_bits:
                        line += " (" + " – ".join(date_bits) + ")"
                    pe_lines.append(line)
                    if exp.description:
                        pe_lines.append(f"  • Key outcomes: {exp.description}")
            else:
                pe_lines.append("- (No professional experience details provided.)")
            user_context_parts.extend(pe_lines)

            # PERSONAL TURNING POINTS BLOCK
            ptp_lines: List[str] = ["", "PERSONAL TURNING POINTS:"]
            if user_input.personal_turning_points:
                tp = user_input.personal_turning_points
                if tp.direction_moment:
                    ptp_lines.append(f"- Direction moment: {tp.direction_moment}")
                if tp.failure_or_obstacle:
                    ptp_lines.append(f"- Failure or obstacle: {tp.failure_or_obstacle}")
                if tp.intellectual_shift:
                    ptp_lines.append(f"- Intellectual shift: {tp.intellectual_shift}")
            else:
                ptp_lines.append("- (No personal turning points provided.)")
            user_context_parts.extend(ptp_lines)

            style_bits: List[str] = []
            if prefs and prefs.language_complexity:
                style_bits.append(f"Language complexity preference: {prefs.language_complexity}.")
            if prefs and not prefs.use_em_dash:
                style_bits.append("Avoid using em dashes.")
            if prefs and prefs.target_word_count:
                style_bits.append(
                    f"Global target word count: approximately {prefs.target_word_count} words total; "
                    "prioritize depth over breadth when space is limited."
                )
            if prefs and prefs.extra_instructions:
                style_bits.append(
                    "Treat the following as hard style constraints from the user: "
                    f"{prefs.extra_instructions}."
                )

            if cumulative_text_parts:
                style_bits.append(
                    "Previously drafted sections are provided below between <PREVIOUS_SECTIONS> tags. "
                    "Maintain a consistent voice and do NOT contradict earlier content. "
                    "Avoid reusing the exact same anecdotes, sentences, or lists of details unless "
                    "you are adding genuinely new nuance."
                )

            transition_logic = section.transition_logic or ""
            emotional_arc = section.emotional_arc or ""

            extra_section_rules: List[str] = []
            if section.name == SOPSectionName.INTRO:
                intro_rules = []
                tp = user_input.personal_turning_points
                if tp and (tp.direction_moment or tp.intellectual_shift or tp.failure_or_obstacle):
                    intro_rules.append("Prioritize the personal direction moment or intellectual shift as the opening frame.")
                intro_rules.append("Quickly connect the opening to the overarching goal or research direction.")
                ra = user_input.research_alignment
                if ra and ra.research_problems:
                    intro_rules.append("Explicitly reference at least one concrete research problem or area from the RESEARCH ALIGNMENT block.")
                intro_rules.append("Do not list the full CV here.")
                extra_section_rules.append(" ".join(intro_rules))
            elif section.name == SOPSectionName.WHY_PROGRAM:
                why_prog_rules = []
                if user_input.target_program.target_professors or user_input.target_program.labs:
                    why_prog_rules.append("Name at least one or two specific professors, labs, or research themes from the PROGRAM DETAILS block and connect them to the applicant's goals.")
                why_prog_rules.append("Focus on concrete overlaps between the applicant and the program. Avoid generic praise of the university.")
                extra_section_rules.append(" ".join(why_prog_rules))
            elif section.name == SOPSectionName.WHY_YOU:
                extra_section_rules.append(
                    "Select two to three concrete experiences from ACADEMIC BACKGROUND or PROFESSIONAL EXPERIENCE that "
                    "demonstrate readiness (courses, projects, research, or industry work). "
                    "Tie each experience to skills or knowledge needed for the future direction."
                )
            elif section.name == SOPSectionName.CLOSING:
                extra_section_rules.append(
                    "Echo the opening frame in a forward-looking way, and connect the "
                    "long-term goal to what you hope to do at this program. "
                    "End with calm, grounded ambition rather than hype."
                )

            extra_rules_text = " ".join(extra_section_rules)

            section_instructions = (
                f"You are drafting the section '{section.name.value}'. "
                f"Purpose: {section.purpose}. "
                f"Key claims to support: {'; '.join(section.key_claims)}. "
                f"Evidence to weave in (from the data blocks above): {'; '.join(section.evidence)}. "
                f"Transition logic: {transition_logic} "
                f"Emotional arc: {emotional_arc} "
                f"{extra_rules_text} "
                f"Target around {target_words} words. "
                "Write as a continuous, polished paragraph or two without headings or bullet lists. "
                "Explicitly reference at least two to three concrete details from the data blocks above "
                "instead of speaking in generic terms. "
                "Use a level of vocabulary and sentence complexity that matches the user's preference."
            )
            
            prompt_parts = user_context_parts + style_bits
            if cumulative_text_parts:
                prompt_parts.extend(
                    [
                        "",
                        "<PREVIOUS_SECTIONS>",
                        "\n\n".join(cumulative_text_parts),
                        "</PREVIOUS_SECTIONS>",
                    ]
                )
            prompt_parts.append(section_instructions)

            user_prompt = "\n".join(prompt_parts)

            response = await self._llm.chat(
                ChatPrompt(
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_prompt},
                    ]
                )
            )
            
            llm_output = response["content"]
            usage = response["usage"]
            total_tokens += usage["total_tokens"]

            section_text = llm_output.strip()
            drafts.append(SOPSectionDraft(name=section.name, text=section_text))
            cumulative_text_parts.append(section_text)

        return drafts, total_tokens

    def combine_into_master(self, drafts: List[SOPSectionDraft]) -> str:
        ordered = sorted(
            drafts,
            key=lambda d: [
                SOPSectionName.INTRO,
                SOPSectionName.WHY_PROGRAM,
                SOPSectionName.WHY_YOU,
                SOPSectionName.CLOSING,
            ].index(d.name),
        )
        return "\n\n".join(d.text for d in ordered)
