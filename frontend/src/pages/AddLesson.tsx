import { ArrowLeft, Camera, LoaderCircle } from 'lucide-react'
import { useRef, useState } from 'react'
import type { ChangeEvent } from 'react'
import { useNavigate } from 'react-router'

import { useCreateLesson, useGenerateCards, useTranscribePhoto } from '../api/hooks'
import { BottomBar } from '../components/ui/BottomBar'
import { Button } from '../components/ui/Button'
import { ErrorNote } from '../components/ui/ErrorNote'
import { IconButton } from '../components/ui/IconButton'
import { Page } from '../components/ui/Page'

const MIN_TEXT = 20

/** Titre par défaut : la première ligne du texte, coupée proprement. */
function titleFrom(text: string): string {
  const firstLine = text.trim().split('\n')[0].trim()
  return firstLine.length <= 60 ? firstLine : `${firstLine.slice(0, 57).trimEnd()}…`
}

export function AddLesson() {
  const navigate = useNavigate()
  const fileInput = useRef<HTMLInputElement>(null)
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')

  const transcribe = useTranscribePhoto()
  const createLesson = useCreateLesson()
  const generate = useGenerateCards()

  const busyMessage = transcribe.isPending
    ? 'Je lis ta photo…'
    : createLesson.isPending || generate.isPending
      ? 'Je prépare tes questions…'
      : null
  const error = transcribe.error ?? createLesson.error

  async function onPhoto(event: ChangeEvent<HTMLInputElement>) {
    const photo = event.target.files?.[0]
    event.target.value = '' // pour pouvoir reprendre la même photo
    if (!photo) return
    const { text: transcribed } = await transcribe.mutateAsync(photo).catch(() => ({ text: '' }))
    if (!transcribed) return
    setText((current) => (current.trim() ? `${current.trim()}\n\n${transcribed}` : transcribed))
  }

  async function onSubmit() {
    const lesson = await createLesson
      .mutateAsync({ title: title.trim() || titleFrom(text), text })
      .catch(() => null)
    if (!lesson) return
    // Si la génération rate, la page de la leçon proposera de réessayer.
    await generate.mutateAsync(lesson.id).catch(() => null)
    navigate(`/lecons/${lesson.id}`, { replace: true })
  }

  if (busyMessage) {
    return (
      <Page>
        <div className="flex flex-1 flex-col items-center justify-center gap-4 text-center" role="status">
          <LoaderCircle className="size-12 animate-spin text-pen motion-reduce:animate-none" strokeWidth={2.5} />
          <p className="font-display text-2xl font-extrabold">{busyMessage}</p>
        </div>
      </Page>
    )
  }

  return (
    <Page withBottomBar>
      <header className="flex items-center gap-3">
        <IconButton label="Retour" onClick={() => navigate('/')}>
          <ArrowLeft strokeWidth={2.5} />
        </IconButton>
        <h1 className="text-3xl">Nouvelle leçon</h1>
      </header>

      {error && <ErrorNote message={error.message} />}

      <input ref={fileInput} type="file" accept="image/*" className="hidden" onChange={onPhoto} />
      <Button variant="secondary" onClick={() => fileInput.current?.click()}>
        <Camera strokeWidth={2.5} aria-hidden /> Prendre en photo
      </Button>

      <label className="flex flex-col gap-2">
        <span className="font-semibold">{text ? 'Relis et corrige si besoin' : 'Ou colle ton texte'}</span>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={10}
          placeholder="La photosynthèse est…"
          className="pop-border min-h-56 rounded-card bg-surface p-4 text-text placeholder:text-muted"
        />
      </label>

      <label className="flex flex-col gap-2">
        <span className="font-semibold">Titre (facultatif)</span>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={120}
          placeholder={text ? titleFrom(text) : 'Ex. La photosynthèse'}
          className="pop-border min-h-14 rounded-card bg-surface px-4 text-text placeholder:text-muted"
        />
      </label>

      <BottomBar>
        <Button disabled={text.trim().length < MIN_TEXT} onClick={onSubmit}>
          Créer mes questions
        </Button>
      </BottomBar>
    </Page>
  )
}
