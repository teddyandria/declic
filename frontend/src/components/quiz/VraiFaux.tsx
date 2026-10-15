import { ChoiceTile } from './ChoiceTile'
import { tileState } from './tileState'

type VraiFauxProps = {
  selected: string
  correctAnswer: string | null
  onSelect: (choice: string) => void
}

/** Vrai / Faux : deux grosses tuiles côte à côte. */
export function VraiFaux({ selected, correctAnswer, onSelect }: VraiFauxProps) {
  return (
    <div className="flex gap-3" role="group" aria-label="Vrai ou faux">
      {['Vrai', 'Faux'].map((choice) => (
        <ChoiceTile
          key={choice}
          label={choice}
          state={tileState(choice, selected, correctAnswer)}
          disabled={correctAnswer !== null}
          onSelect={() => onSelect(choice)}
          className="min-h-20 justify-center text-center font-display text-2xl font-extrabold"
        />
      ))}
    </div>
  )
}
