import type { Control, UseFormRegister, FieldErrors } from "react-hook-form";
import { useFieldArray } from "react-hook-form";
import type { FullUserInputForm } from "../lib/schema";

type Props = {
  control: Control<FullUserInputForm>;
  register: UseFormRegister<FullUserInputForm>;
  errors?: FieldErrors<FullUserInputForm>;
};

export function ProfessionalExperiencesForm({ control, register, errors }: Props) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: "professional_experiences",
  });

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-slate-900">Professional experience</h3>

      {fields.map((field, index) => (
        <div key={field.id} className="rounded-lg border border-slate-200 bg-slate-50/50 p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-700">Experience {index + 1}</span>
            <button
              type="button"
              onClick={() => remove(index)}
              className="text-sm text-red-600 hover:text-red-700"
            >
              Remove
            </button>
          </div>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <div>
              <label className="block text-xs font-medium text-slate-600">Title *</label>
              <input
                type="text"
                className={`mt-1 block w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 ${
                  errors?.professional_experiences?.[index]?.title
                    ? "border-red-300 focus:border-red-500 focus:ring-red-500"
                    : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-500"
                }`}
                {...register(`professional_experiences.${index}.title`)}
              />
              {errors?.professional_experiences?.[index]?.title && (
                <p className="mt-1 text-xs text-red-600">
                  {errors.professional_experiences[index]?.title?.message}
                </p>
              )}
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600">Company</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                {...register(`professional_experiences.${index}.company`)}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600">Start date</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                placeholder="e.g. 2020"
                {...register(`professional_experiences.${index}.start_date`)}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600">End date</label>
              <input
                type="text"
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                placeholder="e.g. 2022 or Present"
                {...register(`professional_experiences.${index}.end_date`)}
              />
            </div>
          </div>
          <div className="mt-3">
            <label className="block text-xs font-medium text-slate-600">Description</label>
            <textarea
              rows={3}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              {...register(`professional_experiences.${index}.description`)}
            />
          </div>
        </div>
      ))}

      <button
        type="button"
        onClick={() => append({ title: "", company: null, start_date: null, end_date: null, description: null })}
        className="text-sm text-indigo-600 hover:text-indigo-700"
      >
        Add experience
      </button>
    </div>
  );
}
