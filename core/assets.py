"""
assets.py — Resolvedor de Caminhos de Assets

Objetivo Macro:
    Garantir que qualquer arquivo em /assets/ seja encontrado tanto
    em modo de desenvolvimento quanto no executavel gerado pelo PyInstaller.

Fluxo Logico:
    1. Origem: Qualquer modulo que precise carregar um arquivo de asset.
    2. Transformacao: Detecta se esta rodando via PyInstaller (sys._MEIPASS)
       ou em desenvolvimento (__file__) e retorna o caminho absoluto correto.
    3. Destino: Retorna um objeto Path absoluto pronto para uso em QIcon, QPixmap ou QSound.
"""

import sys
from pathlib import Path


def asset_path(relative: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent
    return base / "assets" / relative
