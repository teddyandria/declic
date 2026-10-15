import { Flame, Star } from 'lucide-react'

import { Chip } from './ui/Chip'

/** Gommette de série : flamme orange. */
export function StreakSticker({ streak, tilt = -3 }: { streak: number; tilt?: number }) {
  return (
    <Chip tone="flame" tilt={tilt} icon={<Flame size={18} strokeWidth={2.5} aria-hidden />}>
      <span className="sr-only">Série de </span>
      {streak} j
    </Chip>
  )
}

/** Gommette de niveau : étoile lilas. */
export function LevelSticker({ level, tilt = 2 }: { level: number; tilt?: number }) {
  return (
    <Chip tone="lilac" tilt={tilt} icon={<Star size={18} strokeWidth={2.5} aria-hidden />}>
      Niv. {level}
    </Chip>
  )
}
