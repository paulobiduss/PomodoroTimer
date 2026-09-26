import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QPushButton

from core.constants import STATE_COMPLETED, STATE_SHORT_BREAK
from ui.theme import DARK_PALETTE, LIGHT_PALETTE, gradient_for
from ui.tray import SystemTray
from ui.windows.overlay_window import OverlayWindow


class SilentOverlayWindow(OverlayWindow):
    """Overlay de transicao sem tocar som durante os testes."""

    def _play_notification_sound(self):
        pass


class FakeTimerWindow:
    pass


class OverlayThemeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_transition_uses_next_block_gradient(self):
        overlay = SilentOverlayWindow("Pausa curta", 25, 5, theme="dark")
        self.assertIn(gradient_for(STATE_SHORT_BREAK)[0], overlay._panel.styleSheet())
        overlay.close()

    def test_light_theme_uses_light_panel_colors(self):
        overlay = SilentOverlayWindow("Foco", 5, 25, theme="light")
        self.assertIn(LIGHT_PALETTE.bg_top, overlay._panel.styleSheet())
        overlay.close()

    def test_completion_has_primary_and_secondary_actions(self):
        overlay = OverlayWindow("Plano Concluido", 0, 0, theme="dark", completion_mode=True)
        names = {button.objectName() for button in overlay.findChildren(QPushButton)}
        self.assertEqual({"primaryBtn", "secondaryBtn"}, names)
        self.assertIn(gradient_for(STATE_COMPLETED)[0], overlay._panel.styleSheet())
        overlay.close()


class TrayThemeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_menu_follows_theme_changes(self):
        tray = SystemTray(QIcon(), FakeTimerWindow(), theme="dark")
        self.assertIn(DARK_PALETTE.bg_top, tray.contextMenu().styleSheet())
        tray.apply_theme("light")
        self.assertIn(LIGHT_PALETTE.bg_top, tray.contextMenu().styleSheet())

    def test_pause_action_text_toggles(self):
        tray = SystemTray(QIcon(), FakeTimerWindow())
        tray.update_pause_action(True, "#22D3A6")
        self.assertEqual("Retomar", tray._action_pause_resume.text())
        tray.update_pause_action(False)
        self.assertEqual("Pausar", tray._action_pause_resume.text())


if __name__ == "__main__":
    unittest.main()
