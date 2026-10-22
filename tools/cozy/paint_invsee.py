#!/usr/bin/env python3
"""Cozy painter: invsee_online and invsee_offline (backgrounds + outer frames).

    python tools/cozy/paint_invsee.py                     # paint both into pack-source
    python tools/cozy/paint_invsee.py --skin invsee_offline
    python tools/cozy/paint_invsee.py --out-root DIR      # DIR laid out like textures/

Family identity: a magnifying glass over a leather satchel.

* invsee_online  - the satchel is open with the lens raised over it, a lit
  lantern pools warm light, brass fittings, a dusk window, a steaming mug.
* invsee_offline - the same satchel closed and buckled, the lens laid on its
  flap, an unlit iron lantern, a moonlit window throwing blue-grey light,
  iron fittings, a cold mug and a dimmer board.

Both backgrounds are a full 9x6 grid of native wells: the sheet is satchel
leather with a burnished edge, the well rim is stitched in waxed thread (warm
brass thread online, ash thread offline), rivets mark the main / hotbar /
armour row groups in the margins, the title band is a linen label sewn on, and
a small lens (plus a moon stamp offline) rests at the far right of the
inventory band. Every pixel is placed here or by the shared primitives;
deterministic (fixed seeds, no clock).

Licence: code MIT; artwork CC0-1.0.
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
import lettering as L  # noqa: E402
import primitives as P  # noqa: E402
from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD, ramp_of  # noqa: E402

SKINS = ('invsee_online', 'invsee_offline')
SEED = 23

IRON = [INK[2], ASH[0], ASH[1], ASH[2]]          # 4-step metal ramp for offline fittings
DIM_PARCH = [PARCHMENT[0], PARCHMENT[0], PARCHMENT[1], PARCHMENT[2]]

MOODS = {
    'invsee_online': dict(
        lit=True,
        leather=WOOD,                    # warm satchel leather
        sheet=3,                         # background leather body: tan (wood_3)
        thread=PARCHMENT[3],             # cream waxed thread on the well rim
        metal=BRASS,
        glass=dict(s=SKY[2], t=SKY[1], c=PARCHMENT[3]),
        accent=SKY,
        paper=PARCHMENT,
    ),
    'invsee_offline': dict(
        lit=False,
        leather=[INK[1], WOOD[0], WOOD[1], WOOD[2], WOOD[3]],   # same satchel, one step into shadow
        sheet=3,                         # the same hide in shadow (wood_2)
        thread=ASH[2],
        metal=IRON,
        glass=dict(s=SKY[1], t=SKY[0], c=ASH[2]),
        accent=ASH,
        paper=DIM_PARCH,
    ),
}


# ---------------------------------------------------------------------------
# Small helpers (local; the shared modules stay untouched)
# ---------------------------------------------------------------------------

def remap(img, mapping, box=None, keep=None):
    """Replace exact palette colours by ``mapping`` inside ``box`` (alpha kept).
    ``keep(x, y)`` returning True protects a pixel."""
    x0, y0, w, h = box or (0, 0, img.width, img.height)
    px = img.load()
    m = {tuple(k[:3]): tuple(v[:3]) for k, v in mapping.items()}
    for y in range(max(0, y0), min(img.height, y0 + h)):
        for x in range(max(0, x0), min(img.width, x0 + w)):
            p = px[x, y]
            if p[3] and p[:3] in m and not (keep and keep(x, y)):
                px[x, y] = m[p[:3]] + (p[3],)


def metal_key(metal):
    return {'o': INK[1], 'O': INK[0], '3': metal[3], '2': metal[2], '1': metal[1], '0': metal[0]}


def rivet(img, x, y, metal):
    """3x3 domed rivet, lit top-left (x, y = top-left)."""
    P.sprite(img, x, y, ['.3.', '320', '.0.'], {'3': metal[3], '2': metal[2], '0': metal[0]})


# Brass (or iron) buckle with the strap running through it and a centre prong.
BUCKLE = [
    '.ooooooo.',
    'o3333322o',
    'o3sspss1o',
    'o2sspss1o',
    'o2sspss0o',
    'o1111100o',
    '.ooooooo.',
]

# Large magnifying glass: 14x14 ring (brass rim, inner ink lip, glass with a
# glint top-left and a darker crescent bottom-right). Handle drawn separately.
BIG_LENS = [
    '.....oooo.....',
    '...oo3332oo...',
    '..o33oooo22o..',
    '.o3ooccssoo2o.',
    '.o3ocssssso2o.',
    'o3ocssssssto2o',
    'o3osssssssto1o',
    'o2osssssstto1o',
    'o2ossssstttO1o',
    '.o2osstttto1o.',
    '.o2ootttto01o.',
    '..o11oooo00o..',
    '...oo1000oo...',
    '.....oooo.....',
]


def big_lens(img, x, y, mood, handle=(1, 1), length=8):
    """Draw the 14x14 lens at (x, y) with a 4-px wooden handle leaving the
    ring at the lower right (``handle`` = direction (dx, dy), 45 degrees)."""
    g = mood['glass']
    key = metal_key(mood['metal'])
    key.update({'s': g['s'], 't': g['t'], 'c': g['c']})
    rows = [r.replace('O', 'o') for r in BIG_LENS]
    dx, dy = handle
    # handle: brass collar (2 steps), then wood; staircase band 3 px wide with ink sides
    sx, sy = (x + 11, y + 11) if dx > 0 else (x + 2, y + 11)
    for i in range(length + 2):
        cx, cy = sx + i * dx, sy + i * dy
        collar = i < 2
        core = [mood['metal'][3], mood['metal'][2], mood['metal'][1]] if collar else [WOOD[3], WOOD[2], WOOD[1]]
        if dx < 0:
            core = core[::-1]
        P.put(img, cx - 2, cy, INK[1])
        for k, c in enumerate(core):
            P.put(img, cx - 1 + k, cy, c)
        P.put(img, cx + 2, cy, INK[0])
    end = (sx + (length + 2) * dx, sy + (length + 2) * dy)
    P.hline(img, end[0] - 1, end[0] + 1, end[1], INK[0])
    P.put(img, end[0] - 1 if dx > 0 else end[0] + 1, end[1] - 1, WOOD[1])
    P.sprite(img, x, y, rows, key)
    return (x, y, 14, 14)


def shape(img, box, fill, cut_top=1, cut_bottom=1, outline=INK[1], heavy=INK[0]):
    """Filled shape with independent pixel-art corner cuts on top and bottom;
    ink outline, heavier on the bottom/right. Returns the inside set (local)."""
    x, y, w, h = box
    top, bot = P._CORNERS[cut_top], P._CORNERS[cut_bottom]
    inside = set()
    for j in range(h):
        for i in range(w):
            if j < h // 2 and ((i, j) in top or (w - 1 - i, j) in top):
                continue
            if j >= h // 2 and ((i, h - 1 - j) in bot or (w - 1 - i, h - 1 - j) in bot):
                continue
            inside.add((i, j))
    for (i, j) in inside:
        P.put(img, x + i, y + j, fill)
    for (i, j) in P._edge_pixels(inside):
        sd = P._side(inside, i, j)
        P.put(img, x + i, y + j, heavy if ('b' in sd or 'r' in sd) else outline)
    return inside


def strap_line(img, pts, lea):
    """A 2-px leather strap along ``pts`` with ink edges (heavier on the
    shadow side) and a worn sheen on the lit edge every few pixels."""
    for i, (px_, py_) in enumerate(pts):
        nb = pts[min(i + 1, len(pts) - 1)]
        pb = pts[max(i - 1, 0)]
        if abs(nb[1] - pb[1]) > abs(nb[0] - pb[0]):        # steep: thickness runs in x
            P.put(img, px_ - 1, py_, INK[1]); P.put(img, px_ + 2, py_, INK[0])
        else:
            P.put(img, px_, py_ - 1, INK[1]); P.put(img, px_, py_ + 2, INK[0])
    for i, (px_, py_) in enumerate(pts):
        nb = pts[min(i + 1, len(pts) - 1)]
        pb = pts[max(i - 1, 0)]
        steep = abs(nb[1] - pb[1]) > abs(nb[0] - pb[0])
        a, b = ((px_, py_), (px_ + 1, py_)) if steep else ((px_, py_), (px_, py_ + 1))
        P.put(img, *a, lea[4] if i % 7 in (2, 3) else lea[3])
        P.put(img, *b, lea[2])


KEY = [
    '.ooooo.',
    'o33221o',
    'o3o.o1o',
    'o2o.o0o',
    'o21100o',
    '.oo1oo.',
    '..o2o..',
    '..o1o..',
    '..o2o..',
    '..o1ooo',
    '..o233o',
    '..o1ooo',
    '..o23o.',
    '..oooo.',
]


def satchel(img, x, y, mood, open_=False, seed=0, contents=None, strap_from=None):
    """Leather satchel, 32 wide; the front body spans y+12 .. y+30.
    Open: the flap is thrown back behind the bag (y .. y+13), a dark mouth,
    ``contents(img)`` is drawn between the back and the front so things can
    stick out of it. Closed: the flap is down over the front with two buckled
    straps. ``strap_from`` (peg point) hangs it by a carry strap."""
    lea = mood['leather']
    thread = mood['thread']
    metal = mood['metal']
    w = 32
    if strap_from:
        for ax in (x + 2, x + w - 4):
            strap_line(img, P._sag_points(strap_from[0], strap_from[1], ax, y + 12, -1), lea)
    if open_:
        shape(img, (x + 2, y, w - 4, 14), lea[3], cut_top=3, cut_bottom=0)
        P.hline(img, x + 4, x + w - 5, y + 1, lea[4])
        P.vline(img, x + 3, y + 3, y + 9, lea[4])
        P.vline(img, x + w - 4, y + 3, y + 9, lea[2])
        P.stitch_line(img, x + 5, y + 2, x + w - 6, y + 2, thread, 2, 2)
        P.stitch_line(img, x + 4, y + 4, x + 4, y + 11, thread, 2, 2)
        P.stitch_line(img, x + w - 5, y + 4, x + w - 5, y + 11, thread, 2, 2, phase=1)
        P.fill(img, (x + 3, y + 10, w - 6, 3), INK[1])                 # dark mouth
        P.hline(img, x + 6, x + w - 7, y + 11, INK[0])
    if contents:
        contents(img)
    # front body: square-ish top, rounded bottom
    body = (x, y + 12, w, 19)
    shape(img, body, lea[3], cut_top=1, cut_bottom=3)
    P.hline(img, x + 1, x + w - 2, y + 13, lea[4])                     # rolled top edge
    P.hline(img, x + 2, x + w - 3, y + 14, lea[2])
    P.vline(img, x + 1, y + 15, y + 27, lea[4])
    P.vline(img, x + w - 2, y + 14, y + 28, lea[2])
    P.hline(img, x + 3, x + w - 4, y + 29, lea[2])
    for gx in (x + 3, x + w - 4):                                      # side gussets
        P.vline(img, gx, y + 16, y + 27, lea[2])
    P.stitch_line(img, x + 5, y + 16, x + w - 6, y + 16, thread, 2, 2)
    P.stitch_line(img, x + 5, y + 27, x + w - 6, y + 27, thread, 2, 2, phase=1)
    for (sx, sy, c) in ((x + 9, y + 23, lea[2]), (x + 10, y + 23, lea[2]), (x + 9, y + 22, lea[4]),
                        (x + 24, y + 25, lea[2]), (x + 18, y + 19, lea[2])):
        P.put(img, sx, sy, c)                                          # wear marks
    for ax in (x + 2, x + w - 4):                                      # strap rings
        P.sprite(img, ax - 1, y + 11, ['.o.', 'o.o', '.o.'], {'o': metal[2]})
    if open_:
        # a stitched front pocket with a stud
        shape(img, (x + 8, y + 18, 16, 9), lea[3], cut_top=0, cut_bottom=2)
        P.hline(img, x + 9, x + 22, y + 19, lea[4])
        P.hline(img, x + 9, x + 22, y + 25, lea[2])
        P.stitch_line(img, x + 10, y + 21, x + 21, y + 21, thread, 2, 2, phase=1)
        P.sprite(img, x + 15, y + 17, ['o3o', 'o0o'], dict(metal_key(metal)))
        return body
    # closed: the flap comes over the top and down the front
    flap = (x + 1, y + 7, w - 2, 17)
    shape(img, flap, lea[3], cut_top=2, cut_bottom=3)
    P.hline(img, x + 3, x + w - 4, y + 8, lea[4])
    P.vline(img, x + 2, y + 9, y + 20, lea[4])
    P.hline(img, x + 4, x + w - 5, y + 22, lea[2])
    P.stitch_line(img, x + 4, y + 10, x + 4, y + 20, thread, 2, 2)
    P.stitch_line(img, x + w - 5, y + 10, x + w - 5, y + 20, thread, 2, 2, phase=1)
    P.stitch_line(img, x + 6, y + 20, x + w - 7, y + 20, thread, 2, 2, phase=1)
    P.hline(img, x + 3, x + w - 4, y + 24, lea[1])                     # flap shadow on the body
    for tx in (x + 6, x + w - 12):
        shape(img, (tx + 1, y + 18, 4, 10), lea[2], cut_top=0, cut_bottom=2)
        P.sprite(img, tx - 1, y + 20, BUCKLE, dict(metal_key(metal), s=lea[2], p=metal[3]))
    return body


def luggage_tag(img, cx, y, text, seed, metal, ramp=PARCHMENT):
    """Linen luggage tag with SPRIG lettering (the artLayers leftHeading),
    clipped left corners and a metal eyelet."""
    tw = L.text_width(text, 'sprig')
    w = tw + 10
    x = cx - w // 2
    P.linen_tag(img, (x, y, w, 11), eyelet=None, seed=seed, notch=2, ramp=ramp)
    P.sprite(img, x + 2, y + 4, ['.o.', 'o0o', '.o.'], {'o': metal[2], '0': INK[0]})
    L.draw_text(img, x + 6, y + 3, text, 'ink_0', face='sprig')
    return (x, y, w, 11)


def book(img, x, y, w, h, ramp, band=None):
    """A standing book spine: ink outline, cloth ramp, two bands."""
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=0, heavy='r', fill_colour=ramp[1])
    P.vline(img, x + 1, y + 1, y + h - 2, ramp[2])
    for by in (y + 2, y + h - 4):
        P.hline(img, x + 1, x + w - 2, by, band or BRASS[2])


def shelf(img, x, y, w, seed, metal):
    P.plank(img, (x, y, w, 5), C.FRAME_WOOD[1:] + [WOOD[4]], seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': metal[1]})


def notebook_open(img, x, y, seed, mood):
    """An open field notebook: two parchment pages, ruled in the accent, a
    ribbon bookmark and a pencil across it (no writing)."""
    w, h = 30, 22
    P.ink_outline(img, (x - 1, y + 1, w + 2, h), 'ink_1', radius=1, heavy='b', fill_colour=WOOD[1])  # cover
    ramp = mood['paper']
    for i, px_ in enumerate((x + 1, x + w // 2)):
        P.parchment_panel(img, (px_, y, w // 2 - 1, h - 1), seed + i, outline='ink_2', fibres=False, ramp=ramp)
        for ry in range(y + 4, y + h - 4, 3):
            P.stitch_line(img, px_ + 2, ry, px_ + w // 2 - 4, ry, mood['accent'][2] if mood['lit'] else SKY[1], 3, 1, phase=ry + i)
    P.vline(img, x + w // 2 - 1, y + 1, y + h - 2, INK[2])        # gutter
    # ribbon bookmark hanging out of the bottom
    P.vline(img, x + w // 2 + 3, y + h - 2, y + h + 3, BERRY[1])
    P.put(img, x + w // 2 + 3, y + h + 4, BERRY[0])
    P.put(img, x + w // 2 + 4, y + h + 4, BERRY[1])
    # pencil lying diagonally
    for k in range(12):
        px_, py_ = x + 5 + k, y + 16 - k // 2
        P.put(img, px_, py_, BRASS[2] if k > 2 else (WOOD[3] if k > 0 else INK[0]))
        P.put(img, px_, py_ + 1, BRASS[0] if k > 2 else WOOD[2])
    P.put(img, x + 17, y + 10, BERRY[2]); P.put(img, x + 17, y + 11, BERRY[1])


def ink_pot(img, x, y, quill=True):
    rows = [
        '..ooo..',
        '..o1o..',
        '.ooooo.',
        'o02220o',
        'o0aa10o',
        'o0a110o',
        'o00000o',
        '.ooooo.',
    ]
    if quill:
        for k in range(9):
            P.put(img, x + 4 + k // 2, y - 1 - k, PARCHMENT[3] if k > 3 else PARCHMENT[1])
            if k > 3:
                P.put(img, x + 5 + k // 2, y - 1 - k, PARCHMENT[2])
                P.put(img, x + 3 + k // 2, y - 1 - k, PARCHMENT[1] if k % 2 else PARCHMENT[2])
    P.sprite(img, x, y, rows, {'o': INK[1], '0': INK[0], '1': BRASS[2], '2': SKY[0], 'a': SKY[1]})


def coffee_mug(img, x, y, lit, seed):
    P.mug(img, x, y, SKY if lit else ASH, steam=lit, seed=seed)


def window(img, x, y, lit):
    """26 x 24 four-pane window. Online: warm dusk sky. Offline: night with a
    crescent moon and two stars."""
    w, h = 26, 24
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=1, heavy='br', fill_colour=WOOD[3])
    P.highlight_edge(img, (x, y, w, h), WOOD[4], 'tl', inset=1)
    P.shadow_edge(img, (x, y, w, h), WOOD[1], 'br', inset=1)
    panes = [(x + 3, y + 3, 9, 8), (x + 14, y + 3, 9, 8), (x + 3, y + 13, 9, 8), (x + 14, y + 13, 9, 8)]
    for (px_, py_, pw, ph) in panes:
        P.ink_outline(img, (px_ - 1, py_ - 1, pw + 2, ph + 2), 'ink_1', radius=0)
        if lit:
            top = py_ < y + 10
            P.fill(img, (px_, py_, pw, ph), SKY[1] if top else EMBER[2])
            if top:
                P.hline(img, px_, px_ + pw - 1, py_ + ph - 1, SKY[2])
                P.hline(img, px_, px_ + pw - 1, py_ + ph - 2, SKY[2]) if px_ > x + 10 else None
            else:
                P.hline(img, px_, px_ + pw - 1, py_, SKY[2])
                P.hline(img, px_, px_ + pw - 1, py_ + ph - 1, EMBER[1])
                P.hline(img, px_, px_ + pw - 1, py_ + ph - 2, EMBER[1])
        else:
            P.fill(img, (px_, py_, pw, ph), SKY[0])
    if lit:
        # the sun sinking behind distant hills (bottom panes)
        P.sprite(img, x + 7, y + 14, ['..ooo..', '.o333o.', 'o33333o'],
                 {'o': EMBER[1], '3': PARCHMENT[3]})
        P.sprite(img, x + 3, y + 17, ['...ss.....', '.sssss..ss', 'ssssssssss'],
                 {'s': SAGE[1]})
        P.sprite(img, x + 14, y + 17, ['..........', 'ss....ss..', 'ssss.sssss'], {'s': SAGE[1]})
        P.hline(img, x + 3, x + 11, y + 20, SAGE[0]); P.hline(img, x + 14, x + 22, y + 20, SAGE[0])
        P.put(img, x + 18, y + 6, PARCHMENT[3]); P.put(img, x + 6, y + 5, SKY[2])
    else:
        # crescent moon in the top-right pane, stars elsewhere
        P.sprite(img, x + 16, y + 4, ['..33.', '.32..', '32...', '32...', '.33..', '..33.'],
                 {'3': PARCHMENT[3], '2': ASH[2]})
        for sx, sy in ((x + 5, y + 5), (x + 9, y + 8), (x + 21, y + 17), (x + 6, y + 18), (x + 16, y + 15)):
            P.put(img, sx, sy, PARCHMENT[2] if (sx + sy) % 2 else SKY[2])
        P.hline(img, x + 3, x + 11, y + 20, SKY[1]); P.hline(img, x + 14, x + 22, y + 20, SKY[1])
    # mullions and sill
    P.vline(img, x + 12, y + 2, y + h - 3, WOOD[2]); P.vline(img, x + 13, y + 2, y + h - 3, WOOD[1])
    P.hline(img, x + 2, x + w - 3, y + 11, WOOD[2]); P.hline(img, x + 2, x + w - 3, y + 12, WOOD[1])
    P.plank(img, (x - 2, y + h - 1, w + 4, 4), WOOD, 5, 'ink_1', radius=1, grain=0)


def moonlight(img, x0, y0, x1, y1, spread):
    """A cool shaft of moonlight from a window: board browns inside the slanted
    band turn to their ash counterparts on an ordered checker (50 % in the
    core, 25 % at the soft edges and the far end). Never a gradient."""
    cool = {WOOD[1]: ASH[0], WOOD[2]: ASH[1], WOOD[3]: ASH[2]}
    px = img.load()
    n = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / n
        cx = round(x0 + (x1 - x0) * t)
        half = spread + round(3 * t)
        for x in range(cx - half, cx + half + 1):
            if not (0 <= x < img.width and 0 <= y < img.height):
                continue
            p = px[x, y]
            if not p[3] or p[:3] not in cool:
                continue
            soft = abs(x - cx) > half - 2 or t > 0.75
            if P.BAYER4[y % 4][x % 4] < (4 if soft else 8):
                px[x, y] = cool[p[:3]] + (255,)


def sleeping_cat(img, x, y):
    """A grey cat curled asleep on a small linen cushion (offline only)."""
    shape(img, (x - 2, y + 8, 21, 5), PARCHMENT[1], cut_top=2, cut_bottom=2)
    P.hline(img, x, x + 16, y + 9, PARCHMENT[2])
    P.stitch_line(img, x, y + 10, x + 16, y + 10, SKY[1], 2, 2)
    shape(img, (x + 4, y + 2, 13, 8), ASH[1], cut_top=3, cut_bottom=2)     # body
    P.hline(img, x + 7, x + 13, y + 3, ASH[2])
    P.hline(img, x + 6, x + 14, y + 4, ASH[2])
    P.hline(img, x + 6, x + 15, y + 8, ASH[0])
    shape(img, (x, y + 3, 8, 6), ASH[1], cut_top=2, cut_bottom=2)          # head
    P.sprite(img, x + 1, y + 1, ['o..o.', 'oo.oo'], {'o': INK[1]})         # ears
    P.put(img, x + 2, y + 3, ASH[1]); P.put(img, x + 5, y + 3, ASH[1])
    P.hline(img, x + 2, x + 5, y + 4, ASH[2])
    for (ex, ey) in ((x + 1, y + 5), (x + 2, y + 6), (x + 5, y + 6), (x + 6, y + 5)):
        P.put(img, ex, ey, INK[0])                                          # closed eyes
    P.put(img, x + 3, y + 7, BERRY[2]); P.put(img, x + 4, y + 7, BERRY[2])  # nose
    # tail wrapped round the front
    P.hline(img, x + 6, x + 16, y + 9, INK[1])
    P.hline(img, x + 7, x + 15, y + 8, ASH[2])
    P.put(img, x + 6, y + 8, ASH[2]); P.put(img, x + 16, y + 8, INK[1])


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def paint_background(key):
    mood = MOODS[key]
    s = geo.skin(key)
    W, H = s.width, s.height
    img = C.base_background(key, seed=SEED)                 # shared base: bands, wells, rim
    tband, iband = C.bands(key)
    tcrop = img.crop(tband.crop_box())
    icrop = img.crop(iband.crop_box())
    lea = mood['leather']

    # 1. the sheet becomes satchel leather (flat, burnished edge, few pores)
    si = mood['sheet']
    P.fill(img, (1, 1, W - 2, H - 2), lea[si])
    img.paste(tcrop, (tband.x, tband.y))
    img.paste(icrop, (iband.x, iband.y))
    # base tacks give way to rivets in the mood metal
    for (tx, ty) in ((tband.x + 1, tband.y + 5), (tband.right - 4, tband.y + 5)):
        P.fill(img, (tx, ty, 3, 3), PARCHMENT[2])
    if not mood['lit']:
        remap(img, {PARCHMENT[3]: PARCHMENT[2], PARCHMENT[2]: PARCHMENT[1], PARCHMENT[1]: PARCHMENT[0]},
              tband.tuple())
        remap(img, {PARCHMENT[3]: PARCHMENT[2], PARCHMENT[2]: PARCHMENT[1], PARCHMENT[1]: PARCHMENT[0]},
              iband.tuple())
    P.ink_outline(img, (0, 0, W, H), 'ink_1', radius=2, heavy='br')
    P.highlight_edge(img, (0, 0, W, H), lea[si + 1], 'tl', broken=7, seed=SEED, inset=1)
    P.shadow_edge(img, (0, 0, W, H), lea[si - 1], 'br', inset=1)

    # 2. the well rim: recessed, stitched in waxed thread
    holes = P.merge_holes(s.content_slots) + P.merge_holes(s.player_slots)
    P.stitched_well(img, holes, thread=mood['thread'], protect=[tband.tuple(), iband.tuple()])

    paper = PARCHMENT if mood['lit'] else DIM_PARCH
    # 3. the title label is sewn on: running stitch along its top and both ends
    P.stitch_line(img, tband.x + 6, tband.y + 1, tband.right - 7, tband.y + 1, paper[0], 2, 2)
    for ex in (tband.x + 2, tband.right - 3):
        P.stitch_line(img, ex, tband.y + 3, ex, tband.bottom - 3, paper[0], 2, 2)
    # inventory band: stitched ends only (glyph rows stay clean)
    for ex in (iband.x + 1, iband.right - 2):
        P.stitch_line(img, ex, iband.y + 1, ex, iband.bottom - 2, paper[0], 2, 2)

    # 4. rivets in the margins mark the row groups (main | hotbar | lower rows)
    metal = mood['metal']
    rows = sorted({sl.y for sl in s.content_slots})
    marks = []
    if len(rows) >= 5:
        marks = [rows[3] - 2, rows[4] - 2]               # between rows 2|3 and 3|4
    marks.append(s.player_slots[-1].y - 4)                # main inventory | hotbar seam
    for my in marks:
        rivet(img, 1, my - 1, metal)
        rivet(img, W - 4, my - 1, metal)
    # corner rivets on the leather
    rivet(img, 1, H - 5, metal)
    rivet(img, W - 4, H - 5, metal)
    # a few pores / creases in the visible leather (hand-placed)
    for (cx, cy) in ((30, 219), (31, 219), (64, 218), (101, 219), (102, 219), (139, 218), (2, 160), (173, 52)):
        P.put(img, cx, cy, lea[si - 1])
    for (cx, cy) in ((30, 218), (101, 218)):
        P.put(img, cx, cy, lea[si + 1])

    # 5. far right of the inventory band: a small lens (and a moon stamp offline)
    lx, ly = iband.right - 16, iband.y
    small_lens = [
        '.oooo....',
        'o3ccso...',
        'oc sso...',
        'osstso...',
        '.oooo2...',
        '.....o2..',
        '......oo.',
    ]
    g = mood['glass']
    lkey = {'o': INK[2], '3': metal[3] if mood['lit'] else ASH[2], 'c': PARCHMENT[3] if mood['lit'] else PARCHMENT[2],
            's': SKY[2], 't': SKY[1] if mood['lit'] else SKY[2], '2': WOOD[3]}
    P.sprite(img, lx, ly + 1, [r.replace(' ', 's') for r in small_lens], lkey)
    if not mood['lit']:
        # two small night stars stamped beside it
        P.sprite(img, lx - 9, ly + 2, ['.s.', 'sts', '.s.'], {'s': SKY[2], 't': SKY[1]})
        P.put(img, lx - 4, ly + 6, SKY[2])
    else:
        P.leaf(img, lx - 7, ly + 2, 'ne', small=True)
        P.put(img, lx - 8, ly + 6, SAGE[0])

    geo.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def paint_frame(key):
    mood = MOODS[key]
    s = geo.skin(key)
    a = s.layer()
    lit = mood['lit']
    metal = mood['metal']
    lea = mood['leather']
    img = C.base_frame(key, a.id, seed=SEED)
    H = a.h
    lp, rp = a.left_panel, a.right_panel
    lx, rx = lp.x, rp.x + 2           # right panel art starts after the cast shadow
    ribbon = (96, 0, 64, 8)

    def keep_ribbon(x, y):
        return ribbon[0] <= x < ribbon[0] + ribbon[2] and y < ribbon[3]

    if not lit:
        # quieter board: the sheen and highlights drop a step
        remap(img, {WOOD[3]: WOOD[2], WOOD[2]: WOOD[1]}, keep=keep_ribbon)

    # ---------------- left panel -----------------------------------------
    P.rope(img, lx + 4, 12, lx + 35, 12, sag=2)
    P.vline(img, lx + 19, 14, 16, INK[1])
    if lit:
        P.lantern(img, lx + 16, 17)
        P.lantern_glow_ring(img, lx + 19, 22, 15, strength=1)
    else:
        P.lantern(img, lx + 16, 17, ramp=IRON, glow=(None, SKY[0], ASH[0]))
        P.put(img, lx + 18, 21, SKY[1])                     # cold glint on dark glass
    P.twine(img, lx + 19, 26, lx + 19, 33, sag=0)
    luggage_tag(img, lx + 20, 33, a.left_heading or a.heading, SEED, metal, ramp=PARCHMENT if lit else DIM_PARCH)

    # the satchel hangs from a peg by its strap; the lens is over it
    peg = (lx + 19, 54)
    sx, sy = lx + 4, 70

    def contents(im):
        # a rolled paper tied with the accent ribbon, and the raised lens
        qx = sx + 21
        P.ink_outline(im, (qx, sy + 2, 7, 11), 'ink_2', radius=1, fill_colour=PARCHMENT[2])
        P.vline(im, qx + 1, sy + 4, sy + 11, PARCHMENT[3])
        P.vline(im, qx + 5, sy + 4, sy + 11, PARCHMENT[1])
        P.sprite(im, qx + 1, sy + 3, ['ooo', 'o1o'], {'o': PARCHMENT[0], '1': PARCHMENT[1]})
        P.hline(im, qx + 1, qx + 5, sy + 8, SKY[1])
        P.put(im, qx, sy + 9, SKY[1]); P.put(im, qx - 1, sy + 10, SKY[0])
        big_lens(im, sx + 15, sy - 14, mood, handle=(-1, 1), length=10)

    satchel(img, sx, sy, mood, open_=lit, seed=SEED, contents=contents if lit else None, strap_from=peg)
    P.sprite(img, peg[0] - 2, peg[1] - 2, ['.oo.', 'o32o', 'o21o', '.oo.'], metal_key(metal))
    if not lit:
        # the lens laid across the closed flap
        big_lens(img, sx + 9, sy + 4, mood, handle=(1, 1), length=3)

    # shelf: field notebook (closed, elastic band), ink pot and quill
    shelf_y = 122
    shelf(img, lx + 3, shelf_y, 34, SEED + 3, metal)
    nb = (lx + 6, shelf_y - 12, 13, 12)
    P.ink_outline(img, nb, 'ink_1', radius=1, heavy='br', fill_colour=SKY[1] if lit else SKY[0])
    P.vline(img, nb[0] + 1, nb[1] + 1, nb[1] + nb[3] - 2, SKY[2] if lit else SKY[1])
    P.hline(img, nb[0] + 2, nb[0] + nb[2] - 2, nb[1] + nb[3] - 2, PARCHMENT[1])
    P.vline(img, nb[0] + 9, nb[1], nb[1] + nb[3] - 1, INK[0])
    P.vline(img, nb[0] + 10, nb[1] + 1, nb[1] + nb[3] - 2, BERRY[1] if lit else ASH[1])
    ink_pot(img, lx + 24, shelf_y - 8, quill=True)

    # open field notebook pinned below
    notebook_open(img, lx + 4, 138, SEED, mood)
    P.tack(img, lx + 19, 138)

    # a ring of keys on a nail
    P.tack(img, lx + 12, 172)
    P.vline(img, lx + 12, 174, 176, PARCHMENT[0])
    P.sprite(img, lx + 6, 176, ['..ooooooooo..', '.o333222221o.', 'o3o.......o0o', '.o100000000o.', '..ooooooooo..'],
             metal_key(metal))
    P.sprite(img, lx + 4, 180, KEY, metal_key(metal))
    P.sprite(img, lx + 13, 181, KEY[:-4] + ['..o2o..', '..o1oo.', '..o23o.', '..oooo.'], metal_key(metal))

    # ivy climbing the right edge of the left panel
    P.ink_line(img, lx + 31, 166, lx + 29, 214, SAGE[0], wobble=1, seed=SEED)
    for k, yy in enumerate((168, 177, 187, 196, 206)):
        P.leaf(img, lx + (32 if k % 2 else 24), yy, 'ne' if k % 2 else 'nw', small=k in (0, 3))
    icons.draw_motif(img, 'herb_pot', lx + 18, H - 26)
    icons.draw_motif(img, 'crate', lx + 5, H - 24)
    if not lit:
        remap(img, {SAGE[2]: SAGE[1], SAGE[1]: SAGE[0]}, (lx, 160, 40, H - 168))

    # ---------------- right panel ----------------------------------------
    window(img, rx + 5, 12, lit)
    if lit:
        P.lantern_glow_ring(img, rx + 18, 24, 15, strength=1)
    else:
        moonlight(img, rx + 18, 40, rx + 10, 120, 7)

    # the spare shoulder strap hanging in a loop from two pegs, buckle dangling
    p1, p2 = (rx + 6, 52), (rx + 29, 52)
    strap_line(img, P._sag_points(p1[0], p1[1], p2[0], p2[1], 10), lea)
    strap_line(img, [(p2[0], p2[1] + k) for k in range(0, 16)], lea)
    P.sprite(img, p2[0] - 3, p2[1] + 15, BUCKLE, dict(metal_key(metal), s=lea[2], p=metal[3]))
    for pp in (p1, p2):
        P.sprite(img, pp[0] - 1, pp[1] - 2, ['.oo.', 'o32o', 'o21o', '.oo.'], metal_key(metal))
    for hy in (p2[1] + 5, p2[1] + 9):
        P.put(img, p2[0] + 1, hy, INK[0])

    # pinned case note: ruled lines, a small inked lens mark, curled corner
    nx, ny, nw, nh = rx + 5, 86, 26, 32
    P.parchment_panel(img, (nx, ny, nw, nh), SEED + 5, outline='ink_1', fibres=True, ramp=mood['paper'])
    for k in range(13, nh - 5, 4):
        P.stitch_line(img, nx + 3, ny + k, nx + nw - 5, ny + k, SKY[2] if lit else SKY[1], 3, 1, phase=k)
    P.sprite(img, nx + 4, ny + 3, ['.ooo..', 'o...o.', 'o...o.', '.ooo..', '....o.', '.....o'],
             {'o': SKY[1] if lit else SKY[0]})
    P.page_curl(img, (nx, ny, nw, nh), 'br', 5, behind=C.FRAME_WOOD[2] if lit else WOOD[1])
    P.tack(img, nx + nw // 2, ny + 1)

    # shelf of books with a mug
    by = 152
    shelf(img, rx + 3, by, 34, SEED + 7, metal)
    book(img, rx + 5, by - 14, 5, 14, SKY if lit else [SKY[0], SKY[0], SKY[1]])
    book(img, rx + 10, by - 12, 5, 12, BERRY if lit else [INK[2], BERRY[0], BERRY[1]])
    book(img, rx + 15, by - 15, 4, 15, SAGE if lit else [SAGE[0], SAGE[0], SAGE[1]])
    lean = PLUM_OR(lit)
    for k in range(13):
        P.put(img, rx + 19 + k // 4, by - 1 - k, INK[1])
        P.put(img, rx + 20 + k // 4, by - 1 - k, lean[2])
        P.put(img, rx + 21 + k // 4, by - 1 - k, lean[1])
        P.put(img, rx + 22 + k // 4, by - 1 - k, INK[0])
    P.hline(img, rx + 22, rx + 25, by - 14, INK[1])
    coffee_mug(img, rx + 26, by - 9, lit, SEED)

    # a pocket magnifier hanging from a nail on twine
    P.tack(img, rx + 17, 168)
    P.twine(img, rx + 17, 169, rx + 17, 176)
    icon_key = dict(icons.K_LENS)
    if not lit:
        icon_key.update({'2': ASH[2], '1': SKY[0], 's': SKY[1], 'c': ASH[2], 'g': ASH[2]})
    P.sprite(img, rx + 13, 176, icons.LENS, icon_key)

    # bottom shelf: candle and folded map (online) / sleeping cat (offline)
    bs = H - 22
    shelf(img, rx + 3, bs, 34, SEED + 9, metal)
    if lit:
        icons.draw_motif(img, 'candle', rx + 6, bs - 11)
        P.lantern_glow_ring(img, rx + 8, bs - 9, 9, strength=1)
        mx, my = rx + 16, bs - 11
        P.parchment_panel(img, (mx, my, 17, 11), SEED + 9, outline='ink_1', fibres=False)
        for vx in (mx + 5, mx + 11):
            P.vline(img, vx, my + 1, my + 9, PARCHMENT[0])
        P.ink_line(img, mx + 2, my + 8, mx + 7, my + 4, SKY[1])
        P.ink_line(img, mx + 8, my + 4, mx + 14, my + 7, SKY[1])
        P.put(img, mx + 13, my + 3, BERRY[1]); P.put(img, mx + 12, my + 2, BERRY[1])
        P.hline(img, mx, mx + 16, my + 6, PARCHMENT[0])
    else:
        sleeping_cat(img, rx + 10, bs - 13)
        rows = icons.CANDLE[3:]
        P.sprite(img, rx + 3, bs - 8, rows, icons.K_CANDLE)
        P.sprite(img, rx + 4, bs - 15, ['.s', 's.', '.s', 's.'], {'s': ASH[1]})

    P.shadow_edge(img, (rp.x + 2, 9, rp.w - 3, H - 18), INK[1], 'r')

    # ---------------- bottom strip: a stitched satchel strap with buckles --
    yb = H - 4
    P.fill(img, (12, yb - 2, a.w - 24, 5), INK[1])
    P.hline(img, 12, a.w - 13, yb + 2, INK[0])
    P.fill(img, (12, yb - 1, a.w - 24, 3), lea[2])
    P.hline(img, 13, a.w - 14, yb - 1, lea[3])
    P.stitch_line(img, 14, yb, a.w - 15, yb, mood['thread'], 2, 2)
    for bx in (58, a.w - 68):
        P.sprite(img, bx, yb - 3, BUCKLE, dict(metal_key(metal), s=lea[2], p=metal[3]))
    P.tack(img, 10, yb - 1)
    P.tack(img, a.w - 11, yb - 1)

    # top strip: rivets either side of the heading ribbon
    for tx in (44, 76, a.w - 79, a.w - 47):
        rivet(img, tx, 3, metal)

    if not lit:
        # moonlight drains the brass to iron everywhere but the heading ribbon
        remap(img, {BRASS[3]: ASH[2], BRASS[2]: ASH[2], BRASS[1]: ASH[1], BRASS[0]: ASH[0],
                    EMBER[2]: PARCHMENT[1], EMBER[1]: ASH[1], EMBER[0]: ASH[0]}, keep=keep_ribbon)

    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


def PLUM_OR(lit):
    from palette import PLUM
    return PLUM if lit else [INK[1], PLUM[0], PLUM[0]]


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out-root', type=Path, help='directory laid out like textures/ (default: pack-source)')
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    args = ap.parse_args(argv)
    root = args.out_root or geo.TEXTURES
    for key in args.skin or SKINS:
        s = geo.skin(key)
        bg = paint_background(key)
        out = C.save_png(bg, Path(root) / 'menu' / f'{key}.png')
        print('WROTE', out)
        for a in s.art_layers:
            fr = paint_frame(key)
            out = C.save_png(fr, Path(root) / 'frames' / key / f'{a.id}.png')
            print('WROTE', out)


if __name__ == '__main__':
    main()
