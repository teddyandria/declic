import { LoaderCircle, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router'

import { useFinishSession, useReview, useSessionCards } from '../api/hooks'
import type { FinishResult, ReviewResult } from '../api/types'
import { Feedback } from '../components/quiz/Feedback'
import { ListenButton } from '../components/quiz/ListenButton'
import { Qcm } from '../components/quiz/Qcm'
import { QuestionText } from '../components/quiz/QuestionText'
import { spokenText } from '../components/quiz/spoken'
import { Trou } from '../components/quiz/Trou'
import { VraiFaux } from '../components/quiz/VraiFaux'
import { BottomBar } from '../components/ui/BottomBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { ErrorNote } from '../components/ui/ErrorNote'
import { IconButton } from '../components/ui/IconButton'
import { Page } from '../components/ui/Page'
import { ProgressBar } from '../components/ui/ProgressBar'
import { Sheet } from '../components/ui/Sheet'
import { stopSpeaking } from '../lib/speech'

/** Passé à l'écran de fin. `finish` est null si l'appel de fin a raté (on affiche quand même le résumé). */
export type SessionSummary = { correct: number; total: number; xp: number; finish: FinishResult | null }

export function Session() {
  const navigate = useNavigate()
  const lessonParam = useSearchParams()[0].get('lecon')
  const cards = useSessionCards(lessonParam ? Number(lessonParam) : null)
  const review = useReview()
  const finishSession = useFinishSession()

  const [index, setIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<ReviewResult | null>(null)
  const [correctCount, setCorrectCount] = useState(0)
  const [sessionXp, setSessionXp] = useState(0)

  useEffect(() => stopSpeaking, [index]) // coupe la voix en changeant de carte ou en quittant

  if (cards.isPending) {
    return (
      <Page>
        <div className="flex flex-1 items-center justify-center" role="status" aria-label="Chargement">
          <LoaderCircle className="size-12 animate-spin text-pen motion-reduce:animate-none" strokeWidth={2.5} />
        </div>
      </Page>
    )
  }

  if (cards.error || cards.data.length === 0) {
    return (
      <Page withBottomBar>
        {cards.error ? (
          <ErrorNote message={cards.error.message} />
        ) : (
          <Card>
            <p className="font-display text-3xl font-extrabold">Rien à réviser.</p>
            <p className="text-muted">Tout est à jour. Reviens demain.</p>
          </Card>
        )}
        <BottomBar>
          <Button onClick={() => navigate('/')}>Retour</Button>
        </BottomBar>
      </Page>
    )
  }

  const total = cards.data.length
  const card = cards.data[index]
  const isLast = index === total - 1

  function submit(event?: FormEvent) {
    event?.preventDefault()
    if (!answer.trim() || result || review.isPending) return
    review.mutate(
      { card_id: card.id, answer },
      {
        onSuccess: (res) => {
          setResult(res)
          setSessionXp((xp) => xp + res.xp_gained)
          if (res.correct) setCorrectCount((n) => n + 1)
        },
      },
    )
  }

  async function next() {
    if (isLast) {
      const finish = await finishSession.mutateAsync().catch(() => null)
      const summary: SessionSummary = {
        correct: correctCount,
        total,
        xp: sessionXp + (finish?.xp_gained ?? 0),
        finish,
      }
      navigate('/fin', { replace: true, state: summary })
      return
    }
    setIndex(index + 1)
    setAnswer('')
    setResult(null)
    review.reset()
  }

  return (
    <Page withBottomBar>
      <header className="flex items-center gap-3">
        <IconButton label="Arrêter la séance" onClick={() => navigate('/')}>
          <X strokeWidth={2.5} />
        </IconButton>
        <ProgressBar value={index + (result ? 1 : 0)} max={total} label={`Carte ${index + 1} sur ${total}`} />
      </header>

      {/* key : tout l'écran de question repart à zéro à chaque carte */}
      <form key={card.id} onSubmit={submit} className="flex flex-col gap-6">
        <div className="flex flex-col gap-3">
          <p className="text-base font-semibold text-muted">{card.lesson_title}</p>
          <QuestionText type={card.type} question={card.question} typed={answer} />
          <ListenButton text={spokenText(card.type, card.question, card.choices)} />
        </div>

        {card.type === 'qcm' && (
          <Qcm choices={card.choices} selected={answer} correctAnswer={result?.answer ?? null} onSelect={setAnswer} />
        )}
        {card.type === 'vrai_faux' && (
          <VraiFaux selected={answer} correctAnswer={result?.answer ?? null} onSelect={setAnswer} />
        )}
        {card.type === 'trou' && <Trou value={answer} correct={result?.correct ?? null} onChange={setAnswer} />}

        {review.error && <ErrorNote message={review.error.message} />}
      </form>

      {!result && (
        <BottomBar>
          <Button disabled={!answer.trim() || review.isPending} onClick={() => submit()}>
            Valider
          </Button>
        </BottomBar>
      )}

      <Sheet open={result !== null} delay={result?.correct === false ? 0.15 : 0}>
        {result && <Feedback result={result} seed={card.id} isLast={isLast} onContinue={() => void next()} />}
      </Sheet>
    </Page>
  )
}
