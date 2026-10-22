"""Soulrend theme toolkit for the CDUResources Quasar GUI pack.

A dark-fantasy, souls-like theme: blackened iron, umber leather, mossy slate,
bone-white vellum, blood-red wax, ember glow and a sparing cold soul-cyan.
See README.md and docs/SOULREND-STYLE-GUIDE.md.

Import styles that both work:

* painter scripts inside tools/soulrend (the script's directory is sys.path[0]):
  ``import compose as C, geometry as geo, primitives as P, icons, lettering as L``
* anything else, with tools/ on sys.path: ``from soulrend import compose``

Inside the package every module imports its siblings as ``soulrend.<name>``,
so Soulrend modules never collide with the cozy modules of the same name
(palette, lettering, compose ...) when both themes are loaded in one process
(validate.py / preview.py / build_fixtures.py ``--theme soulrend``).
Geometry, masks, pins and validation are reused from tools/cozy/geometry.py,
which is theme-agnostic; it is never copied.

Licence: MIT (code); glyph and sprite designs CC0-1.0.
"""
import sys as _sys
from pathlib import Path as _Path

_TOOLS = _Path(__file__).resolve().parents[1]
for _p in (str(_TOOLS / 'cozy'), str(_TOOLS)):
    if _p not in _sys.path:
        _sys.path.append(_p)   # appended: never shadows a module that is already importable

THEME = 'soulrend'
__all__ = ['palette', 'lettering', 'primitives', 'icons', 'compose']
