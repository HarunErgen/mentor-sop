import type { Control, FieldPath, FieldValues } from "react-hook-form";
import { useFieldArray } from "react-hook-form";

type ListInputProps<T extends FieldValues> = {
  control: Control<T>;
  name: FieldPath<T>;
  label?: string;
  placeholder?: string;
  addLabel?: string;
};

export function ListInput<T extends FieldValues>({
  control,
  name,
  label,
  placeholder = "Item",
  addLabel = "Add item",
}: ListInputProps<T>) {
  const { fields, append, remove } = useFieldArray({ control, name: name as never });

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-slate-700">{label}</label>
      )}
      {fields.map((field, index) => (
        <div key={field.id} className="flex gap-2">
          <input
            type="text"
            className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            placeholder={placeholder}
            {...control.register(`${name}.${index}` as never)}
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
        className="text-sm text-indigo-600 hover:text-indigo-700"
      >
        {addLabel}
      </button>
    </div>
  );
}
