"""Gera version_info.txt a partir da versao da tag de release.

1. Intencao: Evitar que o numero de versao embutido no .exe (visto em
   Propriedades > Detalhes no Windows) fique dessincronizado da tag do
   GitHub Release — ja aconteceu de v1.0.3 ser publicado com FileVersion
   1.0.2.0 porque o arquivo era mantido a mao.
2. Transformacao: Recebe a tag (ex.: "v1.0.3") e escreve o recurso de
   versao do PyInstaller com CompanyName/FileDescription/ProductName fixos
   e FileVersion/ProductVersion derivados da tag.
3. Destino: Sobrescreve version_info.txt antes do `pyinstaller --version-file`
   no job build-windows do release.

Uso: python tools/render_version_info.py v1.0.3 version_info.txt
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")

_TEMPLATE = """VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, 0),
    prodvers=({major}, {minor}, {patch}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0),
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u"040904B0",
          [
            StringStruct(u"CompanyName", u"Paulo Bidu"),
            StringStruct(u"FileDescription", u"PomodoroTimer - timer de produtividade Pomodoro"),
            StringStruct(u"FileVersion", u"{version}.0"),
            StringStruct(u"InternalName", u"PomodoroTimer"),
            StringStruct(u"LegalCopyright", u"Copyright (c) 2026 Paulo Bidu"),
            StringStruct(u"OriginalFilename", u"PomodoroTimer.exe"),
            StringStruct(u"ProductName", u"PomodoroTimer"),
            StringStruct(u"ProductVersion", u"{version}.0"),
          ],
        )
      ]
    ),
    VarFileInfo([VarStruct(u"Translation", [1033, 1200])]),
  ],
)
"""


def parse_version(tag: str) -> tuple[int, int, int]:
    """Extrai (major, minor, patch) de uma tag como "v1.0.3" ou "1.0.3".

    >>> parse_version("v1.0.3")
    (1, 0, 3)
    """
    match = _VERSION_RE.match(tag.strip())
    if not match:
        raise ValueError(f"Tag de versao invalida: {tag!r}, esperado formato vX.Y.Z")
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def render_version_info(tag: str) -> str:
    """Renderiza o conteudo do version_info.txt para a tag informada.

    >>> render_version_info("v1.0.3").splitlines()[2]
    '    filevers=(1, 0, 3, 0),'
    """
    major, minor, patch = parse_version(tag)
    return _TEMPLATE.format(major=major, minor=minor, patch=patch, version=f"{major}.{minor}.{patch}")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Uso: python tools/render_version_info.py <tag> <destino>", file=sys.stderr)
        return 1
    _, tag, destination = argv
    Path(destination).write_text(render_version_info(tag), encoding="utf-8")
    print(f"version_info.txt gerado para {tag} em {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
