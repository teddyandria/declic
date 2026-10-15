import { ProgressBar } from './ui/ProgressBar'

/** Maîtrise d'une leçon : un segment par carte, rempli quand la carte est maîtrisée. */
export function MasteryBar({ mastered, total }: { mastered: number; total: number }) {
  if (total === 0) return null
  return (
    <div className="flex items-center gap-3">
      <ProgressBar value={mastered} max={total} label={`${mastered} cartes maîtrisées sur ${total}`} />
      <span className="shrink-0 text-base text-muted tabular-nums" aria-hidden>
        {mastered}/{total}
      </span>
    </div>
  )
}
