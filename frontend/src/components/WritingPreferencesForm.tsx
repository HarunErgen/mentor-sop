import type { UseFormRegister } from "react-hook-form";
import type { FullUserInputForm } from "../lib/schema";

const LANGUAGE_OPTIONS = [
  { value: "basic", label: "Basic" },
  { value: "normal", label: "Normal" },
  { value: "advanced", label: "Advanced" },
] as const;

type Props = {
  register: UseFormRegister<FullUserInputForm>;
};

export function WritingPreferencesForm({ register }: Props) {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-slate-900">Writing preferences</h3>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Language complexity
        </label>
        <select
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("writing_preferences.language_complexity")}
        >
          <option value="">— Select —</option>
          {LANGUAGE_OPTIONS.map(({ value, label }) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="use_em_dash"
          className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
          {...register("writing_preferences.use_em_dash")}
        />
        <label htmlFor="use_em_dash" className="text-sm text-slate-700">
          Use em dashes in prose
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Target word count (optional)
        </label>
        <input
          type="number"
          min={1}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("writing_preferences.target_word_count", { valueAsNumber: true })}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Extra instructions (optional)
        </label>
        <textarea
          rows={3}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="Style or content preferences"
          {...register("writing_preferences.extra_instructions")}
        />
      </div>
    </div>
  );
}
