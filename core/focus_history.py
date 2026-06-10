"""
focus_history.py - Historico Diario de Foco

Objetivo Macro:
    Registrar minutos de foco por data e gerar um resumo comparativo
    simples para a interface principal.

Fluxo Logico:
    1. Origem: Blocos de foco concluidos pelo TimerWindow.
    2. Transformacao: Persistencia por dia, comparacao com ontem e soma semanal.
    3. Destino: Texto compacto consumido pela UI e pelo overlay de conclusao.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable


DAILY_PREFIX = "history/daily_focus_minutes"
LEGACY_FOCUS_TODAY_KEY = "history/focus_minutes_today"
MIGRATION_DONE_KEY = "history/daily_migration_done"


@dataclass(frozen=True)
class FocusHistorySummary:
    """Resumo pronto para exibicao do historico de foco."""

    today_minutes: int
    yesterday_minutes: int
    weekly_minutes: int

    @property
    def delta_minutes(self) -> int:
        return self.today_minutes - self.yesterday_minutes


class FocusHistory:
    """Camada de persistencia e leitura do foco diario."""

    def __init__(self, store, today_provider: Callable[[], date] = date.today):
        self._store = store
        self._today_provider = today_provider

    def migrate_legacy_today(self):
        if self._as_bool(self._store.value(MIGRATION_DONE_KEY, False)):
            return

        legacy_minutes = self._as_int(self._store.value(LEGACY_FOCUS_TODAY_KEY, 0))
        if legacy_minutes > 0 and self.minutes_for(self.today()) == 0:
            self.add_focus_minutes(legacy_minutes, self.today())

        self._store.setValue(MIGRATION_DONE_KEY, True)

    def add_focus_minutes(self, minutes: int, day: date | None = None):
        normalized_minutes = max(0, int(minutes))
        if normalized_minutes == 0:
            return

        target_day = day or self.today()
        current_minutes = self.minutes_for(target_day)
        self._store.setValue(self._daily_key(target_day), current_minutes + normalized_minutes)

    def minutes_for(self, day: date) -> int:
        return self._as_int(self._store.value(self._daily_key(day), 0))

    def summary(self) -> FocusHistorySummary:
        today = self.today()
        yesterday = today - timedelta(days=1)
        return FocusHistorySummary(
            today_minutes=self.minutes_for(today),
            yesterday_minutes=self.minutes_for(yesterday),
            weekly_minutes=self.weekly_minutes(today),
        )

    def compact_summary_text(self) -> str:
        summary = self.summary()
        return (
            f"Hoje: {self._format_duration(summary.today_minutes)} | "
            f"Ontem: {self._format_delta(summary.delta_minutes)} | "
            f"Semana: {self._format_duration(summary.weekly_minutes)}"
        )

    def weekly_minutes(self, reference_day: date | None = None) -> int:
        target_day = reference_day or self.today()
        week_start = target_day - timedelta(days=target_day.weekday())
        return sum(self.minutes_for(week_start + timedelta(days=offset)) for offset in range(7))

    def today(self) -> date:
        return self._today_provider()

    def _daily_key(self, day: date) -> str:
        return f"{DAILY_PREFIX}/{day.isoformat()}"

    def _format_duration(self, minutes: int) -> str:
        hours = max(0, minutes) // 60
        remaining = max(0, minutes) % 60
        if hours == 0:
            return f"{remaining}min"
        return f"{hours}h{remaining:02d}"

    def _format_delta(self, delta_minutes: int) -> str:
        if delta_minutes == 0:
            return "igual a ontem"
        sign = "+" if delta_minutes > 0 else "-"
        return f"{sign}{self._format_duration(abs(delta_minutes))}"

    def _as_int(self, value) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _as_bool(self, value) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")
