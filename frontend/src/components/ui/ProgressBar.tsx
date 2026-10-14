type ProgressBarProps = {
  value: number
  max: number
  label: string
}

/** Barre segmentée : un segment par carte, pour voir « 3 sur 10 » d'un coup d'œil. */
export function ProgressBar({ value, max, label }: ProgressBarProps) {
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={value}
      className="pop-border flex h-5 w-full gap-1 overflow-hidden rounded-full bg-surface p-0.5"
    >
      {Array.from({ length: max }, (_, i) => (
        <span
          key={i}
          className={`h-full flex-1 rounded-full transition-colors duration-200 ${i < value ? 'bg-pen' : 'bg-transparent'}`}
        />
      ))}
    </div>
  )
}
