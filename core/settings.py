"""
settings.py ? Gerenciamento de Configuracoes e Persistencia

Objetivo Macro:
    Centralizar todas as preferencias do usuario e calculos de tempo,
    persistindo os valores no armazenamento local via QSettings.

Fluxo Logico:
    1. Origem: Valores padrao definidos como constantes.
    2. Transformacao: Normalizacao tipada de valores (int, bool, str).
    3. Destino: Leitura/escrita no escopo de usuario do app.
"""

from PyQt6.QtCore import QSettings


DEFAULT_FOCUS_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_FOCUS_COUNT = 4
DEFAULT_BREAK_DURATION = 5
DEFAULT_LONG_BREAK_ENABLED = True
DEFAULT_LONG_BREAK_DURATION = 15
DEFAULT_SESSIONS_BEFORE_LONG = 4
DEFAULT_THEME = "dark"

ORG_NAME = "PomodoroTimer"
APP_NAME = "PomodoroTimer"


class AppSettings:
    """Fachada tipada para persistencia de configuracoes do app."""

    def __init__(self):
        self._store = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            ORG_NAME,
            APP_NAME,
        )

    @property
    def focus_minutes(self) -> int:
        return int(self._store.value("session/focus_minutes", DEFAULT_FOCUS_MINUTES))

    @focus_minutes.setter
    def focus_minutes(self, value: int):
        self._store.setValue("session/focus_minutes", max(1, int(value)))

    @property
    def sessions_before_long(self) -> int:
        return int(self._store.value("session/sessions_before_long", DEFAULT_SESSIONS_BEFORE_LONG))

    @sessions_before_long.setter
    def sessions_before_long(self, value: int):
        self._store.setValue("session/sessions_before_long", max(1, int(value)))

    @property
    def theme(self) -> str:
        return str(self._store.value("ui/theme", DEFAULT_THEME))

    @theme.setter
    def theme(self, value: str):
        self._store.setValue("ui/theme", value if value in ("dark", "light") else "dark")

    @property
    def short_break_minutes(self) -> int:
        stored = self._store.value("session/short_break_minutes", None)
        if stored is None:
            return max(3, round(self.focus_minutes * 0.20))
        return max(1, int(stored))

    @short_break_minutes.setter
    def short_break_minutes(self, value: int):
        self._store.setValue("session/short_break_minutes", max(1, int(value)))

    @property
    def focus_count(self) -> int:
        stored = self._store.value("session/focus_count", DEFAULT_FOCUS_COUNT)
        return max(1, int(stored))

    @focus_count.setter
    def focus_count(self, value: int):
        self._store.setValue("session/focus_count", max(1, int(value)))

    @property
    def break_duration(self) -> int:
        stored = self._store.value("session/break_duration", DEFAULT_BREAK_DURATION)
        return max(1, int(stored))

    @break_duration.setter
    def break_duration(self, value: int):
        self._store.setValue("session/break_duration", max(1, int(value)))

    @property
    def long_break_enabled(self) -> bool:
        stored = self._store.value("session/long_break_enabled", DEFAULT_LONG_BREAK_ENABLED)
        if isinstance(stored, bool):
            return stored
        return str(stored).strip().lower() in ("1", "true", "yes", "on")

    @long_break_enabled.setter
    def long_break_enabled(self, value: bool):
        self._store.setValue("session/long_break_enabled", bool(value))

    @property
    def long_break_duration(self) -> int:
        stored = self._store.value("session/long_break_duration", DEFAULT_LONG_BREAK_DURATION)
        return max(1, int(stored))

    @long_break_duration.setter
    def long_break_duration(self, value: int):
        self._store.setValue("session/long_break_duration", max(1, int(value)))

    @property
    def long_break_minutes(self) -> int:
        return self.long_break_duration

    @property
    def sessions_today(self) -> int:
        return int(self._store.value("history/sessions_today", 0))

    @sessions_today.setter
    def sessions_today(self, value: int):
        self._store.setValue("history/sessions_today", int(value))

    @property
    def focus_minutes_today(self) -> int:
        return int(self._store.value("history/focus_minutes_today", 0))

    @focus_minutes_today.setter
    def focus_minutes_today(self, value: int):
        self._store.setValue("history/focus_minutes_today", int(value))

    def increment_session(self, focus_duration_minutes: int):
        self.sessions_today = self.sessions_today + 1
        self.focus_minutes_today = self.focus_minutes_today + int(focus_duration_minutes)

    def save(self):
        self._store.sync()
