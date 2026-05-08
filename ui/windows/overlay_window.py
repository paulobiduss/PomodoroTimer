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
import winsound
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.constants import STATE_COMPLETED, STATE_FOCUS, STATE_LONG_BREAK, STATE_SHORT_BREAK
from core.icon_factory import IconFactory


class OverlayWindow(QWidget):
    continue_clicked = pyqtSignal()
    new_plan_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    @classmethod
    def show_completion(
        cls,
        theme: str,
        focused_minutes_total: int,
        audio_path: str = "",
    ):
        overlay = cls(
            message="Plano Concluido",
            session_duration_min=0,
            next_break_min=0,
            theme=theme,
            audio_path=audio_path,
            completion_mode=True,
            focused_minutes_total=focused_minutes_total,
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
        focused_minutes_total: int = 0,
    ):
        super().__init__()
        self._message = message
        self._session_duration_min = session_duration_min
        self._next_break_min = next_break_min
        self._theme = theme
        self._audio_path = audio_path
        self._completion_mode = completion_mode
        self._focused_minutes_total = focused_minutes_total
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

    def _state_color(self, state: str) -> str:
        if state == STATE_FOCUS:
            return "#e74c3c"
        if state == STATE_SHORT_BREAK:
            return "#2ecc71"
        if state == STATE_LONG_BREAK:
            return "#1f8ef1"
        return "#F5A623"

    def _state_icon(self, state: str) -> str:
        if state == STATE_FOCUS:
            return "focus"
        if state == STATE_SHORT_BREAK:
            return "break_short"
        if state == STATE_LONG_BREAK:
            return "break_long"
        return "plan_done"

    def _build_ui(self):
        self._panel = QWidget(self)
        self._panel.setFixedSize(640, 430 if self._completion_mode else 420)
        self._panel.setObjectName("panel")

        screen = QApplication.primaryScreen().geometry()
        self._panel.move((screen.width() - self._panel.width()) // 2, (screen.height() - self._panel.height()) // 2)

        is_dark = self._theme == "dark"
        panel_bg = "rgba(18, 18, 30, 0.97)" if is_dark else "rgba(245, 245, 255, 0.97)"
        text_color = "#e8e8f0" if is_dark else "#1a1a2e"
        sub_color = "#9090a0" if is_dark else "#555570"

        state = self._infer_state()
        accent = self._state_color(state)
        state_icon = self._state_icon(state)

        self._panel.setStyleSheet(
            f"""
            QWidget#panel {{
                background: {panel_bg};
                border-radius: 24px;
                border: 2px solid {accent};
            }}
            """
        )

        layout = QVBoxLayout(self._panel)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._clock_label = QLabel("00:00:00", self._panel)
        self._clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._clock_label.setStyleSheet(
            f"""
            color: {accent};
            font-family: 'Courier New', monospace;
            font-size: 56px;
            font-weight: bold;
            letter-spacing: 4px;
            """
        )
        layout.addWidget(self._clock_label)

        title_row = QHBoxLayout()
        title_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_row.setSpacing(8)

        icon_label = QLabel(self._panel)
        icon_label.setPixmap(IconFactory.pixmap(state_icon, color=accent, size=26))
        title_row.addWidget(icon_label)

        title_text = "Plano Concluido" if self._completion_mode else self._message
        title_label = QLabel(title_text, self._panel)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            f"""
            color: {text_color};
            font-size: 24px;
            font-weight: 700;
            font-family: 'Segoe UI', sans-serif;
            """
        )
        title_row.addWidget(title_label)
        layout.addLayout(title_row)

        if self._completion_mode:
            hours = self._focused_minutes_total // 60
            mins = self._focused_minutes_total % 60
            info_text = f"Voce focou por {hours}h {mins}min hoje"
        else:
            info_text = f"Sessao durou {self._session_duration_min} min | Proximo: {self._next_break_min} min"

        info_label = QLabel(info_text, self._panel)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet(
            f"""
            color: {sub_color};
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;
            """
        )
        layout.addWidget(info_label)

        layout.addSpacing(10)

        if self._completion_mode:
            actions = QHBoxLayout()
            actions.setSpacing(12)

            new_plan_btn = QPushButton("Novo Plano", self._panel)
            new_plan_btn.setIcon(IconFactory.get("reset", color="#FFFFFF", size=16))
            close_btn = QPushButton("Fechar", self._panel)
            close_btn.setIcon(IconFactory.get("close", color="#FFFFFF", size=16))
            for btn in (new_plan_btn, close_btn):
                btn.setFixedHeight(52)
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background: {accent};
                        color: white;
                        border: none;
                        border-radius: 12px;
                        font-size: 16px;
                        font-weight: bold;
                        font-family: 'Segoe UI', sans-serif;
                        padding: 0 26px;
                    }}
                    QPushButton:hover {{
                        background: {QColor(accent).lighter(130).name()};
                    }}
                    """
                )

            new_plan_btn.clicked.connect(self._on_new_plan)
            close_btn.clicked.connect(self._on_close_only)
            actions.addWidget(new_plan_btn)
            actions.addWidget(close_btn)
            layout.addLayout(actions)
            return

        self._auto_close_label = QLabel(f"Fechando em {self._countdown}s...", self._panel)
        self._auto_close_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._auto_close_label.setStyleSheet(
            f"""
            color: {sub_color};
            font-size: 12px;
            font-family: 'Segoe UI', sans-serif;
            """
        )
        layout.addWidget(self._auto_close_label)

        continue_btn = QPushButton("Continuar", self._panel)
        continue_btn.setIcon(IconFactory.get("play", color="#FFFFFF", size=16))
        continue_btn.setFixedHeight(52)
        continue_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {accent};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                padding: 0 30px;
            }}
            QPushButton:hover {{
                background: {QColor(accent).lighter(130).name()};
            }}
            """
        )
        continue_btn.clicked.connect(self._on_continue)
        layout.addWidget(continue_btn)

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
        try:
            if self._audio_path and os.path.exists(self._audio_path):
                winsound.PlaySound(self._audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Space):
            if self._completion_mode:
                self._on_close_only()
            else:
                self._on_continue()
