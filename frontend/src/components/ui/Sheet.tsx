import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import type { ReactNode } from 'react'

type SheetProps = {
  open: boolean
  children: ReactNode
  className?: string
  /** Attente avant l'entrée (s) : laisse finir une autre animation, une seule chose bouge à la fois. */
  delay?: number
}

/** Panneau qui monte du bas (feedback de réponse). `aria-live` pour les lecteurs d'écran. */
export function Sheet({ open, children, className = '', delay = 0 }: SheetProps) {
  const reduceMotion = useReducedMotion()
  const hidden = reduceMotion ? { opacity: 0 } : { y: '100%' }

  return (
    <div aria-live="polite">
      <AnimatePresence>
        {open && (
          <motion.div
            initial={hidden}
            animate={{ y: 0, opacity: 1 }}
            exit={hidden}
            transition={{ type: 'spring', duration: 0.3, bounce: 0.2, delay }}
            className={`pop-border fixed inset-x-0 bottom-0 z-50 mx-auto flex max-w-lg flex-col gap-4 rounded-t-[24px] border-b-0 bg-surface p-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] ${className}`}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
