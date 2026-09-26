import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from core.constants import STATE_FOCUS, STATE_SHORT_BREAK
from core.session_plan import SessionPlan
from ui.theme import gradient_for
from ui.windows.timer_window import TimerWindow


class FakeFocusHistory:
    def compact_summary_text(self) -> str:
        return "Hoje: 0min | Ontem: igual a ontem | Semana: 0min"


class FakeAppSettings:
    """Substitui AppSettings para nao gravar no QSettings real do usuario."""

    def __init__(self, theme: str = "dark"):
        self.theme = theme
        self.focus_count = 2
        self.focus_minutes = 25
        self.break_duration = 5
        self.short_break_minutes = 5
        self.long_break_enabled = False
        self.long_break_duration = 15
        self.focus_history = FakeFocusHistory()
        self.saved = 0

    def save(self):
        self.saved += 1

    def record_focus_session(self, minutes: int):
        pass


def build_window(settings: FakeAppSettings) -> TimerWindow:
    plan = SessionPlan(focus_count=2, focus_duration=25, break_duration=5,
                       long_break_enabled=False, long_break_duration=15)
    return TimerWindow(settings, plan)


class TimerWindowThemeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_state_label_uses_focus_gradient_on_start(self):
        window = build_window(FakeAppSettings())
        self.assertIn(gradient_for(STATE_FOCUS)[0], window._state_badge.styleSheet())

    def test_accent_follows_state_after_skip(self):
        # Regressao: trocar o QSS da janela inteira deixava rotulo/botao com a cor do foco.
        window = build_window(FakeAppSettings())
        window.skip_session()
        start, _ = gradient_for(STATE_SHORT_BREAK)
        self.assertIn(start, window._state_badge.styleSheet())
        self.assertIn(start, window._start_pause_btn.styleSheet())

    def test_toggle_theme_switches_and_persists(self):
        settings = FakeAppSettings("dark")
        window = build_window(settings)
        window._toggle_theme()
        self.assertEqual("light", settings.theme)
        self.assertEqual(1, settings.saved)

    def test_toggle_theme_emits_new_theme(self):
        window = build_window(FakeAppSettings("dark"))
        received = []
        window.theme_changed.connect(received.append)
        window._toggle_theme()
        self.assertEqual(["light"], received)

    def test_settings_panel_starts_hidden_and_toggles(self):
        window = build_window(FakeAppSettings())
        window.show()
        self.assertFalse(window._settings_card.isVisible())
        window._settings_btn.setChecked(True)
        window._toggle_settings_panel()
        self.assertTrue(window._settings_card.isVisible())
        window.close()


if __name__ == "__main__":
    unittest.main()
