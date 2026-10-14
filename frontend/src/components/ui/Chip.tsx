import type { ReactNode } from 'react'

type Tone = 'flame' | 'lilac' | 'mint' | 'coral' | 'highlight'

type ChipProps = {
  tone: Tone
  icon?: ReactNode
  children: ReactNode
  /** Légère rotation façon gommette collée à la main (−3° à 3°). */
  tilt?: number
}

const tones: Record<Tone, string> = {
  flame: 'bg-flame',
  lilac: 'bg-lilac',
  mint: 'bg-mint',
  coral: 'bg-coral',
  highlight: 'bg-highlight',
}

/** Gommette / sticker pour XP, série, niveau, statut. Texte toujours foncé : les fonds sont vifs. */
export function Chip({ tone, icon, children, tilt = 0 }: ChipProps) {
  return (
    <span
      style={{ rotate: `${tilt}deg` }}
      className={`pop-border inline-flex items-center gap-1.5 rounded-full px-3 py-1 font-display text-base font-extrabold tabular-nums text-[#17172B] shadow-pop ${tones[tone]}`}
    >
      {icon}
      {children}
    </span>
  )
}
