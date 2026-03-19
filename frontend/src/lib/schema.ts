import { z } from "zod";

const degreeTypeEnum = z.enum([
  "MS",
  "MS Thesis",
  "MS Course",
  "PhD",
  "Post-Doc",
  "MEng",
  "MEng Thesis",
  "MEng Course",
  "MEng Project",
  "Other",
]);

const languageComplexityEnum = z.enum(["basic", "normal", "advanced"]);

const professorPublicationSchema = z.object({
  title: z.string().optional().nullable(),
  publication_date: z.string().optional().nullable(),
  publication_url: z.string().url().optional().nullable().or(z.literal("")),
  abstract: z.string().optional().nullable(),
  description: z.string().optional().nullable(),
});

const professorSchema = z.object({
  name: z.string().min(1, "Professor name is required"),
  research_areas: z.array(z.string()).optional().nullable(),
  research_projects: z.array(z.string()).optional().nullable(),
  publications: z.array(professorPublicationSchema).optional().nullable(),
  other_relevant_info: z.string().optional().nullable(),
});

const targetProgramSchema = z.object({
  university_name: z.string().min(1, "University name is required"),
  degree_type: degreeTypeEnum,
  department: z.string().optional().nullable(),
  labs: z.array(z.string()).default([]),
  target_professors: z.array(professorSchema).default([]),
});

const researchAlignmentSchema = z.object({
  intended_research_area: z.string().optional().nullable(),
  research_problems: z.array(z.string()).default([]),
  why_these_problems_matter: z.string().optional().nullable(),
  long_term_goal: z.string().optional().nullable(),
});

const academicBackgroundSchema = z.object({
  school_name: z.string().optional().nullable(),
  undergraduate_degree: z.string().optional().nullable(),
  gpa: z.string().optional().nullable(),
  relevant_coursework: z.array(z.string()).default([]),
  research_projects: z.array(z.string()).default([]),
  publications: z.array(z.string()).default([]),
});

const professionalExperienceItemSchema = z.object({
  title: z.string().min(1, "Job title is required"),
  company: z.string().optional().nullable(),
  start_date: z.string().optional().nullable(),
  end_date: z.string().optional().nullable(),
  description: z.string().optional().nullable(),
});

const personalTurningPointsSchema = z.object({
  direction_moment: z.string().optional().nullable(),
  failure_or_obstacle: z.string().optional().nullable(),
  intellectual_shift: z.string().optional().nullable(),
});

const writingPreferencesSchema = z.object({
  language_complexity: languageComplexityEnum.optional().nullable(),
  use_em_dash: z.boolean().default(true),
  target_word_count: z.number().int().positive().optional().nullable(),
  extra_instructions: z.string().optional().nullable(),
});

export const fullUserInputSchema = z.object({
  target_program: targetProgramSchema,
  research_alignment: researchAlignmentSchema,
  academic_background: academicBackgroundSchema,
  professional_experiences: z.array(professionalExperienceItemSchema).default([]),
  personal_turning_points: personalTurningPointsSchema,
  writing_preferences: writingPreferencesSchema,
});

export type FullUserInputForm = z.infer<typeof fullUserInputSchema>;

// Default form values for react-hook-form
export const defaultFullUserInput: FullUserInputForm = {
  target_program: {
    university_name: "",
    degree_type: "MS",
    department: null,
    labs: [],
    target_professors: [],
  },
  research_alignment: {
    intended_research_area: null,
    research_problems: [],
    why_these_problems_matter: null,
    long_term_goal: null,
  },
  academic_background: {
    school_name: null,
    undergraduate_degree: null,
    gpa: null,
    relevant_coursework: [],
    research_projects: [],
    publications: [],
  },
  professional_experiences: [],
  personal_turning_points: {
    direction_moment: null,
    failure_or_obstacle: null,
    intellectual_shift: null,
  },
  writing_preferences: {
    language_complexity: null,
    use_em_dash: true,
    target_word_count: null,
    extra_instructions: null,
  },
};
