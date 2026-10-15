import { useQueryClient } from '@tanstack/react-query'
import { ArrowLeft } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router'

import { useDeleteAccount, useMe } from '../api/hooks'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { ErrorNote } from '../components/ui/ErrorNote'
import { IconButton } from '../components/ui/IconButton'
import { Page } from '../components/ui/Page'
import { Sheet } from '../components/ui/Sheet'
import { clearToken } from '../lib/token'

const DATE = new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })

export function Data() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const me = useMe()
  const deleteAccount = useDeleteAccount()
  const [confirming, setConfirming] = useState(false)

  function leave() {
    clearToken()
    queryClient.clear()
    navigate('/connexion', { replace: true })
  }

  return (
    <Page>
      <header className="flex items-center gap-3">
        <IconButton label="Retour" onClick={() => navigate('/')}>
          <ArrowLeft strokeWidth={2.5} />
        </IconButton>
        <h1 className="text-3xl">Tes données</h1>
      </header>

      {me.data && (
        <Card className="flex flex-col gap-1">
          <p className="font-display text-2xl font-extrabold">{me.data.pseudo}</p>
          <p className="text-muted">Compte créé le {DATE.format(new Date(me.data.created_at))}</p>
        </Card>
      )}

      <section className="flex flex-col gap-2">
        <h2 className="text-2xl">Ce qu'on garde</h2>
        <ul className="flex list-disc flex-col gap-1 pl-6">
          <li>Ton pseudo et ton mot de passe (chiffré : illisible, même pour nous).</li>
          <li>Tes leçons et leurs questions.</li>
          <li>Tes réponses (juste ou faux, et quand), pour savoir quand reposer une question.</li>
          <li>Ton XP et ta série.</li>
        </ul>
        <p>Pas d'e-mail, pas de nom, pas d'âge.</p>
      </section>

      <section className="flex flex-col gap-2">
        <h2 className="text-2xl">Ce qui part à l'IA</h2>
        <p>
          Seulement le texte ou la photo de ta leçon, envoyé à OpenAI pour fabriquer les questions. Jamais ton pseudo.
        </p>
      </section>

      <div className="mt-auto flex flex-col gap-4 pt-4">
        <Button variant="secondary" onClick={leave}>
          Se déconnecter
        </Button>
        <Button variant="danger" onClick={() => setConfirming(true)}>
          Supprimer mon compte
        </Button>
      </div>

      <Sheet open={confirming}>
        <h2 className="text-2xl">Tout supprimer ?</h2>
        <p>Leçons, questions, XP, série : tout est effacé. Impossible de revenir en arrière.</p>
        {deleteAccount.error && <ErrorNote message={deleteAccount.error.message} />}
        <Button
          variant="danger"
          disabled={deleteAccount.isPending}
          onClick={() => deleteAccount.mutate(undefined, { onSuccess: leave })}
        >
          Oui, tout supprimer
        </Button>
        <button
          type="button"
          onClick={() => setConfirming(false)}
          className="min-h-12 font-semibold text-muted underline"
        >
          Annuler
        </button>
      </Sheet>
    </Page>
  )
}
