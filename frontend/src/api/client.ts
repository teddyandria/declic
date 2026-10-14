const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

/** Appel JSON vers l'API. Lève une erreur si la réponse n'est pas 2xx. */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    throw new Error(`API ${response.status} sur ${path}`)
  }
  return (await response.json()) as T
}
