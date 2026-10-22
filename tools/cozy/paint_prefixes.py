#!/usr/bin/env python3
"""Cozy painter for the prefixes family: name tags pinned to a corkboard.

    python tools/cozy/paint_prefixes.py                     # all six skins -> pack-source
    python tools/cozy/paint_prefixes.py --skin prefixes_3   # one skin
    python tools/cozy/paint_prefixes.py --out-root DIR      # DIR/menu/..., DIR/frames/...

Skins: prefixes_1 .. prefixes_6 (chest_1 .. chest_6 geometry, every top cell a
native well holding a selectable prefix item; no painted buttons). Each skin
owns one background (176 x 114+18N) and one outer frame (256 x height+16).

Background: a light cork sheet (hand-authored granule tile, not noise) with a
rounded ink rim. The title and inventory bands are parchment strips held by
coloured drawing pins (the title strip has a curled corner, the inventory
strip carries a pencil at its far right, clear of the live label). The native
prefix wells are recessed into the cork with a plum running stitch, like the
stitched edge of a linen name tag, and every row of tags is pinned at both
side margins. Player wells keep the shared parchment stitch so they read as
the player's own, calm inventory.

Frame: the corkboard's wooden edge (the shared beams, rim and brass corners)
around two darker recessed cork panels. Left: the PREFIXES heading tag hung
from a drawing pin, pinned blank name badges, a ruled blank card, a cluster of
spare pins (more badges / a tag strip on taller boards). Right: garlands of
blank hanging tags on twine between drawing pins, the twine running down to a
ball of twine resting on the bottom ledge. A pencil lies on the ledge under
the sheet. Compositions are laid out per height, not cropped. No words other
than the PREFIXES heading; no fake items, names or counts anywhere.

Deterministic: fixed seeds only. Licence: code MIT; artwork CC0-1.0.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import lettering as L  # noqa: E402
import primitives as P  # noqa: E402
from palette import (BERRY, BRASS, EMBER, INK, PARCHMENT, PLUM, SAGE, SKY,  # noqa: E402
                     WOOD, step)

KEYS = [f'prefixes_{n}' for n in range(1, 7)]
SEED = 41

# Cork ramps: (body, granule, deep granule, light fleck). The frame's cork is
# one step darker than the sheet's, so the menu reads as a raised cork tile.
CORK_SHEET = (WOOD[3], WOOD[2], WOOD[1], WOOD[4])
CORK_FRAME = (WOOD[2], WOOD[1], WOOD[0], WOOD[3])

# Hand-authored 16x16 cork tile: '.' body, 'd' granule, 'D' deep granule,
# 'l' light fleck. Sparse clusters, placed by hand, repeated as a tile. Kept
# to about one mark in twelve so the board reads as calm cork, not speckle.
CORK_TILE = [
    '................',
    '.dd.........l...',
    '..d.............',
    '..........D.....',
    '.......l........',
    '....D.......dd..',
    '.............d..',
    '................',
    '.l.......dd.....',
    '..........d.....',
    '.....d..........',
    '....dd.......l..',
    '................',
    '.D.........d....',
    '........l.......',
    '................',
]
assert all(len(r) == 16 for r in CORK_TILE) and len(CORK_TILE) == 16

# Drawing pin seen from the front: round head, glint top-left.
PIN = ['.ooo.', 'og32o', 'o321o', 'o211o', '.ooo.']
PIN_SMALL = ['.oo.', 'o32o', 'o21o', '.oo.']

# Pencil, drawn vertically (eraser at the top, graphite at the bottom).
PENCIL = [
    '.ooo.',
    'o221o',
    'o211o',
    'o3B0o',
    'oBb0o',
    'o3B0o',
] + ['oLMDo'] * 14 + [
    'oWWwo',
    '.oWo.',
    '.oko.',
    '..o..',
]
K_PENCIL = {'o': INK[1], '2': BERRY[2], '1': BERRY[1], '3': BRASS[3], 'B': BRASS[2],
            'b': BRASS[1], '0': BRASS[0], 'L': EMBER[2], 'M': EMBER[1], 'D': EMBER[0],
            'W': WOOD[4], 'w': WOOD[3], 'k': INK[0]}

TAG_RAMPS = [PLUM, EMBER, SKY, BERRY, SAGE]


# ---------------------------------------------------------------------------
# Small drawing helpers (local to this painter)
# ---------------------------------------------------------------------------

def rotate_sprite(rows):
    """Rotate an ASCII sprite 90 degrees clockwise (top -> right)."""
    rows = list(rows)
    h, w = len(rows), max(len(r) for r in rows)
    rows = [r.ljust(w, '.') for r in rows]
    return [''.join(rows[h - 1 - j][i] for j in range(h)) for i in range(w)]


def cork_fill(img, box, ramp, phase=(0, 0)):
    x, y, w, h = box
    body, dark, deep, light = ramp
    key = {'d': dark, 'D': deep, 'l': light}
    for yy in range(y, y + h):
        row = CORK_TILE[(yy + phase[1]) % 16]
        for xx in range(x, x + w):
            ch = row[(xx + phase[0]) % 16]
            P.put(img, xx, yy, key.get(ch, body))


def shadowed(img, draw, dx=1, dy=1):
    """Draw onto a scratch layer, cast a one-step-darker shadow of it at
    (+dx, +dy) onto what is already painted, then lay the drawing on top."""
    layer = C.new(img.width, img.height)
    draw(layer)
    la, ia = layer.load(), img.load()
    for yy in range(img.height):
        for xx in range(img.width):
            if la[xx, yy][3] or not ia[xx, yy][3]:
                continue
            sx, sy = xx - dx, yy - dy
            if 0 <= sx < img.width and 0 <= sy < img.height and la[sx, sy][3]:
                P.put(img, xx, yy, step(ia[xx, yy], -1))
    img.alpha_composite(layer)
    return img


def pin(img, cx, cy, ramp, small=False):
    """Drawing pin with its head centred on (cx, cy)."""
    if small:
        P.sprite(img, cx - 1, cy - 1, PIN_SMALL, {'o': INK[1], '3': ramp[2], '2': ramp[1], '1': ramp[0]})
    else:
        P.sprite(img, cx - 2, cy - 2, PIN, {'o': INK[1], 'g': PARCHMENT[3], '3': ramp[2],
                                            '2': ramp[1], '1': ramp[0]})


def hang_tag(img, x, y, w, h, ramp, style=0):
    """Blank hanging name tag: clipped top corners, reinforced string hole.
    style 0: dyed tag with a blank cream writing panel; 1: cream tag with a
    dyed hem; 2: dyed tag, plain. Never carries words."""
    inside = {(i, j) for j in range(h) for i in range(w) if not (j + i < 2 or j + (w - 1 - i) < 2)}
    edge = P._edge_pixels(inside)
    body = PARCHMENT[2] if style == 1 else ramp[1]
    for (i, j) in inside:
        P.put(img, x + i, y + j, body)
    for (i, j) in inside - edge:
        if i == 1:
            P.put(img, x + i, y + j, PARCHMENT[3] if style == 1 else ramp[2])
        elif i == w - 2:
            P.put(img, x + i, y + j, PARCHMENT[1] if style == 1 else ramp[0])
    for (i, j) in edge:
        P.put(img, x + i, y + j, INK[0] if j == h - 1 else INK[1])
    cx = x + w // 2
    ring = PARCHMENT[3] if style != 1 else BRASS[2]
    for (px, py) in ((cx - 1, y + 2), (cx + 1, y + 2), (cx, y + 1), (cx, y + 3)):
        P.put(img, px, py, ring)
    P.put(img, cx, y + 2, INK[0])
    if style == 0 and h >= 10:
        P.fill(img, (x + 1, y + 5, w - 2, h - 7), PARCHMENT[2])
        P.hline(img, x + 1, x + w - 3, y + 5, PARCHMENT[3])
        P.hline(img, x + 2, x + w - 3, y + h - 4, PARCHMENT[0])     # blank writing line
    elif style == 1:
        P.fill(img, (x + 1, y + h - 4, w - 2, 3), ramp[1])
        P.hline(img, x + 1, x + w - 2, y + h - 5, ramp[2])


def name_badge(img, x, y, w, h, ramp, seed=0):
    """Pinned blank name badge: dyed header band, cream body with one ruled
    writing line (no words), small stitched hem, pin at the top centre."""
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=1, heavy='b', fill_colour=PARCHMENT[2])
    P.fill(img, (x + 1, y + 1, w - 2, 4), ramp[1])
    P.hline(img, x + 2, x + w - 3, y + 1, ramp[2])
    P.hline(img, x + 1, x + w - 2, y + 4, ramp[0])
    P.highlight_edge(img, (x, y + 4, w, h - 4), PARCHMENT[3], 'l', inset=1)
    P.hline(img, x + 1, x + w - 2, y + h - 2, PARCHMENT[1])
    P.stitch_line(img, x + 3, y + h - 6, x + w - 4, y + h - 6, PARCHMENT[0], 2, 1)
    P.stitch_line(img, x + 2, y + 2, x + w - 3, y + 2, ramp[2], 1, 2, phase=seed)
    pin(img, x + w // 2, y + 2, PLUM if ramp is not PLUM else EMBER)


def blank_card(img, x, y, w, h, seed):
    """A pinned parchment card with sky ruled lines (no words) and a curl."""
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=True)
    P.hline(img, x + 3, x + w - 4, y + 5, BERRY[2])                  # margin rule
    for k in range(9, h - 4, 4):
        P.stitch_line(img, x + 3, y + k, x + w - 4, y + k, SKY[2], 4, 1, phase=k)
    P.page_curl(img, (x, y, w, h), 'br', 5, behind=CORK_FRAME[0])


def heading_tag(img, panel, text, top, seed):
    """The leftHeading on a linen name tag hung by twine from a drawing pin."""
    tw = L.text_width(text, 'sprig')
    w = tw + 6
    x = panel.x + (panel.w - w) // 2
    y = top + 6
    pcx = panel.x + panel.w // 2

    def draw(lay):
        P.twine(lay, pcx - 1, top + 1, x + 4, y + 1, sag=0)
        P.twine(lay, pcx + 1, top + 1, x + w - 5, y + 1, sag=0)
        P.ink_outline(lay, (x, y, w, 12), 'ink_1', radius=1, heavy='b', fill_colour=PARCHMENT[2])
        P.fill(lay, (x + 1, y + 1, w - 2, 2), PLUM[1])
        P.hline(lay, x + 2, x + w - 3, y + 1, PLUM[2])
        P.hline(lay, x + 1, x + w - 2, y + 3, PARCHMENT[3])
        P.hline(lay, x + 1, x + w - 2, y + 10, PARCHMENT[1])
        for ex in (x + 4, x + w - 5):
            P.put(lay, ex, y + 1, INK[0])
        L.draw_text(lay, x + 3, y + 4, text, 'ink_0', face='sprig')
        pin(lay, pcx, top, EMBER)
    shadowed(img, draw)
    return y + 12


def garland(img, x0, x1, y, sag, tags, seed):
    """Twine between two drawing pins with blank tags hanging from it.
    ``tags`` = [(dx, ramp, style, h)]."""
    def draw(lay):
        pts = P.twine(lay, x0, y, x1, y, sag=sag)
        ys = {px: py for px, py in pts}
        for dx, ramp, style, h in tags:
            tx = x0 + dx
            ty = ys.get(tx + 3, y + sag)
            P.vline(lay, tx + 3, ty, ty + 1, PARCHMENT[0])
            hang_tag(lay, tx, ty + 1, 7, h, ramp, style)
        pin(lay, x0, y, PLUM)
        pin(lay, x1, y, EMBER)
    shadowed(img, draw)


BALL_WRAPS = [((1, 5), (7, 11)), ((3, 2), (11, 10)), ((7, 1), (13, 7)),     # one way
              ((2, 9), (9, 1)), ((5, 11), (12, 4))]                     # crossing
BALL_W, BALL_H = 14, 12


def twine_ball(img, x, y):
    """Ball of twine, 14x12: lit top-left, wraps laid as hand-set chords in
    two crossing directions, heavier ink at the bottom where it rests."""
    cx, cy = 6.5, 5.5
    inside = {(i, j) for j in range(BALL_H) for i in range(BALL_W)
              if ((i - cx) / 7.0) ** 2 + ((j - cy) / 6.0) ** 2 <= 1.0}
    edge = P._edge_pixels(inside)
    for (i, j) in inside:
        d = (i - 4) ** 2 + (j - 3) ** 2
        c = PARCHMENT[3] if d <= 5 else PARCHMENT[2] if d <= 24 else PARCHMENT[1] if d <= 56 else PARCHMENT[0]
        P.put(img, x + i, y + j, c)
    for k, ((a, b), (c, d)) in enumerate(BALL_WRAPS):
        for (i, j) in P.line_points(a, b, c, d):
            if (i, j) in inside and (i, j) not in edge:
                dd = (i - 4) ** 2 + (j - 3) ** 2
                P.put(img, x + i, y + j, PARCHMENT[1] if dd <= 8 else PARCHMENT[0] if dd <= 40 else INK[2])
    for (i, j) in edge:
        P.put(img, x + i, y + j, INK[0] if j >= BALL_H - 3 or i >= BALL_W - 2 else INK[1])
    P.put(img, x + 3, y + 2, PARCHMENT[3]); P.put(img, x + 4, y + 2, PARCHMENT[3]); P.put(img, x + 3, y + 3, PARCHMENT[3])


def lug_tag(img, x, y, w, h, ramp, pin_at, seed=0):
    """Horizontal linen luggage tag (blank), dyed tail band, tied through its
    eyelet with a twine loop to a drawing pin at ``pin_at``."""
    P.linen_tag(img, (x, y, w, h), eyelet='left', seed=seed)
    P.fill(img, (x + w - 5, y + 1, 4, h - 2), ramp[1])
    P.vline(img, x + w - 5, y + 1, y + h - 2, ramp[2])
    P.vline(img, x + w - 2, y + 2, y + h - 2, ramp[0])
    P.put(img, x + w - 2, y + 1, ramp[1])
    ex, ey = x + 4, y + h // 2
    P.twine(img, ex - 1, ey, pin_at[0] - 1, pin_at[1] + 1, sag=0)
    P.twine(img, ex + 1, ey, pin_at[0] + 1, pin_at[1] + 1, sag=0, colour='parch_0', knot='parch_1')
    P.put(img, ex, ey, INK[0])
    pin(img, pin_at[0], pin_at[1], ramp if ramp is not PLUM else BERRY)


def pencil(img, x, y, horizontal=False):
    rows = rotate_sprite(PENCIL) if horizontal else PENCIL
    if horizontal:
        rows = [r[::-1] for r in rows]          # graphite to the left
    P.sprite(img, x, y, rows, K_PENCIL)
    return P.sprite_size(rows)


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def tag_end(img, band, behind, eyelet=True):
    """Turn the left end of a parchment strip into a luggage-tag end: clipped
    corners showing the cork behind, an inked notch and a brass eyelet.
    Stays left of x=8, where live text starts."""
    x, y, w, h = band
    for k in range(3):
        for j in range(3 - k):
            P.put(img, x + k, y + j, behind)
            P.put(img, x + k, y + h - 1 - j, behind)
    for k in range(3):
        P.put(img, x + k, y + 2 - k, INK[2])
        P.put(img, x + k, y + h - 3 + k, INK[2])
    P.vline(img, x, y + 3, y + h - 4, INK[2])
    if eyelet:
        ey = y + h // 2 - 1
        P.sprite(img, x + 2, ey, ['.b.', 'bdB', '.B.'], {'b': BRASS[2], 'd': INK[0], 'B': BRASS[0]})


def paint_background(key, seed=SEED):
    s = geo.skin(key)
    base = C.base_background(key, seed=seed)     # shared base: rim, bands, wells
    img = C.new(s.width, s.height)
    # cork sheet in place of the planks; same rim, bands and well grammar
    cork_fill(img, (1, 1, s.width - 2, s.height - 2), CORK_SHEET, (seed % 16, 3))
    P.ink_outline(img, (0, 0, s.width, s.height), 'ink_1', radius=2, heavy='br')
    P.highlight_edge(img, (0, 0, s.width, s.height), WOOD[4], 'tl', broken=6, seed=seed, inset=1)
    tband, iband = C.bands(key)
    assert tband.tuple() == (3, 2, s.width - 6, 13)

    # title strip = a big blank name tag: tag end with eyelet on the left,
    # curled corner and a drawing pin on the right (all outside x 8..167)
    P.parchment_panel(img, tband.tuple(), seed, outline='ink_2', fibres=True)
    tag_end(img, tband.tuple(), CORK_SHEET[0])
    P.page_curl(img, tband.tuple(), 'br', 4, outline='ink_2', behind=CORK_SHEET[0])
    pin(img, tband.right - 4, tband.y + 2, EMBER, small=True)
    # inventory strip: tag end, drawing pin, a pencil resting at the far right
    P.parchment_panel(img, iband.tuple(), seed + 1, outline=None, fibres=False)
    tag_end(img, iband.tuple(), CORK_SHEET[0], eyelet=iband.h >= 7)
    pin(img, iband.right - 4, iband.y + iband.h // 2 - 1, PLUM, small=True)
    pw, ph = P.sprite_size(rotate_sprite(PENCIL))
    pencil(img, iband.right - 8 - pw, iband.y + (iband.h - ph) // 2, horizontal=True)

    protect = [tband.tuple(), iband.tuple()]
    content = P.merge_holes(s.content_slots)
    player = P.merge_holes(s.player_slots)
    P.stitched_well(img, content, thread='plum_2', protect=protect)
    P.stitched_well(img, player, thread='parch_2', protect=protect)

    # every row of name tags is pinned at both side margins
    for r, slot in enumerate(s.content_slots[::9]):
        cy = slot.clearance.y + 8 + (2 if r % 2 else 0)
        pin(img, 2, cy, TAG_RAMPS[r % 5], small=True)
        pin(img, s.width - 4, cy + (3 if r % 2 else -1), TAG_RAMPS[(r + 2) % 5], small=True)

    geo.finish_background(img, key)
    assert img.size == base.size
    return img


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def cork_panel(img, box, seed):
    x, y, w, h = box
    cork_fill(img, box, CORK_FRAME, (seed % 16, seed % 7))
    P.ink_outline(img, (x - 1, y - 1, w + 2, h + 2), 'ink_1', radius=0)
    P.hline(img, x, x + w - 1, y, WOOD[0])          # recessed under the moulding
    P.vline(img, x, y, y + h - 1, WOOD[0])
    P.hline(img, x + 1, x + w - 1, y + 1, WOOD[1])
    P.vline(img, x + w, y, y + h - 1, WOOD[3])      # lit moulding edge right/bottom
    P.hline(img, x, x + w, y + h, WOOD[3])


ITEM_H = {'badge': 16, 'card': 31, 'pins': 9, 'tagstrip': 17, 'lug': 15,
          'garland': 22, 'bigtag': 27}


def left_items(H):
    """Left panel stack, chosen per board height (not a crop of one design)."""
    items = [('badge', PLUM), ('card', None), ('lug', EMBER), ('pins', None)]
    if H >= 166:
        items.insert(3, ('badge', EMBER))
    if H >= 202:
        items.insert(2, ('badge', SKY))
    if H >= 220:
        items.insert(1, ('tagstrip', None))
    return items


def right_items(H):
    items = [('garland', 0), ('bigtag', PLUM), ('garland', 1)]
    if H >= 166:
        items.append(('lug', SAGE))
    if H >= 184:
        items.append(('garland', 2))
    if H >= 202:
        items.insert(3, ('badge', BERRY))
    if H >= 238:
        items.append(('garland', 3))
    return items


GARLANDS = [
    [(1, PLUM, 0, 12), (9, EMBER, 1, 11), (17, SKY, 2, 12)],
    [(2, EMBER, 2, 11), (11, PLUM, 1, 13), (19, BERRY, 0, 11)],
    [(1, SAGE, 1, 12), (9, PLUM, 2, 11), (17, EMBER, 0, 13)],
    [(3, SKY, 0, 12), (12, BERRY, 1, 11)],
]


def stack(top, bottom, items):
    total = sum(ITEM_H[k] for k, _ in items)
    gap = max(2, (bottom - top - total) // (len(items) + 1))
    y = top + gap
    for n, (kind, arg) in enumerate(items):
        yield n, kind, arg, y
        y += ITEM_H[kind] + gap


def draw_item(img, n, kind, arg, y, x0, x1, seed):
    """Paint one stacked motif across the cork column x0..x1 (inclusive)."""
    cw = x1 - x0 + 1
    if kind == 'badge':
        w = 24 if n % 2 == 0 else 22
        bx = x0 + (cw - w) // 2 + (1 if n % 2 else -1)
        shadowed(img, lambda lay: name_badge(lay, bx, y + 2, w, 13, arg, n))
    elif kind == 'card':
        shadowed(img, lambda lay: (blank_card(lay, x0 + 3, y + 2, 22, 28, seed + n),
                                   pin(lay, x0 + 14, y + 3, BERRY)))
    elif kind == 'lug':
        lx = x0 + 3 + (n % 2) * 2
        shadowed(img, lambda lay: lug_tag(lay, lx, y + 6, 22, 9, arg, (lx + 4, y + 1), seed))
    elif kind == 'tagstrip':
        def strip(lay):
            for k, (dx, ramp_, st) in enumerate(((3, PLUM, 0), (12, SAGE, 1), (21, EMBER, 2))):
                hang_tag(lay, x0 + dx - 1, y + 4 + (k % 2), 7, 12, ramp_, st)
                pin(lay, x0 + dx + 2, y + 2 + (k % 2), BRASS, small=True)
        shadowed(img, strip)
    elif kind == 'pins':
        def spare(lay):
            pin(lay, x0 + 5, y + 3, BERRY)
            pin(lay, x0 + 12, y + 6, SKY)
            pin(lay, x0 + 19, y + 2, PLUM)
            pin(lay, x0 + 25, y + 6, SAGE, small=True)
        shadowed(img, spare)
    elif kind == 'garland':
        g = arg
        garland(img, x0 + 2 - (g % 2), x1 - 3 - (g % 2), y + 4, 3 + (g % 2), GARLANDS[g % 4], seed + g)
    elif kind == 'bigtag':
        def big(lay):
            tx, ty = x0 + 9, y + 7
            P.twine(lay, x0 + 15, y + 2, tx + 5, ty + 2, sag=0)
            hang_tag(lay, tx, ty, 11, 19, arg, 0)
            P.stitch_line(lay, tx + 2, ty + 15, tx + 8, ty + 15, arg[0], 1, 1)
            pin(lay, x0 + 15, y + 2, EMBER)
        shadowed(img, big)


CORK_L = (6, 10, 29)        # x, y, w of the left cork column
CORK_R = (221, 10, 29)


def paint_frame(key, seed=SEED):
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, a.id, seed=seed)       # shared base: beams, rim, corners, ribbon
    H = a.h
    for (x, y, w), sd in ((CORK_L, seed), (CORK_R, seed + 3)):
        cork_panel(img, (x, y, w, H - 20), sd)
    # left: heading tag, then the stack
    lx0, lx1 = CORK_L[0] + 1, CORK_L[0] + CORK_L[2] - 1
    top = heading_tag(img, a.left_panel, a.left_heading or a.heading or 'PREFIXES', 12, seed)
    for n, kind, arg, y in stack(top, H - 12, left_items(H)):
        draw_item(img, n, kind, arg, y, lx0, lx1, seed)
    # right: garlands and tags, the twine running down to a ball on the ledge
    rx0, rx1 = CORK_R[0] + 1, CORK_R[0] + CORK_R[2] - 1
    ball_y = H - 9 - BALL_H
    last = None
    for n, kind, arg, y in stack(10, ball_y - 4, right_items(H)):
        draw_item(img, n, kind, arg, y, rx0, rx1, seed)
        if kind == 'garland':
            last = (rx1 - 3 - (arg % 2), y + 4)
    bx = rx0 + 2

    def run(lay):
        P.twine(lay, last[0] + 1, last[1] + 2, rx1 - 1, last[1] + 6, sag=0)
        P.twine(lay, rx1 - 1, last[1] + 6, rx1 - 2, ball_y - 6, sag=0)
        P.twine(lay, rx1 - 2, ball_y - 6, bx + BALL_W - 4, ball_y + 1, sag=1)
        twine_ball(lay, bx, ball_y)
        pin(lay, rx1 - 3, ball_y + 8, BERRY)
    shadowed(img, run)
    # pencil resting on the bottom ledge of the board, under the sheet
    shadowed(img, lambda lay: pencil(lay, 58, H - 7, horizontal=True))
    # drawing pins in the top beam either side of the heading ribbon
    for px, ramp in ((72, PLUM), (184, EMBER)):
        shadowed(img, lambda lay, px=px, ramp=ramp: pin(lay, px, 3, ramp, small=True))
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--skin', choices=KEYS, action='append')
    ap.add_argument('--out-root', type=Path, help='write DIR/menu/<key>.png and DIR/frames/<key>/<id>.png instead of pack-source')
    a = ap.parse_args(argv)
    for key in a.skin or KEYS:
        s = geo.skin(key)
        bg = paint_background(key)
        fr = paint_frame(key)
        lay = s.layer()
        if a.out_root:
            bp = a.out_root / 'menu' / f'{key}.png'
            fp = a.out_root / 'frames' / key / f'{lay.id}.png'
        else:
            bp, fp = s.background_path, s.frame_path(lay.id)
        C.save_png(bg, bp)
        C.save_png(fr, fp)
        print('WROTE', bp)
        print('WROTE', fp)
    return 0


if __name__ == '__main__':
    sys.exit(main())
