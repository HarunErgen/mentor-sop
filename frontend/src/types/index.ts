export const DegreeType = {
  MS: "MS",
  MS_THESIS: "MS Thesis",
  MS_COURSE: "MS Course",
  PHD: "PhD",
  POST_DOC: "Post-Doc",
  MENG: "MEng",
  MENG_THESIS: "MEng Thesis",
  MENG_COURSE: "MEng Course",
  MENG_PROJECT: "MEng Project",
  OTHER: "Other",
} as const;
export type DegreeType = (typeof DegreeType)[keyof typeof DegreeType];

export const LanguageComplexity = {
  BASIC: "basic",
  NORMAL: "normal",
  ADVANCED: "advanced",
} as const;
export type LanguageComplexity = (typeof LanguageComplexity)[keyof typeof LanguageComplexity];

export interface ProfessorPublication {
  title: string;
  publication_date?: string | null;
  publication_url?: string | null;
  abstract?: string | null;
  description?: string | null;
}

export interface Professor {
  name: string;
  research_areas?: string[] | null;
  research_projects?: string[] | null;
  publications?: ProfessorPublication[] | null;
  other_relevant_info?: string | null;
}

export interface TargetProgram {
  university_name: string;
  degree_type: DegreeType;
  department?: string | null;
  labs: string[];
  target_professors?: Professor[] | null;
}

export interface ResearchAlignmentInput {
  intended_research_area?: string | null;
  research_problems: string[];
  why_these_problems_matter?: string | null;
  long_term_goal?: string | null;
}

export interface AcademicBackground {
  school_name?: string | null;
  undergraduate_degree?: string | null;
  gpa?: string | null;
  relevant_coursework: string[];
  research_projects: string[];
  publications: string[];
}

export interface ProfessionalExperienceItem {
  title: string;
  company?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  description?: string | null;
}

export interface PersonalTurningPoints {
  direction_moment?: string | null;
  failure_or_obstacle?: string | null;
  intellectual_shift?: string | null;
}

export interface WritingPreferences {
  language_complexity?: LanguageComplexity | null;
  use_em_dash: boolean;
  target_word_count?: number | null;
  extra_instructions?: string | null;
}

export interface FullUserInput {
  target_program: TargetProgram;
  research_alignment?: ResearchAlignmentInput | null;
  academic_background?: AcademicBackground | null;
  professional_experiences: ProfessionalExperienceItem[];
  personal_turning_points?: PersonalTurningPoints | null;
  writing_preferences?: WritingPreferences | null;
}

// API responses
export interface JobCreateResponse {
  job_id: string;
}

export type JobStatus = "pending" | "running" | "completed" | "failed";

export interface ResearchAlignmentSummary {
  why_school_fits_you?: string | null;
  why_you_fit_lab?: string | null;
}

export interface StrategicPositioningInsight {
  differentiation_angle?: string | null;
  intellectual_identity?: string | null;
  strength_profile?: string | null;
}

export interface RiskAssessment {
  weak_areas: string[];
  suggestions?: string | null;
}

export interface SOPReport {
  research_alignment_summary?: ResearchAlignmentSummary | null;
  strategic_positioning_insight?: StrategicPositioningInsight | null;
  master_sop?: string | null;
  sections: string[];
  school_specific_sops: string[];
  risk_assessment?: RiskAssessment | null;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  current_step: string;
  result?: SOPReport | null;
  error?: string | null;
  created_at?: string | null;
}

export interface JobSummary {
  job_id: string;
  status: JobStatus;
  current_step: string;
  university_name: string;
  degree_type: string;
  created_at: string;
}

export interface ListJobsResponse {
  jobs: JobSummary[];
}
