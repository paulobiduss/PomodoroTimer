"""
icon_factory.py — Fabrica de Icones SVG Programaticos

Objetivo Macro:
    Gerar QIcon e QPixmap a partir de SVG inline (strings),
    eliminando dependencia de arquivos externos para icones de UI
    e garantindo escalabilidade e consistencia visual.

Fluxo Logico:
    1. Origem: Qualquer widget que precise de um icone de controle (botao, label).
    2. Transformacao: Recebe um nome de icone e uma cor hex, renderiza o SVG
       via QSvgRenderer em um QPixmap transparente no tamanho solicitado.
    3. Destino: Retorna um QIcon pronto para uso em QPushButton.setIcon() ou QAction.setIcon().
"""

from PyQt6.QtCore import QByteArray, QRectF
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer


class IconFactory:
    _SVG_ICONS = {
        "play": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>',
        "pause": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>',
        "stop": '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12"/></svg>',
        "skip": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 6v12l9-6zM16 6h3v12h-3z"/></svg>',
        "reset": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20 11a8 8 0 1 1-2.3-5.7"/><path d="M20 4v6h-6"/></svg>',
        "settings": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1 1 0 0 0 .2 1.1l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1 1 0 0 0-1.1-.2 1 1 0 0 0-.6.9V20a2 2 0 1 1-4 0v-.1a1 1 0 0 0-.7-.9 1 1 0 0 0-1.1.2l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1 1 0 0 0 .2-1.1 1 1 0 0 0-.9-.6H4a2 2 0 1 1 0-4h.1a1 1 0 0 0 .9-.7 1 1 0 0 0-.2-1.1l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1 1 0 0 0 1.1.2 1 1 0 0 0 .6-.9V4a2 2 0 1 1 4 0v.1a1 1 0 0 0 .7.9 1 1 0 0 0 1.1-.2l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1 1 0 0 0-.2 1.1 1 1 0 0 0 .9.6H20a2 2 0 1 1 0 4h-.1a1 1 0 0 0-.9.7z"/></svg>',
        "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg>',
        "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
        "focus": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>',
        "break_short": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10h11v4a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z"/><path d="M15 11h3a2 2 0 0 1 0 4h-3"/><path d="M7 6h1M10 5h1"/></svg>',
        "break_long": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14.5 2.5A8.5 8.5 0 1 0 21 16a7 7 0 1 1-6.5-13.5z"/></svg>',
        "plan_done": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 4h10v3a4 4 0 0 1-4 4h-2a4 4 0 0 1-4-4z"/><path d="M9 11v3a3 3 0 0 0 6 0v-3"/><path d="M8 20h8"/><path d="M6 5H4a2 2 0 0 0 2 2M18 5h2a2 2 0 0 1-2 2"/></svg>',
        "tray_active": '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg>',
        "tray_paused": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="7"/><path d="M10 9v6M14 9v6"/></svg>',
    }

    @staticmethod
    def pixmap(name: str, color: str = "#FFFFFF", size: int = 24) -> QPixmap:
        svg = IconFactory._SVG_ICONS.get(name)
        if not svg:
            return QPixmap()

        svg = svg.replace("currentColor", color)
        renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))

        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, size, size))
        painter.end()
        return pixmap

    @staticmethod
    def get(name: str, color: str = "#FFFFFF", size: int = 24) -> QIcon:
        return QIcon(IconFactory.pixmap(name=name, color=color, size=size))
