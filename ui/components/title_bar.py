"""
title_bar.py — Barra de Título Customizada Arrastável

Objetivo Macro:
    Permitir que a janela principal (que é frameless) seja movida pela tela
    sem interferir com os cliques dos botões contidos nela.

Fluxo Lógico:
    1. Origem: Eventos de mouse press e move.
    2. Transformação: Calcula o delta de movimento e aplica na janela pai.
    3. Destino: parent_window atualiza sua posição (move).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

class DraggableTitleBar(QWidget):
    """Barra de titulo que move a janela sem capturar cliques dos controles."""

    def __init__(self, parent_window: QWidget):
        super().__init__(parent_window)
        self._parent_window = parent_window
        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self._parent_window.frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self._drag_pos is not None:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)
