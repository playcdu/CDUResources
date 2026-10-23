#!/usr/bin/env python3
"""Faithful theme painter for the admin shop family: admin_shop_categories,
admin_shop_listings, admin_shop_search, admin_shop_configured.

    python tools/faithful/paint_adminshop.py [--skin KEY] [--out-root DIR]

Paints, deterministically, every texture the four skins own: the background
and the outer frame (none of them has painted buttons). Without
``--out-root`` the PNGs go to pack-source/assets/quasar_gui/textures/; with
it they go to DIR laid out the same way (menu/, frames/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, section 5, admin_shop): all four are
chest_6 screens whose 54 top cells are native content wells, so there is no
static region for a pictogram on the background. The shared base carries the
whole look: the light panel, one merged inset tray round the 6x9 grid, the
player trays, and the family identity as a whisper: the blue_1 accent line
on row 14 under the live title, and one recessed shield tile on each docked
side panel of the frame. The four screens are deliberately identical: the
live title is what tells them apart. No words, no scenes, no props.

Licence: MIT.
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

SKINS = ('admin_shop_categories', 'admin_shop_listings', 'admin_shop_search', 'admin_shop_configured')
SEED = 31                                           # one seed: the four screens are identical by design


def _expected_size(path, fallback):
    """Size of the PNG already in pack-source (never resize: match it)."""
    try:
        with Image.open(path) as im:
            return im.size
    except OSError:
        return fallback


def paint_background(key):
    bg = C.base_background(key, seed=SEED)          # panel, inset trays, blue accent line
    C.finish_background(bg, key)                    # clear masks + stamp pin, always last
    return bg


def paint_frames(key):
    s = geo.skin(key)
    out = {}
    for a in s.art_layers:
        fr = C.base_frame(key, a.id, seed=SEED)     # docked side panels with the shield tile
        C.finish_frame(fr, key, a.id)
        out[a.id] = fr
    return out


def paint(key, out_root=None):
    s = geo.skin(key)
    root = Path(out_root) if out_root else geo.TEXTURES
    written = []
    bg = paint_background(key)
    want = _expected_size(geo.TEXTURES / 'menu' / Path(s.asset).name, (s.width, s.height))
    assert bg.size == want and bg.mode == 'RGBA', (key, bg.size, want)
    written.append(C.save_png(bg, root / 'menu' / Path(s.asset).name))
    for lid, fr in paint_frames(key).items():
        a = s.layer(lid)
        want = _expected_size(geo.TEXTURES / 'frames' / key / f'{lid}.png', (a.w, a.h))
        assert fr.size == want and fr.mode == 'RGBA', (key, lid, fr.size, want)
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
