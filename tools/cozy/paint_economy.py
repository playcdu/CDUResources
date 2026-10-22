#!/usr/bin/env python3
"""Cozy painter "economy": economy_hub and economy_log.

    python tools/cozy/paint_economy.py                 # paint into pack-source
    python tools/cozy/paint_economy.py --out-root DIR  # paint a pack-source-like tree elsewhere
    python tools/cozy/paint_economy.py --sprites PNG   # also dump the motif sprites (inspection)

Family identity (style guide, economy): a market stall's sage-and-cream
awning, a leather coin purse and a green-bound account ledger.

* economy_hub (chest_3, eight painted controls, no content wells): the title
  sheet becomes the stall's sign under a scalloped awning hem, two stall posts
  stand in the side margins and a brass-nailed counter edge runs under the
  controls. The frame is the stall itself: a striped awning across the top
  beam, a hanging purse and a merchant's scale on the left, a shop bell, an
  open ledger (ruled, never numbered), a quill and a sack of coins on the
  right.
* economy_log (chest_6, 28 balance-free listing wells): the wells lie on a
  ruled account-ledger page bound in green cloth with brass corner guards, a
  double heading rule, red margin rules and a bookmark ribbon. The frame is a
  counting house: receipts on a spike, shelved ledgers, an hourglass, an
  abacus and ribbon bookmarks.

Every sprite below is an original pixel map (CC0-1.0); code MIT. Deterministic:
fixed seeds only.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from PIL import Image  # noqa: E402

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import icons  # noqa: E402
import lettering as L  # noqa: E402
import primitives as P  # noqa: E402
from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD, luminance  # noqa: E402

HUB, LOG = 'economy_hub', 'economy_log'
SEED = 23
TEX_REL = Path('assets') / 'quasar_gui' / 'textures'

# ---------------------------------------------------------------------------
# Sprite keys
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


def spr(img, x, y, rows, flip_x=False):
    P.sprite(img, x, y, rows, K, flip_x=flip_x)


# Hanging leather coin purse (15 x 17): frilled neck, twine drawstring with a
# tied bow, lit top-left, a brass clasp coin peeking at the foot.
PURSE = [
    '...o..o.o..o...',
    '..odo.oeo.odo..',
    '...ocoodoocoo..',
    '....ocdcdco....',
    '....oqsqqqo....',
    '...oqo.oqo.o...',
    '...obcdddcbo...',
    '..obcdeedddcbo.',
    '.obcdeedddddcbo',
    '.obcdedddddccbo',
    'obcddddddddccbo',
    'obcdddddddcccbo',
    'obccdddddccc3bo',
    '.obcccccccc232o',
    '.oabbbbbbbbo1oo',
    '..oaaaaaaaaoo..',
    '...ooooooooo...',
]

# Merchant's balance scale (23 x 18): brass beam on a turned post, two pans
# on twine, a wooden plinth.
SCALE = [
    '..........o3o..........',
    '..oooooooo323oooooooo..',
    '.o32222222222222222220o',
    '..oooooooo121oooooooo..',
    '..q.q.....o21o....q.q..',
    '.q...q....o21o...q...q.',
    '.q...q....o21o...q...q.',
    'q.....q...o21o..q.....q',
    'ooooooo...o21o..ooooooo',
    'o32221o...o21o..o32221o',
    '.o000o....o21o...o000o.',
    '..ooo.....o21o....ooo..',
    '..........o21o.........',
    '.........o2221o........',
    '.......oo222110oo......',
    '......oeddddddccbo.....',
    '......obbbbbbbbbao.....',
    '.......ooooooooooo.....',
]

# Coins seen edge-on in a stack: two rows per coin (lit rim, shaded edge),
# a lit top face, nudged by hand so the stack does not look machined.
COIN_TOP = ['.oooo.', 'o3332o']
COIN_EDGE = ['o2221o', 'o1100o']
COIN_FOOT = ['.oooo.']
COIN_JITTER = (0, 0, 1, 0, -1, 0, 0, 1, 1, 0)

# Small purse for the Balance plaque (8 x 10).
MINI_PURSE = [
    '.o....o.',
    '.oeo.do.',
    '..oddo..',
    '..oqqo..',
    '.odeddo.',
    'odeedddo',
    'odedddco',
    'oddddcbo',
    '.obbbbo.',
    '..oooo..',
]

# Shop bell on a curled bracket (16 x 15).
BELL = [
    'oooooooooo......',
    'oddddddddco.....',
    'ooooooocboo.....',
    '.......oco......',
    '.......o3o......',
    '......o323o.....',
    '.....o32221o....',
    '.....o32211o....',
    '....o322111o....',
    '....o3221110o...',
    '...o32221110o...',
    '...o0000000oo...',
    '....ooo2ooo.....',
    '......o0o.......',
    '.......o........',
]

# Open account ledger (30 x 19): two ruled pages (no figures), red margin
# rules, a green cloth cover and a ribbon hanging out of the gutter.
LEDGER_OPEN = [
    '.oooooooooooooo.oooooooooooooo',
    'osssssssssssssooosssssssssssso',
    'osrrrrrrrrrrrrqoqrrrrrrrrrrrro',
    'orrzrmmmmmmmmrqoqrzrmmmmmmmrro',
    'orrzrrrrrrrrrrqoqrzrrrrrrrrrro',
    'orrzrmmmmmmmmrqoqrzrmmmmmmrrro',
    'orrzrrrrrrrrrrqoqrzrrrrrrrrrro',
    'orrzrmmmmmmrrrqoqrzrmmmmmmmmro',
    'orrzrrrrrrrrrrqoqrzrrrrrrrrrro',
    'orrzrmmmmmmmmrqoqrzrmmmmrrrrro',
    'orrzrrrrrrrrrrqoqrzrrrrrrrrrro',
    'orrzrmmmmmrrrrqoqrzrmmmmmmmrro',
    'orrzrrrrrrrrrrqoqrzrrrrrrrrrro',
    'oqqqqqqqqqqqqqpopqqqqqqqqqqqqo',
    'ohhhhhhhhhhhhhhyhhhhhhhhhhhhho',
    'oggggggggggggggygggggggggggggo',
    '.oooooooooooooozooooooooooooo.',
    '..............oyo.............',
    '..............oxo.............',
]

# Inkpot with a quill (14 x 16).
QUILL_POT = [
    '...........oo.',
    '..........osso',
    '.........osrso',
    '........osrso.',
    '.......osrso..',
    '......osrso...',
    '.....osrqo....',
    '....osqqo.....',
    '....oqqo......',
    '..ooooOooo....',
    '.oiikkkkiio...',
    'oikkllkkkkio..',
    'oklmllkkkkko..',
    'okllkkkkkkko..',
    'okkkkkkkkkko..',
    '.ooooooooooo..',
]

# Burlap sack of coins (17 x 16): drawstring, coins spilling at its foot.
SACK = [
    '.....o.o.o........',
    '....oqoroqo.......',
    '.....oqrqo........',
    '....oo1o1oo.......',
    '...oqrrrrrqo......',
    '..oqrsrrrrrqo.....',
    '.oqrsrrrrrrrqo....',
    '.oqsrrrprrrrqo....',
    'oqrsrrpppprrrqo...',
    'oqrrrrp33prrrqo...',
    'oqrrrrpppprrqqo...',
    'oqrrrrrrrrrqqpo...',
    '.oqqrrrrrqqqpo.oo.',
    '..ooqqqqqqppo.o32o',
    '...ooooooooooo321o',
    '..............ooo.',
]

# Hourglass (11 x 16): wooden caps and posts, sand mid-fall.
HOURGLASS = [
    'ooooooooooo',
    'oeddddddcbo',
    'ooooooooooo',
    '.o.osssso.o',
    '.o.oGGGGo.o',
    '.o..oFFo..o',
    '.o..oFFo..o',
    '.o...oo...o',
    '.o...oFo..o',
    '.o..ossFo.o',
    '.o.ossFsso.',
    '.o.osFFFso.',
    '.o.oFFFFFo.',
    'ooooooooooo',
    'oeddddddcbo',
    'ooooooooooo',
]

# Receipt spike: a brass spike on a wooden block with ruled slips (no figures).
SPIKE_BASE = [
    '..oooooooooo..',
    '.oeddddddddbo.',
    'oddddddddddcbo',
    'obbbbbbbbbbbao',
    '.oooooooooooo.',
]


# ---------------------------------------------------------------------------
# Drawing helpers (economy only)
# ---------------------------------------------------------------------------

def awning(img, x0, x1, y, body=3, stripe=6, phase=0, top_ink=True, bottom_ink=True, clip=None):
    """Market-stall awning valance from x0..x1: ``body`` rows of alternating
    sage / cream stripes (lit first row, shaded last row), then one row of
    rounded scallops whose dips are inked, then (``bottom_ink``) an ink row
    under each scallop. ``clip`` (x, y, w, h) restricts painting."""
    def put(x, yy, c):
        if clip and not (clip[0] <= x < clip[0] + clip[2] and clip[1] <= yy < clip[1] + clip[3]):
            return
        P.put(img, x, yy, c)

    if top_ink:
        for x in range(x0, x1 + 1):
            put(x, y - 1, INK[1])
    for x in range(x0, x1 + 1):
        k = (x - x0 + phase) // stripe
        i = (x - x0 + phase) % stripe
        sage = k % 2 == 0
        ramp = (SAGE[0], SAGE[1], SAGE[2]) if sage else (PARCHMENT[1], PARCHMENT[2], PARCHMENT[3])
        for j in range(body):
            c = ramp[1]
            if j == 0:
                c = ramp[2]
            elif j == body - 1 and body > 2:
                c = ramp[0] if not sage else SAGE[0]
            if sage and i == 0 and 0 < j < body - 1:
                c = SAGE[2]
            if not sage and i == stripe - 1 and 0 < j:
                c = PARCHMENT[1]
            put(x, y + j, c)
        edge = i in (0, stripe - 1)
        put(x, y + body, INK[1] if edge else (PARCHMENT[1] if not sage else SAGE[1]))
        if bottom_ink and not edge:
            put(x, y + body + 1, INK[1])


def frame_awning(img, a):
    """The stall's awning along a frame's top: a shallow valance over the
    container (top strip only) and a deeper one over each side panel, with
    stripes kept in register across both."""
    awning(img, 1, a.w - 2, 1, body=4, stripe=8, phase=0, top_ink=False, bottom_ink=True)
    lp, rp = a.left_panel, a.right_panel
    for x0, x1 in ((1, lp.right - 1), (rp.x, a.w - 2)):
        awning(img, x0, x1, 1, body=8, stripe=8, phase=(x0 - 1) % 16, top_ink=False, bottom_ink=True)


def coin_stack(img, x, y_bottom, n, salt=0):
    """Stack of ``n`` coins seen edge-on, bottom ink row at y_bottom."""
    spr(img, x, y_bottom, COIN_FOOT)
    dx = 0
    for k in range(n):
        dx = COIN_JITTER[(k + salt) % len(COIN_JITTER)]
        spr(img, x + dx, y_bottom - 2 - 2 * k, COIN_EDGE)
    spr(img, x + dx, y_bottom - 2 * n - 2, COIN_TOP)


def shelf(img, x, y, w, seed):
    """Short plank shelf on two brass brackets (5 px board)."""
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def peg(img, x, y):
    """Wooden peg knocked into a board (3 x 3)."""
    P.sprite(img, x - 1, y - 1, ['oeo', 'odb', 'obo'], K)


def side_ruled_card(img, box, seed, rules=SKY[2], margin=BERRY[2], curl=None, behind=None):
    """Parchment slip with ruled lines and a red margin rule; no figures."""
    x, y, w, h = box
    P.parchment_panel(img, box, seed, outline='ink_1', fibres=False)
    for yy in range(y + 3, y + h - 2, 3):
        P.hline(img, x + 2, x + w - 3, yy, rules)
    if margin is not None and w > 8:
        P.vline(img, x + 3, y + 1, y + h - 2, margin)
    if curl:
        P.page_curl(img, box, curl, 4, behind=behind)


def bunting(img, x0, x1, y, sag, colours, seed):
    """Pennant bunting on twine: little triangular flags every 6 px."""
    pts = P.twine(img, x0, y, x1, y, sag=sag)
    for n, (px, py) in enumerate(pts[2:-2:6]):
        col = colours[n % len(colours)]
        rows = ['ooooo', 'occco', '.oco.', '.oco.', '..o..']
        P.sprite(img, px - 2, py + 1, rows, {'o': INK[1], 'c': col[1]})
        P.put(img, px - 1, py + 2, col[2])


def book_spine(img, x, y_bottom, w, h, ramp, band=BRASS[2]):
    """Upright ledger seen spine-on on a shelf: cloth spine with two brass bands."""
    box = (x, y_bottom - h + 1, w, h)
    P.ink_outline(img, box, 'ink_1', radius=0, heavy='r', fill_colour=ramp[1])
    P.vline(img, x + 1, box[1] + 1, y_bottom - 1, ramp[2])
    P.hline(img, x + 1, x + w - 2, box[1] + 3, band)
    P.hline(img, x + 1, x + w - 2, y_bottom - 3, band)
    P.put(img, x + w - 2, box[1] + 3, BRASS[0])
    P.put(img, x + w - 2, y_bottom - 3, BRASS[0])


def abacus(img, x, y, seed):
    """Counting frame (30 x 22): wooden frame, five wires, hand-placed beads.
    Bead positions are decorative only (no value is shown)."""
    w, h = 30, 22
    P.plank(img, (x, y, w, h), WOOD, seed, 'ink_1', radius=1, grain=0.0)
    P.fill(img, (x + 3, y + 3, w - 6, h - 6), WOOD[0])
    P.highlight_edge(img, (x + 2, y + 2, w - 4, h - 4), INK[1], 'tl')
    beads = [(0, 1, 2, 9, 10), (0, 5, 6, 7, 10), (1, 2, 3, 4, 10), (0, 1, 7, 8, 9), (0, 4, 5, 9, 10)]
    ramps = [BERRY, BRASS, SAGE, BRASS, BERRY]
    for row in range(5):
        wy = y + 4 + row * 3
        P.hline(img, x + 3, x + w - 4, wy, ASH[1])
        for b in beads[row]:
            bx = x + 3 + b * 2
            r = ramps[row]
            P.put(img, bx, wy, r[1] if r is not BRASS else BRASS[1])
            P.put(img, bx + 1, wy, r[0] if r is not BRASS else BRASS[0])
            P.put(img, bx, wy - 1, r[2] if r is not BRASS else BRASS[3])
            P.put(img, bx + 1, wy - 1, r[1] if r is not BRASS else BRASS[2])
    # divider bar
    P.vline(img, x + 3 + 11, y + 3, y + h - 4, WOOD[3])


def ribbon_bookmark(img, x, y0, y1, ramp=BERRY, w=4):
    """Hanging ribbon bookmark with a swallowtail end."""
    for yy in range(y0, y1 + 1):
        P.put(img, x, yy, INK[1])
        P.put(img, x + w - 1, yy, INK[1])
        for xx in range(x + 1, x + w - 1):
            P.put(img, xx, yy, ramp[1])
        P.put(img, x + 1, yy, ramp[2] if (yy - y0) % 5 else ramp[1])
    # swallowtail
    P.put(img, x, y1 + 1, INK[1]); P.put(img, x + w - 1, y1 + 1, INK[1])
    P.put(img, x + 1, y1 + 1, ramp[0]); P.put(img, x + w - 2, y1 + 1, ramp[0])
    P.put(img, x + 1, y1 + 2, INK[1]); P.put(img, x + w - 2, y1 + 2, INK[1])
    for xx in range(x + 1, x + w - 1):
        P.put(img, xx, y1, ramp[0])


def clipboard(img, x, y, w, h, seed):
    """Wooden clipboard holding a ruled receipt sheet (no figures) under a
    brass clip, with a second slip peeking out underneath."""
    P.plank(img, (x, y, w, h), WOOD, seed, 'ink_1', radius=1, grain=0.4)
    side_ruled_card(img, (x + 4, y + 5, w - 6, h - 7), seed + 1, margin=None)
    side_ruled_card(img, (x + 2, y + 4, w - 6, h - 8), seed + 2, curl='br', behind=WOOD[2])
    cx = x + w // 2 - 4
    P.sprite(img, cx, y - 1, ['..oooo..', '.o3322o.', 'o322221o', 'o211110o', '.oooooo.'],
             {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[1], '0': BRASS[0]})


def brass_corner_guard(img, x, y, corner):
    """Triangular brass corner protector of a ledger cover (5 x 5)."""
    rows = ['ooooo', 'o332o', 'o21o.', 'o1o..', 'oo...']
    P.sprite(img, x, y, rows, {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[1]},
             flip_x='r' in corner, flip_y='b' in corner)


def engrave(img, x, y, rows, lip=BRASS[3], groove=BRASS[0]):
    """Engrave a tiny motif into a brass plate: groove with a lit lower-right lip."""
    on = {(i, j) for j, r in enumerate(rows) for i, ch in enumerate(r) if ch == '#'}
    for (i, j) in on:
        if (i + 1, j + 1) not in on:
            P.put(img, x + i + 1, y + j + 1, lip)
    for (i, j) in on:
        P.put(img, x + i, y + j, groove)


GAVEL = ['.###.......', '.###.......', '.###########', '.###.......', '#####......']
CROWN = ['#...#...#', '##.#.#.##', '#.#...#.#', '#.......#', '#########']


# ---------------------------------------------------------------------------
# economy_hub
# ---------------------------------------------------------------------------

def hub_background():
    s = geo.skin(HUB)
    img = C.base_background(HUB, seed=SEED)
    tband, iband = C.bands(HUB)
    # Stall sign: the title sheet hangs under the awning roll (rows 2-4 are
    # above the live glyph rows 5-13), and a scalloped hem drops below it.
    awning(img, tband.x, tband.right - 1, 2, body=2, stripe=8, phase=4, top_ink=False, bottom_ink=False)
    # restore the sheet's soft rim at its ends
    P.vline(img, tband.x, 2, 14, INK[2]); P.vline(img, tband.right - 1, 2, 14, INK[2])
    P.hline(img, tband.x, tband.right - 1, 1, INK[1])
    awning(img, 1, s.width - 2, 15, body=1, stripe=8, phase=4, top_ink=True, bottom_ink=True)
    # stall posts in the side margins (between rim and controls)
    for px in (2, s.width - 6):
        P.ink_outline(img, (px, 17, 4, 55), 'ink_1', radius=0, heavy='r', fill_colour=WOOD[2])
        P.vline(img, px + 1, 18, 70, WOOD[4])
        for yy in (24, 40, 58):
            P.put(img, px + 2, yy, WOOD[1]); P.put(img, px + 2, yy + 1, WOOD[1])
        P.put(img, px + 1, 34, WOOD[3])
    # counter edge under the controls: brass-nailed rail
    P.hline(img, 1, s.width - 2, 71, BRASS[1])
    P.hline(img, 1, s.width - 2, 72, INK[1])
    for nx in range(5, s.width - 4, 12):
        P.put(img, nx, 71, BRASS[3])
    geo.finish_background(img, HUB)
    return img


def hub_button(b):
    img = C.paint_button(HUB, b.id, seed=SEED)
    if b.id in ('auction', 'admin_shop'):
        # a little stall: awning over the brass sign
        awning(img, 1, b.w - 2, 1, body=3, stripe=6, phase=0 if b.id == 'auction' else 3,
               top_ink=False, bottom_ink=True)
        P.put(img, 1, 1, INK[1]); P.put(img, b.w - 2, 1, INK[1])
        motif = GAVEL if b.id == 'auction' else CROWN
        mw = len(motif[0])
        engrave(img, (b.w - mw) // 2, b.h - 9, motif)
    elif b.id in ('balance', 'rank'):
        img = C.new(b.w, b.h)
        info_plaque(img, b)
    elif b.style == 'secondary':
        # sage running stitch: the stall's linen
        _recolour(img, PARCHMENT[0], SAGE[1], rows=(2, b.h - 3))
    geo.finish_button(img, HUB, b.id)
    return img


def _recolour(img, src, dst, rows):
    px = img.load()
    for y in rows:
        for x in range(img.width):
            if px[x, y][:3] == tuple(src) and px[x, y][3]:
                px[x, y] = tuple(dst) + (255,)


def info_plaque(img, b):
    """Read-only information card: a flat parchment card in a thin brass bezel,
    softly inked, pinned with two tacks; never a raised plank."""
    w, h = b.w, b.h
    P.ink_outline(img, (0, 0, w, h), 'ink_2', radius=1, fill_colour=BRASS[1])
    P.hline(img, 1, w - 2, 1, BRASS[2]); P.vline(img, 1, 1, h - 2, BRASS[2])
    P.hline(img, 2, w - 2, h - 2, BRASS[0]); P.vline(img, w - 2, 2, h - 2, BRASS[0])
    card = (2, 2, w - 4, h - 4)
    P.ink_outline(img, card, 'ink_2', radius=0, fill_colour=PARCHMENT[2])
    P.hline(img, 3, w - 4, 3, PARCHMENT[3])
    if b.id == 'rank':
        icons.draw_icon(img, 'rank', (0, 0, w, h))
        return
    # balance: purse at the left, the button's own label to its right
    spr(img, 4, (h - len(MINI_PURSE)) // 2, MINI_PURSE)
    C.letter(img, b, (14, 4, w - 17, h - 8), 'ink_0')


def hub_frame():
    s = geo.skin(HUB)
    a = s.layer()
    img = C.base_frame(HUB, a.id, seed=SEED, heading=False)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    # awning across the top beam, deeper scallops over the side panels
    frame_awning(img, a)
    P.ink_outline(img, (0, 0, a.w, a.h), 'ink_0', radius=3)
    for corner, (x, y) in (('bl', (2, H - 8)), ('br', (a.w - 8, H - 8))):
        C.brass_corner(img, x, y, corner)
    C.heading_ribbon(img, a.w // 2, 0, a.heading)

    # --- left panel: name tag, hanging purse, scale on a shelf, coin stacks ---
    peg(img, lp.x + 20, 14)
    C.side_tag(img, lp, a.left_heading or a.heading, 22, SEED, twine_from=(lp.x + 20, 15))
    peg(img, lp.x + 20, 38)
    P.twine(img, lp.x + 20, 39, lp.x + 20, 44)
    spr(img, lp.x + 13, 43, PURSE)
    P.lantern_glow_ring(img, lp.x + 20, 52, 0)
    shelf(img, lp.x + 4, 86, lp.w - 8, SEED + 3)
    spr(img, lp.x + 8, 68, SCALE)
    shelf(img, lp.x + 4, 120, lp.w - 8, SEED + 4)
    coin_stack(img, lp.x + 6, 119, 5, salt=0)
    coin_stack(img, lp.x + 13, 119, 3, salt=3)
    coin_stack(img, lp.x + 20, 119, 8, salt=5)
    coin_stack(img, lp.x + 27, 119, 2, salt=1)
    # a vine of sage climbing from below
    P.ink_line(img, lp.x + 30, 128, lp.x + 31, H - 12, SAGE[0], wobble=1, seed=SEED)
    for k, yy in enumerate(range(132, H - 14, 9)):
        P.leaf(img, lp.x + (31 if k % 2 else 25), yy, 'ne' if k % 2 else 'nw', small=k % 3 == 2)
    icons.draw_motif(img, 'crate', lp.x + 6, H - 21)
    icons.draw_motif(img, 'coin', lp.x + 18, H - 14)

    # --- right panel: shop bell, bunting, open ledger, quill, sack of coins ---
    spr(img, rp.x + 4, 13, BELL)
    P.lantern_glow_ring(img, rp.x + 12, 21, 9, strength=1)
    bunting(img, rp.x + 2, rp.right - 3, 34, 3, [SAGE, PARCHMENT, BERRY], SEED)
    peg(img, rp.x + 19, 46)
    spr(img, rp.x + 5, 50, LEDGER_OPEN)
    shelf(img, rp.x + 4, 98, rp.w - 8, SEED + 5)
    spr(img, rp.x + 6, 82, QUILL_POT)
    icons.draw_motif(img, 'candle', rp.x + 25, 87)
    P.lantern_glow_ring(img, rp.x + 27, 89, 10, strength=1)
    # a lantern hung from a peg, and herbs trailing past it
    peg(img, rp.x + 12, 110)
    P.vline(img, rp.x + 12, 111, 113, INK[1])
    P.lantern(img, rp.x + 9, 114)
    P.lantern_glow_ring(img, rp.x + 12, 119, 12, strength=1)
    P.ink_line(img, rp.x + 31, 106, rp.x + 30, 146, SAGE[0], wobble=1, seed=SEED + 1)
    for k, yy in enumerate(range(110, 146, 8)):
        P.leaf(img, rp.x + (31 if k % 2 else 25), yy, 'ne' if k % 2 else 'nw', small=k % 2 == 1)
    spr(img, rp.x + 5, H - 30, SACK)
    coin_stack(img, rp.x + 26, H - 14, 4)

    # --- bottom strip: the counter's brass-nailed front rail ---
    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0, light='brass_2', dark='brass_0')
    P.tack(img, 10, H - 5); P.tack(img, a.w - 11, H - 5)
    geo.finish_frame(img, HUB, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# economy_log
# ---------------------------------------------------------------------------

def log_background():
    s = geo.skin(LOG)
    img = C.base_background(LOG, seed=SEED + 10)
    tband, iband = C.bands(LOG)
    grid = s.content_bbox                      # 24..151 x 34..107
    # green cloth ledger cover with a parchment page lying on it
    cover = (3, 16, s.width - 6, 91)
    P.ink_outline(img, cover, 'ink_1', radius=1, heavy='br', fill_colour=SAGE[0])
    P.hline(img, cover[0] + 1, cover[0] + cover[2] - 2, cover[1] + 1, SAGE[1])
    page = (cover[0] + 2, cover[1] + 2, cover[2] - 4, cover[3] - 4)
    P.parchment_panel(img, page, SEED + 11, outline='ink_2', fibres=True)
    for corner, (x, y) in (('tl', (cover[0], cover[1])), ('tr', (cover[0] + cover[2] - 5, cover[1])),
                           ('bl', (cover[0], cover[1] + cover[3] - 5)),
                           ('br', (cover[0] + cover[2] - 5, cover[1] + cover[3] - 5))):
        brass_corner_guard(img, x, y, corner)
    px0, py0, pw, ph = page
    # page head: a ledger's double heading rule running edge to edge across
    # the page (no column boxes, so nothing reads as a slot or an empty field)
    hy = grid.y - 5
    for yy, c in ((hy - 3, SKY[2]), (hy - 1, SKY[1]), (hy, SKY[2])):
        P.hline(img, px0 + 2, px0 + pw - 3, yy, c)
    # red double margin rules down both margins
    for mx in (px0 + 12, px0 + 14):
        P.vline(img, mx, py0 + 1, py0 + ph - 2, BERRY[2])
    # ruled lines across the margins, level with the listing rows
    for yy in [grid.y - 1] + [grid.y + 18 * k + 17 for k in range(4)] + [grid.y + 18 * k + 8 for k in range(4)]:
        if yy < py0 + ph - 1:
            P.hline(img, px0 + 2, px0 + 11, yy, SKY[2])
            P.hline(img, grid.right + 7, px0 + pw - 3, yy, SKY[2])
    # the ledger's pressed wax seal in the header corner
    P.wax_seal(img, px0 + 8, py0 + 7, 6, BERRY, SEED + 12, drip=True, emblem='coin')
    # bookmark ribbon hanging from the top edge over the right margin
    ribbon_bookmark(img, grid.right + 9, cover[1] - 1, 70, BERRY, w=5)
    # wells: recessed frames with a parchment-thread stitch on the page
    holes = P.merge_holes(s.content_slots)
    P.stitched_well(img, holes, thread=PARCHMENT[0], protect=[tband.tuple(), iband.tuple()])
    geo.finish_background(img, LOG)
    return img


def log_button(b):
    img = C.paint_button(LOG, b.id, seed=SEED + 20)
    if b.id in ('previous', 'next'):
        # ledger ruling on the page-turn sheets: a red margin rule by the spine side
        x, y, w, h = b.body.tuple()
        for yy in range(y + 2, y + h - 2):
            if img.getpixel((x + 3, yy))[:3] == tuple(PARCHMENT[2]):
                P.put(img, x + 3, yy, BERRY[2])
        for xx in range(x + 4, x + w - 2):
            if img.getpixel((xx, y + h - 4))[:3] == tuple(PARCHMENT[2]):
                P.put(img, xx, y + h - 4, SKY[2])
    geo.finish_button(img, LOG, b.id)
    return img


def log_frame():
    s = geo.skin(LOG)
    a = s.layer()
    img = C.base_frame(LOG, a.id, seed=SEED + 30, heading=False)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    frame_awning(img, a)
    P.ink_outline(img, (0, 0, a.w, a.h), 'ink_0', radius=3)
    for corner, (x, y) in (('bl', (2, H - 8)), ('br', (a.w - 8, H - 8))):
        C.brass_corner(img, x, y, corner)
    C.heading_ribbon(img, a.w // 2, 0, a.heading)

    # --- left panel: receipts on a spike, shelved ledgers, hourglass, lantern ---
    P.rope(img, lp.x + 4, 16, lp.right - 5, 16, sag=2)
    P.vline(img, lp.x + 19, 17, 20, INK[1])
    P.lantern(img, lp.x + 16, 21)
    P.lantern_glow_ring(img, lp.x + 19, 26, 13, strength=1)
    # clipboard of ruled receipts hung on a peg
    peg(img, lp.x + 19, 42)
    clipboard(img, lp.x + 7, 45, 25, 32, SEED + 1)
    # shelf of ledgers
    shelf(img, lp.x + 4, 112, lp.w - 8, SEED + 6)
    for k, (w_, h_, ramp) in enumerate(((5, 22, SAGE), (5, 20, BERRY), (6, 23, SAGE), (4, 18, SKY), (5, 21, BERRY))):
        x = lp.x + 6 + sum((5, 5, 6, 4, 5)[:k])
        book_spine(img, x, 111, w_, h_, ramp)
    # hourglass on a second shelf
    shelf(img, lp.x + 4, 146, lp.w - 8, SEED + 7)
    spr(img, lp.x + 7, 130, HOURGLASS)
    coin_stack(img, lp.x + 22, 145, 3)
    coin_stack(img, lp.x + 28, 145, 5)
    # trailing vine to the floor
    P.ink_line(img, lp.x + 9, 152, lp.x + 8, H - 26, SAGE[0], wobble=1, seed=SEED + 2)
    for k, yy in enumerate(range(156, H - 28, 9)):
        P.leaf(img, lp.x + (9 if k % 2 else 3), yy, 'ne' if k % 2 else 'nw', small=k % 3 == 1)
    spr(img, lp.x + 16, H - 28, SACK)

    # --- right panel: ribbon bookmarks, open ledger, abacus, purse ---
    for k, (x, y1, ramp) in enumerate(((rp.x + 5, 34, BERRY), (rp.x + 11, 28, SAGE), (rp.x + 17, 38, SKY))):
        ribbon_bookmark(img, x, 8, y1, ramp, w=4)
    spr(img, rp.x + 5, 52, LEDGER_OPEN)
    abacus(img, rp.x + 5, 86, SEED + 8)
    peg(img, rp.x + 20, 124)
    P.twine(img, rp.x + 20, 125, rp.x + 20, 130)
    spr(img, rp.x + 13, 129, PURSE)
    shelf(img, rp.x + 4, 172, rp.w - 8, SEED + 9)
    spr(img, rp.x + 6, 156, QUILL_POT)
    icons.draw_motif(img, 'candle', rp.x + 25, 161)
    P.lantern_glow_ring(img, rp.x + 27, 163, 10, strength=1)
    for k, yy in enumerate(range(184, H - 14, 9)):
        P.leaf(img, rp.x + (31 if k % 2 else 25), yy, 'ne' if k % 2 else 'nw', small=k % 3 == 2)
    P.ink_line(img, rp.x + 30, 180, rp.x + 31, H - 12, SAGE[0], wobble=1, seed=SEED + 3)
    coin_stack(img, rp.x + 6, H - 13, 4)
    coin_stack(img, rp.x + 13, H - 13, 2)

    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0, light='brass_2', dark='brass_0')
    P.tack(img, 10, H - 5); P.tack(img, a.w - 11, H - 5)
    geo.finish_frame(img, LOG, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def paint_all(out_root):
    out_root = Path(out_root)
    tex = out_root / TEX_REL
    written = {'background': 0, 'button': 0, 'frame': 0}
    for key, bg_fn, btn_fn, fr_fn in ((HUB, hub_background, hub_button, hub_frame),
                                       (LOG, log_background, log_button, log_frame)):
        s = geo.skin(key)
        C.save_png(bg_fn(), out_root / s.asset)
        written['background'] += 1
        for b in s.buttons:
            normal = btn_fn(b)
            states = C.button_states(normal, key, b.id)
            C.save_button_states(states, key, b.id, root=tex)
            written['button'] += len(states)
        a = s.layer()
        C.save_png(fr_fn(), tex / 'frames' / key / f'{a.id}.png')
        written['frame'] += 1
    return written


def sprite_sheet(path, scale=6):
    items = [PURSE, SCALE, BELL, LEDGER_OPEN, QUILL_POT, SACK, HOURGLASS, SPIKE_BASE]
    W = sum(len(r[0]) + 3 for r in items) + 3
    Hh = max(len(r) for r in items) + 6
    img = Image.new('RGBA', (W, Hh), WOOD[2] + (255,))
    x = 3
    for rows in items:
        spr(img, x, 3, rows)
        x += len(rows[0]) + 3
    img = img.resize((W * scale, Hh * scale), Image.Resampling.NEAREST)
    img.save(path)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out-root', type=Path, default=geo.ROOT / 'pack-source',
                    help='pack-source-like root to paint into (default: pack-source)')
    ap.add_argument('--sprites', type=Path, help='also write a sprite inspection sheet here')
    args = ap.parse_args(argv)
    for rows in (PURSE, SCALE, BELL, LEDGER_OPEN, QUILL_POT, SACK, HOURGLASS, SPIKE_BASE):
        assert len({len(r) for r in rows}) == 1, rows
    written = paint_all(args.out_root)
    print('WROTE', written, 'under', args.out_root)
    if args.sprites:
        print('WROTE', sprite_sheet(args.sprites))


if __name__ == '__main__':
    main()
