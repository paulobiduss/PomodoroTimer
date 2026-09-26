"""
theme.py ? Paletas e Folha de Estilo do Visual "Glass"

Objetivo Macro:
    Concentrar as cores dos temas escuro e claro (vidro fosco + gradiente
    por estado) em um unico lugar, mantendo a TimerWindow livre de CSS.

Fluxo Logico:
    1. Origem: Nome do tema salvo em AppSettings ("dark" | "light").
    2. Transformacao: palette_for() devolve a paleta; build_stylesheet() gera o QSS.
    3. Destino: TimerWindow e componentes aplicam cores e gradientes.
"""

import re
from dataclasses import dataclass

from core.constants import (
    STATE_COMPLETED,
    STATE_FOCUS,
    STATE_LONG_BREAK,
    STATE_SHORT_BREAK,
)

THEME_DARK = "dark"
THEME_LIGHT = "light"

FONT_FAMILY = "'Segoe UI Variable', 'Segoe UI', 'SF Pro Display', 'Inter', sans-serif"

# Cada estado tem um gradiente proprio (inicio, fim): o anel, o botao principal
# e a barra segmentada mudam juntos, sinalizando o bloco sem precisar ler texto.
STATE_GRADIENTS: dict[str, tuple[str, str]] = {
    STATE_FOCUS: ("#FF7A45", "#FF4D8D"),
    STATE_SHORT_BREAK: ("#22D3A6", "#38BDF8"),
    STATE_LONG_BREAK: ("#6366F1", "#A855F7"),
    STATE_COMPLETED: ("#F5B83D", "#F97316"),
}


@dataclass(frozen=True)
class ThemePalette:
    """Cores de um tema. Valores rgba() sao aceitos pelo QSS e pelo QColor via helper."""

    name: str
    bg_top: str
    bg_bottom: str
    glass: str
    glass_hover: str
    glass_border: str
    text: str
    text_muted: str
    track: str
    input_bg: str


DARK_PALETTE = ThemePalette(
    name=THEME_DARK,
    bg_top="#141A2E",
    bg_bottom="#0B1020",
    glass="rgba(255, 255, 255, 0.06)",
    glass_hover="rgba(255, 255, 255, 0.12)",
    glass_border="rgba(255, 255, 255, 0.10)",
    text="#EEF1F8",
    text_muted="#8B93A7",
    track="rgba(255, 255, 255, 0.08)",
    input_bg="rgba(0, 0, 0, 0.25)",
)

LIGHT_PALETTE = ThemePalette(
    name=THEME_LIGHT,
    bg_top="#FFFFFF",
    bg_bottom="#EEF1F8",
    glass="rgba(255, 255, 255, 0.70)",
    glass_hover="rgba(255, 255, 255, 0.95)",
    glass_border="rgba(20, 26, 46, 0.08)",
    text="#141A2E",
    text_muted="#6B7285",
    track="rgba(20, 26, 46, 0.07)",
    input_bg="rgba(20, 26, 46, 0.04)",
)


def palette_for(theme_name: str) -> ThemePalette:
    """Devolve a paleta do tema; nomes desconhecidos caem no escuro (padrao do app).

    Exemplo: palette_for("light").text -> "#141A2E"
    """
    return LIGHT_PALETTE if theme_name == THEME_LIGHT else DARK_PALETTE


def gradient_for(state: str) -> tuple[str, str]:
    """Gradiente (inicio, fim) do estado; estados desconhecidos usam o de foco.

    Exemplo: gradient_for("short_break") -> ("#22D3A6", "#38BDF8")
    """
    return STATE_GRADIENTS.get(state, STATE_GRADIENTS[STATE_FOCUS])


def rgba_components(color: str) -> tuple[int, int, int, int]:
    """Converte "#RRGGBB" ou "rgba(r, g, b, a<=1)" em (r, g, b, alpha 0-255).

    QColor nao entende rgba() do QSS; os componentes pintados com QPainter
    usam esta funcao para reaproveitar a mesma paleta.
    Exemplo: rgba_components("rgba(255, 255, 255, 0.5)") -> (255, 255, 255, 128)
    """
    value = color.strip()
    if value.startswith("#") and len(value) == 7:
        return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16), 255
    match = re.fullmatch(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)", value)
    if not match:
        raise ValueError(f"Cor invalida: {color!r}; esperado '#RRGGBB' ou 'rgba(r, g, b, a)'")
    r, g, b, alpha = match.groups()
    return int(r), int(g), int(b), round(float(alpha) * 255)


def _qss_gradient(start: str, end: str) -> str:
    return f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {start}, stop:1 {end})"


def build_stylesheet(palette: ThemePalette) -> str:
    """Gera o QSS base (independente do estado) da janela principal.

    Exemplo: window.setStyleSheet(build_stylesheet(palette_for("dark")))
    """
    p = palette
    return f"""
        QWidget#container {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {p.bg_top}, stop:1 {p.bg_bottom});
            border-radius: 24px;
            border: 1px solid {p.glass_border};
        }}
        QWidget {{ font-family: {FONT_FAMILY}; }}
        QLabel#titleLabel {{ color: {p.text}; font-size: 13px; font-weight: 600; }}
        QLabel#blocksLabel {{ color: {p.text_muted}; font-size: 11px; }}
        QLabel#historyLabel {{ color: {p.text_muted}; font-size: 11px; }}
        QLabel#settingLabel {{ color: {p.text}; font-size: 12px; }}
        QLabel#calcLabel {{ color: {p.text_muted}; font-size: 11px; }}
        QLabel#cardTitle {{ color: {p.text_muted}; }}
        QFrame#glassCard {{
            background: {p.glass};
            border: 1px solid {p.glass_border};
            border-radius: 18px;
        }}
        QPushButton#ctrlBtn {{
            background: {p.glass};
            border: 1px solid {p.glass_border};
            border-radius: 24px;
        }}
        QPushButton#ctrlBtn:hover {{ background: {p.glass_hover}; }}
        QPushButton#ctrlBtn:disabled {{ background: transparent; }}
        QPushButton#winBtn, QPushButton#closeBtn {{
            background: transparent; border: none; border-radius: 14px;
        }}
        QPushButton#winBtn:hover {{ background: {p.glass_hover}; }}
        QPushButton#winBtn:checked {{ background: {p.glass}; }}
        QPushButton#closeBtn:hover {{ background: rgba(255, 77, 109, 0.85); }}
        QSpinBox#spinBox {{
            background: {p.input_bg};
            color: {p.text};
            border: 1px solid {p.glass_border};
            border-radius: 10px;
            padding: 5px 8px;
            font-size: 12px;
        }}
        QSpinBox#spinBox:disabled {{ color: {p.text_muted}; }}
        QCheckBox {{ color: {p.text}; font-size: 12px; spacing: 8px; }}
        QCheckBox::indicator {{
            width: 16px; height: 16px; border-radius: 5px;
            border: 1px solid {p.glass_border}; background: {p.input_bg};
        }}
        QToolTip {{
            color: {p.text}; background: {p.bg_top};
            border: 1px solid {p.glass_border}; border-radius: 6px; padding: 4px;
        }}
    """


def build_accent_stylesheets(palette: ThemePalette, state: str) -> dict[str, str]:
    """QSS dos widgets que mudam de cor conforme o estado, indexado por objectName.

    Aplicado widget a widget: trocar o QSS da janela inteira a cada bloco nao
    repinta os filhos de forma confiavel no Qt 6 (cor antiga fica em cache).
    Exemplo: build_accent_stylesheets(palette_for("dark"), "focus")["mainBtn"]
    """
    start, end = gradient_for(state)
    accent, accent_hover = _qss_gradient(start, end), _qss_gradient(end, start)
    return {
        "stateLabel": f"QLabel {{ color: {start}; }}",
        "mainBtn": f"""
            QPushButton {{ background: {accent}; border: none; border-radius: 36px; }}
            QPushButton:hover {{ background: {accent_hover}; }}
            QPushButton:disabled {{ background: {palette.track}; }}
        """,
        "saveBtn": f"""
            QPushButton {{
                background: {accent}; color: #FFFFFF; border: none; border-radius: 12px;
                font-size: 12px; font-weight: 600; padding: 9px;
            }}
            QPushButton:hover {{ background: {accent_hover}; }}
        """,
        "longBreakCheck": f"""
            QCheckBox::indicator:checked {{ background: {accent}; border: none; }}
        """,
        "spinBox": f"QSpinBox:focus {{ border: 1px solid {start}; }}",
    }
