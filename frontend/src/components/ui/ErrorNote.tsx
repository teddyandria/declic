import { TriangleAlert } from 'lucide-react'

/** Message d'erreur court, icône + texte (jamais la couleur seule). */
export function ErrorNote({ message }: { message: string }) {
  return (
    <p role="alert" className="pop-border flex items-start gap-2 rounded-card bg-coral/15 px-4 py-3">
      <TriangleAlert className="mt-0.5 shrink-0 text-coral" strokeWidth={2.5} aria-hidden />
      {message}
    </p>
  )
}
