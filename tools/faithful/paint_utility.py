#!/usr/bin/env python3
"""Faithful theme painter for the utility screens: trashcan, ender_chest, crafting.

    python tools/faithful/paint_utility.py [--skin KEY] [--out-root DIR]

Paints, deterministically, every texture the three skins own: the
background of each and the outer frame of the two chests (crafting has no
frame and none of the three has buttons). Without ``--out-root`` the PNGs go
to pack-source/assets/quasar_gui/textures/; with it they go to DIR laid out
the same way (menu/, frames/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, sections 5-7). Restraint is the craft:
these are vanilla storage and crafting screens, so the shared base carries
the whole look.

* trashcan (chest_6, 54 wells): the plain light grey panel with one merged
  inset tray round the 6x9 grid, the red_1 utility accent line on row 14
  and the bin pictogram in one recessed tile on each docked side panel of
  the frame. Nothing else: the background has no static cell for a tile.
* ender_chest (chest_3, 27 wells): the same anatomy on the purple-tinted
  panel (ENDER_PANEL_RAMP: purple_1 panel, purple_0 bottom/right bevel), a
  purple_0 accent line and the ender orb tile on the frame's side panels.
  purple_1 (luminance 187) keeps the live title and "Inventory" rows light.
* crafting (176x166, no frame, live title at x=29): the plain vanilla
  crafting look. The 3x3 grid is one inset tray; the result slot is a
  larger 26x26 recessed square (a 2 px slot-grey margin round its
  transparent clearance inside one inset ring) so it reads as the output.
  The recipe-book toggle [4,33,22,20] and the arrow / recipe-ghost rect
  [88,30,28,24] stay fully transparent with nothing drawn round them, so
  the client's own toggle and arrow show unchanged. No accent line, no
  pictogram, no painted title.

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
import primitives as P  # noqa: E402
from palette import GREY  # noqa: E402

SKINS = ('trashcan', 'ender_chest', 'crafting')
SEED = {'trashcan': 41, 'ender_chest': 43, 'crafting': 47}
RESULT_BOX = 26                                     # the crafting output square


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def _result_box(key):
    """26x26 square centred on the result slot's clearance (slot 0)."""
    s = geo.skin(key)
    cl = next(sl for sl in s.content_slots if sl.index == 0).clearance
    m = (RESULT_BOX - cl.w) // 2
    return geo.Rect(cl.x - m, cl.y - m, RESULT_BOX, RESULT_BOX)


def paint_crafting(key='crafting'):
    """The plain crafting panel: the base gives the outlined panel, the 3x3
    grid tray and the player trays; the result slot's single-ring inset is
    replaced by the larger output square. finish_background clears every
    clearance and both extra-transparent rects last."""
    s = geo.skin(key)
    bg = C.base_background(key, seed=SEED[key], wells=False, accent=False, pictograms=False)
    result = next(sl for sl in s.content_slots if sl.index == 0)
    grid = [sl for sl in s.content_slots if sl.index != 0]
    holes = P.merge_holes(grid) + P.merge_holes(s.player_slots)
    P.inset_well(bg, holes, protect=C.text_rows(key))
    box = _result_box(key)
    # recessed square: slot-grey margin, dark top/left and white bottom/right
    # ring, mid-grey mixed corners; the 20x20 centre is cleared by finish
    P.inset_box(bg, box.tuple(), GREY[4])
    assert result.clearance.x > box.x and result.clearance.right < box.right
    C.finish_background(bg, key)
    return bg


def paint_background(key):
    if key == 'crafting':
        return paint_crafting(key)
    bg = C.base_background(key, seed=SEED[key])     # panel, trays, accent line (no static cells)
    C.finish_background(bg, key)
    return bg


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def paint_frames(key):
    """The base side-panel extension: one recessed pictogram tile per side
    panel (bin / ender orb), nothing else. Crafting has no art layer."""
    s = geo.skin(key)
    out = {}
    for a in s.art_layers:
        fr = C.base_frame(key, a.id, seed=SEED[key])
        C.finish_frame(fr, key, a.id)
        out[a.id] = fr
    return out


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _check_size(img, path):
    """Never change an existing texture's size or mode."""
    from PIL import Image
    if path.exists():
        with Image.open(path) as old:
            assert old.size == img.size, f'{path}: {img.size} != existing {old.size}'
            assert img.mode == 'RGBA', f'{path}: mode {img.mode}'


def paint(key, out_root=None):
    s = geo.skin(key)
    root = Path(out_root) if out_root else geo.TEXTURES
    written = []
    bg = paint_background(key)
    target = root / 'menu' / Path(s.asset).name
    _check_size(bg, geo.TEXTURES / 'menu' / Path(s.asset).name)
    written.append(C.save_png(bg, target))
    assert not s.buttons, f'{key}: unexpected buttons'
    for lid, fr in paint_frames(key).items():
        _check_size(fr, geo.TEXTURES / 'frames' / key / f'{lid}.png')
        written.append(C.save_png(fr, root / 'frames' / key / f'{lid}.png'))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', help='write under DIR (menu/, frames/) instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        paths = paint(key, args.out_root)
        print(f'{key}: wrote {len(paths)} PNGs')


if __name__ == '__main__':
    main()
