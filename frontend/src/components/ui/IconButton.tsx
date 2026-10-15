import type { ButtonHTMLAttributes, ReactNode } from 'react'

type IconButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  label: string
  children: ReactNode
}

/** Bouton icône carré de 48 px (cible tactile minimale). `label` est lu par les lecteurs d'écran. */
export function IconButton({ label, children, className = '', type = 'button', ...props }: IconButtonProps) {
  return (
    <button
      type={type}
      aria-label={label}
      title={label}
      className={`pop-border flex size-12 shrink-0 items-center justify-center rounded-card bg-surface text-text shadow-pop transition-[translate,box-shadow] duration-100 active:translate-y-1 active:shadow-none ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
