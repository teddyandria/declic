import { Check, Flame, PlugZap, Sparkles, Star, X } from 'lucide-react'
import { useState } from 'react'

import { useHealth } from '../api/hooks'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Chip } from '../components/ui/Chip'
import { ProgressBar } from '../components/ui/ProgressBar'
import { Sheet } from '../components/ui/Sheet'

/** Phase 1 : vérifie la connexion à l'API et montre les composants « Cahier Pop ». */
export function Home() {
  const health = useHealth()
  const [sheetOpen, setSheetOpen] = useState(false)
  const connected = health.data?.status === 'ok'

  return (
    <main className="mx-auto flex min-h-dvh max-w-lg flex-col gap-6 px-4 py-8">
      <header className="flex items-center justify-between">
        <h1 className="text-4xl">Déclic</h1>
        <Chip tone="flame" tilt={-3} icon={<Flame size={18} strokeWidth={2.5} />}>
          3 j
        </Chip>
      </header>

      <Card className="flex items-center gap-4">
        <span
          className={`pop-border flex size-12 shrink-0 items-center justify-center rounded-full text-[#17172B] ${
            health.isPending ? 'bg-highlight' : connected ? 'bg-mint' : 'bg-coral'
          }`}
        >
          {health.isPending ? (
            <PlugZap strokeWidth={2.5} />
          ) : connected ? (
            <Check strokeWidth={2.5} />
          ) : (
            <X strokeWidth={2.5} />
          )}
        </span>
        <p className="font-display text-2xl font-extrabold" role="status">
          {health.isPending ? 'Connexion…' : connected ? 'API connectée' : 'API injoignable'}
        </p>
      </Card>

      <p>
        Révise ta leçon en <mark className="surligne">5 minutes</mark>. Pas plus.
      </p>

      <div className="flex flex-wrap gap-3">
        <Chip tone="highlight" tilt={2} icon={<Sparkles size={18} strokeWidth={2.5} />}>
          120 XP
        </Chip>
        <Chip tone="lilac" tilt={-2} icon={<Star size={18} strokeWidth={2.5} />}>
          Niveau 2
        </Chip>
      </div>

      <ProgressBar value={3} max={10} label="Carte 3 sur 10" />

      <div className="mt-auto">
        <Button onClick={() => setSheetOpen(true)}>Tester le feedback</Button>
      </div>

      <Sheet open={sheetOpen}>
        <p className="flex items-center gap-2 font-display text-2xl font-extrabold">
          <Check className="text-mint" strokeWidth={3} /> Juste !
        </p>
        <p className="text-muted">C'est le style Cahier Pop. Contours épais, ombres nettes.</p>
        <Button onClick={() => setSheetOpen(false)}>Continuer</Button>
      </Sheet>
    </main>
  )
}
