#!/usr/bin/env python3
"""Soulrend painter "guildbank": the guild bank family (8 skins).

    python tools/soulrend/paint_guildbank.py                 # all eight skins
    python tools/soulrend/paint_guildbank.py --skin guild_bank_3
    python tools/soulrend/paint_guildbank.py --out-root DIR  # DIR/menu, DIR/frames

Skins (all native_content_preserved, no buttons): guild_bank_select_1 and
guild_bank_select_3 are the vault-selection screens; guild_bank_1 .. 6 show a
vault's contents. Each owns one background (176 wide) and one outer frame
(256 x container + 16).

Family identity (docs/SOULREND-STYLE-GUIDE.md section 5, guild_bank: accent
iron, secondary moss): an iron strongroom. Backgrounds keep the shared sheet
and sockets and add riveted iron straps in the margins beside the grids and
under the hotbar. Frames show ONE great vault door in a stone portal (strap
hinges, hand wheel, keyhole escutcheon, locking bolts) in the left panel, and a
moss guild banner bearing a wordless crossed-keys crest in the right panel.
Selection screens: the door's bolts are thrown, a ring of keys hangs on a hook
and a shut padlock hangs on a chain. Vault screens: the bolts are withdrawn and
ember light leaks from the door's seam, an open padlock hangs from a peg and a
lit brazier burns on the floor. Every frame height is laid out for its height
(door, banner and spacing scale; extra elements join on taller frames).

Deterministic: fixed seeds per skin, no clock. Licence: MIT (tooling); the
artwork it paints is CC0-1.0.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
for _p in (str(_HERE.parent), str(_HERE.parent / 'cozy')):
    if _p not in sys.path:
        sys.path.append(_p)

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import icons  # noqa: E402
import primitives as P  # noqa: E402
from palette import EMBER, GOLD, INK, IRON, MOSS, STONE  # noqa: E402

SKINS = ('guild_bank_select_1', 'guild_bank_select_3', 'guild_bank_1', 'guild_bank_2',
         'guild_bank_3', 'guild_bank_4', 'guild_bank_5', 'guild_bank_6')
SEEDS = {k: 61 + 7 * i for i, k in enumerate(SKINS)}


def is_select(key):
    return key.startswith('guild_bank_select')


# ---------------------------------------------------------------------------
# Background: shared sheet + iron strongroom straps in the margins
# ---------------------------------------------------------------------------

def _rivet2(img, x, y, right=False):
    """A 2x2 domed rivet on an iron strap (lit top-left)."""
    P.put(img, x, y, IRON[3])
    P.put(img, x + 1, y, IRON[2] if not right else IRON[1])
    P.put(img, x, y + 1, IRON[2])
    P.put(img, x + 1, y + 1, INK[0])


def paint_background(key, seed):
    s = geo.skin(key)
    W, H = s.width, s.height
    img = C.base_background(key, seed=seed)
    holes = P.merge_holes(s.content_slots) + P.merge_holes(s.player_slots)
    top = min(r[1] for r in holes)
    bottom = max(r[1] + r[3] for r in holes)
    # Side straps: the sheet column beside the iron band becomes a riveted
    # iron strap (x1-2 lit side, x173-174 shadow side), from just under the
    # title band to the corner brackets.
    for y in range(2, H - 7):
        P.put(img, 2, y, IRON[1])
        P.put(img, W - 3, y, IRON[1])
    # rivets on every slot seam of the grids (never in a clearance: x <= 2)
    ys = set()
    for (x, y, w, h) in holes:
        for k in range(0, h + 1, 18):
            ys.add(y + k + 8)
    for y in sorted(ys):
        if 16 <= y <= H - 10:
            _rivet2(img, 1, y)
            _rivet2(img, W - 3, y, right=True)
    # strap ends: a dark notch under the title band and above the brackets
    for x in (1, 2, W - 3, W - 2):
        P.put(img, x, 15, INK[1])
    # Bottom strap under the hotbar socket (two rows of sheet): blackened iron
    # with rivets at the slot seams and a small moss creep at the damp corner.
    y0 = bottom + 3
    if y0 <= H - 4:
        for y in range(y0, H - 2):
            P.hline(img, 7, W - 8, y, IRON[1] if y == y0 else IRON[0])
        for x in range(6, W - 6, 18):
            if 8 <= x <= W - 10:
                P.put(img, x + 8, y0, IRON[3])
                P.put(img, x + 9, y0, IRON[2])
                P.put(img, x + 9, y0 + 1, INK[0])
        # a gold-rimmed hasp plate at the centre of the strap
        cx = W // 2
        P.hline(img, cx - 3, cx + 2, y0, GOLD[1])
        P.put(img, cx - 3, y0, GOLD[2])
        P.hline(img, cx - 3, cx + 2, y0 + 1, GOLD[0])
        P.put(img, cx - 1, y0 + 1, INK[0])
        P.put(img, cx, y0 + 1, INK[0])
        P.put(img, cx - 1, y0, INK[0])
        P.put(img, W - 12, y0 + 1, MOSS[1]); P.put(img, W - 11, y0 + 1, MOSS[2])
        P.put(img, 10, y0 + 1, MOSS[0])
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frame sprites (hand-authored, original)
# ---------------------------------------------------------------------------

# Shut padlock: iron shackle seated in an iron body, gold escutcheon, keyhole.
PADLOCK_SHUT = [
    '...ooooo...',
    '..odddcco..',
    '.odo...obo.',
    '.oco...obo.',
    '.oco...oao.',
    'ooooooooooo',
    'odccccccbao',
    'ocbbhHhbbao',
    'ocbhgOghbao',
    'ocbhOOOhbao',
    'ocbhgOghbao',
    'ocbhOOOhbao',
    'obbbggg bao'.replace(' ', 'b'),
    'oaaaaaaaaao',
    '.ooooooooo.',
]

# Open padlock: the shackle lifted out and swung, its free leg clear of the body.
PADLOCK_OPEN = [
    '..ooooo....',
    '.odddcco...',
    'odo...obo..',
    'oco...obo..',
    'oco...oao..',
    'oco...ooo..',
    'oco........',
    'oco........',
    'ooooooooooo',
    'odccccccbao',
    'ocbbhHhbbao',
    'ocbhgOghbao',
    'ocbhOOOhbao',
    'ocbhgOghbao',
    'ocbhOOOhbao',
    'obbbgggbbao',
    'oaaaaaaaaao',
    '.ooooooooo.',
]

KEY_GOLD = [
    '.ooo.',
    'oHhho',
    'oh.go',
    'ohggo',
    '.oho.',
    '.oho.',
    '.oho.',
    '.ohoo',
    '.ohHo',
    '.ohoo',
    '.oho.',
    '.ooo.',
]
KEY_IRON = [row.replace('H', 'd').replace('h', 'c').replace('g', 'b') for row in KEY_GOLD]


# Guild crest: an iron shield, gold rim, gold crossed keys (no words).
GUILD_SHIELD = [
    'ooooooooooooo',
    'ohhhhhhhhhhgo',
] + ['ohbbbbbbbbbgo'] * 8 + [
    '.ohbbbbbbbgo.',
    '.ohbbbbbbbgo.',
    '..ohbbbbbgo..',
    '...ohbbbgo...',
    '....ohbgo....',
    '.....ogo.....',
    '......o......',
]
GUILD_CHARGE = [            # relative to (2, 2): one upright key, ring bow up, bit down
    '...HHH...',
    '..Hh.hh..',
    '..H...g..',
    '..h...g..',
    '...hgg...',
    '....H....',
    '....h....',
    '....hHh..',
    '....h....',
    '....hHg..',
]


def guild_crest(img, x, y):
    P.sprite(img, x, y, GUILD_SHIELD)
    for j, row in enumerate(GUILD_CHARGE):
        for i, ch in enumerate(row):
            if ch != '.':
                P.put(img, x + 2 + i, y + 2 + j, P.SK[ch])
    return len(GUILD_SHIELD[0]), len(GUILD_SHIELD)


# ---------------------------------------------------------------------------
# Frame elements
# ---------------------------------------------------------------------------

def wheel(img, cx, cy, r):
    """Vault hand-wheel: a forged iron ring lit top-left over a dark recess,
    four heavy spokes, gold knobs beyond the ring at the spoke ends and a
    gold hub."""
    for y in range(cy - r - 3, cy + r + 4):
        for x in range(cx - r - 3, cx + r + 4):
            d = math.hypot(x - cx, y - cy)
            t = (x - cx) + (y - cy)
            if d <= r - 2.5:
                P.put(img, x, y, IRON[0])
            elif d <= r - 1.5:
                P.put(img, x, y, INK[1])
            elif d <= r + 0.5:
                P.put(img, x, y, IRON[3] if t < -r * 0.7 else IRON[0] if t > r * 0.7 else IRON[2])
            elif d <= r + 1.5:
                P.put(img, x, y, INK[0])
    spokes = {}
    for a in (45, 135, 225, 315):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        lit = IRON[3] if a == 225 else IRON[2]
        for k in range(2, r - 1):
            px, py = round(cx + k * ca), round(cy + k * sa)
            spokes[(px, py)] = lit
            spokes.setdefault((px + 1, py), IRON[1])
    for (px, py) in list(spokes):
        if (px, py + 1) not in spokes:
            P.put(img, px, py + 1, INK[0])
    for (px, py), c in spokes.items():
        P.put(img, px, py, c)
    for a in (45, 135, 225, 315):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        kx, ky = round(cx + (r + 2) * ca), round(cy + (r + 2) * sa)
        P.sprite(img, kx - 1, ky - 1, ['.o.', 'oHo', 'ogO'] if a != 45 else ['.o.', 'oho', 'ogO'])
    P.sprite(img, cx - 2, cy - 2, ['.ooo.', 'oHhgo', 'ohOgo', 'oggOo', '.ooo.'])


def keyhole_plate(img, cx, y):
    """Gold escutcheon (7x9) with an ink keyhole, top-left at (cx-3, y)."""
    P.sprite(img, cx - 3, y, [
        '.ooooo.',
        'oHHHHho',
        'oHhOhgo',
        'oHOOOgo',
        'oHhOhgo',
        'ohhOhgo',
        'ohOOOgo',
        'ohgggOo',
        '.ooooo.',
    ])


def strap_hinge(img, x, y, length, tip=True):
    """A strap hinge 3 rows tall from a knuckle left of the leaf edge ``x``,
    running ``length`` px across the door, ending in a spear tip, riveted."""
    P.sprite(img, x - 4, y - 2, ['.oo.', 'odbo', 'odbo', 'odbo', 'odbo', 'odbo', '.oo.'])
    x1 = x + length
    P.hline(img, x, x1, y - 1, INK[0])
    P.hline(img, x, x1, y, IRON[3])
    P.hline(img, x, x1, y + 1, IRON[2])
    P.hline(img, x, x1, y + 2, IRON[0])
    P.hline(img, x, x1, y + 3, INK[0])
    if tip:
        P.sprite(img, x1 + 1, y - 2, ['o..', 'do.', 'cdo', 'cbo', 'ao.', 'o..'])
    for rx in range(x + 3, x1 - 1, 5):
        P.put(img, rx, y + 1, IRON[3]); P.put(img, rx + 1, y + 2, INK[0])


def portal(img, x, y, w, h, seed):
    """Stone door portal round a door leaf at (x, y, w, h): two jambs of
    alternating ashlar, a lintel with a keystone, a stone threshold step.
    Returns the portal's outer box."""
    ox, oy, ow, oh = x - 4, y - 6, w + 8, h + 6
    r = P._rng(seed, 'portal', x, y)
    P.fill(img, (ox, oy, ow, oh), STONE[0])
    # jambs: blocks of 5-8 rows, alternating long/short
    for side, jx in ((0, ox), (1, x + w)):
        yy = y
        k = side
        while yy < y + h:
            bh = r.randint(5, 8)
            bh = min(bh, y + h - yy)
            face = STONE[2] if (k % 3) else STONE[3]
            P.fill(img, (jx, yy, 4, bh - 1), face)
            P.hline(img, jx, jx + 2, yy, STONE[3] if face == STONE[2] else STONE[3])
            P.vline(img, jx + 3, yy + 1, yy + bh - 2, STONE[1])
            yy += bh
            k += 1
    # lintel: three voussoir-like blocks and a raised keystone
    P.fill(img, (ox, oy, ow, 5), STONE[2])
    P.hline(img, ox, ox + ow - 1, oy, STONE[3])
    P.hline(img, ox, ox + ow - 1, oy + 4, STONE[1])
    for jx in (ox + ow // 3, ox + 2 * ow // 3):
        P.vline(img, jx, oy + 1, oy + 4, STONE[0])
    kx = x + w // 2
    P.sprite(img, kx - 3, oy - 2, ['.ooooo.', 'oqqqqpo', 'oqppppo', 'oqpppno', 'oqpppno', '.oqpno.', '..ooo..'])
    P.ink_outline(img, (ox - 1, oy - 1, ow + 2, oh + 1), 'ink_1', radius=0, heavy='r')
    P.crack(img, ox + 1, y + h // 2, 5, seed=seed, colour=STONE[0], light=STONE[3], branch=False)
    return (ox - 1, oy - 1, ow + 2, oh + 1)


def threshold(img, x, y, w):
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[1])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0, heavy='b')


def vault_door(img, x, y, w, h, seed, locked=True):
    """One great iron vault door in a stone portal. ``locked``: bolts thrown
    into the right jamb; otherwise the bolts are withdrawn and ember light
    leaks from the seam."""
    portal(img, x, y, w, h, seed)
    # leaf
    P.ink_outline(img, (x, y, w, h), 'ink_0', radius=1, fill_colour=IRON[1])
    P.bevel(img, (x + 1, y + 1, w - 2, h - 2), IRON[2], INK[1])
    P.highlight_edge(img, (x + 1, y + 1, w - 2, h - 2), IRON[3], 'tl', broken=5, seed=seed)
    # recessed inner panel: shadow on its top/left walls, light on bottom/right
    px0, py0, px1, py1 = x + 4, y + 4, x + w - 5, y + h - 5
    P.hline(img, px0, px1, py0, IRON[0]); P.vline(img, px0, py0, py1, IRON[0])
    P.hline(img, px0 + 1, px1, py1, IRON[2]); P.vline(img, px1, py0 + 1, py1, IRON[2])
    # perimeter rivets
    for rx in range(x + 3, x + w - 3, 4):
        for ry in (y + 2, y + h - 3):
            P.put(img, rx, ry, IRON[3]); P.put(img, rx + 1, ry + 1 if ry + 1 < y + h - 1 else ry, INK[0])
    for ry in range(y + 6, y + h - 5, 4):
        for rx in (x + 2, x + w - 3):
            P.put(img, rx, ry, IRON[3]); P.put(img, rx + 1, ry + 1, INK[0])
    # hammer pits
    r = P._rng(seed, 'door')
    for _ in range(w * h // 70):
        P.put(img, r.randint(px0 + 2, px1 - 2), r.randint(py0 + 2, py1 - 2), IRON[0])
    # strap hinges at top and bottom; tall doors get a third hinge at the
    # middle with the wheel above it and the keyhole below it
    rw = 8
    if h >= 80:
        hinge_rows = [y + 7, y + h // 2, y + h - 10]
        cy = (y + 10 + y + h // 2 - 2) // 2
        plate_y = (y + h // 2 + 3 + y + h - 12) // 2 - 4
    else:
        hinge_rows = [y + 7, y + h - 10]
        cy = y + max(rw + 14, int(h * 0.36))
        plate_y = cy + rw + 4
    for hy in hinge_rows:
        strap_hinge(img, x, hy, int(w * 0.55))
    # bolts on the right edge
    bolt_rows = [y + h // 5, y + h // 2 + 3, y + h - h // 5 - 2]
    for by in bolt_rows:
        if locked:
            P.sprite(img, x + w - 2, by, ['oooooo', 'cddcbo', 'baaaao', 'oooooo'])
        else:
            P.sprite(img, x + w + 1, by, ['ooo', 'OOo', 'OOo', 'ooo'])     # empty bolt sockets
            P.sprite(img, x + w - 3, by, ['ooo', 'cbo', 'bao', 'ooo'])
    if not locked:
        # the door stands unlatched: a dark seam with ember light leaking out
        for yy in range(y + 2, y + h - 1):
            P.put(img, x + w - 1, yy, INK[0])
            if yy % 3 == 0:
                P.put(img, x + w - 1, yy, EMBER[0])
            if yy % 6 == 1:
                P.put(img, x + w - 1, yy, EMBER[1])
    # wheel and keyhole
    cx = x + w // 2
    wheel(img, cx, cy, rw)
    keyhole_plate(img, cx, plate_y)
    # moss at the foot of the door, a scuff on the leaf
    P.moss_tuft(img, x + 2, y + h - 2, 4, seed=seed)
    P.moss_tuft(img, x + w - 7, y + h - 2, 3, seed=seed + 1)


def candle_on(img, x, y_base, height, seed, glow=10):
    """A lit candle standing with its holder's foot on row ``y_base``."""
    fx, fy = P.candle(img, x, y_base - height - 2, height=height, lit=True, holder='iron', seed=seed)
    if glow:
        P.glow(img, fx, fy + 1, glow, 'ember')
    return fx, fy


def ledge(img, x, y, w):
    """A carved stone ledge on two iron brackets (top row at ``y``)."""
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0, heavy='b')
    for bx in (x + 2, x + w - 5):
        P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


# Key cores: '+' is the hole in the bow (ink), H/h/g lit/mid/shadow metal.
KEY_CORE = {
    'long':  ['HHh', 'H+g', 'hgg', '.h.', '.h.', '.h.', '.h.', '.hH', '.h.', '.hH'],
    'mid':   ['HHh', 'H+g', 'hgg', '.h.', '.h.', '.h.', '.hH', '.hH'],
    'short': ['HHh', 'H+g', 'hgg', '.h.', '.h.', '.hH', '.h.', '.hH'],
    # hanging askew to the lower left from a bow at the top right
    'askew': ['....HHh', '....H+g', '....hgg', '...h...', '..h....', '.h.....', 'hhH....', '.H.....'],
    # hanging from the ring and leaning a pixel outward (left; flip for
    # right), its bit on the outer side, so the bunch fans gently downward
    'lean':  ['.HHh', '.H+g', '.hgg', '..h.', '..h.', '.h..', 'Hh..', '.h..', 'Hh..'],
}


def draw_key(img, x, y, core, ramp, flip=False):
    """A key from ``KEY_CORE`` with its bow's top-left core pixel at (x, y),
    in ``ramp`` (lit, mid, dark), outlined in ink (ink_0 below/right)."""
    rows = KEY_CORE[core]
    if flip:
        rows = [r[::-1] for r in rows]
    pts = {}
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != '.':
                pts[(x + i, y + j)] = ch
    for (px, py) in list(pts):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                q = (px + ddx, py + ddy)
                if q not in pts:
                    P.put(img, q[0], q[1], INK[0] if (ddx > 0 or ddy > 0) else INK[1])
    lit, mid, dark = ramp
    for (px, py), ch in pts.items():
        P.put(img, px, py, {'H': lit, 'h': mid, 'g': dark, '+': INK[0]}[ch])


def key_ring(img, cx, y, seed):
    """A wall staple at row ``y`` holding a small forged iron ring with a
    bunch of three keys hanging from its lower arc, bows threaded on the ring
    and bits pointing down (tarnished gold in the middle): read at 1x as keys
    on a ring, never as a claw. 25 rows."""
    rcx, rcy, rr = cx, y + 8, 4
    gold = (GOLD[2], GOLD[1], GOLD[0])
    iron = (IRON[3], IRON[2], IRON[0])

    def ring_px(yy_min=-99):
        for yy in range(max(rcy - rr - 2, yy_min), rcy + rr + 3):
            for xx in range(rcx - rr - 2, rcx + rr + 3):
                d = math.hypot(xx - rcx, yy - rcy)
                t = (xx - rcx) + (yy - rcy)
                if rr - 0.6 < d <= rr + 0.6:
                    yield xx, yy, IRON[3] if t < -3 else IRON[0] if t > 3 else IRON[2]
                elif yy_min < 0 and (rr + 0.6 < d <= rr + 1.5 or rr - 1.5 < d <= rr - 0.6):
                    yield xx, yy, INK[0] if t > 0 else INK[1]

    for xx, yy, col in ring_px():
        P.put(img, xx, yy, col)
    # keys hang below the ring, bows hooked over its lower arc ...
    draw_key(img, rcx - 6, rcy + 4, 'lean', iron)
    draw_key(img, rcx + 3, rcy + 4, 'lean', iron, flip=True)
    draw_key(img, rcx - 1, rcy + 6, 'long', gold)
    # ... and the ring passes back over the top of each bow (threaded)
    for xx, yy, col in ring_px(rcy + 2):
        P.put(img, xx, yy, col)
    P.sprite(img, cx - 2, y, ['ooooo', 'odcbo', 'obbao', '.oco.', '.oco.'])
    return y + 28


def hung_padlock(img, cx, y0, y1, seed):
    """A shut padlock hanging on a chain from a wall staple at ``y0``; the
    lock's top sits at ``y1``."""
    P.sprite(img, cx - 2, y0, ['ooooo', 'odcbo', 'obbao', 'ooooo'])
    P.chain(img, cx, y0 + 4, cx, y1 - 1, seed=seed)
    P.sprite(img, cx - 5, y1, PADLOCK_SHUT)
    return y1 + len(PADLOCK_SHUT)


def open_padlock(img, cx, y0, y1, seed):
    """An open padlock hanging by its free shackle from a chain on a wall
    staple at ``y0``; the shackle top sits at ``y1``."""
    P.sprite(img, cx - 2, y0, ['ooooo', 'odcbo', 'obbao', 'ooooo'])
    P.chain(img, cx, y0 + 4, cx, y1, seed=seed)
    P.sprite(img, cx - 2, y1, PADLOCK_OPEN)
    return y1 + len(PADLOCK_OPEN)


STRONGBOX = [
    '.ooooooooooooo.',
    'o3c3333c3333c2o',
    'o2c2222c2222c1o',
    'ooooooooooooooo',
    'o2c22hHHh22c21o',
    'o2c22hOgh22c10o',
    'o2c22gOgg22c10o',
    'o1c1111a111c00o',
    'oaaaaaaaaaaaaao',
    '.oo.........oo.',
]


def sconce(img, cx, y, seed, glow=11):
    """An iron wall sconce holding a lit candle (16 rows from ``y``)."""
    fx, fy = P.candle(img, cx - 1, y + 4, height=6, lit=True, holder=None, seed=seed)
    P.sprite(img, cx - 3, y + 11, ['occcco', '.obao.', '..oo..', '..oa..', '...o..'])
    if glow:
        P.glow(img, fx, fy + 1, glow, 'ember')
        P.candle(img, cx - 1, y + 4, height=6, lit=True, holder=None, seed=seed)
    return y + 16


def corbel(img, cx, y, seed):
    """A worn gargoyle crouched on a carved corbel jutting from the wall
    (18 rows from ``y``), a moss tuft under it."""
    gw, gh = icons.motif_size('gargoyle')
    icons.draw_motif(img, 'gargoyle', cx - gw // 2, y)
    P.sprite(img, cx - 7, y + gh, [
        'oooooooooooooo',
        'oqqqqqqqqqqqpo',
        'opppppppppppno',
        '.onnnnnnnnnmo.',
        '..ommmmmmmmo..',
        '...oooooooo...',
    ])
    P.moss_tuft(img, cx - 4, y + gh + 5, 3, seed=seed)
    return y + gh + 7


def niche_strongbox(img, cx, y, seed):
    """A round-topped stone niche (24 x 24) holding an iron-bound strongbox,
    on a short sill."""
    x = cx - 12
    P.arch_niche(img, (x, y, 24, 24), seed=seed)
    w, h = P.sprite_size(STRONGBOX)
    P.sprite(img, cx - w // 2, y + 24 - h, STRONGBOX)
    ledge(img, x - 1, y + 24, 26)
    return y + 31


def floor_brazier(img, cx, floor):
    """The lit brazier on the floor (motif ``brazier``) with pooled ember light."""
    w, h = icons.motif_size('brazier')
    x, y = cx - w // 2, floor - h
    icons.draw_motif(img, 'brazier', x, y)
    # extra flame tongues for a strongly lit brazier
    P.sprite(img, x + 3, y - 2, ['..F..', '.fFf.'])
    P.glow(img, cx, y, 14, 'ember')
    P.glow(img, cx, y - 1, 6, 'ember')
    icons.draw_motif(img, 'brazier', x, y)
    P.sprite(img, x + 3, y - 2, ['..F..', '.fFf.'])


def lantern_on_chain(img, cx, y0, y1, seed):
    P.chain(img, cx, y0, cx, y1 - 1, seed=seed)
    w, h = icons.motif_size('lantern')
    icons.draw_motif(img, 'lantern', cx - w // 2, y1)
    P.glow(img, cx, y1 + 5, 12, 'ember')
    icons.draw_motif(img, 'lantern', cx - w // 2, y1)
    return y1 + h


def stack(top, bottom, heights):
    """Vertical positions for blocks of ``heights`` spread evenly in
    [top, bottom): equal gaps before, between and after."""
    free = (bottom - top) - sum(heights)
    gap = free / (len(heights) + 1)
    out, y = [], top + gap
    for h in heights:
        out.append(int(round(y)))
        y += h + gap
    return out


def choose(room, required, optional, min_gap=6):
    """Blocks to stack: the required ones plus as many optional ones (in
    priority order) as the room allows with at least ``min_gap`` air."""
    chosen = list(required)
    for name, h in optional:
        trial = chosen + [(name, h)]
        if sum(b for _, b in trial) + min_gap * (len(trial) + 1) <= room:
            chosen = trial
    return chosen


def paint_frame(key, seed):
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, a.id, seed=seed)
    H, W = a.h, a.w
    lp, rp = a.left_panel, a.right_panel
    select = is_select(key)
    floor = H - 9                 # the floor line just above the bottom strip
    tall = H - 148                # 0 .. 90 extra rows over the chest_1 frame

    # --- left panel: the one great vault door ------------------------------
    dw = 25
    dh = 64 + round(tall * 0.36)
    dx = lp.x + 8
    dy = floor - 5 - dh
    vault_door(img, dx, dy, dw, dh, seed, locked=select)
    threshold(img, dx - 5, dy + dh, dw + 10)
    portal_top = dy - 8
    candle_on(img, dx - 3, portal_top, 4, seed, glow=9)
    candle_on(img, dx + dw, portal_top, 5, seed + 1, glow=9)
    lcx = lp.x + 20
    top, bottom = 9, portal_top - 11
    blocks = choose(bottom - top, [('lantern', 22)], [('ledge', 16), ('niche', 31)])
    ys = stack(top, bottom, [h for _, h in blocks])
    for (name, h), yy in zip(blocks, ys):
        if name == 'lantern':
            lantern_on_chain(img, lcx, 3, yy + 12, seed + 2)
        elif name == 'ledge':
            ly = yy + 11
            ledge(img, lp.x + 6, ly, 28)
            icons.draw_motif(img, 'ledger', lp.x + 8, ly - 11)
            icons.draw_motif(img, 'coin_stack', lp.x + 24, ly - 8)
            P.moss_tuft(img, lp.x + 9, ly + 5, 4, seed=seed + 3)
        elif name == 'niche':
            niche_strongbox(img, lcx, yy, seed + 4)
    P.crack(img, lp.x + 34, portal_top - 14, 6, seed=seed, colour=STONE[0], light=STONE[3])

    # --- right panel: guild banner, locks and keys, candles ---------------
    rcx = rp.x + 19
    bw = 19 if tall < 54 else 21
    bh = 30 + tall // 4
    bx = rcx - bw // 2
    by = 15
    P.chain(img, bx + 1, 3, bx + 1, by - 2, seed=seed + 4, shadow=None)
    P.chain(img, bx + bw - 2, 3, bx + bw - 2, by - 2, seed=seed + 5, shadow=None)
    P.banner(img, bx, by, bw, bh, MOSS, seed, emblem=None)
    guild_crest(img, rcx - 6, by + 4 + max(0, (bh - 30) // 3))
    top, bottom = by + bh + 2, floor - 1
    if select:
        required = [('keys', 28), ('padlock', 25), ('ledge', 15)]
        optional = [('sconce', 16), ('crate', 12), ('gargoyle', 18)]
    else:
        bw_, bh_ = icons.motif_size('brazier')
        required = [('padlock', 28), ('ledge', 15), ('brazier', bh_ + 2)]
        optional = [('sconce', 16), ('gargoyle', 18)]
    blocks = choose(bottom - top, required, optional)
    # floor pieces stand on the floor; the rest share the wall above them
    floor_blocks = [b for b in blocks if b[0] in ('crate', 'brazier')]
    wall_blocks = [b for b in blocks if b[0] not in ('crate', 'brazier')]
    order = ['sconce', 'keys', 'padlock', 'gargoyle', 'ledge'] if select else ['padlock', 'sconce', 'gargoyle', 'ledge']
    wall_blocks.sort(key=lambda b: order.index(b[0]))
    wall_bottom = bottom - sum(h for _, h in floor_blocks) - (2 if floor_blocks else 0)
    ys = stack(top, wall_bottom, [h for _, h in wall_blocks])
    for (name, h), yy in zip(wall_blocks, ys):
        if name == 'keys':
            key_ring(img, rcx - 4, yy, seed)
        elif name == 'padlock' and select:
            hung_padlock(img, rcx + 7, yy, yy + 10, seed + 6)
        elif name == 'padlock':
            open_padlock(img, rcx + 2, yy, yy + 10, seed + 6)
        elif name == 'sconce':
            sconce(img, rcx, yy, seed + 12)
        elif name == 'gargoyle':
            corbel(img, rcx, yy, seed + 13)
        elif name == 'ledge':
            ly = yy + 10
            ledge(img, rp.x + 5, ly, 29)
            if select:
                candle_on(img, rp.x + 9, ly, 6, seed + 7, glow=10)
                candle_on(img, rp.x + 30, ly, 4, seed + 8, glow=0)
                icons.draw_motif(img, 'coin_stack', rp.x + 17, ly - 8)
            else:
                candle_on(img, rp.x + 9, ly, 6, seed + 7, glow=10)
                icons.draw_motif(img, 'ledger', rp.x + 17, ly - 11)
            P.moss_tuft(img, rp.x + 22, ly + 5, 5, seed=seed + 9)
    names = [n for n, _ in blocks]
    if not select:
        floor_brazier(img, rcx, floor)
    elif 'crate' in names:
        cw, ch = icons.motif_size('crate')
        icons.draw_motif(img, 'crate', rcx - cw // 2 + 4, floor - ch)
        icons.draw_motif(img, 'bone', rp.x + 4, floor - 5)
    else:
        icons.draw_motif(img, 'bone', rp.x + 4, floor - 5)
    if tall >= 36:
        P.crack(img, rp.x + 34, top + 6, 8, seed=seed + 10, colour=STONE[0], light=STONE[3])

    # --- top strip: chains from the corners to the plaque ------------------
    P.chain(img, 12, 4, W // 2 - 22, 4, sag=2, seed=seed + 11)
    P.chain(img, W // 2 + 21, 4, W - 13, 4, sag=2, seed=seed + 12)
    # --- bottom strip: chains swagged between gold rivets, a fleur ---------
    for x0, x1 in ((46, 120), (136, 209)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3)
        P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 125, H - 7, 'fleur')

    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', type=Path, default=None,
                    help='textures root to write into (default: pack-source/assets/quasar_gui/textures)')
    args = ap.parse_args(argv)
    root = args.out_root or geo.TEXTURES
    for key in args.skin or SKINS:
        s = geo.skin(key)
        seed = SEEDS[key]
        bg = paint_background(key, seed)
        assert bg.size == (s.width, s.height) and bg.mode == 'RGBA'
        p1 = C.save_png(bg, Path(root) / 'menu' / f'{key}.png')
        a = s.layer()
        fr = paint_frame(key, seed)
        assert fr.size == (a.w, a.h) and fr.mode == 'RGBA'
        p2 = C.save_png(fr, Path(root) / 'frames' / key / f'{a.id}.png')
        print('WROTE', p1)
        print('WROTE', p2)


if __name__ == '__main__':
    main()
