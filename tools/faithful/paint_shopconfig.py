#!/usr/bin/env python3
"""Faithful theme painter for the chest-shop configuration screens.

    python tools/faithful/paint_shopconfig.py [--skin KEY] [--out-root DIR]

Skins (eight backgrounds, 71 button regions x 6 states, eight frames):

    chest_shop_settings                    Back, Stats (info), Upgrade (primary),
                                           Rename Shop / Refresh Listings (54x36)
    chest_shop_buy / chest_shop_sell       More / Less, BUY NOW / SELL NOW (primary),
                                           Back, Option 1 / Opt 2 / Option 3 / Option 4
    chest_shop_upgrade[_confirm|_disabled] Back, Your Bid (info), More / Less,
                                           Tier 1-3, Apply (36x54 primary)
    chest_shop_listing_enabled|_disabled   Back, Stats / Stock / Quantity (info),
                                           Sell / Qty / Buy +/-, Sell / Buy Price,
                                           Disable Listing (danger) / Enable Listing
                                           (primary)

Without ``--out-root`` the PNGs go to pack-source/assets/quasar_gui/textures/;
with it they go to DIR laid out the same way (menu/, buttons/, frames/).
Deterministic: fixed seeds per screen family, no clock.

Design (docs/FAITHFUL-STYLE-GUIDE.md, sections 1, 5, 8): vanilla Minecraft
with painted buttons. The shared base carries the whole look; the chest-shop
family adds only

* the 1 px accent line under the title band: green_1 on every screen, red_1
  on the two "off" variants (chest_shop_upgrade_disabled,
  chest_shop_listing_disabled). The paired variants therefore differ only by
  that line and by the authored button states/labels, never by painted words;
* one recessed 16x16 chest pictogram tile in the largest static region of
  each background (every other static cell stays plain panel);
* one chest tile on each docked side panel of the frame.

Every control uses the shared grammar through ``compose.paint_button``: the
digits on Option 1 .. Option 4 and Tier 1 .. Tier 3 are their authored
labels on plain stone (never coins, never amounts), info regions are
recessed read-only plates, the two listing toggles keep their authored
danger red / primary gold styles. No well, no fake item, no baked value.

Licence: MIT.
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

import compose as C  # noqa: E402  (tools/faithful/compose.py; must precede geometry)
import geometry as geo  # noqa: E402
from palette import GREEN, RED  # noqa: E402

ACCENT_ON = GREEN[1]          # family accent: active / ready
ACCENT_OFF = RED[1]           # the "off" variant of a paired screen

# key -> (screen family, seed, accent line colour)
SCREENS = {
    'chest_shop_settings':         ('settings', 41, ACCENT_ON),
    'chest_shop_buy':              ('amount',   43, ACCENT_ON),
    'chest_shop_sell':             ('amount',   43, ACCENT_ON),
    'chest_shop_upgrade':          ('upgrade',  47, ACCENT_ON),
    'chest_shop_upgrade_confirm':  ('upgrade',  47, ACCENT_ON),
    'chest_shop_upgrade_disabled': ('upgrade',  47, ACCENT_OFF),
    'chest_shop_listing_enabled':  ('listing',  53, ACCENT_ON),
    'chest_shop_listing_disabled': ('listing',  53, ACCENT_OFF),
}
SKINS = tuple(SCREENS)

# The authored kind each region must resolve to through the shared grammar.
# Checked before painting so a manifest change can never silently turn a
# read-only plate into a pressable stone (or the reverse).
EXPECTED_KINDS = {
    'settings': {'back': 'secondary', 'stats': 'info', 'upgrade': 'primary',
                 'rename': 'secondary', 'refresh': 'secondary'},
    'amount':   {'back': 'secondary', 'increase': 'secondary', 'decrease': 'secondary',
                 'selected_amount': 'primary', 'preset_1': 'secondary', 'preset_2': 'secondary',
                 'preset_3': 'secondary', 'preset_4': 'secondary'},
    'upgrade':  {'back': 'secondary', 'bid': 'info', 'increase': 'secondary', 'decrease': 'secondary',
                 'tier_1': 'secondary', 'tier_2': 'secondary', 'tier_3': 'secondary',
                 'confirm': 'primary'},
    'listing':  {'back': 'secondary', 'stats': 'info', 'stock': 'info', 'quantity': 'info',
                 'sell_more': 'secondary', 'sell_price': 'secondary', 'sell_less': 'secondary',
                 'quantity_more': 'secondary', 'quantity_less': 'secondary',
                 'buy_more': 'secondary', 'buy_price': 'secondary', 'buy_less': 'secondary',
                 'toggle': None},        # danger on _enabled, primary on _disabled (authored)
}
# Labels lettered in PLAIN mixed case of their own authored label (guide 4.3
# and 9: mixed case is allowed for fit). In capitals these fill their text box
# to the last column (TIER 1 31/31 on a 36 px stone, BUY PRICE 49/49), so the
# shadow runs into the bevel; mixed case gives them air, and Buy Price then
# matches Sell Price, which the shared fit order already sets in mixed case.
MIXED_CASE = {'tier_1', 'tier_2', 'tier_3', 'buy_price'}
TOGGLE_KIND = {'chest_shop_listing_enabled': 'danger', 'chest_shop_listing_disabled': 'primary'}


# ---------------------------------------------------------------------------
# Shared per-screen helpers
# ---------------------------------------------------------------------------

def check_kinds(key):
    """Assert every region resolves to the grammar its screen expects."""
    family = SCREENS[key][0]
    want = dict(EXPECTED_KINDS[family])
    if 'toggle' in want:
        want['toggle'] = TOGGLE_KIND[key]
    s = geo.skin(key)
    got = {b.id: C.button_kind(b) for b in s.buttons}
    assert set(got) == set(want), f'{key}: regions {sorted(got)} != {sorted(want)}'
    bad = {k: (got[k], want[k]) for k in got if got[k] != want[k]}
    assert not bad, f'{key}: unexpected button kinds {bad}'


def background(key):
    """The base panel (no wells on these screens), the chest tile in the
    largest static region, then the accent line in the screen's colour."""
    _, seed, accent = SCREENS[key]
    img = C.base_background(key, seed=seed, accent=False)
    C.draw_accent_line(img, key, colour=accent)
    C.finish_background(img, key)                    # clear masks + stamp pin, always last
    return img


def mixed_case_secondary(key, button_id, seed):
    """A plain stone button lettered in PLAIN mixed case of its own label.
    The label is passed to ``compose.letter`` as a one-line proxy of the same
    region (same skin key and id), so the glyph pixels are registered exactly
    as ``paint_button`` would and the states protect them; on a copy the
    whole-label template search finds the same mixed-case option."""
    b = geo.skin(key).button(button_id)
    assert C.button_kind(b) == 'secondary' and not b.lines, (key, button_id)
    img = C.new(b.w, b.h)
    box = C.secondary_face(img, b.body.tuple(), seed)
    C.letter(img, dataclasses.replace(b, lines=(b.label,)), box, C.LABEL_LIGHT, shadow=C.LABEL_SHADOW)
    C.finish_button(img, key, button_id)
    return img


def paint_normal(key, button_id, seed):
    if button_id in MIXED_CASE:
        return mixed_case_secondary(key, button_id, seed)
    return C.paint_button(key, button_id, seed=seed)


def buttons(key):
    """Every region of the skin in the shared grammar, six states each."""
    seed = SCREENS[key][1]
    out = {}
    for b in geo.skin(key).buttons:
        normal = paint_normal(key, b.id, seed)
        C.finish_button(normal, key, b.id)
        out[b.id] = C.button_states(normal, key, b.id)
    return out


def frames(key):
    """Docked side panels carrying the chest tile only."""
    seed = SCREENS[key][1]
    out = {}
    for a in geo.skin(key).art_layers:
        fr = C.base_frame(key, a.id, seed=seed)
        C.finish_frame(fr, key, a.id)
        out[a.id] = fr
    return out


# ---------------------------------------------------------------------------
# Per-screen painters (one per screen family; variants share them)
# ---------------------------------------------------------------------------

def paint_settings(key):
    """Back / Stats plate / Upgrade primary on the top row, the two tall
    secondary buttons either side of the static block that holds the tile."""
    return background(key), buttons(key), frames(key)


def paint_amount(key):
    """Buy and sell share one layout: the primary BUY NOW / SELL NOW in the
    middle row, More / Less on the left, the four option presets on plain
    stone. The tile sits in the static cells under Back."""
    return background(key), buttons(key), frames(key)


def paint_upgrade(key):
    """Three variants of one screen. The Apply column is the tall primary;
    on _disabled the server shows its disabled frame by default, and the
    accent line turns red. Button PNGs are identical across the three."""
    return background(key), buttons(key), frames(key)


def paint_listing(key):
    """Three columns of Sell / Qty / Buy controls under three info plates,
    the wide toggle below. The tile sits in the static cells left of it."""
    return background(key), buttons(key), frames(key)


PAINTERS = {'settings': paint_settings, 'amount': paint_amount,
            'upgrade': paint_upgrade, 'listing': paint_listing}


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def paint(key, out_root=None):
    check_kinds(key)
    s = geo.skin(key)
    bg, btns, frs = PAINTERS[SCREENS[key][0]](key)
    root = Path(out_root) if out_root else geo.TEXTURES
    written = {'background': [], 'buttons': [], 'frames': []}
    written['background'].append(C.save_png(bg, root / 'menu' / Path(s.asset).name))
    for bid, states in btns.items():
        written['buttons'] += C.save_button_states(states, key, bid, root=None if out_root is None else root)
    for lid, fr in frs.items():
        written['frames'].append(C.save_png(fr, root / 'frames' / key / f'{lid}.png'))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', help='write under DIR (menu/, buttons/, frames/) instead of pack-source')
    args = ap.parse_args(argv)
    total = {'background': 0, 'buttons': 0, 'frames': 0}
    for key in args.skin or SKINS:
        w = paint(key, args.out_root)
        for k in total:
            total[k] += len(w[k])
        print(f'{key}: {len(w["background"])} background, {len(w["buttons"])} button PNGs, '
              f'{len(w["frames"])} frame')
    print(f'total: {total["background"]} backgrounds, {total["buttons"]} button PNGs, {total["frames"]} frames')


if __name__ == '__main__':
    main()
