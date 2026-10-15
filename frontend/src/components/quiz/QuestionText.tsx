import type { CardType } from '../../api/types'

import { BLANK } from './spoken'

/** La question. Pour un texte à trous, le blanc est surligné et se remplit pendant la frappe. */
export function QuestionText({ type, question, typed }: { type: CardType; question: string; typed: string }) {
  if (type !== 'trou' || !question.includes(BLANK)) {
    return <p className="text-2xl leading-snug font-semibold">{question}</p>
  }
  const [before, after] = question.split(BLANK)
  return (
    <p className="text-2xl leading-snug font-semibold">
      {before}
      <span className="surligne inline-block min-w-20 border-b-[3px] border-text px-1 text-center">
        {typed || ' '}
      </span>
      {after}
    </p>
  )
}
