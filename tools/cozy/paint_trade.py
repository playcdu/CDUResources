#!/usr/bin/env python3
"""Cozy painter "trade": the player-to-player trade table and its money dial.

    python tools/cozy/paint_trade.py                      # all five skins -> pack-source
    python tools/cozy/paint_trade.py --skin trade_idle    # one skin
    python tools/cozy/paint_trade.py --out-root DIR       # write a pack-source-shaped tree elsewhere

Skins: trade_idle, trade_self_ready, trade_other_ready, trade_both_ready
(chest_6 with outer frame) and trade_money (dispenser, no frame).

Family identity (trade: accent sky, secondary ember): two mugs on a shared
table and a handshake rope knot. YOUR side is sky blue, THEIR side ember.

The centre column of the offer grid (cells 4, 13, 22, 31, 40, x 80..95) is a
dark table-edge post. It carries two independent, noninteractive readiness
marks (icons only, no words):

* upper half = YOU, lower half = THEM. Each half has a saucer on a little
  ledge and a linen pennant that points at that party's offer (left for you,
  right for them) and holds that party's end of the handshake rope.
* ready:     the pennant carries a sage check, a steaming mug stands on the
             saucer, lantern light pools on the post, and the rope end
             reaches the middle with an open loop, offered for tying.
* not ready: the pennant carries an ash dash, the saucer is empty, the post
             stays dark, and the rope end is held back, whipped and fraying.
* only when both are ready are the two ends tied in a bow - the knot.

The outer frame repeats the story: your lantern (left) and their lantern
(right) are lit only when that party is ready, and each side's mug on the
shared table steams only then. Everything is deterministic (fixed seeds).

Licence: MIT (code); the pixel designs are CC0-1.0.
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
from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD  # noqa: E402

CHEST_SKINS = ('trade_idle', 'trade_self_ready', 'trade_other_ready', 'trade_both_ready')
MONEY_SKIN = 'trade_money'
SKINS = CHEST_SKINS + (MONEY_SKIN,)
# (you ready, they ready) per readiness skin
READINESS = {
    'trade_idle': (False, False),
    'trade_self_ready': (True, False),
    'trade_other_ready': (False, True),
    'trade_both_ready': (True, True),
}
SEED = 23
POST = [INK[1], WOOD[0], WOOD[1], WOOD[2], WOOD[3]]       # dark table-edge wood
HEMP = {'o': INK[1], 'O': INK[0], '3': PARCHMENT[3], '2': PARCHMENT[2], '1': PARCHMENT[1], '0': PARCHMENT[0]}

PACK_SOURCE = geo.ROOT / 'pack-source'


# ---------------------------------------------------------------------------
# Output paths (pack-source or a pack-source-shaped --out-root)
# ---------------------------------------------------------------------------

def _out(path, out_root):
    if out_root is None:
        return path
    rel = Path(path).resolve().relative_to(PACK_SOURCE.resolve())
    return Path(out_root) / rel


# ---------------------------------------------------------------------------
# Hand-authored sprites
# ---------------------------------------------------------------------------

# Linen pennant pointing LEFT (14 x 9); flipped for THEM.
PENNANT = [
    '...ooooooooooo',
    '..o33333333aao',
    '.o322222222aao',
    'o3222222222AAo',
    'o2222222222AAo',
    'o1222222222AAO',
    '.o12222222211O',
    '..o1111111111O',
    '...OOOOOOOOOOO',
]
# bold check (sage) and a flat dash (ash) pressed onto the pennant
CHECK = ['.....s', '....sS', 's..sS.', 'SssS..', '.SS...']
DASH = ['ddddd', 'DDDDD']

SAUCER = [
    '.oooooooooooo.',
    'o333333333332o',
    '.o1111111110o.',
    '..oooooooooo..',
]

# The knot section of the divider (14 x 21, rows 51..71). The upper rope end
# belongs to you, the lower one to them; both are tied to their pennants.
ROPE_A, ROPE_B = '.....o32o.....', '.....o21o.....'
# both ready: the two ends tied in a bow - the handshake knot
KNOT_TIED = [
    ROPE_A, ROPE_B, ROPE_A, ROPE_B,
    '.oo..o32o..oo.',
    'o32ooo21ooo21o',
    'o3..2o32o2..1o',
    'o2..o3221o..1o',
    'o2..o2210o..0o',
    'o21.o1100o.10o',
    '.oo.oo10oo.oo.',
    '....oo21o.....',
    '...o3o32o.....',
    '..o2oo21o.....',
    '..oo.o32o.....',
    ROPE_B, ROPE_A, ROPE_B, ROPE_A, ROPE_B, ROPE_A,
]
# a rope end offered to the middle (that party is ready): an open eye loop
LOOP_DOWN = ['.o21o.', 'o3oo1o', 'o2..1o', 'o2..0o', '.o10o.', '..oo..']
LOOP_UP = ['..oo..', '.o32o.', 'o3..1o', 'o2..0o', 'o2oo0o', '.o21o.']
# a rope end held back (not ready): whipped with ink thread, strands loose
FRAY_DOWN = ['OOOO', '3.2.', '2..1', '.2..']
FRAY_UP = ['..2.', '3..1', '.3.2', 'OOOO']

# the money screen's leather coin purse (15 x 16), drawstring tied at the neck
PURSE_BIG = [
    '.....o...o.....',
    '......o.o......',
    '.....otTto.....',
    '....o1tTt1o....',
    '.....o121o.....',
    '....o23332o....',
    '...o2344332o...',
    '..o234443332o..',
    '.o23444333322o.',
    '.o23443333322o.',
    'o2334333333221o',
    'o2333333332221o',
    'o2233333322211o',
    '.o22222222111o.',
    '..o111111111o..',
    '...ooooooooo...',
]
K_PURSE_BIG = {'o': INK[1], 't': PARCHMENT[1], 'T': PARCHMENT[3], '1': WOOD[1], '2': WOOD[2], '3': WOOD[3],
               '4': WOOD[4]}

# side-view coin stack piece (one coin, 7 x 2) and a coin top (icons.COIN)
COIN_SIDE = ['o33221o', 'o10000o']

# lit and unlit lantern glass
GLASS_LIT = EMBER
GLASS_COLD = [SKY[0], SKY[0], ASH[0]]


def sprite(img, x, y, rows, key, flip_x=False):
    w = max(len(r) for r in rows)
    for r in rows:
        assert len(r) == w, (rows, r)
    P.sprite(img, x, y, rows, key, flip_x=flip_x)


# ---------------------------------------------------------------------------
# Small drawing helpers (local to this painter)
# ---------------------------------------------------------------------------

def check_mark(img, x, y, dark=SAGE[0], light=SAGE[1]):
    sprite(img, x, y, CHECK, {'s': light, 'S': dark})


def dash_mark(img, x, y):
    sprite(img, x, y, DASH, {'d': ASH[1], 'D': ASH[0]})


def pennant(img, x, y, facing, ready, accent):
    """Readiness pennant: 14 x 9 linen arrow-tag pointing ``facing`` ('l'/'r')
    with a dyed hem in ``accent`` at the tied end and a check or dash."""
    key = {'o': INK[1], 'O': INK[0], '3': PARCHMENT[3], '2': PARCHMENT[2], '1': PARCHMENT[1],
           'a': accent[2], 'A': accent[1]}
    sprite(img, x, y, PENNANT, key, flip_x=(facing == 'r'))
    # brass tack through the dyed hem
    tx = x + 11 if facing == 'l' else x + 2
    P.put(img, tx, y + 3, BRASS[3]); P.put(img, tx, y + 4, BRASS[0])
    mx = x + 3 if facing == 'l' else x + 5
    if ready:
        check_mark(img, mx, y + 2)
    else:
        dash_mark(img, mx, y + 4)


def saucer(img, x, y):
    sprite(img, x, y, SAUCER, {'o': INK[1], '3': PARCHMENT[3], '2': PARCHMENT[1], '1': PARCHMENT[0],
                               '0': INK[2]})


def ledge(img, x, y, w):
    """A short oak ledge (3 rows) the saucer rests on, with bracket pegs."""
    P.hline(img, x, x + w - 1, y, INK[1])
    P.hline(img, x, x + w - 1, y + 1, WOOD[3])
    P.put(img, x, y + 1, WOOD[4]); P.put(img, x + 1, y + 1, WOOD[4])
    P.hline(img, x, x + w - 1, y + 2, WOOD[1])
    P.hline(img, x, x + w - 1, y + 3, INK[0])
    P.put(img, x + 2, y + 4, INK[1]); P.put(img, x + w - 3, y + 4, INK[1])


def big_mug(img, x, y, ramp, facing='r', steam=True, seed=0, full=True):
    """A 14 x 12 glazed mug (body 10 wide, handle 4) seen slightly from above:
    cream rim, coffee surface, a pale band round the belly. ``facing`` is the
    side the handle is on."""
    bx = x if facing == 'r' else x + 4
    hx = bx + 10 if facing == 'r' else x
    # body
    P.ink_outline(img, (bx, y + 1, 10, 11), 'ink_1', radius=1, heavy='br', fill_colour=ramp[1])
    P.vline(img, bx + 1, y + 3, y + 9, ramp[2])
    P.vline(img, bx + 2, y + 4, y + 6, ramp[2])
    P.vline(img, bx + 8, y + 3, y + 10, ramp[0])
    P.hline(img, bx + 2, bx + 8, y + 10, ramp[0])
    # band
    P.hline(img, bx + 1, bx + 8, y + 7, PARCHMENT[2])
    P.put(img, bx + 8, y + 7, PARCHMENT[0])
    P.put(img, bx + 1, y + 7, PARCHMENT[3])
    # rim and contents
    P.hline(img, bx + 1, bx + 8, y + 1, INK[1])
    P.hline(img, bx + 1, bx + 8, y + 2, PARCHMENT[3])
    P.hline(img, bx + 2, bx + 7, y + 3, WOOD[0] if full else ramp[0])
    P.put(img, bx + 3, y + 3, WOOD[1] if full else ramp[0])
    # handle
    rows = ['ooo.', 'o22o', '.o.o', '.o.o', 'o11o', 'ooo.']
    sprite(img, hx, y + 3, rows, {'o': INK[1], '2': ramp[2], '1': ramp[0]}, flip_x=(facing == 'l'))
    if steam:
        r = P._rng(seed, 'mugsteam')
        sx = bx + 2 + r.randint(0, 1)
        sprite(img, sx, y - 5, ['.s..s.', 's..s..', '.s..s.', '..s..s', '.s....'], {'s': ASH[2]})


def coin_stack(img, x, y, n):
    """``n`` coins seen side-on, bottom coin at row y (stack grows upward),
    with a coin top on the uppermost."""
    for k in range(n):
        sprite(img, x, y - 2 * k, COIN_SIDE, {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[1],
                                              '0': BRASS[0]})
    P.hline(img, x + 1, x + 5, y - 2 * n + 1, INK[1])
    if n:
        P.hline(img, x + 2, x + 4, y - 2 * n + 2, BRASS[3])


def lantern(img, x, y, lit):
    P.lantern(img, x, y, BRASS, GLASS_LIT if lit else GLASS_COLD)
    if not lit:
        # a cold wick instead of a flame
        P.put(img, x + 3, y + 5, ASH[1]); P.put(img, x + 4, y + 4, INK[1])


# ---------------------------------------------------------------------------
# Readiness divider (background, chest skins)
# ---------------------------------------------------------------------------

DIV_X0, DIV_X1 = 80, 95          # divider column between the two clearance grids
DIV_Y0, DIV_Y1 = 15, 107
ROPE_X = 86                       # left ink column of the 4 px rope (x 86..89)


ROPE_TWIST = ('o32o', 'o13o', 'o21o')   # strands climb diagonally: a laid rope


def rope_column(img, y0, y1):
    """Straight hemp rope segment in the divider's rope columns."""
    for y in range(y0, y1 + 1):
        sprite(img, ROPE_X, y, [ROPE_TWIST[y % 3]], HEMP)


def knot_section(img, y, you, them):
    """Rows y .. y+20: tied bow when both are ready; otherwise each party's rope
    end either reaches the middle with an open loop (ready) or is held back,
    whipped and fraying (not ready)."""
    if you and them:
        sprite(img, ROPE_X - 5, y, KNOT_TIED, HEMP)
        rope_column(img, y, y + 3)
        rope_column(img, y + 15, y + 20)
        return
    if you:
        rope_column(img, y, y + 7)
        sprite(img, ROPE_X - 1, y + 8, LOOP_DOWN, HEMP)
    else:
        rope_column(img, y, y + 2)
        sprite(img, ROPE_X, y + 3, FRAY_DOWN, HEMP)
    if them:
        rope_column(img, y + 13, y + 20)
        sprite(img, ROPE_X - 1, y + 7, LOOP_UP, HEMP)
    else:
        rope_column(img, y + 18, y + 20)
        sprite(img, ROPE_X, y + 14, FRAY_UP, HEMP)


def paint_divider(img, you, them, seed):
    x0, x1, y0, y1 = DIV_X0, DIV_X1, DIV_Y0, DIV_Y1
    # the post: dark table-edge wood running down between the two offers
    P.fill(img, (x0, y0, x1 - x0 + 1, y1 - y0 + 1), POST[2])
    P._grain(img, (x0 + 2, y0 + 1, x1 - x0 - 3, y1 - y0 - 1), POST, (seed, 'post'), 0.8, True)
    P.vline(img, x0, y0, y1, INK[1])                 # well lips stay crisp
    P.vline(img, x1, y0, y1, INK[1])
    P.highlight_edge(img, (x0 + 1, y0, 1, y1 - y0 + 1), POST[3], 'l', broken=4, seed=seed)
    P.vline(img, x0 + 1, y0 + 1, y0 + 3, POST[3])
    P.vline(img, x1 - 1, y0 + 1, y1, POST[0])        # shadow wall next to their wells
    P.hline(img, x0, x1, y0, INK[1])
    P.hline(img, x0, x1, y1, INK[0])

    you_mug_y, them_mug_y = 21, 88                  # mug top rows (steam above)
    # lantern light pools round a ready party's mug (dither falloff, no gradient)
    if you:
        P.lantern_glow_ring(img, 87, you_mug_y + 6, 13, strength=1)
    if them:
        P.lantern_glow_ring(img, 88, them_mug_y + 6, 13, strength=1)

    # YOU (upper): mug or empty saucer on a ledge, pennant pointing at your offer
    if you:
        big_mug(img, 81, you_mug_y, SKY, 'r', steam=True, seed=seed)
    saucer(img, 81, you_mug_y + 11)
    ledge(img, 81, you_mug_y + 15, 14)
    pennant(img, 81, 42, 'l', you, SKY)
    # the handshake knot between the two pennants
    knot_section(img, 51, you, them)
    # THEM (lower): pennant pointing at their offer, then mug or empty saucer
    pennant(img, 81, 72, 'r', them, EMBER)
    if them:
        big_mug(img, 81, them_mug_y, EMBER, 'l', steam=True, seed=seed + 2)
    saucer(img, 81, them_mug_y + 11)
    ledge(img, 81, them_mug_y + 15, 14)


def paint_chest_background(key):
    you, them = READINESS[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=SEED)
    paint_divider(img, you, them, SEED)
    tband, iband = C.bands(key)
    # light paper touches only: a twine with a tiny hemp knot at the far right
    # of the inventory band, clear of the live "Inventory" label at the left
    yy = iband.y + 4
    P.twine(img, iband.right - 30, yy - 1, iband.right - 8, yy - 1, sag=1)
    sprite(img, iband.right - 21, yy - 3, ['.0.', '010', '.0.'], {'0': PARCHMENT[0], '1': PARCHMENT[1]})
    # warm wear at the lower corners of the sheet and two brass tacks
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    P.dither_patch(img, (1, s.height - 6, 4, 4), WOOD[1], 0.25)
    P.dither_patch(img, (s.width - 5, 120, 4, 5), WOOD[1], 0.25)
    geo.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Buttons (chest skins)
# ---------------------------------------------------------------------------

def paint_own_money(key):
    b = geo.skin(key).button('own_money')
    img = C.paint_button(key, 'own_money', seed=SEED)
    # your colour: a sky-dyed hem at the tag's tail and sky thread at the eyelet
    x, y, w, h = b.body.tuple()
    P.vline(img, x + w - 4, y + 3, y + h - 4, SKY[2])
    P.vline(img, x + w - 3, y + 3, y + h - 4, SKY[1])
    P.put(img, x + 2, y + h // 2 - 1, SKY[1]); P.put(img, x + 1, y + h // 2, SKY[1])
    geo.finish_button(img, key, 'own_money')
    return C.button_states(img, key, 'own_money')


def _plaque(img, b, seed):
    """Read-only plaque: a parchment card tacked flat to the board at both
    ends - no eyelet, no stitch - so it reads as information, not a tag."""
    x, y, w, h = b.body.tuple()
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', radius=1, fibres=False)
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=1, heavy='br')
    P.hline(img, x + 3, x + w - 4, y + 2, PARCHMENT[1])        # recessed inner rule
    P.hline(img, x + 3, x + w - 4, y + h - 3, PARCHMENT[3])
    P.vline(img, x + 2, y + 2, y + h - 3, PARCHMENT[1])
    P.vline(img, x + w - 3, y + 2, y + h - 3, PARCHMENT[3])
    P.tack(img, x + 4, y + h // 2 - 1)
    return (x + 7, y + 2, w - 14, h - 3)


def paint_other_money(key):
    b = geo.skin(key).button('other_money')
    img = C.new(b.w, b.h)
    box = _plaque(img, b, SEED)
    C.letter(img, b, box, 'ink_0')
    x, y, w, h = b.body.tuple()
    rest = img.copy()
    P.tack(rest, x + w - 5, y + h // 2 - 1)                       # normal: tacked
    # confirmed (their side is ready): a small sage wax seal pressed with a check
    conf = img.copy()
    sx, sy = x + w - 9, y + h // 2 - 3
    sprite(conf, sx, sy, ['.oooo.', 'o2221o', 'o2ss1o', 'o2s11O', 'o111OO', '.OOOO.'],
           {'o': INK[1], 'O': INK[0], '2': SAGE[2], '1': SAGE[1], 's': SAGE[0]})
    P.put(conf, sx + 4, sy + 1, PARCHMENT[3])
    for im in (rest, conf):
        geo.finish_button(im, key, 'other_money')
    selected = geo.finish_button(P.make_selected(conf), key, 'other_money')
    return C.button_states(rest, key, 'other_money', overrides={'selected': selected})


def paint_ready(key):
    b = geo.skin(key).button('ready')
    img = C.paint_button(key, 'ready', seed=SEED)
    x, y, w, h = b.body.tuple()
    cy = y + h // 2 - 1
    # engraved rope-knot pips at the left of the plate
    for (dx, dy) in ((8, 0), (9, -1), (9, 1), (10, 0)):
        P.put(img, x + dx, cy + dy, BRASS[0])
    P.put(img, x + 11, cy + 1, BRASS[3])
    # at rest: an empty engraved ring at the right (nothing confirmed yet)
    ring = ['.000.', '0...0', '0...0', '0...0', '.000.']
    rest = img.copy()
    sprite(rest, x + w - 12, cy - 2, ring, {'0': BRASS[0]})
    P.put(rest, x + w - 11, cy + 3, BRASS[3]); P.put(rest, x + w - 9, cy + 3, BRASS[3])
    # confirmed: the ring holds an inked check
    conf = rest.copy()
    sprite(conf, x + w - 12, cy - 3, ['.....O', '....O.', 'O..O..', '.OO...', '......'], {'O': INK[0]})
    for im in (rest, conf):
        geo.finish_button(im, key, 'ready')
    selected = geo.finish_button(P.make_selected(conf), key, 'ready')
    return C.button_states(rest, key, 'ready', overrides={'selected': selected})


# ---------------------------------------------------------------------------
# Outer frame (chest skins)
# ---------------------------------------------------------------------------

def note_card(img, x, y, w, h, seed, lines=(), curl=True):
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=True)
    if curl:
        P.page_curl(img, (x, y, w, h), 'br', 4, behind=WOOD[0])
    P.tack(img, x + w // 2, y + 1)
    ty = y + 5
    for t in lines:
        L.draw_text_centered(img, x + (w + 1) // 2, ty, t, 'ink_0', face='sprig')
        ty += 7
    return ty


def shelf(img, x, y, w, seed):
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def table_top(img, x, y, w, seed, legs=True, open_side=None):
    """The shared table: a thick oak top (8 rows, lit front edge), a dark apron
    and, when ``legs``, two turned legs down to ``y + 17``. ``open_side`` ('l'
    or 'r') runs the top off that edge, as if it continues under the sheet."""
    P.plank(img, (x, y, w, 8), WOOD, seed, 'ink_1', radius=1, grain=0.6)
    P.hline(img, x + 1, x + w - 2, y + 1, WOOD[4])
    P.hline(img, x + 1, x + w - 2, y + 5, WOOD[1])
    P.fill(img, (x + 2, y + 8, w - 4, 3), WOOD[0])
    P.hline(img, x + 2, x + w - 3, y + 8, INK[1])
    if open_side:
        ex = x if open_side == 'l' else x + w - 1
        P.vline(img, ex, y + 1, y + 6, WOOD[2])
    if legs:
        for lx in (x + 3, x + w - 7):
            P.ink_outline(img, (lx, y + 10, 4, 8), 'ink_1', radius=0, heavy='r', fill_colour=WOOD[1])
            P.vline(img, lx + 1, y + 11, y + 16, WOOD[3])
            P.hline(img, lx, lx + 3, y + 13, INK[1])


def rope_coil(img, cx, cy, rx, ry, seed=0):
    """A coil of hemp rope hung on a peg: concentric laid-rope rings around an
    open middle (the board shows through), lit top-left, a frayed tail."""
    import math
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            dx, dy = x - cx, y - cy
            n = 0
            for j in range(6):
                ax, ay = rx - j, ry - j
                if ax <= 0 or ay <= 0:
                    break
                if (dx / ax) ** 2 + (dy / ay) ** 2 <= 1.0:
                    n += 1
            if n == 0 or n >= 6:
                continue
            if n in (1, 3, 5):
                P.put(img, x, y, INK[1] if (dx < 0 or dy < 0) else INK[0])
                continue
            ang = math.atan2(dy, dx)
            stripe = int((ang + math.pi) / (2 * math.pi) * 22 + n) % 3
            lit = dx + dy < 0
            if stripe == 0:
                col = PARCHMENT[3] if lit else PARCHMENT[2]
            elif stripe == 1:
                col = PARCHMENT[2] if lit else PARCHMENT[1]
            else:
                col = PARCHMENT[1] if lit else PARCHMENT[0]
            P.put(img, x, y, col)
    # the peg it hangs from
    sprite(img, cx - 1, cy - ry - 2, ['oo', '32', '10'],
           {'o': INK[1], '3': WOOD[4], '2': WOOD[3], '1': WOOD[1], '0': WOOD[0]})
    # a tail hanging from the lower right, whipped and fraying
    tx, ty = cx + rx // 2, cy + ry - 1
    for k in range(7):
        sprite(img, tx + (1 if k > 3 else 0), ty + k, [ROPE_TWIST[k % 3]], HEMP)
    sprite(img, tx + 1, ty + 7, FRAY_DOWN, HEMP)


def scroll(img, x, y, w, seed=0, ribbon=SKY):
    """A rolled agreement: parchment between two rolled ends, tied with a
    ribbon and closed with a small wax seal (ruled lines, no writing)."""
    P.parchment_panel(img, (x + 3, y + 1, w - 6, 8), seed, outline='ink_1', fibres=False)
    for k in range(3):
        P.stitch_line(img, x + 6, y + 3 + 2 * k, x + w - 8 - 3 * (k == 2), y + 3 + 2 * k,
                      PARCHMENT[0], 3, 1, phase=k)
    roll = ['.oo.', 'o32o', 'o21o', 'o21o', 'o21o', 'o21o', 'o10o', 'o10o', 'o10o', '.oo.']
    key = {'o': INK[1], '3': PARCHMENT[3], '2': PARCHMENT[2], '1': PARCHMENT[1], '0': PARCHMENT[0]}
    sprite(img, x, y, roll, key)
    sprite(img, x + w - 4, y, roll, key)
    mx = x + w // 2
    P.vline(img, mx - 1, y + 1, y + 8, ribbon[1])
    P.vline(img, mx, y + 1, y + 8, ribbon[2])
    P.vline(img, mx + 1, y + 1, y + 8, ribbon[0])
    P.wax_seal(img, mx, y + 5, 4, BERRY, seed, drip=False)
    sprite(img, mx - 2, y + 10, ['o1.1o', 'o1.0o', '.o.o.'], {'o': INK[1], '1': ribbon[1], '0': ribbon[0]})


def tag_string(img, x0, x1, y, accent, seed, n=3):
    P.twine(img, x0, y, x1, y, sag=4)
    step = (x1 - x0) // n
    for k in range(n):
        tx = x0 + 2 + k * step
        ty = y + 3 + (2 if k == 1 else 0)
        P.vline(img, tx + 3, ty - 1, ty + 1, PARCHMENT[0])
        P.linen_tag(img, (tx, ty + 2, 7, 11), eyelet=None, seed=seed + k)
        P.put(img, tx + 3, ty + 4, INK[0])
        P.fill(img, (tx + 1, ty + 9, 5, 2), accent[1])
        P.hline(img, tx + 1, tx + 5, ty + 8, accent[2])


def knot_rope(img, a, tied):
    """The bottom strip: one rope from your side to theirs with the handshake
    knot at the centre of the table edge."""
    H = a.h
    y = H - 4
    cx = a.w // 2
    P.rope(img, 14, y, cx - 6, y, sag=0)
    P.rope(img, cx + 6, y, a.w - 15, y, sag=0)
    P.tack(img, 11, y - 1); P.tack(img, a.w - 12, y - 1)
    # compact horizontal knot (fits the 8 px strip)
    if tied:
        rows = ['..oooooooo..', '.o32o32o32o.', 'o3221o21o210', 'o2110o10o10o', '.oo1ooo1oo..', '...oo..oo...']
    else:
        rows = ['...oo..oo...', '.oo3oo32o...', 'o32o21o21oo.', 'o21o1o10o21o', '.oooo.oo.oo.', '............']
    sprite(img, cx - 6, y - 3, rows, HEMP)


def paint_frame(key):
    you, them = READINESS[key]
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, seed=SEED)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    TABLE_Y = 207

    # ---- left panel: YOUR side (sky) ------------------------------------
    P.rope(img, lp.x + 5, 11, lp.right - 6, 11, sag=2)
    P.vline(img, lp.x + 19, 13, 15, INK[1])
    lantern(img, lp.x + 16, 16, you)
    if you:
        P.lantern_glow_ring(img, lp.x + 19, 21, 13, strength=1)
    C.side_tag(img, lp, a.left_heading or a.heading or '', 34, SEED, twine_from=(lp.x + 20, 25))
    # your offer note: a coin purse sketched on a pinned card, ruled lines
    note_card(img, lp.x + 6, 52, 27, 34, SEED)
    icons.draw_icon(img, 'balance', (lp.x + 6, 56, 27, 15))
    for k in range(3):
        P.stitch_line(img, lp.x + 9, 74 + 3 * k, lp.x + 29 - 4 * (k == 2), 74 + 3 * k, SKY[2], 3, 1, phase=k)
    tag_string(img, lp.x + 3, lp.right - 4, 96, SKY, SEED)
    # the handshake rope coiled on a peg, and a vine trailing down the board
    rope_coil(img, lp.x + 24, 134, 9, 8, SEED)
    for k in range(6):
        yy = 122 + k * 13
        P.ink_line(img, lp.x + 7 - (k % 2), yy, lp.x + 7 - ((k + 1) % 2), yy + 13, SAGE[0])
        P.leaf(img, lp.x + (8 if k % 2 else 1), yy + 3, 'ne' if k % 2 else 'nw', small=k % 3 == 2)
    shelf(img, lp.x + 14, 176, 22, SEED + 3)
    coin_stack(img, lp.x + 17, 174, 3)
    coin_stack(img, lp.x + 25, 174, 2)
    sprite(img, lp.x + 31, 170, icons.COIN, icons.K_COIN)
    # the shared table with your mug and purse
    table_top(img, lp.x + 1, TABLE_Y, lp.w, SEED + 4, open_side='r')
    big_mug(img, lp.x + 19, TABLE_Y - 11, SKY, 'r', steam=you, seed=SEED)
    icons.draw_icon(img, 'balance', (lp.x + 3, TABLE_Y - 13, 13, 13))

    # ---- right panel: THEIR side (ember) -----------------------------------
    P.rope(img, rp.x + 5, 11, rp.right - 6, 11, sag=2)
    P.vline(img, rp.x + 20, 13, 15, INK[1])
    lantern(img, rp.x + 17, 16, them)
    if them:
        P.lantern_glow_ring(img, rp.x + 20, 21, 13, strength=1)
    lines = list(a.right_lines)
    if lines:
        bottom = note_card(img, rp.x + 5, 34, 30, 7 * len(lines) + 9, SEED + 1, lines)
    else:
        bottom = 40
    shelf(img, rp.x + 4, bottom + 22, rp.w - 8, SEED + 5)
    icons.draw_motif(img, 'candle', rp.x + 7, bottom + 11)
    if them:
        P.lantern_glow_ring(img, rp.x + 9, bottom + 13, 8, strength=1)
    icons.draw_motif(img, 'ledger', rp.x + 20, bottom + 12)
    tag_string(img, rp.x + 3, rp.right - 4, bottom + 40, EMBER, SEED + 7)
    # the agreement both sides will seal, rolled and tied
    scroll(img, rp.x + 5, bottom + 68, 28, SEED)
    for k in range(5):
        yy = bottom + 88 + k * 13
        P.ink_line(img, rp.x + 33 - (k % 2), yy, rp.x + 33 - ((k + 1) % 2), yy + 13, SAGE[0])
        P.leaf(img, rp.x + (34 if k % 2 else 27), yy + 3, 'ne' if k % 2 else 'nw', small=k % 3 == 2)
    icons.draw_motif(img, 'crate', rp.x + 5, 176)
    coin_stack(img, rp.x + 17, 184, 2)
    # the shared table with their mug and coins
    table_top(img, rp.x - 1, TABLE_Y, rp.w, SEED + 6, open_side='l')
    big_mug(img, rp.x + 4, TABLE_Y - 11, EMBER, 'l', steam=them, seed=SEED + 1)
    coin_stack(img, rp.x + 22, TABLE_Y - 1, 3)
    coin_stack(img, rp.x + 29, TABLE_Y - 1, 1)

    # ---- bottom strip: the rope and handshake knot along the table edge ----
    knot_rope(img, a, you and them)
    P.highlight_edge(img, (lp.x + 1, 9, lp.w - 2, H - 18), WOOD[2], 'l', broken=4, seed=SEED)
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# trade_money (dispenser)
# ---------------------------------------------------------------------------

def paint_money_background():
    key = MONEY_SKIN
    s = geo.skin(key)
    img = C.base_background(key, seed=SEED + 11)
    tband, iband = C.bands(key)
    # documented dispenser exception: the static label in HEARTH ink_0
    L.draw_text_centered(img, 88, tband.y + 3, 'OFFERED MONEY', 'ink_0')

    # ---- left third: your purse and coin stacks on a little shelf ---------
    lx0, lx1 = 6, 57
    P.rope(img, lx0 + 2, 19, lx1 - 2, 19, sag=2)
    P.tack(img, lx0 + 1, 18); P.tack(img, lx1 - 1, 18)
    P.vline(img, lx0 + 12, 21, 23, INK[1])
    lantern(img, lx0 + 9, 24, True)
    P.lantern_glow_ring(img, lx0 + 12, 29, 10, strength=1)
    shelf(img, lx0 + 3, 55, lx1 - lx0 - 5, SEED)
    sprite(img, lx0 + 19, 39, PURSE_BIG, K_PURSE_BIG)
    coin_stack(img, lx0 + 7, 53, 4)
    coin_stack(img, lx0 + 36, 53, 2)
    sprite(img, lx0 + 43, 49, icons.COIN, icons.K_COIN)
    sprite(img, lx0 + 14, 50, icons.COIN, icons.K_COIN)
    # a sprig trailing off the shelf end
    P.ink_line(img, lx0 + 6, 61, lx0 + 5, 67, SAGE[0])
    P.leaf(img, lx0 + 6, 62, 'ne', small=True)
    P.leaf(img, lx0 + 1, 64, 'nw', small=True)

    # ---- right third: two mugs on the shared table, rope knot between ----
    rx0, rx1 = 118, 169
    note_card(img, rx0 + 4, 18, 22, 24, SEED + 2)
    for k in range(4):
        P.stitch_line(img, rx0 + 7, 24 + 4 * k, rx0 + 22 - 3 * (k == 3), 24 + 4 * k, SKY[2], 3, 1, phase=k)
    P.wax_seal(img, rx0 + 21, 37, 4, BERRY, SEED, drip=True)
    # yours and theirs: two dyed linen tags on a twine
    P.tack(img, rx0 + 29, 19); P.tack(img, rx1 - 2, 19)
    P.twine(img, rx0 + 29, 20, rx1 - 2, 20, sag=3)
    for k, (tx, accent) in enumerate(((rx0 + 31, SKY), (rx0 + 41, EMBER))):
        ty = 22 + k
        P.vline(img, tx + 3, ty, ty + 1, PARCHMENT[0])
        P.linen_tag(img, (tx, ty + 2, 7, 11), eyelet=None, seed=SEED + k)
        P.put(img, tx + 3, ty + 4, INK[0])
        P.fill(img, (tx + 1, ty + 9, 5, 2), accent[1])
        P.hline(img, tx + 1, tx + 5, ty + 8, accent[2])
    table_top(img, rx0 + 1, 58, rx1 - rx0 - 1, SEED + 3)
    big_mug(img, rx0 + 4, 46, SKY, 'r', steam=True, seed=SEED)
    big_mug(img, rx1 - 18, 46, EMBER, 'l', steam=True, seed=SEED + 1)
    # a hemp rope looped between the two handles, knotted in the middle
    P.twine(img, rx0 + 18, 51, rx1 - 18, 51, sag=2, colour='parch_2', knot='parch_0')
    sprite(img, (rx0 + rx1) // 2 - 2, 51, ['.oo.', 'o32o', 'o21o', '.oo.'], HEMP)

    # wear at the corners
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    geo.finish_background(img, key)
    return img


def paint_money_buttons():
    key = MONEY_SKIN
    out = {}
    for bid in ('increase', 'return', 'decrease'):
        b = geo.skin(key).button(bid)
        img = C.paint_button(key, bid, seed=SEED + 31)
        x, y, w, h = b.body.tuple()
        if b.style == 'primary':
            # scuffs on the oiled rim, like a well-used dial lever
            P.put(img, x + 6, y + 1, WOOD[1]); P.put(img, x + 7, y + 1, WOOD[1])
            P.put(img, x + w - 9, y + h - 2, WOOD[3])
        geo.finish_button(img, key, bid)
        out[bid] = C.button_states(img, key, bid)
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def save_states(states, key, button_id, out_root):
    s = geo.skin(key)
    for st, im in states.items():
        C.save_png(im, _out(s.button_path(button_id, st), out_root))


def paint_skin(key, out_root=None):
    s = geo.skin(key)
    written = []
    if key == MONEY_SKIN:
        bg = paint_money_background()
        written.append(C.save_png(bg, _out(s.background_path, out_root)))
        for bid, states in paint_money_buttons().items():
            save_states(states, key, bid, out_root)
            written += [bid] * 6
        return written
    bg = paint_chest_background(key)
    written.append(C.save_png(bg, _out(s.background_path, out_root)))
    for bid, fn in (('own_money', paint_own_money), ('ready', paint_ready), ('other_money', paint_other_money)):
        save_states(fn(key), key, bid, out_root)
        written += [bid] * 6
    fr = paint_frame(key)
    written.append(C.save_png(fr, _out(s.frame_path(), out_root)))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', type=Path, help='write a pack-source-shaped tree here instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        w = paint_skin(key, args.out_root)
        print(f'painted {key}: 1 background, {sum(1 for x in w if isinstance(x, str))} button PNGs, '
              f'{sum(1 for x in w if not isinstance(x, str)) - 1} frame')


if __name__ == '__main__':
    main()
