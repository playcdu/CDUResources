#!/usr/bin/env python3
"""Faithful theme painter: the auction family.

    python tools/faithful/paint_auction.py                 # all six skins into pack-source
    python tools/faithful/paint_auction.py --skin auction_confirm
    python tools/faithful/paint_auction.py --out-root evidence/tmp/textures

Skins: auction_house, auction_search, auction_mine, auction_watchlist,
auction_confirm, auction_duration. For each one this paints the background,
every button region in all six states and the outer frame(s), deterministically
(fixed seeds, no clock, no unseeded randomness).

The look is the shared Faithful grammar (docs/FAITHFUL-STYLE-GUIDE.md) and
nothing more: the light grey vanilla-style panel, inset trays round the native
wells, stone buttons, a red_1 accent line under the title band and one gavel
pictogram tile in the largest static region; the frames are the docked
side-panel treatment with the gavel tile. Restraint is the craft: no scenes,
no props, no baked prices, names or page numbers.

``--out-root DIR`` writes the same layout as pack-source's textures directory
(DIR/menu/<asset>.png, DIR/buttons/<key>/<id>/<state>.png,
DIR/frames/<key>/<layer>.png) instead of pack-source.

Licence: MIT (tooling). The pixels it paints are CC0-1.0.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))                     # faithful modules first
for _p in (str(_HERE.parent), str(_HERE.parent / 'cozy')):
    if _p not in sys.path:
        sys.path.append(_p)                            # tools/ and the shared geometry

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import primitives as P  # noqa: E402
from palette import accent_for  # noqa: E402

SKINS = ('auction_house', 'auction_search', 'auction_mine',
         'auction_watchlist', 'auction_confirm', 'auction_duration')
SEED = 23


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

PAGED = ('auction_house', 'auction_search', 'auction_mine', 'auction_watchlist')


def paint_background(key):
    """The shared base background: panel, inset trays (28 listing wells on the
    paged screens, the single display well on confirm, none on duration),
    the red family tint on the tray walls. Static cells stay plain panel
    (backgrounds carry no pictogram tile; the gavel is on the frame tabs)."""
    bg = C.base_background(key, seed=SEED, pictograms=False)
    C.finish_background(bg, key)                       # clear masks + stamp pin, always last
    return bg


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def paint_buttons(key):
    """Every region in the shared grammar: secondary stone (My Items, Watch,
    Alerts, Find, durations), gold-bevel primary (Sell, Confirm Purchase),
    page-turn arrows (Prev / Previous / Next), red stone danger (Close),
    the 18x18 red close X and the recessed 18x72 balance column with the
    coin-slash icon. States come from the shared transforms."""
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        normal = C.paint_button(key, b.id, seed=SEED)
        C.finish_button(normal, key, b.id)
        out[b.id] = C.button_states(normal, key, b.id)
    return out


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def paint_frames(key):
    """Docked side panels in the vanilla bevel language, one gavel tile on
    each; no words, no click targets."""
    s = geo.skin(key)
    out = {}
    for a in s.art_layers:
        fr = C.base_frame(key, a.id, seed=SEED)
        C.finish_frame(fr, key, a.id)
        out[a.id] = fr
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def paint(key, out_root=None):
    s = geo.skin(key)
    written = {'background': 0, 'button': 0, 'frame': 0}
    bg = paint_background(key)
    bg_path = s.background_path if out_root is None else Path(out_root) / 'menu' / Path(s.asset).name
    C.save_png(bg, bg_path)
    written['background'] += 1
    for bid, states in paint_buttons(key).items():
        written['button'] += len(C.save_button_states(states, key, bid, root=out_root))
    for lid, fr in paint_frames(key).items():
        p = s.frame_path(lid) if out_root is None else Path(out_root) / 'frames' / key / f'{lid}.png'
        C.save_png(fr, p)
        written['frame'] += 1
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--skin', action='append', choices=SKINS,
                    help='paint only this skin (repeatable); default all six')
    ap.add_argument('--out-root', default=None,
                    help='textures root to write into instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        assert accent_for(key).get('pictogram') == 'gavel', key
        w = paint(key, args.out_root)
        print(f'PAINTED {key}: {w["background"]} background, {w["button"]} button states, {w["frame"]} frame(s)')


if __name__ == '__main__':
    main()
