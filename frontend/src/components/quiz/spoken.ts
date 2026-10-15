import type { CardType } from '../../api/types'

export const BLANK = '___'

/** Version à lire à voix haute : le blanc devient « blanc », les choix sont énumérés. */
export function spokenText(type: CardType, question: string, choices: string[]): string {
  const spokenQuestion = question.replace(BLANK, '… blanc …')
  if (type === 'qcm') return `${spokenQuestion} Choix : ${choices.join(' ; ')}.`
  if (type === 'vrai_faux') return `Vrai ou faux ? ${spokenQuestion}`
  return spokenQuestion
}
