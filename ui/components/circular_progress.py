"""
circular_progress.py — Widget de Progresso Circular

Objetivo Macro:
    Desenhar um anel de progresso circular com gradiente e brilho suave
    (visual "glass") usando QPainter.

Fluxo Lógico:
    1. Origem: Valor de progresso (0.0 a 1.0), gradiente do estado e cores do tema.
    2. Transformação: Desenha trilha, halo e arco com gradiente cônico.
    3. Destino: Renderiza na tela via paintEvent.
"""

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QConicalGradient, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from ui.components.fonts import monospace_font
from ui.theme import rgba_components

RING_WIDTH = 12
GRADIENT_ORIGIN_OFFSET = 10  # graus; afasta a emenda do gradiente conico da ponta inicial do arco
GLOW_LAYERS = ((26, 18), (20, 30))  # (largura extra do traço, alpha) para simular brilho


def _qcolor(color: str) -> QColor:
    return QColor(*rgba_components(color))


class CircularProgress(QWidget):
    """
    Desenha um anel de progresso circular usando QPainter.
    O ângulo decresce de 360° → 0° conforme o tempo passa.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(250, 250)
        self._progress = 1.0      # 0.0 a 1.0
        self._gradient = ("#FF7A45", "#FF4D8D")
        self._track_color = "rgba(255, 255, 255, 0.08)"
        self._text_color = "#EEF1F8"
        self._muted_color = "#8B93A7"
        self._text = "25:00"
        self._sub_text = ""

    def set_progress(self, value: float, text: str, gradient: tuple[str, str], sub_text: str = ""):
        self._progress = max(0.0, min(1.0, value))
        self._text = text
        self._gradient = gradient
        self._sub_text = sub_text
        self.update()

    def set_theme_colors(self, track: str, text: str, muted: str):
        self._track_color = track
        self._text_color = text
        self._muted_color = muted
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ring = self._ring_rect()
        self._draw_track(painter, ring)
        if self._progress > 0:
            self._draw_glow(painter, ring)
            self._draw_arc(painter, ring, RING_WIDTH, self._arc_gradient(ring))
        self._draw_texts(painter)

    def _ring_rect(self) -> QRectF:
        margin = RING_WIDTH + 18  # espaço para o halo não ser cortado
        side = min(self.width(), self.height()) - margin * 2
        return QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)

    def _draw_track(self, painter: QPainter, ring: QRectF):
        pen = QPen(_qcolor(self._track_color), RING_WIDTH)
        painter.setPen(pen)
        painter.drawEllipse(ring)

    def _draw_glow(self, painter: QPainter, ring: QRectF):
        for extra_width, alpha in GLOW_LAYERS:
            color = QColor(self._gradient[1])
            color.setAlpha(alpha)
            self._draw_arc(painter, ring, RING_WIDTH + extra_width, color)

    def _draw_arc(self, painter: QPainter, ring: QRectF, width: int, brush):
        pen = QPen(brush, width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        angle = int(self._progress * 360 * 16)  # QPainter usa 1/16 de grau
        # Começa no topo (90°) e vai no sentido horário
        painter.drawArc(ring, 90 * 16, -angle)

    def _arc_gradient(self, ring: QRectF) -> QConicalGradient:
        # QConicalGradient avança no sentido anti-horário a partir do ângulo de origem;
        # o arco anda no horário a partir do topo. Com a origem 10° antes do topo,
        # o topo fica na posição `top` e o arco ocupa [top - progresso, top].
        gradient = QConicalGradient(ring.center(), 90 + GRADIENT_ORIGIN_OFFSET)
        top = 1.0 - GRADIENT_ORIGIN_OFFSET / 360
        start, end = QColor(self._gradient[0]), QColor(self._gradient[1])
        gradient.setColorAt(0.0, end)
        gradient.setColorAt(max(0.0, top - self._progress), end)
        gradient.setColorAt(top, start)
        gradient.setColorAt(1.0, start)
        return gradient

    def _draw_texts(self, painter: QPainter):
        painter.setFont(monospace_font(40))
        painter.setPen(_qcolor(self._text_color))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)

        if not self._sub_text:
            return
        sub_font = QFont("Segoe UI", 9)
        sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        painter.setFont(sub_font)
        painter.setPen(_qcolor(self._muted_color))
        painter.drawText(self.rect().adjusted(0, 78, 0, 0), Qt.AlignmentFlag.AlignCenter, self._sub_text)
