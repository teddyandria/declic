import { Check } from 'lucide-react'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'

import { useRegister } from '../api/hooks'
import { BottomBar } from '../components/ui/BottomBar'
import { Button } from '../components/ui/Button'
import { ErrorNote } from '../components/ui/ErrorNote'
import { Field } from '../components/ui/Field'
import { Page } from '../components/ui/Page'

// Mêmes règles que le backend (schemas.RegisterBody) : on prévient avant d'envoyer.
const PSEUDO_RULE = /^[A-Za-z0-9_-]{3,20}$/
const MIN_PASSWORD = 8

export function Register() {
  const navigate = useNavigate()
  const register = useRegister()
  const [pseudo, setPseudo] = useState('')
  const [password, setPassword] = useState('')
  const [consent, setConsent] = useState(false)

  const pseudoOk = PSEUDO_RULE.test(pseudo)
  const passwordOk = password.length >= MIN_PASSWORD
  const canSubmit = pseudoOk && passwordOk && consent && !register.isPending

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!canSubmit) return
    register.mutate({ pseudo, password, consent: true }, { onSuccess: () => navigate('/', { replace: true }) })
  }

  return (
    <Page withBottomBar>
      <h1 className="text-4xl">Crée ton compte</h1>

      <form id="register" onSubmit={onSubmit} className="flex flex-col gap-4">
        {register.error && <ErrorNote message={register.error.message} />}
        <Field
          label="Pseudo"
          name="pseudo"
          value={pseudo}
          onChange={(e) => setPseudo(e.target.value.trim())}
          autoComplete="username"
          autoCapitalize="off"
          spellCheck={false}
          maxLength={20}
          hint="3 à 20 caractères : lettres, chiffres, _ ou -. Pas ton vrai nom."
        />
        <Field
          label="Mot de passe"
          name="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
          hint="8 caractères minimum. Pas d'e-mail : si tu l'oublies, on ne peut pas le retrouver."
        />

        <label className="pop-border flex min-h-14 cursor-pointer items-start gap-3 rounded-card bg-surface p-4">
          <input
            type="checkbox"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
            className="peer sr-only"
          />
          <span
            aria-hidden
            className={`pop-border mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-lg peer-focus-visible:outline-3 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-pen ${consent ? 'bg-pen text-white' : 'bg-surface'}`}
          >
            {consent && <Check size={18} strokeWidth={3} />}
          </span>
          <span>J'ai 15 ans ou plus, ou un parent est d'accord pour que j'utilise Déclic.</span>
        </label>
      </form>

      <Link to="/connexion" className="min-h-12 font-semibold text-pen underline underline-offset-4">
        Déjà un compte ? Connecte-toi
      </Link>

      <BottomBar>
        <Button type="submit" form="register" disabled={!canSubmit}>
          Créer mon compte
        </Button>
      </BottomBar>
    </Page>
  )
}
