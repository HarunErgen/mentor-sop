import type { UseFormRegister, Control } from "react-hook-form";
import { useFieldArray } from "react-hook-form";
import type { FullUserInputForm } from "../lib/schema";

type Props = {
  register: UseFormRegister<FullUserInputForm>;
  control: Control<FullUserInputForm>;
};

export function ResearchAlignmentForm({ register, control }: Props) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: "research_alignment.research_problems" as never,
  });

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-slate-900">Research alignment</h3>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Intended research area (optional)
        </label>
        <textarea
          rows={3}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="e.g. Machine learning for healthcare"
          {...register("research_alignment.intended_research_area")}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Research problems (2–3 of interest)
        </label>
        {fields.map((field, index) => (
          <div key={field.id} className="mt-2 flex gap-2">
            <input
              type="text"
              className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder={`Problem ${index + 1}`}
              {...register(`research_alignment.research_problems.${index}`)}
            />
            <button
              type="button"
              onClick={() => remove(index)}
              className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-600 hover:bg-slate-50"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => append("" as never)}
          className="mt-2 text-sm text-indigo-600 hover:text-indigo-700"
        >
          Add problem
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Why these problems matter (optional)
        </label>
        <textarea
          rows={3}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("research_alignment.why_these_problems_matter")}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Long-term goal (optional)
        </label>
        <textarea
          rows={3}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("research_alignment.long_term_goal")}
        />
      </div>
    </div>
  );
}
