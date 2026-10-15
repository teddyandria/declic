import type { ReactNode } from 'react'

/** Zone fixée en bas pour LE bouton principal de l'écran, à portée de pouce. */
export function BottomBar({ children }: { children: ReactNode }) {
  return (
    <div className="fixed inset-x-0 bottom-0 z-40 bg-gradient-to-t from-paper from-70% to-transparent px-4 pt-6 pb-[max(1.25rem,env(safe-area-inset-bottom))]">
      <div className="mx-auto max-w-lg">{children}</div>
    </div>
  )
}
