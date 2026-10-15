import { useState } from 'react'
import type { FormEvent } from 'react'

import type { CardData, CardUpdate } from '../api/types'
import { Button } from './ui/Button'
import { ErrorNote } from './ui/ErrorNote'

type CardEditorProps = {
  card: CardData
  error: string | null
  saving: boolean
  onSave: (update: CardUpdate) => void
  onCancel: () => void
}

const fieldClass = 'pop-border min-h-12 w-full rounded-card bg-surface px-3 text-text'

/** Formulaire de correction d'une carte, adapté à son type. */
export function CardEditor({ card, error, saving, onSave, onCancel }: CardEditorProps) {
  const [question, setQuestion] = useState(card.question)
  const [answer, setAnswer] = useState(card.answer)
  const [choices, setChoices] = useState(card.choices)
  const [explanation, setExplanation] = useState(card.explanation)

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    onSave({ question, answer, explanation, ...(card.type === 'qcm' && { choices }) })
  }

  function setChoice(index: number, value: string) {
    // Si on modifie la bonne réponse, la réponse suit.
    if (choices[index] === answer) setAnswer(value)
    setChoices(choices.map((c, i) => (i === index ? value : c)))
  }

  return (
    <form onSubmit={onSubmit} className="flex max-h-[80dvh] flex-col gap-3 overflow-y-auto">
      <h2 className="text-2xl">Corriger la carte</h2>
      {error && <ErrorNote message={error} />}

      <label className="flex flex-col gap-1">
        <span className="font-semibold">Question</span>
        <textarea rows={2} className={`${fieldClass} py-2`} value={question} onChange={(e) => setQuestion(e.target.value)} />
      </label>

      {card.type === 'qcm' && (
        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 font-semibold">Choix (coche la bonne réponse)</legend>
          {choices.map((choice, i) => (
            <div key={i} className="flex items-center gap-2">
              <input
                type="radio"
                name="answer"
                aria-label={`Choix ${i + 1} est la bonne réponse`}
                checked={choice === answer}
                onChange={() => setAnswer(choice)}
                className="size-6 shrink-0 accent-[var(--pen)]"
              />
              <input className={fieldClass} value={choice} onChange={(e) => setChoice(i, e.target.value)} />
            </div>
          ))}
        </fieldset>
      )}

      {card.type === 'vrai_faux' && (
        <div className="flex gap-3" role="radiogroup" aria-label="Bonne réponse">
          {['Vrai', 'Faux'].map((value) => (
            <button
              key={value}
              type="button"
              role="radio"
              aria-checked={answer === value}
              onClick={() => setAnswer(value)}
              className={`pop-border min-h-12 flex-1 rounded-card font-display font-extrabold ${answer === value ? 'bg-highlight text-[#17172B]' : 'bg-surface'}`}
            >
              {value}
            </button>
          ))}
        </div>
      )}

      {card.type === 'trou' && (
        <label className="flex flex-col gap-1">
          <span className="font-semibold">Mot manquant</span>
          <input className={fieldClass} value={answer} onChange={(e) => setAnswer(e.target.value)} />
        </label>
      )}

      <label className="flex flex-col gap-1">
        <span className="font-semibold">Explication</span>
        <textarea
          rows={2}
          className={`${fieldClass} py-2`}
          value={explanation}
          onChange={(e) => setExplanation(e.target.value)}
        />
      </label>

      <Button type="submit" disabled={saving}>
        Enregistrer
      </Button>
      <button type="button" onClick={onCancel} className="min-h-12 font-semibold text-muted underline">
        Annuler
      </button>
    </form>
  )
}
