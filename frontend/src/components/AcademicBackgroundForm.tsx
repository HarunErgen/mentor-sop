import type { UseFormRegister, Control } from "react-hook-form";
import type { FullUserInputForm } from "../lib/schema";
import { ListInput } from "./ListInput";

type Props = {
  register: UseFormRegister<FullUserInputForm>;
  control: Control<FullUserInputForm>;
};

export function AcademicBackgroundForm({ register, control }: Props) {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-slate-900">Academic background</h3>

      <div>
        <label className="block text-sm font-medium text-slate-700">School name (optional)</label>
        <input
          type="text"
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("academic_background.school_name")}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700">Undergraduate degree (optional)</label>
        <input
          type="text"
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("academic_background.undergraduate_degree")}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700">GPA (optional)</label>
        <input
          type="text"
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="e.g. 3.8"
          {...register("academic_background.gpa")}
        />
      </div>

      <ListInput
        control={control}
        name="academic_background.relevant_coursework"
        label="Relevant coursework"
        addLabel="Add course"
      />
      <ListInput
        control={control}
        name="academic_background.research_projects"
        label="Research projects"
        addLabel="Add project"
      />
      <ListInput
        control={control}
        name="academic_background.publications"
        label="Publications"
        addLabel="Add publication"
      />
    </div>
  );
}
