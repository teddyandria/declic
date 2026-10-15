import { clearToken, currentToken } from '../lib/token'

const API_URL: string = import.meta.env.VITE_API_URL ?? '/api'

/** Erreur d'API avec le message lisible renvoyé par FastAPI (`detail`). */
export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const token = currentToken()
  const headers = new Headers(init.headers)
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, headers })
  } catch {
    throw new ApiError(0, 'Pas de connexion. Vérifie ton réseau.')
  }
  // Jeton absent, expiré ou compte supprimé : retour à l'écran de connexion.
  if (response.status === 401 && !path.startsWith('/auth/')) {
    clearToken()
    window.location.replace('/connexion')
  }
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null)
    const detail = (body as { detail?: unknown } | null)?.detail
    if (typeof detail === 'string') throw new ApiError(response.status, detail)
    // 502/503/504 : l'API est arrêtée ou injoignable (en dev, le proxy Vite répond à sa place).
    if (response.status >= 502 && response.status <= 504) {
      throw new ApiError(response.status, 'Le serveur ne répond pas. Réessaie dans un instant.')
    }
    throw new ApiError(response.status, 'Un truc a planté côté serveur. Réessaie.')
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

/** Appel JSON vers l'API. */
export function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  return request<T>(path, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } })
}

/** Formulaire classique (application/x-www-form-urlencoded), attendu par /auth/login. */
export function apiPostForm<T>(path: string, fields: Record<string, string>): Promise<T> {
  return request<T>(path, { method: 'POST', body: new URLSearchParams(fields) })
}

/** Envoi de fichier (multipart) : le navigateur pose lui-même le Content-Type. */
export function apiUpload<T>(path: string, form: FormData): Promise<T> {
  return request<T>(path, { method: 'POST', body: form })
}
