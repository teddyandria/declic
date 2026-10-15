// Miroir des schémas de backend/app/schemas.py

export type CardType = 'qcm' | 'vrai_faux' | 'trou'

export type LessonSummary = {
  id: number
  title: string
  created_at: string
  card_count: number
  /** Cartes maîtrisées (état FSRS « Review ») */
  mastered: number
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
  mastered: number
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
  xp_gained: number
}

export type Progress = {
  xp: number
  level: number
  xp_into_level: number
  xp_for_next: number
  streak: number
}

export type FinishResult = Progress & {
  xp_gained: number
  level_up: boolean
  streak_extended: boolean
}

export type Me = Progress & {
  pseudo: string
  played_today: boolean
  lessons: LessonSummary[]
}
