"""Gamification : XP, niveaux, série de jours.

Fonctions pures (pas de base de données) pour être faciles à tester.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

XP_CORRECT = 10
XP_WRONG = 2  # l'erreur n'est jamais punie : on gagne quand même un peu
XP_SESSION_END = 20

PARIS = ZoneInfo("Europe/Paris")


def xp_for_answer(correct: bool) -> int:
    return XP_CORRECT if correct else XP_WRONG


def level_threshold(level: int) -> int:
    """XP total pour atteindre un niveau : 0, 100, 250, 450, 700, 1000, 1350…

    Chaque palier coûte 50 XP de plus que le précédent.
    """
    steps = level - 1
    return 100 * steps + 25 * steps * (steps - 1)


@dataclass(frozen=True)
class LevelInfo:
    level: int
    xp_into_level: int  # XP gagnés depuis le début du niveau
    xp_for_next: int  # XP nécessaires pour passer ce niveau


def level_info(xp: int) -> LevelInfo:
    level = 1
    while xp >= level_threshold(level + 1):
        level += 1
    start = level_threshold(level)
    return LevelInfo(level=level, xp_into_level=xp - start, xp_for_next=level_threshold(level + 1) - start)


def paris_today(now: datetime) -> date:
    """Le jour de l'ado, à Paris (pas en UTC) : 00h30 à Paris compte pour le nouveau jour.

    Une date sans fuseau (SQLite les renvoie ainsi) est en UTC : c'est ce qu'on enregistre.
    """
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)
    return now.astimezone(PARIS).date()


def next_streak(streak: int, last_played: date | None, today: date) -> int:
    """Série après une séance jouée `today`.

    Même jour → inchangée ; lendemain → +1 ; plus tard (ou première fois) → repart à 1.
    """
    if last_played == today:
        return max(streak, 1)
    if last_played == today - timedelta(days=1):
        return streak + 1
    return 1


def current_streak(streak: int, last_played: date | None, today: date) -> int:
    """Série à afficher : tombe à 0 si l'ado n'a joué ni aujourd'hui ni hier."""
    if last_played is None or last_played < today - timedelta(days=1):
        return 0
    return streak
