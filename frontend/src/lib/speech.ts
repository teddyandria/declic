/** Lecture à voix haute avec la synthèse vocale du navigateur, en français. */

export const canSpeak = typeof window !== 'undefined' && 'speechSynthesis' in window

export function speak(text: string): void {
  if (!canSpeak) return
  window.speechSynthesis.cancel() // un nouvel appui relance depuis le début
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'fr-FR'
  utterance.rate = 0.95
  const voice = window.speechSynthesis.getVoices().find((v) => v.lang.startsWith('fr'))
  if (voice) utterance.voice = voice
  window.speechSynthesis.speak(utterance)
}

export function stopSpeaking(): void {
  if (canSpeak) window.speechSynthesis.cancel()
}
