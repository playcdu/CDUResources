#!/usr/bin/env python3
"""Soulrend painter "plots": plot_buy, plot_rent, plot_list and plot_manage.

    python tools/soulrend/paint_plots.py                    # all four skins -> pack-source
    python tools/soulrend/paint_plots.py --skin plot_buy
    python tools/soulrend/paint_plots.py --out-root DIR     # DIR laid out like textures/

Family identity (decorative regions only, never in wells, text bands or
lettering): land claimed and recorded - boundary stakes driven into the
earth and joined by a surveyor's chain with brass tallies, a sealed land
writ, and a carved stone waymarker cut with a surveyor's benchmark.

* plot_buy: a survey deed hangs unrolled across the top of the sheet, its
  two ends still rolled, ruled in faint lines (no words) with an illuminated
  box and a compass rose. In front of it a stone waymarker rises from the
  earth between the two buttons; the native plot preview (slot 22) sits in a
  socket cut into its head, the featured stone socket. A surveyor's chain
  swags from the deed to the stone, a blood-sealed pendant hangs on the
  right; on the sill boundary stakes, the chain, a rolled writ and a candle.
* plot_rent: the same deed, but the seal is pressed with a key, an iron key
  hangs on a ring from the right-hand stake and the frame's banner bears a
  key: let, not sold. No words.
* plot_list: the 45 listing wells stay empty iron-framed sockets; only the
  margins carry the family (a flourish below the hotbar) and the frame shows
  the registry: a rack of rolled writs, stakes and the chain.
* plot_manage: the two native cells 13-14 stay empty sockets; the static
  cells 22-23 below them hold a small scene straddling their boundary: a
  waymarker between two stakes, the chain swagged across.

Frames: wordless plaques like every Soulrend frame; moss-green banners,
sconces, a waymarker, stakes and chain, a posted survey plat, a rolled writ
on a ledge, a lantern and a gargoyle.

Deterministic (fixed seeds, no clock). Only the four plot skins' PNGs are
written. Licence: code MIT; artwork CC0-1.0.
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
import primitives as P  # noqa: E402
from palette import BLOOD, EMBER, GOLD, INK, IRON, MOSS, STONE, UMBER, VELLUM  # noqa: E402

SKINS = ('plot_buy', 'plot_rent', 'plot_list', 'plot_manage')
SEED = {'plot_buy': 61, 'plot_rent': 67, 'plot_list': 71, 'plot_manage': 73}

# --- plot_buy / plot_rent geometry (background coordinates) -----------------
DEED = (18, 18, 140, 29)            # unrolled deed body: x 18..157, y 18..46
ROLLS = ((11, 16, 8, 33), (157, 16, 8, 33))   # the two rolled ends
SOCKET = (78, 52, 20, 20)           # slot 22 clearance (never painted)
STONE_BOX = (68, 40, 40, 73)        # the waymarker: x 68..107, y 40..112
PLINTH = (63, 111, 50, 11)          # its stepped footing: y 111..121
SILL_Y = 122                        # ground line (inventory band starts at 127)
PENDANT = (141, 60, 6)              # pendant seal centre and radius

# sprite keys: primitives.SK
ROLLED_WRIT = [
    '.ooooooooooooo.',
    'oyyyyysyyyyyywo',
    'oxxxxxsxxxxxwoo',
    'owwwwwrwwwwwvwo',
    '.ooooorooooooo.',
    '.....oto.......',
    '.....ost.......',
    '......o........',
]
COMPASS = [
    '....t....',
    '....s....',
    '...isi...',
    '..i.i.i..',
    'giiiHiiig',
    '..i.i.i..',
    '...igi...',
    '....g....',
    '....g....',
]
# a surveyor's benchmark cut into stone: a broad arrow under a level bar
BENCHMARK = [
    'nnnnnnn',
    'qqqqqqq',
    '...n...',
    '..nqn..',
    '.n.q.n.',
    'n..q..n',
    'q..q..q',
    '...q...',
]
# a tarnished brass key hanging bow-up (5x12): ring bow, shaft, two-toothed bit
KEY_V = [
    '.ooo.',
    'oHhgo',
    'oh.go',
    'ohggo',
    '.oOo.',
    '.oho.',
    '.oho.',
    '.ohO.',
    '.ohho',
    '.ohO.',
    '.ohgo',
    '.OOO.',
]


# ---------------------------------------------------------------------------
# Small helpers (local: the shared modules are not edited)
# ---------------------------------------------------------------------------

def rect_mask(x, y, w, h):
    return {(i, j) for j in range(y, y + h) for i in range(x, x + w)}


def mask_edges(mask):
    return {p for p in mask if any((p[0] + dx, p[1] + dy) not in mask
                                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


def paint_paper(img, mask, seed, ramp=VELLUM, fibres=True):
    """Vellum filling a pixel ``mask``: ramp[2] body, ramp[3] lit row/column
    under the top/left edges, ramp[1] inside the bottom/right edges, ink_1
    outline that turns ink_0 on the bottom/right."""
    edge = mask_edges(mask)
    for (x, y) in mask - edge:
        P.put(img, x, y, ramp[2])
    for (x, y) in mask - edge:
        if (x, y - 1) in edge or (x - 1, y) in edge:
            P.put(img, x, y, ramp[3])
        elif (x, y + 1) in edge or (x + 1, y) in edge:
            P.put(img, x, y, ramp[1])
    for (x, y) in edge:
        heavy = (x + 1, y) not in mask or (x, y + 1) not in mask
        P.put(img, x, y, INK[0] if heavy else INK[1])
    if fibres:
        r = P._rng(seed, 'fibres')
        inner = sorted(mask - edge)
        for _ in range(len(inner) // 400):
            x, y = r.choice(inner)
            if all((x + k, y) in mask and (x + k, y) not in edge for k in range(3)):
                P.hline(img, x, x + r.randint(1, 2), y, ramp[1])


def deckle_mask(mask, box, sides, seed):
    """Hand-cut edges: step the outline of ``mask`` in by 1 px in seeded runs."""
    x, y, w, h = box
    r = P._rng(seed, 'deckle', box, sides)
    out = set(mask)
    for side in sides:
        n = w if side in 'tb' else h
        t = 3
        while t < n - 3:
            run = r.randint(2, 6)
            if r.random() < 0.4:
                for k in range(t, min(n - 3, t + run)):
                    p = {'t': (x + k, y), 'b': (x + k, y + h - 1),
                         'l': (x, y + k), 'r': (x + w - 1, y + k)}[side]
                    out.discard(p)
            t += run + r.randint(2, 5)
    return out


def heal(img, before, box):
    """Give back what was painted before wherever a primitive punched alpha-0
    holes inside ``box`` (banner tatters over the wall)."""
    x, y, w, h = box
    for yy in range(max(0, y), min(img.height, y + h)):
        for xx in range(max(0, x), min(img.width, x + w)):
            if img.getpixel((xx, yy))[3] == 0 and before.getpixel((xx, yy))[3]:
                img.putpixel((xx, yy), before.getpixel((xx, yy)))


def press_emblem(img, cx, cy, rows, ramp=BLOOD):
    """Press a hand-drawn emblem into wax (ramp[0] grooves, ramp[2] lip)."""
    w, h = len(rows[0]), len(rows)
    x0, y0 = cx - w // 2, cy - h // 2
    on = {(i, j) for j, r in enumerate(rows) for i, c in enumerate(r) if c == '#'}
    for (i, j) in on:
        if (i + 1, j + 1) not in on:
            P.put(img, x0 + i + 1, y0 + j + 1, ramp[2])
    for (i, j) in on:
        P.put(img, x0 + i, y0 + j, ramp[0])


# a boundary stake (sold land) and a key (let land) pressed into the seal
STAKE_EMBLEM = ['.#.', '###', '.#.', '.#.', '.#.', '.#.']
KEY_EMBLEM = ['.#.', '#.#', '.#.', '.#.', '.##', '.#.', '.##']


def stake(img, x, ground, height, seed, rag=BLOOD, lean=0):
    """A wooden boundary stake driven into the ground: its foot is hidden at
    row ``ground``; iron-shod cap on top, a blood rag tied under it with a
    short tail fluttering right. 5 px wide (7 with the tail). Returns the
    rag's tail point."""
    top = ground - height
    # shaft: outline cols x and x+4, wood x+1..x+3 (lit left)
    for j in range(height):
        yy = top + j
        P.put(img, x, yy, INK[1]); P.put(img, x + 4, yy, INK[0])
        P.put(img, x + 1, yy, UMBER[3]); P.put(img, x + 2, yy, UMBER[2]); P.put(img, x + 3, yy, UMBER[0])
    # a knot and a split in the grain
    r = P._rng(seed, 'stake', x, ground)
    k = top + 7 + r.randint(0, max(0, height - 11))
    P.put(img, x + 2, k, UMBER[0])
    if height > 12:
        P.vline(img, x + 2, k + 2, k + 3, UMBER[1])
    # iron cap with a lit glint, ink rim above
    P.sprite(img, x, top - 2, ['.ooo.', 'odcbo', 'obbao', 'oaaao'])
    # the rag
    ry = top + 3
    P.sprite(img, x, ry, ['ottso', 'osrro'], {'t': rag[2], 's': rag[1], 'r': rag[0]})
    P.sprite(img, x + 5, ry, ['.o', 'so', 'ro', 'o.'], {'s': rag[1], 'r': rag[0]})
    return (x + 6, ry + 1)


def earth(img, x0, x1, y, seed, moss=True):
    """A strip of trodden earth and turf 3 px deep whose top row is ``y``:
    moss_1 turf with moss_2 blades, umber soil below, ink_0 underside."""
    r = P._rng(seed, 'earth', x0, y)
    for xx in range(x0, x1 + 1):
        P.put(img, xx, y, MOSS[1] if moss else UMBER[2])
        P.put(img, xx, y + 1, UMBER[2] if (xx + y) % 5 else UMBER[3])
        P.put(img, xx, y + 2, UMBER[0])
        P.put(img, xx, y + 3, INK[0])
        if moss and r.random() < 0.3:
            P.put(img, xx, y - 1, MOSS[2] if r.random() < 0.5 else MOSS[1])
    P.put(img, x0 - 1, y, INK[1]); P.put(img, x1 + 1, y, INK[1])
    for xx in range(x0 + 2, x1 - 1, 7):
        P.put(img, xx + r.randint(0, 3), y + 1, STONE[2])       # a pebble


def survey_chain(img, x0, y0, x1, y1, sag, seed, shadow='ink_0'):
    """A surveyor's chain: forged iron links with a brass tally tag every
    fourth link."""
    pts = P.chain(img, x0, y0, x1, y1, sag=sag, seed=seed, shadow=shadow)
    for i, (cx, cy) in enumerate(pts):
        if i % 4 == 2:
            P.put(img, cx, cy, GOLD[2]); P.put(img, cx, cy + 1, GOLD[0])
    return pts


def waymarker(img, box, seed, mark=True, moss=True, top='gable'):
    """A carved standing stone: a gabled (pointed) or chamfered head, ink
    outline (heavy bottom/right), stone_2 face lit stone_3 on the left and
    shaded stone_1 on the right, a few chisel marks, moss and a lichen spot
    creeping up from its foot and, with ``mark``, a surveyor's benchmark cut
    into the shaft. Returns the face mask."""
    x, y, w, h = box
    m = rect_mask(x, y, w, h)
    cut_n = (w + 1) // 2 if top == 'gable' else min(8, w // 4)
    for j in range(cut_n):
        cut = cut_n - j - (0 if top == 'gable' else 0)
        for i in range(cut):
            m.discard((x + i, y + j)); m.discard((x + w - 1 - i, y + j))
    edge = mask_edges(m)
    for (px, py) in m - edge:
        P.put(img, px, py, STONE[2])
    for (px, py) in m - edge:
        if (px - 1, py) in edge or (px, py - 1) in edge:
            P.put(img, px, py, STONE[3])
        elif (px + 1, py) in edge:
            P.put(img, px, py, STONE[1])
    for (px, py) in edge:
        heavy = (px + 1, py) not in m or (px, py + 1) not in m
        P.put(img, px, py, INK[0] if heavy else INK[1])
    # the dressed faces: a narrow shaded return face down the right side,
    # split from the front face by a lit arris
    if w >= 9:
        rx = x + w - 1 - max(2, w // 7)
        for (px, py) in m - edge:
            if px > rx:
                P.put(img, px, py, STONE[1])
            elif px == rx and (px + 1, py) in m - edge:
                P.put(img, px, py, STONE[3])
    r = P._rng(seed, 'waymarker', box)
    inner = sorted(m - edge)
    for _ in range(max(2, w * h // 140)):
        cx, cy = r.choice(inner)
        if (cx + 1, cy + 1) in m - edge and P.get(img, cx, cy)[:3] in (STONE[2], STONE[1]):
            P.put(img, cx, cy, STONE[0]); P.put(img, cx + 1, cy + 1, STONE[3])
    if mark and w >= 9:
        bx = x + (w - 7) // 2
        P.sprite(img, bx, y + max(cut_n + 3, h // 3), BENCHMARK)
    if moss:
        for i in range(1, w - 1):
            reach = r.choice((0, 0, 1, 1, 2, 3)) + (1 if i < w // 3 else 0)
            for k in range(reach):
                if (x + i, y + h - 2 - k) in m - edge:
                    P.put(img, x + i, y + h - 2 - k, MOSS[1] if k else MOSS[0])
            if reach and (x + i, y + h - 2 - reach) in m - edge and r.random() < 0.4:
                P.put(img, x + i, y + h - 2 - reach, MOSS[2])
        lx, ly = x + w - 5, y + cut_n + 2 + r.randint(0, 3)
        if {(lx, ly), (lx + 1, ly + 1)} <= m - edge:
            P.sprite(img, lx, ly, ['zZ', 'jz'])
    return m


def iron_ring(img, x, y):
    """A forged iron tethering ring on a staple driven into stone (5x6)."""
    P.sprite(img, x, y, ['.oo..', 'odco.', 'oO.ao', 'oc.ao', '.oaao', '..oo.'])


def ledge(img, x, y, w, brackets=True):
    """A short carved stone ledge on two iron brackets."""
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0)
    if brackets:
        for bx in (x + 2, x + w - 4):
            P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


def sconce(img, x, y, seed):
    """An iron wall sconce with a lit candle; returns the flame centre."""
    P.sprite(img, x - 3, y + 8, ['occcco', '.obao.', '..oo..', '..oa..', '..ob..', '...o..'])
    return P.candle(img, x - 1, y, height=6, lit=True, holder=None, seed=seed)


def hook(img, x, y):
    P.sprite(img, x - 1, y, ['ooo', 'odo', '.co', '.oa', '..o'])


def hanging_key(img, x, y, seed, links=2):
    """A brass key hanging bow-up from (x, y) on a few iron chain links."""
    if links:
        P.chain(img, x, y, x, y + links * 2 - 1, seed=seed, shadow=None)
    P.sprite(img, x - 2, y + links * 2, KEY_V)
    return (x - 2, y + links * 2, 5, 12)


# ---------------------------------------------------------------------------
# plot_buy / plot_rent background
# ---------------------------------------------------------------------------

def scroll_roll(img, box):
    """A rolled end of the deed standing upright: a vellum cylinder lit on the
    left, shaded right, with the spiral of the roll showing at its top and
    bottom caps."""
    x, y, w, h = box
    P.ink_outline(img, box, 'ink_1', radius=1, heavy='br', fill_colour=VELLUM[2])
    ramp = [VELLUM[3], VELLUM[3], VELLUM[2], VELLUM[2], VELLUM[1], VELLUM[1], VELLUM[0]]
    for i in range(1, w - 1):
        P.vline(img, x + i, y + 2, y + h - 3, ramp[min(len(ramp) - 1, (i - 1) * len(ramp) // (w - 2))])
    for cy in (y + 1, y + h - 2):
        P.hline(img, x + 1, x + w - 2, cy, VELLUM[1])
        P.put(img, x + w // 2 - 1, cy, INK[2]); P.put(img, x + w // 2, cy, VELLUM[0])
        P.put(img, x + w // 2 + 1, cy, INK[2])
    # creases where the vellum bends round
    for yy in range(y + 5, y + h - 4, 6):
        P.put(img, x + w - 3, yy, VELLUM[0])


def illuminated_box(img, bx, by, size=9):
    """An illuminated box: a gold-framed blood field with a gold fleur
    (ornament, never a letter)."""
    P.ink_outline(img, (bx, by, size, size), 'ink_1', radius=0, heavy='br', fill_colour=BLOOD[1])
    P.hline(img, bx + 1, bx + size - 2, by + 1, GOLD[2]); P.vline(img, bx + 1, by + 1, by + size - 2, GOLD[2])
    P.hline(img, bx + 2, bx + size - 2, by + size - 2, GOLD[0]); P.vline(img, bx + size - 2, by + 2, by + size - 2, GOLD[0])
    P.sprite(img, bx + 2, by + 2, ['..H..', '.hHh.', '..h..', '.ggg.'])


def paint_deed(img, seed):
    x, y, w, h = DEED
    m = deckle_mask(rect_mask(*DEED), DEED, 'tb', seed)
    # the deed's cast shadow on the sheet
    for (px, py) in m:
        q = (px + 1, py + 1)
        if q not in m and P.get(img, *q)[:3] in UMBER:
            P.put(img, q[0], q[1], INK[1])
    paint_paper(img, m, seed)
    # ruled lines, no words: a heading rule beside the illuminated box, two
    # short paragraphs, then the plat's compass rose on the right
    r = P._rng(seed, 'rules')
    for i, yy in enumerate(range(y + 5, y + h - 3, 4)):
        a = x + (16 if i < 2 else 6)
        b = x + w - (34 if i < 3 else 24) - (r.randint(8, 20) if i in (1, 4) else 0)
        for xx in range(a, b + 1):
            if (xx, yy) in m and P.get(img, xx, yy)[:3] in (VELLUM[1], VELLUM[2], VELLUM[3]):
                if not (64 <= xx <= 111):                  # the waymarker stands in front here
                    P.put(img, xx, yy, VELLUM[0])
        if i in (2, 5):
            P.sprite(img, x + 3, yy - 1, ['ts', 'sr'])          # rubric mark
    illuminated_box(img, x + 4, y + 3)
    P.sprite(img, x + w - 22, y + 5, COMPASS)
    # a parcel corner drawn on the plat: dashed blood boundary with stake ticks
    px0, py0 = x + w - 30, y + 17
    for k in range(0, 22, 2):
        P.put(img, px0 + k, py0, BLOOD[1])
    for k in range(0, 8, 2):
        P.put(img, px0, py0 + k, BLOOD[1])
    for (sx, sy) in ((px0, py0), (px0 + 21, py0)):
        P.sprite(img, sx - 1, sy - 1, ['.i.', 'iOi', '.i.'])
    # iron pins at the top corners of the unrolled sheet
    for px in (x + 2, x + w - 5):
        P.rivet(img, px, y + 1, 'iron', 3)
    for rb in ROLLS:
        scroll_roll(img, rb)
    return m


def paint_waymarker_socket(img, seed):
    """The featured stone socket: a tall waymarker with chamfered shoulders
    rising from a stepped footing between the buttons, slot 22 cut into its
    head inside a chiselled collar with gold rivets; a benchmark and an iron
    tethering ring on the shaft."""
    x, y, w, h = STONE_BOX
    m = waymarker(img, STONE_BOX, seed, mark=False, moss=False, top='chamfer')
    edge = mask_edges(m)
    sx, sy, sw, sh = SOCKET
    for d in (4, 5):
        for xx in range(sx - d, sx + sw + d):
            for yy in (sy - d, sy + sh - 1 + d):
                if (xx, yy) in m - edge:
                    P.put(img, xx, yy, STONE[3] if (yy < sy) == (d == 4) else STONE[1])
        for yy in range(sy - d, sy + sh + d):
            for xx in (sx - d, sx + sw - 1 + d):
                if (xx, yy) in m - edge:
                    P.put(img, xx, yy, STONE[3] if (xx < sx) == (d == 4) else STONE[1])
    P.socket_well(img, [SOCKET])
    for (cx, cy) in ((sx - 6, sy - 6), (sx + sw + 3, sy - 6), (sx - 6, sy + sh + 3), (sx + sw + 3, sy + sh + 3)):
        P.rivet(img, cx, cy, 'gold', 3)
    # the benchmark cut into the shaft, a hairline crack, lichen
    P.sprite(img, x + (w - 7) // 2, sy + sh + 10, BENCHMARK)
    P.crack(img, x + w - 8, sy + sh + 20, 9, seed=seed, colour=STONE[0], light=STONE[3])
    P.sprite(img, x + 5, y + 14, ['zZ.', 'jzz'])
    # stepped footing: two courses of dressed blocks, moss in the joints
    px, py, pw, ph = PLINTH
    P.stone_blocks(img, (px + 1, py + 1, pw - 2, ph - 2), seed, STONE, course=4, moss=0.25, cracks=0.2)
    P.ink_outline(img, PLINTH, 'ink_1', radius=0, heavy='br')
    P.hline(img, px + 1, px + pw - 2, py + 1, STONE[3])
    for i in range(3):                                   # moss creeping up the stone's foot
        P.put(img, x + 2 + i * 3, py - 1, MOSS[1]); P.put(img, x + 3 + i * 3, py - 1, MOSS[2])
    return m


def paint_buy_background(key, seed):
    rent = key == 'plot_rent'
    img = C.base_background(key, seed=seed)
    paint_deed(img, seed)
    earth(img, 8, 167, SILL_Y, seed)                    # the earth everything stands in
    paint_waymarker_socket(img, seed)

    # left: the surveyor's chain swagged from the deed's pin to a ring on the
    # stone; on the ground two stakes with the chain run between them and on
    # to the tethering ring low on the shaft
    survey_chain(img, 21, 47, 66, 58, sag=5, seed=seed + 1)
    iron_ring(img, 65, 56)
    if rent:
        # let, not sold: a key hangs from the stone's tethering ring,
        # in the gap between the Cancel cloth and the waymarker
        hanging_key(img, 65, 62, seed, links=1)
    stake(img, 13, SILL_Y + 1, 15, seed)
    stake(img, 44, SILL_Y + 1, 13, seed + 1)
    survey_chain(img, 18, SILL_Y - 9, 44, SILL_Y - 7, sag=3, seed=seed + 2)
    survey_chain(img, 49, SILL_Y - 7, 69, 101, sag=2, seed=seed + 3)
    iron_ring(img, 69, 97)
    P.moss_tuft(img, 30, SILL_Y, 4, seed=seed)

    # right: the deed's pendant seal on gold ribbons
    cx, cy, rad = PENDANT
    for (ax, lean) in ((cx - 3, -1), (cx + 2, 1)):
        for k in range(cy - DEED[1] - DEED[3] + 1):
            yy = DEED[1] + DEED[3] - 1 + k
            xx = ax + (lean * k) // 6
            P.put(img, xx - 1, yy, INK[1]); P.put(img, xx, yy, GOLD[2]); P.put(img, xx + 1, yy, GOLD[0])
            P.put(img, xx + 2, yy, INK[0])
    P.wax_seal(img, cx, cy, rad, BLOOD, seed)
    press_emblem(img, cx, cy, KEY_EMBLEM if rent else STAKE_EMBLEM)

    # the sill on the right: a rolled writ, a stake, a candle
    P.sprite(img, 118, SILL_Y - 7, ROLLED_WRIT)
    stake(img, 146, SILL_Y + 1, 14, seed + 2)
    fx, fy = P.candle(img, 160, SILL_Y - 9, height=7, lit=True, holder='iron', seed=seed)
    P.glow(img, fx, fy + 2, 12, 'ember')
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# plot_list / plot_manage backgrounds
# ---------------------------------------------------------------------------

def paint_list_background(key, seed):
    img = C.base_background(key, seed=seed)
    s = geo.skin(key)
    H = s.height
    P.gold_filigree(img, s.width // 2 - 5, H - 4, 'flourish')
    C.finish_background(img, key)
    return img


def paint_manage_background(key, seed):
    """Static cells 22-23 (x 79..114, y 53..70) under the two native wells:
    a small waymarker on the seam between them, a stake either side and the
    surveyor's chain swagged across, all standing in a strip of earth."""
    img = C.base_background(key, seed=seed)
    ground = 68
    earth(img, 80, 113, ground, seed, moss=True)
    waymarker(img, (93, ground - 10, 9, 11), seed, mark=False, moss=True)
    P.sprite(img, 95, ground - 5, ['qqqqq', '..n..'])    # a tiny benchmark
    stake(img, 82, ground + 1, 9, seed)
    stake(img, 107, ground + 1, 9, seed + 1, lean=0)
    survey_chain(img, 87, ground - 7, 93, ground - 5, sag=1, seed=seed + 2, shadow=None)
    survey_chain(img, 102, ground - 5, 107, ground - 7, sag=1, seed=seed + 3, shadow=None)
    s = geo.skin(key)
    P.gold_filigree(img, s.width // 2 - 5, s.height - 4, 'flourish')
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def touch_button(img, key, b, seed):
    """Hand touches on the shared grammar, kept to the rims (never near the
    lettering): a moss-green gem in the primary plates' top rim (the land),
    a soul rune on Teleport's, a blood_0 hem on wide danger cloth."""
    kind = C.button_kind(b)
    bx, by, bw, bh = b.body.tuple()
    cx = bx + bw // 2
    if kind == 'primary':
        gem = ['OZzO', 'Ozjo', '.OO.'] if b.id != 'teleport' else ['OLlO', 'Olko', '.OO.']
        P.sprite(img, cx - 2, by, gem)
        if bh >= 30:
            P.sprite(img, cx - 2, by + bh - 3, ['.OO.', 'Ohgo', 'OggO'])
    elif kind == 'danger' and bw >= 50 and bh >= 30:
        P.hline(img, bx + 2, bx + bw - 3, by + bh - 2, BLOOD[0])


def paint_buttons(key, seed, root=None):
    s = geo.skin(key)
    written = []
    for b in s.buttons:
        img = C.paint_button(key, b.id, seed=seed + len(b.id))
        touch_button(img, key, b, seed)
        C.finish_button(img, key, b.id)
        states = C.button_states(img, key, b.id)
        written += C.save_button_states(states, key, b.id, root=root)
    return written


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def posted_plat(img, x, y, seed):
    """A survey plat nailed to the wall: vellum with a dashed blood parcel
    outline, stake ticks at its corners and a small compass needle."""
    w, h = 24, 22
    m = deckle_mask(rect_mask(x, y, w, h), (x, y, w, h), 'tblr', seed)
    paint_paper(img, m, seed)
    px0, py0, pw, ph = x + 4, y + 5, 13, 11
    pts = []
    for k in range(pw):
        pts += [(px0 + k, py0), (px0 + k, py0 + ph - 1)]
    for k in range(ph):
        pts += [(px0, py0 + k), (px0 + pw - 1, py0 + k)]
    for (i, (qx, qy)) in enumerate(sorted(set(pts))):
        if (qx + qy) % 2 == 0:
            P.put(img, qx, qy, BLOOD[1])
    for (qx, qy) in ((px0, py0), (px0 + pw - 1, py0), (px0, py0 + ph - 1), (px0 + pw - 1, py0 + ph - 1)):
        P.put(img, qx, qy, INK[0])
    P.sprite(img, x + w - 5, y + 4, ['.t.', '.s.', '.i.', '.i.'])
    P.rivet(img, x + w // 2 - 1, y - 1, 'iron', 3)


def writ_rack(img, x, y, seed):
    """A wall rack of pigeonholes, each holding a rolled writ end-on: the
    registry of every plot (wordless)."""
    cols, rows, cw, ch = 3, 3, 9, 8
    w, h = cols * cw + 1, rows * ch + 1
    P.fill(img, (x, y, w, h), INK[1])
    P.ink_outline(img, (x - 1, y - 1, w + 2, h + 2), 'ink_1', radius=0, heavy='br')
    for i in range(cols + 1):
        P.vline(img, x + i * cw, y, y + h - 1, UMBER[2])
        if i < cols:
            P.vline(img, x + i * cw + 1, y + 1, y + h - 2, INK[0])     # shadow inside each hole
    for j in range(rows + 1):
        P.hline(img, x, x + w - 1, y + j * ch, UMBER[3] if j < rows else UMBER[2])
    r = P._rng(seed, 'rack')
    for j in range(rows):
        for i in range(cols):
            if r.random() < 0.15:
                continue                         # an empty hole: a claim struck off
            # a rolled writ lying in the hole, its spiral end towards us
            ox, oy = x + i * cw + 1, y + j * ch + 3
            P.sprite(img, ox, oy, ['.oooooo.', 'oyyyxxwo', 'owwvvvio', '.oooooo.'])
            if r.random() < 0.6:
                P.put(img, ox + 3 + (i + j) % 2, oy + 1, BLOOD[1]); P.put(img, ox + 3 + (i + j) % 2, oy + 2, BLOOD[0])


def frame_strips(img, a, seed):
    """Chains from the corners to the plaque, a seal on the plaque, swags
    along the bottom strip between gold rivets."""
    H, W = a.h, a.w
    P.chain(img, 12, 4, W // 2 - 22, 4, sag=2, seed=seed + 11)
    P.chain(img, W // 2 + 21, 4, W - 13, 4, sag=2, seed=seed + 12)
    P.wax_seal(img, W // 2, 4, 3, BLOOD, seed)
    for x0, x1 in ((8, 120), (136, W - 9)):
        survey_chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3); P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur')


def paint_frame(key, seed):
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, a.id, seed=seed)
    wall = img.copy()
    L, R, H = a.left_panel.x, a.right_panel.x, a.h
    tall = H >= 230
    rent = key == 'plot_rent'

    # ---- left panel: moss banner, sconce, the waymarker on its earth, stakes
    P.chain(img, L + 9, 9, L + 9, 13, seed=seed, shadow=None)
    P.chain(img, L + 29, 9, L + 29, 13, seed=seed + 1, shadow=None)
    C.side_banner(img, geo.Rect(L + 4, 0, 32, 0), y=15, seed=seed, ramp=MOSS,
                  crest='key' if rent else 'chevron', h=34 if tall else 28)
    heal(img, wall, (L, 0, a.left_panel.w, 60))
    fy0 = 66 if tall else 56
    fx, fy = sconce(img, L + 21, fy0, seed)
    P.glow(img, fx, fy + 2, 13, 'ember')
    g0 = 140 if tall else 116
    earth(img, L + 4, L + 35, g0, seed + 4)
    waymarker(img, (L + 13, g0 - 30, 14, 31), seed, mark=True)
    stake(img, L + 5, g0 + 1, 12, seed + 5)
    stake(img, L + 30, g0 + 1, 10, seed + 6)
    survey_chain(img, L + 10, g0 - 8, L + 13, g0 - 6, sag=0, seed=seed + 7, shadow=None)
    survey_chain(img, L + 27, g0 - 6, L + 30, g0 - 7, sag=0, seed=seed + 8, shadow=None)
    # a spare surveyor's chain hung in two swags between wall hooks
    hy = 166 if tall else 132
    hook(img, L + 7, hy); hook(img, L + 33, hy)
    survey_chain(img, L + 7, hy + 4, L + 33, hy + 4, sag=9 if tall else 6, seed=seed + 9)
    survey_chain(img, L + 7, hy + 4, L + 33, hy + 4, sag=15 if tall else 11, seed=seed + 10)
    if tall:
        P.crack(img, L + 33, 196, 7, seed=seed, colour=STONE[0], light=STONE[3])
        icons.draw_motif(img, 'brazier', L + 15, H - 36)        # a brazier by the boundary
        P.glow(img, L + 20, H - 36, 10, 'ember')
    icons.draw_motif(img, 'bone', L + 4, H - 17)

    # ---- right panel: lantern, ledge with the rolled writ, the posted plat
    P.chain(img, R + 20, 4, R + 20, 14, seed=seed + 2)
    icons.draw_motif(img, 'lantern', R + 16, 15)
    P.glow(img, R + 20, 20, 12, 'ember')
    ly = 44 if tall else 40
    ledge(img, R + 4, ly, 32)
    P.sprite(img, R + 6, ly - 8, ROLLED_WRIT)
    cfx, cfy = P.candle(img, R + 28, ly - 9, height=7, lit=True, holder='gold', seed=seed + 5)
    P.glow(img, cfx, cfy + 2, 10, 'ember')
    P.moss_tuft(img, R + 10, ly + 5, 5, seed=seed + 3)
    if key == 'plot_list':
        writ_rack(img, R + 6, ly + 20, seed)
        py = ly + 54
    else:
        posted_plat(img, R + 8, ly + 22, seed + 7)
        py = ly + 52
    if rent:
        hook(img, R + 20, py + 2)
        P.chain(img, R + 20, py + 6, R + 20, py + 9, seed=seed, shadow=None)
        icons.draw_motif(img, 'key', R + 15, py + 10)
    elif tall:
        C.side_banner(img, geo.Rect(R + 4, 0, 32, 0), y=py + 4, seed=seed + 1, ramp=BLOOD,
                      crest='flame', h=28)
        heal(img, wall, (R, py, a.right_panel.w, 40))
    if tall or not rent:
        fx, fy = sconce(img, R + 21, 172 if tall else 104, seed + 8)
        P.glow(img, fx, fy + 2, 12, 'ember')
    icons.draw_motif(img, 'gargoyle', R + 22, H - 26)
    P.crack(img, R + 6, H - 34, 7, seed=seed + 5, colour=STONE[0], light=STONE[3])
    frame_strips(img, a, seed)
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------

def paint_background(key, seed):
    if key in ('plot_buy', 'plot_rent'):
        return paint_buy_background(key, seed)
    if key == 'plot_list':
        return paint_list_background(key, seed)
    return paint_manage_background(key, seed)


def paint(key, root=None):
    seed = SEED[key]
    s = geo.skin(key)
    written = []
    bg = paint_background(key, seed)
    written.append(C.save_png(bg, s.background_path if root is None else Path(root) / 'menu' / f'{key}.png'))
    written += paint_buttons(key, seed, root)
    a = s.layer()
    fr = paint_frame(key, seed)
    written.append(C.save_png(fr, s.frame_path(a.id) if root is None else
                              Path(root) / 'frames' / key / f'{a.id}.png'))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--skin', choices=SKINS, action='append')
    ap.add_argument('--out-root', help='directory laid out like textures/ (default: pack-source)')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        for p in paint(key, args.out_root):
            print('WROTE', p)


if __name__ == '__main__':
    main()
