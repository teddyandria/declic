type LevelBarProps = {
  value: number
  max: number
  label: string
}

/** Barre continue (lilas) pour la progression vers le niveau suivant. */
export function LevelBar({ value, max, label }: LevelBarProps) {
  const percent = max > 0 ? Math.min(100, (value / max) * 100) : 0
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={value}
      className="pop-border h-5 w-full overflow-hidden rounded-full bg-surface p-0.5"
    >
      <span
        className="block h-full rounded-full bg-lilac transition-[width] duration-300"
        style={{ width: `${percent}%` }}
      />
    </div>
  )
}
