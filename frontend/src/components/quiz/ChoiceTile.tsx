import { Check, X } from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'

export type TileState = 'idle' | 'selected' | 'correct' | 'wrong' | 'dimmed'

type ChoiceTileProps = {
  label: string
  state: TileState
  disabled: boolean
  onSelect: () => void
  className?: string
}

const styles: Record<TileState, string> = {
  idle: 'bg-surface text-text',
  selected: 'bg-highlight text-[#17172B]',
  correct: 'bg-mint text-[#17172B]',
  wrong: 'bg-coral text-[#17172B]',
  dimmed: 'bg-surface text-muted',
}

/** Grande tuile de réponse. Juste/faux : couleur + icône (jamais la couleur seule). */
export function ChoiceTile({ label, state, disabled, onSelect, className = '' }: ChoiceTileProps) {
  const reduceMotion = useReducedMotion()
  const shake = state === 'wrong' && !reduceMotion

  return (
    <motion.button
      type="button"
      onClick={onSelect}
      disabled={disabled}
      aria-pressed={state === 'selected'}
      animate={shake ? { x: [0, -8, 8, -4, 0] } : { x: 0 }}
      transition={{ duration: 0.15 }}
      className={`pop-border flex min-h-16 w-full items-center gap-3 rounded-card px-4 py-3 text-left font-semibold shadow-pop transition-[translate,box-shadow,background-color] duration-100 enabled:active:translate-y-1 enabled:active:shadow-none ${styles[state]} ${className}`}
    >
      <span className="flex-1">{label}</span>
      {state === 'correct' && <Check strokeWidth={3} aria-label="bonne réponse" />}
      {state === 'wrong' && <X strokeWidth={3} aria-label="ta réponse, fausse" />}
    </motion.button>
  )
}
