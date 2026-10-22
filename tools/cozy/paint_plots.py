#!/usr/bin/env python3
"""Cozy painter "plot": plot_buy, plot_rent, plot_list and plot_manage.

    python tools/cozy/paint_plots.py                     # paint all four into pack-source
    python tools/cozy/paint_plots.py --skin plot_manage
    python tools/cozy/paint_plots.py --out-root DIR      # DIR laid out like textures/

Family identity (decorative regions only): a land surveyor's workbench. A
parchment deed with a double ruled border and brass corner guards, the plot
boundary pegged out with wooden stakes and sagging twine, a signpost with blank
arrow boards, a rolled survey map, a brass key, an eight-point compass rose
(no letters), a picket fence with grass at its feet and a potted sapling.
Accent sage, secondary sky.

* plot_buy / plot_rent (chest_6): the whole static top area is the deed. The
  native plot preview (22) sits inside the pegged boundary square at the
  deed's centre; the Cancel wax slab and Confirm brass plate lie on the deed.
  Between them the sale deed carries a pressed star seal and the key to the
  land; the lease deed carries a linen lease tag and an hourglass. A fence
  runs along the board under the deed.
* plot_list (chest_6): 45 native wells on a surveyor's string grid (sage
  thread); page-turn sheets and a close seal in the bottom row.
* plot_manage (chest_3): three linen/wax controls in the top row, the brass
  Teleport plate, the native Sell / Lease status cells framed as a notice
  pair with two boundary stakes pegged beneath them, and the Destroy wax slab.

No words other than the button labels and the frame headings. Deterministic:
fixed seeds, no clock. Every sprite is an original pixel map (CC0-1.0);
code MIT.
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
from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD, ramp_of, step  # noqa: E402

SKINS = ('plot_buy', 'plot_rent', 'plot_list', 'plot_manage')
SEED = {'plot_buy': 71, 'plot_rent': 73, 'plot_list': 79, 'plot_manage': 83}
TRANSPARENT = (0, 0, 0, 0)

# ---------------------------------------------------------------------------
# Sprite key and hand-authored sprites
# ---------------------------------------------------------------------------
K = {
    'o': INK[1], 'O': INK[0], 'i': INK[2],
    'a': WOOD[0], 'b': WOOD[1], 'c': WOOD[2], 'd': WOOD[3], 'e': WOOD[4],
    '0': BRASS[0], '1': BRASS[1], '2': BRASS[2], '3': BRASS[3],
    'p': PARCHMENT[0], 'q': PARCHMENT[1], 'r': PARCHMENT[2], 's': PARCHMENT[3],
    'g': SAGE[0], 'h': SAGE[1], 'j': SAGE[2],
    'x': BERRY[0], 'y': BERRY[1], 'z': BERRY[2],
    'k': SKY[0], 'l': SKY[1], 'm': SKY[2],
    'E': EMBER[0], 'F': EMBER[1], 'G': EMBER[2],
    'A': ASH[0], 'B': ASH[1], 'D': ASH[2],
}


def spr(img, x, y, rows, flip_x=False, flip_y=False):
    rows = [r.ljust(max(len(q) for q in rows), '.') for r in rows]
    P.sprite(img, x, y, rows, K, flip_x=flip_x, flip_y=flip_y)
    return P.sprite_size(rows)


# Boundary stake (5 x 10): squared top, twine wrapped twice, pointed foot
# driven into the ground.
STAKE = [
    '.ooo.',
    'oedco',
    'oqpqo',
    'oedco',
    'oqpqo',
    'oedco',
    'oedco',
    '.odo.',
    '.oco.',
    '..o..',
]

# Signpost (19 x 32): a turned post with two blank arrow boards, the upper one
# pointing right, the lower one pointing left; a cap on top.
SIGNPOST = [
    '........ooo........',
    '........oeo........',
    '.......oooooooooooo',
    '.......oeedddddddco',
    '.......oeddddddddcco',
    '.......odddddddddcco',
    '.......oddddddddccco',
    '.......occccccccccoo',
    '.......obbbbbbbbbbo.',
    '.......oooooooooooo.',
    '........oeo........',
    '........odo........',
    'oooooooooooo.......',
    'oeedddddddco.......',
    'oedddddddco........',
    'oddddddddco........',
    'odddddddcco........',
    'occccccccco........',
    'obbbbbbbbco........',
    'oooooooooooo.......',
    '........odo........',
    '........odo........',
    '........odo........',
    '........ocoo.......',
    '........oco........',
    '........oco........',
    '........oco........',
    '........obo........',
    '........obo........',
    '........obo........',
    '.......ooooo.......',
    '.......oaaao.......',
]

# Brass key lying flat (14 x 7): round bow with a hole, straight shank, two teeth.
KEY = [
    '.oooo.........',
    'o3322o........',
    'o2o.o2oooooooo',
    'o2o.o222222222o',
    'o2211oooo1o1oo',
    '.o110o...o1o..',
    '..ooo....oo...',
]

# Rolled survey map (18 x 9): parchment scroll with a sage ribbon and the
# sky edge of the map showing at the roll.
SCROLL = [
    '..oooooooooooooo..',
    '.osrrrrrrrrrrrrso.',
    'osrrrgrrrrrrrrrrso',
    'orqrrgrrrrmmrrrqro',
    'orqrrgrrrrrrrrrqro',
    'orpqqgqqqqqqqqqpro',
    '.oppphpppppppppro.',
    '..oooooooooooooo..',
    '.....ogo..........',
]

# Eight-point compass rose (13 x 13): ink outline, parchment and sky quarters,
# the north point in berry. No letters.
COMPASS = [
    '......y......',
    '.....oyo.....',
    '....osyko....',
    '..o.osyko.o..',
    '.ooooskkoooo.',
    '..osssokkko..',
    'oossssokkkkoo',
    '..okkkosssoo.',
    '.oookkosssoo.',
    '..o.okkso.o..',
    '....okkso....',
    '.....oko.....',
    '......o......',
]

# Small hourglass (7 x 11): wooden caps, posts, sand mid-fall.
HOURGLASS = [
    'ooooooo',
    'oeddcbo',
    'ooooooo',
    'o.sss.o',
    'o.oGo.o',
    'o..o..o',
    'o..F..o',
    'o.oFo.o',
    'o.sFs.o',
    'ooooooo',
    'oeddcbo',
]

# Grass tufts (two variants) and a small round tree.
TUFT_A = ['.h.j.', 'hjhjh', '.ghg.']
TUFT_B = ['j.h.j.h', '.hjgjh.', '..ghg..']
TREE = [
    '..ooo..',
    '.ojjho.',
    'ojjhhgo',
    'ohhhggo',
    '.ohggo.',
    '..obo..',
    '..obo..',
]

# Brass corner guard of the deed (6 x 6).
CORNER_GUARD = ['oooooo', 'o3332o', 'o32oo.', 'o2o...', 'o2o...', 'oo....']

# A nail hook (4 x 5) to hang the key from.
HOOK = ['.oo.', 'o23o', 'o2o.', 'o2o.', '.o..']

# Ender-eye-ish preview marker engraved on the Teleport plate (11 x 3) and the
# pegged-boundary engraving on the Confirm plates (13 x 3).
ENGRAVE_ARC = ['#.........#', '.##.....##.', '...#####...']
ENGRAVE_PEGS = ['#.....#.....#', '#######~#####', '#.....#.....#']
ENGRAVE_GLASS = ['#####', '.#.#.', '..#..', '.#.#.', '#####']


# ---------------------------------------------------------------------------
# Drawing helpers (plot family only)
# ---------------------------------------------------------------------------

def engrave(img, x, y, rows, lip=BRASS[3], groove=BRASS[0]):
    """Engrave a motif into a brass plate: groove with a lit lower-right lip."""
    on = {(i, j) for j, r in enumerate(rows) for i, ch in enumerate(r) if ch in '#~'}
    for (i, j) in on:
        if (i + 1, j + 1) not in on:
            P.put(img, x + i + 1, y + j + 1, lip)
    for (i, j) in on:
        P.put(img, x + i, y + j, groove)


def stake(img, x, y, flip=False):
    """Boundary stake with its top-left at (x, y); returns the twine tie point."""
    spr(img, x, y, STAKE, flip_x=flip)
    return (x + 2, y + 2)


def pegged_boundary(img, box, seed, grass=True):
    """Four stakes at the corners of ``box`` joined by sagging twine, with a
    tuft of grass at the foot of each stake."""
    x, y, w, h = box
    corners = [(x, y), (x + w - 5, y), (x, y + h - 10), (x + w - 5, y + h - 10)]
    ties = [stake(img, cx, cy, flip=(i % 2 == 1)) for i, (cx, cy) in enumerate(corners)]
    P.twine(img, ties[0][0] + 1, ties[0][1], ties[1][0] - 1, ties[1][1], sag=2)
    P.twine(img, ties[2][0] + 1, ties[2][1], ties[3][0] - 1, ties[3][1], sag=2)
    for (ax, ay), (bx, by) in ((ties[0], ties[2]), (ties[1], ties[3])):
        for i, (px, py) in enumerate(P.line_points(ax, ay + 1, bx, by - 1)):
            P.put(img, px + (1 if (i // 3) % 2 else 0), py, PARCHMENT[1] if i % 2 else PARCHMENT[0])
    if grass:
        for i, (cx, cy) in enumerate(corners):
            spr(img, cx - 1 + (2 if i % 2 else 0), cy + 8, TUFT_A if i % 2 else TUFT_B[:], flip_x=i >= 2)


def fence(img, x0, x1, y, seed, grass=True, posts=24):
    """Picket fence between x0 and x1 with its top rail at ``y``: posts every
    ``posts`` px, two rails, grass tufts along the foot (rows y+8 .. y+11)."""
    rng = P._rng(seed, 'fence')
    for ry in (y + 1, y + 5):
        P.hline(img, x0, x1, ry - 1, INK[1])
        P.hline(img, x0, x1, ry, WOOD[3])
        P.hline(img, x0, x1, ry + 1, WOOD[1])
        P.hline(img, x0, x1, ry + 2, INK[1])
    px = x0 + 2
    while px <= x1 - 2:
        P.ink_outline(img, (px - 1, y - 2, 4, 12), 'ink_1', radius=0, heavy='b', fill_colour=WOOD[2])
        P.vline(img, px, y - 1, y + 8, WOOD[4])
        P.put(img, px, y - 2, INK[1]); P.put(img, px + 1, y - 2, INK[1])
        P.put(img, px, y - 3, WOOD[3]); P.put(img, px + 1, y - 3, WOOD[3])
        P.put(img, px - 1, y - 3, INK[1]); P.put(img, px + 2, y - 3, INK[1])
        px += posts + rng.choice((-2, 0, 0, 2))
    if grass:
        gx = x0 + 3
        k = 0
        while gx < x1 - 6:
            spr(img, gx, y + 8, TUFT_B if k % 3 == 0 else TUFT_A, flip_x=k % 2 == 1)
            gx += 9 + (k % 3) * 2
            k += 1


def map_sketch(img, box, seed, outline='ink_2'):
    """A surveyor's sketch on parchment: sage field patches (dithered), a sky
    river, a hatched hill, a few trees and a dotted boundary. Nothing that
    reads as a word or a number."""
    x, y, w, h = box
    P.parchment_panel(img, box, seed, outline=outline, fibres=False)
    # fields: two sage patches with dithered edges
    P.fill(img, (x + 3, y + 3, w // 2 - 3, h // 2 - 2), SAGE[2])
    P.dither_patch(img, (x + 3 + w // 2 - 5, y + 3, 4, h // 2 - 2), PARCHMENT[2], 0.5)
    P.fill(img, (x + w // 2 + 2, y + h // 2 + 3, w // 2 - 5, h // 2 - 6), SAGE[2])
    P.dither_patch(img, (x + w // 2 + 2, y + h // 2 + 3, w // 2 - 5, 3), PARCHMENT[2], 0.5)
    # the river, winding from the top right to the bottom left
    pts = P.line_points(x + w - 4, y + 2, x + 3, y + h - 3)
    for i, (px, py) in enumerate(pts):
        jog = (0, 1, 1, 0, -1, -1)[(i // 3) % 6]
        P.put(img, px + jog, py, SKY[1])
        P.put(img, px + jog + 1, py, SKY[2])
    # a hatched hill in the top-right corner
    for k in range(5):
        P.hline(img, x + w - 12 + k, x + w - 4 - k, y + 4 + k, INK[2] if k % 2 else PARCHMENT[1])
    # trees along the lower field
    for k, (tx, ty) in enumerate(((x + 4, y + h - 13), (x + 12, y + h - 11), (x + w - 12, y + h - 14))):
        spr(img, tx, ty, TREE, flip_x=k == 1)
    # dotted boundary of the claim
    bx, by, bw, bh = x + 2, y + 2, w - 4, h - 4
    for i in range(bw):
        if i % 2 == 0:
            P.put(img, bx + i, by, INK[2]); P.put(img, bx + i, by + bh - 1, INK[2])
    for j in range(bh):
        if j % 2 == 0:
            P.put(img, bx, by + j, INK[2]); P.put(img, bx + bw - 1, by + j, INK[2])


def deed_rules(img, box, inset_a=3, inset_b=5):
    """Double ruled border of a deed: a sage rule and a sky rule inside the
    parchment outline."""
    x, y, w, h = box
    for inset, col in ((inset_a, SAGE[1]), (inset_b, SKY[2])):
        P.hline(img, x + inset, x + w - 1 - inset, y + inset, col)
        P.hline(img, x + inset, x + w - 1 - inset, y + h - 1 - inset, col)
        P.vline(img, x + inset, y + inset, y + h - 1 - inset, col)
        P.vline(img, x + w - 1 - inset, y + inset, y + h - 1 - inset, col)


def corner_guards(img, box, inset=1):
    x, y, w, h = box
    for corner, (cx, cy) in (('tl', (x + inset, y + inset)), ('tr', (x + w - 6 - inset, y + inset)),
                             ('bl', (x + inset, y + h - 6 - inset)), ('br', (x + w - 6 - inset, y + h - 6 - inset))):
        spr(img, cx, cy, CORNER_GUARD, flip_x='r' in corner, flip_y='b' in corner)


def ruled_text(img, x, y, widths, colour=SKY[2], pitch=6, phase=0):
    """Dashed ruled lines standing in for deed text (no glyphs)."""
    for k, w in enumerate(widths):
        P.stitch_line(img, x, y + k * pitch, x + w, y + k * pitch, colour, 4, 2, phase=(k + phase) * 2)


def shade(img, x, y):
    """Cast-shadow pixel: darken what is already there (paper two steps)."""
    p = P.get(img, x, y)
    if not p[3]:
        return
    rp = ramp_of(p)
    P.put(img, x, y, step(p, -2 if rp and rp[0] == 'parchment' else -1))


def button_shadows(img, s):
    for b in s.buttons:
        for xx in range(b.x + 1, b.x + b.w + 1):
            shade(img, xx, b.y + b.h)
        for yy in range(b.y + 1, b.y + b.h):
            shade(img, b.x + b.w, yy)


def hanging_deed(img, x, y, seed, sealed=True):
    """Small deed (18 x 24) hanging from a tack: ruled, double-bordered, sealed."""
    box = (x, y, 18, 24)
    P.parchment_panel(img, box, seed, outline='ink_1', fibres=False)
    deed_rules(img, box, 2, 4)
    ruled_text(img, x + 5, y + 7, (8, 8, 6), pitch=3)
    if sealed:
        P.wax_seal(img, x + 12, y + 17, 4, BERRY, seed, drip=False)
    P.tack(img, x + 9, y - 1, small=True)


def shelf(img, x, y, w, seed):
    """Short plank shelf on two brass brackets (5 px board)."""
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def peg(img, x, y):
    P.sprite(img, x - 1, y - 1, ['oeo', 'odb', 'obo'], K)


def ember_window(img, x, y):
    """A lit cottage window (5 x 5) for the frame's dusk vignette."""
    spr(img, x, y, ['ooooo', 'oGFGo', 'oFEFo', 'oGFGo', 'ooooo'])


# ---------------------------------------------------------------------------
# plot_buy / plot_rent
# ---------------------------------------------------------------------------
DEED = (4, 17, 168, 94)            # x 4..171, y 17..110


def paint_deed_background(key):
    renting = key == 'plot_rent'
    seed = SEED[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    x, y, w, h = DEED
    P.parchment_panel(img, DEED, seed, outline='ink_1', radius=1, fibres=True)
    P.ink_outline(img, DEED, 'ink_1', radius=1, heavy='br')
    deed_rules(img, DEED)
    corner_guards(img, DEED)
    # cast shadow of the deed onto the board
    P.hline(img, x + 2, x + w, y + h, WOOD[0])
    P.vline(img, x + w, y + 2, y + h, WOOD[0])
    # heading rule across the deed, with the compass rose at the centre
    P.hline(img, x + 10, x + w - 11, y + 5, SAGE[1])
    P.hline(img, x + 10, x + w - 11, y + 7, SKY[2])
    spr(img, 82, 22, COMPASS)
    # deed text: ruled lines on the left, the survey sketch on the right
    ruled_text(img, 12, 27, (44, 40, 46, 38, 44, 30), phase=1)
    map_sketch(img, (118, 24, 48, 42), seed + 1)
    # the pegged boundary square around the native plot preview
    pegged_boundary(img, (66, 40, 44, 44), seed, grass=True)
    holes = P.merge_holes(s.content_slots)
    P.well_frame(img, holes, 'stitched', 3, thread='parch_0')
    # left of the boundary: a brass key (sale) or the lease hourglass (rent)
    if renting:
        spr(img, 16, 66, HOURGLASS)
        P.lantern_glow_ring(img, 19, 71, 0)
    else:
        spr(img, 10, 62, KEY)
    # between the buttons: seal and ribbon (sale) / lease tag on twine (rent)
    cx, sy = 88, 96
    if renting:
        P.twine(img, 88, 84, 88, 90, sag=0)
        P.linen_tag(img, (73, 90, 30, 13), eyelet='left', seed=seed)
        ruled_text(img, 82, 93, (14, 12), colour=SAGE[1], pitch=4)
    else:
        for k, (dx, dy) in enumerate(((-3, 10), (3, 10))):
            pts = P.line_points(cx + (-1 if k == 0 else 1), sy + 5, cx + dx * 2, sy + dy)
            for i, (px, py) in enumerate(pts):
                P.put(img, px, py, BERRY[1] if i % 3 else BERRY[0])
                P.put(img, px + (1 if k else -1), py, BERRY[2] if i % 2 else BERRY[1])
        P.wax_seal(img, cx, sy, 7, BERRY, seed, drip=True, emblem='star')
    button_shadows(img, s)
    # the board below the deed: a picket fence with grass at its feet
    fence(img, 3, s.width - 4, 114, seed + 2, grass=True, posts=26)
    geo.finish_background(img, key)
    return img


def paint_deed_buttons(key):
    renting = key == 'plot_rent'
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        img = C.paint_button(key, b.id, seed=SEED[key])
        if b.id == 'cancel':
            # a small pressed X in the wax, top right, clear of the lettering
            icons.draw_emblem(img, b.w - 9, 7, 'x', BERRY)
        elif b.id == 'confirm':
            engrave(img, (b.w - 13) // 2, b.h - 9, ENGRAVE_GLASS if renting else ENGRAVE_PEGS)
        geo.finish_button(img, key, b.id)
        out[b.id] = C.button_states(img, key, b.id)
    return out


# ---------------------------------------------------------------------------
# plot_list
# ---------------------------------------------------------------------------

def paint_list_background(key):
    seed = SEED[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    tband, iband = C.bands(key)
    # the surveyor's string grid: sage thread round the 45 wells
    holes = P.merge_holes(s.content_slots)
    P.stitched_well(img, holes, thread=SAGE[2], protect=[tband.tuple(), iband.tuple()])
    # small brass tacks where the string is pinned, in the 6 px margins
    for yy in (18, 60, 102):
        P.tack(img, 2, yy, small=True)
        P.tack(img, s.width - 4, yy, small=True)
    geo.finish_background(img, key)
    return img


def paint_list_buttons(key):
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        img = C.paint_button(key, b.id, seed=SEED[key])
        if b.id in ('previous', 'next'):
            # a sage margin rule on the spine side and a sky base rule
            x, y, w, h = b.body.tuple()
            mx = x + w - 4 if b.id == 'previous' else x + 3
            for yy in range(y + 2, y + h - 2):
                if img.getpixel((mx, yy))[:3] == tuple(PARCHMENT[2]):
                    P.put(img, mx, yy, SAGE[1])
            for xx in range(x + 4, x + w - 4):
                if img.getpixel((xx, y + h - 4))[:3] == tuple(PARCHMENT[2]):
                    P.put(img, xx, y + h - 4, SKY[2])
        geo.finish_button(img, key, b.id)
        out[b.id] = C.button_states(img, key, b.id)
    return out


# ---------------------------------------------------------------------------
# plot_manage
# ---------------------------------------------------------------------------

def paint_manage_background(key):
    seed = SEED[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    tband, iband = C.bands(key)
    # fence posts in the side margins, rails running behind the controls
    for px in (2, s.width - 6):
        P.ink_outline(img, (px, 16, 4, 56), 'ink_1', radius=0, heavy='r', fill_colour=WOOD[2])
        P.vline(img, px + 1, 17, 70, WOOD[4])
        P.put(img, px + 1, 15, WOOD[3]); P.put(img, px + 2, 15, WOOD[3])
        P.put(img, px, 15, INK[1]); P.put(img, px + 3, 15, INK[1])
        for yy in (30, 48):
            P.put(img, px + 2, yy, WOOD[1]); P.put(img, px + 2, yy + 1, WOOD[1])
    # the native status cells: a notice pair on a parchment card
    holes = P.merge_holes(s.content_slots)
    card = (74, 31, 48, 42)
    P.parchment_panel(img, card, seed, outline='ink_2', fibres=False)
    P.well_frame(img, holes, 'stitched', 3, thread='parch_0')
    # under them: the boundary pegged out with two stakes and grass
    a = stake(img, 80, 56)
    b = stake(img, 111, 56, flip=True)
    P.twine(img, a[0] + 1, a[1], b[0] - 1, b[1], sag=2)
    spr(img, 85, 64, TUFT_B)
    spr(img, 101, 65, TUFT_A, flip_x=True)
    spr(img, 93, 60, TREE)
    # brass-nailed rail under the controls
    P.hline(img, 1, s.width - 2, 71, BRASS[1])
    P.hline(img, 1, s.width - 2, 72, INK[1])
    for nx in range(5, s.width - 4, 12):
        P.put(img, nx, 71, BRASS[3])
    geo.finish_background(img, key)
    return img


def _recolour(img, src, dst, rows):
    px = img.load()
    for y in rows:
        for x in range(img.width):
            if px[x, y][:3] == tuple(src) and px[x, y][3]:
                px[x, y] = tuple(dst) + (255,)


def paint_manage_buttons(key):
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        img = C.paint_button(key, b.id, seed=SEED[key])
        if b.id == 'preview':
            _recolour(img, PARCHMENT[0], SKY[1], rows=range(1, b.h - 1))
        elif b.id == 'rename':
            _recolour(img, PARCHMENT[0], SAGE[1], rows=range(1, b.h - 1))
        elif b.id == 'teleport':
            engrave(img, (b.body.w - 11) // 2, b.h - 8, ENGRAVE_ARC)
        elif b.id == 'destroy':
            icons.draw_emblem(img, b.w - 9, 7, 'x', BERRY)
        geo.finish_button(img, key, b.id)
        out[b.id] = C.button_states(img, key, b.id)
    return out


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def paint_frame(key):
    seed = SEED[key]
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    tall = H >= 200

    # ---- left panel: heading tag, signpost, lantern, shelf with map and key
    peg(img, lp.x + 20, 12)
    C.side_tag(img, lp, a.left_heading or a.heading or '', 20, seed, twine_from=(lp.x + 20, 13))
    spr(img, lp.x + 10, 33, SIGNPOST)
    P.lantern(img, lp.x + 31, 44)
    P.lantern_glow_ring(img, lp.x + 34, 49, 11, strength=1)
    shelf(img, lp.x + 4, 76, lp.w - 8, seed + 1)
    spr(img, lp.x + 9, 67, SCROLL)
    spr(img, lp.x + 17, 85, HOOK)
    spr(img, lp.x + 13, 91, KEY, flip_x=True)
    if tall:
        shelf(img, lp.x + 4, 126, lp.w - 8, seed + 2)
        P.mug(img, lp.x + 8, 116, SAGE, steam=True, seed=seed)
        spr(img, lp.x + 22, 112, HOURGLASS)
        map_sketch(img, (lp.x + 6, 140, 28, 30), seed + 3, outline='ink_1')
        P.tack(img, lp.x + 19, 139, small=True)
        fence(img, lp.x + 2, lp.right - 3, H - 26, seed + 4, grass=True, posts=14)
        icons.draw_motif(img, 'herb_pot', lp.x + 26, H - 24)
    else:
        map_sketch(img, (lp.x + 6, 104, 28, 30), seed + 3, outline='ink_1')
        P.tack(img, lp.x + 19, 103, small=True)
        fence(img, lp.x + 2, lp.right - 3, H - 26, seed + 4, grass=True, posts=14)

    # ---- right panel: hanging deed, dusk cottage, pegged boundary, fence
    hanging_deed(img, rp.x + 11, 16, seed + 5, sealed=key != 'plot_list')
    # a cottage on the claim: wall, roof, one lit window, chimney smoke
    cx, cy = rp.x + 6, 50
    P.ink_outline(img, (cx, cy + 8, 28, 14), 'ink_1', radius=0, heavy='br', fill_colour=PARCHMENT[1])
    for k in range(8):
        P.hline(img, cx + 3 + k, cx + 24 - k, cy + k, WOOD[1] if k % 2 else WOOD[2])
        P.put(img, cx + 2 + k, cy + k, INK[1]); P.put(img, cx + 25 - k, cy + k, INK[1])
    P.hline(img, cx + 2, cx + 25, cy + 8, INK[1])
    P.ink_outline(img, (cx + 19, cy - 4, 4, 6), 'ink_1', radius=0, fill_colour=WOOD[1])
    spr(img, cx + 18, cy - 9, ['.D.', 'D..', '.D.', '..D'])
    ember_window(img, cx + 5, cy + 12)
    P.lantern_glow_ring(img, cx + 7, cy + 14, 7, strength=1)
    P.ink_outline(img, (cx + 17, cy + 13, 5, 9), 'ink_1', radius=0, fill_colour=WOOD[0])
    P.put(img, cx + 20, cy + 17, BRASS[2])
    spr(img, cx + 1, cy + 22, TUFT_A)
    spr(img, cx + 23, cy + 22, TUFT_B)
    pegged_boundary(img, (rp.x + 6, 86, 28, 34), seed + 6, grass=True)
    spr(img, rp.x + 15, 96, TREE)
    if tall:
        shelf(img, rp.x + 4, 150, rp.w - 8, seed + 7)
        icons.draw_motif(img, 'crate', rp.x + 7, 140)
        spr(img, rp.x + 20, 141, SCROLL[:8])
        icons.draw_motif(img, 'candle', rp.x + 25, 166)
        P.lantern_glow_ring(img, rp.x + 27, 168, 9, strength=1)
        icons.draw_motif(img, 'herb_pot', rp.x + 6, 168)
        fence(img, rp.x + 2, rp.right - 3, H - 26, seed + 8, grass=True, posts=14)
    else:
        icons.draw_motif(img, 'herb_pot', rp.x + 6, 128)
        icons.draw_motif(img, 'candle', rp.x + 25, 130)
        P.lantern_glow_ring(img, rp.x + 27, 132, 9, strength=1)
        fence(img, rp.x + 2, rp.right - 3, H - 26, seed + 8, grass=True, posts=14)

    # ---- bottom strip: a rope run between two tacks
    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0)
    P.tack(img, 10, H - 5); P.tack(img, a.w - 11, H - 5)
    P.highlight_edge(img, (lp.x + 1, 9, lp.w - 2, H - 18), WOOD[2], 'l', broken=4, seed=seed)
    P.shadow_edge(img, (rp.x, 9, rp.w - 1, H - 18), INK[1], 'r')
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
PAINTERS = {
    'plot_buy': (paint_deed_background, paint_deed_buttons),
    'plot_rent': (paint_deed_background, paint_deed_buttons),
    'plot_list': (paint_list_background, paint_list_buttons),
    'plot_manage': (paint_manage_background, paint_manage_buttons),
}


def paint(key, out_root=None):
    s = geo.skin(key)
    root = Path(out_root) if out_root else None
    bg_fn, btn_fn = PAINTERS[key]
    C.save_png(bg_fn(key), s.background_path if root is None else root / 'menu' / f'{key}.png')
    for bid, states in btn_fn(key).items():
        C.save_button_states(states, key, bid, root=root)
    for a in s.art_layers:
        fr = paint_frame(key)
        C.save_png(fr, s.frame_path(a.id) if root is None else root / 'frames' / key / f'{a.id}.png')
    print(f'PAINTED {key}: background, {len(s.buttons)} buttons x 6 states, {len(s.art_layers)} frame(s)')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', type=Path, help='directory laid out like textures/ (default: pack-source)')
    a = ap.parse_args(argv)
    for rows in (STAKE, SIGNPOST, KEY, SCROLL, COMPASS, HOURGLASS, TREE, CORNER_GUARD, HOOK):
        assert len({len(r) for r in rows}) <= 2, rows   # ragged rows are padded by spr()
    for key in a.skin or SKINS:
        paint(key, a.out_root)
    return 0


if __name__ == '__main__':
    sys.exit(main())
