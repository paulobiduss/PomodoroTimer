"""
session_plan.py — Orquestrador do Plano de Sessoes

Objetivo Macro:
    Gerenciar a sequencia finita de estados do ciclo Pomodoro,
    determinando qual e o proximo estado e quando o plano se encerra.

Fluxo Logico:
    1. Origem: AppSettings injeta os parametros do plano na instanciacao.
    2. Transformacao: A cada chamada de advance(), o plano avanca um passo
       na sequencia e retorna o estado e duracao do proximo bloco.
    3. Destino: Emite o sinal `plan_finished` quando todos os blocos
       foram consumidos, ou retorna (state, duration_seconds) caso contrario.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from core.constants import STATE_FOCUS, STATE_SHORT_BREAK, STATE_LONG_BREAK


class SessionPlan(QObject):
    """Fonte unica da verdade para a sequencia do plano."""

    plan_finished = pyqtSignal()

    def __init__(
        self,
        focus_count: int,
        focus_duration: int,
        break_duration: int,
        long_break_enabled: bool,
        long_break_duration: int,
    ):
        super().__init__()
        self._focus_count = max(1, int(focus_count))
        self._focus_duration = max(1, int(focus_duration))
        self._break_duration = max(1, int(break_duration))
        self._long_break_enabled = bool(long_break_enabled)
        self._long_break_duration = max(1, int(long_break_duration))
        self._blocks: list[tuple[str, int]] = []
        self._cursor = 0
        self._build_sequence()

    @property
    def blocks(self) -> list[tuple[str, int]]:
        return list(self._blocks)

    def _build_sequence(self):
        self._blocks.clear()
        for i in range(self._focus_count):
            self._blocks.append((STATE_FOCUS, self._focus_duration * 60))
            is_last_focus = i == self._focus_count - 1
            if not is_last_focus:
                self._blocks.append((STATE_SHORT_BREAK, self._break_duration * 60))

        if self._long_break_enabled:
            self._blocks.append((STATE_LONG_BREAK, self._long_break_duration * 60))

        self._cursor = 0

    def current_block(self) -> tuple[str, int]:
        if not self._blocks:
            raise RuntimeError("SessionPlan sem blocos configurados.")
        idx = min(self._cursor, len(self._blocks) - 1)
        return self._blocks[idx]

    def advance(self) -> tuple[str, int] | None:
        self._cursor += 1
        if self._cursor >= len(self._blocks):
            self._cursor = len(self._blocks)
            self.plan_finished.emit()
            return None
        return self._blocks[self._cursor]

    def progress(self) -> tuple[int, int]:
        total = len(self._blocks)
        done = min(self._cursor, total)
        return done, total

    def reset(self):
        self._cursor = 0
