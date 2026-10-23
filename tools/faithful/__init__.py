"""Faithful theme toolkit for the CDUResources Quasar GUI pack.

A vanilla-faithful theme: the game's own inventory language (light grey
bevelled panels, inset slot wells, grey stone buttons, white lettering with a
dark shadow), redrawn from scratch. No Mojang texture or font pixel is copied,
traced, sampled or embedded. See README.md and docs/FAITHFUL-STYLE-GUIDE.md.

Import styles that both work:

* painter scripts inside tools/faithful (the script's directory is sys.path[0]):
  ``import compose as C, geometry as geo, primitives as P, icons, lettering as L``
* anything else, with tools/ on sys.path: ``from faithful import compose``

Inside the package every module imports its siblings as ``faithful.<name>``,
so Faithful modules never collide with the cozy or Soulrend modules of the
same name (palette, lettering, compose ...) when several themes are loaded in
one process (validate.py / preview.py / build_fixtures.py ``--theme faithful``).
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

THEME = 'faithful'
__all__ = ['palette', 'lettering', 'primitives', 'icons', 'compose']
