#!/usr/bin/env python3
"""Faithful theme painter for the trade family: trade_idle, trade_self_ready,
trade_other_ready, trade_both_ready and trade_money.

    python tools/faithful/paint_trade.py [--skin KEY] [--out-root DIR]

Paints, deterministically, every texture the five skins own: the background,
every button region in all six states and the outer frame (the four chest
skins; trade_money is a dispenser screen and has none). Without
``--out-root`` the PNGs go to pack-source/assets/quasar_gui/textures/; with
it they go to DIR laid out the same way (menu/, buttons/, frames/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, section 5, trade): the shared base
carries the whole look. The family identity is the blue_1 accent line under
the title band and the two-arrows pictogram (a recessed tile in the divider,
one tile on each docked side panel of the frame).

The one thing this family needs (docs/PAINTED-BUTTONS.md): the centre
divider column of the four chest skins (cells 4, 13, 22, 31, 40 at x 79..96,
between your offer on the left and theirs on the right) carries two
independent, wordless readiness lamps, a recessed socket holding a small
black-outlined lamp:

    cell 13  YOU   (upper)   grey lamp = not ready, green lamp + white check = ready
    cell 22  the two-arrows pictogram tile (your offer goes right, theirs comes left)
    cell 31  THEM  (lower)   same lamp

so idle / self_ready / other_ready / both_ready differ only in which lamps
are lit. The marks are noninteractive; the Ready action stays the footer
button. Cells 4 and 40 stay plain panel.

trade_money (dispenser) is the base: the static OFFERED MONEY label in PLAIN
ink_1 centred on x=88 (the documented dispenser exception, drawn by
``base_background``), three stacked stone buttons, plain side thirds.

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
import icons  # noqa: E402
import primitives as P  # noqa: E402
from palette import GREEN, GREY, INK  # noqa: E402

CHEST_SKINS = ('trade_idle', 'trade_self_ready', 'trade_other_ready', 'trade_both_ready')
SKINS = CHEST_SKINS + ('trade_money',)
SEED = {'trade_idle': 31, 'trade_self_ready': 31, 'trade_other_ready': 31, 'trade_both_ready': 31,
        'trade_money': 37}
READY = {                       # (you ready, them ready)
    'trade_idle': (False, False),
    'trade_self_ready': (True, False),
    'trade_other_ready': (False, True),
    'trade_both_ready': (True, True),
}

# Divider geometry (chest_6): native cells at x 80 (column 4), pitch 18 from y 18.
DIVIDER_X = 80                  # native 16 px footprint x of the centre column
CELL_Y = {4: 18, 13: 36, 22: 54, 31: 72, 40: 90}
YOU_CELL, PICTO_CELL, THEM_CELL = 13, 22, 31


# ---------------------------------------------------------------------------
# The readiness lamp (original sprite, drawn from scratch)
# ---------------------------------------------------------------------------
#
# 12x12 overall: a recessed socket ring (grey_0 top/left, grey_7 bottom/right,
# grey_4 mixed corners) round a 10x10 lamp with a black notched outline. The
# lamp face has a one-step bevel of its own ramp: grey when off, green when
# lit; the lit lamp carries a bold white check.

LAMP = [
    'sssssssssssm',
    's.OOOOOOOO.h',
    'sOLLLLLLLLOh',
    'sOLffffffdOh',
    'sOLffffffdOh',
    'sOLffffffdOh',
    'sOLffffffdOh',
    'sOLffffffdOh',
    'sOLffffffdOh',
    'sOLddddddddh',
    's.OOOOOOOO.h',
    'mhhhhhhhhhhh',
]
# The 'd' in column 10 of row 9 is the outline position; fixed below.
LAMP[9] = 'sOLdddddddOh'

CHECK = [                       # 6x5 bold check, drawn on the face at (x+3, y+4)
    '.....W',
    '....WW',
    'W..WW.',
    'WWWW..',
    '.WW...',
]

LAMP_KEYS = {
    False: {'O': INK[0], 'L': GREY[5], 'f': GREY[4], 'd': GREY[3]},
    True: {'O': INK[0], 'L': GREEN[2], 'f': GREEN[1], 'd': GREEN[0]},
}
SOCKET = {'s': GREY[0], 'h': GREY[7], 'm': GREY[4]}


def draw_lamp(img, x, y, lit):
    """The 12x12 readiness lamp with its top-left at (x, y)."""
    P.sprite(img, x, y, LAMP, key={**SOCKET, **LAMP_KEYS[lit]})
    if lit:
        P.sprite(img, x + 3, y + 4, CHECK, key={'W': GREY[7]})


def lamp_box(cell):
    """12x12 box centred on the 16 px native footprint of a divider cell."""
    return (DIVIDER_X + 2, CELL_Y[cell] + 2, 12, 12)


def picto_box(cell):
    """14x16 recessed tile across the divider's free columns (x 81..94)."""
    return (DIVIDER_X + 1, CELL_Y[cell], 14, 16)


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def paint_background(key):
    if key == 'trade_money':
        return C.base_background(key, seed=SEED[key])      # OFFERED MONEY label, plain panel
    bg = C.base_background(key, seed=SEED[key], pictograms=False)
    you, them = READY[key]
    C.pictogram_tile(bg, picto_box(PICTO_CELL), 'arrows')
    draw_lamp(bg, *lamp_box(YOU_CELL)[:2], you)
    draw_lamp(bg, *lamp_box(THEM_CELL)[:2], them)
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
