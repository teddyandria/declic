import type { ReactNode } from 'react'
import { Navigate } from 'react-router'

import { currentToken } from '../lib/token'

/** Écrans réservés aux connectés : sans jeton, direction la connexion. */
export function RequireAuth({ children }: { children: ReactNode }) {
  if (!currentToken()) return <Navigate to="/connexion" replace />
  return children
}
