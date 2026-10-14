import type { HTMLAttributes } from 'react'

/** Carte papier : fond blanc, contour épais, ombre décalée nette. */
export function Card({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`pop-border rounded-card bg-surface p-5 shadow-pop-lg ${className}`} {...props} />
}
