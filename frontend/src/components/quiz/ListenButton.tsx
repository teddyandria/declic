import { Volume2 } from 'lucide-react'

import { canSpeak, speak } from '../../lib/speech'

/** Bouton « Écouter » : lit la question en français. Masqué si le navigateur ne sait pas parler. */
export function ListenButton({ text }: { text: string }) {
  if (!canSpeak) return null
  return (
    <button
      type="button"
      onClick={() => speak(text)}
      className="pop-border inline-flex min-h-12 items-center gap-2 self-start rounded-full bg-surface px-4 font-semibold text-text shadow-pop transition-[translate,box-shadow] duration-100 active:translate-y-1 active:shadow-none"
    >
      <Volume2 strokeWidth={2.5} aria-hidden /> Écouter
    </button>
  )
}
