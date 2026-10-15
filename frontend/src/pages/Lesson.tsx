import { ArrowLeft, Pencil, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router'

import { useDeleteCard, useDeleteLesson, useGenerateCards, useLesson, useUpdateCard } from '../api/hooks'
import type { CardData, CardType } from '../api/types'
import { CardEditor } from '../components/CardEditor'
import { BottomBar } from '../components/ui/BottomBar'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { ErrorNote } from '../components/ui/ErrorNote'
import { IconButton } from '../components/ui/IconButton'
import { Page } from '../components/ui/Page'
import { Sheet } from '../components/ui/Sheet'

const TYPE_LABELS: Record<CardType, string> = { qcm: 'QCM', vrai_faux: 'Vrai / Faux', trou: 'À trou' }

export function Lesson() {
  const navigate = useNavigate()
  const lessonId = Number(useParams().id)
  const lesson = useLesson(lessonId)
  const generate = useGenerateCards()
  const updateCard = useUpdateCard(lessonId)
  const deleteCard = useDeleteCard()
  const deleteLesson = useDeleteLesson()

  const [editing, setEditing] = useState<CardData | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<number | 'lesson' | null>(null)

  if (lesson.isPending) return <Page>{null}</Page>
  if (lesson.error) {
    return (
      <Page>
        <ErrorNote message={lesson.error.message} />
        <Button onClick={() => navigate('/')}>Retour à l'accueil</Button>
      </Page>
    )
  }

  const { cards } = lesson.data

  async function onDeleteLesson() {
    if (confirmDelete !== 'lesson') return setConfirmDelete('lesson')
    await deleteLesson.mutateAsync(lessonId)
    navigate('/', { replace: true })
  }

  function onDeleteCard(cardId: number) {
    if (confirmDelete !== cardId) return setConfirmDelete(cardId)
    deleteCard.mutate(cardId)
    setConfirmDelete(null)
  }

  return (
    <Page withBottomBar>
      <header className="flex items-start gap-3">
        <IconButton label="Retour" onClick={() => navigate('/')}>
          <ArrowLeft strokeWidth={2.5} />
        </IconButton>
        <div className="flex-1">
          <h1 className="text-3xl break-words">{lesson.data.title}</h1>
          <p className="text-muted tabular-nums">
            {cards.length} carte{cards.length > 1 ? 's' : ''}
          </p>
        </div>
        <IconButton
          label={confirmDelete === 'lesson' ? 'Confirmer la suppression de la leçon' : 'Supprimer la leçon'}
          onClick={onDeleteLesson}
          className={confirmDelete === 'lesson' ? 'bg-coral text-[#17172B]' : ''}
        >
          <Trash2 strokeWidth={2.5} />
        </IconButton>
      </header>

      {confirmDelete === 'lesson' && <p className="font-semibold">Sûr ? Appuie encore pour supprimer.</p>}
      {generate.error && <ErrorNote message={generate.error.message} />}

      {cards.length === 0 && !generate.isPending && (
        <Card>
          <p className="font-display text-2xl font-extrabold">Pas encore de questions.</p>
          <p className="text-muted">Je les crée à partir de ta leçon.</p>
        </Card>
      )}

      <ul className="flex flex-col gap-3">
        {cards.map((card) => (
          <li key={card.id}>
            <Card className="flex flex-col gap-2 p-4">
              <div className="flex items-center gap-2">
                <span className="flex-1 text-sm font-semibold tracking-wide text-muted uppercase">
                  {TYPE_LABELS[card.type]}
                </span>
                <IconButton label="Corriger la carte" onClick={() => setEditing(card)}>
                  <Pencil strokeWidth={2.5} />
                </IconButton>
                <IconButton
                  label={confirmDelete === card.id ? 'Confirmer la suppression' : 'Supprimer la carte'}
                  onClick={() => onDeleteCard(card.id)}
                  className={confirmDelete === card.id ? 'bg-coral text-[#17172B]' : ''}
                >
                  <Trash2 strokeWidth={2.5} />
                </IconButton>
              </div>
              <p className="font-semibold">{card.question}</p>
              <p className="text-muted">→ {card.answer}</p>
            </Card>
          </li>
        ))}
      </ul>

      <Sheet open={editing !== null}>
        {editing && (
          <CardEditor
            key={editing.id}
            card={editing}
            saving={updateCard.isPending}
            error={updateCard.error?.message ?? null}
            onCancel={() => {
              updateCard.reset()
              setEditing(null)
            }}
            onSave={(update) =>
              updateCard.mutate({ id: editing.id, ...update }, { onSuccess: () => setEditing(null) })
            }
          />
        )}
      </Sheet>

      {!editing && (
        <BottomBar>
          {cards.length > 0 ? (
            <Button onClick={() => navigate(`/seance?lecon=${lessonId}`)}>Réviser cette leçon</Button>
          ) : (
            <Button disabled={generate.isPending} onClick={() => generate.mutate(lessonId)}>
              {generate.isPending ? 'Je prépare tes questions…' : 'Créer les questions'}
            </Button>
          )}
        </BottomBar>
      )}
    </Page>
  )
}
