import type { InputHTMLAttributes } from 'react'

type FieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string
  hint?: string
}

/** Champ de formulaire : libellé au-dessus, aide courte en dessous. */
export function Field({ label, hint, id, ...props }: FieldProps) {
  const inputId = id ?? props.name
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={inputId} className="font-semibold">
        {label}
      </label>
      <input
        id={inputId}
        aria-describedby={hint ? `${inputId}-hint` : undefined}
        className="pop-border min-h-14 rounded-card bg-surface px-4 text-text placeholder:text-muted"
        {...props}
      />
      {hint && (
        <p id={`${inputId}-hint`} className="text-base text-muted">
          {hint}
        </p>
      )}
    </div>
  )
}
