"""
fonts.py — Fontes Compartilhadas da UI

Objetivo Macro:
    Reunir as fontes configuradas em codigo (rotulos espacados e relogios),
    usadas pela janela principal, pelo anel de progresso e pelo overlay.

Fluxo Logico:
    1. Origem: Tamanho e espacamento pedidos pelo widget.
    2. Transformacao: Monta QFont com familias de fallback por plataforma.
    3. Destino: widget.setFont(...) ou QPainter.setFont(...).
"""

from PyQt6.QtGui import QFont

# Primeira familia instalada vence: JetBrains/Cascadia (Win 11), SF Mono/Menlo (macOS), Consolas (Win).
TIME_FONT_FAMILIES = ["JetBrains Mono", "Cascadia Mono", "SF Mono", "Menlo", "Consolas", "DejaVu Sans Mono"]


def spaced_font(point_size: int, letter_spacing: float, weight: QFont.Weight = QFont.Weight.Bold) -> QFont:
    """Fonte com espacamento entre letras, para rotulos em caixa alta.

    QSS nao suporta letter-spacing, por isso a fonte e configurada no codigo.
    Exemplo: label.setFont(spaced_font(10, 3.0))
    """
    font = QFont("Segoe UI", point_size, weight)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, letter_spacing)
    return font


def monospace_font(point_size: int, weight: QFont.Weight = QFont.Weight.Medium) -> QFont:
    """Fonte monoespacada para relogios, evitando que os digitos "pulem" a cada segundo.

    Exemplo: painter.setFont(monospace_font(40))
    """
    font = QFont()
    font.setFamilies(TIME_FONT_FAMILIES)
    font.setPointSize(point_size)
    font.setWeight(weight)
    font.setStyleHint(QFont.StyleHint.Monospace)
    return font
