import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'

import { useLogin } from '../api/hooks'
import { BottomBar } from '../components/ui/BottomBar'
import { Button } from '../components/ui/Button'
import { ErrorNote } from '../components/ui/ErrorNote'
import { Field } from '../components/ui/Field'
import { Page } from '../components/ui/Page'

export function Login() {
  const navigate = useNavigate()
  const login = useLogin()
  const [pseudo, setPseudo] = useState('')
  const [password, setPassword] = useState('')

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    login.mutate({ pseudo: pseudo.trim(), password }, { onSuccess: () => navigate('/', { replace: true }) })
  }

  return (
    <Page withBottomBar>
      <header className="flex flex-col gap-1">
        <h1 className="text-5xl">Déclic</h1>
        <p className="text-muted">Ta leçon en 5 minutes. Pas plus.</p>
      </header>

      <form id="login" onSubmit={onSubmit} className="flex flex-col gap-4">
        {login.error && <ErrorNote message={login.error.message} />}
        <Field
          label="Pseudo"
          name="pseudo"
          value={pseudo}
          onChange={(e) => setPseudo(e.target.value)}
          autoComplete="username"
          autoCapitalize="off"
          spellCheck={false}
        />
        <Field
          label="Mot de passe"
          name="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
        />
      </form>

      <Link to="/inscription" className="min-h-12 font-semibold text-pen underline underline-offset-4">
        Pas encore de compte ? Crée-le
      </Link>

      <BottomBar>
        <Button type="submit" form="login" disabled={!pseudo.trim() || !password || login.isPending}>
          Se connecter
        </Button>
      </BottomBar>
    </Page>
  )
}
