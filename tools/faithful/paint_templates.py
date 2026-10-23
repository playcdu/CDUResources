#!/usr/bin/env python3
"""Faithful theme painter for the generic chest templates: template_chest_1 ... template_chest_6.

    python tools/faithful/paint_templates.py [--skin KEY] [--out-root DIR]

Paints, deterministically, every texture the six skins own: the background
and the outer frame (the templates have no painted buttons). Without
``--out-root`` the PNGs go to pack-source/assets/quasar_gui/textures/; with
it they go to DIR laid out the same way (menu/, frames/<skin>/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, section 5, template_chest_1..6):
template_chest_N is a plain chest_N, the plainest vanilla look in the pack.
The templates belong to the utility family, so they carry no family colour
and no pictogram:

* background: the light grey bevelled panel, one merged inset tray round all
  N x 9 content clearances, the main 3x9 and hotbar 1x9 player trays, the
  title and "Inventory" rows left as plain light panel for the live text.
  No accent line: the utility entry has ``line: False``. A neutral grey_5
  hairline on row 14 was tried (``--hairline`` still paints it for
  comparison) and dropped: in every chest layout row 15 is the content
  tray's grey_0 shadow run, so a grey row 14 directly above it reads as a
  2 px soft gradient on the tray edge, 1 px short of the tray at each end,
  i.e. a mistake rather than an accent. The tray's own shadow already
  separates title from contents, exactly as in vanilla.
* frame: the docked side-panel extension at each of the six heights, with
  the side panels left empty (templates get no pictogram tile).

No words, no item icons, no counts, no tiles. Restraint is the design.

Licence: MIT (tooling). The pixels it paints are CC0-1.0.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))                  # faithful modules first
for _p in (str(_HERE.parent), str(_HERE.parent / 'cozy')):
    if _p not in sys.path:
        sys.path.append(_p)                         # tools/ and the shared geometry

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
from palette import GREY, accent_for  # noqa: E402

SKINS = tuple(f'template_chest_{n}' for n in range(1, 7))
SEED = {k: 90 + n for n, k in enumerate(SKINS, start=1)}
HAIRLINE = GREY[5]           # the rejected neutral grey accent (see module docstring)


def _check_contract(key):
    s = geo.skin(key)
    if s.buttons:
        raise SystemExit(f'{key}: unexpected painted buttons {[b.id for b in s.buttons]}; contract changed')
    if s.static_slots:
        raise SystemExit(f'{key}: unexpected static cells {s.static_slots}; contract changed')
    if accent_for(key).get('pictogram'):
        raise SystemExit(f'{key}: templates must carry no pictogram')
    return s


def paint_background(key, hairline=False):
    """Panel, full inset tray over every content well, player trays. Nothing
    else (``hairline`` adds the rejected grey row-14 line, comparison only)."""
    bg = C.base_background(key, seed=SEED[key], accent=False, pictograms=False)
    if hairline:
        C.draw_accent_line(bg, key, colour=HAIRLINE)
    C.finish_background(bg, key)                    # clear masks + stamp pin, always last
    return bg


def paint_frames(key):
    """The base side-panel frame; the side panels stay empty (no tile)."""
    s = geo.skin(key)
    out = {}
    for a in s.art_layers:
        fr = C.base_frame(key, a.id, seed=SEED[key])
        C.finish_frame(fr, key, a.id)
        out[a.id] = fr
    return out


def paint(key, out_root=None, hairline=False):
    s = _check_contract(key)
    root = Path(out_root) if out_root else geo.TEXTURES
    written = [C.save_png(paint_background(key, hairline), root / 'menu' / Path(s.asset).name)]
    for lid, fr in paint_frames(key).items():
        written.append(C.save_png(fr, root / 'frames' / key / f'{lid}.png'))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', help='write under DIR (menu/, frames/) instead of pack-source')
    ap.add_argument('--hairline', action='store_true', help='add the rejected grey row-14 hairline (comparison only)')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        paths = paint(key, args.out_root, hairline=args.hairline)
        print(f'{key}: wrote {len(paths)} PNGs: ' + ', '.join(str(p) for p in paths))


if __name__ == '__main__':
    main()
