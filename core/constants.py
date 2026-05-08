"""
constants.py ? Estados Globais e Constantes do PomodoroTimer

Objetivo Macro:
    Centralizar as constantes de estado do Pomodoro e
    seus respectivos rotulos/cores.

Fluxo Logico:
    1. Origem: Definicoes de estado compartilhadas pelo core/UI.
    2. Destino: Importadas por timer_window, session_plan e overlays.
"""

STATE_FOCUS = "focus"
STATE_SHORT_BREAK = "short_break"
STATE_LONG_BREAK = "long_break"
STATE_COMPLETED = "completed"

STATE_LABELS = {
    STATE_FOCUS: ("Foco", "#e74c3c"),
    STATE_SHORT_BREAK: ("Intervalo Curto", "#2ecc71"),
    STATE_LONG_BREAK: ("Intervalo Longo", "#1f8ef1"),
    STATE_COMPLETED: ("Plano Concluido", "#F5A623"),
}
