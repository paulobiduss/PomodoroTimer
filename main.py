"""
main.py ? Entry Point do PomodoroTimer

Objetivo Macro:
    Inicializar o app PyQt6, orquestrar os modulos e manter
    o ciclo de vida correto da aplicacao.

Fluxo Logico:
    1. Origem: QApplication com suporte a DPI alto.
    2. Transformacao: Injeta settings + session_plan + janelas e conecta sinais.
    3. Destino: App permanece ativo no loop de eventos do Qt.
"""

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = str(Path(__file__).resolve().parent)

sys.path.insert(0, BASE_DIR)

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from core.assets import asset_path
from core.settings import AppSettings
from core.session_plan import SessionPlan
from ui.tray import SystemTray
from ui.windows.overlay_window import OverlayWindow
from ui.windows.timer_window import TimerWindow


def build_session_plan(settings: AppSettings) -> SessionPlan:
    return SessionPlan(
        focus_count=settings.focus_count,
        focus_duration=settings.focus_minutes,
        break_duration=settings.break_duration,
        long_break_enabled=settings.long_break_enabled,
        long_break_duration=settings.long_break_duration,
    )


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("PomodoroTimer")
    app.setOrganizationName("PomodoroTimer")

    icon_file = asset_path("icon.png")
    app_icon = QIcon(str(icon_file)) if icon_file.exists() else QIcon()
    app.setWindowIcon(app_icon)

    settings = AppSettings()
    session_plan_holder = {"plan": build_session_plan(settings)}

    timer_window = TimerWindow(settings, session_plan_holder["plan"])
    timer_window.setWindowIcon(app_icon)

    tray = SystemTray(app_icon, timer_window)
    tray.show()

    def connect_plan_signals(plan: SessionPlan):
        plan.plan_finished.connect(timer_window.on_plan_finished)
        plan.plan_finished.connect(show_plan_completion_overlay)

    def disconnect_plan_signals(plan: SessionPlan):
        try:
            plan.plan_finished.disconnect(timer_window.on_plan_finished)
        except Exception:
            pass
        try:
            plan.plan_finished.disconnect(show_plan_completion_overlay)
        except Exception:
            pass

    def rebuild_plan_from_settings():
        old_plan = session_plan_holder["plan"]
        disconnect_plan_signals(old_plan)

        new_plan = build_session_plan(settings)
        session_plan_holder["plan"] = new_plan
        connect_plan_signals(new_plan)
        timer_window.set_session_plan(new_plan)

    def on_session_finished(message: str, duration_min: int, next_min: int):
        audio_path = str(asset_path("notify.wav"))
        timer_window.current_overlay = OverlayWindow(
            message,
            duration_min,
            next_min,
            settings.theme,
            audio_path,
            completion_mode=False,
        )
        timer_window.current_overlay.continue_clicked.connect(timer_window.toggle_pause)
        timer_window.current_overlay.show()

    def show_plan_completion_overlay():
        audio_path = str(asset_path("notify.wav"))
        focused_total = settings.focus_minutes_today
        timer_window.current_overlay = OverlayWindow.show_completion(
            theme=settings.theme,
            focused_minutes_total=focused_total,
            audio_path=audio_path,
        )
        timer_window.current_overlay.new_plan_clicked.connect(rebuild_plan_from_settings)

    timer_window.session_finished.connect(on_session_finished)
    timer_window.plan_config_changed.connect(rebuild_plan_from_settings)

    connect_plan_signals(session_plan_holder["plan"])

    def update_tray():
        tray.update_tooltip(timer_window.tray_state, timer_window.tray_time_str)
        tray.update_pause_action(timer_window.is_paused)
        tray.update_skip_enabled(timer_window.is_running)

    tray_updater = QTimer()
    tray_updater.timeout.connect(update_tray)
    tray_updater.start(5000)
    update_tray()

    timer_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
