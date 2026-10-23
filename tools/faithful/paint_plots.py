#!/usr/bin/env python3
"""Faithful theme painter for the plot family: plot_buy, plot_rent,
plot_list and plot_manage.

    python tools/faithful/paint_plots.py [--skin KEY] [--out-root DIR]

Paints, deterministically (fixed seeds, no clock, no unseeded randomness),
every texture the four skins own: the background, every button region in all
six states and the outer frame. Without ``--out-root`` the PNGs go to
pack-source/assets/quasar_gui/textures/; with it they go to DIR laid out the
same way (menu/, buttons/, frames/).

Design (docs/FAITHFUL-STYLE-GUIDE.md, section 5, plot): the shared base
carries the whole look. The family identity is exactly two things: the
green_1 tint on the top/left walls of every inset tray, and the signpost
pictogram (a two-plank wooden board on a post, standing on a grass plot) on
the frame's two docked tabs. Backgrounds carry no pictogram; every static
cell is plain panel.

* plot_buy / plot_rent (chest_6): one native display well at slot 22 (the
  live plot preview with its owner, bounds and price lore) as a single inset
  slot; Cancel (cells 27-29, 36-38) is red danger stone, as authored, and
  Confirm Purchase / Confirm Rental (cells 33-35, 42-44) the gold primary.
  The 26 decorative border cells and the rest of the static cells stay plain
  panel.
* plot_list (chest_6): the 45 plot entries (rows 0-4) as one inset tray;
  the footer row carries Previous Page, Close and Next Page in the shared
  grammar (page arrows, red stone Close; "Previous" in mixed case of its own
  line so the footer keeps one face). The tray's clearance trims row 0 of
  all three 54x18 regions alike, so the footer paints on one line
  (``compose.aligned_body``).
* plot_manage (chest_3): cells 13 and 14 stay native (their item, name and
  lore change with the plot state) as two inset slots; Toggle Preview and
  Rename are plain stone, Close and Destroy red stone, Teleport the gold
  primary, exactly as authored. Static cells 22 and 23 stay plain panel.

Nothing else: no prices, plot names, owners or page numbers, no fake items,
no words a control does not own.

Licence: MIT (tooling). The pixels it paints are CC0-1.0.
"""
from __future__ import annotations

import argparse
import dataclasses
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
from palette import accent_for  # noqa: E402

SKINS = ('plot_buy', 'plot_rent', 'plot_list', 'plot_manage')
SEED = {'plot_buy': 41, 'plot_rent': 41, 'plot_list': 43, 'plot_manage': 47}

# Page buttons lettered in mixed case of their own line: PREVIOUS in PLAIN
# capitals is 45 px and the page box beside the arrow is 42, so the shared
# fit order would drop to TINY next to a PLAIN NEXT and CLOSE. "Previous"
# (41 px) is the authored line in mixed case (style guide section 8), as on
# the auction watchlist and economy log, so the footer reads in one face.
MIXED_CASE = {('plot_list', 'previous'): ('Previous',)}


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def paint_background(key):
    """Shared base: panel, inset trays round the native wells (slot 22 on
    buy / rent, rows 0-4 on the list, cells 13-14 on manage) and the player
    trays, their top/left walls tinted green_1. Static cells stay plain panel
    (no background pictogram tile; the signpost is on the frame tabs)."""
    bg = C.base_background(key, seed=SEED[key], pictograms=False)
    C.finish_background(bg, key)                    # clear masks + stamp pin, always last
    return bg


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def mixed_case_page(key, button_id, seed):
    """A page-turn button (stone, arrow on the left) lettered with the
    mixed-case form of its own line (``MIXED_CASE``)."""
    b = geo.skin(key).button(button_id)
    lines = MIXED_CASE[(key, button_id)]
    assert [t.upper() for t in lines] == b.text_lines, (key, button_id)   # never other words
    img = C.new(b.w, b.h)
    body = C.aligned_body(b).tuple()
    box, arrow = C.page_face(img, body, 'next' if C.button_kind(b) == 'page_next' else 'prev', seed)
    C.remember_extras(img, b, arrow)
    C.letter(img, dataclasses.replace(b, lines=lines), box, C.LABEL_LIGHT, shadow=C.LABEL_SHADOW)
    C.finish_button(img, key, button_id)
    return img


def paint_buttons(key):
    """Every region in the shared grammar with its authored style (Cancel and
    Close red danger stone, Confirm / Teleport gold primary, the rest plain
    stone); states from the shared transforms."""
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        if (key, b.id) in MIXED_CASE:
            normal = mixed_case_page(key, b.id, SEED[key])
        else:
            normal = C.paint_button(key, b.id, seed=SEED[key])
        C.finish_button(normal, key, b.id)
        out[b.id] = C.button_states(normal, key, b.id)
    return out


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def paint_frames(key):
    """Lean frame: one docked tab per side with the signpost pictogram and
    the two mirrored grips, everything else alpha 0; no words, no click
    targets."""
    s = geo.skin(key)
    out = {}
    for a in s.art_layers:
        fr = C.base_frame(key, a.id, seed=SEED[key])
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
                    help='paint only this skin (repeatable); default all four')
    ap.add_argument('--out-root', default=None,
                    help='textures root to write into instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        assert accent_for(key).get('pictogram') == 'signpost', key
        w = paint(key, args.out_root)
        print(f'PAINTED {key}: {w["background"]} background, {w["button"]} button states, {w["frame"]} frame(s)')


if __name__ == '__main__':
    main()
