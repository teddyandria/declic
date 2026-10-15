import { ChoiceTile } from './ChoiceTile'
import type { TileState } from './ChoiceTile'
import { tileState } from './tileState'

type QcmProps = {
  choices: string[]
  selected: string
  correctAnswer: string | null
  onSelect: (choice: string) => void
}

/** QCM : grandes tuiles empilées. */
export function Qcm({ choices, selected, correctAnswer, onSelect }: QcmProps) {
  return (
    <div className="flex flex-col gap-3" role="group" aria-label="Choix de réponse">
      {choices.map((choice) => {
        const state: TileState = tileState(choice, selected, correctAnswer)
        return (
          <ChoiceTile
            key={choice}
            label={choice}
            state={state}
            disabled={correctAnswer !== null}
            onSelect={() => onSelect(choice)}
          />
        )
      })}
    </div>
  )
}
