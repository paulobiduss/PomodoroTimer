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
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
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
from ui.components.segmented_progress import SegmentedProgress
from ui.components.title_bar import DraggableTitleBar
from ui.theme import (
    THEME_DARK,
    THEME_LIGHT,
    build_accent_stylesheets,
    build_stylesheet,
    gradient_for,
    palette_for,
)


def _spaced_font(point_size: int, letter_spacing: float) -> QFont:
    # QSS nao suporta letter-spacing; rotulos em caixa alta usam fonte configurada no codigo.
    font = QFont("Segoe UI", point_size, QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, letter_spacing)
    return font


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
        self._plan_status_text = ""
        self._palette = palette_for(self._settings.theme)

        self._setup_window()
        self._build_ui()
        self._apply_theme()
        self._apply_session_plan(self._session_plan)
        self._update_history_label()

    def _setup_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(360)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        # Janela acompanha o conteudo: encolhe/cresce ao abrir o painel do plano.
        root.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self._container = QWidget()
        self._container.setObjectName("container")
        self._container.setFixedWidth(360)
        root.addWidget(self._container)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(20, 14, 20, 20)
        layout.setSpacing(14)

        layout.addWidget(self._build_title_bar())
        layout.addWidget(self._build_timer_card())
        layout.addLayout(self._build_controls())

        self._history_label = QLabel("Hoje: 0min | Ontem: igual a ontem | Semana: 0min")
        self._history_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._history_label.setObjectName("historyLabel")
        layout.addWidget(self._history_label)

        self._settings_card = self._build_settings_panel()
        self._settings_card.setVisible(False)
        layout.addWidget(self._settings_card)

        self._qt_timer = QTimer(self)
        self._qt_timer.timeout.connect(self._tick)

    def _build_timer_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("glassCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        state_row = QHBoxLayout()
        state_row.setSpacing(6)
        state_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._state_icon = QLabel()
        self._state_icon.setFixedSize(16, 16)
        self._state_badge = QLabel("FOCO")
        self._state_badge.setObjectName("stateLabel")
        self._state_badge.setFont(_spaced_font(10, 3.0))
        state_row.addWidget(self._state_icon)
        state_row.addWidget(self._state_badge)
        layout.addLayout(state_row)

        self._circular = CircularProgress()
        layout.addWidget(self._circular, 0, Qt.AlignmentFlag.AlignHCenter)

        self._plan_progress = SegmentedProgress()
        layout.addWidget(self._plan_progress)

        self._blocks_label = QLabel("0/1 blocos")
        self._blocks_label.setObjectName("blocksLabel")
        self._blocks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._blocks_label)
        return card

    def _build_title_bar(self) -> QWidget:
        title_bar = DraggableTitleBar(self)
        title_bar.setObjectName("titleBar")

        bar = QHBoxLayout(title_bar)
        bar.setContentsMargins(4, 0, 0, 0)
        bar.setSpacing(2)

        title = QLabel("Pomodoro")
        title.setObjectName("titleLabel")
        title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        bar.addWidget(title)
        bar.addStretch()

        self._theme_btn = self._title_button("winBtn", "Alternar tema", self._toggle_theme)
        self._settings_btn = self._title_button("winBtn", "Plano de sessoes", self._toggle_settings_panel)
        self._settings_btn.setCheckable(True)
        self._min_btn = self._title_button("winBtn", "Minimizar", self.showMinimized)
        self._close_btn = self._title_button("closeBtn", "Ocultar para bandeja", self._hide_to_tray)

        for button in (self._theme_btn, self._settings_btn, self._min_btn, self._close_btn):
            bar.addWidget(button)
        return title_bar

    def _title_button(self, object_name: str, tooltip: str, on_click) -> QPushButton:
        button = QPushButton("")
        button.setObjectName(object_name)
        button.setFixedSize(28, 28)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(on_click)
        return button

    def _build_controls(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(18)

        self._reset_btn = QPushButton("")
        self._reset_btn.setObjectName("ctrlBtn")
        self._reset_btn.setToolTip("Reiniciar plano")
        self._reset_btn.setFixedSize(48, 48)
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
        self._skip_btn.clicked.connect(self.skip_session)

        row.addStretch()
        for button in (self._reset_btn, self._start_pause_btn, self._skip_btn):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            row.addWidget(button)
        row.addStretch()
        return row

    def _build_settings_panel(self) -> QFrame:
        group = QFrame()
        group.setObjectName("glassCard")

        layout = QVBoxLayout(group)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        card_title = QLabel("PLANO DE SESSOES")
        card_title.setObjectName("cardTitle")
        card_title.setFont(_spaced_font(9, 2.0))
        layout.addWidget(card_title)

        def row_spin(label: str, value: int, min_val: int, max_val: int):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setObjectName("settingLabel")
            spin = QSpinBox()
            spin.setRange(min_val, max_val)
            spin.setValue(value)
            spin.setFixedWidth(72)
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        self._check_long_break.setObjectName("longBreakCheck")
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
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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
            self._settings.record_focus_session(finished_duration_min)
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
        self._plan_status_text = "Plano concluido"
        _, total = self._session_plan.progress()
        self._plan_progress.set_progress(total, total, gradient_for(STATE_COMPLETED))
        self._blocks_label.setText(f"{total}/{total} blocos")
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
        label, _ = STATE_LABELS[self._state]
        start, _ = gradient_for(self._state)
        self._state_badge.setText(label.upper())
        self._state_icon.setPixmap(IconFactory.pixmap(self._state_icon_name(self._state), color=start, size=16))
        self._apply_accent_styles()

    def _apply_accent_styles(self):
        accent = build_accent_stylesheets(self._palette, self._state)
        for widget in self.findChildren(QWidget):
            rule = accent.get(widget.objectName())
            if rule is not None:
                widget.setStyleSheet(rule)

    def _refresh_display(self):
        mm = self._remaining_seconds // 60
        ss = self._remaining_seconds % 60
        time_str = f"{mm:02d}:{ss:02d}"
        progress = self._remaining_seconds / self._total_seconds if self._total_seconds > 0 else 0.0
        self._circular.set_progress(progress, time_str, gradient_for(self._state), self._plan_status_text)

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
            self._plan_status_text = f"Sessao {max(1, focus_current)} de {max(1, focus_total)}"
        elif current_state == STATE_SHORT_BREAK:
            self._plan_status_text = f"Pausa {max(1, break_current)} de {max(1, break_total)}"
        elif current_state == STATE_LONG_BREAK:
            self._plan_status_text = "Pausa longa final"
        else:
            self._plan_status_text = "Plano concluido"

        self._plan_progress.set_progress(done, total, gradient_for(self._state))
        self._blocks_label.setText(f"{done}/{total} blocos")
        self._refresh_display()

    def _emit_tray_update(self):
        mm = self._remaining_seconds // 60
        ss = self._remaining_seconds % 60
        self._tray_time_str = f"{mm:02d}:{ss:02d}"
        self._tray_state = STATE_LABELS[self._state][0]

    def _update_history_label(self):
        self._history_label.setText(self._settings.focus_history.compact_summary_text())

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
        self._palette = palette_for(self._settings.theme)
        p = self._palette
        self._circular.set_theme_colors(p.track, p.text, p.text_muted)
        self._plan_progress.set_track_color(p.track)
        self.setStyleSheet(build_stylesheet(p))
        self._refresh_icons()
        self._refresh_state_ui()

    def _refresh_icons(self):
        """Icones sao pixmaps coloridos; precisam ser refeitos a cada troca de tema."""
        p = self._palette
        next_theme_icon = "sun" if p.name == THEME_DARK else "moon"
        self._theme_btn.setIcon(IconFactory.get(next_theme_icon, color=p.text_muted, size=14))
        self._settings_btn.setIcon(IconFactory.get("settings", color=p.text_muted, size=14))
        self._min_btn.setIcon(IconFactory.get("minimize", color=p.text_muted, size=12))
        self._close_btn.setIcon(IconFactory.get("close", color=p.text_muted, size=12))
        self._reset_btn.setIcon(IconFactory.get("reset", color=p.text, size=18))
        self._skip_btn.setIcon(IconFactory.get("skip", color=p.text, size=18))
        self._update_start_pause_icon()

    def _toggle_theme(self):
        self._settings.theme = THEME_LIGHT if self._settings.theme == THEME_DARK else THEME_DARK
        self._settings.save()
        self._apply_theme()

    def _toggle_settings_panel(self):
        self._settings_card.setVisible(self._settings_btn.isChecked())

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
