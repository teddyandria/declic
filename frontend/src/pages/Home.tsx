import { ChevronRight, Plus } from 'lucide-react'
import { Link, useNavigate } from 'react-router'

import { useLessons, useMe, useSessionPreview } from '../api/hooks'
import { MasteryBar } from '../components/MasteryBar'
import { LevelSticker, StreakSticker } from '../components/Stickers'
import { BottomBar } from '../components/ui/BottomBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { ErrorNote } from '../components/ui/ErrorNote'
import { Page } from '../components/ui/Page'

export function Home() {
  const navigate = useNavigate()
  const lessons = useLessons()
  const preview = useSessionPreview()
  const me = useMe()

  const dueCount = preview.data?.length ?? 0
  const hasLessons = (lessons.data?.length ?? 0) > 0
  const loading = lessons.isPending || preview.isPending

  return (
    <Page withBottomBar>
      <header className="flex items-center gap-3">
        <h1 className="flex-1 text-4xl">Déclic</h1>
        {me.data && (
          <>
            <StreakSticker streak={me.data.streak} />
            <LevelSticker level={me.data.level} />
          </>
        )}
      </header>

      {lessons.error && <ErrorNote message={lessons.error.message} />}

      {!loading && (
        <Card>
          {dueCount > 0 ? (
            <>
              <p className="font-display text-3xl font-extrabold tabular-nums">
                {dueCount} carte{dueCount > 1 ? 's' : ''} t'attend{dueCount > 1 ? 'ent' : ''}
              </p>
              <p className="text-muted">5 minutes. Pas plus.</p>
            </>
          ) : hasLessons ? (
            <>
              <p className="font-display text-3xl font-extrabold">Rien à réviser.</p>
              <p className="text-muted">Ton cerveau a quartier libre. Reviens demain.</p>
            </>
          ) : (
            <>
              <p className="font-display text-3xl font-extrabold">Ajoute ta leçon.</p>
              <p className="text-muted">Photo ou texte. Je fais les questions.</p>
            </>
          )}
        </Card>
      )}

      {hasLessons && (
        <section className="flex flex-col gap-3">
          <h2 className="text-2xl">Tes leçons</h2>
          {lessons.data?.map((lesson) => (
            <Link
              key={lesson.id}
              to={`/lecons/${lesson.id}`}
              className="pop-border flex min-h-16 items-center gap-3 rounded-card bg-surface px-4 py-3 shadow-pop transition-[translate,box-shadow] duration-100 active:translate-y-1 active:shadow-none"
            >
              <span className="flex flex-1 flex-col gap-2">
                <span className="font-semibold">{lesson.title}</span>
                {lesson.card_count > 0 ? (
                  <MasteryBar mastered={lesson.mastered} total={lesson.card_count} />
                ) : (
                  <span className="text-base text-muted">Pas encore de questions</span>
                )}
              </span>
              <ChevronRight strokeWidth={2.5} aria-hidden />
            </Link>
          ))}
          {dueCount > 0 && (
            <Link
              to="/ajouter"
              className="flex min-h-14 items-center justify-center gap-2 rounded-card border-[2.5px] border-dashed border-muted font-semibold text-muted"
            >
              <Plus strokeWidth={2.5} aria-hidden /> Ajouter une leçon
            </Link>
          )}
        </section>
      )}

      {!loading && (
        <BottomBar>
          {dueCount > 0 ? (
            <Button onClick={() => navigate('/seance')}>Réviser</Button>
          ) : (
            <Button onClick={() => navigate('/ajouter')}>Ajouter une leçon</Button>
          )}
        </BottomBar>
      )}
    </Page>
  )
}
