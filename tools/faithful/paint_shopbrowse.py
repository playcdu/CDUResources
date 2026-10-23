#!/usr/bin/env python3
"""Faithful theme painter "shopbrowse": the chest-shop browsing screens.

    python tools/faithful/paint_shopbrowse.py [--skin KEY] [--out-root DIR]

Skins: chest_shop, chest_shop_owner (chest_3: 24 listing wells, a right
column of three 18x18 icon controls) and chest_shop_ads, chest_shop_search
(chest_6: 28 listing wells, an 18x72 balance column, a static top row and
right column, and a footer of Prev / Find / Create / Next / Close).

Paints, deterministically, every texture the four skins own: the background,
every button region in all six states and the outer frame. Without
``--out-root`` the PNGs go to pack-source/assets/quasar_gui/textures/; with
it they go to DIR laid out the same way (menu/, buttons/, frames/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, section 5, chest_shop): the shared
base carries the whole look. Family identity is the green_1 accent line
under the title band, one recessed chest tile in the largest static region
of the background (the chest_6 top row; the chest_3 screens have no static
cells, so none) and one chest tile on each docked side panel of the frame.
No scenes, no props, no words beyond the buttons' own labels.

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
import lettering as L  # noqa: E402

SKINS = ('chest_shop', 'chest_shop_owner', 'chest_shop_ads', 'chest_shop_search')
SEED = {'chest_shop': 31, 'chest_shop_owner': 37, 'chest_shop_ads': 41, 'chest_shop_search': 43}


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def paint_background(key):
    """Panel, inset trays round every listing and player clearance with the
    green family tint on their walls. Everything under a button and every
    static cell stay plain panel (no background pictogram tile)."""
    img = C.base_background(key, seed=SEED[key], pictograms=False)
    C.finish_background(img, key)                   # clear masks + stamp pin, always last
    return img


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def _paint_info_label(key, b):
    """A lettered read-only plate (chest_6 'Create'). The shared info grammar
    letters inside the plate minus its 1 px rim; CREATE in PLAIN capitals is
    34 px, exactly that box, so the C would sit on the dark rim. Narrowing the
    box by 1 px each side makes compose's own fit order choose the label's
    mixed case (Create, 32 px; style guide 9), leaving 1 px of air at both
    ends. Same words, same face, same ink_1."""
    img = C.new(b.w, b.h)
    x, y, w, h = C.info_face(img, b.body.tuple(), seed=SEED[key])
    lines, face = C.letter(img, b, (x + 1, y, w - 2, h), C.LABEL_DARK)
    assert face == 'plain', (key, b.id, lines, face)
    C.finish_button(img, key, b.id)
    return img


def _cramped_info(b):
    """True for a lettered info plate whose PLAIN capitals fill the whole box."""
    if C.button_kind(b) != 'info':
        return False
    x, y, w, h = b.body.tuple()
    return any(L.text_width(t, 'plain') >= w - 2 for t in b.text_lines)


def paint_buttons(key):
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        if _cramped_info(b):
            normal = _paint_info_label(key, b)
        else:
            normal = C.paint_button(key, b.id, seed=SEED[key])
        C.finish_button(normal, key, b.id)
        out[b.id] = C.button_states(normal, key, b.id)
    return out


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

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
    written = [C.save_png(paint_background(key), root / 'menu' / Path(s.asset).name)]
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
