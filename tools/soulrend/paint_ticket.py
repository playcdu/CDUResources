#!/usr/bin/env python3
"""Soulrend painter "ticket": ticket_valid and ticket_invalid.

    python tools/soulrend/paint_ticket.py                    # both skins -> pack-source
    python tools/soulrend/paint_ticket.py --skin ticket_valid
    python tools/soulrend/paint_ticket.py --out-root DIR     # DIR laid out like textures/

Family identity: a wax-sealed writ of passage.

* ticket_valid: a crisp vellum writ pinned to the umber sheet by iron
  rivets, ruled in faint lines (no words) with an illuminated gold-and-blood
  box and rubric marks; the native display item sits in an iron-cornered
  window cut through the writ; a folded plica carries a blood ribbon through
  two iron eyelets down to a heavy pendant wax seal pressed with a portcullis
  gate; on the sill below an inkpot and quill, a stick of sealing wax, a gold
  signet and a lit candle. Frame: a raised portcullis with the lit passage
  beyond, blood banners, lit sconces and lantern, the writ posted on the wall.
* ticket_invalid: the same writ, burnt along its right edge, its top-left
  corner torn away and a rip up from its bottom edge, ruled lines broken; the
  ribbon cut, the seal broken in two; cold ash, burnt scraps, a snuffed
  candle with a curl of smoke. Frame: the portcullis down, the banner
  charred, sconces and lantern dark, the posted writ burnt.

Deterministic (fixed seeds, no clock). Only ticket_valid / ticket_invalid
PNGs are written. Licence: code MIT; artwork CC0-1.0.
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
from palette import BLOOD, EMBER, GOLD, INK, IRON, STONE, UMBER, VELLUM  # noqa: E402

SKINS = ('ticket_valid', 'ticket_invalid')
SEED = {'ticket_valid': 31, 'ticket_invalid': 37}

# --- writ geometry (background coordinates) ---------------------------------
WRIT = (14, 17, 148, 53)            # main sheet: x 14..161, y 17..69
TAB = (66, 60, 44, 25)              # lower tab (plica) between the buttons: y .. 84
FOLD_Y = 77                         # the plica fold line
EYELETS = ((78, 79), (93, 79))      # iron eyelets the ribbon passes through (top-left)
SEAL = (88, 94, 9)                  # pendant seal centre and radius
WINDOW = (78, 52, 20, 20)           # slot 22 clearance (never painted)
BURN_X = 137                        # where the burn starts on ticket_invalid
RIBBON = GOLD                       # the seal's silk: gold, so the blood wax reads against it


# ---------------------------------------------------------------------------
# Small helpers (local: the shared modules are not edited)
# ---------------------------------------------------------------------------

def rect_mask(x, y, w, h):
    return {(i, j) for j in range(y, y + h) for i in range(x, x + w)}


def mask_edges(mask):
    return {p for p in mask if any((p[0] + dx, p[1] + dy) not in mask
                                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


def paint_paper(img, mask, seed, ramp=VELLUM, fibres=True):
    """Vellum filling an arbitrary pixel ``mask``: ramp[2] body, ramp[3] lit
    row/column under the top/left edges, ramp[1] row/column inside the
    bottom/right edges, ink_1 outline that turns ink_0 on the bottom/right."""
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
    """Give back the wall wherever a primitive punched alpha-0 holes inside
    ``box`` (banner tatters, tears with no backing)."""
    x, y, w, h = box
    for yy in range(max(0, y), min(img.height, y + h)):
        for xx in range(max(0, x), min(img.width, x + w)):
            if img.getpixel((xx, yy))[3] == 0 and before.getpixel((xx, yy))[3]:
                img.putpixel((xx, yy), before.getpixel((xx, yy)))


def ribbon(img, pts, ramp=BLOOD, width=2):
    """A silk strand along ``pts`` (centres, top to bottom): ``width`` px of
    cloth (lit ramp[2] left, ramp[0] right) inside an ink outline."""
    path = []
    for a, b in zip(pts, pts[1:]):
        seg = P.line_points(*a, *b)
        path += seg if not path else seg[1:]
    body = set()
    for (x, y) in path:
        for k in range(width):
            body.add((x + k, y))
    edge = {(x + dx, y) for (x, y) in body for dx in (1, -1)} - body
    for (x, y) in edge:
        P.put(img, x, y, INK[0] if (x - 1, y) in body else INK[1])
    for (x, y) in body:
        left = (x - 1, y) not in body
        P.put(img, x, y, ramp[2] if left else (ramp[0] if (x + 1, y) not in body and width > 1 else ramp[1]))
    return path


def ribbon_tail(img, x, y, length, lean, ramp=None, seed=0, cut=True):
    """A hanging ribbon end 4 px wide from (x, y) leaning ``lean`` px over its
    length: lit ramp[2] left, ramp[1] body, ramp[0] shaded right, ink rims;
    finished with a swallowtail notch (``cut``) or a frayed end."""
    ramp = ramp or RIBBON
    pts = [(x + round(lean * k / max(1, length - 1)), y + k) for k in range(length)]
    for i, (px, py) in enumerate(pts):
        if cut and i == length - 1:
            # swallowtail: two ink points either side of the V notch, whose
            # pixels keep whatever lies behind the ribbon
            P.put(img, px, py, INK[1]); P.put(img, px + 3, py, INK[0])
            continue
        P.put(img, px - 1, py, INK[1])
        P.put(img, px + 4, py, INK[0])
        if cut and i == length - 2:
            P.sprite(img, px, py, ['hoOg'], {'h': ramp[2], 'g': ramp[0]})
            continue
        P.put(img, px, py, ramp[2]); P.put(img, px + 1, py, ramp[1]); P.put(img, px + 2, py, ramp[1])
        P.put(img, px + 3, py, ramp[0])
        if i % 6 == 4:
            P.put(img, px + 2, py, ramp[0])           # a soft twist in the silk
    if not cut:
        r = P._rng(seed, 'fray', x, y)
        ex, ey = pts[-1]
        for k in range(4):
            if r.random() < 0.75:
                P.put(img, ex + k, ey + 1, ramp[0])
                if r.random() < 0.5:
                    P.put(img, ex + k, ey + 2, INK[1])
    return pts


def eyelet(img, x, y):
    """A forged iron eyelet (5x5) punched through vellum; dark centre."""
    P.sprite(img, x, y, ['.ooo.', 'oddco', 'odOao', 'ocaao', '.ooo.'])


GATE = ['..###..', '.#...#.', '#.#.#.#', '#.#.#.#', '#######', '#.#.#.#', '#.#.#.#']


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


def seal_layer(size, cx, cy, r, seed, emblem=True):
    """Paint a pendant seal on its own transparent layer."""
    lay = C.new(*size)
    P.wax_seal(lay, cx, cy, r, BLOOD, seed)
    if emblem:
        press_emblem(lay, cx, cy, GATE)
    return lay


def composite(img, lay, dx=0, dy=0):
    """Paste opaque pixels of ``lay`` onto ``img`` offset by (dx, dy)."""
    src = lay.load()
    for y in range(lay.height):
        for x in range(lay.width):
            p = src[x, y]
            if p[3]:
                P.put(img, x + dx, y + dy, p[:3])


def split_seal(lay, cx, cy, r, seed):
    """Break a seal layer in two along a jagged crack that wanders down
    through the middle. Returns (left, right) layers whose broken faces show
    the thick wax: an ink_0 fracture edge and a blood_0 band behind it."""
    rr = P._rng(seed, 'split')
    split = {}
    off = 0
    for y in range(cy - r - 1, cy + r + 2):
        if rr.random() < 0.6:
            off = max(-2, min(2, off + rr.choice((-1, 1))))
        split[y] = cx + off
    left, right = C.new(*lay.size), C.new(*lay.size)
    src = lay.load()
    for y in range(lay.height):
        for x in range(lay.width):
            p = src[x, y]
            if not p[3] or y not in split:
                continue
            if x < split[y]:
                left.putpixel((x, y), p)
            elif x > split[y]:
                right.putpixel((x, y), p)
    for lay2, side in ((left, -1), (right, 1)):
        px = lay2.load()
        for y, s in split.items():
            x = s + side
            if 0 <= y < lay2.height and px[x, y][3]:
                P.put(lay2, x, y, INK[0])
                if px[x + side, y][3] and px[x + side, y][:3] != INK[0]:
                    P.put(lay2, x + side, y, BLOOD[0])
    return left, right


def smoke(img, x, y, height, seed, colours=(IRON[2], IRON[1])):
    """A thin curl of cold smoke rising from (x, y): a 1 px S-curve that
    breaks up towards the top."""
    r = P._rng(seed, 'smoke', x, y)
    cx = x
    drift = r.choice((-1, 1))
    for k in range(height):
        yy = y - k
        if k and k % 3 == 0:
            cx += drift
            if r.random() < 0.45:
                drift = -drift
        if k > height * 0.6 and k % 2:
            continue
        P.put(img, cx, yy, colours[0] if k < height // 2 else colours[1])
        if k % 4 == 1 and k < height - 2:
            P.put(img, cx + drift, yy, colours[1])


def snuffed_candle(img, x, y, height, seed, holder='iron', smoke_h=8):
    """An unlit candle with a charred, bent wick and a curl of cold smoke."""
    P.candle(img, x, y, height=height, lit=False, holder=holder, seed=seed)
    P.put(img, x + 1, y - 1, INK[0]); P.put(img, x + 2, y - 2, INK[1])
    smoke(img, x + 2, y - 3, smoke_h, seed)


def ash(img, x, y, w, seed, embers=True):
    """A low heap of cold ash on a ledge or sill whose base row is ``y``."""
    r = P._rng(seed, 'ash', x, y)
    h = max(2, w // 4)
    for i in range(w):
        t = 1 - abs(i - (w - 1) / 2) / ((w + 1) / 2)
        col_h = max(1, round(h * t + r.choice((0, 0, 1))))
        for k in range(col_h):
            c = IRON[2] if k == col_h - 1 else IRON[1]
            if k == col_h - 1 and r.random() < 0.3:
                c = IRON[3]
            P.put(img, x + i, y - k, c)
    P.hline(img, x, x + w - 1, y + 1, INK[1])
    if embers:
        for _ in range(max(1, w // 6)):
            P.put(img, x + r.randint(2, w - 3), y - r.randint(0, 1), EMBER[0])


def scrap(img, x, y, flip=False):
    """A small burnt scrap of vellum with charred edges."""
    P.sprite(img, x, y, ['.Owwo.', 'Ovxxwo', 'oxwwve', '.OeOO.'], flip_x=flip)


def window_brackets(img, hole):
    """Iron corner brackets with gold rivets round a socket window: the
    'iron-cornered cut-out' framing the featured native item. The brackets
    sit outside the socket's three rings (Chebyshev distance 4..6)."""
    x, y, w, h = hole
    tl = ['oooooooo', 'odddccbo', 'odHoooo.', 'odoo....', 'oco.....', 'oco.....', 'obo.....', 'ooo.....']
    P.sprite(img, x - 6, y - 6, tl)
    P.sprite(img, x + w - 2, y - 6, tl, flip_x=True)
    P.sprite(img, x - 6, y + h - 2, tl, flip_y=True)
    P.sprite(img, x + w - 2, y + h - 2, tl, flip_x=True, flip_y=True)


INKPOT = [
    '..ooooo..',
    '..oOOOo..',
    '...oco...',
    '.ooccbaoo',
    'ocddcbbao',
    'odcbbbbao',
    'ocbbbbbao',
    'ocbbbbaao',
    'obbbbaaao',
    '.oaaaaao.',
    '..ooooo..',
]
QUILL = [
    '.........oo',
    '........oyo',
    '.......oyxo',
    '......oyxwo',
    '.....oyxwo.',
    '....oyxwvo.',
    '....oyxwo..',
    '...oyxwo...',
    '...oxwvo...',
    '..oywo.....',
    '..oxo......',
    '.oio.......',
    '.oi........',
]
WAX_STICK = [
    '.ooooooooooooo..',
    'otssssssssssrOo.',
    'osrrrrrrrrrrrOiO',
    '.OOOOOOOOOOOOO..',
]
SIGNET = [
    '..ooo..',
    '.o332o.',
    '.o221o.',
    '..o20..',
    '..o1o..',
    '..o2o..',
    '..o1o..',
    '.ohHgo.',
    'oHhhhgo',
    'ohhhggo',
    'OOOOOOO',
]


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def writ_mask(seed, burnt=False):
    x, y, w, h = WRIT
    m = rect_mask(*WRIT) | rect_mask(*TAB)
    tx, ty, tw, th = TAB
    for k in range(3):                                  # chamfer the tab's foot
        for j in range(3 - k):
            m.discard((tx + k, ty + th - 1 - j)); m.discard((tx + tw - 1 - k, ty + th - 1 - j))
    m = deckle_mask(m, WRIT, 'tlr' if not burnt else 'tl', seed)
    m = deckle_mask(m, (tx, y + h, tw, ty + th - y - h), 'b', seed + 1)
    if burnt:
        # the top-left corner torn away along a ragged diagonal
        r = P._rng(seed, 'corner')
        for j in range(0, 14):
            reach = 15 - j + r.choice((0, 0, 1, -1))
            for i in range(0, max(0, reach)):
                m.discard((x + i, y + j))
    return m


def illuminated_box(img, bx, by):
    """An illuminated box opening the writ: a gold-framed blood field with a
    gold fleur (ornament, never a letter)."""
    P.ink_outline(img, (bx, by, 11, 11), 'ink_1', radius=0, heavy='br', fill_colour=BLOOD[1])
    P.hline(img, bx + 1, bx + 9, by + 1, GOLD[2]); P.vline(img, bx + 1, by + 1, by + 9, GOLD[2])
    P.hline(img, bx + 2, bx + 9, by + 9, GOLD[0]); P.vline(img, bx + 9, by + 2, by + 9, GOLD[0])
    P.put(img, bx + 9, by + 1, GOLD[1]); P.put(img, bx + 1, by + 9, GOLD[1])
    P.sprite(img, bx + 3, by + 3, ['..H..', '.hHh.', 'h.H.h', '..h..', '.ggg.'])
    P.put(img, bx + 2, by + 2, BLOOD[2])


def paint_writ_lines(img, mask, seed, burnt=False):
    """Ruled lines (no words): faint vellum_0 rules in two paragraphs round
    the window, a dotted heading rule, rubric marks, an illuminated box."""
    r = P._rng(seed, 'lines')
    x0, x1 = 22, 153
    wl, wr = WINDOW[0] - 9, WINDOW[0] + WINDOW[2] + 9   # keep clear of the brackets
    rows = list(range(36, 68, 4))
    for i, yy in enumerate(rows):
        start = 36 if yy < 34 else x0
        segs = [(start, x1)] if yy < 44 else [(x0, wl), (wr, x1)]
        para_end = i in (1, 5)
        for (a, b) in segs:
            if para_end and b == x1:
                b -= r.randint(20, 36)
            elif b == wl and i == 7:
                b -= 14
            for xx in range(a, b + 1):
                if (xx, yy) in mask and P.get(img, xx, yy)[:3] in (VELLUM[2], VELLUM[3], VELLUM[1]):
                    P.put(img, xx, yy, VELLUM[0])
        if i in (2, 6):
            P.sprite(img, x0 - 2, yy - 1, ['ts', 'sr'])             # rubric mark
    # the two ruled lines beside the illuminated box
    for yy in (25, 29):
        for xx in range(36, 154):
            if (xx, yy) in mask and P.get(img, xx, yy)[:3] in (VELLUM[2], VELLUM[3], VELLUM[1]):
                if not (80 <= xx <= 96 and yy == 25):
                    P.put(img, xx, yy, VELLUM[0])
    if not burnt:
        illuminated_box(img, 22, 21)
    else:
        illuminated_box(img, 22, 21)
    P.gold_filigree(img, 83, 24, 'flourish')


def paint_plica(img, mask):
    """The folded foot of the writ: a crease (vellum_0 valley, vellum_3
    ridge) and the doubled vellum below it in vellum_1."""
    tx, ty, tw, th = TAB
    for xx in range(tx + 1, tx + tw - 1):
        if (xx, FOLD_Y) in mask and (xx, FOLD_Y - 1) in mask:
            P.put(img, xx, FOLD_Y, VELLUM[0])
        if (xx, FOLD_Y + 1) in mask and (xx, FOLD_Y + 2) in mask:
            P.put(img, xx, FOLD_Y + 1, VELLUM[3])
    for yy in range(FOLD_Y + 2, ty + th):
        for xx in range(tx + 1, tx + tw - 1):
            if (xx, yy) in mask and (xx, yy + 1) in mask and P.get(img, xx, yy)[:3] in (VELLUM[2], VELLUM[3]):
                P.put(img, xx, yy, VELLUM[1])


def writ_shadow(img, mask):
    """1 px cast shadow of the writ on the sheet (below-right)."""
    for (x, y) in mask:
        q = (x + 1, y + 1)
        if q not in mask and P.get(img, *q)[:3] in UMBER:
            P.put(img, q[0], q[1], INK[1])


def corner_pins(img, mask, burnt=False):
    """Iron rivets pinning the writ's corners to the sheet."""
    for (x, y) in ((17, 20), (157, 20), (17, 64), (157, 64)):
        if all((x + i, y + j) in mask for i in range(3) for j in range(3)):
            P.rivet(img, x, y, 'iron', 3)


def seal_ribbon(img, burnt):
    """The gold silk loop across the plica between the two iron eyelets; on
    the invalid writ it is cut through beside the left eyelet."""
    (lx, ly), (rx, ry) = EYELETS
    y0 = ly + 1
    rr = RIBBON
    P.hline(img, lx + 4, rx, y0, INK[1])
    P.hline(img, lx + 4, rx, y0 + 1, rr[2])
    P.hline(img, lx + 4, rx, y0 + 2, rr[1])
    P.hline(img, lx + 4, rx, y0 + 3, INK[0])
    for xx in range(lx + 6, rx, 5):
        P.put(img, xx, y0 + 2, rr[0])                 # the silk's twist
    if burnt:
        # cut: the loop parted beside the left eyelet, ends frayed, the
        # plica showing through the gap
        for xx in (lx + 6, lx + 7, lx + 8):
            for yy in range(y0, y0 + 4):
                P.put(img, xx, yy, VELLUM[1])
        P.sprite(img, lx + 5, y0, ['o..o', 'h..g', 'g..h', 'O..O'], {'h': rr[1], 'g': rr[0]})
        P.put(img, lx + 6, y0 + 1, rr[0]); P.put(img, lx + 8, y0 + 2, rr[0])
    eyelet(img, lx, ly)
    eyelet(img, rx, ry)


def paint_background(key, seed):
    burnt = key == 'ticket_invalid'
    img = C.base_background(key, seed=seed)
    mask = writ_mask(seed, burnt)
    writ_shadow(img, mask)
    paint_paper(img, mask, seed)
    paint_writ_lines(img, mask, seed, burnt)
    paint_plica(img, mask)
    corner_pins(img, mask, burnt)
    P.socket_well(img, [WINDOW])
    window_brackets(img, WINDOW)
    seal_ribbon(img, burnt)

    cx, cy, rad = SEAL
    sill = 125
    if not burnt:
        ribbon_tail(img, cx - 6, cy + rad - 6, 17, -7, seed=seed)
        ribbon_tail(img, cx + 2, cy + rad - 6, 15, 7, seed=seed + 1)
        composite(img, seal_layer(img.size, cx, cy, rad, seed))
        # the sill: inkpot and quill, sealing wax, signet, a lit candle
        P.sprite(img, 19, sill - 22, QUILL)
        P.sprite(img, 15, sill - 10, INKPOT)
        P.sprite(img, 30, sill - 3, WAX_STICK)
        P.sprite(img, 130, sill - 10, SIGNET)
        P.sprite(img, 139, sill - 1, ['.ss.', 'otsr'])
        fx, fy = P.candle(img, 152, sill - 11, height=8, lit=True, holder='iron', seed=seed)
        P.glow(img, fx, fy + 2, 12, 'ember')
    else:
        lay = seal_layer(img.size, cx, cy, rad, seed)
        left, right = split_seal(lay, cx, cy, rad, seed)
        # the right half still hangs on its tail; the left half has slipped
        # and swung away, a frayed scrap of silk still caught in it
        ribbon_tail(img, cx + 3, cy + rad - 6, 15, 7, seed=seed + 1)
        composite(img, right, 2, 0)
        ribbon_tail(img, cx - 8, cy + rad - 2, 7, -3, seed=seed + 2, cut=False)
        composite(img, left, -3, 3)
        # wax crumbs on the sill under the break
        for (wx, wy) in ((82, sill), (91, sill)):
            P.sprite(img, wx, wy - 2, ['.o.', 'ost', 'Orr'])
        # cold ash, burnt scraps, a snuffed candle
        ash(img, 16, sill, 24, seed)
        scrap(img, 44, sill - 4)
        scrap(img, 118, sill - 5, flip=True)
        scrap(img, 104, sill - 2)
        snuffed_candle(img, 152, sill - 11, 8, seed, smoke_h=12)
        ash(img, 138, sill, 9, seed + 3, embers=False)
        burn_edge(img, mask, seed)
        tear(img, 48, WRIT[1] + WRIT[3] - 1, 12, seed)
    C.finish_background(img, key)
    return img


def burn_edge(img, mask, seed):
    """Burn the writ's right edge: a ragged charred margin (ink_0 crust),
    then umber_2 / umber_3 scorch and vellum_0 browning that creep in by
    seeded runs (flat stains, no gradient)."""
    x, y, w, h = WRIT
    r = P._rng(seed, 'burn')
    depth = 0
    for yy in range(y, y + h + 1):
        if r.random() < 0.6:
            depth = max(0, min(9, depth + r.choice((-2, -1, 1, 2))))
        edge = BURN_X + 12 - depth - (3 if yy < y + 6 else 0)
        # beyond the char the sheet shows through
        for xx in range(edge + 1, x + w + 1):
            if (xx, yy) in mask or (xx - 1, yy - 1) in mask:
                P.put(img, xx, yy, UMBER[1])
        if not any((xx, yy) in mask for xx in range(x, edge)):
            continue
        P.put(img, edge, yy, INK[0])
        P.put(img, edge - 1, yy, EMBER[0] if r.random() < 0.2 else UMBER[0])
        reach = r.randint(1, 3)
        for k in range(2, 2 + reach):
            P.put(img, edge - k, yy, UMBER[2] if k == 2 else UMBER[3])
        for k in range(2 + reach, 2 + reach + r.randint(1, 4)):
            if P.get(img, edge - k, yy)[:3] in VELLUM:
                P.put(img, edge - k, yy, VELLUM[0])
    # a cast shadow under the burnt margin and drifting ash flecks
    for (fx, fy) in ((158, 22), (160, 31), (156, 44), (163, 57), (159, 66)):
        P.put(img, fx, fy, IRON[2] if fy % 2 else IRON[1])


def tear(img, x, y, length, seed):
    """A rip running up into the writ from its bottom edge: a narrowing
    wedge of sheet between two ink edges, a lit fibre lip on the left."""
    r = P._rng(seed, 'tear', x, y)
    cx = x
    for k in range(length):
        yy = y - k
        if k and r.random() < 0.45:
            cx += r.choice((-1, 1))
        gap = 2 if k < length // 3 else (1 if k < 2 * length // 3 else 0)
        P.put(img, cx - 1, yy, VELLUM[3])
        P.put(img, cx, yy, INK[1])
        for g in range(gap):
            P.put(img, cx + 1 + g, yy, UMBER[0])
        P.put(img, cx + 1 + gap, yy, INK[0])
        P.put(img, cx + 2 + gap, yy, VELLUM[1])


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def paint_buttons(key, seed, root=None):
    s = geo.skin(key)
    written = []
    for b in s.buttons:
        img = C.paint_button(key, b.id, seed=seed)
        if b.id == 'redeem':
            cx = b.w // 2
            # a blood seal-gem set in the top rim, gold flourish under the lettering
            P.sprite(img, cx - 2, 0, ['OttO', 'Osro', '.OO.'])
            P.gold_filigree(img, cx - 5, b.h - 6, 'flourish')
        elif b.id == 'cancel':
            # a dog-eared corner fold at the top-right of the strip
            P.page_curl(img, b.body.tuple(), 'tr', 4)
        C.finish_button(img, key, b.id)
        states = C.button_states(img, key, b.id)
        written += C.save_button_states(states, key, b.id, root=root)
    return written


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def ledge(img, x, y, w):
    """A short carved stone ledge on two iron brackets."""
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0)
    for bx in (x + 2, x + w - 4):
        P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


def sconce(img, x, y, seed, lit=True):
    """An iron wall sconce with a candle: lit (returns the flame centre) or
    snuffed with a curl of smoke (returns None)."""
    P.sprite(img, x - 3, y + 8, ['occcco', '.obao.', '..oo..', '..oa..', '..ob..', '...o..'])
    if lit:
        return P.candle(img, x - 1, y, height=6, lit=True, holder=None, seed=seed)
    snuffed_candle(img, x - 1, y, 6, seed, holder=None, smoke_h=12)
    return None


def portcullis(img, box, seed, raised=True):
    """An arch niche with an iron portcullis. Raised: only its spiked foot
    shows under the arch and the passage beyond is lit (returns the light
    centre). Lowered: a full grid of iron bars over a cold dark passage."""
    x, y, w, h = box
    interior = P.arch_niche(img, box, seed=seed, interior=INK[1])
    ys = sorted({p[1] for p in interior})
    xs = sorted({p[0] for p in interior})
    top, bot = ys[0], ys[-1]
    left, right = xs[0], xs[-1]
    if raised:
        # the passage: umber walls receding to a lit doorway, flagstone floor
        for (px, py) in interior:
            P.put(img, px, py, UMBER[0])
        door = (left + 6, top + 9, right - left - 11, bot - top - 12)
        P.fill(img, door, UMBER[2])
        P.hline(img, door[0], door[0] + door[2] - 1, door[1], UMBER[3])
        P.vline(img, door[0] - 1, door[1], bot - 3, INK[1])
        P.vline(img, door[0] + door[2], door[1], bot - 3, INK[1])
        for (px, py) in interior:
            if py >= bot - 2:
                P.put(img, px, py, STONE[1] if (px + (py - bot)) % 5 else STONE[0])
        # raised gate: a lit bottom rail and its spikes hanging under the arch
        for xx in range(left, right + 1):
            if (xx, top + 2) in interior:
                P.put(img, xx, top + 2, IRON[2])
                P.put(img, xx, top + 3, INK[0])
        for bx in range(left + 1, right + 1, 3):
            for yy in range(top, top + 6):
                if (bx, yy) in interior:
                    P.put(img, bx, yy, IRON[2] if yy < top + 5 else IRON[3])
        return (door[0] + door[2] // 2, door[1] + door[3] // 2 + 2)
    for (px, py) in interior:
        P.put(img, px, py, INK[0] if py > bot - 4 else INK[1])
    for bx in range(left + 1, right + 1, 3):
        for yy in range(top, bot + 1):
            if (bx, yy) in interior:
                P.put(img, bx, yy, IRON[2])
                if (bx + 1, yy) in interior:
                    P.put(img, bx + 1, yy, INK[0])
    for yy in range(top + 3, bot, 5):
        for xx in range(left, right + 1):
            if (xx, yy) in interior:
                P.put(img, xx, yy, IRON[1] if (xx - left) % 3 else IRON[3])
    for bx in range(left + 1, right + 1, 3):
        if (bx, bot) in interior:
            P.put(img, bx, bot, IRON[3])
    return None


def posted_writ(img, x, y, seed, burnt=False):
    """A small writ nailed to the wall: vellum, ruled lines, a pendant seal
    (valid) or charred away down its right side (invalid)."""
    w, h = 24, 30
    before = img.copy()
    m = deckle_mask(rect_mask(x, y, w, h), (x, y, w, h), 'tblr', seed)
    paint_paper(img, m, seed)
    for yy in range(y + 7, y + h - 7, 3):
        end = x + w - 4 - (7 if (yy - y) % 9 == 1 else 0)
        for xx in range(x + 4, end):
            if (xx, yy) in m and P.get(img, xx, yy)[:3] in VELLUM:
                P.put(img, xx, yy, VELLUM[0])
    P.gold_filigree(img, x + 7, y + 3, 'flourish')
    P.rivet(img, x + w // 2 - 1, y - 1, 'iron', 3)
    if not burnt:
        ribbon_tail(img, x + w // 2 - 3, y + h - 2, 7, -1, BLOOD, seed)
        P.wax_seal(img, x + w // 2, y + h - 3, 4, BLOOD, seed)
    else:
        P.torn_edge(img, (x + w - 10, y + 6, 10, h - 4), 'r', seed, depth=6, behind=None, burnt=True)
        P.torn_edge(img, (x, y + h - 5, w, 5), 'b', seed + 1, depth=3, behind=None, burnt=True)
        heal(img, before, (x - 2, y - 2, w + 4, h + 4))
        for (fx, fy) in ((x + w + 1, y + h + 3), (x + w - 3, y + h + 6), (x + 6, y + h + 4)):
            P.put(img, fx, fy, IRON[2])


def cold_brazier(img, x, y):
    """The brazier motif with its coals gone to ash."""
    icons.draw_motif(img, 'brazier', x, y)
    for i in range(x, x + 12):
        for j in range(y, y + 3):
            p = P.get(img, i, j)
            if p[3] and p[:3] in EMBER:
                P.put(img, i, j, IRON[2] if p[:3] == EMBER[2] else IRON[1])


def dark_lantern(img, x, y):
    """The lantern motif, unlit: cold dark glass behind the iron cage."""
    icons.draw_motif(img, 'lantern', x, y)
    for i in range(x, x + 8):
        for j in range(y, y + 9):
            p = P.get(img, i, j)
            if p[3] and p[:3] in EMBER:
                P.put(img, i, j, IRON[1] if p[:3] == EMBER[2] else INK[2])


def paint_frame(key, seed):
    s = geo.skin(key)
    a = s.layer()
    valid = key == 'ticket_valid'
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    wall = img.copy()

    # --- left panel: banner, sconce, the portcullis, a ledge, a chained key
    P.chain(img, lp.x + 9, 9, lp.x + 9, 13, seed=seed, shadow=None)
    P.chain(img, lp.x + 29, 9, lp.x + 29, 13, seed=seed + 1, shadow=None)
    C.side_banner(img, geo.Rect(lp.x + 4, 0, 32, 0), y=15, seed=seed, ramp=BLOOD, crest='key', h=36)
    if not valid:
        P.torn_edge(img, (lp.x + 13, 36, 13, 16), 'b', seed, depth=7, behind=None, burnt=True)
        for (fx, fy) in ((lp.x + 15, 56), (lp.x + 22, 59), (lp.x + 18, 62)):
            P.put(img, fx, fy, IRON[2])
    heal(img, wall, (lp.x, 0, lp.w, 70))
    fl = sconce(img, lp.x + 20, 70, seed, lit=valid)
    if fl:
        P.glow(img, fl[0], fl[1] + 2, 13, 'ember')
    g = portcullis(img, (lp.x + 7, 98, 26, 40), seed, raised=valid)
    if g:
        P.glow(img, g[0], g[1], 9, 'ember')
    ledge(img, lp.x + 5, 152, 30)
    P.moss_tuft(img, lp.x + 12, 158, 5, seed=seed)
    if valid:
        icons.draw_motif(img, 'writ', lp.x + 7, 143)
        fx, fy = P.candle(img, lp.x + 26, 144, height=6, lit=True, holder='iron', seed=seed + 3)
        P.glow(img, fx, fy + 2, 9, 'ember')
    else:
        ash(img, lp.x + 6, 150, 16, seed)
        snuffed_candle(img, lp.x + 26, 144, 5, seed + 3, smoke_h=9)
    P.chain(img, lp.x + 20, 165, lp.x + 20, 183, seed=seed + 4)
    if valid:
        icons.draw_motif(img, 'key', lp.x + 13, 184)
    else:
        P.sprite(img, lp.x + 19, 184, ['c.b', 'o.a'])            # the last link sprung open
        icons.draw_motif(img, 'key', lp.x + 24, H - 13)            # the key lies dropped
    P.crack(img, lp.x + 31, 192, 9, seed=seed, colour=STONE[0], light=STONE[3])
    if valid:
        icons.draw_motif(img, 'brazier', lp.x + 14, H - 34)
        P.glow(img, lp.x + 19, H - 34, 10, 'ember')
    else:
        cold_brazier(img, lp.x + 14, H - 34)
    icons.draw_motif(img, 'bone', lp.x + 2, H - 17)

    # --- right panel: lantern, banner, ledge, posted writ, sconce, gargoyle
    P.chain(img, rp.x + 20, 4, rp.x + 20, 18, seed=seed + 2)
    if valid:
        icons.draw_motif(img, 'lantern', rp.x + 16, 19)
        P.glow(img, rp.x + 20, 24, 12, 'ember')
    else:
        dark_lantern(img, rp.x + 16, 19)
    C.side_banner(img, geo.Rect(rp.x + 4, 0, 32, 0), y=46, seed=seed + 1, ramp=BLOOD if valid else IRON,
                  crest='tower', h=30)
    heal(img, wall, (rp.x, 40, rp.w, 40))
    ledge(img, rp.x + 4, 106, 32)
    if valid:
        icons.draw_motif(img, 'goblet', rp.x + 4, 96)
        P.sprite(img, rp.x + 14, 98, SIGNET[2:])
        fx, fy = P.candle(img, rp.x + 28, 97, height=8, lit=True, holder='gold', seed=seed + 5)
        P.glow(img, fx, fy + 2, 10, 'ember')
    else:
        P.sprite(img, rp.x + 4, 101, ['..ooooooo', '.oHrssgOo', 'ohhhhgggO', 'OOOOOOOOO'])  # goblet on its side
        snuffed_candle(img, rp.x + 28, 97, 8, seed + 5, holder='gold', smoke_h=12)
        ash(img, rp.x + 15, 105, 9, seed + 6, embers=False)
    P.moss_tuft(img, rp.x + 22, 111, 6, seed=seed + 3)
    posted_writ(img, rp.x + 8, 128, seed + 7, burnt=not valid)
    fl = sconce(img, rp.x + 21, 178, seed + 8, lit=valid)
    if fl:
        P.glow(img, fl[0], fl[1] + 2, 12, 'ember')
    icons.draw_motif(img, 'gargoyle', rp.x + 22, H - 26)
    P.crack(img, rp.x + 6, 205, 7, seed=seed + 5, colour=STONE[0], light=STONE[3])

    # --- top strip: chains from the corners to the plaque -----------------
    P.chain(img, 12, 4, a.w // 2 - 22, 4, sag=2, seed=seed + 11)
    if valid:
        P.chain(img, a.w // 2 + 21, 4, a.w - 13, 4, sag=2, seed=seed + 12)
    else:
        P.chain(img, a.w // 2 + 21, 4, a.w // 2 + 54, 5, sag=1, seed=seed + 12)   # snapped
    # a wax seal on the plaque: whole on the valid writ, cracked on the invalid
    P.wax_seal(img, a.w // 2, 4, 3, BLOOD if valid else IRON, seed)
    if not valid:
        P.put(img, a.w // 2, 3, INK[0]); P.put(img, a.w // 2 + 1, 4, INK[0]); P.put(img, a.w // 2, 5, INK[0])
    # bottom strip: chains swagged between gold rivets
    for x0, x1 in ((8, 120), (136, a.w - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3); P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur')

    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------

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
