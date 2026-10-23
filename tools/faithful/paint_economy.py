#!/usr/bin/env python3
"""Faithful theme painter for the economy family: economy_hub, economy_log.

    python tools/faithful/paint_economy.py [--skin KEY] [--out-root DIR]

Paints, deterministically, every texture the two skins own: the background,
every button region in all six states and the outer frame. Without
``--out-root`` the PNGs go to pack-source/assets/quasar_gui/textures/;
with it they go to DIR laid out the same way (menu/, buttons/, frames/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, section 5, economy): the shared base
carries the whole look. The only family identity is the gold_0 tint on the
top/left walls of the inset trays (economy_log's listing wells and both
skins' player wells) and the coin pictogram on each of the frame's two docked
tabs, beside a ribbed grip on each side. Static cells (economy_log's top row
and left column) stay plain panel: backgrounds carry no pictogram tile.
Restraint is the point: no scenes, no props, no words beyond button labels.

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

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402

SKINS = ('economy_hub', 'economy_log')
SEED = {'economy_hub': 11, 'economy_log': 23}


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def paint_background(key):
    bg = C.base_background(key, seed=SEED[key], pictograms=False)   # no background tile (guide 5)
    return bg


# ---------------------------------------------------------------------------
# Buttons and frames
# ---------------------------------------------------------------------------

def paint_buttons(key):
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        normal = C.paint_button(key, b.id, seed=SEED[key])
        C.finish_button(normal, key, b.id)
        out[b.id] = C.button_states(normal, key, b.id)
    return out


def paint_frames(key):
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

def paint(key, out_root=None):
    s = geo.skin(key)
    root = Path(out_root) if out_root else geo.TEXTURES
    written = []
    bg = paint_background(key)
    C.finish_background(bg, key)                    # clear masks + stamp pin, always last
    written.append(C.save_png(bg, root / 'menu' / Path(s.asset).name))
    for bid, states in paint_buttons(key).items():
        written += C.save_button_states(states, key, bid, root=None if out_root is None else root)
    for lid, fr in paint_frames(key).items():
        written.append(C.save_png(fr, root / 'frames' / key / f'{lid}.png'))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', help='write under DIR (menu/, buttons/, frames/) instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        paths = paint(key, args.out_root)
        print(f'{key}: wrote {len(paths)} PNGs')


if __name__ == '__main__':
    main()
