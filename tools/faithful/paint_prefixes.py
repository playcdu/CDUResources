#!/usr/bin/env python3
"""Faithful theme painter for the prefixes family: prefixes_1 ... prefixes_6.

    python tools/faithful/paint_prefixes.py [--skin KEY] [--out-root DIR]

Paints, deterministically, every texture the six skins own: the background
and the outer frame (the prefixes screens have no painted buttons). Without
``--out-root`` the PNGs go to pack-source/assets/quasar_gui/textures/; with
it they go to DIR laid out the same way (menu/, frames/<skin>/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, section 5, prefixes): prefixes_N is a
chest_N screen whose every top cell is a native well (the prefix items the
server lists), so the shared base carries the whole look and nothing is
added:

* background: the light grey bevelled panel, one merged inset tray round all
  N x 9 content clearances, the main 3x9 and hotbar 1x9 player trays, the
  title and "Inventory" rows left as plain light panel for the live text,
  and the 1 px blue_1 prefixes accent line on row 14 under the title. There
  are no static cells, so no pictogram tile on the background.
* frame: the docked side-panel extension at each of the six heights, with
  one recessed 24x24 tile holding the name-tag pictogram on each side panel.

No words, no item icons, no counts. Restraint is the design.

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

SKINS = tuple(f'prefixes_{n}' for n in range(1, 7))
SEED = {k: 60 + n for n, k in enumerate(SKINS, start=1)}


def paint_background(key):
    """Panel, full inset tray over every content well, player trays, the
    blue prefixes accent line. Nothing else."""
    bg = C.base_background(key, seed=SEED[key])
    C.finish_background(bg, key)                    # clear masks + stamp pin, always last
    return bg


def paint_frames(key):
    """The base side-panel frame with the name-tag tile on each side."""
    s = geo.skin(key)
    out = {}
    for a in s.art_layers:
        fr = C.base_frame(key, a.id, seed=SEED[key])
        C.finish_frame(fr, key, a.id)
        out[a.id] = fr
    return out


def paint(key, out_root=None):
    s = geo.skin(key)
    if s.buttons:
        raise SystemExit(f'{key}: unexpected painted buttons {[b.id for b in s.buttons]}; contract changed')
    root = Path(out_root) if out_root else geo.TEXTURES
    written = [C.save_png(paint_background(key), root / 'menu' / Path(s.asset).name)]
    for lid, fr in paint_frames(key).items():
        written.append(C.save_png(fr, root / 'frames' / key / f'{lid}.png'))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', help='write under DIR (menu/, frames/) instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        paths = paint(key, args.out_root)
        print(f'{key}: wrote {len(paths)} PNGs: ' + ', '.join(str(p) for p in paths))


if __name__ == '__main__':
    main()
