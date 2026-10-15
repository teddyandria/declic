from datetime import UTC, datetime, timedelta

from app.models import Card, Lesson
from app.scheduler import due_date, is_mastered, pick_session_cards, review

NOW = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)


def make_card(card_id: int, fsrs_state: dict[str, object] | None = None, lesson: Lesson | None = None) -> Card:
    lesson = lesson or Lesson(id=1, user_id=1, title="L", text="t", created_at=NOW)
    return Card(id=card_id, lesson_id=lesson.id, type="trou", question="q ___", answer="a",
                explanation="e", fsrs_state=fsrs_state, lesson=lesson)


def test_carte_ratee_revient_avant_carte_reussie() -> None:
    failed = review(None, correct=False, now=NOW)
    passed = review(None, correct=True, now=NOW)
    assert due_date(failed) < due_date(passed)


def test_reussir_plusieurs_fois_eloigne_la_carte_et_la_maitrise() -> None:
    state = review(None, correct=True, now=NOW)
    assert not is_mastered(state)
    state = review(state, correct=True, now=due_date(state))
    assert is_mastered(state)
    assert due_date(state) - NOW >= timedelta(days=1)


def test_session_dues_d_abord_puis_nouvelles() -> None:
    very_late = make_card(1, review(None, correct=False, now=NOW - timedelta(days=3)))
    late = make_card(2, review(None, correct=False, now=NOW - timedelta(days=1)))
    not_due = make_card(3, review(review(None, True, NOW), True, NOW + timedelta(minutes=10)))
    new = make_card(4)
    assert pick_session_cards([new, not_due, late, very_late], NOW) == [very_late, late, new]


def test_session_limitee_a_10_cartes() -> None:
    assert len(pick_session_cards([make_card(i) for i in range(15)], NOW)) == 10


def test_nouvelles_cartes_de_la_lecon_la_plus_recente_d_abord() -> None:
    old = Lesson(id=1, user_id=1, title="Vieille", text="t", created_at=NOW - timedelta(days=5))
    recent = Lesson(id=2, user_id=1, title="Récente", text="t", created_at=NOW)
    cards = [make_card(1, lesson=old), make_card(2, lesson=recent)]
    assert [c.id for c in pick_session_cards(cards, NOW)] == [2, 1]
