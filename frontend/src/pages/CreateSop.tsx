import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { fullUserInputSchema, defaultFullUserInput, type FullUserInputForm } from "../lib/schema";
import { generateSop } from "../api/client";
import { TargetProgramForm } from "../components/TargetProgramForm";
import { ResearchAlignmentForm } from "../components/ResearchAlignmentForm";
import { AcademicBackgroundForm } from "../components/AcademicBackgroundForm";
import { ProfessionalExperiencesForm } from "../components/ProfessionalExperiencesForm";
import { PersonalTurningPointsForm } from "../components/PersonalTurningPointsForm";
import { WritingPreferencesForm } from "../components/WritingPreferencesForm";
import type { FullUserInput } from "../types";

const STEPS = [
  { title: "Target program", key: "target" },
  { title: "Research alignment", key: "research" },
  { title: "Academic background", key: "academic" },
  { title: "Professional experience", key: "professional" },
  { title: "Personal turning points", key: "personal" },
  { title: "Writing preferences", key: "writing" },
] as const;

function toApiPayload(data: FullUserInputForm): FullUserInput {
  const prefs = data.writing_preferences;
  const targetWordCount = prefs?.target_word_count;
  const target_professors = data.target_program.target_professors
    ?.filter((p) => p?.name?.trim())
    .map((p) => ({
      ...p,
      publications: p.publications?.filter((pub) => pub?.title?.trim()) ?? [],
    }));
  return {
    ...data,
    target_program: {
      ...data.target_program,
      target_professors: target_professors?.length ? target_professors : null,
    },
    writing_preferences: prefs
      ? {
        ...prefs,
        target_word_count:
          typeof targetWordCount === "number" && Number.isFinite(targetWordCount)
            ? targetWordCount
            : null,
      }
      : null,
  } as FullUserInput;
}

export default function CreateSop() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pendingData, setPendingData] = useState<FullUserInputForm | null>(null);

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
    trigger,
  } = useForm<FullUserInputForm>({
    resolver: zodResolver(fullUserInputSchema) as never,
    defaultValues: defaultFullUserInput,
  });

  const onNext = async () => {
    const fields = getStepFields(step);
    const ok = await trigger(fields as never);
    if (ok) setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };

  const onSubmit = (data: FullUserInputForm) => {
    setPendingData(data);
  };

  const handleConfirm = async (): Promise<void> => {
    if (!pendingData) return;
    setSubmitError(null);
    setIsSubmitting(true);
    const dataToSubmit = pendingData;
    setPendingData(null);
    try {
      const payload = toApiPayload(dataToSubmit);
      const res = await generateSop(payload);
      navigate(`/result/${res.job_id}`);
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Failed to start generation");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4">
          <Link to="/" className="text-lg font-semibold text-slate-900">
            MentorFit SoP
          </Link>
          <Link to="/" className="text-sm text-slate-600 hover:text-slate-900">
            Home
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8">
        <div className="mb-8 flex gap-2 overflow-x-auto pb-2">
          {STEPS.map((s, i) => (
            <button
              key={s.key}
              type="button"
              onClick={async () => {
                if (i > step) {
                  let isValid = true;
                  for (let j = 0; j < i; j++) {
                    const fields = getStepFields(j);
                    const ok = await trigger(fields as never);
                    if (!ok) {
                      isValid = false;
                      setStep(j);
                      break;
                    }
                  }
                  if (isValid) setStep(i);
                } else {
                  setStep(i);
                }
              }}
              className={`shrink-0 rounded-full px-3 py-1 text-sm font-medium ${i === step
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-200 text-slate-600 hover:bg-slate-300"
                }`}
            >
              {s.title}
            </button>
          ))}
        </div>

        <form
          onSubmit={handleSubmit(onSubmit as never)}
          className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          {step === 0 && <TargetProgramForm register={register} control={control as never} errors={errors} />}
          {step === 1 && <ResearchAlignmentForm register={register} control={control as never} />}
          {step === 2 && <AcademicBackgroundForm register={register} control={control as never} />}
          {step === 3 && (
            <ProfessionalExperiencesForm control={control as never} register={register as never} errors={errors} />
          )}
          {step === 4 && <PersonalTurningPointsForm register={register as never} />}
          {step === 5 && <WritingPreferencesForm register={register as never} />}

          {Object.keys(errors).length > 0 && (
            <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
              Please fix the errors above.
            </div>
          )}
          {submitError && (
            <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
              {submitError}
            </div>
          )}

          <div className="mt-8 flex justify-between">
            <button
              type="button"
              onClick={() => setStep((s) => Math.max(0, s - 1))}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Back
            </button>
            {step < STEPS.length - 1 ? (
              <button
                key="next-btn"
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  onNext();
                }}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
              >
                Next
              </button>
            ) : (
              <button
                key="submit-btn"
                type="submit"
                disabled={isSubmitting}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {isSubmitting ? "Starting…" : "Generate SoP"}
              </button>
            )}
          </div>
        </form>
      </main>

      {pendingData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-xl font-semibold text-slate-900">Confirm Generation</h2>
            <p className="mb-6 text-slate-600">
              Are you sure you want to generate the Statement of Purpose?
            </p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setPendingData(null)}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirm}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function getStepFields(step: number): (keyof FullUserInputForm)[] {
  switch (step) {
    case 0:
      return ["target_program"];
    case 1:
      return ["research_alignment"];
    case 2:
      return ["academic_background"];
    case 3:
      return ["professional_experiences"];
    case 4:
      return ["personal_turning_points"];
    case 5:
      return ["writing_preferences"];
    default:
      return [];
  }
}
