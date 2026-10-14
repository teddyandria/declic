"""Génère les cartes des leçons de référence et écrit un rapport lisible par leçon dans eval/out/.

À relancer après chaque changement de prompt ou de modèle, puis comparer avec `git diff eval/out/`.

    uv run python eval/run_eval.py
"""

import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # pour importer app/

from app.config import settings  # noqa: E402
from app.generate import MAX_CARDS, CardDraft, clean_card, count_words, request_deck  # noqa: E402

EVAL_DIR = Path(__file__).resolve().parent
LESSONS_DIR = EVAL_DIR / "lessons"
OUT_DIR = EVAL_DIR / "out"


def format_card(index: int, card: CardDraft) -> str:
    lines = [f"{index}. **[{card.type}]** {card.question} _({count_words(card.question)} mots)_"]
    if card.choices:
        lines.append("   - Choix : " + " · ".join(f"**{c}**" if c == card.answer else c for c in card.choices))
    lines.append(f"   - Réponse : {card.answer}")
    lines.append(f"   - Explication : {card.explanation}")
    return "\n".join(lines)


def evaluate(lesson_path: Path) -> tuple[int, int]:
    """Écrit eval/out/<leçon>.md et renvoie (cartes gardées, cartes générées)."""
    text = lesson_path.read_text(encoding="utf-8")
    deck = request_deck(text)

    kept: list[CardDraft] = []
    rejected: list[CardDraft] = []
    for draft in deck.cards:
        card = clean_card(draft)
        if card:
            kept.append(card)
        else:
            rejected.append(draft)
    kept = kept[:MAX_CARDS]
    types = Counter(card.type for card in kept)

    report = [
        f"# {text.splitlines()[0]}",
        "",
        f"- Modèle : `{settings.llm_model}` — {date.today().isoformat()}",
        f"- Cartes gardées : **{len(kept)}** / {len(deck.cards)} générées",
        f"- Types : qcm {types['qcm']} · vrai_faux {types['vrai_faux']} · trou {types['trou']}",
        "",
        "## Cartes",
        "",
        *(format_card(i, card) for i, card in enumerate(kept, 1)),
    ]
    if rejected:
        report += ["", "## Écartées par la validation", "", *(format_card(i, c) for i, c in enumerate(rejected, 1))]
    report += [
        "",
        "## À vérifier à la main",
        "",
        "- [ ] Chaque info est bien dans la leçon (aucune invention)",
        "- [ ] Une seule bonne réponse possible par QCM",
        "- [ ] Questions claires pour un collégien",
        "",
    ]

    (OUT_DIR / f"{lesson_path.stem}.md").write_text("\n".join(report), encoding="utf-8")
    return len(kept), len(deck.cards)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    for lesson_path in sorted(LESSONS_DIR.glob("*.txt")):
        kept, total = evaluate(lesson_path)
        print(f"{lesson_path.stem:32} {kept:2} cartes gardées / {total} générées")
    print(f"\nRapports dans {OUT_DIR.relative_to(Path.cwd()) if OUT_DIR.is_relative_to(Path.cwd()) else OUT_DIR}")


if __name__ == "__main__":
    main()
