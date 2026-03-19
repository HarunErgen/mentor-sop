from __future__ import annotations

from os import name
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, Field


class DegreeType(str, Enum):
    MS = "MS"
    MS_THESIS = "MS Thesis"
    MS_COURSE = "MS Course"
    PHD = "PhD"
    POST_DOC = "Post-Doc"
    MENG = "MEng"
    MENG_THESIS = "MEng Thesis"
    MENG_COURSE = "MEng Course"
    MENG_PROJECT = "MEng Project"
    OTHER = "Other"

class ProfessorPublication(BaseModel):
    title: str
    publication_date: Optional[str] = None
    publication_url: Optional[str] = None
    abstract: Optional[str] = None
    description: Optional[str] = None

class Professor(BaseModel):
    name: str
    research_areas: Optional[List[str]] = None
    research_projects: Optional[List[str]] = None
    publications: Optional[List[ProfessorPublication]] = None
    other_relevant_info: Optional[str] = None

class TargetProgram(BaseModel):
    university_name: str = Field(..., description="Target university name")
    degree_type: DegreeType = Field(..., description="Degree type, e.g., 'MS Thesis', 'MS Course', 'PhD'")
    department: Optional[str] = Field(None, description="Target department or program")
    labs: List[str] = Field(default_factory=list, description="Optional list of target labs")
    target_professors: Optional[List[Professor]] = Field(
        None, description="User-provided list of target professors"
    )

class ResearchAlignmentInput(BaseModel):
    intended_research_area: Optional[str] = None
    research_problems: List[str] = Field(default_factory=list, description="2–3 research problems of interest")
    why_these_problems_matter: Optional[str] = None
    long_term_goal: Optional[str] = None


class AcademicBackground(BaseModel):
    school_name: Optional[str] = None
    undergraduate_degree: Optional[str] = None
    gpa: Optional[str] = None
    relevant_coursework: List[str] = Field(default_factory=list)
    research_projects: List[str] = Field(default_factory=list)
    publications: List[str] = Field(default_factory=list)


class ProfessionalExperienceItem(BaseModel):
    title: str
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class PersonalTurningPoints(BaseModel):
    direction_moment: Optional[str] = Field(
        None, description="Moment that clarified research direction or intellectual focus"
    )
    failure_or_obstacle: Optional[str] = None
    intellectual_shift: Optional[str] = None


class LanguageComplexity(str, Enum):
    BASIC = "basic"
    NORMAL = "normal"
    ADVANCED = "advanced"
    

class WritingPreferences(BaseModel):
    language_complexity: Optional[LanguageComplexity] = Field(None)
    use_em_dash: bool = Field(default=True, description="Whether to use em dashes in the prose")
    target_word_count: Optional[int] = None
    extra_instructions: Optional[str] = Field(
        None, description="Any additional style or content preferences"
    )


class FullUserInput(BaseModel):
    target_program: TargetProgram
    research_alignment: Optional[ResearchAlignmentInput] = None
    academic_background: Optional[AcademicBackground] = None
    professional_experiences: List[ProfessionalExperienceItem] = Field(default_factory=list)
    personal_turning_points: Optional[PersonalTurningPoints] = None
    writing_preferences: Optional[WritingPreferences] = None


class ResearchAlignmentSummary(BaseModel):
    why_school_fits_you: Optional[str] = None
    why_you_fit_lab: Optional[str] = None


class StrategicPositioningInsight(BaseModel):
    differentiation_angle: Optional[str] = None
    intellectual_identity: Optional[str] = None
    strength_profile: Optional[str] = None


class RiskAssessment(BaseModel):
    weak_areas: List[str] = Field(default_factory=list)
    suggestions: Optional[str] = None


class SOPReport(BaseModel):
    research_alignment_summary: Optional[ResearchAlignmentSummary] = None
    strategic_positioning_insight: Optional[StrategicPositioningInsight] = None
    master_sop: Optional[str] = None
    sections: List[str] = Field(default_factory=list)
    school_specific_sops: List[str] = Field(default_factory=list)
    risk_assessment: Optional[RiskAssessment] = None
