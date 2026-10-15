import { Check, Sparkles, X } from 'lucide-react'

import type { ReviewResult } from '../../api/types'
import { Button } from '../ui/Button'
import { Chip } from '../ui/Chip'

const RIGHT = ['Juste.', 'Exact.', 'Carré.', 'Bien vu.', 'Propre.']
const WRONG = ['Pas cette fois.', 'Raté. Ça arrive.', 'Presque.', 'Non. Tu l’auras la prochaine.']

type FeedbackProps = {
  result: ReviewResult
  /** Sert à varier la phrase sans qu'elle change à chaque rendu. */
  seed: number
  isLast: boolean
  onContinue: () => void
}

/** Contenu du panneau de correction : verdict (icône + texte), bonne réponse, explication. */
export function Feedback({ result, seed, isLast, onContinue }: FeedbackProps) {
  const phrases = result.correct ? RIGHT : WRONG
  return (
    <>
      <p className="flex items-center gap-3 font-display text-3xl font-extrabold">
        <span
          className={`pop-border flex size-11 items-center justify-center rounded-full text-[#17172B] ${result.correct ? 'bg-mint' : 'bg-coral'}`}
          aria-hidden
        >
          {result.correct ? <Check strokeWidth={3} /> : <X strokeWidth={3} />}
        </span>
        <span className="flex-1">{phrases[seed % phrases.length]}</span>
        <Chip tone="flame" tilt={3} icon={<Sparkles size={18} strokeWidth={2.5} aria-hidden />}>
          +{result.xp_gained} XP
        </Chip>
      </p>
      {!result.correct && (
        <p className="text-xl">
          Réponse : <strong className="surligne">{result.answer}</strong>
        </p>
      )}
      <p className="text-muted">{result.explanation}</p>
      <Button autoFocus onClick={onContinue}>
        {isLast ? 'Terminer' : 'Continuer'}
      </Button>
    </>
  )
}
