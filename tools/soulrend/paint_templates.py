#!/usr/bin/env python3
"""Soulrend painter "templates": the six generic chest templates.

    python tools/soulrend/paint_templates.py                      # all six into pack-source
    python tools/soulrend/paint_templates.py --skin template_chest_3
    python tools/soulrend/paint_templates.py --out-root DIR       # DIR laid out like textures/

Skins: template_chest_1 .. template_chest_6 (chest_1 .. chest_6, heights
132/150/168/186/204/222). Each owns one background (menu/<key>.png) and one
outer frame (frames/<key>/menu_frame.png); there are no painted buttons.

Look: plain dark stone and iron framing for screens nobody has designed yet,
deliberately function-neutral. The sheet is the shared umber ledger with its
vellum title and inventory bands and iron sockets; the only hand touches are
iron (an iron flourish, rivets, a hairline crack) in the free rows under the
hotbar. The frame is hand-laid dungeon masonry with cracks and moss, the
ledger clamped into its niche by riveted iron straps, a blank faded banner,
an iron sconce with a lit candle, a candle in an arched niche, a barred
window on the taller sizes, an iron lantern on a hanging chain, a tether
ring, a swagged chain, a candle ledge, a worn gargoyle corbel and fallen
rubble. No coins, ledgers, seals, weapons or words: nothing implies a
purpose. Each of the six heights is composed for its own panel length (the
optional pieces appear only where they fit), never cropped.

Deterministic: fixed seeds, no clock. Licence: MIT (tooling); the artwork it
paints is CC0-1.0.
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
from palette import INK, IRON, MOSS, STONE, UMBER  # noqa: E402

KEYS = tuple(f'template_chest_{n}' for n in range(1, 7))
SEED = 41
DEFAULT_ROOT = geo.ROOT / 'pack-source' / 'assets' / 'quasar_gui' / 'textures'


# ---------------------------------------------------------------------------
# Hand-authored sprites (shared SK colour key, see primitives.SK)
# ---------------------------------------------------------------------------

# wrought-iron wall sconce: a cup on a bracket bolted to the wall
SCONCE = ['occcco', '.obao.', '..oo..', '..oa..', '..ob..', '...o..']

# tether ring: a staple plate with a heavy iron ring hanging from it
RING = [
    '...ooo...',
    '..ocdco..',
    '..obcbo..',
    '...oco...',
    '..ocdco..',
    '.oc...bo.',
    'oc.....bo',
    'od.....ao',
    'oc.....ao',
    '.ob...ao.',
    '..obbao..',
    '...ooo...',
]

# iron wall bracket clamping the sheet into its niche (left form): a riveted
# vertical plate against the container edge with a short arm into the wall
BRACKET = [
    '....oooooo',
    '....odccbo',
    '....ocbbao',
    '....ocbbao',
    'oooooobbao',
    'occcccbbao',
    'obbbbbbbao',
    'oaaaaacbao',
    'OOOOOocbao',
    '....ocbbao',
    '....ocbbao',
    '....ocbbao',
    '....obaaaO',
    '....OOOOOO',
]

# a small iron vent grate set in the masonry
VENT = [
    'ooooooooooo',
    'ocdcccccbao',
    'ocOcOcOcOao',
    'obObObObOao',
    'obObObObOao',
    'obObObObOao',
    'obbbbbbbaao',
    'ooooooooooo',
]

# wall hook for chains
HOOK = ['oo.', 'oco', '.oc', 'oco', 'oo.']

# fallen masonry chunks
RUBBLE = [
    '......oooo.....',
    '..ooo.oqpno....',
    '.oqpno.opnmo.oo',
    'oqppnno.ooo.oqno',
    'opnnnmmo...opnmo',
    'oooooooo..oooooo',
]

# carved corbel ledge end (left form)
CORBEL = ['oooo', 'oqpo', '.opo', '..oo']


def bracket(img, x, y, side):
    """Iron wall bracket clamping the sheet into its niche; ``x`` is the
    column of the plate face that touches the container edge side
    ('l': the plate ends at x, 'r': the plate starts at x). Two rivets on the
    plate, one on the arm; a stone_0 shadow under the arm."""
    w, h = P.sprite_size(BRACKET)
    if side == 'l':
        x0 = x - w + 1
        P.sprite(img, x0, y, BRACKET)
        P.rivet(img, x0 + 6, y + 2, 'iron', 2)
        P.rivet(img, x0 + 6, y + 9, 'iron', 2)
        P.rivet(img, x0 + 1, y + 5, 'iron', 2)
        P.hline(img, x0 + 1, x0 + 3, y + 9, STONE[0])
    else:
        P.sprite(img, x, y, BRACKET, flip_x=True)
        P.rivet(img, x + 2, y + 2, 'iron', 2)
        P.rivet(img, x + 2, y + 9, 'iron', 2)
        P.rivet(img, x + 7, y + 5, 'iron', 2)
        P.hline(img, x + 6, x + 8, y + 9, STONE[0])
    return h


def sconce(img, x, y, seed):
    """Iron wall sconce holding a lit bone-wax candle whose wick top is at
    (x, y). Returns the flame centre."""
    P.sprite(img, x - 3, y + 8, SCONCE)
    fx, fy = P.candle(img, x - 1, y, height=6, lit=True, holder=None, seed=seed)
    return fx, fy


def ledge(img, x, y, w, left_corbel=True, right_corbel=True):
    """A short carved stone ledge (4 rows) with corbel ends below it."""
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0, heavy='b')
    if left_corbel:
        P.sprite(img, x - 1, y + 5, CORBEL)
    if right_corbel:
        P.sprite(img, x + w - 3, y + 5, CORBEL, flip_x=True)


def barred_window(img, x, y, w, h, seed):
    """A small round-headed window in the masonry, deep dark, with three iron
    bars and a crossbar; a moss tuft on its sill."""
    inside = P.arch_niche(img, (x, y, w, h), seed=seed, interior='ink_0')
    bars = [x + 3 + k * ((w - 6) // 3) + 1 for k in range(3)]
    cross = y + h // 2
    for (px, py) in inside:
        if px in bars:
            P.put(img, px, py, IRON[1])
        if py == cross:
            P.put(img, px, py, IRON[1])
    for bx in bars:
        for (px, py) in inside:
            if px == bx - 1 and py != cross:
                P.put(img, px, py, INK[1])
    for (px, py) in inside:
        if py == cross - 1 and px not in bars:
            P.put(img, px, py, IRON[2])
        if py == cross + 1:
            P.put(img, px, py, IRON[0] if px in bars else INK[1])
    for bx in bars:
        top = min(py for (px, py) in inside if px == bx)
        P.put(img, bx, top, IRON[2])
    sill = y + h
    P.hline(img, x - 1, x + w, sill, STONE[3])
    P.hline(img, x - 1, x + w, sill + 1, STONE[1])
    P.hline(img, x - 2, x + w + 1, sill + 2, INK[1])
    P.moss_tuft(img, x + 2, sill + 2, 4, seed=seed)


def candle_niche(img, x, y, w, h, seed):
    """An arched niche with a single lit candle standing in it; returns the
    flame centre so the caller can pool its light."""
    P.arch_niche(img, (x, y, w, h), seed=seed)
    cx = x + w // 2 - 1
    base = y + h - 1
    P.hline(img, x + 2, x + w - 3, base, STONE[1])
    fx, fy = P.candle(img, cx, base - 8, height=6, lit=True, holder='iron', seed=seed)
    return fx, fy


def heal(img, before, box):
    """Give back the wall wherever a primitive cut a transparent notch
    (banner tatter) inside ``box``: frames stay opaque outside the container."""
    x, y, w, h = box
    for yy in range(max(0, y), min(img.height, y + h)):
        for xx in range(max(0, x), min(img.width, x + w)):
            if img.getpixel((xx, yy))[3] == 0 and before.getpixel((xx, yy))[3] == 255:
                img.putpixel((xx, yy), before.getpixel((xx, yy)))


def wall_cracks(img, specs, seed):
    for i, (x, y, ln, direction) in enumerate(specs):
        P.crack(img, x, y, ln, seed=seed + i, direction=direction, colour=STONE[0], light=STONE[3])


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def paint_background(key):
    s = geo.skin(key)
    n = KEYS.index(key) + 1
    img = C.base_background(key, seed=SEED + n)
    H, W = s.height, s.width
    # the free rows under the hotbar socket: H-5 .. H-3 (inside the rim)
    y = H - 5
    P.gold_filigree(img, W // 2 - 5, y, 'flourish', ramp=IRON)
    for rx in (W // 2 - 13, W // 2 + 11):
        P.rivet(img, rx, y, 'iron', size=3)
    # two short iron strap stubs riveted near the corners (the sheet's binding)
    for sx, d in ((14, 1), (W - 15, -1)):
        P.hline(img, min(sx, sx + 9 * d), max(sx, sx + 9 * d), y, IRON[2])
        P.hline(img, min(sx, sx + 9 * d), max(sx, sx + 9 * d), y + 1, IRON[1])
        P.hline(img, min(sx, sx + 9 * d), max(sx, sx + 9 * d), y + 2, INK[1])
        P.put(img, sx + 3 * d, y + 1, IRON[3])
        P.put(img, sx + 7 * d, y + 1, IRON[3])
    P.crack(img, 40 + 7 * n, y, 4, seed=SEED + n, direction='right', colour=UMBER[0], branch=False)
    P.crack(img, W - 52 + 3 * n, y + 2, 3, seed=SEED + 10 + n, direction='right', colour=UMBER[0], branch=False)
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def stack(top, end, items):
    """Spread ``items`` [(height, draw(y))] evenly between rows ``top`` and
    ``end`` (exclusive), equal air above, between and below; returns the
    tops used."""
    used = sum(h for h, _ in items)
    gap = max(2, (end - top - used) / (len(items) + 1))
    y = top + gap
    tops = []
    for h, draw in items:
        t = int(round(y))
        draw(t)
        tops.append(t)
        y += h + gap
    return tops


def paint_frame(key):
    s = geo.skin(key)
    a = s.layer()
    n = KEYS.index(key) + 1
    seed = SEED + 7 * n
    img = C.base_frame(key, a.id, seed=seed)
    H, W = a.h, a.w
    c = a.container
    lp, rp = a.left_panel, a.right_panel
    bottom = H - 9                  # last wall row above the bottom strip
    tall = H >= 184                 # chest_3 and up
    taller = H >= 202               # chest_4 and up
    tallest = H >= 220              # chest_5 and up
    # Left-panel art stays in x 4 .. 29 and right-panel art in x 227 .. 252,
    # so the brackets at the container edges never collide with it.

    # ---- wall weathering first, so the props sit on top of it --------------
    wall_cracks(img, [(lp.x + 5, c.y + 40, 6, 'down'), (lp.x + 24, bottom - 26, 7, 'up'),
                      (rp.x + 30, c.y + 30, 6, 'down'), (rp.x + 14, bottom - 30, 5, 'right')], seed)
    for i, (mx, my) in enumerate(((lp.x + 4, c.y + 60), (rp.x + 40 - 12, c.y + 70), (lp.x + 17, bottom - 20))):
        P.moss_tuft(img, mx, my + n, 3, seed=seed + 50 + i)

    # ---- iron brackets clamping the ledger into its niche (both sides) -----
    rows = [c.y + 6, c.bottom - 30]
    if tallest:
        rows.insert(1, c.y + c.h // 2 - 7)
    for by in rows:
        bracket(img, c.x - 2, by, 'l')
        bracket(img, c.right, by, 'r')

    # ---- left panel: blank banner, sconce, (barred window), candle niche,
    #      (hook and loose chain), fallen rubble ------------------------------
    ban_h = 24 + 2 * n
    bx = lp.x + 10
    P.chain(img, bx + 1, 9, bx + 1, 12, seed=seed, shadow=None)
    P.chain(img, bx + 15, 9, bx + 15, 12, seed=seed + 1, shadow=None)
    wall = img.copy()
    P.banner(img, bx, 14, 17, ban_h, MOSS, seed, emblem=None)
    heal(img, wall, (bx - 3, 12, 23, ban_h + 3))          # tatter notches show the wall, not the world
    for k in range(3):                                   # weathering stains
        P.put(img, bx + 4 + 4 * k, 22 + 5 * k, MOSS[0])
    glows = []

    def draw_sconce(t):
        glows.append((*sconce(img, lp.x + 18, t + 4, seed), 12))

    def draw_window(t):
        barred_window(img, lp.x + 9, t + 1, 15, 24, seed + 3)

    niche_h = 26 if tall else 24

    def draw_niche(t):
        fx, fy = candle_niche(img, lp.x + 8, t + 1, 19, niche_h, seed + 4)
        glows.append((fx, fy, 9))
        ly = t + 1 + niche_h + 1
        ledge(img, lp.x + 6, ly, 22)
        P.moss_tuft(img, lp.x + 9, ly + 4, 5, seed=seed + 5)
        P.moss_tuft(img, lp.x + 22, ly + 4, 3, seed=seed + 6)

    def draw_hook(t):
        P.sprite(img, lp.x + 13, t, HOOK)
        P.chain(img, lp.x + 14, t + 5, lp.x + 14, t + 5 + 8 + 2 * n, seed=seed + 7)

    left = [(18, draw_sconce)]
    if taller:
        left.append((30, draw_window))
    left.append((niche_h + 12, draw_niche))
    if tall:
        left.append((14 + 2 * n, draw_hook))
    stack(14 + ban_h, bottom - 7, left)
    P.sprite(img, lp.x + 4, bottom - 5, RUBBLE)
    P.moss_tuft(img, lp.x + 8, bottom - 6, 3, seed=seed + 8)

    # ---- right panel: lantern on a chain, tether ring, (swagged chain),
    #      (vent grate), candle ledge, gargoyle corbel ----------------------
    rcx = rp.x + 23
    P.sprite(img, rcx - 1, 8, HOOK)
    lw, lh = icons.motif_size('lantern')

    def draw_lantern(t):
        P.chain(img, rcx, 13, rcx, t - 1, seed=seed + 20)
        icons.draw_motif(img, 'lantern', rcx - lw // 2, t)
        glows.append((rcx, t + 5, 13))

    def draw_ring(t):
        P.sprite(img, rcx - 4, t, RING)

    def draw_swag(t):
        P.sprite(img, rp.x + 12, t, HOOK)
        P.sprite(img, rp.x + 34, t, HOOK, flip_x=True)
        P.chain(img, rp.x + 14, t + 3, rp.x + 34, t + 3, sag=4, seed=seed + 21)

    def draw_vent(t):
        P.sprite(img, rp.x + 17, t, VENT)
        P.moss_tuft(img, rp.x + 19, t + 8, 4, seed=seed + 25)

    def draw_ledge(t):
        ly = t + 12
        ledge(img, rp.x + 13, ly, 22)
        fx, fy = P.candle(img, rp.x + 17, ly - 8, height=7, lit=True, holder=None, seed=seed + 22)
        P.candle(img, rp.x + 24, ly - 5, height=4, lit=False, holder=None, seed=seed + 23)
        glows.append((fx, fy + 2, 10))
        P.moss_tuft(img, rp.x + 27, ly + 4, 5, seed=seed + 24)

    right = [(lh, draw_lantern), (12, draw_ring)]
    if tall:
        right.append((11, draw_swag))
    if taller:
        right.append((10, draw_vent))
    right.append((23, draw_ledge))
    stack(18 + 2 * n, bottom - 11, right)
    gw, gh = icons.motif_size('gargoyle')
    icons.draw_motif(img, 'gargoyle', rp.x + 26, bottom - gh + 1)
    P.sprite(img, rp.x + 11, bottom - 4, RUBBLE[2:])

    for (gx, gy, r) in glows:                        # light last, over everything
        P.glow(img, gx, gy, r, 'ember')

    # ---- top strip: chains from the corners to the plaque -------------------
    P.chain(img, 12, 4, W // 2 - 22, 4, sag=2, seed=seed + 40)
    P.chain(img, W // 2 + 21, 4, W - 13, 4, sag=2, seed=seed + 41)

    # ---- bottom strip: chains swagged between iron rivets, an iron fleur -----
    for x0, x1 in ((10, 120), (136, W - 11)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'iron', 3)
        P.rivet(img, x1 - 1, H - 7, 'iron', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur', ramp=IRON)

    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--out-root', type=Path, default=DEFAULT_ROOT,
                    help='directory laid out like textures/ (default: pack-source textures)')
    ap.add_argument('--skin', action='append', choices=KEYS,
                    help='paint only this skin (repeatable); default: all six')
    args = ap.parse_args(argv)
    root = args.out_root
    for key in args.skin or KEYS:
        s = geo.skin(key)
        bg = paint_background(key)
        fr = paint_frame(key)
        p1 = C.save_png(bg, root / 'menu' / f'{key}.png')
        p2 = C.save_png(fr, root / 'frames' / key / f'{s.layer().id}.png')
        print('WROTE', p1)
        print('WROTE', p2)


if __name__ == '__main__':
    main()
