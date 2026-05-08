"""
timer_window.py ? Janela Principal do PomodoroTimer

Objetivo Macro:
    Exibir o timer com contagem regressiva, controles de sessao e
    configuracao do plano finito, sem acoplar regras de ciclo na UI.

Fluxo Logico:
    1. Origem: AppSettings + SessionPlan injetados pelo main.
    2. Transformacao: QTimer decrementa o bloco atual e dispara sinais.
    3. Destino: Atualiza UI, tray e overlays via signals/slots.
"""

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizeGrip,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.constants import (
    STATE_COMPLETED,
    STATE_FOCUS,
    STATE_LABELS,
    STATE_LONG_BREAK,
    STATE_SHORT_BREAK,
)
from core.icon_factory import IconFactory
from core.session_plan import SessionPlan
from core.settings import AppSettings
from ui.components.circular_progress import CircularProgress
from ui.components.title_bar import DraggableTitleBar


class TimerWindow(QWidget):
    session_finished = pyqtSignal(str, int, int)
    plan_config_changed = pyqtSignal()

    def __init__(self, settings: AppSettings, session_plan: SessionPlan):
        super().__init__()
        self._settings = settings
        self._session_plan = session_plan
        self._state = STATE_FOCUS
        self._is_running = False
        self._is_paused = False
        self._remaining_seconds = 0
        self._total_seconds = 0

        self._setup_window()
        self._build_ui()
        self._apply_theme()
        self._apply_session_plan(self._session_plan)
        self._update_history_label()

    def _setup_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(380)
        self.setMinimumHeight(620)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._container = QWidget()
        self._container.setObjectName("container")
        root.addWidget(self._container)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(24, 16, 24, 24)
        layout.setSpacing(12)

        layout.addWidget(self._build_title_bar())

        state_row = QHBoxLayout()
        state_row.setSpacing(8)
        state_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._state_icon = QLabel()
        self._state_icon.setFixedSize(20, 20)
        self._state_badge = QLabel("Foco")
        self._state_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._state_badge.setObjectName("stateBadge")

        state_row.addWidget(self._state_icon)
        state_row.addWidget(self._state_badge)
        layout.addLayout(state_row)

        self._circular = CircularProgress()
        h_circ = QHBoxLayout()
        h_circ.addStretch()
        h_circ.addWidget(self._circular)
        h_circ.addStretch()
        layout.addLayout(h_circ)

        self._plan_status_label = QLabel("Sessao 1 de 1")
        self._plan_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._plan_status_label.setObjectName("sessionCounter")
        layout.addWidget(self._plan_status_label)

        self._plan_progress = QProgressBar()
        self._plan_progress.setObjectName("planProgress")
        self._plan_progress.setTextVisible(True)
        self._plan_progress.setRange(0, 100)
        self._plan_progress.setValue(0)
        layout.addWidget(self._plan_progress)

        self._history_label = QLabel("Hoje: 0 sessoes | 0 min focados")
        self._history_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._history_label.setObjectName("historyLabel")
        layout.addWidget(self._history_label)

        layout.addLayout(self._build_controls())
        layout.addWidget(self._build_settings_panel())

        theme_btn = QPushButton("Alternar Tema")
        theme_btn.setObjectName("themeBtn")
        theme_btn.setIcon(IconFactory.get("settings", color="#FFFFFF", size=14))
        theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(theme_btn)

        resize_row = QHBoxLayout()
        resize_row.addStretch()
        self._size_grip = QSizeGrip(self)
        resize_row.addWidget(self._size_grip, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(resize_row)

        self._qt_timer = QTimer(self)
        self._qt_timer.timeout.connect(self._tick)

    def _build_title_bar(self) -> QWidget:
        title_bar = DraggableTitleBar(self)
        title_bar.setObjectName("titleBar")

        bar = QHBoxLayout(title_bar)
        bar.setContentsMargins(0, 0, 0, 0)

        title = QLabel("PomodoroTimer")
        title.setObjectName("titleLabel")
        title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        bar.addWidget(title)
        bar.addStretch()

        min_btn = QPushButton("")
        min_btn.setObjectName("winBtn")
        min_btn.setFixedSize(28, 28)
        min_btn.setIcon(IconFactory.get("stop", color="#8A8A8A", size=12))
        min_btn.setToolTip("Minimizar")
        min_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.setIcon(IconFactory.get("close", color="#8A8A8A", size=12))
        close_btn.setToolTip("Ocultar para bandeja")
        close_btn.clicked.connect(self._hide_to_tray)

        bar.addWidget(min_btn)
        bar.addWidget(close_btn)
        return title_bar

    def _build_controls(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        self._reset_btn = QPushButton("")
        self._reset_btn.setObjectName("ctrlBtn")
        self._reset_btn.setToolTip("Reiniciar plano")
        self._reset_btn.setFixedSize(48, 48)
        self._reset_btn.setIcon(IconFactory.get("reset", color="#FFFFFF", size=20))
        self._reset_btn.clicked.connect(self.reset_plan)

        self._start_pause_btn = QPushButton("")
        self._start_pause_btn.setObjectName("mainBtn")
        self._start_pause_btn.setFixedSize(72, 72)
        self._start_pause_btn.setToolTip("Iniciar/Pausar")
        self._start_pause_btn.clicked.connect(self.toggle_pause)

        self._skip_btn = QPushButton("")
        self._skip_btn.setObjectName("ctrlBtn")
        self._skip_btn.setToolTip("Pular bloco")
        self._skip_btn.setFixedSize(48, 48)
        self._skip_btn.setIcon(IconFactory.get("skip", color="#FFFFFF", size=20))
        self._skip_btn.clicked.connect(self.skip_session)

        row.addStretch()
        row.addWidget(self._reset_btn)
        row.addWidget(self._start_pause_btn)
        row.addWidget(self._skip_btn)
        row.addStretch()
        return row

    def _build_settings_panel(self) -> QGroupBox:
        group = QGroupBox("Plano de Sessoes")
        group.setObjectName("settingsGroup")
        group.setCheckable(True)
        group.setChecked(False)

        layout = QVBoxLayout(group)

        def row_spin(label: str, value: int, min_val: int, max_val: int):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setObjectName("settingLabel")
            spin = QSpinBox()
            spin.setRange(min_val, max_val)
            spin.setValue(value)
            spin.setFixedWidth(82)
            spin.setObjectName("spinBox")
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(spin)
            return row, spin

        row_focus_count, self._spin_focus_count = row_spin("Sessoes de foco:", self._settings.focus_count, 1, 12)
        row_focus_min, self._spin_focus_minutes = row_spin("Foco (min):", self._settings.focus_minutes, 5, 120)
        row_break_min, self._spin_break_minutes = row_spin("Pausa curta (min):", self._settings.break_duration, 1, 30)
        row_long_min, self._spin_long_break_minutes = row_spin("Pausa longa (min):", self._settings.long_break_duration, 1, 60)

        self._check_long_break = QCheckBox("Ativar pausa longa ao final")
        self._check_long_break.setChecked(self._settings.long_break_enabled)

        layout.addLayout(row_focus_count)
        layout.addLayout(row_focus_min)
        layout.addLayout(row_break_min)
        layout.addWidget(self._check_long_break)
        layout.addLayout(row_long_min)

        self._calc_label = QLabel()
        self._calc_label.setObjectName("calcLabel")
        self._calc_label.setWordWrap(True)
        layout.addWidget(self._calc_label)

        save_btn = QPushButton("Salvar Plano")
        save_btn.setObjectName("saveBtn")
        save_btn.setIcon(IconFactory.get("check", color="#FFFFFF", size=14))
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)

        self._spin_focus_count.valueChanged.connect(self._on_settings_changed)
        self._spin_focus_minutes.valueChanged.connect(self._on_settings_changed)
        self._spin_break_minutes.valueChanged.connect(self._on_settings_changed)
        self._spin_long_break_minutes.valueChanged.connect(self._on_settings_changed)
        self._check_long_break.toggled.connect(self._on_long_break_toggled)
        self._check_long_break.toggled.connect(self._on_settings_changed)

        self._spin_long_break_minutes.setEnabled(self._check_long_break.isChecked())
        self._update_calc_label()
        return group

    def set_session_plan(self, session_plan: SessionPlan):
        self._session_plan = session_plan
        self._apply_session_plan(session_plan)

    def _apply_session_plan(self, session_plan: SessionPlan):
        state, duration = session_plan.current_block()
        self._state = state
        self._remaining_seconds = duration
        self._total_seconds = duration
        self._is_running = False
        self._is_paused = False
        self._enable_controls(True)
        self._refresh_state_ui()
        self._refresh_display()
        self._update_plan_progress_ui()

    def _update_start_pause_icon(self):
        if self._is_running and not self._is_paused:
            self._start_pause_btn.setIcon(IconFactory.get("pause", color="#FFFFFF", size=26))
        else:
            self._start_pause_btn.setIcon(IconFactory.get("play", color="#FFFFFF", size=26))

    def toggle_pause(self):
        if self._state == STATE_COMPLETED:
            return
        if not self._is_running:
            self._qt_timer.start(1000)
            self._is_running = True
            self._is_paused = False
        elif not self._is_paused:
            self._qt_timer.stop()
            self._is_paused = True
        else:
            self._qt_timer.start(1000)
            self._is_paused = False
        self._update_start_pause_icon()
        self._emit_tray_update()

    def skip_session(self):
        if self._state == STATE_COMPLETED:
            return
        self._qt_timer.stop()
        self._is_running = False
        self._is_paused = False
        self._update_start_pause_icon()
        self._go_to_next_block()

    def _tick(self):
        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            self._refresh_display()
            self._emit_tray_update()
            return
        self._on_session_complete()

    def _on_session_complete(self):
        self._qt_timer.stop()
        self._is_running = False
        self._is_paused = False
        self._update_start_pause_icon()

        finished_duration_min = max(1, self._total_seconds // 60)
        if self._state == STATE_FOCUS:
            self._settings.increment_session(finished_duration_min)
            self._update_history_label()

        next_block = self._session_plan.advance()
        if next_block is None:
            return

        next_state, next_duration = next_block
        self._set_active_block(next_state, next_duration)
        next_duration_min = max(1, next_duration // 60)
        message = self._message_for_state(next_state)
        self.session_finished.emit(message, finished_duration_min, next_duration_min)

    def _go_to_next_block(self):
        next_block = self._session_plan.advance()
        if next_block is None:
            return
        next_state, next_duration = next_block
        self._set_active_block(next_state, next_duration)

    def _set_active_block(self, state: str, duration_seconds: int):
        self._state = state
        self._remaining_seconds = duration_seconds
        self._total_seconds = duration_seconds
        self._refresh_state_ui()
        self._refresh_display()
        self._update_plan_progress_ui()
        self._emit_tray_update()

    def on_plan_finished(self):
        self._qt_timer.stop()
        self._state = STATE_COMPLETED
        self._remaining_seconds = 0
        self._total_seconds = 1
        self._is_running = False
        self._is_paused = False
        self._enable_controls(False)
        self._state_badge.setText("Plano concluido")
        self._plan_status_label.setText("Plano concluido")
        self._plan_progress.setValue(100)
        self._refresh_state_ui()
        self._refresh_display()

    def reset_plan(self):
        self._qt_timer.stop()
        self._session_plan.reset()
        self._apply_session_plan(self._session_plan)

    def _enable_controls(self, enabled: bool):
        self._start_pause_btn.setEnabled(enabled)
        self._skip_btn.setEnabled(enabled)
        self._update_start_pause_icon()

    def _message_for_state(self, state: str) -> str:
        if state == STATE_FOCUS:
            return "Foco"
        if state == STATE_LONG_BREAK:
            return "Pausa longa"
        return "Pausa curta"

    def _state_icon_name(self, state: str) -> str:
        if state == STATE_FOCUS:
            return "focus"
        if state == STATE_SHORT_BREAK:
            return "break_short"
        if state == STATE_LONG_BREAK:
            return "break_long"
        if state == STATE_COMPLETED:
            return "plan_done"
        return "focus"

    def _refresh_state_ui(self):
        label, color = STATE_LABELS[self._state]
        self._state_badge.setText(label)
        self._state_badge.setStyleSheet(
            f"color: {color}; font-size: 14px; font-weight: bold; "
            f"background: {color}22; border-radius: 10px; padding: 4px 12px;"
        )
        self._state_icon.setPixmap(IconFactory.pixmap(self._state_icon_name(self._state), color=color, size=18))

    def _refresh_display(self):
        mm = self._remaining_seconds // 60
        ss = self._remaining_seconds % 60
        time_str = f"{mm:02d}:{ss:02d}"
        progress = self._remaining_seconds / self._total_seconds if self._total_seconds > 0 else 0.0
        _, color = STATE_LABELS[self._state]
        state_label, _ = STATE_LABELS[self._state]
        self._circular.set_progress(progress, time_str, color, state_label)

    def _update_plan_progress_ui(self):
        done, total = self._session_plan.progress()
        blocks = self._session_plan.blocks
        current_index = min(done, len(blocks) - 1) if blocks else 0
        current_state = blocks[current_index][0] if blocks else STATE_FOCUS

        focus_total = sum(1 for s, _ in blocks if s == STATE_FOCUS)
        focus_current = sum(1 for s, _ in blocks[: current_index + 1] if s == STATE_FOCUS)
        break_total = sum(1 for s, _ in blocks if s == STATE_SHORT_BREAK)
        break_current = sum(1 for s, _ in blocks[: current_index + 1] if s == STATE_SHORT_BREAK)

        if current_state == STATE_FOCUS:
            self._plan_status_label.setText(f"Sessao {max(1, focus_current)} de {max(1, focus_total)}")
        elif current_state == STATE_SHORT_BREAK:
            self._plan_status_label.setText(f"Pausa {max(1, break_current)} de {max(1, break_total)}")
        elif current_state == STATE_LONG_BREAK:
            self._plan_status_label.setText("Pausa longa final")
        else:
            self._plan_status_label.setText("Plano concluido")

        percent = int((done / total) * 100) if total else 0
        self._plan_progress.setValue(percent)
        self._plan_progress.setFormat(f"{done}/{total} blocos")

    def _emit_tray_update(self):
        mm = self._remaining_seconds // 60
        ss = self._remaining_seconds % 60
        self._tray_time_str = f"{mm:02d}:{ss:02d}"
        self._tray_state = STATE_LABELS[self._state][0]

    def _update_history_label(self):
        s = self._settings
        self._history_label.setText(f"Hoje: {s.sessions_today} sessoes | {s.focus_minutes_today} min focados")

    def _update_calc_label(self):
        focus_count = self._spin_focus_count.value()
        breaks = max(0, focus_count - 1)
        long_break = "ON" if self._check_long_break.isChecked() else "OFF"
        self._calc_label.setText(f"Pausas curtas: {breaks} | Pausa longa: {long_break}")

    def _on_long_break_toggled(self, checked: bool):
        self._spin_long_break_minutes.setEnabled(checked)

    def _on_settings_changed(self):
        self._settings.focus_count = self._spin_focus_count.value()
        self._settings.focus_minutes = self._spin_focus_minutes.value()
        self._settings.break_duration = self._spin_break_minutes.value()
        self._settings.short_break_minutes = self._spin_break_minutes.value()
        self._settings.long_break_enabled = self._check_long_break.isChecked()
        self._settings.long_break_duration = self._spin_long_break_minutes.value()
        self._update_calc_label()

    def _save_settings(self):
        self._on_settings_changed()
        self._settings.save()
        self.plan_config_changed.emit()

    def _apply_theme(self):
        is_dark = self._settings.theme == "dark"
        if is_dark:
            bg = "#12121e"
            surface = "#1a1a2e"
            text = "#e8e8f0"
            sub = "#8080a0"
            border = "#2a2a45"
            self._circular.set_bg_color("#2a2a3e")
        else:
            bg = "#f0f0f8"
            surface = "#ffffff"
            text = "#1a1a2e"
            sub = "#555570"
            border = "#d0d0e0"
            self._circular.set_bg_color("#e0e0f0")

        self.setStyleSheet(
            f"""
            QWidget#container {{
                background: {surface};
                border-radius: 20px;
                border: 1px solid {border};
            }}
            QLabel#titleLabel {{
                color: {text};
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
            }}
            QLabel#sessionCounter, QLabel#historyLabel, QLabel#settingLabel, QLabel#calcLabel {{
                color: {sub};
                font-family: 'Segoe UI', sans-serif;
            }}
            QLabel#sessionCounter {{ font-size: 13px; }}
            QLabel#historyLabel {{ font-size: 11px; }}
            QLabel#settingLabel {{ color: {text}; font-size: 13px; }}
            QLabel#calcLabel {{ font-size: 11px; }}
            QPushButton#mainBtn {{
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 36px;
                font-size: 24px;
            }}
            QPushButton#mainBtn:hover {{ background: #c0392b; }}
            QPushButton#ctrlBtn {{
                background: {border};
                color: {text};
                border: none;
                border-radius: 24px;
                font-size: 18px;
            }}
            QPushButton#ctrlBtn:hover {{ background: #e74c3c; color: white; }}
            QPushButton#winBtn, QPushButton#closeBtn {{
                background: transparent;
                color: {sub};
                border: none;
                border-radius: 14px;
                font-size: 14px;
            }}
            QPushButton#closeBtn:hover {{ background: #e74c3c; color: white; }}
            QPushButton#winBtn:hover {{ background: {border}; }}
            QPushButton#saveBtn, QPushButton#themeBtn {{
                background: {border};
                color: {text};
                border: none;
                border-radius: 8px;
                font-size: 12px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton#saveBtn:hover, QPushButton#themeBtn:hover {{
                background: #e74c3c; color: white;
            }}
            QGroupBox#settingsGroup {{
                color: {sub};
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
                border: 1px solid {border};
                border-radius: 10px;
                margin-top: 8px;
                padding-top: 8px;
            }}
            QGroupBox#settingsGroup::title {{
                subcontrol-origin: margin;
                left: 10px;
            }}
            QSpinBox#spinBox {{
                background: {bg};
                color: {text};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
            }}
            QProgressBar#planProgress {{
                border: 1px solid {border};
                border-radius: 6px;
                text-align: center;
                color: {text};
                background: {bg};
                height: 18px;
            }}
            QProgressBar#planProgress::chunk {{
                border-radius: 5px;
                background-color: #e74c3c;
            }}
            QCheckBox {{
                color: {text};
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }}
            """
        )
        self._refresh_state_ui()
        self._update_start_pause_icon()

    def _toggle_theme(self):
        self._settings.theme = "light" if self._settings.theme == "dark" else "dark"
        self._settings.save()
        self._apply_theme()

    def _hide_to_tray(self):
        self.hide()

    @property
    def tray_time_str(self) -> str:
        mm = self._remaining_seconds // 60
        ss = self._remaining_seconds % 60
        return f"{mm:02d}:{ss:02d}"

    @property
    def tray_state(self) -> str:
        return STATE_LABELS[self._state][0]

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def is_running(self) -> bool:
        return self._is_running
