import type { ButtonHTMLAttributes } from 'react'

type Variant = 'primary' | 'secondary'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant
}

const variants: Record<Variant, string> = {
  primary: 'bg-pen text-white',
  secondary: 'bg-surface text-text',
}

/**
 * Bouton « tampon » : il s'enfonce de 4 px et perd son ombre quand on appuie.
 * `primary` = l'action principale de l'écran (une seule par écran).
 */
export function Button({ variant = 'primary', className = '', type = 'button', ...props }: ButtonProps) {
  return (
    <button
      type={type}
      className={[
        'pop-border flex min-h-14 w-full items-center justify-center gap-2 rounded-card px-6',
        'font-display text-xl font-extrabold shadow-pop',
        'transition-[translate,box-shadow] duration-100',
        'active:translate-y-1 active:shadow-none',
        'disabled:cursor-not-allowed disabled:border-muted disabled:bg-muted/30 disabled:text-muted',
        'disabled:shadow-none disabled:active:translate-y-0',
        variants[variant],
        className,
      ].join(' ')}
      {...props}
    />
  )
}
