/** Jeton de connexion, gardé dans le navigateur. Tout est protégé : le stockage peut être bloqué. */

const KEY = 'declic.token'

/** Secours si localStorage est bloqué. */
let memoryToken: string | null = null

export function getToken(): string | null {
  try {
    return localStorage.getItem(KEY)
  } catch {
    return null
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(KEY, token)
  } catch {
    // stockage indisponible (navigation privée…) : la connexion durera le temps de l'onglet
  }
  memoryToken = token
}

export function clearToken(): void {
  try {
    localStorage.removeItem(KEY)
  } catch {
    // rien à faire
  }
  memoryToken = null
}

export function currentToken(): string | null {
  return getToken() ?? memoryToken
}
