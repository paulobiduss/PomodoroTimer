"""
tray.py ? Icone na Bandeja do Sistema (System Tray)

Objetivo Macro:
    Manter o app acessivel mesmo quando minimizado, exibindo o tempo
    restante no tooltip e oferecendo acoes rapidas no menu de contexto.

Fluxo Logico:
    1. Origem: Referencia ao timer_window para leitura do estado.
    2. Transformacao: Formata tooltip e atualiza icones/acoes conforme estado.
    3. Destino: Atualizacoes visuais no icone da bandeja em tempo real.
"""

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from core.icon_factory import IconFactory


class SystemTray(QSystemTrayIcon):
    def __init__(self, icon: QIcon, timer_window, parent=None):
        super().__init__(icon, parent)
        self._timer_window = timer_window
        self._build_menu()
        self._connect_signals()

    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #1a1a2e;
                color: #e8e8f0;
                border: 1px solid #333355;
                border-radius: 8px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #e74c3c;
            }
            QMenu::separator {
                height: 1px;
                background: #333355;
                margin: 4px 0;
            }
            """
        )

        self._action_show = QAction("Mostrar PomodoroTimer", menu)
        self._action_show.setIcon(IconFactory.get("focus", color="#FFFFFF", size=16))
        self._action_show.triggered.connect(self._show_main_window)

        self._action_pause_resume = QAction("Pausar", menu)
        self._action_pause_resume.setIcon(IconFactory.get("pause", color="#FFFFFF", size=16))
        self._action_pause_resume.triggered.connect(self._toggle_pause_resume)

        self._action_skip = QAction("Pular Sessao", menu)
        self._action_skip.setIcon(IconFactory.get("skip", color="#FFFFFF", size=16))
        self._action_skip.triggered.connect(self._skip_session)

        self._action_quit = QAction("Sair", menu)
        self._action_quit.setIcon(IconFactory.get("close", color="#FFFFFF", size=16))
        self._action_quit.triggered.connect(QApplication.quit)

        menu.addAction(self._action_show)
        menu.addSeparator()
        menu.addAction(self._action_pause_resume)
        menu.addAction(self._action_skip)
        menu.addSeparator()
        menu.addAction(self._action_quit)

        self.setContextMenu(menu)

    def _connect_signals(self):
        self.activated.connect(self._on_tray_activated)

    def update_tooltip(self, state_name: str, time_remaining: str):
        self.setToolTip(f"PomodoroTimer\n{state_name}: {time_remaining} restante")

    def update_pause_action(self, is_paused: bool):
        if is_paused:
            self._action_pause_resume.setText("Retomar")
            self._action_pause_resume.setIcon(IconFactory.get("play", color="#FFFFFF", size=16))
            self.setIcon(IconFactory.get("tray_paused", color="#8A8A8A", size=22))
        else:
            self._action_pause_resume.setText("Pausar")
            self._action_pause_resume.setIcon(IconFactory.get("pause", color="#FFFFFF", size=16))
            self.setIcon(IconFactory.get("tray_active", color="#e74c3c", size=22))

    def update_skip_enabled(self, running: bool):
        self._action_skip.setEnabled(running)

    def _show_main_window(self):
        self._timer_window.show()
        self._timer_window.raise_()
        self._timer_window.activateWindow()

    def _toggle_pause_resume(self):
        self._timer_window.toggle_pause()

    def _skip_session(self):
        self._timer_window.skip_session()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_main_window()
