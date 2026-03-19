import type { UseFormRegister, Control, FieldErrors } from "react-hook-form";
import { useFieldArray } from "react-hook-form";
import type { FullUserInputForm } from "../lib/schema";
import { ProfessorEditor } from "./ProfessorEditor";

const DEGREE_OPTIONS = [
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
] as const;

type Props = {
  register: UseFormRegister<FullUserInputForm>;
  control: Control<FullUserInputForm>;
  errors?: FieldErrors<FullUserInputForm>;
};

export function TargetProgramForm({ register, control, errors }: Props) {
  const { fields: labFields, append: appendLab, remove: removeLab } = useFieldArray({
    control,
    name: "target_program.labs" as never,
  });
  const { fields: profFields, append: appendProf, remove: removeProf } = useFieldArray({
    control,
    name: "target_program.target_professors" as never,
  });

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-slate-900">Target program</h3>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          University name *
        </label>
        <input
          type="text"
          className={`mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-1 ${
            errors?.target_program?.university_name
              ? "border-red-300 focus:border-red-500 focus:ring-red-500"
              : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-500"
          }`}
          placeholder="e.g. Stanford University"
          {...register("target_program.university_name")}
        />
        {errors?.target_program?.university_name && (
          <p className="mt-1 text-sm text-red-600">
            {errors.target_program.university_name.message}
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Degree type *
        </label>
        <select
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("target_program.degree_type")}
        >
          {DEGREE_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Department (optional)
        </label>
        <input
          type="text"
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="e.g. Computer Science"
          {...register("target_program.department")}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Target labs (optional)
        </label>
        {labFields.map((field, index) => (
          <div key={field.id} className="mt-2 flex gap-2">
            <input
              type="text"
              className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="Lab name"
              {...register(`target_program.labs.${index}`)}
            />
            <button
              type="button"
              onClick={() => removeLab(index)}
              className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-600 hover:bg-slate-50"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => appendLab("")}
          className="mt-2 text-sm text-indigo-600 hover:text-indigo-700"
        >
          Add lab
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Target professors (optional)
        </label>
        {profFields.map((field, index) => (
          <ProfessorEditor
            key={field.id}
            control={control}
            index={index}
            onRemove={() => removeProf(index)}
            errors={errors}
          />
        ))}
        <button
          type="button"
          onClick={() =>
            appendProf({
              name: "",
              research_areas: [],
              research_projects: [],
              publications: [],
              other_relevant_info: null,
            } as any)
          }
          className="mt-2 text-sm text-indigo-600 hover:text-indigo-700"
        >
          Add professor
        </button>
      </div>
    </div>
  );
}
