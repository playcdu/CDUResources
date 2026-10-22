#!/usr/bin/env python3
"""Soulrend painter "shopconfig": the eight chest-shop configuration skins.

    python tools/soulrend/paint_shopconfig.py                 # all eight -> pack-source
    python tools/soulrend/paint_shopconfig.py --skin chest_shop_buy
    python tools/soulrend/paint_shopconfig.py --out-root DIR  # DIR laid out like textures/

Skins: chest_shop_settings, chest_shop_buy, chest_shop_sell,
chest_shop_upgrade, chest_shop_upgrade_confirm, chest_shop_upgrade_disabled,
chest_shop_listing_enabled, chest_shop_listing_disabled (backgrounds, all 71
button regions in six states, outer frames).

Family identity (CHEST SHOP): a merchant's stall under a stone arch. Iron-
banded crates, an iron lantern, a hanging shop sign with a wordless scales
emblem, burlap sacks, a striped stall awning. Every scene prop sits in the
static protected cells (on a counter, a shelf or under an arch, straddling
cell seams) or in the frame's side panels; nothing enters a well clearance or
the vellum text bands. Deterministic: fixed seeds, no clock.

Licence: MIT (tooling); the artwork it paints is CC0-1.0.
"""
from __future__ import annotations

import argparse
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
import lettering as L  # noqa: E402
import primitives as P  # noqa: E402
from palette import EMBER, GOLD, INK, IRON, MOSS, STONE, UMBER, VELLUM  # noqa: E402

SKINS = (
    'chest_shop_settings', 'chest_shop_buy', 'chest_shop_sell',
    'chest_shop_upgrade', 'chest_shop_upgrade_confirm', 'chest_shop_upgrade_disabled',
    'chest_shop_listing_enabled', 'chest_shop_listing_disabled',
)
SEEDS = {k: 401 + 17 * i for i, k in enumerate(SKINS)}

# Mood of each skin's scene: lit (ordinary ember lantern light), warm (extra
# candlelight), cold (unlit, cobwebbed, desaturated accents).
MOOD = {
    'chest_shop_settings': 'lit', 'chest_shop_buy': 'lit', 'chest_shop_sell': 'lit',
    'chest_shop_upgrade': 'lit', 'chest_shop_upgrade_confirm': 'warm',
    'chest_shop_upgrade_disabled': 'cold',
    'chest_shop_listing_enabled': 'lit', 'chest_shop_listing_disabled': 'cold',
}

# desaturated stand-ins for the warm ramps on cold scenes
COLD_WOOD = [INK[2], IRON[0], IRON[1], IRON[2]]
DIM_WOOD = [UMBER[0], UMBER[0], UMBER[1], UMBER[2]]
# pale crate wood for props standing in a dark recess
PALE_WOOD = [UMBER[1], UMBER[2], UMBER[3], VELLUM[0]]

# ---------------------------------------------------------------------------
# Small original sprites (shared key primitives.SK)
# ---------------------------------------------------------------------------

# burlap sack tied at the neck with twine
SACK = [
    '...oo....',
    '..ow3o...',
    '...oho...',
    '..owvvo..',
    '.owvvvvo.',
    'owvvwvv3o',
    'owvvvvv3o',
    'ow3vvv33o',
    '.oOOOOOO.',
]
# a slumped sack lying on its side
SACK_LOW = [
    '...ooooo...',
    '.oowvvvvoo.',
    'owvvvwvvv3o',
    'owvvvvvv33o',
    'ow3vvv3333h',
    '.oOOOOOOOoh',
]
# small leather coin pouch with a gold drawstring and a coin at its foot
POUCH = [
    '..o..o..',
    '..ohho..',
    '...oo...',
    '..o23o..',
    '.o3222o.',
    'o322221o',
    'o322211o',
    'o221110oo',
    '.oooooohHo',
    '.......ogo',
]
# a hanging shop sign emblem: tarnished-gold balance scales (wordless)
SCALES_EMBLEM = [
    '....H....',
    '.hhhHhhh.',
    '.h..h..h.',
    'h.h.h.h.h',
    'ggg.h.ggg',
    '...hHh...',
]
# iron hook on a wall plate
HOOK = ['oo', 'cd', 'cb', '.c', 'cb', 'oo']
# hammer lying flat (head left)
HAMMER_FLAT = [
    'ooo.......',
    'dcbooooooo',
    'cba3222221o',
    'oaaoooooooo',
]
# tongs lying flat
TONGS_FLAT = [
    'oo.......o',
    'cbbooo.oc.',
    '..obbbcc..',
    'ab.ooo.oa.',
    'oo.......o',
]
# corner cobweb (top-left form)
COBWEB = [
    'cwcccc',
    'w.c.c.',
    'cc.c..',
    'c.c...',
    'cc....',
    'c.....',
]
# iron padlock
PADLOCK = [
    '.ooo.',
    'oc.co',
    'ob.bo',
    'ocdco',
    'obOao',
    'oaaao',
    '.ooo.',
]
# an iron-hooped barrel
BARREL = [
    '.ooooooooo.',
    'o332222221o',
    'oddcccccbao',
    'o332222210o',
    'o322222210o',
    'o322222210o',
    'oddcccccbao',
    'o322222210o',
    'o322222210o',
    'o222222110o',
    'oddcccccbao',
    'o221111100o',
    '.OOOOOOOOO.',
]
# a coil of rope on a peg
ROPE = [
    '...oo...',
    '..obbo..',
    '.ovvvvo.',
    'ov3oo3vo',
    'ovo..ovo',
    'ov3oo3vo',
    '.ovvvvo.',
    '..oooo..',
]
# closed tool chest: arched iron handle, iron corner caps, brass latch
TOOLCHEST = [
    '.....ooooooo.....',
    '....oc.....bo....',
    '....oc.....ao....',
    'ooooooooooooooooo',
    'odc33333333333bao',
    'oc2222222222222ao',
    'ooooooooHoooooooo',
    'oc2222222gh22221o',
    'o322222222222221o',
    'odc22222222222bao',
    'OOOOOOOOOOOOOOOOO',
]
# a hammer lying flat on a counter, head right
HAMMER_LOW = [
    '.......oooo',
    'ooooooodccbo',
    'o3322221bbao',
    'ooooooooooo.',
]
# a tall wall lantern hung from a bracket: peaked iron hood, ember glass
# with a flame, iron base and a drop finial (13 rows; taller than wide, so it
# never reads as the squat lantern item)
WALL_LANTERN = [
    '...o...',
    '..odo..',
    '.odcbo.',
    'odccbao',
    'ooooooO',
    'ocfFfaO',
    'ocFFfaO',
    'ocfFeaO',
    'obffeaO',
    'ooooooO',
    '.obbaO.',
    '..oaO..',
    '...O...',
]
# the iron lantern, unlit: glass dark, no flame
LANTERN_UNLIT_KEY = {'F': IRON[1], 'f': INK[2], 'e': INK[2]}


def sprite(img, x, y, rows, **kw):
    P.sprite(img, x, y, rows, **kw)
    return P.sprite_size(rows)


# ---------------------------------------------------------------------------
# Scene helpers (painted on local canvases, then pasted into place)
# ---------------------------------------------------------------------------

def crate(img, x, y, w, h, ramp=UMBER, seed=0, bands=True, lid=False):
    """An iron-banded wooden crate: ink outline heavy bottom/right, vertical
    planks with ramp[1] seams, ramp[3] lit top row, two iron bands with lit
    rivets (or one on small crates), a diagonal brace on wide faces."""
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=0, heavy='br', fill_colour=ramp[2])
    P.hline(img, x + 1, x + w - 2, y + 1, ramp[3])
    P.vline(img, x + 1, y + 2, y + h - 2, ramp[3])
    P.hline(img, x + 1, x + w - 2, y + h - 2, ramp[1])
    for px in range(x + 4, x + w - 2, 4):
        P.vline(img, px, y + 2, y + h - 3, ramp[1])
        if px + 1 < x + w - 2:
            P.vline(img, px + 1, y + 2, y + h - 3, ramp[3])
    if w >= 10 and h >= 8 and not bands:
        P.line(img, x + 2, y + h - 3, x + w - 3, y + 2, ramp[1])
    if bands:
        rows = (y + 2, y + h - 4) if h >= 10 else (y + h // 2 - 1,)
        for by in rows:
            P.hline(img, x + 1, x + w - 2, by, IRON[2])
            P.put(img, x + 1, by, IRON[3]); P.put(img, x + w - 2, by, IRON[0])
            P.put(img, x + 2, by, IRON[3]) if w >= 8 else None
            P.put(img, x + w - 3, by, IRON[3]) if w >= 8 else None
    if lid:
        P.hline(img, x - 1, x + w, y, 'ink_1')
        P.hline(img, x, x + w - 1, y - 1, ramp[3])
        P.hline(img, x - 1, x + w, y - 2, 'ink_1')


def stall_alcove(img, box, seed, wall=STONE, interior=UMBER[0], arch=True, lit=True):
    """A stone stall front filling ``box``: masonry jambs and a segmental arch
    of voussoirs over a dark recess. Returns the interior Rect tuple."""
    x, y, w, h = box
    P.stone_blocks(img, box, seed, wall, course=6, moss=0.06)
    jamb = 4
    ix, iw = x + jamb, w - 2 * jamb
    if not arch:
        top = y + 2
        P.fill(img, (ix, top, iw, h - 2), interior)
        P.hline(img, ix - 1, ix + iw, top - 1, 'ink_1')
        P.vline(img, ix - 1, top, y + h - 1, 'ink_1')
        P.vline(img, ix + iw, top, y + h - 1, 'ink_0')
        P.hline(img, ix, ix + iw - 1, top, INK[1])
        return (ix, top, iw, y + h - top)
    # segmental arch over the recess: the opening rises 5 px at the crown;
    # a ring of voussoirs 3 px deep (lit stone_3 intrados, alternating
    # blocks, ink extrados) springs from the jambs
    rise_max = 5
    spring = y + 8                       # first row of the straight jambs
    span = iw
    tops = []
    for i in range(span):
        t = (i - (span - 1) / 2) / ((span - 1) / 2)
        tops.append(spring - int(round(rise_max * (1 - t * t))))
    P.fill(img, (ix, spring, iw, y + h - spring), interior)
    for i, ty in enumerate(tops):
        cx = ix + i
        for yy in range(ty, spring):
            P.put(img, cx, yy, interior)
        seg = ((i + 2) // 5) % 2
        joint = (i + 2) % 5 == 0
        P.put(img, cx, ty - 1, wall[3])                                    # lit intrados
        P.put(img, cx, ty - 2, wall[0] if joint else (wall[2] if seg else wall[1]))
        P.put(img, cx, ty - 3, wall[0] if joint else (wall[2] if seg else wall[1]))
        P.put(img, cx, ty - 4, 'ink_1')                                    # extrados
        P.put(img, cx, ty, INK[1])                                          # arch shadow
    # jambs: dressed stone with an ink reveal
    for jx in (x + 1, x + w - jamb):
        P.fill(img, (jx, spring - 3, jamb - 1, y + h - spring + 3), wall[2])
        P.vline(img, jx, spring - 3, y + h - 1, wall[3])
        for yy in range(spring + 2, y + h - 1, 6):
            P.hline(img, jx, jx + jamb - 2, yy, wall[0])
    P.vline(img, ix - 1, spring - 3, y + h - 1, 'ink_1')
    P.vline(img, ix + iw, spring - 3, y + h - 1, 'ink_0')
    P.vline(img, ix, spring, y + h - 1, INK[1])
    # keystone
    kx = ix + iw // 2
    P.sprite(img, kx - 2, tops[iw // 2] - 5, ['ooooo', 'oqqpo', 'oqppo', '.opo.', '..o..'])
    return (ix, tops[iw // 2], iw, y + h - tops[iw // 2])


def counter(img, x, y, w, h, ramp=UMBER, seed=0):
    """A heavy wooden counter: lit top plank, a front of vertical boards, an
    iron strap along the lip."""
    P.fill(img, (x, y, w, h), ramp[1])
    P.hline(img, x, x + w - 1, y, 'ink_1')
    P.hline(img, x, x + w - 1, y + 1, ramp[3])
    P.hline(img, x, x + w - 1, y + 2, ramp[2])
    P.hline(img, x, x + w - 1, y + 3, 'ink_1')
    r = P._rng(seed, 'counter', x, y)
    for px in range(x + r.randint(2, 5), x + w, r.randint(5, 7)):
        P.vline(img, px, y + 4, y + h - 1, ramp[0])
        P.put(img, px + 1, y + 4, ramp[2])
    if h >= 7:
        P.hline(img, x, x + w - 1, y + 5, IRON[1])
        for px in range(x + 2, x + w, 9):
            P.put(img, px, y + 5, IRON[3])
    P.hline(img, x, x + w - 1, y + h - 1, INK[0])


def lantern(img, x, y, lit=True, chain_to=None, seed=0):
    """The iron lantern motif hung at (x, y) (top-left). Lit: ember glass and
    a dithered pool of light; unlit: dark glass. Returns the glass centre."""
    if chain_to is not None:
        P.chain(img, x + 4, chain_to, x + 4, y, seed=seed, shadow=None)
    if lit:
        icons.draw_motif(img, 'lantern', x, y)
    else:
        P.sprite(img, x, y, icons.MOTIFS['lantern'], LANTERN_UNLIT_KEY)
    return x + 4, y + 5


def wall_bracket(img, x, y, length, right=True):
    """Wrought-iron wall bracket: a wall plate, an arm and a scroll brace."""
    d = 1 if right else -1
    P.sprite(img, x - (0 if right else 1), y - 1, ['oo', 'cb', 'cb', 'ba', 'oo'])
    for i in range(1, length):
        P.put(img, x + d * (1 + i), y, IRON[2])
        P.put(img, x + d * (1 + i), y - 1, 'ink_1')
        P.put(img, x + d * (1 + i), y + 1, 'ink_0')
    P.put(img, x + d * (length + 1), y, 'ink_1')
    for k in range(1, min(5, length - 1)):
        P.put(img, x + d * (1 + k), y + 1 + (k - 1) // 1 if k < 3 else y + 3, IRON[1])
    P.line(img, x + d * 2, y + 3, x + d * min(length - 1, 5), y + 1, IRON[1])


def shop_sign(img, x, y, w, h, seed=0, ramp=UMBER, emblem=True, cold=False):
    """A hanging wooden shop sign with iron corner straps and a wordless
    tarnished-gold scales emblem."""
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=1, heavy='br', fill_colour=ramp[2])
    P.hline(img, x + 1, x + w - 2, y + 1, ramp[3])
    P.hline(img, x + 2, x + w - 3, y + h // 2, ramp[1])          # plank seam
    P.hline(img, x + 1, x + w - 2, y + h - 2, ramp[1])
    for (cx, cy, fx, fy) in ((x + 1, y + 1, False, False), (x + w - 4, y + 1, True, False),
                             (x + 1, y + h - 4, False, True), (x + w - 4, y + h - 4, True, True)):
        P.sprite(img, cx, cy, ['ccb', 'c..', 'b..'], flip_x=fx, flip_y=fy)
    if emblem:
        ew, eh = P.sprite_size(SCALES_EMBLEM)
        key = {'H': IRON[3], 'h': IRON[2], 'g': IRON[1]} if cold else None
        P.sprite(img, x + (w - ew) // 2, y + (h - eh) // 2, SCALES_EMBLEM, key)


def hanging_sign(img, x, y, w, h, top, seed=0, ramp=UMBER, cold=False):
    """Shop sign hung on two short chains from row ``top``."""
    for cx in (x + 3, x + w - 4):
        P.chain(img, cx, top, cx, y - 1, seed=seed + cx, shadow=None)
    shop_sign(img, x, y, w, h, seed, ramp, cold=cold)


def toolbox(img, x, y, ramp=UMBER):
    """An open wooden toolbox: arched iron handle, hammer and tongs inside."""
    w, h = 17, 7
    # tools poking out (behind the front board)
    P.sprite(img, x + 2, y - 4, ['oooo', 'dccb', 'obao', '.o3o', '.o2o'])          # hammer head + haft
    P.sprite(img, x + 11, y - 5, ['o.o', 'coc', '.c.', '.b.', '.b.'])             # tongs jaws
    # handle
    P.hline(img, x + 6, x + 10, y - 6, 'ink_1')
    P.sprite(img, x + 5, y - 5, ['o.....o', 'c.....b', 'c.....b', 'c.....b'])
    P.hline(img, x + 6, x + 10, y - 5, IRON[2])
    # box
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=0, heavy='br', fill_colour=ramp[2])
    P.hline(img, x + 1, x + w - 2, y + 1, ramp[3])
    P.hline(img, x + 1, x + w - 2, y + h - 2, ramp[1])
    P.hline(img, x + 1, x + w - 2, y + 3, IRON[1])
    P.put(img, x + 2, y + 3, IRON[3]); P.put(img, x + w - 3, y + 3, IRON[3])
    P.sprite(img, x + w // 2 - 1, y + 2, ['oho', 'ogo'])                         # brass latch


def cobweb(img, x, y, corner='tl'):
    P.sprite(img, x, y, COBWEB, flip_x='r' in corner, flip_y='b' in corner)


def candle_on(img, x, y, height, lit, seed):
    fx, fy = P.candle(img, x, y, height=height, lit=lit, holder='iron', seed=seed)
    return fx, fy


def lamp_glow(img, cx, cy, r):
    """Ember light pooling round a flame or lantern glass: the shared
    ``primitives.glow`` bands (solid step-lighter core, checker, sparse
    Bayer rim) with the warm stipple on the darkest pixels kept to a light
    sprinkle so a small lamp never wears a dotted ring."""
    from palette import luminance, ramp_of, step
    base = img.copy()
    bpx = base.load()
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            if not (0 <= x < img.width and 0 <= y < img.height):
                continue
            p = bpx[x, y]
            if p[3] == 0 or (ramp_of(p) or ('', 0))[0] == 'ink':
                continue
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            b = P.BAYER4[y % 4][x % 4]
            if d2 <= (r // 2) ** 2 and luminance(p) < 60 and b < 2:
                P.put(img, x, y, EMBER[0])
            elif d2 <= (3 * r // 5) ** 2:
                P.put(img, x, y, step(p, 1))
            elif d2 <= (3 * r // 4) ** 2:
                if (x + y) % 2 == 0:
                    P.put(img, x, y, step(p, 1))
            elif d2 <= r * r:
                if b < 2:
                    P.put(img, x, y, step(p, 1))


def paste(dst, src, box):
    """Copy the opaque pixels of ``src`` cropped to ``box`` into ``dst``."""
    x, y, w, h = box
    tile = src.crop((x, y, x + w, y + h))
    dst.alpha_composite(tile, (x, y))


# ---------------------------------------------------------------------------
# Static scenes per screen (background coordinates)
# ---------------------------------------------------------------------------

def cell_box(slots):
    """Bounding box (x, y, w, h) of the 18 px cells of chest slots."""
    xs = [7 + 18 * (i % 9) for i in slots]
    ys = [17 + 18 * (i // 9) for i in slots]
    return (min(xs), min(ys), max(xs) + 18 - min(xs), max(ys) + 18 - min(ys))


def scene_settings(bg, key, seed):
    """Static centre of the shop settings: the stall under its arch, the shop
    sign hanging from the keystone, a counter carrying the toolbox, a lantern
    and a sack."""
    box = cell_box([12, 13, 14, 21, 22, 23])          # 61,35 54x36
    x, y, w, h = box
    layer = C.new(bg.width, bg.height)
    ix, iy, iw, ih = stall_alcove(layer, box, seed)
    # back wall of the recess: dark planks
    for px in range(ix + 3, ix + iw - 1, 6):
        P.vline(layer, px, iy + 1, y + h - 1, UMBER[1])
    # shop sign on chains from under the arch
    hanging_sign(layer, x + 15, iy + 3, 25, 11, iy, seed)
    # counter across the bottom
    counter(layer, ix, y + h - 9, iw, 9, seed=seed)
    ctop = y + h - 9
    sprite(layer, ix + 1, ctop - 10, TOOLCHEST)
    sprite(layer, ix + 17, ctop - 4, HAMMER_LOW)
    lx, ly = lantern(layer, ix + iw - 10, ctop - 9, lit=True)
    sprite(layer, ix + iw - 19, ctop - 8, SACK[:-1])
    lamp_glow(layer, lx, ly, 12)
    paste(bg, layer, box)


def scene_trade(bg, key, seed, buying):
    """Buy / sell: the counter in the three-cell gap (15-17) with the trade's
    props; slot 2 a wall lantern on its bracket; slot 20 sacks against the
    pillar foot."""
    layer = C.new(bg.width, bg.height)
    # --- counter strip 115,35 54x18 --------------------------------------
    box = cell_box([15, 16, 17])
    x, y, w, h = box
    ix, iy, iw, ih = stall_alcove(layer, box, seed, interior=UMBER[1], arch=False)
    for px in range(ix + 2, ix + iw - 1, 5):
        P.vline(layer, px, iy + 1, y + h - 1, UMBER[0])
    counter(layer, x, y + h - 6, w, 6, seed=seed)
    ctop = y + h - 6
    # a striped stall valance along the top of the opening
    awning(layer, ix, y + 1, iw, 3, seed=seed)
    if buying:
        # coin pouch and a coin stack by a candle; a crate being lowered in
        # on a rope sling from the awning bar, about to be set down
        sprite(layer, x + 5, ctop - 9, POUCH[1:])
        icons.draw_motif(layer, 'coin_stack', x + 15, ctop - 8)
        fx, fy = candle_on(layer, x + 25, ctop - 5, 3, True, seed)
        for (ax, bx2) in ((x + 37, x + 34), (x + 43, x + 46)):
            P.line(layer, ax, y + 5, bx2, ctop - 8, VELLUM[0])
        P.sprite(layer, x + 38, y + 5, ['ooooo', '.cdb.'])
        crate(layer, x + 33, ctop - 8, 15, 7, PALE_WOOD, seed=seed)
        lamp_glow(layer, fx, fy + 1, 7)
    else:
        # outgoing: a crate roped and sealed for carriage, pushed to the
        # counter's edge; an emptied pouch lies folded flat by the candle
        crate(layer, x + 28, ctop - 9, 14, 9, PALE_WOOD, seed=seed, bands=False)
        for ry in (ctop - 6, ctop - 3):
            P.hline(layer, x + 28, x + 41, ry, VELLUM[0])
        P.vline(layer, x + 34, ctop - 9, ctop - 1, VELLUM[0])
        P.sprite(layer, x + 33, ctop - 10, ['o.o'])
        P.sprite(layer, x + 40, ctop - 5, ['.o.', 'ost', 'oss', '.r.'])          # wax-sealed tag
        crate(layer, x + 43, ctop - 6, 8, 6, PALE_WOOD, seed=seed + 1)
        P.sprite(layer, x + 5, ctop - 3, ['.oooooo.', 'o3222hho', '.oooooo.'])
        fx, fy = candle_on(layer, x + 18, ctop - 5, 3, True, seed)
        lamp_glow(layer, fx, fy + 1, 7)
    paste(bg, layer, box)

    # --- slot 2: masonry pillar with a lantern on a bracket ------------------
    layer = C.new(bg.width, bg.height)
    box = cell_box([2])
    x, y, w, h = box
    P.stone_blocks(layer, box, seed + 3, STONE, course=6, moss=0.0)
    P.ink_outline(layer, box, 'ink_1', radius=0, heavy='br')
    # a tall bracket lantern (peaked iron hood, finial below; not the squat
    # cage of the lantern motif) hangs off-centre from the wall bracket and
    # throws a cast shadow down and right onto the masonry, so the cell reads
    # as a lit stretch of wall rather than an item icon in a framed slot; the
    # light pools only round the glass
    lamp_glow(layer, x + 12, y + 10, 6)
    wall_bracket(layer, x + 1, y + 3, 11)
    lx, ly = x + 9, y + 4
    for (i, j) in [(i, j) for j, row in enumerate(WALL_LANTERN) for i, ch in enumerate(row) if ch != '.']:
        sx, sy = lx + i + 1, ly + j + 1
        if x < sx < x + w - 1 and y < sy < y + h - 1:
            P.put(layer, sx, sy, INK[2])
    sprite(layer, lx, ly, WALL_LANTERN)
    paste(bg, layer, box)

    # --- slot 20: pillar foot with sacks slumped against it -----------------
    layer = C.new(bg.width, bg.height)
    box = cell_box([20])
    x, y, w, h = box
    P.stone_blocks(layer, box, seed + 4, STONE, course=6, moss=0.15)
    P.ink_outline(layer, box, 'ink_1', radius=0, heavy='br')
    P.hline(layer, x + 1, x + w - 2, y + h - 3, STONE[3])
    P.hline(layer, x + 1, x + w - 2, y + h - 2, STONE[0])
    if buying:
        sprite(layer, x + 1, y + h - 11, SACK)
        sprite(layer, x + 7, y + h - 8, SACK_LOW)
    else:
        sprite(layer, x + 8, y + h - 11, SACK)
        crate(layer, x + 1, y + h - 9, 8, 7, seed=seed + 5)
    paste(bg, layer, box)


def scene_upgrade(bg, key, seed, mood):
    """A three-tier iron shelf of crates (static strip 11-13 / 20-22). The
    confirm screen is lit by ember candlelight; the disabled one is cold,
    unlit and cobwebbed."""
    box = cell_box([11, 12, 13, 20, 21, 22])          # 43,35 54x36
    x, y, w, h = box
    cold = mood == 'cold'
    wood = COLD_WOOD if cold else PALE_WOOD
    layer = C.new(bg.width, bg.height)
    # back wall: dark boards
    P.fill(layer, box, UMBER[1] if not cold else IRON[0])
    for px in range(x + 2, x + w, 5):
        P.vline(layer, px, y, y + h - 1, UMBER[0] if not cold else INK[1])
    P.ink_outline(layer, box, 'ink_1', radius=0, heavy='br')
    # iron posts
    for px in (x + 1, x + w - 4):
        P.fill(layer, (px, y + 1, 3, h - 2), IRON[1])
        P.vline(layer, px, y + 1, y + h - 2, IRON[2])
        P.vline(layer, px + 2, y + 1, y + h - 2, IRON[0])
        for ry in range(y + 3, y + h - 2, 6):
            P.put(layer, px + 1, ry, IRON[3])
    # three shelves: boards at rows 12, 24, 36 (iron-edged planks)
    shelves = [y + 11, y + 23, y + 35]
    for sy in shelves:
        P.hline(layer, x + 1, x + w - 2, sy - 2, 'ink_1')
        P.hline(layer, x + 1, x + w - 2, sy - 1, IRON[2])
        P.hline(layer, x + 1, x + w - 2, sy, IRON[0])
        P.put(layer, x + 1, sy - 1, IRON[3])
    # tier 1 (top): one small crate; tier 2: two; tier 3: three (and a sack)
    crate(layer, x + 21, y + 3, 11, 6, wood, seed)
    crate(layer, x + 8, y + 13, 12, 8, wood, seed + 1)
    crate(layer, x + 30, y + 14, 11, 7, wood, seed + 2)
    crate(layer, x + 5, y + 24, 14, 9, wood, seed + 3)
    crate(layer, x + 20, y + 25, 13, 8, wood, seed + 4)
    crate(layer, x + 34, y + 26, 11, 7, wood, seed + 5)
    if not cold:
        P.sprite(layer, x + 41, y + 3, SACK[1:], {'v': VELLUM[0]})
    # candles and light
    lit = not cold
    pts = []
    pts.append(candle_on(layer, x + 9, y + 3, 5, lit, seed))
    pts.append(candle_on(layer, x + 45, y + 15, 4, lit, seed + 1))
    if mood == 'warm':
        pts.append(candle_on(layer, x + 35, y + 4, 4, True, seed + 2))
        pts.append(candle_on(layer, x + 47, y + 26, 5, True, seed + 3))
        for (fx, fy) in pts:
            lamp_glow(layer, fx, fy + 2, 9)
    elif lit:
        for (fx, fy) in pts:
            lamp_glow(layer, fx, fy + 2, 7)
    else:
        cobweb(layer, x + 4, y + 1, 'tl')
        cobweb(layer, x + w - 10, y + 1, 'tr')
        cobweb(layer, x + 4, y + 25, 'tl')
        P.put(layer, x + 26, y + 12, IRON[2]); P.put(layer, x + 26, y + 13, IRON[2])   # a dangling thread
    paste(bg, layer, box)


def scene_listing(bg, key, seed, enabled):
    """Static cells 36-38: the stall window. Enabled: shutters thrown open
    on warm light, the lantern lit. Disabled: shutters closed and barred,
    padlocked, the lantern cold."""
    box = cell_box([36, 37, 38])                      # 7,89 54x18
    x, y, w, h = box
    layer = C.new(bg.width, bg.height)
    P.stone_blocks(layer, box, seed, STONE, course=6, moss=0.08)
    P.ink_outline(layer, box, 'ink_1', radius=0, heavy='br')
    # window opening in the right two cells; its shutters straddle the seams
    wx, wy, ww, wh = x + 30, y + 3, 16, 13
    P.ink_outline(layer, (wx - 1, wy - 1, ww + 2, wh + 2), 'ink_1', radius=0)
    P.hline(layer, wx - 2, wx + ww + 1, wy + wh + 1, STONE[3])        # sill
    P.hline(layer, wx - 2, wx + ww + 1, wy + wh, STONE[2])
    if enabled:
        P.fill(layer, (wx, wy, ww, wh - 1), EMBER[0])
        P.fill(layer, (wx + 2, wy + 2, ww - 4, wh - 5), EMBER[1])
        P.fill(layer, (wx + 6, wy + 4, ww - 12, wh - 8), EMBER[2])
        P.vline(layer, wx + ww // 2, wy, wy + wh - 2, INK[1])            # mullion
        P.hline(layer, wx, wx + ww - 1, wy + wh // 2 - 1, INK[1])
        # shutters swung open against the wall
        for (sx, fx) in ((wx - 7, False), (wx + ww + 1, True)):
            P.ink_outline(layer, (sx, wy - 1, 6, wh + 1), 'ink_1', radius=0, heavy='br', fill_colour=UMBER[2])
            P.vline(layer, sx + (1 if not fx else 1), wy, wy + wh - 2, UMBER[3])
            P.vline(layer, sx + 3, wy, wy + wh - 2, UMBER[1])
            for hy in (wy + 1, wy + wh - 3):
                P.hline(layer, sx + 1, sx + 4, hy, IRON[2])
        lamp_glow(layer, wx + ww // 2, wy + wh // 2, 14)
    else:
        # closed shutters fill the window, an iron bar and padlock across
        P.fill(layer, (wx, wy, ww, wh), UMBER[1])
        for px in range(wx + 2, wx + ww, 3):
            P.vline(layer, px, wy, wy + wh - 1, UMBER[0])
        P.vline(layer, wx + ww // 2, wy, wy + wh - 1, INK[1])
        P.hline(layer, wx, wx + ww - 1, wy, UMBER[2])
        for hy in (wy + 2, wy + wh - 3):
            P.hline(layer, wx + 1, wx + ww - 2, hy, IRON[1])
        by = wy + wh // 2 - 1
        P.hline(layer, wx - 3, wx + ww + 2, by - 1, 'ink_1')
        P.hline(layer, wx - 3, wx + ww + 2, by, IRON[2])
        P.hline(layer, wx - 3, wx + ww + 2, by + 1, IRON[0])
        P.hline(layer, wx - 3, wx + ww + 2, by + 2, 'ink_0')
        sprite(layer, wx + ww // 2 - 2, by - 1, PADLOCK)
        cobweb(layer, x + w - 7, y + 1, 'tr')
    # the lantern hangs from a long wall bracket across the seam of cells 36
    # and 37 (never centred in one cell like an item icon)
    wall_bracket(layer, x + 1, y + 3, 17)
    lx, ly = lantern(layer, x + 14, y + 5, lit=enabled)
    if enabled:
        lamp_glow(layer, lx, ly, 8)
    paste(bg, layer, box)


SCENES = {
    'chest_shop_settings': lambda bg, k, s: scene_settings(bg, k, s),
    'chest_shop_buy': lambda bg, k, s: scene_trade(bg, k, s, True),
    'chest_shop_sell': lambda bg, k, s: scene_trade(bg, k, s, False),
    'chest_shop_upgrade': lambda bg, k, s: scene_upgrade(bg, k, s, 'lit'),
    'chest_shop_upgrade_confirm': lambda bg, k, s: scene_upgrade(bg, k, s, 'warm'),
    'chest_shop_upgrade_disabled': lambda bg, k, s: scene_upgrade(bg, k, s, 'cold'),
    'chest_shop_listing_enabled': lambda bg, k, s: scene_listing(bg, k, s, True),
    'chest_shop_listing_disabled': lambda bg, k, s: scene_listing(bg, k, s, False),
}


def paint_background(key):
    s = geo.skin(key)
    seed = SEEDS[key]
    bg = C.base_background(key, seed=seed)
    SCENES[key](bg, key, seed)
    H, W = s.height, s.width
    # under the hotbar: a gold flourish centred, a wax drip and a crack
    P.gold_filigree(bg, W // 2 - 5, H - 4, 'flourish')
    P.crack(bg, 24, H - 5, 3, seed=seed, direction='right', colour='umber_0', branch=False)
    P.crack(bg, W - 28, H - 5, 3, seed=seed + 1, direction='right', colour='umber_0', branch=False)
    C.finish_background(bg, key)
    return bg


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

TAG_IDS = ('preset_1', 'preset_2', 'preset_3', 'preset_4', 'tier_1', 'tier_2', 'tier_3',
           'sell_price', 'buy_price')


def _is_ink(p):
    """True for an opaque ink pixel."""
    return p[3] and tuple(p[:3]) in (INK[0], INK[1], INK[2])


def tag_face(img, b, seed):
    """A vellum merchant's tag: the left end clipped at 45 degrees, an iron
    eyelet with a twine loop; lettering to the right of the eyelet."""
    w, h = b.w, b.h
    P.vellum_strip(img, (0, 0, w, h), seed, outline='ink_1', deckle='tb', heavy='br')
    cut = 4
    for j in range(cut):
        for i in range(cut - j):
            img.putpixel((i, j), (0, 0, 0, 0))
            img.putpixel((i, h - 1 - j), (0, 0, 0, 0))
        P.put(img, cut - j, j, 'ink_1')
        P.put(img, cut - j, h - 1 - j, 'ink_0')
    P.vline(img, 0, cut, h - 1 - cut, 'ink_1')
    cy = h // 2 - 2
    P.sprite(img, 2, cy, ['.oo.', 'oc.d', 'ob.c', '.ba.'])
    P.put(img, 1, cy + 1, VELLUM[0]); P.put(img, 1, cy + 2, VELLUM[0])
    P.put(img, w - 3, h - 3, VELLUM[0])
    return (6, 2, w - 9, h - 4)            # centred between eyelet and rim


def plate_gem(img, b, seed):
    """An ember glass gem set in the top rim of a primary plate."""
    cx = b.w // 2
    P.sprite(img, cx - 2, 0, ['OeeO', 'OfFe', '.OO.'])


def plate_ends(img, b):
    """Small gold fleurs at either end of a wide primary plate."""
    yy = b.h // 2 - 2
    for xx in (6, b.w - 9):
        P.sprite(img, xx, yy, ['.h.', 'hHh', 'hHg', '.g.'])


def paint_one_button(key, b, seed):
    kind = C.button_kind(b)
    mood = MOOD[key]
    if b.id in TAG_IDS:
        img = C.new(b.w, b.h)
        box = tag_face(img, b, seed)
        C.letter(img, b, box, 'ink_0')
        # a descender (the y of Buy Price) hangs close to the deckled bottom
        # edge; where a deckle notch rises under it the pulse ring would run
        # right beneath the tail, so the cut is left straight under the
        # descender (the caps stay on the same rows as the neighbouring tags)
        tail = [x for (x, y) in C.label_pixels(C.label_layout(b, box)) if y >= b.h - 4]
        for x in range(min(tail, default=0) - 4, max(tail, default=-9) + 5):
            if img.getpixel((x, b.h - 1))[3] == 0:
                P.put(img, x, b.h - 1, 'ink_0')
                P.put(img, x, b.h - 2, VELLUM[1])
                if _is_ink(img.getpixel((x, b.h - 3))):
                    P.put(img, x, b.h - 3, VELLUM[2])
    elif kind == 'primary' and b.h > 36:
        # the tall Apply plate: an engraved stack of crates above the label
        img = C.new(b.w, b.h)
        box = C.primary_face(img, b.body.tuple(), seed)
        C.letter(img, b, box, 'gold_2', shadow='ink_0')
        cx = b.w // 2
        top = 8
        P.sprite(img, cx - 6, top, [
            '....hhhh....',
            '....hggh....',
            '....hhhh....',
            '.hhhhh.hhhhh',
            '.hg.gh.hg.gh',
            '.hhhhh.hhhhh',
        ])
        P.gold_filigree(img, cx - 5, top + 9, 'flourish')
        P.gold_filigree(img, cx - 5, b.h - 14, 'flourish')
        P.sprite(img, cx - 2, 0, ['OeeO', 'OfFe', '.OO.'])
    else:
        img = C.paint_button(key, b.id, seed=seed)
        if kind == 'primary':
            plate_gem(img, b, seed)
            if b.w >= 72:
                plate_ends(img, b)
        elif kind == 'danger':
            # frayed hem: the cloth's bottom edge loses a few threads
            r = P._rng(seed, 'fray', key, b.id)
            for xx in range(5, b.w - 5):
                if r.random() < 0.18:
                    img.putpixel((xx, b.h - 1), (0, 0, 0, 0))
                    P.put(img, xx, b.h - 2, 'ink_0')
        elif kind == 'info':
            # chisel-cut diamond rosettes at either end of the tablet
            yy = b.h // 2 - 1
            room = b.w - max(L.text_width(t, 'graven') for t in b.text_lines)
            for xx in ((4, b.w - 7) if room >= 20 else ()):
                P.sprite(img, xx, yy, ['.n.', 'n.p', '.p.'])
        elif kind == 'secondary' and b.h >= 36:
            # a gold flourish under the lettering of the tall notices
            P.gold_filigree(img, b.w // 2 - 5, b.h - 7, 'flourish')
    C.finish_button(img, key, b.id)
    return img


def paint_buttons(key, root=None):
    s = geo.skin(key)
    seed = SEEDS[key]
    for i, b in enumerate(s.buttons):
        normal = paint_one_button(key, b, seed + i)
        states = C.button_states(normal, key, b.id)   # shared transforms (crack clearance built in)
        C.save_button_states(states, key, b.id, root=root)


# ---------------------------------------------------------------------------
# Frames: the stall's side panels
# ---------------------------------------------------------------------------

def awning(img, x, y, w, h, cold=False, seed=0):
    """A striped stall awning on an iron rod with a scalloped hem."""
    a, b = (IRON[1], IRON[0]) if cold else (EMBER[0], UMBER[2])
    hi = IRON[2] if cold else EMBER[1]
    for i in range(w):
        stripe = (i // 4) % 2
        col = a if stripe == 0 else b
        depth = h - (1 if (i % 4) in (0, 3) else 0)
        for j in range(depth):
            P.put(img, x + i, y + j, col)
        P.put(img, x + i, y + depth, 'ink_0')
        if stripe == 0:
            P.put(img, x + i, y + 1, hi)
    P.hline(img, x - 1, x + w, y - 1, IRON[2])
    P.hline(img, x - 1, x + w, y - 2, 'ink_1')
    P.put(img, x - 2, y - 1, 'ink_1'); P.put(img, x + w + 1, y - 1, 'ink_1')
    P.vline(img, x - 1, y, y + h, 'ink_1')
    P.vline(img, x + w, y, y + h, 'ink_0')


def ledge(img, x, y, w, seed):
    """A short carved stone ledge on two iron brackets."""
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0)
    for bx in (x + 2, x + w - 4):
        P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


def paint_frame(key):
    s = geo.skin(key)
    a = s.layer()
    seed = SEEDS[key]
    mood = MOOD[key]
    cold = mood == 'cold'
    lit = not cold
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    L0, R0 = lp.x, rp.x

    # ---- left panel: the shop sign on its bracket, the lantern in an arch,
    #      sacks on a ledge, the stall's leather banner, crates and a barrel
    #      stacked at the foot -------------------------------------------
    wood = COLD_WOOD if cold else UMBER
    wall_bracket(img, L0 + 3, 12, 30)
    hanging_sign(img, L0 + 9, 18, 24, 13, 13, seed, ramp=wood, cold=cold)
    P.arch_niche(img, (L0 + 9, 42, 22, 34), seed=seed, interior='umber_0' if lit else 'ink_1')
    lx, ly = lantern(img, L0 + 16, 55, lit=lit, chain_to=45, seed=seed)
    if lit:
        lamp_glow(img, lx, ly, 13 if mood != 'warm' else 16)
    else:
        cobweb(img, L0 + 12, 49, 'tl')
    ledge(img, L0 + 7, 79, 26, seed)
    sprite(img, L0 + 10, 70, SACK)
    sprite(img, L0 + 20, 73, ROPE[:-1] + ['..oooo..'])
    P.moss_tuft(img, L0 + 12, 84, 4, seed=seed)
    # leather stall banner with a gold scales emblem
    bramp = [IRON[0], IRON[1], IRON[2]] if cold else [UMBER[1], UMBER[2], UMBER[3]]
    btrim = IRON if cold else GOLD
    P.banner(img, L0 + 13, 97, 14, 34, bramp, seed, emblem=None, trim=btrim)
    ckey = {'H': IRON[3], 'h': IRON[2], 'g': IRON[1]} if cold else None
    P.sprite(img, L0 + 15, 106, SCALES_EMBLEM[1:], ckey)
    P.sprite(img, L0 + 17, 114, ['..h..', '.hHh.', '..g..'], ckey)
    base = H - 12
    crate(img, L0 + 4, base - 13, 16, 13, wood, seed)
    sprite(img, L0 + 22, base - 13, BARREL)
    crate(img, L0 + 7, base - 23, 12, 10, wood, seed + 2)
    P.crack(img, L0 + 31, 140, 8, seed=seed, colour=STONE[0], light=STONE[3])
    if key == 'chest_shop_upgrade_disabled':
        icons.draw_motif(img, 'bone', L0 + 22, base - 20)
        cobweb(img, L0 + 4, base - 23, 'tl')

    # ---- right panel: the striped awning, a lantern under it, a shelf of
    #      wares that tells which screen this is, a mid-wall story, crates
    #      and a sack at the foot -----------------------------------------
    awning(img, R0 + 4, 11, 32, 8, cold=cold, seed=seed)
    P.chain(img, R0 + 20, 21, R0 + 20, 27, seed=seed + 2, shadow=None)
    rlx, rly = lantern(img, R0 + 16, 28, lit=lit)
    if lit:
        lamp_glow(img, rlx, rly, 12)
    shelf_y = 66
    ledge(img, R0 + 4, shelf_y, 32, seed + 1)
    mid = 'board'
    if key == 'chest_shop_settings':
        # the stall's tools on hooks over the shelf, the tool chest on it
        for hx in (R0 + 11, R0 + 27):
            sprite(img, hx, 42, ['oo', 'cd', 'ob', '.c', 'co'])
        icons.draw_motif(img, 'hammer', R0 + 8, 47)
        icons.draw_motif(img, 'tongs', R0 + 26, 47)
        sprite(img, R0 + 12, shelf_y - 11, TOOLCHEST)
    elif key == 'chest_shop_buy':
        sprite(img, R0 + 6, shelf_y - 10, POUCH)
        icons.draw_motif(img, 'coin_stack', R0 + 16, shelf_y - 8)
        icons.draw_motif(img, 'scales', R0 + 23, shelf_y - 11)
        # an incoming crate lowered on the hoist chain
        mid = None
        P.chain(img, R0 + 20, 74, R0 + 20, 92, seed=seed + 5, shadow=None)
        P.sprite(img, R0 + 17, 93, ['..o..', '.oco.', 'oc.bo', 'o...o'])
        P.line(img, R0 + 18, 96, R0 + 13, 100, VELLUM[0])
        P.line(img, R0 + 22, 96, R0 + 27, 100, VELLUM[0])
        crate(img, R0 + 11, 100, 18, 12, wood, seed + 6)
    elif key == 'chest_shop_sell':
        icons.draw_motif(img, 'ledger', R0 + 5, shelf_y - 11)
        icons.draw_motif(img, 'scales', R0 + 21, shelf_y - 11)
        # an outgoing crate roped onto a barrow, handles toward the door
        mid = None
        crate(img, R0 + 8, 92, 18, 12, wood, seed + 6, bands=False)
        for ry in (95, 99):
            P.hline(img, R0 + 8, R0 + 25, ry, VELLUM[0])
        P.vline(img, R0 + 16, 92, 103, VELLUM[0])
        P.sprite(img, R0 + 15, 90, ['o.o', '.v.'])
        P.hline(img, R0 + 5, R0 + 30, 104, UMBER[3])
        P.hline(img, R0 + 5, R0 + 30, 105, UMBER[1])
        P.hline(img, R0 + 5, R0 + 30, 106, 'ink_0')
        P.line(img, R0 + 30, 104, R0 + 35, 98, UMBER[2])
        P.line(img, R0 + 31, 104, R0 + 36, 98, 'ink_1')
        P.sprite(img, R0 + 7, 105, ['.ooo.', 'ocdbo', 'od.ao', 'obaao', '.ooo.'])
        P.vline(img, R0 + 27, 107, 110, IRON[1])
    elif key.startswith('chest_shop_upgrade'):
        icons.draw_motif(img, 'anvil', R0 + 4, shelf_y - 10)
        if mood == 'warm':
            for i, cx in enumerate((R0 + 21, R0 + 26, R0 + 31)):
                fx, fy = P.candle(img, cx, shelf_y - 8 + (i % 2) * 2, height=6 - (i % 2) * 2,
                                  lit=True, holder=None, seed=cx)
                lamp_glow(img, fx, fy + 2, 10)
        elif cold:
            for cx in (R0 + 22, R0 + 29):
                P.candle(img, cx, shelf_y - 5, height=3, lit=False, holder=None, seed=cx)
            cobweb(img, R0 + 30, shelf_y - 14, 'tr')
        else:
            icons.draw_motif(img, 'coin_stack', R0 + 19, shelf_y - 8)
            fx, fy = P.candle(img, R0 + 30, shelf_y - 7, height=5, lit=True, holder='iron', seed=seed)
            lamp_glow(img, fx, fy + 2, 9)
    elif key == 'chest_shop_listing_enabled':
        icons.draw_motif(img, 'ledger', R0 + 5, shelf_y - 11)
        icons.draw_motif(img, 'coin_stack', R0 + 19, shelf_y - 8)
        fx, fy = P.candle(img, R0 + 30, shelf_y - 7, height=5, lit=True, holder='iron', seed=seed)
        lamp_glow(img, fx, fy + 2, 9)
    else:   # listing disabled: the stall is shut
        icons.draw_motif(img, 'ledger', R0 + 5, shelf_y - 11)
        sprite(img, R0 + 25, shelf_y - 8, PADLOCK)
        cobweb(img, R0 + 30, shelf_y - 14, 'tr')
    if mid == 'board':
        # the stall's notice board: two blank, ruled writs pinned to planks
        bx, by = R0 + 7, 86
        P.ink_outline(img, (bx, by, 26, 22), 'ink_1', radius=1, heavy='br', fill_colour=wood[1])
        P.hline(img, bx + 1, bx + 24, by + 1, wood[2])
        for px in range(bx + 6, bx + 24, 6):
            P.vline(img, px, by + 2, by + 20, wood[0])
        for (wx, wy, ww, wh) in ((bx + 3, by + 3, 11, 13), (bx + 14, by + 6, 9, 12)):
            P.vellum_strip(img, (wx, wy, ww, wh), seed + wx, outline='ink_1', deckle='b', heavy='br',
                           ramp=[IRON[1], IRON[2], IRON[2], IRON[3]] if cold else VELLUM)
            for ry in range(wy + 4, wy + wh - 3, 2):
                P.hline(img, wx + 2, wx + ww - 3, ry, IRON[2] if cold else VELLUM[0])
            P.put(img, wx + ww // 2, wy + 1, IRON[3]); P.put(img, wx + ww // 2, wy + 2, IRON[0])
        if cold:
            P.line(img, bx + 1, by + 20, bx + 24, by + 2, INK[1])
    # crates, a barrel and a sack at the foot of the right panel
    crate(img, R0 + 4, base - 13, 16, 13, wood, seed + 7)
    crate(img, R0 + 20, base - 10, 14, 10, wood, seed + 8)
    crate(img, R0 + 7, base - 23, 12, 10, wood, seed + 9)
    sprite(img, R0 + 22, base - 19, SACK)
    P.moss_tuft(img, R0 + 9, shelf_y + 5, 5, seed=seed + 3)
    P.crack(img, R0 + 33, 125, 7, seed=seed + 5, colour=STONE[0], light=STONE[3])
    if cold:
        cobweb(img, R0 + 4, 21, 'tl')

    # ---- top strip: chains to the plaque; bottom: swagged chains ---------
    P.chain(img, 12, 4, a.w // 2 - 22, 4, sag=2, seed=seed + 11)
    P.chain(img, a.w // 2 + 21, 4, a.w - 13, 4, sag=2, seed=seed + 12)
    for x0, x1 in ((8, 120), (136, a.w - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3); P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur')
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def out_path(path, root):
    if root is None:
        return path
    return Path(root) / Path(path).relative_to(geo.TEXTURES)


def paint_skin(key, root=None):
    s = geo.skin(key)
    C.save_png(paint_background(key), out_path(s.background_path, root))
    paint_buttons(key, root=root)
    for a in s.art_layers:
        C.save_png(paint_frame(key), out_path(s.frame_path(a.id), root))
    print('painted', key)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', help='write under this directory (laid out like textures/) instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        paint_skin(key, args.out_root)


if __name__ == '__main__':
    main()
