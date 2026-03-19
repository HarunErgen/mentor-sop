import type { Control, UseFormRegister, FieldErrors } from "react-hook-form";
import { useFieldArray } from "react-hook-form";
import type { FullUserInputForm } from "../lib/schema";

type Props = {
  control: Control<FullUserInputForm>;
  index: number;
  onRemove: () => void;
  errors?: FieldErrors<FullUserInputForm>;
};

export function ProfessorEditor({ control, index, onRemove, errors }: Props) {
  const base = `target_program.target_professors.${index}` as const;
  const { fields: areaFields, append: appendArea, remove: removeArea } = useFieldArray({
    control,
    name: `${base}.research_areas` as never,
  });
  const { fields: projectFields, append: appendProject, remove: removeProject } = useFieldArray({
    control,
    name: `${base}.research_projects` as never,
  });
  const { fields: pubFields, append: appendPub, remove: removePub } = useFieldArray({
    control,
    name: `${base}.publications` as never,
  });

  const register = control.register as UseFormRegister<FullUserInputForm>;

  return (
    <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50/50 p-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">Professor {index + 1}</span>
        <button
          type="button"
          onClick={onRemove}
          className="text-sm text-red-600 hover:text-red-700"
        >
          Remove professor
        </button>
      </div>
      <div className="mt-3 space-y-3">
        <div>
          <label className="block text-xs font-medium text-slate-600">Name *</label>
          <input
            type="text"
            className={`mt-1 block w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 ${
              errors?.target_program?.target_professors?.[index]?.name
                ? "border-red-300 focus:border-red-500 focus:ring-red-500"
                : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-500"
            }`}
            {...register(`${base}.name`)}
          />
          {errors?.target_program?.target_professors?.[index]?.name && (
            <p className="mt-1 text-xs text-red-600">
              {errors.target_program.target_professors[index]?.name?.message}
            </p>
          )}
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600">Research areas</label>
          {areaFields.map((f, i) => (
            <div key={f.id} className="mt-1 flex gap-2">
              <input
                type="text"
                className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                {...register(`${base}.research_areas.${i}`)}
              />
              <button type="button" onClick={() => removeArea(i)} className="text-slate-500 hover:text-slate-700">×</button>
            </div>
          ))}
          <button type="button" onClick={() => appendArea("")} className="mt-1 text-xs text-indigo-600">Add area</button>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600">Research projects</label>
          {projectFields.map((f, i) => (
            <div key={f.id} className="mt-1 flex gap-2">
              <input
                type="text"
                className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                {...register(`${base}.research_projects.${i}`)}
              />
              <button type="button" onClick={() => removeProject(i)} className="text-slate-500 hover:text-slate-700">×</button>
            </div>
          ))}
          <button type="button" onClick={() => appendProject("")} className="mt-1 text-xs text-indigo-600">Add project</button>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600">Publications</label>
          {pubFields.map((f, i) => (
            <div key={f.id} className="mt-2 rounded border border-slate-200 bg-white p-2">
              <div className="grid gap-2 sm:grid-cols-2">
                <input
                  type="text"
                  placeholder="Title"
                  className="rounded border border-slate-300 px-2 py-1 text-sm"
                  {...register(`${base}.publications.${i}.title`)}
                />
                <input
                  type="text"
                  placeholder="Date / URL"
                  className="rounded border border-slate-300 px-2 py-1 text-sm"
                  {...register(`${base}.publications.${i}.publication_date`)}
                />
              </div>
              <textarea
                placeholder="Abstract (optional)"
                rows={2}
                className="mt-2 w-full rounded border border-slate-300 px-2 py-1 text-sm"
                {...register(`${base}.publications.${i}.abstract`)}
              />
              <button type="button" onClick={() => removePub(i)} className="mt-1 text-xs text-slate-500">Remove publication</button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => appendPub({ title: "", publication_date: null, publication_url: null, abstract: null, description: null })}
            className="mt-1 text-xs text-indigo-600"
          >
            Add publication
          </button>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600">Other relevant info</label>
          <textarea
            rows={2}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            {...register(`${base}.other_relevant_info`)}
          />
        </div>
      </div>
    </div>
  );
}
