import { useLocation, useNavigate } from 'react-router'

import { BottomBar } from '../components/ui/BottomBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Page } from '../components/ui/Page'
import type { SessionSummary } from './Session'

/** Fin de séance (version simple ; XP, série et confettis arrivent en phase 5). */
export function SessionEnd() {
  const navigate = useNavigate()
  const summary = useLocation().state as SessionSummary | null

  return (
    <Page withBottomBar>
      <div className="flex flex-1 flex-col justify-center gap-6">
        <h1 className="text-4xl">Séance finie.</h1>
        {summary && (
          <Card>
            <p className="font-display text-5xl font-extrabold tabular-nums">
              {summary.correct}/{summary.total}
            </p>
            <p className="text-muted">bonnes réponses. Le reste reviendra au bon moment.</p>
          </Card>
        )}
      </div>
      <BottomBar>
        <Button onClick={() => navigate('/', { replace: true })}>Retour à l'accueil</Button>
      </BottomBar>
    </Page>
  )
}
