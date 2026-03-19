import type { UseFormRegister } from "react-hook-form";
import type { FullUserInputForm } from "../lib/schema";

type Props = {
  register: UseFormRegister<FullUserInputForm>;
};

export function PersonalTurningPointsForm({ register }: Props) {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-slate-900">Personal turning points (optional)</h3>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Moment that clarified your research direction
        </label>
        <textarea
          rows={3}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("personal_turning_points.direction_moment")}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700">
          Failure or obstacle and how you responded
        </label>
        <textarea
          rows={3}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("personal_turning_points.failure_or_obstacle")}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700">
          Intellectual shift or pivot
        </label>
        <textarea
          rows={3}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          {...register("personal_turning_points.intellectual_shift")}
        />
      </div>
    </div>
  );
}
