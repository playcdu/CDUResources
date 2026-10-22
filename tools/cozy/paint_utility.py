#!/usr/bin/env python3
"""Cozy painter "utility": trashcan, ender_chest and crafting.

    python tools/cozy/paint_utility.py                    # paint all three into pack-source
    python tools/cozy/paint_utility.py --skin crafting    # one skin
    python tools/cozy/paint_utility.py --out-root DIR     # write a textures/-shaped tree elsewhere

Every texture is painted deterministically (fixed seeds) on top of the shared
cozy base (compose.base_background / base_frame), then finished with the
geometry helpers so masks are cleared and advance pins stamped last.

* trashcan    (chest_6, 54 wells, 256x238 frame): compost bin and leaves.
  Weathered slatted boards with carved wells; the frame carries a garden
  fork, a compost-bin lid with a rope loop, a leaf rake, autumn leaves, a
  hanging lantern, drying herbs, a watering can, a planter of sprouting herbs
  and a slatted compost bin heaped with leaves (and one worm).
* ender_chest (chest_3, 27 wells, 256x184 frame): indigo-dark wood and soft
  purple lantern light pooled by dither; stars, a crescent moon, an eye
  charm, an hourglass, a crystal ball, potions and books. Only the heading
  word UTILITY appears.
* crafting    (176x166, no frame): a workbench with a tool loop - a claw
  hammer hanging from a rope between pegs, chisel, awl and gouge in a leather
  strap, a hand saw hung on two pegs, a mallet with shavings, a try square,
  an oil can, a crate of nails, twine and a candle; a pencil rests on the
  title sheet left of the live title (x < 29). The recipe toggle and arrow
  rects stay transparent.

Artwork CC0-1.0, code MIT. Every sprite below is original.
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
from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, PLUM, SAGE, SKY, WOOD, name_of  # noqa: E402

BAYER4 = P.BAYER4
SKINS = ('trashcan', 'ender_chest', 'crafting')

# One shared sprite key: every character is a palette colour.
K = {
    'O': INK[0], 'o': INK[1], 'i': INK[2],
    '0': WOOD[0], '1': WOOD[1], '2': WOOD[2], '3': WOOD[3], '4': WOOD[4],
    'w': PARCHMENT[0], 'x': PARCHMENT[1], 'y': PARCHMENT[2], 'z': PARCHMENT[3],
    'q': BRASS[0], 'r': BRASS[1], 's': BRASS[2], 't': BRASS[3],
    'g': SAGE[0], 'h': SAGE[1], 'j': SAGE[2],
    'B': BERRY[0], 'C': BERRY[1], 'D': BERRY[2],
    'k': SKY[0], 'l': SKY[1], 'm': SKY[2],
    'e': EMBER[0], 'f': EMBER[1], 'F': EMBER[2],
    'u': PLUM[0], 'v': PLUM[1], 'V': PLUM[2],
    'a': ASH[0], 'b': ASH[1], 'c': ASH[2],
}


def spr(img, x, y, rows, flip_x=False, flip_y=False, key=None):
    P.sprite(img, x, y, rows, key or K, flip_x=flip_x, flip_y=flip_y)
    return P.sprite_size(rows)


# ---------------------------------------------------------------------------
# Shared small sprites (hand-authored)
# ---------------------------------------------------------------------------

LEAF_INKED = ['...ooo', '..o22o', '.o2m2o', 'o2m1o.', 'om1o..', 'oo....']
LEAF_TINY = ['..oo', '.o2o', 'om1o', 'oo..']
LEAF_RAMPS = {
    'sage': (SAGE[0], SAGE[1], SAGE[2]),
    'amber': (EMBER[0], EMBER[1], BRASS[2]),
    'rust': (BERRY[0], BERRY[1], EMBER[1]),
    'gold': (BRASS[0], BRASS[1], BRASS[3]),
}


def leaf(img, x, y, kind='sage', direction='ne', small=False):
    """A leaf with a warm ink outline and a vein in the darkest tone."""
    d, m, l = LEAF_RAMPS[kind]
    spr(img, x, y, LEAF_TINY if small else LEAF_INKED, 'w' in direction, 's' in direction,
        key={'o': INK[1], '2': l, '1': m, 'm': d})


MAPLE = [      # maple leaf, stem down (9 x 10)
    '....o....',
    '.o.o2o.o.',
    'o2oo2oo2o',
    'o22o2o22o',
    '.o22m21o.',
    'oo2m2m1oo',
    'o22mm1m1o',
    '.o221m1o.',
    '..oo1oo..',
    '....o....',
]
OAK = [        # broad oak-ish leaf pointing up-right (9 x 9)
    '......ooo',
    '....oo22o',
    '...o22m2o',
    '..o2m2m1o',
    '.o2m2m1o.',
    'o22m1m1o.',
    'o2m111o..',
    'om1ooo...',
    'oo.......',
]


def big_leaf(img, x, y, kind='amber', shape='maple', flip=False):
    d, m, l = LEAF_RAMPS[kind]
    spr(img, x, y, MAPLE if shape == 'maple' else OAK, flip_x=flip,
        key={'o': INK[1], '2': l, '1': m, 'm': d})


SPROUT = ['jj.hh', 'jhgjh', '..g..', '..g..']
SPROUT_TALL = ['.jj....', 'jhhj.hh', '.jjghjh', '...g...', '..hg...', '..jg...', '...g...']
STAR5 = ['..t..', '.tFt.', 'tFzFt', '.tFt.', '..t..']
STAR3 = ['.V.', 'VzV', '.V.']


# ---------------------------------------------------------------------------
# Tools for the crafting workbench and the garden
# ---------------------------------------------------------------------------

HAMMER_HEAD = [  # claw hammer head seen from the side, claw left, face right (14 x 7)
    '...ooooooo.ooo',
    '..occcccccooco',
    '.ocbbbbbbbbbbo',
    'ocbbbbbbbbbbbo',
    'obaaoooooaaaao',
    'oao.o432o.oaoo',
    'oo..o321o..oo.',
]

SAW_HANDLE = [  # open pistol grip of a hand saw (12 x 11)
    '...ooooooo..',
    '..o4444433o.',
    '.o44oooo32o.',
    'o43o....o21o',
    'o32o....o21o',
    'o32o....o21o',
    'o32o...o21o.',
    'o32ooooo1o..',
    'o322221110o.',
    'o2111110oo..',
    '.ooooooo....',
]

OIL_CAN = [     # brass oil can: cone body, long spout, thumb pump (12 x 13)
    '..........oo',
    '.........oto',
    '........oso.',
    '.......oso..',
    '......oso...',
    '...oooso....',
    '..otsso.....',
    '..ostqo.....',
    '.otsrrqo....',
    'otssrrrqo...',
    'osrrrrrqo...',
    'oqqqqqqqo...',
    '.ooooooo....',
]

TWINE_BALL = [  # ball of garden twine with a loose end (11 x 8)
    '..ooooo....',
    '.ozyyxyo...',
    'ozyxyyxyo..',
    'oyxyyxyxo..',
    'oxyyxyxwo..',
    'oyyxyxywoxx',
    '.oxyxwwox..',
    '..ooooo....',
]

NAIL = ['ooo', 'ocb', '.b.', '.a.']

CHISEL = [     # bench chisel, handle up (5 x 21)
    '.ooo.',
    'o443o',
    'o332o',
    'o332o',
    'o332o',
    'o221o',
    'o221o',
    'oo1oo',
    'otsqo',
    '.oqo.',
    '.oco.',
    '.oco.',
    '.oco.',
    '.ocbo',
    '.ocbo',
    'occbo',
    'occbo',
    'occbo',
    'occao',
    'ozzzo',
    '.ooo.',
]

AWL = [        # bradawl, handle up (5 x 18)
    '.ooo.',
    'oDDCo',
    'oDCCo',
    'oDCCo',
    'oCCBo',
    'oCCBo',
    'oo1oo',
    'otsqo',
    '.oqo.',
    '..oo.',
    '.oco.',
    '.oco.',
    '.oco.',
    '.obo.',
    '.obo.',
    '..o..',
    '..o..',
    '.....',
]

GOUGE = [      # gouge with a round mushroom handle (5 x 20)
    '.ooo.',
    'o443o',
    'o443o',
    'o332o',
    '.o2o.',
    '.o2o.',
    'o332o',
    'o221o',
    'oo1oo',
    'otsqo',
    '.oqo.',
    '.oco.',
    '.oco.',
    '.ocbo',
    '.ocbo',
    'occbo',
    'ocabo',
    'oc.bo',
    'ozzzo',
    '.ooo.',
]

TRY_SQUARE = [  # wooden stock with a brass blade, hung on a nail (16 x 13)
    'ooooo...........',
    'o433o...........',
    'o322ooooooooooo.',
    'o322ostssssssstO',
    'o322orroroororrO',
    'o322oqqqqqqqqqqO',
    'o322ooooooooooo.',
    'o322o...........',
    'o322o...........',
    'o211o...........',
    'o211o...........',
    'o111o...........',
    'oOOOO...........',
]

PENCIL = [     # carpenter's pencil, sharpened to the right (19 x 4)
    '.' + 'o' * 15 + '...',
    'o' + 'F' + 'f' * 13 + 'o' + '33' + 'O',
    'o' + 'e' * 14 + 'o' + '2' + 'o' + '.',
    '.' + 'o' * 15 + '...',
]


def mallet(img, x, y, seed):
    """Carpenter's mallet lying on the bench (24 x 10): end-grain beech head
    with two darker bands, round handle to the right."""
    hx = x + 8
    P.ink_outline(img, (hx, y + 3, 16, 4), 'ink_1', radius=1, heavy='br', fill_colour=WOOD[3])
    P.hline(img, hx + 1, hx + 13, y + 4, WOOD[4])
    P.hline(img, hx + 1, hx + 14, y + 5, WOOD[2])
    P.put(img, hx + 14, y + 4, WOOD[2])
    P.plank(img, (x, y, 9, 10), WOOD, (seed, 'mallet'), 'ink_1', radius=1, vertical=True, grain=0.0, heavy='br')
    P.vline(img, x + 2, y + 1, y + 8, WOOD[1]); P.vline(img, x + 6, y + 1, y + 8, WOOD[1])
    P.put(img, x + 4, y + 3, WOOD[1]); P.put(img, x + 4, y + 6, WOOD[1])
    P.put(img, x + 1, y + 2, WOOD[4]); P.put(img, x + 1, y + 3, WOOD[4])


SHAVING_A = ['.44.', '4..3', '4.3.', '.3..']
SHAVING_B = ['.443', '4...', '.33.', '...3']


def saw(img, x, y, length=40):
    """Hand saw hung flat: tip at the left (x), D-grip at the right. Straight
    lit back, blade deepening toward the heel, serrated teeth along the bottom
    (ink points over the board, never holes)."""
    for i in range(length):
        xx = x + i
        depth = 5 + (i * 3) // length                # steel rows: 5 at the tip .. 7 at the heel
        P.put(img, xx, y, INK[1])                    # back edge
        P.put(img, xx, y + 1, PARCHMENT[2] if i % 7 else ASH[2])   # lit back
        for j in range(2, depth):
            P.put(img, xx, y + j, ASH[2] if j < depth - 2 else ASH[1] if j < depth - 1 else ASH[0])
        P.put(img, xx, y + depth, INK[1])            # cutting edge
        if i % 2 == 0:
            P.put(img, xx, y + depth + 1, INK[1])    # tooth points
    P.vline(img, x, y, y + 6, INK[1])                # square tip
    P.put(img, x + 1, y + 1, ASH[2])
    for gx in range(x + 5, x + 12):                  # a long glint, broken by hand
        if gx != x + 9:
            P.put(img, gx, y + 2, PARCHMENT[3])
    P.put(img, x + 21, y + 3, ASH[2]); P.put(img, x + 22, y + 3, ASH[2])
    spr(img, x + length - 2, y - 2, SAW_HANDLE)
    for sy in (y + 1, y + 6):                        # brass screws through the heel
        P.put(img, x + length - 1, sy, BRASS[3]); P.put(img, x + length - 1, sy + 1, BRASS[0])


def hammer(img, x, y, handle=24):
    """Claw hammer hanging head-up: steel head (HAMMER_HEAD) on a wooden
    handle with a leather-wrapped grip; (x, y) is the head's top-left."""
    hx = x + 4                                       # handle outline column
    P.ink_outline(img, (hx, y + 5, 5, handle), 'ink_1', radius=1, heavy='br', fill_colour=WOOD[2])
    P.vline(img, hx + 1, y + 6, y + 4 + handle - 1, WOOD[3])
    P.vline(img, hx + 3, y + 6, y + 4 + handle - 1, WOOD[1])
    P.put(img, hx + 1, y + 8, WOOD[4]); P.put(img, hx + 1, y + 9, WOOD[4])
    for k in range(7):                               # leather grip, wound
        gy = y + 4 + handle - 8 + k
        P.hline(img, hx + 1, hx + 3, gy, WOOD[0] if k % 2 else WOOD[1])
        P.put(img, hx + 1, gy, BERRY[0] if k % 2 else WOOD[1])
    P.hline(img, hx + 1, hx + 3, y + 4 + handle - 9, BRASS[2])
    spr(img, x, y, HAMMER_HEAD)
    P.put(img, x + 12, y + 2, PARCHMENT[3])          # glint on the face


GARDEN_FORK = (
    ['..ooooo..',
     '.o44443o.',
     'o4o...o2o',
     'o3o...o1o',
     '.o3ooo1o.',
     '..o431o..']
    + ['..o321o..'] * 24
    + ['..otsqo..',
       '..otsqo..',
       '.ooooooo.',
       'occcccbbo',
       'oaaaaaaao',
       'ocococobo',
       'ocococobo',
       'ocococobo',
       'ocococobo',
       'ocococobo',
       'ocococobo',
       '.o.o.o.o.']
)

TROWEL = (
    ['.ooo.',
     'o443o',
     'o332o',
     'o332o',
     'o221o',
     'o221o',
     'o221o',
     '.oto.',
     '.oqo.',
     'ooooooo',
     'occccbo',
     'occcbbo',
     'ocbcbbo',
     'ocbbbao',
     '.ocbbo.',
     '.ocbao.',
     '..oao..',
     '..oo...',
     '...o...'])

WATERING_CAN = [
    '.....ooooo.......',
    '....o.....o......',
    '...o.......o.....',
    '..ooooooooooo....',
    '..omlllllllko...o',
    '..omlllllllkooool',
    '..omllllllllkkko.',
    '..omllllllllkoo..',
    '..omllllllllko...',
    '..omkkkkkkkkko...',
    '...ooooooooooo...',
]

SEED_PACKET = [
    'ooooooooo',
    'oyzzzzzyo',
    'oyxxxxxyo',
    'oyyyjyyyo',
    'oyyjhjyyo',
    'oyyygyyyo',
    'oyxyxyxyo',
    'oyyyyyyxo',
    'oxxxxxxxo',
    'ooooooooo',
]

WORM = ['.DD...', 'D..D.D', '....DD']


def compost_bin(img, x, y, w, h, seed):
    """Slatted compost bin: two corner posts, horizontal slats with dark gaps
    showing leaf-mould inside, and a heap of leaves and sprouts piled on top."""
    top = y + 12                                      # first slat; the heap rises above it
    P.fill(img, (x + 2, top, w - 4, h - (top - y) - 1), WOOD[0])   # dark interior in the gaps
    for k, (gx, gy) in enumerate(((5, 7), (14, 15), (22, 7), (9, 23), (19, 31), (26, 23))):
        if top + gy < y + h - 2:
            P.put(img, x + gx, top + gy, SAGE[0] if k % 2 else WOOD[1])
    # heap of leaf-mould: a rounded mound, inked on top
    n = w - 4
    for i in range(n):
        f = (i - (n - 1) / 2) / ((n - 1) / 2)
        hh = int(round(7 - 5 * f * f))
        P.vline(img, x + 2 + i, top - hh + 1, top, WOOD[1] if (i * 7) % 5 else WOOD[0])
        P.put(img, x + 2 + i, top - hh, INK[1])
        if i % 4 == 1 and hh > 3:
            P.put(img, x + 2 + i, top - hh + 2, WOOD[2])
    spr(img, x + 13, top - 14, SPROUT_TALL)
    big_leaf(img, x + 3, top - 10, 'amber', 'maple')
    big_leaf(img, x + 21, top - 11, 'rust', 'oak', flip=True)
    leaf(img, x + 10, top - 5, 'sage', 'ne', small=True)
    spr(img, x + 18, top - 4, WORM)
    # slats
    sy = top + 1
    for k in range(4):
        P.plank(img, (x + 1, sy, w - 2, 6), WOOD, (seed, 'slat', k), 'ink_1', radius=1, grain=0.7)
        sy += 8
    # corner posts, taller than the slats, with brass bolts
    for px in (x, x + w - 5):
        P.plank(img, (px, top - 3, 5, h - (top - y) + 3), WOOD, (seed, 'post', px), 'ink_1',
                radius=1, vertical=True, grain=0.4)
        for by in (top + 3, top + 19):
            P.put(img, px + 2, by, BRASS[3]); P.put(img, px + 3, by + 1, BRASS[0])


def wooden_lid(img, x, y, w, h, seed):
    """Compost-bin lid leaning on the wall: three vertical slats on two
    battens, with a rope carry-loop through the top edge."""
    sw = w // 3
    for k in range(3):
        bw = sw if k < 2 else w - 2 * sw
        P.plank(img, (x + k * sw, y, bw + (1 if k < 2 else 0), h), WOOD, (seed, 'lid', k), 'ink_1',
                radius=1, vertical=True, grain=0.6)
    for by in (y + 5, y + h - 9):
        P.plank(img, (x - 1, by, w + 2, 5), WOOD, (seed, 'batten', by), 'ink_1', radius=1, grain=0.3)
        P.put(img, x + 1, by + 2, BRASS[3]); P.put(img, x + w - 2, by + 2, BRASS[3])
    # rope carry-loop threaded through the top edge, arching above it
    sx0, sx1 = x + 5, x + w - 6
    P.rope(img, sx0, y + 1, sx1, y + 1, sag=-6)
    for sx in (sx0, sx1):
        spr(img, sx - 1, y + 1, ['oOo', '.o.'])


def leaf_rake(img, cx, y, handle=30):
    """Fan-shaped leaf rake hanging tines-down; ``cx`` is the handle centre."""
    P.ink_outline(img, (cx - 1, y, 4, handle), 'ink_1', radius=1, heavy='r', fill_colour=WOOD[2])
    P.vline(img, cx, y + 1, y + handle - 2, WOOD[3])
    P.put(img, cx, y + 3, WOOD[4]); P.put(img, cx, y + 4, WOOD[4])
    by = y + handle - 1
    spr(img, cx - 2, by, ['oooooo', 'otssqo', '.oooo.'])            # brass collar
    sy = by + 3
    ends = []
    for k in range(-3, 4):                                        # seven tines fan out
        ex = cx + k * 3 + (1 if k > 0 else 0)
        ey = sy + 12 - (k * k) // 3
        for (px, py) in P.line_points(cx + (1 if k > 0 else 0), sy, ex, ey):
            P.put(img, px, py, ASH[2] if k <= 0 else ASH[1])
        ends.append((ex, ey))
    for (ex, ey) in ends:                                          # bent tips
        P.put(img, ex, ey + 1, INK[1])
    for k in range(-3, 4):                                        # cross wire
        P.put(img, cx + (k * 3) // 2 + (1 if k > 0 else 0), sy + 5, ASH[0])
    P.put(img, cx, sy, INK[1]); P.put(img, cx + 1, sy, INK[1])


def planter(img, x, y, w, seed):
    """Long wooden planter box with herbs sprouting at different heights."""
    spr(img, x + 2, y, SPROUT_TALL)
    spr(img, x + 11, y + 3, SPROUT)
    spr(img, x + 18, y + 1, ['.jj.', 'jhhj', '.gj.', '.g..', 'hg..', '.g..'])
    spr(img, x + 25, y + 3, SPROUT)
    P.plank(img, (x, y + 7, w, 8), WOOD, (seed, 'planter'), 'ink_1', radius=1, grain=0.6)
    P.hline(img, x + 1, x + w - 2, y + 8, WOOD[0])                 # soil line
    P.hline(img, x + 2, x + w - 3, y + 8, WOOD[1])
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 15, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def herb_bundle(img, x, y, kind):
    """Bunch of herbs hung upside-down to dry: twine tie at the top."""
    spr(img, x + 2, y, ['.o.', 'oxo', 'oxo'])
    if kind == 0:
        spr(img, x, y + 3, ['.ghg.', 'ghjhg', 'hjgjh', 'jh.hj', 'j.j.j', '.j.h.'])
    elif kind == 1:
        spr(img, x, y + 3, ['.ghg.', 'hjgjh', 'gjhjg', 'j.h.j', 'h.j.h', '..j..', '..h..'])
    else:
        spr(img, x, y + 3, ['.ggg.', 'gDhDg', 'hjgjh', 'D.j.D', '.j.h.'])


# ---------------------------------------------------------------------------
# Ender motifs
# ---------------------------------------------------------------------------

EYE_CHARM = [   # brass ring with a teal eye and a dark slit pupil (11 x 11)
    '...ooooo...',
    '..otsssso..',
    '.osooooosq.',
    'osohhjjhosq',
    'tsohmOmhosq',
    'ssojmOmjosq',
    'ssohmOmhoqq',
    'osohhjjhoqo',
    '.oqooooooq.',
    '..oqqqqqo..',
    '...ooooo...',
]

MOON = [        # crescent moon (9 x 11)
    '...ooo...',
    '..oztoo..',
    '.oztoo...',
    'oztto....',
    'oztso....',
    'oztso....',
    'oztso....',
    'oztsso...',
    '.ozttoo..',
    '..ozzsoo.',
    '...oooo..',
]

POTION = [      # small bottle of plum potion (7 x 11)
    '..ooo..',
    '..o1o..',
    '..ooo..',
    '..omo..',
    '.oommo.',
    'ommmmmo',
    'omVVVVo',
    'omVvvVo',
    'oVvvvuo',
    'ovvvuuo',
    '.ooooo.',
]

POTION_SKY = [  # squat round flask (7 x 9)
    '..ooo..',
    '..oxo..',
    '..omo..',
    '.ommmo.',
    'omllllo',
    'omlmlko',
    'olllkko',
    '.okkko.',
    '..ooo..',
]

BOOKS_UP = [    # three books standing (12 x 13)
    '.ooo........',
    '.oVo.ooo....',
    '.oVoooxo....',
    '.oVvoxyo.ooo',
    '.ovvoxyoomlo',
    '.ovvoxyoomlo',
    '.oxxoxyoozzo',
    '.ovvoxyoomlo',
    '.ovvoyyoomlo',
    '.ovvoxyoomlo',
    '.ovvoxxoomko',
    '.ouuowwookko',
    '.oooooooOooo',
]

JAR_CANDLE = [  # candle in a plum glass jar (9 x 12)
    '...F.....',
    '..FfF....',
    '...F.....',
    '...o.....',
    '.ooooooo.',
    'oVvzzvvVo',
    'oVvzyvvuo',
    'oVvyyvvuo',
    'ovvyxvvuo',
    'ovvxxvuuo',
    'ouuuuuuuo',
    '.ooooooo.',
]

CHEST = [       # small indigo strongbox with a teal clasp (15 x 11)
    '.ooooooooooooo.',
    'oVVVVVVVVVVVVvo',
    'ovvvvvvvvvvvvuo',
    'ovvvvvoooovvvuo',
    'oooooootsoooooo',
    'ouuuuuohmouuuuo',
    'ovvvvvohjovvvuo',
    'ovvvvvoooovvvuo',
    'ovvvvvvvvvvvvuo',
    'ouuuuuuuuuuuuuo',
    '.ooooooooooooo.',
]

HOURGLASS = [   # hourglass with plum sand (7 x 12)
    'ooooooo',
    'o43332o',
    'ooooooo',
    '.ozmmo.',
    '.omVmo.',
    '..oVo..',
    '.omVmo.',
    '.oVVVo.',
    '.oVvVo.',
    'ooooooo',
    'o32221o',
    'ooooooo',
]

CRYSTAL = [     # crystal ball with a plum swirl on a brass stand (11 x 13)
    '...ooooo...',
    '..ozzmmlo..',
    '.ozmVVVmlo.',
    'ozmVvvvVmlo',
    'omVvuuuvVlo',
    'omVvuuuvVko',
    'omlVvvvVlko',
    '.omlVVVlko.',
    '..ollllko..',
    '...ooooo...',
    '..otsssqo..',
    '.otssssrqo.',
    '.ooooooooo.',
]

# Ender board colours under purple lantern light (one step "lit" toward plum).
ENDER_LIT = {
    INK[0]: PLUM[0], PLUM[0]: PLUM[1], INK[1]: PLUM[0], PLUM[1]: PLUM[2], WOOD[1]: PLUM[2],
    WOOD[0]: PLUM[1], PLUM[2]: PLUM[2],
}


def ender_glow(img, cx, cy, r, protect=()):
    """Purple lantern light pooled by hand dither: solid core, 50 % checker,
    sparse 25 % Bayer at the rim. Only board pixels in ENDER_LIT change;
    alpha never changes. Call before drawing objects over the board."""
    base = img.copy()
    bpx = base.load()
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if not (0 <= x < img.width and 0 <= y < img.height):
                continue
            if any(px <= x < px + pw and py <= y < py + ph for (px, py, pw, ph) in protect):
                continue
            p = bpx[x, y]
            if p[3] == 0 or tuple(p[:3]) not in ENDER_LIT:
                continue
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 <= (r * 2 // 5) ** 2:
                lit = True
            elif d2 <= (r * 3 // 5) ** 2:
                lit = (x + y) % 2 == 0
            elif d2 <= r * r:
                lit = BAYER4[y % 4][x % 4] < 4
            else:
                lit = False
            if lit:
                P.put(img, x, y, ENDER_LIT[tuple(p[:3])])


def shelf(img, x, y, w, seed, ramp=WOOD, bracket=BRASS[1]):
    """Short plank shelf on two brackets."""
    P.plank(img, (x, y, w, 5), ramp, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': bracket})


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _out(root, rel):
    return (Path(root) if root else geo.TEXTURES) / rel


def save_background(img, key, root):
    geo.finish_background(img, key)
    return C.save_png(img, _out(root, f'menu/{key}.png'))


def save_frame(img, key, layer_id, root):
    geo.finish_frame(img, key, layer_id, 'ink_0')
    return C.save_png(img, _out(root, f'frames/{key}/{layer_id}.png'))


# ---------------------------------------------------------------------------
# TRASHCAN: compost bin and leaves
# ---------------------------------------------------------------------------

# weathered slats: warm body, grey weathered grain, silvered sheen
WEATHERED = [WOOD[0], ASH[0], WOOD[2], ASH[2], WOOD[4]]
TRASH_SEED = 41


def paint_trashcan_background():
    key = 'trashcan'
    s = geo.skin(key)
    img = C.base_background(key, seed=TRASH_SEED, wells='wood', ramp=WEATHERED)
    tband, iband = C.bands(key)
    # slats: a nail head at both ends of every board in the side margins
    for yy in range(3, s.height - 3, 9):
        for xx in (2, s.width - 3):
            if P.get(img, xx, yy)[3] and name_of(P.get(img, xx, yy)) not in ('ink_1',):
                P.put(img, xx, yy, ASH[2])
    # a fallen sprig and leaves at the right end of the inventory band, away from the label
    leaf(img, iband.right - 14, iband.y + 1, 'sage', 'ne', small=True)
    leaf(img, iband.right - 21, iband.y + 3, 'amber', 'nw', small=True)
    P.twine(img, iband.right - 25, iband.y + 6, iband.right - 8, iband.y + 6, sag=1, colour='sage_1', knot='sage_0')
    leaf(img, iband.right - 31, iband.y + 2, 'gold', 'ne', small=True)
    # brass tacks at the bottom corners, worn corners
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    return img


def paint_trashcan_frame():
    key = 'trashcan'
    s = geo.skin(key)
    a = s.layer()
    seed = TRASH_SEED
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp, H = a.left_panel, a.right_panel, a.h
    L0, R0 = lp.x, rp.x                     # 0, 216

    # light first: the glow only lifts the boards it lands on
    P.lantern_glow_ring(img, R0 + 21, 24, 16, strength=1)

    # ---- left panel: tag, fork and lid, rake, herbs, trowel, leaf heap ----
    P.rope(img, L0 + 4, 12, L0 + 35, 12, sag=2)
    P.tack(img, L0 + 4, 11); P.tack(img, L0 + 35, 11)
    C.side_tag(img, lp, a.left_heading or a.heading, 21, seed, twine_from=(L0 + 20, 14))
    P.tack(img, L0 + 8, 36)
    spr(img, L0 + 4, 38, GARDEN_FORK)
    wooden_lid(img, L0 + 17, 44, 20, 32, seed)
    big_leaf(img, L0 + 15, 78, 'amber', 'oak')
    P.tack(img, L0 + 20, 90)
    leaf_rake(img, L0 + 20, 92, handle=28)
    big_leaf(img, L0 + 3, 99, 'rust', 'maple')
    big_leaf(img, L0 + 28, 107, 'gold', 'oak', flip=True)
    big_leaf(img, L0 + 24, 128, 'amber', 'maple')          # caught in the tines
    leaf(img, L0 + 6, 140, 'sage', 'ne')
    leaf(img, L0 + 30, 147, 'amber', 'nw', small=True)
    shelf(img, L0 + 4, 168, 32, seed)
    icons.draw_motif(img, 'herb_pot', L0 + 6, 156)
    spr(img, L0 + 20, 158, SEED_PACKET)
    spr(img, L0 + 31, 160, ['.jj', 'jhg', '..g', '..g'])
    P.tack(img, L0 + 9, 181)
    spr(img, L0 + 7, 183, TROWEL)
    big_leaf(img, L0 + 22, 184, 'rust', 'oak', flip=True)
    leaf(img, L0 + 28, 197, 'gold', 'ne')
    for (lx, ly, kind, shape, fl) in ((L0 + 4, 209, 'gold', 'oak', False), (L0 + 12, 205, 'amber', 'maple', False),
                                      (L0 + 21, 207, 'sage', 'oak', True), (L0 + 28, 211, 'rust', 'maple', False),
                                      (L0 + 2, 218, 'rust', 'maple', False), (L0 + 10, 215, 'sage', 'oak', False),
                                      (L0 + 18, 217, 'amber', 'maple', False), (L0 + 27, 219, 'gold', 'oak', True)):
        big_leaf(img, lx, ly, kind, shape, fl)

    # ---- right panel: lantern, drying herbs, watering can, planter, bin ----
    P.rope(img, R0 + 4, 12, R0 + 36, 12, sag=2)
    P.tack(img, R0 + 4, 11); P.tack(img, R0 + 36, 11)
    P.vline(img, R0 + 21, 14, 16, INK[1])
    P.lantern(img, R0 + 18, 17)
    P.twine(img, R0 + 4, 44, R0 + 36, 44, sag=3)
    P.tack(img, R0 + 4, 43); P.tack(img, R0 + 36, 43)
    for k, hx in enumerate((R0 + 8, R0 + 18, R0 + 28)):
        herb_bundle(img, hx, 45 + (2 if k == 1 else 1), k)
    shelf(img, R0 + 4, 92, 32, seed + 3)
    spr(img, R0 + 5, 81, WATERING_CAN)
    spr(img, R0 + 25, 81, ['.jj.hh', 'jhhghj', '..ggh.', 'oooooo', 'o2332o', '.o21o.', '.oooo.'])
    big_leaf(img, R0 + 6, 104, 'amber', 'oak')
    big_leaf(img, R0 + 24, 113, 'rust', 'maple')
    big_leaf(img, R0 + 11, 126, 'gold', 'maple')
    leaf(img, R0 + 28, 133, 'sage', 'nw')
    planter(img, R0 + 4, 148, 32, seed)
    compost_bin(img, R0 + 3, 180, 34, 49, seed)

    # ---- bottom strip: a trailing vine between the corner brackets ------
    pts = P.twine(img, 10, 233, a.w - 11, 233, sag=0, colour='sage_1', knot='sage_0')
    for k, (vx, vy) in enumerate(pts):
        if k % 23 == 7:
            leaf(img, vx, vy - 3, 'sage' if k % 2 else 'amber', 'ne' if k % 3 else 'nw', small=True)
    # top strip: a sprig either side of the ribbon tails
    leaf(img, a.w // 2 - 32, 2, 'sage', 'nw', small=True)
    leaf(img, a.w // 2 + 28, 2, 'amber', 'ne', small=True)
    return img


# ---------------------------------------------------------------------------
# ENDER_CHEST: indigo-dark wood and soft purple lantern light
# ---------------------------------------------------------------------------

ENDER_SEED = 23
# indigo board: recolour the shared base frame's dark brown body to plum
ENDER_BOARD = {INK[1]: PLUM[0], PLUM[0]: INK[0], WOOD[1]: PLUM[1]}


def paint_ender_background():
    key = 'ender_chest'
    s = geo.skin(key)
    img = C.base_background(key, seed=ENDER_SEED, wells='none')
    tband, iband = C.bands(key)
    holes = P.merge_holes(s.content_slots) + P.merge_holes(s.player_slots)
    P.stitched_well(img, holes, thread='plum_2', protect=[tband.tuple(), iband.tuple()])
    # a small star pinned at the right end of the inventory band
    spr(img, iband.right - 12, iband.y + 1, ['..s..', '.sts.', 'stzts', '.sts.', '..s..'])
    spr(img, iband.right - 20, iband.y + 3, ['.x.', 'xzx', '.x.'])
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    return img


def paint_ender_frame():
    key = 'ender_chest'
    s = geo.skin(key)
    a = s.layer()
    seed = ENDER_SEED
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp, H = a.left_panel, a.right_panel, a.h
    L0, R0 = lp.x, rp.x
    c = a.container
    # indigo board: recolour board pixels (not the rim or the cast shadow)
    px = img.load()
    for y in range(2, H - 2):
        for x in range(2, a.w - 2):
            p = px[x, y]
            if p[3] and not c.contains(x, y) and tuple(p[:3]) in ENDER_BOARD:
                if c.right <= x <= c.right + 1 and c.y < y <= c.bottom + 1:
                    continue                      # keep the cast shadow
                if c.y <= y <= c.bottom + 1 and c.x <= x <= c.right + 1 and y >= c.bottom:
                    continue
                px[x, y] = ENDER_BOARD[tuple(p[:3])] + (255,)
    # light pools first, objects on top
    ender_glow(img, L0 + 20, 22, 17)
    ender_glow(img, R0 + 20, 86, 16)

    # ---- left panel: lantern, tag, shelf of books, eye charm, strongbox ----
    P.rope(img, L0 + 4, 12, L0 + 35, 12, sag=2, light='plum_2', dark='plum_1')
    P.tack(img, L0 + 4, 11); P.tack(img, L0 + 35, 11)
    P.vline(img, L0 + 19, 13, 16, INK[0])
    P.lantern(img, L0 + 16, 17, BRASS, PLUM)
    C.side_tag(img, lp, a.left_heading or a.heading, 34, seed, twine_from=(L0 + 20, 26))
    shelf(img, L0 + 4, 72, 32, seed)
    spr(img, L0 + 6, 59, BOOKS_UP)
    spr(img, L0 + 24, 60, HOURGLASS)
    P.tack(img, L0 + 20, 88)
    P.vline(img, L0 + 20, 90, 95, PARCHMENT[1])
    spr(img, L0 + 15, 96, EYE_CHARM)
    for (sx, sy, big) in ((L0 + 6, 110, True), (L0 + 30, 116, False), (L0 + 24, 126, True)):
        spr(img, sx, sy, STAR5 if big else STAR3)
    shelf(img, L0 + 4, 148, 32, seed + 2)
    spr(img, L0 + 6, 137, CHEST)
    spr(img, L0 + 25, 137, POTION)
    for (sx, sy, big) in ((L0 + 9, 160, False), (L0 + 27, 164, True)):
        spr(img, sx, sy, STAR5 if big else STAR3)

    # ---- right panel: moon, star garland, crystal ball, candle and potions ----
    P.tack(img, R0 + 20, 9)
    P.vline(img, R0 + 20, 10, 15, PARCHMENT[1])
    spr(img, R0 + 15, 16, MOON)
    P.twine(img, R0 + 3, 40, R0 + 36, 40, sag=4)
    P.tack(img, R0 + 3, 39); P.tack(img, R0 + 36, 39)
    for k, (tx, drop) in enumerate(((R0 + 9, 4), (R0 + 19, 9), (R0 + 29, 5))):
        top = 42 + (3 if k == 1 else 1)
        P.vline(img, tx, top, top + drop, PARCHMENT[0])
        spr(img, tx - 2, top + drop + 1, STAR5)
    shelf(img, R0 + 4, 98, 32, seed + 1)
    spr(img, R0 + 15, 85, CRYSTAL)
    spr(img, R0 + 5, 90, POTION_SKY)
    spr(img, R0 + 29, 87, POTION)
    shelf(img, R0 + 4, 140, 32, seed + 3)
    spr(img, R0 + 7, 128, JAR_CANDLE)
    spr(img, R0 + 19, 127, BOOKS_UP)
    for (sx, sy, big) in ((R0 + 31, 72, False), (R0 + 5, 112, True), (R0 + 29, 118, False),
                          (R0 + 10, 156, True), (R0 + 28, 162, False)):
        spr(img, sx, sy, STAR5 if big else STAR3)

    # ---- bottom strip: rope between tacks ----
    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0, light='plum_2', dark='plum_1')
    P.tack(img, 10, H - 5); P.tack(img, a.w - 11, H - 5)
    return img


# ---------------------------------------------------------------------------
# CRAFTING: workbench and tool loop
# ---------------------------------------------------------------------------

CRAFT_SEED = 17


def tool_strap(img, x, y, w, tools):
    """Leather strap nailed to the bench back with loops holding tools upright.
    ``tools`` lists (dx, rows, dy): sprite top-left relative to (x, y)."""
    for dx, rows, dy in tools:
        spr(img, x + dx, y + dy, rows)
    P.ink_outline(img, (x, y, w, 5), 'ink_1', radius=1, heavy='b', fill_colour=WOOD[1])
    P.hline(img, x + 1, x + w - 2, y + 1, WOOD[2])
    P.hline(img, x + 1, x + w - 2, y + 3, WOOD[0])
    P.stitch_line(img, x + 2, y + 2, x + w - 3, y + 2, 'parch_1', 1, 1)
    for dx, rows, dy in tools:                      # each loop bulges over its tool
        tw = max(len(r) for r in rows)
        P.hline(img, x + dx, x + dx + tw - 1, y + 1, WOOD[3])
        P.put(img, x + dx - 1, y + 1, INK[1]); P.put(img, x + dx + tw, y + 1, INK[1])
    P.tack(img, x + 1, y + 1, small=True)
    P.tack(img, x + w - 2, y + 1, small=True)


def paint_crafting_background():
    key = 'crafting'
    s = geo.skin(key)
    img = C.base_background(key, seed=CRAFT_SEED, wells='wood')

    # warm light first: a candle stub on the bench, top-left corner
    P.lantern_glow_ring(img, 12, 22, 8, strength=1)
    icons.draw_motif(img, 'candle', 9, 17)
    spr(img, 17, 25, SHAVING_A)

    # carpenter's pencil resting on the title sheet, left of the live title (x < 29)
    spr(img, 8, 7, PENCIL)

    # below the recipe toggle: a tin of nails and a loose nail
    for nx, ny in ((5, 57), (8, 56), (11, 58)):
        spr(img, nx, ny, NAIL)
    icons.draw_motif(img, 'crate', 3, 60)
    spr(img, 14, 63, TWINE_BALL)

    # above the arrow: a mallet resting on the bench with curled shavings
    mallet(img, 89, 17, CRAFT_SEED)
    spr(img, 113, 18, SHAVING_A)
    spr(img, 112, 23, SHAVING_B)

    # above the result: try square hung on a nail
    P.tack(img, 124, 16, small=True)
    spr(img, 122, 17, TRY_SQUARE)

    # right column, the tool loop: a rope between two pegs with the hammer
    # hanging from it, and a leather strap holding a chisel, an awl and a gouge
    P.rope(img, 147, 18, 172, 18, sag=2)
    P.tack(img, 147, 17); P.tack(img, 172, 17)
    P.vline(img, 151, 20, 21, PARCHMENT[1])
    hammer(img, 146, 22, handle=22)
    tool_strap(img, 158, 38, 16, [(1, CHISEL, -11), (6, AWL, -7), (11, GOUGE, -9)])
    # oil can and shavings at the foot of the column
    spr(img, 160, 57, OIL_CAN)
    spr(img, 148, 64, SHAVING_B)
    spr(img, 152, 60, SHAVING_A)

    # under the arrow and result: the saw hung flat on two pegs
    saw(img, 90, 61, 40)
    P.tack(img, 100, 58, small=True)
    P.tack(img, 120, 58, small=True)

    # brass tacks at the bottom corners
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    return img


# ---------------------------------------------------------------------------

def paint(key, root=None):
    written = []
    if key == 'trashcan':
        written.append(save_background(paint_trashcan_background(), key, root))
        written.append(save_frame(paint_trashcan_frame(), key, 'menu_frame', root))
    elif key == 'ender_chest':
        written.append(save_background(paint_ender_background(), key, root))
        written.append(save_frame(paint_ender_frame(), key, 'menu_frame', root))
    elif key == 'crafting':
        written.append(save_background(paint_crafting_background(), key, root))
    else:
        raise SystemExit(f'paint_utility does not own skin {key!r}; owns {", ".join(SKINS)}')
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', type=Path, help='textures/-shaped output root (default: pack-source textures)')
    a = ap.parse_args(argv)
    for key in a.skin or SKINS:
        for p in paint(key, a.out_root):
            print('WROTE', p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
