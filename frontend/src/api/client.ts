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
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, init)
  } catch {
    throw new ApiError(0, 'Pas de connexion. Vérifie ton réseau.')
  }
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null)
    const detail = (body as { detail?: unknown } | null)?.detail
    throw new ApiError(response.status, typeof detail === 'string' ? detail : 'Un truc a planté. Réessaie.')
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

/** Appel JSON vers l'API. */
export function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  return request<T>(path, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } })
}

/** Envoi de fichier (multipart) : le navigateur pose lui-même le Content-Type. */
export function apiUpload<T>(path: string, form: FormData): Promise<T> {
  return request<T>(path, { method: 'POST', body: form })
}
