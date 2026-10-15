type TrouProps = {
  value: string
  correct: boolean | null
  onChange: (value: string) => void
}

/** Texte à trous : un seul champ, validation avec Entrée ou le bouton du bas. */
export function Trou({ value, correct, onChange }: TrouProps) {
  const background = correct === null ? 'bg-surface' : correct ? 'bg-mint/25' : 'bg-coral/25'
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      readOnly={correct !== null}
      autoFocus
      autoComplete="off"
      autoCapitalize="off"
      spellCheck={false}
      enterKeyHint="done"
      aria-label="Le mot manquant"
      placeholder="Le mot manquant"
      className={`pop-border min-h-16 w-full rounded-card px-4 text-xl font-semibold text-text shadow-pop placeholder:font-normal placeholder:text-muted ${background}`}
    />
  )
}
