from datetime import UTC, date, datetime

import pytest

from app.game import current_streak, level_info, level_threshold, next_streak, paris_today, xp_for_answer


def test_xp_par_reponse() -> None:
    assert xp_for_answer(True) == 10
    assert xp_for_answer(False) == 2  # jamais zéro


def test_seuils_de_niveau() -> None:
    assert [level_threshold(n) for n in range(1, 8)] == [0, 100, 250, 450, 700, 1000, 1350]


@pytest.mark.parametrize(
    ("xp", "level", "into", "needed"),
    [(0, 1, 0, 100), (99, 1, 99, 100), (100, 2, 0, 150), (260, 3, 10, 200), (1000, 6, 0, 350)],
)
def test_niveau_selon_xp(xp: int, level: int, into: int, needed: int) -> None:
    info = level_info(xp)
    assert (info.level, info.xp_into_level, info.xp_for_next) == (level, into, needed)


D = date(2026, 10, 15)


def test_serie_premiere_seance() -> None:
    assert next_streak(0, None, D) == 1


def test_serie_meme_jour_inchangee() -> None:
    assert next_streak(4, D, D) == 4


def test_serie_lendemain_plus_un() -> None:
    assert next_streak(4, date(2026, 10, 14), D) == 5


def test_serie_jour_saute_repart_a_un() -> None:
    assert next_streak(4, date(2026, 10, 13), D) == 1


def test_serie_changement_de_mois() -> None:
    assert next_streak(2, date(2026, 9, 30), date(2026, 10, 1)) == 3


def test_paris_minuit_compte_pour_le_nouveau_jour() -> None:
    # 22h30 UTC le 15 = 00h30 le 16 à Paris (heure d'été, UTC+2)
    assert paris_today(datetime(2026, 10, 15, 22, 30, tzinfo=UTC)) == date(2026, 10, 16)
    # 21h59 UTC le 15 = 23h59 le 15 à Paris
    assert paris_today(datetime(2026, 10, 15, 21, 59, tzinfo=UTC)) == date(2026, 10, 15)


def test_paris_minuit_en_hiver() -> None:
    # Heure d'hiver (UTC+1) : 23h30 UTC le 15 décembre = 00h30 le 16 à Paris
    assert paris_today(datetime(2026, 12, 15, 23, 30, tzinfo=UTC)) == date(2026, 12, 16)


def test_seance_a_23h59_puis_00h01_allonge_la_serie() -> None:
    before = paris_today(datetime(2026, 10, 15, 21, 59, tzinfo=UTC))  # 23h59 à Paris
    after = paris_today(datetime(2026, 10, 15, 22, 1, tzinfo=UTC))  # 00h01 à Paris
    assert next_streak(next_streak(0, None, before), before, after) == 2


def test_seance_a_1h_utc_meme_jour_a_paris() -> None:
    # 23h UTC le 14 et 1h UTC le 15 : en UTC deux jours, à Paris le même jour (15)
    first = paris_today(datetime(2026, 10, 14, 23, 0, tzinfo=UTC))
    second = paris_today(datetime(2026, 10, 15, 1, 0, tzinfo=UTC))
    assert next_streak(1, first, second) == 1


def test_serie_affichee() -> None:
    assert current_streak(5, D, D) == 5
    assert current_streak(5, date(2026, 10, 14), D) == 5  # pas encore joué aujourd'hui : la série tient
    assert current_streak(5, date(2026, 10, 13), D) == 0
    assert current_streak(0, None, D) == 0
