"""
segmented_progress.py — Barra de Progresso Segmentada do Plano

Objetivo Macro:
    Mostrar o plano como uma fileira de segmentos (um por bloco), deixando
    visível quantos blocos já foram feitos e qual está em andamento.

Fluxo Lógico:
    1. Origem: Total de blocos, blocos concluídos e gradiente do estado atual.
    2. Transformação: segment_states() classifica cada segmento.
    3. Destino: paintEvent desenha segmentos arredondados.
"""

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import QWidget

from ui.theme import rgba_components

SEGMENT_DONE = "done"
SEGMENT_CURRENT = "current"
SEGMENT_PENDING = "pending"

SEGMENT_HEIGHT = 6
SEGMENT_GAP = 6
CURRENT_ALPHA = 110  # bloco atual aparece "aceso pela metade"


def segment_states(total: int, done: int) -> list[str]:
    """Classifica cada segmento do plano; `done >= total` marca todos como feitos.

    Exemplo: segment_states(4, 1) -> ["done", "current", "pending", "pending"]
    """
    if total < 0 or done < 0:
        raise ValueError(f"total/done devem ser >= 0; recebido total={total}, done={done}")
    states = []
    for index in range(total):
        if index < done:
            states.append(SEGMENT_DONE)
        elif index == done:
            states.append(SEGMENT_CURRENT)
        else:
            states.append(SEGMENT_PENDING)
    return states


class SegmentedProgress(QWidget):
    """Fileira de segmentos arredondados representando os blocos do plano."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(SEGMENT_HEIGHT + 2)
        self._total = 1
        self._done = 0
        self._gradient = ("#FF7A45", "#FF4D8D")
        self._track_color = "rgba(255, 255, 255, 0.08)"

    def set_progress(self, done: int, total: int, gradient: tuple[str, str]):
        self._total = max(1, total)
        self._done = max(0, min(done, self._total))
        self._gradient = gradient
        self.update()

    def set_track_color(self, color: str):
        self._track_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        states = segment_states(self._total, self._done)
        width = (self.width() - SEGMENT_GAP * (self._total - 1)) / self._total
        for index, state in enumerate(states):
            rect = QRectF(index * (width + SEGMENT_GAP), 1, width, SEGMENT_HEIGHT)
            painter.setBrush(self._brush_for(state, rect))
            painter.drawRoundedRect(rect, SEGMENT_HEIGHT / 2, SEGMENT_HEIGHT / 2)

    def _brush_for(self, state: str, rect: QRectF):
        if state == SEGMENT_PENDING:
            return QColor(*rgba_components(self._track_color))
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        start, end = QColor(self._gradient[0]), QColor(self._gradient[1])
        if state == SEGMENT_CURRENT:
            start.setAlpha(CURRENT_ALPHA)
            end.setAlpha(CURRENT_ALPHA)
        gradient.setColorAt(0.0, start)
        gradient.setColorAt(1.0, end)
        return gradient
