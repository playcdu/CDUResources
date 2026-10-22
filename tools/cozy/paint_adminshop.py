#!/usr/bin/env python3
"""Cozy painter "adminshop": the quartermaster's counter.

    python tools/cozy/paint_adminshop.py                      # all four skins into pack-source
    python tools/cozy/paint_adminshop.py --skin admin_shop_search
    python tools/cozy/paint_adminshop.py --out-root DIR       # DIR laid out like textures/

Paints, deterministically, the background and the 256x238 outer frame of

    admin_shop_categories   drawer cabinet with blank, colour-coded label cards
    admin_shop_listings     crates stacked for sale, straw, a blank hang tag
    admin_shop_search       a magnifying lens over a ruled ledger page, and one on the counter
    admin_shop_configured   a pinned notice closed with a red wax seal

All four are chest_6 screens whose 54 top cells are native (wells only), so the
background carries the family in its brass-trimmed well rails, band ends and
corner studs, while the frame is the quartermaster's counter: keys on a hook
rail, the ADMIN tag, inkwell and open ledger, brass scales, a requisition
clipboard, drying sage, a hanging lantern, a rubber stamp, and a brass-edged
counter top carrying stacked crates and a service bell.

No words other than the frame heading (ADMIN SHOP) and leftHeading (ADMIN).
Every sprite below is original pixel work (CC0-1.0); the script is MIT.
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
import primitives as P  # noqa: E402
from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, PLUM, SAGE, SKY, WOOD  # noqa: E402

SKINS = ('admin_shop_categories', 'admin_shop_listings', 'admin_shop_search', 'admin_shop_configured')
SEEDS = {'admin_shop_categories': 41, 'admin_shop_listings': 42, 'admin_shop_search': 43,
         'admin_shop_configured': 44}
FW = C.FRAME_WOOD           # wall boards behind the counter (one step darker than the sheet)

# One shared sprite key: every character is a palette colour.
K = {
    'O': INK[0], 'o': INK[1], 'i': INK[2],
    'a': WOOD[0], 'b': WOOD[1], 'c': WOOD[2], 'd': WOOD[3], 'e': WOOD[4],
    'p': PARCHMENT[0], 'q': PARCHMENT[1], 'r': PARCHMENT[2], 's': PARCHMENT[3],
    '0': BRASS[0], '1': BRASS[1], '2': BRASS[2], '3': BRASS[3],
    'g': SAGE[0], 'h': SAGE[1], 'j': SAGE[2],
    'x': BERRY[0], 'y': BERRY[1], 'z': BERRY[2],
    'k': SKY[0], 'l': SKY[1], 'm': SKY[2],
    'E': EMBER[0], 'F': EMBER[1], 'G': EMBER[2],
    'A': ASH[0], 'B': ASH[1], 'C': ASH[2],
}
IRON = {'3': ASH[2], '2': ASH[2], '1': ASH[1], '0': ASH[0]}   # remap brass -> iron


def spr(img, x, y, rows, remap=None, flip_x=False):
    """Draw a hand-authored sprite with the shared key (rows must be equal length)."""
    w = len(rows[0])
    assert all(len(r) == w for r in rows), rows
    key = dict(K)
    if remap:
        key.update(remap)
    P.sprite(img, x, y, rows, key, flip_x=flip_x)
    return w, len(rows)


# ---------------------------------------------------------------------------
# Sprites (hand-placed pixels)
# ---------------------------------------------------------------------------

KEY = [
    '.ooo.',
    'o332o',
    'o3o1o',
    'o211o',
    '.o1o.',
    '.o2o.',
    '.o2o.',
    '.o2oo',
    '.o21o',
    '.o2oo',
    '.o21o',
    '.ooo.',
]

HOOK = ['oo', 'o3', 'o1', '.o', 'oo']

BELL = [
    '.....ooo.....',
    '.....o3o.....',
    '....oo1oo....',
    '...o33221o...',
    '..o3322110o..',
    '..o3222110o..',
    '.o322221100o.',
    'o12222221100o',
    'oooooooooooOo',
    'oeddddddddcbo',
    'obbbbbbbbbbao',
    '.oooooooooOO.',
]

INKWELL = [
    '.........s',
    '........sr',
    '.......srq',
    '......srq.',
    '.....srq..',
    '....srq...',
    '....iq....',
    '...i......',
    '..oOo.....',
    '.ooOoo....',
    'oklkkko...',
    'olkkkko...',
    'okkkkOo...',
    '.ooooo....',
]

COINS = [
    '.ooooo.',
    'o33221o',
    'o00000o',
    'o32211o',
    'o00000o',
    'o32211o',
    '.ooooo.',
]

STAMP = [
    '..ooo..',
    '.oedco.',
    '.odcbo.',
    '..oco..',
    '..obo..',
    'ooooooo',
    'o32221o',
    'oyyyyxo',
    'ooooooo',
]

INK_PAD = [
    '.ooooooooo.',
    'o322222210o',
    'o1xxxyxxx0o',
    'o1xyxxxxx0o',
    'o000000000o',
    '.ooooooooo.',
]

SEALING_WAX = [
    '......F',
    '.....oG',
    '....oyo',
    '...oyx.',
    '..ozyo.',
    '.ozyo..',
    'oyyo...',
    'oxo....',
    '.o.....',
]

PAN = ['o2222o', '.o110o', '..oo..']

SAGE_BUNDLE = [
    '..oqo..',
    '..pqp..',
    '..hgh..',
    '.jhghj.',
    'jhjgjhj',
    'hj.g.jh',
    'g.jhj.g',
    '..h.h..',
    '..g.g..',
]

TINY_CRATE = [
    'ooooooo',
    'odddddo',
    'oaoboao',
    'ocboaco',
    'oaoboao',
    'ooooooo',
]

TINY_INDEX = [          # a ruled index card with a berry tab (not the search-button lens)
    '.....ooo',
    'oooooyzo',
    'osssssso',
    'ommmmmmo',
    'orrrrrro',
    'ommmmmmo',
    'oooooooo',
]

TINY_LABEL = [          # a little drawer front: blank card, brass pull
    'ooooooooo',
    'oeeeeeedo',
    'od1sss1co',
    'od11111co',
    'oddd3ddco',
    'ooooooooo',
]

TINY_SEAL = [
    '.oyo.',
    'oyzyo',
    'yzyyx',
    'oyyxo',
    '.oxo.',
]


# ---------------------------------------------------------------------------
# Procedural-by-hand helpers (explicit coordinates, no noise)
# ---------------------------------------------------------------------------

def shelf(img, x, y, w, seed):
    """Short plank shelf on two brass brackets."""
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def crate(img, x, y, w, h, seed, open_top=False):
    """Slatted crate: ink rim, wood_2 slats with wood_0 seams, lighter corner
    posts, one diagonal brace and brass nail heads."""
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=0, heavy='br', fill_colour=WOOD[2])
    for yy in range(y + 1, y + h - 1):
        if (yy - y) % 4 == 0:
            P.hline(img, x + 1, x + w - 2, yy, WOOD[0])
        elif (yy - y) % 4 == 1:
            P.hline(img, x + 1, x + w - 2, yy, WOOD[3])
    for px in (x + 1, x + w - 3):
        P.vline(img, px, y + 1, y + h - 2, WOOD[3])
        P.vline(img, px + 1, y + 1, y + h - 2, WOOD[1])
    P.vline(img, x + 1, y + 1, y + h - 2, WOOD[4])
    # diagonal brace bottom-left to top-right between the posts
    pts = P.line_points(x + 3, y + h - 2, x + w - 4, y + 1)
    for (px, py) in pts:
        P.put(img, px, py, WOOD[3])
        P.put(img, px, py + 1, WOOD[1]) if py + 1 < y + h - 1 else None
    for (nx, ny) in ((x + 1, y + 2), (x + w - 3, y + 2), (x + 1, y + h - 3), (x + w - 3, y + h - 3)):
        P.put(img, nx, ny, BRASS[2])
    if open_top:
        # straw spilling over the rim (brass and parchment wisps)
        straw = ['..3.....2..3.....',
                 '.3.2...23.3.2..3.',
                 '2.32.2.3223.2.32.',
                 '22323q22323232q22']
        for j, row in enumerate(straw):
            for i, ch in enumerate(row[:w - 2]):
                if ch != '.':
                    P.put(img, x + 1 + i, y - 3 + j, K[ch])
        P.hline(img, x + 1, x + w - 2, y + 1, WOOD[1])


def cast_shadow(img, c, ramp_dark):
    """The sheet's 2 px cast shadow right of and below the container."""
    for k in (0, 1):
        P.vline(img, c.right + k, c.y + 2 + k, c.bottom - 1 + k, INK[1] if k == 0 else ramp_dark)
        P.hline(img, c.x + 2 + k, c.right + k, c.bottom + k, INK[1] if k == 0 else ramp_dark)


def counter(img, a, top, seed):
    """Brass-edged counter top across the bottom of both side panels and the
    bottom strip: horizontal oiled planks, a back rail against the wall, a
    three-row brass edge with rivets, the counter front below it."""
    c = a.container
    W, H = a.w, a.h
    # counter surface (lighter oiled wood than the wall boards)
    for (x0, x1) in ((1, c.x - 1), (c.right, W - 2)):
        P.planks(img, (x0, top, x1 - x0 + 1, H - 1 - top), WOOD, (seed, x0), board=7, seams=WOOD[0], grain=0.7)
    P.planks(img, (c.x, c.bottom, c.w, H - 1 - c.bottom), WOOD, (seed, 'mid'), board=7, seams=WOOD[0], grain=0.7)
    # back rail where the counter meets the wall
    for (x0, x1) in ((1, c.x - 1), (c.right, W - 2)):
        P.hline(img, x0, x1, top - 2, INK[1])
        P.hline(img, x0, x1, top - 1, WOOD[1])
        P.hline(img, x0, x1, top, WOOD[4])
        P.hline(img, x0, x1, top + 1, WOOD[3])
    # brass edge: lit row, body with rivets, shadow row; then the front
    ey = H - 6
    P.hline(img, 1, W - 2, ey - 1, INK[1])
    P.hline(img, 1, W - 2, ey, BRASS[3])
    P.hline(img, 1, W - 2, ey + 1, BRASS[1])
    P.hline(img, 1, W - 2, ey + 2, BRASS[0])
    for rx in range(9, W - 8, 16):
        P.put(img, rx, ey + 1, BRASS[3])
        P.put(img, rx + 1, ey + 1, BRASS[2])
        P.put(img, rx + 1, ey + 2, INK[1])
    for gx in (30, 31, 32, 120, 121, 200, 201, 202, 203):
        P.put(img, gx, ey, BRASS[2])            # worn glints on the lit edge
    P.hline(img, 1, W - 2, ey + 3, WOOD[1])
    P.hline(img, 1, W - 2, ey + 4, WOOD[0])
    for gx in range(6, W - 6, 11):
        P.put(img, gx, ey + 3, WOOD[2]); P.put(img, gx + 1, ey + 3, WOOD[2])
    cast_shadow(img, c, WOOD[0])


def keys_rail(img, x, y, w, seed):
    """A wall batten with three brass hooks; brass and iron keys hang from two."""
    P.plank(img, (x, y, w, 4), WOOD, seed, 'ink_1', radius=1, grain=0.0)
    P.put(img, x + 2, y + 1, BRASS[2]); P.put(img, x + w - 3, y + 1, BRASS[2])   # screws
    hooks = (x + 5, x + w // 2 - 1, x + w - 8)
    for hx in hooks:
        spr(img, hx, y + 3, HOOK)
    spr(img, hooks[0] - 2, y + 7, KEY)
    spr(img, hooks[2] - 2, y + 7, KEY, remap=IRON)
    spr(img, hooks[2] + 2, y + 8, KEY[:8] + ['.o2o.', '.ooo.'])        # a short spare key on the same hook
    return hooks


def open_ledger(img, x, y, seed):
    """Open account ledger, 23x12: two ruled pages (no writing), stitched spine,
    berry cover showing at the foot, a ribbon marker."""
    w, h = 23, 11
    mid = x + w // 2
    P.ink_outline(img, (x, y + 2, w, h - 2), 'ink_1', radius=1, heavy='b', fill_colour=BERRY[0])
    for side in (0, 1):
        px0 = x + 1 if side == 0 else mid + 1
        px1 = mid - 1 if side == 0 else x + w - 2
        P.fill(img, (px0, y + 1, px1 - px0 + 1, h - 3), PARCHMENT[2])
        P.hline(img, px0 + (1 if side == 0 else 0), px1 - (0 if side == 0 else 1), y, INK[1])
        P.put(img, px0 if side == 0 else px1, y + 1, INK[1])
        P.hline(img, px0, px1, y + 1, PARCHMENT[3])
        for k, ry in enumerate((y + 3, y + 5, y + 7)):
            P.hline(img, px0 + 1, px1 - 1 - (k * 2 if side == 0 else 0), ry, SKY[2])
        P.vline(img, px0 + 2 if side == 0 else px0 + 1, y + 2, y + 7, BERRY[2])   # margin rule
    P.vline(img, mid, y + 1, y + h - 2, PARCHMENT[0])
    P.put(img, mid, y, INK[1])
    P.hline(img, x + 1, x + w - 2, y + h - 2, PARCHMENT[1])
    # ribbon marker hanging over the foot
    P.vline(img, mid + 4, y + h - 2, y + h + 1, BERRY[1])
    P.put(img, mid + 5, y + h + 1, BERRY[0]); P.put(img, mid + 3, y + h + 1, BERRY[0])


def balance_scale(img, cx, y, seed):
    """Brass merchant's scales, 21x18, standing on a foot; coins in one pan."""
    # pillar and finial
    spr(img, cx - 1, y, ['.o.', 'o3o', '.o.'])
    P.vline(img, cx - 1, y + 3, y + 14, INK[1]); P.vline(img, cx + 1, y + 3, y + 14, INK[1])
    P.vline(img, cx, y + 3, y + 14, BRASS[2])
    # beam (tilted by one pixel: the coin side is heavier)
    P.hline(img, cx - 10, cx + 10, y + 3, INK[1])
    P.hline(img, cx - 9, cx - 1, y + 4, BRASS[2]); P.hline(img, cx + 1, cx + 9, y + 4, BRASS[1])
    P.hline(img, cx - 10, cx + 10, y + 5, INK[1])
    P.put(img, cx - 10, y + 4, INK[1]); P.put(img, cx + 10, y + 4, INK[1])
    P.put(img, cx - 6, y + 4, BRASS[3])
    spr(img, cx - 1, y + 2, ['o2o', 'o3o', 'o1o', 'ooo'])                   # pivot boss
    # cords
    for (bx, drop) in ((cx - 9, 10), (cx + 9, 9)):
        P.line(img, bx, y + 6, bx - 3, y + 6 + drop, PARCHMENT[0])
        P.line(img, bx, y + 6, bx + 2, y + 6 + drop, PARCHMENT[0])
    spr(img, cx - 13, y + 16, PAN)
    spr(img, cx + 6, y + 15, PAN)
    # coins resting in the left pan
    spr(img, cx - 12, y + 14, ['.ooo.', 'o332o'])
    # foot
    spr(img, cx - 4, y + 15, ['..ooooo..', '.o32221o.', 'o2222110o', 'ooooooooo'])


def clipboard(img, x, y, w, h, seed):
    """Requisition clipboard: oiled board, brass clip, ruled sheet, a stamp ring."""
    P.plank(img, (x, y, w, h), WOOD, seed, 'ink_1', radius=1, grain=0.6)
    sx, sy, sw, sh = x + 2, y + 4, w - 4, h - 6
    P.parchment_panel(img, (sx, sy, sw, sh), seed, outline='ink_2', fibres=True)
    for k, ry in enumerate(range(sy + 6, sy + sh - 3, 3)):
        P.hline(img, sx + 3, sx + sw - 4 - (4 if k % 3 == 2 else 0), ry, SKY[2])
        P.put(img, sx + 2, ry, PARCHMENT[0])                      # tick boxes, left empty
    P.vline(img, sx + 6, sy + 5, sy + sh - 3, BERRY[2])          # margin rule
    # inked stamp ring, no words
    cx, cy = sx + sw - 7, sy + sh - 8
    for (dx, dy) in ((-1, -3), (0, -3), (1, -3), (2, -2), (3, -1), (3, 0), (3, 1), (2, 2), (1, 3), (0, 3),
                     (-1, 3), (-2, 2), (-3, 1), (-3, 0), (-3, -1), (-2, -2)):
        P.put(img, cx + dx, cy + dy, BERRY[1])
    P.put(img, cx, cy, BERRY[1]); P.put(img, cx - 1, cy, BERRY[1]); P.put(img, cx + 1, cy, BERRY[1])
    P.put(img, cx, cy - 1, BERRY[1]); P.put(img, cx, cy + 1, BERRY[1])
    # brass clip
    P.brass_plate(img, (x + w // 2 - 6, y - 1, 12, 6), rivets=False)
    P.hline(img, x + w // 2 - 3, x + w // 2 + 2, y + 2, BRASS[0])


def lens(img, cx, cy, r, handle_len=8, inner=None):
    """Magnifying glass: brass ring, sky glass with a parch_3 glint, oiled
    wood handle to the lower right. ``inner(px, py)`` may return a colour to
    show something magnified through the glass."""
    r2o, r2i = (r + 1) ** 2 + r, r * r + r
    # handle first (the ring overlaps its root)
    hx, hy = cx + int(r * 0.7), cy + int(r * 0.7)
    for t in range(handle_len):
        px, py = hx + t, hy + t
        P.put(img, px, py, BRASS[1] if t < 3 else WOOD[3])
        P.put(img, px + 1, py, BRASS[0] if t < 3 else WOOD[1])
        P.put(img, px, py + 1, INK[1] if t else BRASS[0]); P.put(img, px + 1, py + 1, BRASS[0] if t < 3 else WOOD[2])
        P.put(img, px - 1, py, INK[1]); P.put(img, px + 2, py, INK[1]); P.put(img, px + 2, py + 1, INK[1])
        P.put(img, px - 1, py + 1, INK[1]) if t else None
    end = hx + handle_len
    P.put(img, end, end - hx + hy, INK[1]); P.put(img, end + 1, end - hx + hy, INK[0])
    P.put(img, end, end - hx + hy + 1, INK[0])
    import math
    for py in range(cy - r - 2, cy + r + 3):
        for px in range(cx - r - 2, cx + r + 3):
            dist = math.hypot(px - cx, py - cy)
            lit = (px - cx) + (py - cy) < 0
            if dist >= r + 1.5:
                continue
            if dist >= r + 0.5:                         # ink rim, heavier lower right
                P.put(img, px, py, INK[1] if lit else INK[0])
            elif dist >= r - 0.5:                       # outer brass band
                P.put(img, px, py, BRASS[2] if lit else BRASS[0])
            elif dist >= r - 1.5:                       # inner brass band
                P.put(img, px, py, BRASS[3] if (px - cx) + (py - cy) < -r else BRASS[1])
            elif dist >= r - 2.5:                       # glass edge catches the sky
                P.put(img, px, py, SKY[2] if lit else SKY[1])
            else:
                col = inner(px, py) if inner else None
                if col is None:
                    col = SKY[2] if (px - cx) + (py - cy) < r - 2 else SKY[1]
                P.put(img, px, py, col)
    # glint: a short bright arc just inside the top-left of the glass
    for (dx, dy) in ((-r + 3, -2), (-r + 3, -3), (-r + 4, -4), (-3, -r + 3), (-2, -r + 3)):
        P.put(img, cx + dx, cy + dy, PARCHMENT[3])


def hanging_bundle(img, x, y):
    """Drying sage tied with twine, hung from a brass nail."""
    P.put(img, x + 3, y - 2, BRASS[3]); P.put(img, x + 3, y - 1, BRASS[0])
    spr(img, x, y, SAGE_BUNDLE)
    P.leaf(img, x - 3, y + 5, 'sw', small=True)
    P.leaf(img, x + 6, y + 5, 'se', small=True)


def rope_coil(img, x, y):
    """A coil of rope hung on a wooden peg: two overlapping twisted loops."""
    import math
    spr(img, x + 6, y - 3, ['oooo', 'oedo', 'obbo', 'oooo'])         # peg
    for (ox, oy) in ((x, y), (x + 3, y + 2)):
        rx, ry = 8, 11
        cx, cy = ox + rx, oy + ry
        pts = []
        for k in range(160):
            a = 2 * math.pi * k / 160
            p = (round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a)))
            if not pts or pts[-1] != p:
                pts.append(p)
        for (px, py) in pts:          # 3 px band: ink rims round a twisted core
            for (dx, dy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if P.get(img, px + dx, py + dy)[:3] not in (WOOD[4], WOOD[1]):
                    P.put(img, px + dx, py + dy, INK[1])
        for i, (px, py) in enumerate(pts):
            P.put(img, px, py, WOOD[4] if (i // 2) % 2 else WOOD[2])
    # binding wrapped round the top of the coil
    for yy in range(y - 1, y + 4):
        P.hline(img, x + 9, x + 12, yy, PARCHMENT[1] if yy % 2 else PARCHMENT[0])
    P.vline(img, x + 8, y - 1, y + 3, INK[1]); P.vline(img, x + 13, y - 1, y + 3, INK[1])


def vine(img, x, y0, y1, seed, side=1):
    """A trailing vine with leaves alternating sides."""
    P.ink_line(img, x, y0, x + side, y1, SAGE[0], wobble=1, seed=seed)
    k = 0
    for yy in range(y0 + 3, y1 - 3, 9):
        if k % 2:
            P.leaf(img, x + 1, yy, 'ne', small=(k % 3 == 2))
        else:
            P.leaf(img, x - (4 if k % 3 == 2 else 6), yy, 'nw', small=(k % 3 == 2))
        k += 1


# ---------------------------------------------------------------------------
# Per-screen feature art (right panel, y 32 .. 112)
# ---------------------------------------------------------------------------

def feature_categories(img, rp, seed):
    """A chest of small drawers: blank linen label cards in brass holders,
    each with a dyed corner (colour-coded, wordless) and a brass pull."""
    x, y, w, h = rp.x + 3, 34, rp.w - 5, 74
    P.plank(img, (x, y, w, h), WOOD, seed, 'ink_1', radius=1, grain=0.0)
    # top board overhang
    P.plank(img, (x - 1, y - 4, w + 2, 5), WOOD, seed + 1, 'ink_1', radius=1, grain=0.4)
    dyes = [SAGE, BERRY, SKY, EMBER, PLUM, SAGE, BRASS, BERRY]
    dw, dh = (w - 5) // 2, 16
    k = 0
    for row in range(4):
        for col in range(2):
            dx = x + 2 + col * (dw + 1)
            dy = y + 2 + row * (dh + 1)
            P.ink_outline(img, (dx, dy, dw, dh), 'ink_1', radius=0, heavy='br', fill_colour=WOOD[3])
            P.hline(img, dx + 1, dx + dw - 2, dy + 1, WOOD[4])
            P.hline(img, dx + 1, dx + dw - 2, dy + dh - 2, WOOD[2])
            P.vline(img, dx + dw - 2, dy + 2, dy + dh - 2, WOOD[2])
            # label holder: brass frame, blank card, dyed corner
            lx, ly = dx + dw // 2 - 5, dy + 3
            P.ink_outline(img, (lx, ly, 10, 6), 'ink_1', radius=0, fill_colour=BRASS[1])
            P.fill(img, (lx + 2, ly + 1, 6, 4), PARCHMENT[3])
            P.hline(img, lx + 2, lx + 7, ly + 4, PARCHMENT[1])
            d = dyes[k % len(dyes)]
            P.put(img, lx + 7, ly + 1, d[1]); P.put(img, lx + 6, ly + 1, d[1]); P.put(img, lx + 7, ly + 2, d[0])
            P.put(img, lx + 1, ly + 1, BRASS[3])
            # pull knob
            spr(img, dx + dw // 2 - 2, dy + 10, ['.oo.', 'o32o', 'o10o', '.oo.'])
            k += 1
    P.hline(img, x + 1, x + w - 2, y + h - 2, WOOD[0])
    # feet
    spr(img, x + 1, y + h, ['oooo', '.oo.'])
    spr(img, x + w - 5, y + h, ['oooo', '.oo.'])


def feature_listings(img, rp, seed):
    """Crates stacked for sale: an open crate of straw with a blank hang tag."""
    x = rp.x + 3
    crate(img, x + 1, 92, 17, 15, seed)
    crate(img, x + 18, 92, 15, 15, seed + 1)
    crate(img, x + 6, 77, 16, 15, seed + 2)
    crate(img, x + 4, 60, 18, 17, seed + 3, open_top=True)
    # blank linen hang tag on twine from the open crate's corner
    P.twine(img, x + 21, 62, x + 27, 69, sag=1)
    P.linen_tag(img, (x + 24, 69, 9, 13), eyelet='top', seed=seed)
    # lantern-lit shelf sign above: plain brass plate, no words
    P.brass_plate(img, (x + 2, 36, 30, 10), rivets=True)
    P.twine(img, x + 5, 36, x + 16, 30, sag=0); P.twine(img, x + 16, 30, x + 28, 36, sag=0)
    P.put(img, x + 16, 29, BRASS[3])
    # engraved crate emblem on the plate (a picture, not words)
    spr(img, x + 12, 37, [
        '00000000000',
        '01333333310',
        '00000000000',
        '01111113010',
        '01111301110',
        '01113011110',
        '01301111110',
        '00000000000',
    ])
    for kx in (x + 7, x + 27):
        P.put(img, kx, 41, BRASS[0]); P.put(img, kx - 1, 41, BRASS[0])


def feature_search(img, rp, seed):
    """A ruled ledger page pinned to the wall with a lens hanging over it; the
    ruled lines swell inside the glass."""
    x, y, w, h = rp.x + 4, 40, rp.w - 8, 62
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=True)
    lines = list(range(y + 6, y + h - 4, 4))
    for ry in lines:
        P.hline(img, x + 3, x + w - 4, ry, SKY[2])
    P.vline(img, x + 6, y + 3, y + h - 3, BERRY[2])
    P.tack(img, x + 3, y + 2, small=True)
    P.tack(img, x + w - 4, y + 2, small=True)
    P.page_curl(img, (x, y, w, h), 'br', 5, behind=FW[1])
    cx, cy, r = x + w // 2 - 1, y + 24, 8

    def magnified(px, py):
        # the page seen through the glass: two ruled lines swell to 2 px and
        # the paper brightens
        if py - cy in (-3, -2, 3, 4):
            return SKY[1]
        return PARCHMENT[3]

    lens(img, cx, cy, r, handle_len=7, inner=magnified)


def feature_configured(img, rp, seed):
    """A pinned notice: ruled lines, a curled corner, closed with a wax seal
    pressed with a check, its ribbon tails hanging below."""
    x, y, w, h = rp.x + 4, 38, rp.w - 8, 62
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=True)
    # a dyed sage header bar (no words) and ruled lines
    P.fill(img, (x + 3, y + 4, w - 6, 3), SAGE[2])
    P.hline(img, x + 3, x + w - 4, y + 7, SAGE[1])
    for ry in range(y + 11, y + h - 18, 4):      # plain ruling, never pseudo-writing
        P.hline(img, x + 3, x + w - 4, ry, SKY[2])
    P.page_curl(img, (x, y, w, h), 'bl', 5, behind=FW[1])
    P.tack(img, x + w // 2, y + 1)
    # ribbon tails under the seal
    sx, sy = x + w - 10, y + h - 10
    for t in range(6):
        P.put(img, sx - 2 - t // 2, sy + 4 + t, BERRY[1]); P.put(img, sx - 1 - t // 2, sy + 4 + t, BERRY[0])
        P.put(img, sx + 2 + t // 2, sy + 4 + t, BERRY[1]); P.put(img, sx + 3 + t // 2, sy + 4 + t, BERRY[0])
    P.put(img, sx - 5, sy + 10, INK[1]); P.put(img, sx + 6, sy + 10, INK[1])
    P.wax_seal(img, sx, sy, 6, BERRY, seed, drip=False, emblem='check')


FEATURES = {
    'admin_shop_categories': feature_categories,
    'admin_shop_listings': feature_listings,
    'admin_shop_search': feature_search,
    'admin_shop_configured': feature_configured,
}


def counter_extra(img, key, x, top, seed):
    """Small per-screen object on the right of the counter."""
    if key == 'admin_shop_search':
        lens(img, x + 6, top + 9, 4, handle_len=6)
    elif key == 'admin_shop_listings':
        crate(img, x, top + 4, 13, 11, seed + 9)
    elif key == 'admin_shop_categories':
        # a stack of blank label cards tied with twine
        for k in range(3):
            P.ink_outline(img, (x + k, top + 8 - k * 2, 12, 5), 'ink_2', radius=0,
                          fill_colour=PARCHMENT[3] if k == 2 else PARCHMENT[2])
        P.vline(img, x + 7, top + 4, top + 12, PARCHMENT[0])
        P.put(img, x + 3, top + 13, SAGE[1]); P.put(img, x + 4, top + 13, BERRY[1])
    else:
        spr(img, x + 2, top + 5, SEALING_WAX)
        spr(img, x + 8, top + 8, ['.ooo.', 'oyzyo', 'oyyxo', '.ooo.'])   # a spare dab of wax


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def paint_frame(key):
    seed = SEEDS[key]
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    top = 200                                     # counter top meets the wall here

    # --- counter (bottom of both panels + bottom strip) ---------------------
    counter(img, a, top, seed)

    # --- left panel ----------------------------------------------------------
    hooks = keys_rail(img, lp.x + 4, 10, lp.w - 8, seed)
    C.side_tag(img, lp, a.left_heading or 'ADMIN', 31, seed, twine_from=(hooks[1] + 1, 17))
    spr(img, hooks[1], 17, ['oo'])
    P.put(img, hooks[1] + 1, 17, BRASS[1])
    # shelf: open ledger and inkwell
    shelf(img, lp.x + 3, 64, lp.w - 6, seed + 1)
    open_ledger(img, lp.x + 4, 53, seed)
    spr(img, lp.x + 27, 50, INKWELL)
    # brass scales on their own shelf
    shelf(img, lp.x + 3, 100, lp.w - 6, seed + 2)
    balance_scale(img, lp.x + 19, 81, seed)
    # requisition clipboard on a nail
    P.put(img, lp.x + 19, 110, BRASS[3]); P.put(img, lp.x + 19, 111, BRASS[0])
    P.twine(img, lp.x + 19, 112, lp.x + 13, 117, sag=0); P.twine(img, lp.x + 19, 112, lp.x + 25, 117, sag=0)
    clipboard(img, lp.x + 7, 118, 25, 36, seed)
    # drying sage and a trailing vine down to the counter
    rope_coil(img, lp.x + 13, 160)
    vine(img, lp.x + 31, 158, 194, seed, side=-1)
    # stacked crates on the counter
    crate(img, lp.x + 3, 213, 15, 13, seed + 4)
    crate(img, lp.x + 19, 214, 15, 12, seed + 5)
    crate(img, lp.x + 9, 199, 16, 14, seed + 6)
    spr(img, lp.x + 27, 205, COINS)

    # --- right panel ---------------------------------------------------------
    # hanging lantern, glow pooled by dither
    P.vline(img, rp.x + 20, 8, 13, INK[1])
    P.put(img, rp.x + 20, 9, BRASS[2])
    P.lantern(img, rp.x + 17, 14)
    FEATURES[key](img, rp, seed)
    # shelf: rubber stamp, ink pad, coins
    shelf(img, rp.x + 3, 126, rp.w - 6, seed + 3)
    spr(img, rp.x + 5, 117, STAMP)
    spr(img, rp.x + 13, 120, INK_PAD)
    spr(img, rp.x + 26, 119, COINS)
    # sage bundle and vine
    hanging_bundle(img, rp.x + 6, 146)
    P.rope(img, rp.x + 4, 140, rp.w + rp.x - 6, 140, sag=2)
    P.tack(img, rp.x + 4, 139); P.tack(img, rp.w + rp.x - 6, 139)
    vine(img, rp.x + 30, 143, 194, seed + 1, side=1)
    # service bell and the per-screen counter object
    spr(img, rp.x + 22, 210, BELL)
    counter_extra(img, key, rp.x + 5, 207, seed)
    P.lantern_glow_ring(img, rp.x + 21, 19, 11, strength=1)

    # --- finishing -----------------------------------------------------------
    P.highlight_edge(img, (lp.x + 1, 9, lp.w - 2, top - 12), FW[2], 'l', broken=4, seed=seed)
    for corner, (x, y) in (('tl', (2, 2)), ('tr', (a.w - 8, 2)), ('bl', (2, H - 8)), ('br', (a.w - 8, H - 8))):
        C.brass_corner(img, x, y, corner)
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def brass_rail(img, holes, protect):
    """Replace the d3 ring of the well frame with a brass rail: lit on the
    top/left, shaded on the bottom/right, a brass_3 rivet at every cell
    boundary. Only outside the text bands; never inside a hole."""
    W, H = img.size
    hole = set()
    for (x, y, w, h) in holes:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                hole.add((xx, yy))

    def is_hole(px, py):
        return (px, py) in hole

    def prot(px, py):
        return any(x <= px < x + w and y <= py < y + h for (x, y, w, h) in protect)

    for (x, y, w, h) in holes:
        for py in range(y - 3, y + h + 3):
            for px in range(x - 3, x + w + 3):
                if not (0 <= px < W and 0 <= py < H) or is_hole(px, py) or prot(px, py):
                    continue
                near = [(dx, dy) for dx in range(-3, 4) for dy in range(-3, 4) if is_hole(px + dx, py + dy)]
                if not near or min(max(abs(dx), abs(dy)) for dx, dy in near) != 3:
                    continue
                below_right = any(dx >= 0 and dy >= 0 for dx, dy in near)
                above_left = any(dx <= 0 and dy <= 0 for dx, dy in near)
                if below_right and not above_left:
                    col = BRASS[2]            # rail above / left of the grid: lit
                elif above_left and not below_right:
                    col = BRASS[1]            # below / right: shaded
                else:
                    col = BRASS[1]
                P.put(img, px, py, col)
    return img


def rail_rivets(img, s, holes, protect):
    """Brass_3 studs on the rail at every 18-px cell boundary."""
    def prot(px, py):
        return any(x <= px < x + w and y <= py < y + h for (x, y, w, h) in protect)
    for (x, y, w, h) in holes:
        cols = range(x + 1, x + w, 18)
        for cx in cols:
            for ry in (y - 3, y + h + 2):
                if not prot(cx, ry):
                    P.put(img, cx, ry, BRASS[3])
        for ry in range(y + 1, y + h, 18):
            for rx in (x - 3, x + w + 2):
                if not prot(rx, ry):
                    P.put(img, rx, ry, BRASS[3])


BAND_MOTIF = {
    'admin_shop_categories': TINY_LABEL,
    'admin_shop_listings': TINY_CRATE,
    'admin_shop_search': TINY_INDEX,
    'admin_shop_configured': TINY_SEAL,
}


def paint_background(key):
    seed = SEEDS[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed, wells='stitched')
    tband, iband = C.bands(key)
    protect = [tband.tuple(), iband.tuple()]
    holes = P.merge_holes(s.content_slots) + P.merge_holes(s.player_slots)
    brass_rail(img, holes, protect)
    rail_rivets(img, s, holes, protect)
    # brass studs at the outer grid corners only (calm, symmetric spacing)
    for (x, y, w, h) in holes:
        for (px, py) in ((x - 3, y - 3), (x + w + 2, y - 3), (x - 3, y + h + 2), (x + w + 2, y + h + 2)):
            if not any(bx <= px < bx + bw and by <= py < by + bh for (bx, by, bw, bh) in protect):
                P.put(img, px, py, BRASS[3])
    # title band: brass corner caps instead of plain tacks
    for (cx, flip) in ((tband.x, False), (tband.right - 3, True)):
        spr(img, cx, tband.y, ['ooo', 'o3o', 'oo.'] if not flip else ['ooo', 'o3o', '.oo'])
        spr(img, cx, tband.bottom - 3, ['oo.', 'o1o', 'ooo'] if not flip else ['.oo', 'o1o', 'ooo'])
    # inventory band: a brass clasp at each end, and the screen's small mark at the right
    for bx in (iband.x, iband.right - 2):
        P.vline(img, bx, iband.y, iband.bottom - 1, BRASS[1])
        P.vline(img, bx + 1, iband.y, iband.bottom - 1, BRASS[2] if bx == iband.x else BRASS[0])
        P.put(img, bx, iband.y + iband.h // 2, BRASS[3])
    m = BAND_MOTIF[key]
    mw, mh = len(m[0]), len(m)
    spr(img, iband.right - 6 - mw, iband.y + (iband.h - mh) // 2, m)
    # little sprig beside the mark, light sage only
    P.leaf(img, iband.right - 12 - mw, iband.y + 3, 'nw', small=True)
    # bottom corners: brass tacks and a little wear on the board
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    geo.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------

def out_paths(key, out_root):
    s = geo.skin(key)
    bg, fr = s.background_path, s.frame_path()
    if out_root is None:
        return bg, fr
    root = Path(out_root)
    return root / bg.relative_to(geo.TEXTURES), root / fr.relative_to(geo.TEXTURES)


def paint(key, out_root=None):
    bg_path, fr_path = out_paths(key, out_root)
    s = geo.skin(key)
    bg = paint_background(key)
    assert bg.size == (s.width, s.height) and bg.mode == 'RGBA'
    C.save_png(bg, bg_path)
    fr = paint_frame(key)
    a = s.layer()
    assert fr.size == (a.w, a.h) and fr.mode == 'RGBA'
    C.save_png(fr, fr_path)
    print(f'WROTE {bg_path}')
    print(f'WROTE {fr_path}')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', type=Path, help='write into DIR laid out like textures/ instead of pack-source')
    a = ap.parse_args(argv)
    for key in (a.skin or SKINS):
        paint(key, a.out_root)
    return 0


if __name__ == '__main__':
    sys.exit(main())
