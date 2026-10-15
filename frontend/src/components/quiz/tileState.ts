import type { TileState } from './ChoiceTile'

/** État d'une tuile : avant correction (sélection), puis après (juste / faux / éteinte). */
export function tileState(choice: string, selected: string, correctAnswer: string | null): TileState {
  if (correctAnswer === null) return choice === selected ? 'selected' : 'idle'
  if (choice === correctAnswer) return 'correct'
  if (choice === selected) return 'wrong'
  return 'dimmed'
}
