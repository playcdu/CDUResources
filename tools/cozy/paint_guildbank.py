#!/usr/bin/env python3
"""Cozy painter "guildbank": the guild bank family.

    python tools/cozy/paint_guildbank.py                 # all eight skins into pack-source
    python tools/cozy/paint_guildbank.py --skin guild_bank_3
    python tools/cozy/paint_guildbank.py --out-root DIR  # DIR laid out like textures/

Skins: guild_bank_select_1, guild_bank_select_3 (choose a vault) and
guild_bank_1 .. guild_bank_6 (vault contents). Every top cell is a native
well, so each background is the shared stitched-well sheet with an
iron-banded strongbox treatment: riveted iron straps run down both sides of
the vault grid, riveted iron corner brackets clamp the sheet, and the
player's own inventory keeps the cloth stitching. A small brass key (choose a
vault) or an open padlock (vault open) is pressed at the right end of the
inventory band, clear of the live label.

Frames (256 wide, container height + 16): a riveted iron strap along both
beams, the GUILD tag, a wordless sage guild banner with an embroidered
parchment shield bearing an iron key, and an iron-banded strongbox with a
candle and coins. Vault screens hang a lantern, a coin-and-ledger shelf and,
when there is height, a pennant garland and an inkwell shelf; the selection
screens hang a key ring and a rack of small locked vault doors. Panel
compositions are laid out per height, not cropped.

Deterministic: fixed seeds, no clock. Licence: code MIT; artwork CC0-1.0.
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
import icons  # noqa: E402
import primitives as P  # noqa: E402
from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD  # noqa: E402

SELECT = ('guild_bank_select_1', 'guild_bank_select_3')
VAULTS = tuple(f'guild_bank_{n}' for n in range(1, 7))
SKINS = SELECT + VAULTS
SEED = 53

IRON = ASH  # ash_0 shadow, ash_1 body, ash_2 lit edge


# ---------------------------------------------------------------------------
# Small hand-authored sprites
# ---------------------------------------------------------------------------

# Open padlock (vault open): iron shackle lifted out on the right, brass body.
PADLOCK_OPEN = [
    '.sss...',
    's...s..',
    's......',
    'ooooooo',
    'o3222o.',
    'o22k1o.',
    'o11k1o.',
    '.oooo..',
]
# Closed padlock (hanging on a nail in the selection frames).
PADLOCK_SHUT = [
    '..sss...',
    '.s...s..',
    '.s...s..',
    '.s...s..',
    'oooooooo',
    'o332222o',
    'o22oo21o',
    'o221o21o',
    'o111111o',
    '.oooooo.',
]
K_PADLOCK = {'s': ASH[0], 'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[0], 'k': INK[0]}

# Small brass key lying on the inventory band (choose a vault).
KEY_FLAT = [
    '.ooo........',
    'o332oooooooo',
    'o2.122222221o',
    'o221ooooo1o1o',
    '.ooo.....o.o.',
]
K_KEY = {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[0]}

# Hanging keys for the key ring (bow at the top).
KEY_HANG_LONG = [
    '.ooo.',
    'o323o',
    'o2.1o',
    'o211o',
    '.o2o.',
    '.o2o.',
    '.o2o.',
    '.o2oo',
    '.o21o',
    '.o2oo',
    '.o21o',
    '.ooo.',
]
KEY_HANG_SHORT = [
    '.ooo.',
    'o323o',
    'o2.1o',
    '.o1o.',
    '.o2o.',
    '.o2oo',
    '.o21o',
    '.oooo',
]
K_IRON_KEY = {'o': INK[1], '3': PARCHMENT[3], '2': ASH[2], '1': ASH[0]}

KEY_RING = [
    '...ooooo...',
    '..o22221o..',
    '.o2ooooo1o.',
    'o2o.....o1o',
    'o2o.....o0o',
    'o2o.....o0o',
    'o1o.....o0o',
    '.o1ooooo0o.',
    '..o10000o..',
    '...ooooo...',
]
K_RING = {'o': INK[1], '2': ASH[2], '1': ASH[1], '0': ASH[0]}

# Embroidered parchment shield bearing an iron key (banner emblem), 11x13.
SHIELD = [
    'bbbbbbbbbbb',
    'bPPPPPPPPhb',
    'bPppKkkpphb',
    'bPppkPkpphb',
    'bPppkkkpphb',
    'bPpppkppphb',
    'bPpppkppphb',
    'bPpppkkpphb',
    '.bpppkppphb',
    '.bpppkkphb.',
    '..bppkphb..',
    '...bpphb...',
    '....bbb....',
]
K_SHIELD = {'b': BRASS[1], 'P': PARCHMENT[3], 'p': PARCHMENT[2], 'h': PARCHMENT[1],
            'k': ASH[0], 'K': ASH[2]}

# A four-point brass star embroidered lower on long banners.
STAR = [
    '..3..',
    '..2..',
    '32b23',
    '..2..',
    '..3..',
]
K_STAR = {'3': BRASS[3], '2': BRASS[2], 'b': BRASS[0]}

# Inkwell with a quill (tall frames, left shelf).
INKWELL = [
    '........33',
    '.......321',
    '......321.',
    '.....321..',
    '....o21...',
    '..oooooo..',
    '.oskkkkso.',
    '.oskkkkso.',
    '.oossssoo.',
    '..oooooo..',
]
K_INKWELL = {'o': INK[1], '3': PARCHMENT[3], '2': PARCHMENT[2], '1': PARCHMENT[0],
             's': SKY[1], 'k': INK[0]}


# ---------------------------------------------------------------------------
# Iron helpers
# ---------------------------------------------------------------------------

def rivet(img, x, y):
    """2x2 iron rivet head: lit top-left, shaded bottom-right."""
    P.put(img, x, y, PARCHMENT[3])
    P.put(img, x + 1, y, ASH[2])
    P.put(img, x, y + 1, ASH[2])
    P.put(img, x + 1, y + 1, INK[2])


def strap_h(img, x0, x1, y, rivet_every=12, phase=0):
    """Horizontal riveted iron strap, 5 rows: ink, lit, body, shadow, ink."""
    P.hline(img, x0, x1, y, INK[1])
    P.hline(img, x0, x1, y + 1, ASH[2])
    P.hline(img, x0, x1, y + 2, ASH[1])
    P.hline(img, x0, x1, y + 3, ASH[0])
    P.hline(img, x0, x1, y + 4, INK[0])
    P.vline(img, x0, y, y + 4, INK[1])
    P.vline(img, x1, y, y + 4, INK[0])
    xx = x0 + 3 + phase
    while xx <= x1 - 4:
        rivet(img, xx, y + 1)
        xx += rivet_every


def strap_v(img, x, y0, y1, side, rivet_every=9, phase=0, edge_ink=False):
    """Vertical iron strap 4 px wide (x .. x+3) for the background margins.
    ``side`` 'l' faces a hole on its right (shadowed inner wall), 'r' faces a
    hole on its left (lit inner wall)."""
    for yy in range(y0, y1 + 1):
        if side == 'l':
            cols = (ASH[2], ASH[1], ASH[1], ASH[0])
        else:
            cols = (ASH[2], ASH[1], ASH[1], ASH[0])
        for i, c in enumerate(cols):
            P.put(img, x + i, yy, c)
    yy = y0 + 2 + phase
    while yy <= y1 - 2:
        rivet(img, x + 1, yy)
        yy += rivet_every


def iron_bracket(img, corner, W, H, arm=12, leg=12):
    """Riveted iron corner bracket clamping the sheet corner (background).
    Horizontal arm 3 rows along the outer edge, vertical leg 4 columns."""
    left = 'l' in corner
    top = 't' in corner
    x0 = 1 if left else W - 1 - arm
    x1 = arm if left else W - 2
    ys = (1, 2, 3) if top else (H - 4, H - 3, H - 2)
    cols = (ASH[2], ASH[1], ASH[0]) if top else (ASH[2], ASH[1], ASH[0])
    for yy, c in zip(ys, cols):
        P.hline(img, x0, x1, yy, c)
    # ink edge on the inner side of the arm and its free end
    inner_y = 4 if top else H - 5
    end_x = x1 + 1 if left else x0 - 1
    P.hline(img, min(x0, end_x), max(x1, end_x), inner_y, INK[1])
    P.vline(img, end_x, min(ys[0], inner_y), max(ys[-1], inner_y), INK[1])
    # leg
    lx = 1 if left else W - 5
    ly0, ly1 = (1, leg) if top else (H - 1 - leg, H - 2)
    for yy in range(ly0, ly1 + 1):
        for i, c in enumerate((ASH[2], ASH[1], ASH[1], ASH[0])):
            if yy in ys and i < 3:
                continue
            P.put(img, lx + i, yy, c)
    # rivets
    rx = (x1 - 3) if left else (x0 + 2)
    rivet(img, rx, ys[0])
    rivet(img, lx + 1, (ly1 - 3) if top else (ly0 + 2))


def strongbox(img, x, y, w, h, seed):
    """Iron-banded strongbox: plank body, domed lid, two riveted iron straps,
    iron corner caps and a brass lockplate on the lid seam."""
    lid_h = max(7, h * 2 // 5)
    # shadow on the shelf/floor
    P.hline(img, x + 2, x + w, y + h, INK[1])
    P.plank(img, (x, y + lid_h - 1, w, h - lid_h + 1), WOOD, seed, 'ink_1', radius=1, grain=0.8)
    P.plank(img, (x, y, w, lid_h), WOOD, seed + 1, 'ink_1', radius=2, grain=0.5, heavy='')
    P.hline(img, x + 1, x + w - 2, y + lid_h - 1, INK[0])          # lid seam
    for bx in (x + 4, x + w - 8):
        for yy in range(y + 1, y + h - 1):
            if yy == y + lid_h - 1:
                continue
            P.put(img, bx, yy, ASH[2]); P.put(img, bx + 1, yy, ASH[1])
            P.put(img, bx + 2, yy, ASH[1]); P.put(img, bx + 3, yy, ASH[0])
        P.put(img, bx, y, INK[1]); P.put(img, bx + 3, y, INK[1])
        rivet(img, bx + 1, y + 2)
        rivet(img, bx + 1, y + lid_h + 1)
        if h - lid_h > 9:
            rivet(img, bx + 1, y + h - 4)
    # iron corner caps on the body
    for cx, flip in ((x + 1, False), (x + w - 3, True)):
        P.sprite(img, cx, y + h - 3, ['21', '10'] if not flip else ['12', '01'],
                 {'2': ASH[2], '1': ASH[1], '0': ASH[0]})
    # brass lockplate straddling the seam, keyhole pressed in ink
    cx = x + w // 2
    P.brass_plate(img, (cx - 3, y + lid_h - 4, 7, 8), rivets=False)
    P.put(img, cx, y + lid_h - 2, INK[0])
    P.put(img, cx, y + lid_h - 1, INK[0])
    P.put(img, cx, y + lid_h, INK[0])
    P.put(img, cx - 1, y + lid_h, INK[0])
    # lid handle
    P.hline(img, cx - 2, cx + 2, y - 1, INK[1])
    P.put(img, cx - 3, y, INK[1]); P.put(img, cx + 3, y, INK[1])
    P.hline(img, cx - 1, cx + 1, y - 1, ASH[1])


def shelf(img, x, y, w, seed):
    """A short plank shelf on two iron brackets."""
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': ASH[1]})


def banner(img, cx, top, length, seed, cloth=SAGE, width=22):
    """Wordless guild banner hanging from a wooden rod: sage cloth with a
    swallowtail foot, an embroidered brass border, a parchment shield bearing
    an iron key and, when long, an iron fess and a brass star. Returns the
    bottom row."""
    bx = cx - width // 2
    ty = top + 2
    by = ty + length - 1
    notch = 6
    inside = set()
    for yy in range(ty, by + 1):
        for xx in range(bx, bx + width):
            if yy > by - notch:
                k = yy - (by - notch)
                half = k * (width // 2 - 2) / notch
                if abs(xx - (cx - 0.5)) < half:
                    continue
            inside.add((xx, yy))
    edge = P._edge_pixels(inside)
    for (xx, yy) in inside:
        P.put(img, xx, yy, cloth[1])
    # drape: lit left, shaded right, two soft folds
    for (xx, yy) in inside:
        if xx == bx + 1:
            P.put(img, xx, yy, cloth[2])
        elif xx == bx + width - 2:
            P.put(img, xx, yy, cloth[0])
    r = P._rng(seed, 'banner')
    for fx in (bx + 6, bx + 16):
        yy = ty + 4 + r.randint(0, 3)
        while yy < by - notch - 1:
            run = r.randint(10, 20)
            for k in range(run):
                if (fx, yy + k) in inside and yy + k < by - notch:
                    P.put(img, fx, yy + k, cloth[0])
                    if (fx - 1, yy + k) in inside:
                        P.put(img, fx - 1, yy + k, cloth[2])
            yy += run + r.randint(3, 6)
    for (xx, yy) in edge:
        s = P._side(inside, xx - 0, yy - 0) if False else ''
        right_or_bottom = ((xx + 1, yy) not in inside) or ((xx, yy + 1) not in inside)
        P.put(img, xx, yy, INK[0] if right_or_bottom and xx > cx - 2 else INK[1])
    # embroidered border: brass running stitch 2 px inside the sides
    P.stitch_line(img, bx + 2, ty + 3, bx + 2, by - notch - 1, BRASS[2], 2, 2)
    P.stitch_line(img, bx + width - 3, ty + 3, bx + width - 3, by - notch - 1, BRASS[1], 2, 2, phase=1)
    P.stitch_line(img, bx + 3, ty + 3, bx + width - 4, ty + 3, BRASS[2], 2, 2)
    # emblem
    P.sprite(img, cx - 5, ty + 6, SHIELD, K_SHIELD)
    low = ty + 6 + 13
    if length >= 46:
        fy = low + 3
        P.hline(img, bx + 1, bx + width - 2, fy, INK[1])
        P.hline(img, bx + 1, bx + width - 2, fy + 1, ASH[2])
        P.hline(img, bx + 1, bx + width - 2, fy + 2, ASH[1])
        P.hline(img, bx + 1, bx + width - 2, fy + 3, ASH[0])
        P.hline(img, bx + 1, bx + width - 2, fy + 4, INK[1])
        rivet(img, bx + 3, fy + 1); rivet(img, bx + width - 5, fy + 1)
        low = fy + 5
    if length >= 62:
        P.sprite(img, cx - 2, low + 3 + (by - notch - low - 11) // 2, STAR, K_STAR)
    # tassels at the two tail tips
    for tx in (bx + 1, bx + width - 2):
        P.put(img, tx, by + 1, BRASS[2]); P.put(img, tx, by + 2, BRASS[1])
        P.put(img, tx - 1 if tx < cx else tx + 1, by + 2, BRASS[0])
    # the rod and its cords
    P.tack(img, cx, top - 8)
    P.twine(img, cx, top - 7, bx - 2, top + 1, sag=0)
    P.twine(img, cx, top - 7, bx + width + 1, top + 1, sag=0)
    P.plank(img, (bx - 4, top, width + 8, 4), WOOD, seed + 3, 'ink_1', radius=1, grain=0)
    P.hline(img, bx - 2, bx + width + 1, top + 1, WOOD[4])
    for kx in (bx - 5, bx + width + 4):
        P.sprite(img, kx - 1, top - 0, ['.oo.', 'o32o', 'o21o', '.oo.'],
                 {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[0]})
    return by + 2


def bunting(img, x0, x1, y, seed, sag=3):
    """A garland of wordless pennants on twine (sage, parchment, iron)."""
    pts = P.twine(img, x0, y, x1, y, sag=sag)
    cols = [(SAGE[1], SAGE[2], SAGE[0]), (PARCHMENT[2], PARCHMENT[3], PARCHMENT[0]),
            (ASH[1], ASH[2], ASH[0])]
    rows = ['ooooooo', 'o22bbdo', '.o2bdo.', '.o2bdo.', '..obo..', '..oo...' if False else '..obo..', '...o...']
    k = 0
    for i in range(3, len(pts) - 5, 8):
        px, py = pts[i]
        body, lit, dark = cols[k % 3]
        P.sprite(img, px - 3, py, rows, {'o': INK[1], 'b': body, '2': lit, 'd': dark})
        k += 1
    P.tack(img, x0, y - 1)
    P.tack(img, x1, y - 1)


def pennant(img, x, y, length, seed, cloth=SAGE):
    """A small triangular guild pennant hanging from a nail on a short
    dowel, brass star embroidered near the hoist."""
    w = 13
    P.tack(img, x + w // 2, y)
    P.twine(img, x + w // 2, y + 1, x, y + 4, sag=0)
    P.twine(img, x + w // 2, y + 1, x + w - 1, y + 4, sag=0)
    inside = set()
    for j in range(length):
        half = (w / 2) * (1 - j / length)
        for i in range(w):
            if abs(i - (w - 1) / 2) <= half:
                inside.add((x + i, y + 6 + j))
    edge = P._edge_pixels(inside)
    for (px, py) in inside:
        col = cloth[1]
        if px == x + 1 or (px - x) < (w - 1) / 2 - (w / 2) * (1 - (py - y - 6) / length) + 2:
            col = cloth[2]
        P.put(img, px, py, col)
    for (px, py) in edge:
        P.put(img, px, py, INK[0] if px > x + w // 2 else INK[1])
    P.sprite(img, x + w // 2 - 2, y + 8, STAR, K_STAR)
    P.plank(img, (x - 2, y + 4, w + 4, 3), WOOD, seed, 'ink_1', radius=1, grain=0, highlight=False)
    P.hline(img, x - 1, x + w, y + 5, WOOD[3])


def lockers(img, x, y, rows, seed):
    """A small wooden rack of locked vault doors (2 columns): each an iron
    door with rivets and a brass lockplate. Wordless: choose a vault."""
    dw, dh = 13, 11
    w = 2 * dw + 5
    h = rows * (dh + 2) + 3
    P.plank(img, (x, y, w, h), WOOD, seed, 'ink_1', radius=1, grain=0.4)
    for r_ in range(rows):
        for c_ in range(2):
            dx = x + 2 + c_ * (dw + 1)
            dy = y + 2 + r_ * (dh + 2)
            P.ink_outline(img, (dx, dy, dw, dh), 'ink_1', radius=0, heavy='br', fill_colour=ASH[1])
            P.hline(img, dx + 1, dx + dw - 2, dy + 1, ASH[2])
            P.vline(img, dx + 1, dy + 1, dy + dh - 2, ASH[2])
            P.hline(img, dx + 2, dx + dw - 2, dy + dh - 2, ASH[0])
            P.vline(img, dx + dw - 2, dy + 2, dy + dh - 2, ASH[0])
            for (rx, ry) in ((dx + 2, dy + 2), (dx + dw - 3, dy + 2), (dx + 2, dy + dh - 3), (dx + dw - 3, dy + dh - 3)):
                P.put(img, rx, ry, PARCHMENT[3] if (rx, ry) == (dx + 2, dy + 2) else ASH[2])
            # brass lockplate with keyhole
            lx, ly = dx + dw // 2 - 2, dy + 3
            P.sprite(img, lx, ly, ['o333o', 'o2k1o', 'o2k1o', 'o111o', '.ooo.'] if False else
                     ['.ooo.', 'o32ko' if False else 'o3k2o', 'o2k1o', 'o211o', '.ooo.'],
                     {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[0], 'k': INK[0]})
    return h


def key_hoop(img, cx, y, seed):
    """An iron key hoop hung from a nail with four keys threaded on its
    lower arc (brass, iron, brass, iron), hanging in front of it."""
    P.tack(img, cx, y)
    P.vline(img, cx, y + 2, y + 3, INK[1])
    hw, hh = 23, 13
    hx, hy = cx - hw // 2, y + 4
    ring = set()
    for j in range(hh):
        for i in range(hw):
            dx, dy = (i - hw // 2) / (hw / 2 + 0.1), (j - hh // 2) / (hh / 2 + 0.1)
            ix, iy = (i - hw // 2) / (hw / 2 - 2.6), (j - hh // 2) / (hh / 2 - 2.6)
            if dx * dx + dy * dy <= 1.0 and ix * ix + iy * iy > 1.0:
                ring.add((i, j))
    edge = P._edge_pixels(ring)
    for (i, j) in ring:
        if (i, j) in edge:
            col = INK[1]
        elif j <= 3 or (i < 7 and j <= 7):
            col = ASH[2]
        elif j >= 9 or i > 15:
            col = ASH[0]
        else:
            col = ASH[1]
        P.put(img, hx + i, hy + j, col)
    P.put(img, hx + 6, hy + 2, PARCHMENT[3])
    P.put(img, hx + 7, hy + 1, PARCHMENT[3])
    P.sprite(img, cx - 10, hy + 8, KEY_HANG_SHORT, K_KEY)
    P.sprite(img, cx - 5, hy + 10, KEY_HANG_LONG, K_IRON_KEY)
    P.sprite(img, cx + 1, hy + 10, KEY_HANG_SHORT + ['.o2o.', '.o2oo', '.ooo.'][:0], K_KEY)
    P.sprite(img, cx + 6, hy + 8, KEY_HANG_LONG[:9] + ['.ooo.'], K_IRON_KEY)
    return 4 + 10 + 12


def vine(img, x, y0, y1, seed):
    """A trailing sage ivy: a wobbling stem with alternating leaves."""
    r = P._rng(seed, 'vine')
    xx = x
    y = y0
    k = 0
    while y < y1:
        run = r.randint(3, 6)
        P.vline(img, xx, y, min(y1, y + run - 1), SAGE[0])
        y += run
        xx = x + (1 if (k % 2 == 0) else 0)
        if y < y1 - 4 and k % 2 == 0:
            if (k // 2) % 2 == 0:
                P.leaf(img, xx + 1, y - 3, 'ne', small=(k % 3 == 2))
            else:
                P.leaf(img, xx - 6 if (k % 3 != 2) else xx - 4, y - 3, 'nw', small=(k % 3 == 2))
        k += 1


def wall_lantern(img, x, y, seed):
    """Iron wall bracket (plate at the right, braced arm to the left) with a
    lantern hanging from its tip and a warm dithered glow. ``x`` is the left
    tip of the arm. Returns the height."""
    arm_w = 18
    # wall plate
    px = x + arm_w - 2
    P.ink_outline(img, (px, y - 2, 4, 11), 'ink_1', radius=1, heavy='br', fill_colour=ASH[1])
    P.vline(img, px + 1, y - 1, y + 7, ASH[2])
    rivet(img, px + 1, y)
    rivet(img, px + 1, y + 5)
    # arm with a curled tip
    P.hline(img, x + 1, px - 1, y, INK[1])
    P.hline(img, x + 1, px - 1, y + 1, ASH[2])
    P.hline(img, x + 1, px - 1, y + 2, INK[1])
    P.sprite(img, x - 2, y - 2, ['.oo.', 'o2.o', 'o.oo', '.o..'], {'o': INK[1], '2': ASH[2]})
    # diagonal brace
    P.lantern_glow_ring(img, x + 4, y + 10, 12, strength=1)
    for k in range(6):
        P.put(img, px - 1 - k, y + 6 - k, INK[1])
        P.put(img, px - 1 - k, y + 7 - k, ASH[1])
        P.put(img, px - 1 - k, y + 8 - k, INK[1])
    # chain and lantern
    P.vline(img, x + 3, y + 3, y + 4, ASH[0])
    P.put(img, x + 3, y + 5, INK[1])
    P.lantern(img, x, y + 6)
    return 15


def charter(img, x, y, w, h, seed):
    """The guild charter: a pinned parchment sheet with ruled lines (no
    words), a sage wax seal on a ribbon and a curled corner."""
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=True)
    for k in range(5, h - 9, 3):
        P.stitch_line(img, x + 3, y + k, x + w - 4 - (4 if k % 2 else 0), y + k, SKY[2], 3, 1, phase=k)
    P.page_curl(img, (x, y, w, h), 'br', 4, behind=WOOD[0])
    P.tack(img, x + w // 2, y + 1)
    sx, sy = x + 7, y + h - 6
    P.sprite(img, sx - 2, sy + 2, ['o..o', 'oo.oo'[:4], '.oo.'] if False else ['oo.oo', 'o1.1o', '.o.o.'],
             {'o': INK[1], '1': SAGE[1]})
    P.wax_seal(img, sx, sy, 5, SAGE, seed, drip=False)


def stack_positions(top, bottom, heights):
    """Distribute items of ``heights`` between ``top`` and ``bottom`` with equal
    gaps (first item at ``top``, last item ending at ``bottom``)."""
    total = sum(heights)
    n = len(heights)
    gap = (bottom - top - total) / max(1, n - 1)
    out, y = [], float(top)
    for h in heights:
        out.append(int(round(y)))
        y += h + gap
    return out


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def paint_background(key):
    s = geo.skin(key)
    W, H = s.width, s.height
    img = C.base_background(key, seed=SEED + s.height)
    tband, iband = C.bands(key)
    content_bottom = max(sl.clearance.bottom for sl in s.content_slots)    # exclusive
    # iron straps down both sides of the vault grid, title band to inventory band
    y0, y1 = 4, content_bottom
    strap_v(img, 1, y0, y1, 'l', phase=1)
    strap_v(img, W - 5, y0, y1, 'r', phase=5)
    for x in (5, W - 6):           # ink edge where the strap crosses the title paper
        P.vline(img, x, tband.y, tband.bottom - 1, INK[1])
    P.hline(img, 1, 4, y1 + 1, INK[0])
    P.hline(img, W - 5, W - 2, y1 + 1, INK[0])
    # riveted corner brackets clamping the sheet
    for corner in ('tl', 'tr'):
        iron_bracket(img, corner, W, H, arm=11, leg=4)
    for corner in ('bl', 'br'):
        iron_bracket(img, corner, W, H, arm=11, leg=12)
    # family motif on the inventory band, right end, clear of the live label
    if key in SELECT:
        kx, ky = iband.right - 16, iband.y + iband.h // 2 - 2
        P.sprite(img, kx, ky, KEY_FLAT, K_KEY)
        P.twine(img, kx - 6, ky + 2, kx, ky + 2, sag=0)
        P.tack(img, kx - 7, ky + 1, small=True)
    else:
        lx, ly = iband.right - 12, iband.y + (iband.h - 8) // 2
        P.sprite(img, lx, ly, PADLOCK_OPEN, K_PADLOCK)
    # tidy the title-band tack remnants the straps cut through
    for (x, y) in ((6, 8), (168, 8), (169, 7), (169, 8), (169, 9)):
        P.put(img, x, y, PARCHMENT[2])
    geo.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def paint_frame(key):
    s = geo.skin(key)
    a = s.layer()
    seed = SEED + a.h
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H, Wf = a.h, a.w
    c = a.container

    # --- beams: riveted iron straps (clear of the heading ribbon) ------------
    import lettering as L
    rib_w = L.text_width(a.heading or '', 'sprig') + 16
    mid = Wf // 2
    strap_h(img, 10, mid - rib_w // 2 - 4, 2, rivet_every=14, phase=2)
    strap_h(img, mid + rib_w // 2 + 3, Wf - 11, 2, rivet_every=14, phase=6)
    strap_h(img, 10, Wf - 11, H - 7, rivet_every=16, phase=4)

    # --- left panel: GUILD tag, banner, (inkwell shelf), strongbox --------------
    cx = lp.x + 20
    bottom = H - 11
    banner_len = max(40, min(92, 40 + (H - 148) * 6 // 10))
    has_shelf = H >= 184
    heights = [10, 12 + banner_len]
    if has_shelf:
        heights.append(16)
    heights.append(31)      # strongbox + candle on top
    ys = stack_positions(12, bottom, heights)
    P.tack(img, cx, 10)
    C.side_tag(img, lp, a.left_heading or 'GUILD', ys[0] + 2, seed, twine_from=(cx, 11))
    banner(img, cx, ys[1] + 9, banner_len, seed)
    if has_shelf:
        sy = ys[2] + 11
        shelf(img, lp.x + 4, sy, lp.w - 8, seed + 5)
        P.sprite(img, lp.x + 7, sy - 10, INKWELL, K_INKWELL)
        icons.draw_motif(img, 'ledger', lp.x + 20, sy - 10)
    by = ys[-1] + 12
    strongbox(img, lp.x + 5, by, 30, 19, seed + 7)
    icons.draw_motif(img, 'candle', lp.x + 8, by - 12)
    P.lantern_glow_ring(img, lp.x + 10, by - 10, 9, strength=1)
    icons.draw_motif(img, 'coin', lp.x + 25, by - 6)
    icons.draw_motif(img, 'coin', lp.x + 29, by - 6)
    icons.draw_motif(img, 'coin', lp.x + 27, by - 9)

    # --- right panel ---------------------------------------------------------
    rx = rp.x
    if key not in SELECT:
        vine(img, rp.right - 10, 30, bottom - 20, seed + 23)
    if key in SELECT:
        # key hoop on a nail, a rack of locked vault doors with a candle on
        # top, a shut padlock on a nail and a coin purse
        rows = 3 if H < 170 else 5
        rack_h = rows * 13 + 3
        heights = [23, 12 + rack_h, 17]
        ys = stack_positions(10, bottom, heights)
        key_hoop(img, rx + 19, ys[0], seed)
        ry = ys[1] + 12
        lockers(img, rx + 4, ry, rows, seed + 11)
        icons.draw_motif(img, 'candle', rx + 25, ry - 11)
        P.lantern_glow_ring(img, rx + 27, ry - 9, 10, strength=1)
        icons.draw_motif(img, 'coin', rx + 8, ry - 5)
        icons.draw_motif(img, 'coin', rx + 13, ry - 5)
        fy = ys[2]
        P.tack(img, rx + 10, fy)
        P.vline(img, rx + 10, fy + 2, fy + 3, INK[1])
        P.sprite(img, rx + 6, fy + 4, PADLOCK_SHUT, K_PADLOCK)
        icons.draw_icon(img, 'balance', (rx + 19, fy + 2, 14, 15))
        P.hline(img, rx + 18, rp.right - 6, fy + 16, INK[1])
    else:
        # lantern on a wall bracket, coin + ledger shelf, (pennant garland),
        # (the guild charter), coin purse and crate
        tall = H >= 166
        has_charter = H >= 202
        has_pennant = H >= 220
        heights = ([17, 18] + ([14] if tall else []) + ([22] if has_pennant else [])
                   + ([30] if has_charter else []) + [17])
        ys = stack_positions(10, bottom, heights)
        wall_lantern(img, rx + 9, ys[0] + 2, seed)
        sy = ys[1] + 12
        shelf(img, rx + 3, sy, rp.w - 7, seed + 13)
        icons.draw_motif(img, 'ledger', rx + 5, sy - 10)
        for (ox, oy) in ((19, -5), (24, -5), (29, -5), (21, -8), (26, -8), (24, -11)):
            icons.draw_motif(img, 'coin', rx + ox, sy + oy)
        k = 2
        if tall:
            bunting(img, rx + 4, rp.right - 6, ys[k] + 2, seed, sag=3)
            k += 1
        if has_pennant:
            pennant(img, rx + 13, ys[k], 15, seed + 19)
            k += 1
        if has_charter:
            charter(img, rx + 6, ys[k], 25, 30, seed + 17)
            k += 1
        fy = ys[k]
        icons.draw_icon(img, 'balance', (rx + 3, fy + 1, 14, 15))
        icons.draw_motif(img, 'crate', rx + 20, fy + 6)
        P.hline(img, rx + 3, rp.right - 5, fy + 16, INK[1])

    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out-root', type=Path, help='write into DIR laid out like textures/ instead of pack-source')
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    args = ap.parse_args(argv)
    keys = args.skin or list(SKINS)
    root = args.out_root
    for key in keys:
        s = geo.skin(key)
        bg = paint_background(key)
        p = C.save_png(bg, (root / 'menu' / f'{key}.png') if root else s.background_path)
        print('WROTE', p)
        for a in s.art_layers:
            fr = paint_frame(key)
            p = C.save_png(fr, (root / 'frames' / key / f'{a.id}.png') if root else s.frame_path(a.id))
            print('WROTE', p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
