"""
overlay_window.py ? Janela de Notificacao Fullscreen

Objetivo Macro:
    Exibir notificacoes imersivas ao fim de cada bloco do plano e,
    no fim do ciclo, apresentar a tela de conclusao com acoes do usuario.

Fluxo Logico:
    1. Origem: Sinais da timer_window e do SessionPlan.
    2. Transformacao: Renderiza overlay contextual (transicao ou conclusao).
    3. Destino: Emite sinais para continuar o fluxo ou iniciar novo plano.
"""

import os
import subprocess
import sys
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.constants import STATE_COMPLETED, STATE_FOCUS, STATE_LONG_BREAK, STATE_SHORT_BREAK
from core.icon_factory import IconFactory
from ui.components.fonts import monospace_font, spaced_font
from ui.theme import (
    build_overlay_stylesheet,
    gradient_for,
    palette_for,
    rgba_components,
)


class OverlayWindow(QWidget):
    continue_clicked = pyqtSignal()
    new_plan_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    @classmethod
    def show_completion(
        cls,
        theme: str,
        focus_summary_text: str,
        audio_path: str = "",
    ):
        overlay = cls(
            message="Plano Concluido",
            session_duration_min=0,
            next_break_min=0,
            theme=theme,
            audio_path=audio_path,
            completion_mode=True,
            focus_summary_text=focus_summary_text,
        )
        overlay.show()
        return overlay

    def __init__(
        self,
        message: str,
        session_duration_min: int,
        next_break_min: int,
        theme: str = "dark",
        audio_path: str = "",
        completion_mode: bool = False,
        focus_summary_text: str = "",
    ):
        super().__init__()
        self._message = message
        self._session_duration_min = session_duration_min
        self._next_break_min = next_break_min
        self._theme = theme
        self._audio_path = audio_path
        self._completion_mode = completion_mode
        self._focus_summary_text = focus_summary_text
        self._countdown = 30

        self._setup_window()
        self._build_ui()
        if not self._completion_mode:
            self._start_timers()
            self._play_notification_sound()
        else:
            self._update_clock_once()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

    def _infer_state(self) -> str:
        text = self._message.lower()
        if self._completion_mode:
            return STATE_COMPLETED
        if "longa" in text or "longo" in text:
            return STATE_LONG_BREAK
        if "foco" in text:
            return STATE_FOCUS
        return STATE_SHORT_BREAK

    def _state_icon(self, state: str) -> str:
        if state == STATE_FOCUS:
            return "focus"
        if state == STATE_SHORT_BREAK:
            return "break_short"
        if state == STATE_LONG_BREAK:
            return "break_long"
        return "plan_done"

    def _build_ui(self):
        self._palette = palette_for(self._theme)
        state = self._infer_state()
        self._panel = QWidget(self)
        self._panel.setObjectName("panel")
        self._panel.setFixedWidth(560)
        self._panel.setStyleSheet(build_overlay_stylesheet(self._palette, state))

        layout = QVBoxLayout(self._panel)
        layout.setContentsMargins(48, 28, 48, 36)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        accent_bar = QFrame(self._panel)
        accent_bar.setObjectName("accentBar")
        accent_bar.setFixedSize(56, 4)
        layout.addWidget(accent_bar, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(14)

        layout.addLayout(self._build_state_row(state))
        layout.addWidget(self._build_clock_label())
        layout.addWidget(self._build_title_label())
        layout.addSpacing(6)
        layout.addWidget(self._build_info_card())
        layout.addSpacing(14)

        if self._completion_mode:
            layout.addLayout(self._build_completion_actions())
        else:
            self._build_transition_actions(layout)

        self._panel.adjustSize()
        screen = QApplication.primaryScreen().geometry()
        self._panel.move(
            (screen.width() - self._panel.width()) // 2,
            (screen.height() - self._panel.height()) // 2,
        )

    def _build_state_row(self, state: str) -> QHBoxLayout:
        start, _ = gradient_for(state)
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.setSpacing(8)
        icon_label = QLabel(self._panel)
        icon_label.setPixmap(IconFactory.pixmap(self._state_icon(state), color=start, size=16))
        caption = "CICLO FINALIZADO" if self._completion_mode else "PROXIMO BLOCO"
        state_label = QLabel(caption, self._panel)
        state_label.setObjectName("overlayState")
        state_label.setFont(spaced_font(10, 3.0))
        row.addWidget(icon_label)
        row.addWidget(state_label)
        return row

    def _build_clock_label(self) -> QLabel:
        self._clock_label = QLabel("00:00:00", self._panel)
        self._clock_label.setObjectName("overlayClock")
        self._clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clock_font = monospace_font(15)
        clock_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        self._clock_label.setFont(clock_font)
        return self._clock_label

    def _build_title_label(self) -> QLabel:
        title_text = "Plano Concluido" if self._completion_mode else self._message
        title_label = QLabel(title_text, self._panel)
        title_label.setObjectName("overlayTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return title_label

    def _build_info_card(self) -> QFrame:
        if self._completion_mode:
            info_text = self._focus_summary_text or "Historico de foco atualizado"
        else:
            info_text = f"Sessao durou {self._session_duration_min} min  \u00b7  Proximo: {self._next_break_min} min"
        card = QFrame(self._panel)
        card.setObjectName("overlayCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 14, 20, 14)
        info_label = QLabel(info_text, card)
        info_label.setObjectName("overlayInfo")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(info_label)
        return card

    def _action_button(self, text: str, icon_name: str, primary: bool) -> QPushButton:
        button = QPushButton(text, self._panel)
        button.setObjectName("primaryBtn" if primary else "secondaryBtn")
        icon_color = "#FFFFFF" if primary else self._palette.text
        button.setIcon(IconFactory.get(icon_name, color=icon_color, size=16))
        button.setFixedHeight(48)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def _build_completion_actions(self) -> QHBoxLayout:
        actions = QHBoxLayout()
        actions.setSpacing(12)
        new_plan_btn = self._action_button("Novo Plano", "reset", primary=True)
        close_btn = self._action_button("Fechar", "close", primary=False)
        new_plan_btn.clicked.connect(self._on_new_plan)
        close_btn.clicked.connect(self._on_close_only)
        actions.addStretch()
        actions.addWidget(new_plan_btn)
        actions.addWidget(close_btn)
        actions.addStretch()
        return actions

    def _build_transition_actions(self, layout: QVBoxLayout):
        continue_btn = self._action_button("Continuar", "play", primary=True)
        continue_btn.clicked.connect(self._on_continue)
        layout.addWidget(continue_btn, 0, Qt.AlignmentFlag.AlignHCenter)

        self._auto_close_label = QLabel(f"Fechando em {self._countdown}s...", self._panel)
        self._auto_close_label.setObjectName("overlayCountdown")
        self._auto_close_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._auto_close_label)

    def _start_timers(self):
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock_once)
        self._clock_timer.start(1000)
        self._update_clock_once()

        self._auto_close_timer = QTimer(self)
        self._auto_close_timer.timeout.connect(self._tick_auto_close)
        self._auto_close_timer.start(1000)

    def _update_clock_once(self):
        self._clock_label.setText(datetime.now().strftime("%H:%M:%S"))

    def _tick_auto_close(self):
        self._countdown -= 1
        self._auto_close_label.setText(f"Fechando em {self._countdown}s...")
        if self._countdown <= 0:
            self._on_continue()

    def _on_continue(self):
        if hasattr(self, "_clock_timer"):
            self._clock_timer.stop()
        if hasattr(self, "_auto_close_timer"):
            self._auto_close_timer.stop()
        self.continue_clicked.emit()
        self.close()

    def _on_new_plan(self):
        self.new_plan_clicked.emit()
        self.close()

    def _on_close_only(self):
        self.close_clicked.emit()
        self.close()

    def _play_notification_sound(self):
        """Toca o som de notificacao de forma assincrona e multiplataforma.

        Windows usa winsound (nativo); macOS usa afplay; Linux tenta paplay/aplay.
        Se nao houver arquivo de audio ou o player falhar, cai para um beep simples.
        """
        has_audio = bool(self._audio_path) and os.path.exists(self._audio_path)
        try:
            if sys.platform == "win32":
                import winsound

                if has_audio:
                    winsound.PlaySound(
                        self._audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC
                    )
                else:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                return

            if sys.platform == "darwin":
                players = [["afplay", self._audio_path]] if has_audio else []
            else:
                players = (
                    [["paplay", self._audio_path], ["aplay", "-q", self._audio_path]]
                    if has_audio
                    else []
                )

            for cmd in players:
                try:
                    subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return
                except FileNotFoundError:
                    continue

            # Fallback universal: beep do terminal (nao bloqueia).
            sys.stdout.write("\a")
            sys.stdout.flush()
        except Exception:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(*rgba_components(self._palette.scrim)))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Space):
            if self._completion_mode:
                self._on_close_only()
            else:
                self._on_continue()
