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

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from core.constants import STATE_FOCUS
from core.icon_factory import IconFactory
from ui.theme import THEME_DARK, build_menu_stylesheet, gradient_for, palette_for


class SystemTray(QSystemTrayIcon):
    def __init__(self, icon: QIcon, timer_window, parent=None, theme: str = THEME_DARK):
        super().__init__(icon, parent)
        self._timer_window = timer_window
        self._palette = palette_for(theme)
        self._is_paused = False
        self._accent = gradient_for(STATE_FOCUS)[0]
        self._build_menu()
        self._connect_signals()
        self.apply_theme(theme)

    def _build_menu(self):
        self._menu = QMenu()
        # Sem moldura/fundo nativos o QSS consegue arredondar os cantos do menu.
        self._menu.setWindowFlags(
            self._menu.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self._menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._action_show = QAction("Mostrar PomodoroTimer", self._menu)
        self._action_show.triggered.connect(self._show_main_window)

        self._action_pause_resume = QAction("Pausar", self._menu)
        self._action_pause_resume.triggered.connect(self._toggle_pause_resume)

        self._action_skip = QAction("Pular Sessao", self._menu)
        self._action_skip.triggered.connect(self._skip_session)

        self._action_quit = QAction("Sair", self._menu)
        self._action_quit.triggered.connect(QApplication.quit)

        self._menu.addAction(self._action_show)
        self._menu.addSeparator()
        self._menu.addAction(self._action_pause_resume)
        self._menu.addAction(self._action_skip)
        self._menu.addSeparator()
        self._menu.addAction(self._action_quit)

        self.setContextMenu(self._menu)

    def apply_theme(self, theme: str):
        """Recolore menu e icones; chamado na criacao e a cada troca de tema da janela."""
        self._palette = palette_for(theme)
        self._menu.setStyleSheet(build_menu_stylesheet(self._palette))
        self._refresh_icons()

    def _refresh_icons(self):
        color = self._palette.text
        self._action_show.setIcon(IconFactory.get("focus", color=color, size=16))
        self._action_skip.setIcon(IconFactory.get("skip", color=color, size=16))
        self._action_quit.setIcon(IconFactory.get("close", color=color, size=16))
        pause_icon = "play" if self._is_paused else "pause"
        self._action_pause_resume.setIcon(IconFactory.get(pause_icon, color=color, size=16))
        if self._is_paused:
            self.setIcon(IconFactory.get("tray_paused", color=self._palette.text_muted, size=22))
        else:
            self.setIcon(IconFactory.get("tray_active", color=self._accent, size=22))

    def _connect_signals(self):
        self.activated.connect(self._on_tray_activated)

    def update_tooltip(self, state_name: str, time_remaining: str):
        self.setToolTip(f"PomodoroTimer\n{state_name}: {time_remaining} restante")

    def update_pause_action(self, is_paused: bool, accent: str | None = None):
        """Atualiza texto/icone de pausa; `accent` e a cor do estado atual (gradiente inicial)."""
        self._is_paused = is_paused
        if accent is not None:
            self._accent = accent
        self._action_pause_resume.setText("Retomar" if is_paused else "Pausar")
        self._refresh_icons()

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
