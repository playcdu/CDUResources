#!/usr/bin/env python3
"""Soulrend painter for the invsee family: invsee_online and invsee_offline.

    python tools/soulrend/paint_invsee.py                       # both skins -> pack-source
    python tools/soulrend/paint_invsee.py --skin invsee_online
    python tools/soulrend/paint_invsee.py --out-root DIR        # DIR laid out like textures/

Both screens are chest_6 with all 54 top cells native (another player's
inventory) and no painted buttons, so each skin owns two textures: the
176x222 background and the 256x238 outer frame ``menu_frame``.

Family identity: a scrying mirror / soul-lens over a leather satchel.

* invsee_online: the lens lit with soul-cyan, an eye awake in the glass,
  floating over an open satchel that spills soul-light; a lit candle on an
  iron pricket with ember glow; warm umber leather, mossy slate, gold.
* invsee_offline: the same scene gone cold. Ash-grey moonlit stone, a barred
  window with a crescent moon, the mirror dark and cracked and hanging on a
  chain, the satchel buckled shut and padlocked, a snuffed candle trailing
  smoke, a cobweb, iron where the online screen has gold.

Backgrounds: the shared umber (online) or cold iron-grey (offline) sheet with
saddle stitching in the margins and the vellum bands held by leather straps
through iron buckles; iron-framed sockets round every native well. No words:
the frame plaque is the wordless heraldic plaque like every Soulrend frame.

Deterministic: fixed seeds, no clock. Licence: code MIT; artwork CC0-1.0.
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
from palette import (BLOOD, EMBER, GOLD, INK, IRON, MOSS, SOUL, STONE, UMBER, VELLUM,  # noqa: E402
                     luminance, ramp_of, step)

SKINS = ('invsee_online', 'invsee_offline')
SEED = {'invsee_online': 41, 'invsee_offline': 43}
TEX = geo.ROOT / 'pack-source' / 'assets' / 'quasar_gui' / 'textures'


def online(key):
    return key == 'invsee_online'


# ---------------------------------------------------------------------------
# Small helpers (own to this painter)
# ---------------------------------------------------------------------------

BAYER4 = P.BAYER4


def is_ink(p):
    r = ramp_of(p)
    return r is not None and r[0] == 'ink'


def remap(img, box, mapping):
    """Swap exact palette colours inside ``box`` (e.g. gold -> iron)."""
    x0, y0, w, h = box
    px = img.load()
    for y in range(max(0, y0), min(img.height, y0 + h)):
        for x in range(max(0, x0), min(img.width, x0 + w)):
            p = px[x, y]
            if p[3] and p[:3] in mapping:
                px[x, y] = mapping[p[:3]] + (255,)


def ellipse(cx, cy, rx, ry):
    """Pixel set inside an ellipse centred on (cx, cy) (half-pixel centres ok)."""
    pts = set()
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if rx > 0 and ry > 0 and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                pts.add((x, y))
    return pts


GOLD_TO_IRON = {GOLD[2]: IRON[3], GOLD[1]: IRON[2], GOLD[0]: IRON[0]}
MOSS_TO_ASH = {MOSS[2]: STONE[2], MOSS[1]: STONE[1], MOSS[0]: STONE[0]}
EMBER_TO_ASH = {EMBER[2]: IRON[3], EMBER[1]: IRON[2], EMBER[0]: IRON[1]}


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

# leather strap wrapped round a band end, through an iron buckle with a prong
BUCKLE_13 = ['oooo', 'o32O', 'o21O', 'o2OO', 'o21O', 'dddc', 'd2Hb', 'd2hb', 'cbba', 'o21O', 'o2OO',
             'o21O', 'oOOO']
BUCKLE_9 = ['oooo', 'o32O', 'dddc', 'd2Hb', 'cbba', 'o21O', 'o2OO', 'o21O', 'oOOO']


def band_buckles(img, band, key):
    """Both ends of a vellum band held by a leather strap through an iron
    buckle (lit from the top-left on both sides, so no mirroring)."""
    rows = BUCKLE_13 if band.h >= 13 else BUCKLE_9
    k = None if online(key) else {'H': IRON[3], 'h': IRON[2], '3': IRON[2], '2': UMBER[1], '1': UMBER[0]}
    P.sprite(img, band.x, band.y, rows, k)
    P.sprite(img, band.right - 4, band.y, rows, k)


def stitches(img, x0, y0, x1, y1, colour, on=2, off=2, phase=0):
    """Saddle stitching along a straight run (horizontal or vertical)."""
    pts = P.line_points(x0, y0, x1, y1)
    for i, (x, y) in enumerate(pts):
        if (i + phase) % (on + off) < on:
            P.put(img, x, y, colour)


def paint_background(key):
    s = geo.skin(key)
    seed = SEED[key]
    sheet = UMBER if online(key) else IRON
    img = C.base_background(key, seed=seed, ramp=sheet)
    W, H = s.width, s.height
    tband, iband = C.bands(key)
    band_buckles(img, tband, key)
    band_buckles(img, iband, key)
    px = img.load()
    sheet_px = sheet[1] + (255,)
    thread = UMBER[3] if online(key) else IRON[2]
    # saddle stitching wherever the margin column is still bare sheet
    for x in (2, W - 3):
        for i, y in enumerate(range(16, H - 8)):
            if px[x, y] == sheet_px and i % 4 < 2:
                P.put(img, x, y, thread)
    # the free rows under the hotbar socket: a stitched hem and a small buckle
    free = [y for y in range(H - 8, H - 1) if all(px[x, y] == sheet_px or P.get(img, x, y)[:3] in
                                                     (sheet[0], sheet[2]) for x in range(10, W - 10))]
    if free:
        hy = free[-1]
        stitches(img, 9, hy, W // 2 - 8, hy, thread, 2, 2)
        stitches(img, W // 2 + 7, hy, W - 10, hy, thread, 2, 2)
        cx = W // 2
        if len(free) >= 2:
            row_a = free[-2]
            P.sprite(img, cx - 4, row_a, ['oHhhhho', 'o3222Oo'] if online(key) else ['odcccbo', 'o2111Oo'])
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frame pieces
# ---------------------------------------------------------------------------

def ledge(img, x, y, w, ramp):
    """A short carved stone ledge on two iron brackets."""
    P.fill(img, (x, y, w, 4), ramp[2])
    P.hline(img, x, x + w - 1, y, ramp[3])
    P.hline(img, x, x + w - 1, y + 3, ramp[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0, heavy='b')
    for bx in (x + 2, x + w - 5):
        P.sprite(img, bx, y + 5, ['occo', '.oba', '..oa', '...o'])


def mirror(img, cx, cy, rx, ry, lit, seed):
    """The scrying mirror: an oval of glass in a two-ring frame (gold when lit,
    tarnished iron when cold). Lit: soul glass with an open eye and glints.
    Cold: dark glass shattered from an impact point, one shard missing."""
    metal = GOLD if lit else [IRON[0], IRON[2], IRON[3]]
    outer = ellipse(cx, cy, rx, ry)
    ring1 = ellipse(cx, cy, rx - 1, ry - 1)
    ring3 = ellipse(cx, cy, rx - 3, ry - 3)
    glass = ellipse(cx, cy, rx - 4, ry - 4)
    for (x, y) in outer:
        dx, dy = x - cx, y - cy
        if (x, y) not in ring1:
            P.put(img, x, y, INK[0] if dx + dy > 0 else INK[1])
        elif (x, y) not in ring3:
            # frame: lit top-left, dark bottom-right, a groove between the rings
            inner = (x, y) in ellipse(cx, cy, rx - 2, ry - 2)
            light = (dx / rx + dy / ry)
            if light < -0.45:
                col = metal[2]
            elif light > 0.45:
                col = metal[0]
            else:
                col = metal[1]
            if inner and -0.45 <= light <= 0.45:
                col = metal[0] if light > 0 else metal[1]
            P.put(img, x, y, col)
        elif (x, y) not in glass:
            P.put(img, x, y, INK[0])
    # bead studs on the frame at the four compass points
    for (bx, by) in ((cx, cy - ry + 1), (cx, cy + ry - 1), (cx - rx + 1, cy), (cx + rx - 1, cy)):
        P.put(img, int(bx), int(by), metal[2] if (bx <= cx and by <= cy) else metal[1])
    if lit:
        deep = ellipse(cx, cy, rx - 5, ry - 5)
        for (x, y) in glass:
            dx, dy = x - cx, y - cy
            col = SOUL[0]
            if (x, y) not in deep and dx / rx + dy / ry > 0.25:
                col = INK[1]                                  # shadowed rim of the glass
            elif ((x - 1, y) not in glass or (x, y - 1) not in glass) and dx / rx + dy / ry < -0.2:
                col = SOUL[1]                                 # lit inner edge, top-left
            P.put(img, x, y, col)
        # a swirl of soul-light circling the eye
        for a in range(200, 330, 14):
            t = math.radians(a)
            P.put(img, round(cx + 5 * math.cos(t)), round(cy + 8 * math.sin(t)), SOUL[1])
        for a in (20, 34, 48):
            t = math.radians(a)
            P.put(img, round(cx + 5 * math.cos(t)), round(cy + 8 * math.sin(t)), SOUL[1])
        # the eye: an almond of light, a dark iris ring, a pupil, a catchlight
        eye = ['...LLLLL...',
               '.LLklllkLL.',
               'Lkl.kOk.lkL',
               '.LLklllkLL.',
               '...LLLLL...']
        P.sprite(img, int(cx) - 5, int(cy) - 2, eye)
        P.put(img, int(cx) + 1, int(cy) - 1, SOUL[2])
        # reflection streak top-left and two sparkles
        for k in range(3):
            P.put(img, int(cx - rx + 6 + k // 2), int(cy - ry + 7 + k), SOUL[2])
        P.put(img, int(cx - rx + 8), int(cy - ry + 6), SOUL[2])
        P.put(img, int(cx + 3), int(cy + ry - 9), SOUL[2])
    else:
        for (x, y) in glass:
            dx, dy = x - cx, y - cy
            col = IRON[0]
            if dx + dy > (rx + ry) * 0.3:
                col = INK[1]
            if -dx - dy > (rx + ry) * 0.38:
                col = IRON[1]
            P.put(img, x, y, col)
        # impact point upper right; cracks radiate, lit on their upper-left side
        ix, iy = int(cx) + 2, int(cy) - 4
        r = P._rng(seed, 'shatter')
        ends = [(ix - 8, iy - 6), (ix + 3, iy - 9), (ix - 7, iy + 6), (ix + 4, iy + 12),
                (ix - 3, iy + 16), (ix + 5, iy + 3)]
        for (ex, ey) in ends:
            pts = P.line_points(ix, iy, ex, ey)
            for j, (x, y) in enumerate(pts):
                if (x, y) not in glass:
                    break
                jog = 1 if (j > 2 and r.random() < 0.18) else 0
                P.put(img, x + jog, y, INK[0])
                if (x + jog - 1, y - 1) in glass and r.random() < 0.6:
                    P.put(img, x + jog - 1, y - 1, IRON[2])
        P.put(img, ix, iy, IRON[3]); P.put(img, ix - 1, iy, IRON[2]); P.put(img, ix, iy - 1, IRON[2])
        # a missing shard near the foot: black void with a lit broken edge
        shard = [(int(cx) - 2 + i, int(cy) + 5 + j) for j in range(4) for i in range(j + 1)]
        for (x, y) in shard:
            if (x, y) in glass:
                P.put(img, x, y, INK[0])
        P.hline(img, int(cx) - 2, int(cx) + 2, int(cy) + 9, IRON[2])
        # a cold sliver of moonlight across the top of the glass
        P.put(img, int(cx - rx + 6), int(cy - ry + 7), IRON[3])
        P.put(img, int(cx - rx + 6), int(cy - ry + 8), IRON[2])
        P.put(img, int(cx - rx + 7), int(cy - ry + 6), IRON[3])


def satchel(img, x, y, w, h, opened, seed):
    """A leather satchel seen front-on with its shoulder strap looped above.
    ``opened``: the flap thrown back over the top, the mouth dark with
    soul-light inside, the strap and its gold buckle hanging loose.
    Shut: the flap down over the front, strapped through an iron buckle,
    an iron chain across it and a padlock. Returns the mouth centre."""
    warm = opened
    hi = UMBER[3] if warm else IRON[2]
    body = (x, y, w, h)
    # shoulder strap arc above the body
    sx0, sx1 = x + 3, x + w - 4
    arc = P._sag_points(sx0, y + 1, sx1, y + 1, -9)
    for (ax, ay) in arc:
        P.put(img, ax, ay - 1, INK[1]); P.put(img, ax, ay, hi); P.put(img, ax, ay + 1, UMBER[1])
        P.put(img, ax, ay + 2, INK[0])
    for (ax, ay) in arc[2::6]:
        P.put(img, ax, ay, UMBER[2])                            # worn spots on the strap
    # body
    P.ink_outline(img, body, 'ink_1', radius=2, heavy='br', fill_colour=UMBER[2])
    P.vline(img, x + 1, y + 2, y + h - 3, hi)
    P.hline(img, x + 2, x + w - 3, y + 1, hi)
    P.fill(img, (x + 1, y + h - 4, w - 2, 3), UMBER[1])
    P.vline(img, x + w - 2, y + 2, y + h - 3, UMBER[1])
    P.hline(img, x + 2, x + w - 3, y + h - 2, UMBER[0])
    # gussets: darker side panels
    for gx in (x + 3, x + w - 4):
        P.vline(img, gx, y + 3, y + h - 3, UMBER[1])
    # saddle stitching round the front panel
    thread = VELLUM[0] if warm else IRON[2]
    for i, sx in enumerate(range(x + 5, x + w - 5)):
        if i % 3 < 2:
            P.put(img, sx, y + h - 4, thread)
    for i, sy in enumerate(range(y + 4, y + h - 4)):
        if i % 3 < 2:
            P.put(img, x + 5, sy, thread); P.put(img, x + w - 6, sy, thread)
    cx = x + w // 2
    if opened:
        # flap thrown back: a lip of leather above the mouth
        P.ink_outline(img, (x + 2, y - 4, w - 4, 5), 'ink_1', radius=1, fill_colour=UMBER[1])
        P.hline(img, x + 3, x + w - 4, y - 3, UMBER[3])
        P.hline(img, x + 3, x + w - 4, y - 2, UMBER[2])
        # mouth: a dark slot with a calm band of soul-light deep inside
        P.fill(img, (x + 3, y + 1, w - 6, 3), INK[0])
        P.hline(img, x + 6, x + w - 7, y + 2, SOUL[0])
        P.hline(img, cx - 3, cx + 3, y + 2, SOUL[1])
        P.put(img, cx, y + 2, SOUL[2])
        # a few sparks rising out of it toward the lens
        for (dx, dy) in ((-2, -2), (3, -3), (0, -5), (-4, -6)):
            P.put(img, cx + dx, y + dy, SOUL[2] if dy % 2 else SOUL[1])
        # the strap hangs loose from the mouth, its gold buckle dangling
        sxs = cx + 4
        P.vline(img, sxs, y + 4, y + h + 2, UMBER[3])
        P.vline(img, sxs + 1, y + 4, y + h + 2, UMBER[1])
        P.vline(img, sxs - 1, y + 4, y + h + 2, INK[1]); P.vline(img, sxs + 2, y + 4, y + h + 2, INK[0])
        P.sprite(img, sxs - 2, y + h + 2, ['oHhho', 'Hoo.g', 'hhgg.', '.ooo.'])
        P.put(img, sxs, y + 8, INK[0]); P.put(img, sxs, y + 11, INK[0])
        return cx, y + 2
    # shut: the flap covers the upper front, rounded at its foot
    fh = h * 3 // 5
    P.ink_outline(img, (x + 1, y - 1, w - 2, fh + 1), 'ink_1', radius=2, heavy='b', fill_colour=UMBER[1])
    P.hline(img, x + 3, x + w - 4, y, hi)
    P.hline(img, x + 2, x + w - 3, y + fh - 2, UMBER[0])
    for i, sx in enumerate(range(x + 4, x + w - 4)):
        if i % 3 < 2:
            P.put(img, sx, y + fh - 3, thread)
    # two straps down from the flap, each pulled tight through an iron buckle
    for sx in (x + 6, x + w - 9):
        P.fill(img, (sx, y + 1, 3, h - 4), UMBER[2])
        P.vline(img, sx, y + 1, y + h - 4, hi)
        P.vline(img, sx - 1, y, y + h - 4, INK[1]); P.vline(img, sx + 3, y, y + h - 4, INK[0])
        P.sprite(img, sx - 1, y + fh - 1, ['odcca', 'c.H.a', 'cbbaa'], {'H': IRON[3]})
        P.put(img, sx + 1, y + fh + 3, INK[0])
    # a hasp at the middle of the flap and a shut padlock hanging from it
    P.sprite(img, cx - 1, y + fh - 3, ['oco', 'obo', 'oao'])
    P.sprite(img, cx - 3, y + fh, ['..ooo..', '.oc.do.', '.o...o.', 'ooooooo', 'ocddcbo', 'ocbOcbO',
                                   'obbObaO', 'obbbaaO', '.OOOOO.'])
    return cx, y + 2


def pricket(img, x, y, lit, seed):
    """An iron pricket candlestick (drip pan, knop, tripod foot) holding a
    bone-wax candle. Lit: flame and ember glow. Snuffed: charred wick and a
    curl of cold smoke. Returns the flame centre (or the wick)."""
    # candle body from y .. y+10, pan at y+11
    fx, fy = P.candle(img, x, y, height=10, lit=lit, holder=None, seed=seed)
    P.sprite(img, x - 4, y + 11, ['occcccccco', '.oaaaaaao.', '...odo....', '...oco....', '...obo....',
                                    '..ocbao...', '...obo....', '...oco....', '...obo....', '...oba....',
                                    '..obbbao..', '.obo.oaao.', 'obo...oaao', 'oo.....ooo'])
    if not lit:
        # smoke: a thin cold curl drifting up and right
        P.sprite(img, x - 1, y - 12, ['....d.', '...d..', '..d...', '..d...', '...d..', '....d.', '....d.',
                                      '...d..', '..d...', '..d...', '...d..'])
    return fx, fy


def cobweb(img, cx, cy, size, flip=False):
    """A cobweb anchored in a corner at (cx, cy), spreading down-left
    (``flip``: down-right): iron_3 radials with sagging iron_2 threads."""
    sgn = 1 if flip else -1
    radials = []
    for a in (0, 22, 45, 68, 90):
        t = math.radians(a)
        ex, ey = cx + sgn * round(size * math.cos(t)), cy + round(size * math.sin(t))
        radials.append((ex, ey))
        for (x, y) in P.line_points(cx, cy, ex, ey):
            P.put(img, x, y, IRON[2])
    for rr in (3, 6, 9):
        if rr >= size:
            break
        pts = []
        for a in (0, 22, 45, 68, 90):
            t = math.radians(a)
            pts.append((cx + sgn * round(rr * math.cos(t)), cy + round(rr * math.sin(t))))
        for (a0, a1) in zip(pts, pts[1:]):
            for (x, y) in P.line_points(a0[0], a0[1] + 1 if rr > 3 else a0[1], a1[0], a1[1] + 1 if rr > 3 else a1[1]):
                P.put(img, x, y, IRON[3])


def moon_window(img, box, seed):
    """A tall arched window with iron bars: night sky, a crescent moon and two
    cold stars. Returns the interior pixel set."""
    x, y, w, h = box
    inside = P.arch_niche(img, box, seed=seed, ramp=IRON, interior=INK[1])
    for (px, py) in inside:
        if (px * 3 + py * 5) % 23 == 0:
            P.put(img, px, py, IRON[0])
    # two cold stars
    P.put(img, x + 4, y + 13, IRON[3]); P.put(img, x + w - 6, y + 18, IRON[2])
    # bars: two uprights and a cross bar, lit on their left
    for bx in (x + 6, x + w - 8):
        for (px, py) in inside:
            if px == bx:
                P.put(img, px, py, IRON[2])
            elif px == bx + 1:
                P.put(img, px, py, IRON[0])
    for px in range(x + 2, x + w - 2):
        if (px, y + h // 2 + 3) in inside:
            P.put(img, px, y + h // 2 + 3, IRON[1])
            P.put(img, px, y + h // 2 + 4, INK[0])
    # a crescent moon between the bars, high in the arch
    moon = ['.yyy..', 'yyxi..', 'yx....', 'yx....', 'yyw...', '.ywxi.']
    P.sprite(img, x + w // 2 - 3, y + 5, moon)
    # sill
    P.fill(img, (x - 1, y + h, w + 2, 2), IRON[2])
    P.hline(img, x - 1, x + w, y + h, IRON[3])
    P.ink_outline(img, (x - 2, y + h - 1, w + 4, 4), 'ink_1', radius=0, heavy='b')
    return inside


def rune_tablet(img, box, lit, seed, ramp):
    """A small slab cut into the wall bearing an open-eye rune: soul-lit when
    the owner is online, cut dark and dead when offline."""
    x, y, w, h = box
    P.ink_outline(img, box, 'ink_1', radius=1, heavy='br', fill_colour=ramp[2])
    P.hline(img, x + 1, x + w - 2, y + 1, ramp[1])            # inward bevel: cut, not raised
    P.vline(img, x + 1, y + 1, y + h - 2, ramp[1])
    P.hline(img, x + 2, x + w - 2, y + h - 2, ramp[3])
    P.vline(img, x + w - 2, y + 2, y + h - 2, ramp[3])
    cx, cy = x + w // 2, y + h // 2
    rune = ['.#..#..#.',
            '.........',
            '..#####..',
            '.#.....#.',
            '#..###..#',
            '.#.....#.',
            '..#####..',
            '.........']
    on = {(i, j) for j, row in enumerate(rune) for i, ch in enumerate(row) if ch == '#'}
    ox, oy = cx - 4, cy - 4
    for (i, j) in on:
        if (i + 1, j + 1) not in on:
            P.put(img, ox + i + 1, oy + j + 1, ramp[3])        # lit lip below-right of each groove
    for (i, j) in on:
        P.put(img, ox + i, oy + j, SOUL[1] if lit else ramp[0])
    if lit:
        P.put(img, cx, cy, SOUL[2])


def books(img, x, y, specs):
    """Standing books left to right: ``specs`` is a list of (width, height,
    ramp); spines with an ink rim, a lit left column and two gold bands.
    The bottoms line up on row ``y``. Returns the right edge."""
    for (w, h, ramp) in specs:
        top = y - h + 1
        P.ink_outline(img, (x, top, w, h), 'ink_1', radius=0, heavy='br', fill_colour=ramp[1])
        P.vline(img, x + 1, top + 1, y - 1, ramp[2])
        for by in (top + 2, y - 2):
            P.hline(img, x + 1, x + w - 2, by, GOLD[1])
        P.put(img, x + 1, top + 2, GOLD[2])
        x += w - 1
    return x


def light_shaft(img, top, bottom, w_top, w_bot, clip=None, tint=None):
    """A shaft of light from ``top`` (x, y) to ``bottom`` (x, y), widening from
    ``w_top`` to ``w_bot``: a solid core one step lighter (flat, like a beam
    in a dark nave) with a 1 px checker fringe. ``clip(x, y)`` limits it; the
    darkest mortar in the core may take a sparse ``tint`` stipple."""
    (x0, y0), (x1, y1) = top, bottom
    base = img.copy()
    bp = base.load()
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        c = x0 + (x1 - x0) * t
        half = (w_top + (w_bot - w_top) * t) / 2
        for x in range(int(c - half) - 1, int(c + half) + 2):
            if not (0 <= x < img.width and 0 <= y < img.height) or (clip and not clip(x, y)):
                continue
            p = bp[x, y]
            if p[3] == 0 or is_ink(p):
                continue
            d = abs(x + 0.5 - c)
            if d <= half - 1:
                if tint is not None and luminance(p) < 52:
                    if BAYER4[y % 4][x % 4] < 4:
                        P.put(img, x, y, tint)
                    continue
                P.put(img, x, y, step(p, 1))
            elif d <= half and (x + y) % 2 == 0:
                P.put(img, x, y, step(p, 1))


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def paint_frame(key):
    s = geo.skin(key)
    a = s.layer()
    seed = SEED[key]
    lit = online(key)
    wall = STONE if lit else IRON
    ash = MOSS if lit else [STONE[0], STONE[1], STONE[2]]
    img = C.base_frame(key, a.id, seed=seed, heading=False, ramp=wall)   # frames are wordless
    lp, rp = a.left_panel, a.right_panel
    H, W = a.h, a.w
    if not lit:
        remap(img, (0, 0, W, H), MOSS_TO_ASH)
    in_left = lambda x, y: 3 <= x <= 37 and 3 <= y <= H - 4          # noqa: E731

    # ---------------- left panel: banner or moonlit window -----------------
    mcx, mcy, mrx, mry = lp.x + 20, 78, 11, 16
    if lit:
        P.chain(img, lp.x + 10, 8, lp.x + 10, 12, seed=seed, shadow=None)
        P.chain(img, lp.x + 29, 8, lp.x + 29, 12, seed=seed + 1, shadow=None)
        C.side_banner(img, geo.Rect(lp.x + 4, 0, 32, 0), y=14, seed=seed, ramp=UMBER, crest='key', h=32)
        P.glow(img, mcx, mcy, 17, 'soul')
    else:
        moon_window(img, (lp.x + 9, 10, 22, 30), seed)

    # ---------------- the mirror ------------------------------------------
    if not lit:
        # hung on a chain from an iron hook: inert
        P.sprite(img, mcx - 1, 44, ['oco', '.a.'])
        P.chain(img, mcx, 46, mcx, mcy - mry - 4, seed=seed + 7)
    P.gold_filigree(img, mcx - 2, mcy - mry - 4, 'fleur', ramp=None if lit else IRON)
    mirror(img, mcx, mcy, mrx, mry, lit, seed)
    drop = ['ohgo', '.Hg.', '.og.', '..o.'] if lit else ['odao', '.da.', '.oa.', '..o.']
    P.sprite(img, mcx - 1, mcy + mry, drop)

    # ---------------- the satchel on its ledge ----------------------------
    sy = 124
    if lit:
        # the lens looks down into the open satchel: soul-light pools at its
        # mouth and a thin stream of motes links the two
        P.glow(img, mcx, sy - 4, 10, 'soul')
        for (dx, dy, c) in ((0, 21, SOUL[1]), (-1, 23, SOUL[2]), (1, 25, SOUL[1]), (0, 27, SOUL[1]),
                            (-2, 29, SOUL[2]), (2, 31, SOUL[1]), (-1, 33, SOUL[1]), (3, 35, SOUL[2]),
                            (-4, 26, SOUL[0]), (5, 29, SOUL[0]), (-5, 33, SOUL[1]), (6, 24, SOUL[1])):
            P.put(img, mcx + dx, mcy + dy, c)
    else:
        # moonlight from the window falls across the cracked glass
        light_shaft(img, (lp.x + 18, 42), (lp.x + 27, 116), 10, 16, clip=in_left)
    ledge(img, lp.x + 4, sy + 18, 31, wall)
    satchel(img, lp.x + 6, sy, 27, 18, opened=lit, seed=seed)
    P.moss_tuft(img, lp.x + 7, sy + 23, 5, seed=seed, ramp=ash)

    # under the ledge: the satchel's key on a chain (offline: snapped, fallen)
    P.chain(img, lp.x + 31, sy + 24, lp.x + 31, sy + 44 if lit else sy + 34, seed=seed + 3)
    if lit:
        icons.draw_motif(img, 'key', lp.x + 26, sy + 45)
    else:
        P.sprite(img, lp.x + 30, sy + 35, ['.c.', 'o.a'])
    P.crack(img, lp.x + 22, sy + 52, 7, seed=seed, colour=wall[0], light=wall[3])

    # a wall sconce: a candle burning (online) or long since snuffed (offline)
    scx, scy = lp.x + 11, 168
    # front-on iron sconce: drip pan, knop, and a riveted backplate on the wall
    P.sprite(img, scx - 4, scy + 11, ['obcccbo', '.oaaao.', '..oco..', '.ocdao.', '..oba..', '.obcbo.',
                                      '.ocdba.', '.obbaa.', '..ooo..'])
    sfx, sfy = P.candle(img, scx - 1, scy, height=10, lit=lit, holder=None, seed=seed + 2)
    if lit:
        P.glow(img, sfx, sfy + 4, 12, 'ember')

    # lower left: a brazier on the floor (online: embers; offline: cold ash)
    icons.draw_motif(img, 'brazier', lp.x + 13, H - 30)
    if lit:
        P.glow(img, lp.x + 18, H - 30, 10, 'ember')
    else:
        remap(img, (lp.x + 10, H - 34, 20, 14), EMBER_TO_ASH)
        icons.draw_motif(img, 'key', lp.x + 4, H - 19)            # the fallen key
    if lit:
        icons.draw_motif(img, 'bone', lp.x + 4, H - 19)
    P.moss_tuft(img, lp.x + 28, H - 12, 5, seed=seed + 9, ramp=ash)

    # ---------------- right panel -----------------------------------------
    cxp = rp.x + 19
    ledge(img, rp.x + 10, 47, 18, wall)                    # corbel shelf for the candlestick
    if lit:
        fx, fy = pricket(img, cxp - 1, 22, True, seed)
        P.glow(img, fx, fy + 3, 16, 'ember')
    else:
        pricket(img, cxp - 1, 22, False, seed)
        cobweb(img, W - 4, 3, 11)

    ly = 84
    ledge(img, rp.x + 4, ly, 32, wall)
    icons.draw_motif(img, 'goblet', rp.x + 5, ly - 9)
    icons.draw_icon(img, 'balance', (rp.x + 15, ly - 17, 12, 17))
    icons.draw_motif(img, 'writ', rp.x + 22, ly - 9)
    P.moss_tuft(img, rp.x + 23, ly + 5, 5, seed=seed + 4, ramp=ash)

    if lit:
        P.glow(img, rp.x + 20, 110, 13, 'soul')            # light round the slab, not on it
    rune_tablet(img, (rp.x + 11, 100, 19, 20), lit, seed, wall)

    # chained lantern hanging beside the niche
    P.chain(img, rp.x + 6, ly + 6, rp.x + 6, 136, seed=seed + 5)
    icons.draw_motif(img, 'lantern', rp.x + 2, 137)
    if lit:
        P.glow(img, rp.x + 6, 142, 10, 'ember')
    else:
        remap(img, (rp.x, 136, 12, 10), EMBER_TO_ASH)

    # arch niche with a row of old books
    nx, ny, nw, nh = rp.x + 14, 140, 22, 34
    P.arch_niche(img, (nx, ny, nw, nh), seed=seed, ramp=wall)
    shelf = ny + nh - 3
    books(img, nx + 3, shelf, [(4, 13, BLOOD), (4, 15, UMBER), (3, 11, MOSS), (4, 14, IRON)])
    P.fill(img, (nx + 1, shelf + 1, nw - 2, 2), wall[2])
    P.hline(img, nx + 1, nx + nw - 2, shelf + 1, wall[3])
    if not lit:
        cobweb(img, nx + nw - 3, ny + 9, 5)

    icons.draw_motif(img, 'gargoyle', rp.x + 20, H - 28)
    if not lit:
        remap(img, (rp.x + 18, H - 30, 22, 26), {STONE[0]: IRON[0], STONE[1]: IRON[1], STONE[2]: IRON[2],
                                                 STONE[3]: IRON[3]})
    P.crack(img, rp.x + 33, 186, 8, seed=seed + 6, colour=wall[0], light=wall[3])

    # ---------------- top and bottom strips ---------------------------------
    P.chain(img, 12, 4, W // 2 - 26, 4, sag=2, seed=seed + 11)
    P.chain(img, W // 2 + 25, 4, W - 13, 4, sag=2, seed=seed + 12)
    for x0, x1 in ((8, 120), (136, W - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold' if lit else 'iron', 3)
        P.rivet(img, x1 - 1, H - 7, 'gold' if lit else 'iron', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur', ramp=None if lit else IRON)
    if not lit:
        # the cold screen keeps no gold, blood or ember: all of it goes to iron
        remap(img, (0, 0, W, H), {**GOLD_TO_IRON, **MOSS_TO_ASH,
                                  BLOOD[2]: IRON[2], BLOOD[1]: IRON[1], BLOOD[0]: IRON[0]})
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out-root', type=Path, default=TEX,
                    help='directory laid out like textures/ (default: pack-source textures)')
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        s = geo.skin(key)
        bg = paint_background(key)
        fr = paint_frame(key)
        p1 = C.save_png(bg, args.out_root / 'menu' / f'{key}.png')
        p2 = C.save_png(fr, args.out_root / 'frames' / key / f'{s.layer().id}.png')
        print('WROTE', p1)
        print('WROTE', p2)


if __name__ == '__main__':
    main()
