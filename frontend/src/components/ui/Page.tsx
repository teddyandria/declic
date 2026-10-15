import type { ReactNode } from 'react'

/** Colonne mobile centrée. `withBottomBar` réserve la place du bouton fixé en bas. */
export function Page({ children, withBottomBar = false }: { children: ReactNode; withBottomBar?: boolean }) {
  return (
    <main className={`mx-auto flex min-h-dvh max-w-lg flex-col gap-6 px-4 pt-6 ${withBottomBar ? 'pb-32' : 'pb-8'}`}>
      {children}
    </main>
  )
}
