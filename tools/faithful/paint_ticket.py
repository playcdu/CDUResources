#!/usr/bin/env python3
"""Faithful theme painter for the ticket family: ticket_valid, ticket_invalid.

    python tools/faithful/paint_ticket.py [--skin KEY] [--out-root DIR]

Paints, deterministically, every texture the two skins own: the background,
both button regions (Cancel, Redeem Ticket) in all six states and the outer
frame. Without ``--out-root`` the PNGs go to
pack-source/assets/quasar_gui/textures/; with it they go to DIR laid out the
same way (menu/, buttons/, frames/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, section 5, ticket): the shared base
carries the whole look. Both screens are chest_6 with one native display
item (slot 22) and two 54x36 buttons. The family identity is exactly two
things: the top/left walls of the display well and the player trays, tinted
green_1 on valid and red_1 on invalid, and the ticket-stub pictogram (green
stripe on valid, red stripe on invalid) on the frame's two docked tabs. The
static cells stay plain panel. Validity is told by that colour and by the
Redeem button's default state (normal on valid, disabled on invalid); never
by words.

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

SKINS = ('ticket_valid', 'ticket_invalid')
SEED = {'ticket_valid': 31, 'ticket_invalid': 37}


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def paint_background(key):
    """Shared base: panel, the one inset display well, the player trays and
    the family tint on their walls. Static cells stay plain panel (no
    background pictogram tile; the ticket stub is on the frame tabs)."""
    bg = C.base_background(key, seed=SEED[key], pictograms=False)
    C.finish_background(bg, key)                    # clear masks + stamp pin, always last
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
