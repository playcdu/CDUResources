"""Cozy theme toolkit for the CDUResources Quasar GUI pack.

Importable as ``tools.cozy.<module>`` from the repository root, or as plain
``palette`` / ``lettering`` / ``geometry`` / ``primitives`` / ``icons`` /
``compose`` / ``preview`` / ``validate`` from scripts inside tools/cozy (each
module adds tools/cozy and tools/ to sys.path itself). See README.md and
docs/COZY-STYLE-GUIDE.md.

Licence: MIT (code); glyph and sprite designs CC0-1.0.
"""
import sys as _sys
from pathlib import Path as _Path

_HERE = str(_Path(__file__).resolve().parent)
_TOOLS = str(_Path(__file__).resolve().parents[1])
for _p in (_HERE, _TOOLS):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

__all__ = ['palette', 'lettering', 'geometry', 'primitives', 'icons', 'compose', 'preview', 'validate']
