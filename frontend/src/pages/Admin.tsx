import { ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router'

import { useAdminStats } from '../api/hooks'
import { Card } from '../components/ui/Card'
import { ErrorNote } from '../components/ui/ErrorNote'
import { IconButton } from '../components/ui/IconButton'
import { Page } from '../components/ui/Page'

const DAY = new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short' })
const DATE_TIME = new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })

/** Suivi du critère du MVP. Réservé aux pseudos de ADMIN_PSEUDOS (404 pour les autres). */
export function Admin() {
  const navigate = useNavigate()
  const stats = useAdminStats()

  return (
    <Page>
      <header className="flex items-center gap-3">
        <IconButton label="Retour" onClick={() => navigate('/')}>
          <ArrowLeft strokeWidth={2.5} />
        </IconButton>
        <h1 className="text-3xl">Stats</h1>
      </header>

      {stats.error && <ErrorNote message={stats.error.message === 'Not Found' ? 'Page introuvable.' : stats.error.message} />}

      {stats.data && (
        <>
          <p className="text-muted">Objectif : au moins 50 % des inscrits font 3 séances ou plus par semaine.</p>
          <section className="flex flex-col gap-3">
            {stats.data.weeks.map((week, i) => (
              <Card key={week.week_start} className="flex flex-col gap-1 p-4">
                <p className="font-semibold">
                  {i === 0 ? 'Cette semaine' : `Semaine du ${DAY.format(new Date(week.week_start))}`}
                </p>
                <p
                  className={`font-display text-4xl font-extrabold tabular-nums ${week.pct_3plus >= 50 ? 'text-mint' : 'text-text'}`}
                >
                  {week.pct_3plus} % <span className="text-base font-semibold text-muted">à 3 séances ou +</span>
                </p>
                <p className="text-base text-muted tabular-nums">
                  {week.active}/{week.registered} actifs · {week.sessions} séances · {week.sessions_per_active} par actif
                </p>
              </Card>
            ))}
          </section>

          <section className="flex flex-col gap-2">
            <h2 className="text-2xl">Testeurs</h2>
            <ul className="flex flex-col gap-2">
              {stats.data.users.map((user) => (
                <li key={user.pseudo} className="pop-border flex items-center gap-3 rounded-card bg-surface px-4 py-3">
                  <span className="flex-1">
                    <span className="block font-semibold">{user.pseudo}</span>
                    <span className="text-base text-muted">
                      {user.last_session ? `Dernière séance : ${DATE_TIME.format(new Date(user.last_session))}` : 'Jamais joué'}
                    </span>
                  </span>
                  <span className="text-right tabular-nums">
                    <span className="block font-display text-2xl font-extrabold">{user.sessions_this_week}</span>
                    <span className="text-sm text-muted">cette sem. · {user.sessions_total} au total</span>
                  </span>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </Page>
  )
}
