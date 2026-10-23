#!/usr/bin/env python3
"""Faithful theme painter for the invsee family: invsee_online, invsee_offline.

    python tools/faithful/paint_invsee.py [--skin KEY] [--out-root DIR]

Paints, deterministically, every texture the two skins own: the background
and the outer frame (the invsee screens have no painted buttons). Without
``--out-root`` the PNGs go to pack-source/assets/quasar_gui/textures/; with
it they go to DIR laid out the same way (menu/, frames/<skin>/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, section 5, invsee / invsee_offline):
both screens are chest_6 with all 54 top cells native (the inspected
player's inventory, armour and offhand are real items), so the shared base
carries the whole look:

* background: the light grey bevelled panel, one merged inset tray round all
  6 x 9 content clearances, the main 3x9 and hotbar 1x9 player trays, the
  title zone (rows 5-14) and "Inventory" rows left as plain light panel for
  the live text, and the family accent on the trays' top/left inner-shadow
  walls (``compose.draw_accent_line``). There are no static cells and no
  pictogram on the background.
* frame: the lean docked-tab frame, the eye on each tab, grips at mid-height.

The only difference between the two skins is the family whisper, so the
online / offline state reads at a glance without a single word:

* invsee_online: solid blue_1 tray walls, the open eye (blue iris) on the tabs.
* invsee_offline: the same blue walls broken into 2 px dashes (``dash``),
  the closed eye (lashes down) on the tabs.

Both come from ``palette.accent_for``; this script asserts them so a palette
change that made the two skins identical fails loudly instead of shipping.
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

from PIL import Image  # noqa: E402

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
from palette import accent_for, rgba  # noqa: E402

SKINS = ('invsee_online', 'invsee_offline')
SEED = {'invsee_online': 81, 'invsee_offline': 82}

# what each skin must show (style guide section 5); checked, never invented
EXPECT = {
    'invsee_online': {'wall': rgba('blue_1')[:3], 'pictogram': 'eye', 'dash': 0},
    'invsee_offline': {'wall': rgba('blue_1')[:3], 'pictogram': 'eye_closed', 'dash': 2},
}


def _check_identity(key):
    """The tray-wall tint, dash and pictogram the palette assigns must be
    the ones the design calls for, so online and offline always differ."""
    acc = accent_for(key)
    wall = tuple(C.wall_colour(C.accent_colour(key)) or ())[:3]
    want = EXPECT[key]
    if (wall != tuple(want['wall']) or acc.get('pictogram') != want['pictogram']
            or acc.get('dash', 0) != want['dash']):
        raise SystemExit(f'{key}: palette identity changed (wall {wall}, pictogram {acc.get("pictogram")}, '
                         f'dash {acc.get("dash", 0)}); expected {want}')


def _check_size(img, path):
    """Never change dimensions: match the PNG already in pack-source."""
    if path.exists():
        with Image.open(path) as cur:
            if cur.size != img.size:
                raise SystemExit(f'{path}: painted {img.size} but existing texture is {cur.size}')
    if img.mode != 'RGBA':
        raise SystemExit(f'{path}: mode {img.mode}, expected RGBA')


def paint_background(key):
    """Panel, full inset tray over every content well, player trays, their
    top/left walls in the family tint (dashed when offline). Nothing else."""
    bg = C.base_background(key, seed=SEED[key])
    C.finish_background(bg, key)                    # clear masks + stamp pin, always last
    return bg


def paint_frames(key):
    """The base lean frame: the open or closed eye on each docked tab, mirrored grips."""
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
    _check_identity(key)
    root = Path(out_root) if out_root else geo.TEXTURES
    jobs = [(paint_background(key), Path(s.background_path), root / 'menu' / Path(s.asset).name)]
    for lid, fr in paint_frames(key).items():
        jobs.append((fr, Path(s.frame_path(lid)), root / 'frames' / key / f'{lid}.png'))
    written = []
    for img, canonical, dest in jobs:
        _check_size(img, canonical)
        written.append(C.save_png(img, dest))
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
