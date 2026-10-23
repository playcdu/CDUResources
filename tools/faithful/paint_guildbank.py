#!/usr/bin/env python3
"""Faithful theme painter for the guild bank family.

    python tools/faithful/paint_guildbank.py [--skin KEY] [--out-root DIR]

Paints, deterministically, every texture the eight guild bank skins own:
guild_bank_select_1 (chest_1), guild_bank_select_3 (chest_3) and
guild_bank_1 .. guild_bank_6 (chest_1 .. chest_6), each one background and
one outer frame (``menu_frame``). None of them has buttons. Without
``--out-root`` the PNGs go to pack-source/assets/quasar_gui/textures/; with
it they go to DIR laid out the same way (menu/, frames/<key>/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, sections 5-7, guild_bank): all eight
screens are native_content_preserved chests, so the shared base carries the
whole look and nothing is added on top:

* the light grey bevelled panel with the full inset tray round every vault
  slot and the two player trays (main 3x9 and hotbar), title and
  "Inventory" rows left as plain light panel for the live vanilla text;
* the 1 px gold_1 guild bank accent line on row 14 under the title band;
* no static decorative cells exist, so the background carries no tile;
* the frame is the docked side-panel extension with one 24x24 recessed tile
  per side panel holding the banner pictogram (a blue banner on a rod with a
  gold coin device), composed by the base for each of the six heights.

The vault selection screens are identical to the vault content screens. The
guide's icon set (icons.PICTOGRAMS, section 4.8) has no key glyph and
section 5 limits a family to exactly two identity marks (line + pictogram),
so no select-only key mark is drawn: which screen is which is told by the
live title and the native items, never by baked art.

Before writing, every target's existing PNG is opened and its size and mode
compared with the geometry: the painter never resizes an asset.

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

from PIL import Image  # noqa: E402

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402

SKINS = ('guild_bank_select_1', 'guild_bank_select_3',
         'guild_bank_1', 'guild_bank_2', 'guild_bank_3',
         'guild_bank_4', 'guild_bank_5', 'guild_bank_6')
SEED = {k: 41 + i for i, k in enumerate(SKINS)}


def _check_existing(path, size):
    """The pack-source PNG we replace must already have this exact size."""
    path = Path(path)
    if not path.exists():
        return
    with Image.open(path) as im:
        if im.size != tuple(size):
            raise SystemExit(f'{path}: existing size {im.size} != geometry {size}; refusing to resize')


def paint_background(key):
    s = geo.skin(key)
    bg = C.base_background(key, seed=SEED[key])     # panel, inset trays, gold accent line
    C.finish_background(bg, key)                    # clear masks + stamp pin, always last
    assert bg.size == (s.width, s.height) and bg.mode == 'RGBA'
    return bg


def paint_frames(key):
    s = geo.skin(key)
    out = {}
    for a in s.art_layers:
        fr = C.base_frame(key, a.id, seed=SEED[key])   # docked side panels, banner tiles
        C.finish_frame(fr, key, a.id)
        assert fr.size == (a.w, a.h) and fr.mode == 'RGBA'
        out[a.id] = fr
    return out


def paint(key, out_root=None):
    s = geo.skin(key)
    written = []
    bg = paint_background(key)
    _check_existing(s.background_path, (s.width, s.height))
    p = s.background_path if out_root is None else Path(out_root) / 'menu' / Path(s.asset).name
    C.save_png(bg, p)
    written.append(p)
    for lid, fr in paint_frames(key).items():
        a = s.layer(lid)
        _check_existing(s.frame_path(lid), (a.w, a.h))
        p = s.frame_path(lid) if out_root is None else Path(out_root) / 'frames' / key / f'{lid}.png'
        C.save_png(fr, p)
        written.append(p)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', action='append', choices=SKINS,
                    help='paint only this skin (repeatable); default all eight')
    ap.add_argument('--out-root', help='write under DIR (menu/, frames/) instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        for path in paint(key, args.out_root):
            print('WROTE', path)


if __name__ == '__main__':
    main()
