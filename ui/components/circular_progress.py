"""
circular_progress.py — Widget de Progresso Circular

Objetivo Macro:
    Desenhar um anel de progresso circular animado usando QPainter.

Fluxo Lógico:
    1. Origem: Valor de progresso (0.0 a 1.0) e cores fornecidas pelo parent.
    2. Transformação: Desenha o anel baseado no ângulo.
    3. Destino: Renderiza na tela via paintEvent.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

class CircularProgress(QWidget):
    """
    Desenha um anel de progresso circular usando QPainter.
    O ângulo decresce de 360° → 0° conforme o tempo passa.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(260, 260)
        self._progress = 1.0      # 0.0 a 1.0
        self._color = "#e74c3c"
        self._bg_color = "#2a2a3e"
        self._text = "25:00"
        self._sub_text = ""

    def set_progress(self, value: float, text: str, color: str, sub_text: str = ""):
        self._progress = max(0.0, min(1.0, value))
        self._text = text
        self._color = color
        self._sub_text = sub_text
        self.update()

    def set_bg_color(self, color: str):
        self._bg_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        margin = 16
        rect_size = min(w, h) - margin * 2
        x = (w - rect_size) // 2
        y = (h - rect_size) // 2

        # ── Trilha de fundo (anel cinza) ──
        pen_bg = QPen(QColor(self._bg_color))
        pen_bg.setWidth(14)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawEllipse(x, y, rect_size, rect_size)

        # ── Arco de progresso colorido ──
        angle = int(self._progress * 360 * 16)  # QPainter usa 1/16 de grau
        pen_prog = QPen(QColor(self._color))
        pen_prog.setWidth(14)
        pen_prog.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_prog)
        # Começa no topo (90°) e vai no sentido horário
        painter.drawArc(x, y, rect_size, rect_size, 90 * 16, -angle)

        # ── Texto central (MM:SS) ──
        painter.setPen(QColor("#e8e8f0"))
        font = QFont("Courier New", 36, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)

        # ── Sub-texto (estado) ──
        if self._sub_text:
            painter.setPen(QColor(self._color))
            font_sub = QFont("Segoe UI", 10)
            painter.setFont(font_sub)
            sub_rect = self.rect().adjusted(0, 80, 0, 0)
            painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, self._sub_text)
