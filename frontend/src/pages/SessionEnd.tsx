import confetti from 'canvas-confetti'
import { animate, motion, useReducedMotion } from 'motion/react'
import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router'

import { LevelSticker, StreakSticker } from '../components/Stickers'
import { BottomBar } from '../components/ui/BottomBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { LevelBar } from '../components/ui/LevelBar'
import { Page } from '../components/ui/Page'
import type { SessionSummary } from './Session'

const COUNT_DURATION = 0.9 // s

function headline({ finish, correct, total }: SessionSummary): string {
  if (finish?.level_up) return `Niveau ${finish.level}. Rien que ça.`
  if (finish?.streak_extended && finish.streak > 1) return `${finish.streak} jours d’affilée.`
  if (correct === total) return 'Sans faute. Propre.'
  return 'Séance bouclée.'
}

function recap({ correct, total }: SessionSummary): string {
  const toReview = total - correct
  const inPocket = `${correct} carte${correct > 1 ? 's' : ''} dans la poche.`
  if (toReview === 0) return inPocket
  return `${inPocket} ${toReview} reviendr${toReview > 1 ? 'ont' : 'a'} bientôt.`
}

/** Compteur qui défile de 0 à `target` (ou s'affiche direct si les animations sont réduites). */
function useCountUp(target: number, enabled: boolean): number {
  const [value, setValue] = useState(enabled ? 0 : target)
  useEffect(() => {
    if (!enabled) return
    const controls = animate(0, target, { duration: COUNT_DURATION, ease: 'easeOut', onUpdate: (v) => setValue(Math.round(v)) })
    return () => controls.stop()
  }, [target, enabled])
  return value
}

export function SessionEnd() {
  const navigate = useNavigate()
  const reduceMotion = useReducedMotion() ?? false
  const summary = useLocation().state as SessionSummary | null
  const xp = useCountUp(summary?.xp ?? 0, !reduceMotion)

  // Confettis une fois le compteur arrivé : une seule chose bouge à la fois.
  useEffect(() => {
    if (!summary || reduceMotion) return
    const timer = setTimeout(() => {
      void confetti({
        particleCount: 90,
        spread: 75,
        origin: { y: 0.65 },
        colors: ['#3156F5', '#FFE14D', '#22C97A', '#FF9A1F', '#A98BFF'],
        disableForReducedMotion: true,
      })
    }, COUNT_DURATION * 1000)
    return () => clearTimeout(timer)
  }, [summary, reduceMotion])

  if (!summary) {
    // Arrivée directe sur /fin (rechargement…) : rien à fêter.
    return (
      <Page withBottomBar>
        <h1 className="text-4xl">Séance finie.</h1>
        <BottomBar>
          <Button onClick={() => navigate('/', { replace: true })}>Retour à l'accueil</Button>
        </BottomBar>
      </Page>
    )
  }

  const { finish } = summary
  const pop = reduceMotion
    ? { initial: { opacity: 0 }, animate: { opacity: 1 } }
    : { initial: { scale: 0.6, opacity: 0 }, animate: { scale: 1, opacity: 1 } }

  return (
    <Page withBottomBar>
      <div className="flex flex-1 flex-col justify-center gap-6">
        <h1 className="text-4xl">{headline(summary)}</h1>

        <Card className="flex flex-col items-start gap-1">
          <p className="font-display text-6xl font-extrabold text-flame tabular-nums" aria-label={`${summary.xp} XP gagnés`}>
            +{xp} <span className="text-4xl">XP</span>
          </p>
          <p className="text-muted">{recap(summary)}</p>
        </Card>

        {finish && (
          <motion.div
            {...pop}
            transition={{ type: 'spring', duration: 0.3, bounce: 0.4, delay: COUNT_DURATION }}
            className="flex flex-col gap-4"
          >
            <div className="flex items-center gap-3">
              <StreakSticker streak={finish.streak} tilt={-3} />
              <LevelSticker level={finish.level} tilt={2} />
            </div>
            <div className="flex flex-col gap-1">
              <LevelBar
                value={finish.xp_into_level}
                max={finish.xp_for_next}
                label={`Niveau ${finish.level + 1} : ${finish.xp_into_level} XP sur ${finish.xp_for_next}`}
              />
              <p className="text-base text-muted tabular-nums">
                Niveau {finish.level + 1} dans {finish.xp_for_next - finish.xp_into_level} XP
              </p>
            </div>
          </motion.div>
        )}
      </div>

      <BottomBar>
        <Button onClick={() => navigate('/', { replace: true })}>Retour à l'accueil</Button>
      </BottomBar>
    </Page>
  )
}
