// Miroir des schémas de backend/app/schemas.py

export type CardType = 'qcm' | 'vrai_faux' | 'trou'

export type LessonSummary = {
  id: number
  title: string
  created_at: string
  card_count: number
}

export type CardData = {
  id: number
  type: CardType
  question: string
  answer: string
  choices: string[]
  explanation: string
}

export type LessonDetail = {
  id: number
  title: string
  text: string
  created_at: string
  cards: CardData[]
}

export type CardUpdate = Partial<Pick<CardData, 'question' | 'answer' | 'choices' | 'explanation'>>

/** Carte telle que vue en séance : sans réponse ni explication. */
export type SessionCard = {
  id: number
  type: CardType
  question: string
  choices: string[]
  lesson_title: string
}

export type ReviewResult = {
  correct: boolean
  answer: string
  explanation: string
}
