#!/usr/bin/env python3
"""Cozy painter "auction": the six auction skins, every texture they own.

    python tools/cozy/paint_auction.py                     # paint all six into pack-source
    python tools/cozy/paint_auction.py --skin auction_confirm
    python tools/cozy/paint_auction.py --out-root DIR      # paint into DIR (laid out like pack-source)

Skins: auction_house, auction_search, auction_mine, auction_watchlist,
auction_confirm, auction_duration (backgrounds, every button in all six states,
outer frames).

Family identity (decorative regions only): the auctioneer's gavel on its sound
block, blank price tags hanging on twine (never a number on them), the lot
ledger, a bidding paddle with a blank face, berry silk bookmarks and red wax.
Every sprite below is hand-authored here (CC0-1.0); the shared cozy grammar
comes from compose / primitives. Deterministic: fixed seeds only.

Licence: MIT (code); artwork CC0-1.0.
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

SKINS = ('auction_house', 'auction_search', 'auction_mine',
         'auction_watchlist', 'auction_confirm', 'auction_duration')
MARKET = ('auction_house', 'auction_search', 'auction_mine')
SEED = {'auction_house': 41, 'auction_search': 43, 'auction_mine': 47,
        'auction_watchlist': 53, 'auction_confirm': 59, 'auction_duration': 61}

FW = C.FRAME_WOOD   # frame board ramp (ink_1, wood_0 .. wood_3)


# ===========================================================================
# Hand-authored sprites
# ===========================================================================

# Auctioneer's gavel lying on its side: banded head (left), turned handle with
# a knob (right). 18 x 8.
GAVEL = [
    '.oooo.............',
    'obbbBo.........oo.',
    'o4321ooooooooo043o',
    'o4321133333333332o',
    'o4321122222222221o',
    'o4321OOOOOOOOOO21O',
    'obbBBo.........OO.',
    '.OOOO.............',
]
K_GAVEL = {'o': INK[1], 'O': INK[0], 'b': BRASS[2], 'B': BRASS[0],
           '4': WOOD[4], '3': WOOD[3], '2': WOOD[2], '1': WOOD[1], '0': WOOD[0]}

# Round sound block the gavel strikes. 14 x 4.
SOUND_BLOCK = [
    '.oooooooooooo.',
    'o443333333221o',
    'o111111111100O',
    '.OOOOOOOOOOOO.',
]

# Shorter gavel for narrow static columns. 14 x 8.
GAVEL_S = [
    '.oooo.........',
    'obbbBo.....oo.',
    'o4321oooooo43o',
    'o432113333332o',
    'o432112222221o',
    'o4321OOOOOO21O',
    'obbBBo.....OO.',
    '.OOOO.........',
]

# Auctioneer's hand bell: turned wooden handle, brass bell, clapper. 9 x 13.
BELL = [
    '...ooo...',
    '...oWo...',
    '...oWo...',
    '...owo...',
    '..ooooo..',
    '..o332o..',
    '.o33221o.',
    '.o32221o.',
    '.o32221o.',
    'o3222110o',
    'OOOOOOOOO',
    '...o0O...',
    '....O....',
]
K_BELL = {'o': INK[1], 'O': INK[0], 'W': WOOD[3], 'w': WOOD[1], '3': BRASS[3], '2': BRASS[2],
          '1': BRASS[1], '0': BRASS[0]}

# Stitched emblems for cloth banners (cream thread on berry cloth).
EMBLEM_GAVEL = [
    'ccc.......',
    'ccc.......',
    'cccdddddd.',
    'ccc.......',
    'ccc.......',
    '..........',
    '..dddddd..',
    '.cccccccc.',
]
EMBLEM_EYE = [
    '..ccc..',
    '.c...c.',
    'c..p..c',
    '.c...c.',
    '..ccc..',
]
EMBLEM_HOURGLASS = [
    'ccccccc',
    '.c...c.',
    '..c.c..',
    '...c...',
    '..cdc..',
    '.cdddc.',
    'ccccccc',
]

# Bidding paddle: blank cream face with a berry rim stripe, turned handle. 11 x 19.
PADDLE = [
    '...ooooo...',
    '.oorrrrroo.',
    '.or33222ro.',
    'or3322222ro',
    'or3222222ro',
    'or3222222ro',
    'or2222221ro',
    'or2222211ro',
    '.or22111ro.',
    '.oorrrrroo.',
    '...ooooo...',
    '....o4o....',
    '....o3o....',
    '....o3o....',
    '....o2o....',
    '....o2o....',
    '...obbBo...',
    '...o212o...',
    '....OOO....',
]
K_PADDLE = {'o': INK[1], 'O': INK[0], 'r': BERRY[1], '3': PARCHMENT[3], '2': PARCHMENT[2],
            '1': PARCHMENT[1], '4': WOOD[4], 'b': BRASS[2], 'B': BRASS[0]}
K_PADDLE_WOOD = {'4': WOOD[3]}

# Hourglass: wooden caps and posts, sky glass, ember sand running. 11 x 16.
HOURGLASS = [
    'ooooooooooo',
    'o443333221o',
    'ooooooooooo',
    '.poGggggop.',
    '.pogssssop.',
    '.p.ossso.p.',
    '.p..oso..p.',
    '.p...o...p.',
    '.p..oso..p.',
    '.p.ogsgo.p.',
    '.pogggsgop.',
    '.pogssssop.',
    '.pOOOOOOOp.',
    'ooooooooooo',
    'o443333221o',
    'OOOOOOOOOOO',
]
K_HOURGLASS = {'o': INK[1], 'O': INK[0], '4': WOOD[4], '3': WOOD[3], '2': WOOD[2], '1': WOOD[1],
               'p': WOOD[2], 'G': PARCHMENT[3], 'g': SKY[2], 's': EMBER[2]}

# Closed hunter-case pocket watch on its bow (no face, so it tells no time). 11 x 15.
WATCH = [
    '....ooo....',
    '...o...o...',
    '....oho....',
    '...oo2oo...',
    '..ooooooo..',
    '.o3322221o.',
    'o332222110o',
    'o322000210o',
    'o320222010o',
    'o320222010o',
    'o320222010o',
    'o220000010o',
    '.o2111110o.',
    '..o00000O..',
    '...OOOOO...',
]
K_WATCH = {'o': INK[1], 'O': INK[0], 'h': BRASS[3], '3': BRASS[3], '2': BRASS[2], '1': BRASS[1],
           '0': BRASS[0]}

# Stack of coins seen edge-on (no denominations). 9 x 9.
COIN_STACK = [
    '..ooooo..',
    '.o33322o.',
    'o2222111o',
    'o0000000o',
    'o2222111o',
    'o0000000o',
    'o2222111o',
    'o0000000O',
    '.OOOOOOO.',
]
K_COIN = {'o': INK[1], 'O': INK[0], '3': BRASS[3], '2': BRASS[2], '1': BRASS[1], '0': BRASS[0]}

# Quill standing in a squat inkwell. 9 x 17.
QUILL = [
    '.......ss',
    '......sSs',
    '.....sSs.',
    '....sSs..',
    '...sSs...',
    '...Ss....',
    '..sS.....',
    '..s......',
    '.oS......',
    '.o.......',
    'oooooo...',
    'o3221o...',
    'oooooooo.',
    'o4332221o',
    'o3222111o',
    'o2111110O',
    '.OOOOOOO.',
]
K_QUILL = {'s': PARCHMENT[3], 'S': PARCHMENT[0], 'o': INK[1], 'O': INK[0], '4': SKY[2], '3': SKY[1],
           '2': SKY[0], '1': INK[2], '0': INK[0]}

# Candle clock: a tall candle banded with brass hour rings, on a brass dish. 7 x 18.
CANDLE_CLOCK = [
    '...e...',
    '..eEe..',
    '..eEe..',
    '...E...',
    '...o...',
    '..o3o..',
    '.o332o.',
    '.obbBo.',
    '.o322o.',
    '.o322o.',
    '.obbBo.',
    '.o322o.',
    '.o321o.',
    '.obbBo.',
    '.o321o.',
    'oo321oo',
    'o11111O',
    '.OOOOO.',
]
K_CANDLE_CLOCK = {'e': EMBER[1], 'E': EMBER[2], 'o': INK[1], 'O': INK[0], '3': PARCHMENT[3],
                  '2': PARCHMENT[2], '1': BRASS[1], 'b': BRASS[2], 'B': BRASS[0]}
K_CANDLE_CLOCK['1'] = BRASS[1]

CANDLE_CLOCK_S = [
    '...e...',
    '..eEe..',
    '...E...',
    '...o...',
    '..o3o..',
    '.o332o.',
    '.obbBo.',
    '.o322o.',
    '.obbBo.',
    '.o321o.',
    'o11111O',
    '.OOOOO.',
]

# Little brass hanging nail with a ring.
NAIL = ['.o.', 'o3o', '.1.']


# ===========================================================================
# Small drawing helpers (local to this painter)
# ===========================================================================

def sprite(img, x, y, rows, key, flip_x=False):
    rows = [r.ljust(max(len(q) for q in rows), '.') for r in rows]
    P.sprite(img, x, y, rows, key, flip_x=flip_x)
    return P.sprite_size(rows)


def gavel(img, x, y, flip=False):
    sprite(img, x, y, GAVEL, K_GAVEL, flip_x=flip)


def sound_block(img, x, y):
    sprite(img, x, y, SOUND_BLOCK, K_GAVEL)


def gavel_on_block(img, x, y, flip=False):
    """Gavel resting across its sound block; (x, y) is the block's top-left.
    Occupies about 20 x 10."""
    sound_block(img, x, y + 6)
    gavel(img, x + (0 if not flip else -4) + 2, y, flip)


def price_tag(img, x, y, w, h, hem=BERRY, seed=0, ramp=PARCHMENT):
    """A blank hanging price tag (no numbers): pointed top with clipped
    corners, a brass eyelet at the top centre, dyed hem at the foot.
    Returns the eyelet hole (x, y)."""
    notch = 2 if w >= 7 else 1
    inside = set()
    for j in range(h):
        for i in range(w):
            if j < notch and (i + j < notch or (w - 1 - i) + j < notch):
                continue
            if j == h - 1 and i in (0, w - 1):
                continue
            inside.add((i, j))
    for (i, j) in inside:
        P.put(img, x + i, y + j, ramp[2])
    for (i, j) in inside:
        edge = any((i + dx, j + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge:
            P.put(img, x + i, y + j, INK[0] if j == h - 1 or i == w - 1 else INK[1])
    # light on the left, shade on the right
    for j in range(notch + 1, h - 1):
        P.put(img, x + 1, y + j, ramp[3])
        P.put(img, x + w - 2, y + j, ramp[1])
    for i in range(notch, w - notch):
        P.put(img, x + i, y + 1, ramp[3])
    # dyed hem
    if h >= 9:
        P.hline(img, x + 1, x + w - 2, y + h - 3, hem[2])
        P.hline(img, x + 1, x + w - 2, y + h - 2, hem[1])
    # a fibre so it reads as card, not plastic
    if w >= 7 and h >= 11:
        r = P._rng(seed, 'tagfibre', x, y)
        fx = x + 2 + r.randint(0, max(0, w - 6)); fy = y + 5 + r.randint(0, max(0, h - 10))
        P.hline(img, fx, fx + 1, fy, ramp[1])
    hx, hy = x + (w - 1) // 2, y + 2
    if w >= 7:
        P.sprite(img, hx - 1, hy - 1 + 1, ['.b.', 'bOB', '.B.'], {'b': BRASS[2], 'O': INK[0], 'B': BRASS[0]})
        hy += 1
    else:
        P.put(img, hx, hy, INK[0])
    return hx, hy


def hang(img, x0, y0, x1, y1, sag=0):
    """Twine from a nail at (x0, y0) to a tag eyelet at (x1, y1)."""
    P.twine(img, x0, y0, x1, y1, sag=sag)


def gavel_short(img, x, y):
    sprite(img, x, y, GAVEL_S, K_GAVEL)


def bell(img, x, y):
    sprite(img, x, y, BELL, K_BELL)


def banner(img, x, y, w, h, emblem=EMBLEM_GAVEL, ramp=BERRY, seed=0):
    """A small cloth banner on a brass rod: berry cloth, cream running stitch
    border, swallowtail foot and a stitched emblem (no words)."""
    # rod with knobs, hung from a nail by two twines
    nail(img, x + w // 2, y - 4)
    P.line(img, x + w // 2, y - 3, x + 1, y, PARCHMENT[1])
    P.line(img, x + w // 2, y - 3, x + w - 2, y, PARCHMENT[1])
    P.hline(img, x - 1, x + w, y, BRASS[1])
    P.hline(img, x - 1, x + w, y + 1, BRASS[0])
    for kx in (x - 2, x + w + 1):
        P.sprite(img, kx, y - 1, ['o', '3', 'o'][:1] + ['3', '1'], {'o': INK[1], '3': BRASS[3], '1': BRASS[0]})
    notch = w // 2
    inside = set()
    for j in range(h):
        for i in range(w):
            # swallowtail: a V cut into the foot
            depth = max(0, notch - abs(i - (w - 1) / 2) * 2)
            if j >= h - int(depth / 2 + 0.5) and j > h - notch:
                continue
            inside.add((i, j))
    for (i, j) in inside:
        P.put(img, x + i, y + 2 + j, ramp[1])
    for (i, j) in inside:
        edge = any((i + dx, j + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge:
            P.put(img, x + i, y + 2 + j, INK[0] if (i >= w // 2 or (i, j + 1) not in inside and j > 2) else INK[1])
        elif i == 1:
            P.put(img, x + i, y + 2 + j, ramp[2])
        elif i == w - 2:
            P.put(img, x + i, y + 2 + j, ramp[0])
    # running stitch 2 px inside the sides and top
    P.stitch_line(img, x + 2, y + 4, x + 2, y + h - notch // 2 - 1, PARCHMENT[1], 2, 2)
    P.stitch_line(img, x + w - 3, y + 4, x + w - 3, y + h - notch // 2 - 1, PARCHMENT[1], 2, 2)
    P.hline(img, x + 1, x + w - 2, y + 2, ramp[0])          # shadow under the rod
    ew, eh = P.sprite_size(emblem)
    ex, ey = x + (w - ew) // 2, y + 2 + max(4, (h - notch // 2 - eh) // 2 - 1)
    P.sprite(img, ex, ey, emblem, {'c': PARCHMENT[3], 'd': PARCHMENT[1], 'p': INK[0]})
    return (x, y, w, h + 2)


def book(img, x, y, w, h, ramp, band=BRASS):
    """A ledger lying on its side: cover, brass band, page block on the right."""
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=0, heavy='b', fill_colour=ramp[1])
    P.hline(img, x + 1, x + w - 4, y + 1, ramp[2])
    if h >= 5:
        P.hline(img, x + 1, x + w - 4, y + h - 2, ramp[0])
    P.vline(img, x + 3, y + 1, y + h - 2, band[2])
    P.vline(img, x + w - 3, y + 1, y + h - 2, PARCHMENT[2])
    P.vline(img, x + w - 2, y + 1, y + h - 2, PARCHMENT[1])


def niche(img, box):
    """A recessed cubby in the board (shadowed top/left, lit lower lip)."""
    x, y, w, h = box
    P.ink_outline(img, box, 'ink_1', radius=1, fill_colour=WOOD[1])
    P.hline(img, x + 1, x + w - 2, y + 1, INK[2])
    P.vline(img, x + 1, y + 2, y + h - 2, WOOD[0])
    P.hline(img, x + 2, x + w - 2, y + h - 2, WOOD[3])
    P.vline(img, x + w - 2, y + 2, y + h - 3, WOOD[2])


def coin_stack(img, x, y):
    sprite(img, x, y, COIN_STACK, K_COIN)


def paddle(img, x, y):
    sprite(img, x, y, PADDLE, K_PADDLE)


def hourglass(img, x, y):
    sprite(img, x, y, HOURGLASS, K_HOURGLASS)


def watch(img, x, y):
    sprite(img, x, y, WATCH, K_WATCH)


def quill(img, x, y):
    sprite(img, x, y, QUILL, K_QUILL)


def candle_clock(img, x, y):
    sprite(img, x, y, CANDLE_CLOCK, K_CANDLE_CLOCK)


def nail(img, x, y):
    P.sprite(img, x - 1, y - 1, NAIL, {'o': INK[1], '3': BRASS[3], '1': BRASS[0]})


def ribbon(img, x, y, length, ramp=BERRY, w=5, seed=0):
    """A silk bookmark ribbon hanging straight down from (x, y), ``w`` wide,
    with a swallowtail end; jogs one pixel once so it looks hung by hand."""
    r = P._rng(seed, 'ribbon', x, y)
    jog_at = y + r.randint(length // 3, 2 * length // 3) if length > 14 else None
    dx = 0
    for yy in range(y, y + length):
        if jog_at is not None and yy == jog_at:
            dx = 1
        P.put(img, x + dx, yy, INK[1])
        P.put(img, x + dx + w - 1, yy, INK[0])
        P.put(img, x + dx + 1, yy, ramp[2])
        for k in range(2, w - 1):
            P.put(img, x + dx + k, yy, ramp[1] if k < w - 2 else ramp[0])
    # swallowtail
    yy = y + length
    tail = ['o' + 'a' * (w - 2) + 'O', 'oa' + '.' * (w - 4) + 'aO', 'o' + '.' * (w - 2) + 'O']
    P.sprite(img, x + dx, yy, tail, {'o': INK[1], 'O': INK[0], 'a': ramp[1]})
    # a gloss fold across the silk
    P.hline(img, x + dx + 1, x + dx + w - 2, y + 2, ramp[0])
    return x + dx


def shelf(img, x, y, w, seed, ramp=WOOD):
    """A short plank shelf on two brass brackets."""
    P.plank(img, (x, y, w, 5), ramp, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def ruled_sheet(img, box, seed, lines=SKY[2], curl='br', behind=WOOD[0], seal=True, tack=True,
                margin=True):
    """A blank docket / ledger sheet: parchment, ruled lines (no words), a red
    margin rule, optional curled corner, tack and wax seal."""
    x, y, w, h = box
    P.parchment_panel(img, box, seed, outline='ink_1', fibres=True)
    for k in range(6, h - 4, 4):
        P.hline(img, x + 3, x + w - 4, y + k, lines)
    if margin:
        P.vline(img, x + 5, y + 3, y + h - 3, BERRY[2])
    if curl:
        P.page_curl(img, box, curl, 5, behind=behind)
    if tack:
        P.tack(img, x + w // 2, y + 1)
    if seal:
        P.wax_seal(img, x + w - 8, y + h - 8, 4, BERRY, seed, drip=True)


def lantern_on_rope(img, x0, x1, y, lx, glow=13):
    P.rope(img, x0, y, x1, y, sag=2)
    P.vline(img, lx + 3, y + 1, y + 4, INK[1])
    P.lantern(img, lx, y + 5)
    P.lantern_glow_ring(img, lx + 3, y + 10, glow, strength=1)


def bunting(img, x0, x1, y, seed, colours=(BERRY, PARCHMENT, BRASS)):
    """Twine strung with little triangular pennants (blank)."""
    pts = P.twine(img, x0, y, x1, y, sag=1)
    ys = {px: py for px, py in pts}
    k = 0
    for px in range(x0 + 3, x1 - 4, 8):
        ramp = colours[k % len(colours)]
        py = ys.get(px, y) + 1
        body = ramp[1] if ramp is not PARCHMENT else PARCHMENT[2]
        lit = ramp[2] if ramp is not PARCHMENT else PARCHMENT[3]
        P.sprite(img, px, py, ['ooooo', 'olaao', '.oao.', '..o..'],
                 {'o': INK[1], 'a': body, 'l': lit})
        k += 1


# ===========================================================================
# Buttons
# ===========================================================================

def berry_tag_face(img, b, body, seed):
    """Secondary linen tag stitched with berry thread (the auction house's
    own tags); same geometry and text box as compose.secondary_face."""
    x, y, w, h = body

    def face(target, eyelet):
        box = P.linen_tag(target, body, eyelet=eyelet, seed=seed, stitch=BERRY[1])
        bx, by, bw, bh = box
        return (bx + 1, by + 2, bw - 2, bh - 4)

    eyelet = 'left' if w >= 36 and h <= 20 else ('top' if h >= 36 and w < 36 else None)
    try:
        C._label_plan(b, face(C.new(b.w, b.h), eyelet))
    except ValueError:
        eyelet = None
    return face(img, eyelet)


def page_bookmark(img, body, direction):
    """A berry silk bookmark peeking down from the page's top edge, on the
    side away from the curl's lettering."""
    x, y, w, h = body
    bx = x + w - 9 if direction == 'next' else x + w - 7
    if direction == 'next' and w < 50:
        bx = x + w - 8
    P.sprite(img, bx, y, ['oaO', 'oaO', 'oaO', 'oaO', 'o.O'], {'o': INK[1], 'O': INK[0], 'a': BERRY[1]})


def paint_auction_button(key, bid, seed):
    s = geo.skin(key)
    b = s.button(bid)
    kind = C.button_kind(b)
    body = b.body.tuple()
    img = C.new(b.w, b.h)
    if bid == 'balance':
        balance_plaque(img, body, seed)
    elif kind == 'secondary':
        C.letter(img, b, berry_tag_face(img, b, body, seed), 'ink_0')
    elif kind in ('page_prev', 'page_next'):
        direction = 'next' if kind == 'page_next' else 'prev'
        box = C.page_face(img, body, direction, seed)
        lines, face, _ = C._label_plan(b, box)
        tw = max(L.text_width(t, face) for t in lines)
        if box[2] - tw >= 10:          # room for a bookmark beside the word
            page_bookmark(img, body, direction)
            bx, by, bw, bh = box
            box = (bx, by, bw - 4, bh) if direction == 'next' else (bx, by, bw - 5, bh)
        C.letter(img, b, box, 'ink_0')
    elif kind == 'primary':
        box = C.primary_face(img, body, seed)
        C.letter(img, b, box, 'ink_0', shadow='brass_3')
        x, y, w, h = body
        if h >= 30:
            # an engraved gavel-and-block mark under the lettering
            cx = x + w // 2
            yy = y + h - 7
            for dx in range(-9, 10):
                if abs(dx) > 2 and dx % 2 == 0:
                    P.put(img, cx + dx, yy, BRASS[0])
            P.sprite(img, cx - 2, yy - 1, ['0003', '.0..', '.0..'][:2], {'0': BRASS[0], '3': BRASS[3]})
        # oil scuffs on the plank rim
        P.put(img, x + 5, y + 1, WOOD[1]); P.put(img, x + 6, y + 1, WOOD[1])
        P.put(img, x + w - 7, y + h - 2, WOOD[3])
    elif kind == 'danger':
        C.letter(img, b, C.danger_face(img, body, seed), 'parch_3', shadow='berry_0')
    else:   # close seal / icon
        img = C.paint_button(key, bid, seed)
    geo.finish_button(img, key, bid)
    return img


def balance_plaque(img, body, seed):
    """Read-only Balance column: a recessed carved wooden plaque (shadow on the
    top/left inner edge, so it sits *into* the board and does not read as a
    raised control) holding a coin purse on a nail, a blank ledger slip with a
    bookmark, and a short stack of coins. No numbers."""
    x, y, w, h = body
    P.ink_outline(img, body, 'ink_1', radius=1, fill_colour=WOOD[1])
    # carved recess: dark top/left inner edge, lit bottom/right lip
    P.vline(img, x + 1, y + 1, y + h - 2, WOOD[0])
    P.hline(img, x + 1, x + w - 2, y + 1, WOOD[0])
    P.vline(img, x + w - 2, y + 2, y + h - 2, WOOD[3])
    P.hline(img, x + 2, x + w - 2, y + h - 2, WOOD[3])
    # vertical grain inside
    for gx, y0, y1 in ((5, 4, 20), (11, 26, 40), (7, 56, 66), (12, 6, 12)):
        P.vline(img, x + gx, y + y0, y + y1, WOOD[0])
        P.vline(img, x + gx + 1, y + y0 + 2, y + y0 + 4, WOOD[2])
    # purse hanging from a brass nail
    nail(img, x + w // 2, y + 4)
    icons.draw_icon(img, 'balance', (x, y + 5, w, 14))
    # ledger slip, pinned, ruled, with a berry bookmark
    sx, sy, sw, sh = x + 3, y + 22, w - 6, 26
    P.parchment_panel(img, (sx, sy, sw, sh), seed, outline='ink_1', fibres=False)
    for k in range(5, sh - 3, 3):
        P.hline(img, sx + 2, sx + sw - 3, sy + k, SKY[2])
    P.tack(img, sx + sw // 2, sy, small=True)
    P.sprite(img, sx + sw - 4, sy + sh - 2, ['oaO', 'oaO', 'o.O'], {'o': INK[1], 'O': INK[0], 'a': BERRY[1]})
    # three coins stacked, then a tack
    coin_stack(img, x + (w - 9) // 2, y + 54)
    P.tack(img, x + w // 2, y + h - 6)


# ===========================================================================
# Backgrounds
# ===========================================================================

# Envelope standing on its edge, flap closed with a small berry seal. 13 x 9.
ENVELOPE = [
    'ooooooooooooo',
    'o3p2222222p1o',
    'o23p22222p21o',
    'o222p222p221o',
    'o2222pyp2221o',
    'o222pyzyp221o',
    'o22p2yyx2p21o',
    'o1p1111x11p1o',
    'OOOOOOOOOOOOO',
]
K_ENVELOPE = {'o': INK[1], 'O': INK[0], '3': PARCHMENT[3], '2': PARCHMENT[2], '1': PARCHMENT[1],
              'p': PARCHMENT[0], 'y': BERRY[1], 'z': BERRY[2], 'x': BERRY[0]}


def cubby_shelf(img, x0, x1, y):
    """A ledge fitted across a niche: ink-edged board (lit top row), and the
    shadow it casts on the back wall below it."""
    P.hline(img, x0, x1, y, INK[1])
    P.hline(img, x0, x1, y + 1, WOOD[4])
    P.hline(img, x0, x1, y + 2, WOOD[2])
    P.hline(img, x0, x1, y + 3, INK[0])
    P.hline(img, x0, x1, y + 4, WOOD[0])
    for gx in (x0 + 4, x1 - 3):
        P.put(img, gx, y + 2, WOOD[1])


def static_column_market(img, key, seed):
    """Right column beside the grid (static cells 17/26/35/44): a recessed
    cubby with two blank price tags on twine, a ledge across it holding the
    per-screen still life (house: two ledgers with a bookmark; search: the
    lens propped behind a ledger; mine: my own lot letter, sealed), and the
    gavel resting on its block on the cubby floor. Every prop stands on
    something or overlaps a neighbour, so none reads as an item in a cell."""
    niche(img, (156, 36, 17, 70))
    nail(img, 164, 39)
    hang(img, 164, 40, 160, 45)
    hang(img, 164, 40, 168, 50)
    price_tag(img, 157, 44, 8, 14, BERRY, seed)
    price_tag(img, 165, 49, 7, 12, BRASS, seed + 1)
    ledge = 86                                   # straddles the cell 35 / 44 boundary
    cubby_shelf(img, 157, 171, ledge)
    if key == 'auction_house':
        book(img, 158, ledge - 6, 13, 6, BERRY)
        book(img, 159, ledge - 11, 11, 6, SKY)
        P.vline(img, 167, ledge, ledge + 4, BERRY[1])        # bookmark over the ledge
        P.put(img, 168, ledge + 1, BERRY[0])
        P.put(img, 167, ledge + 5, BERRY[0])
    elif key == 'auction_search':
        rows, k = icons.ICONS['search']
        P.sprite(img, 160, ledge - 16, rows, k, flip_x=True)  # leaning on the back wall
        book(img, 158, ledge - 6, 13, 6, SAGE)              # ...half hidden behind a ledger
    else:   # auction_mine: my own lot, a letter sealed with my wax
        sprite(img, 158, ledge - 9, ENVELOPE, K_ENVELOPE)
    sound_block(img, 157, 100)                    # resting on the cubby floor
    gavel_short(img, 158, 93)


def paint_market_background(key):
    seed = SEED[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    static_column_market(img, key, seed)
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    geo.finish_background(img, key)
    return img


def paint_watchlist_background(key):
    seed = SEED[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    # --- top row (static cells 0-8): a rail of silk bookmarks and blank tags ---
    P.rope(img, 6, 18, 169, 18, sag=1)
    P.tack(img, 5, 17); P.tack(img, 170, 17)
    xs = list(range(14, 164, 13))
    for k, tx in enumerate(xs):
        if k % 2 == 0:
            ribbon(img, tx, 20, 6, BERRY if k % 4 == 0 else SKY, w=4, seed=seed + k)
        else:
            hang(img, tx + 3, 19, tx + 3, 21)
            price_tag(img, tx, 21, 7, 9, BRASS if k % 4 == 1 else BERRY, seed + k)
    # --- left column (cells 9/18/27/36): the watch banner, an eye stitched on ---
    banner(img, 7, 41, 13, 58, EMBLEM_EYE, BERRY, seed)
    # --- right column (17/26/35/44): pocket watch on its chain, a tag ---
    niche(img, (156, 36, 17, 70))
    nail(img, 164, 39)
    for yy in range(40, 49):
        P.put(img, 164, yy, BRASS[2] if yy % 2 else BRASS[0])
    watch(img, 159, 47)
    hang(img, 164, 62, 164, 79)
    price_tag(img, 160, 78, 9, 14, BERRY, seed + 3)
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    geo.finish_background(img, key)
    return img


def paint_confirm_background(key):
    seed = SEED[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed, wells='stitched')
    slot = s.content_slots[0]
    cl = slot.clearance          # (42, 52, 20, 20)
    # --- display stand: a wooden plinth with a berry velvet cushion ---
    stand = (cl.x - 11, cl.y - 11, cl.w + 22, cl.h + 24)
    P.plank(img, stand, WOOD, seed, 'ink_1', radius=1, grain=0.4)
    P.highlight_edge(img, stand, WOOD[4], 'tl', broken=4, seed=seed, inset=1)
    P.shadow_edge(img, stand, WOOD[0], 'br', inset=1)
    vel = (cl.x - 7, cl.y - 7, cl.w + 14, cl.h + 14)
    P.ink_outline(img, vel, 'ink_1', radius=2, heavy='br', fill_colour=BERRY[1])
    P.highlight_edge(img, vel, BERRY[2], 'tl', broken=5, seed=seed, inset=1)
    P.shadow_edge(img, vel, BERRY[0], 'br', inset=1)
    for tx, ty in ((vel[0] + 3, vel[1] + 3), (vel[0] + vel[2] - 4, vel[1] + 3),
                   (vel[0] + 3, vel[1] + vel[3] - 4), (vel[0] + vel[2] - 4, vel[1] + vel[3] - 4)):
        P.put(img, tx, ty, BRASS[3]); P.put(img, tx + 1, ty + 1, BRASS[0])
    P.well_frame(img, [cl.tuple()], 'stitched', thread=PARCHMENT[2])
    # blank brass plaque on the plinth front, then the plinth foot
    py = stand[1] + stand[3] - 8
    P.brass_plate(img, (cl.x - 2, py, cl.w + 4, 6), rivets=False, outline='ink_1')
    P.fill(img, (stand[0] + 3, stand[1] + stand[3], stand[2] - 6, 2), WOOD[0])
    P.hline(img, stand[0] + 3, stand[0] + stand[2] - 4, stand[1] + stand[3] + 2, INK[0])
    # --- a blank lot tag hanging beside the item ---
    nail(img, 85, 22)
    hang(img, 85, 23, 84, 59, sag=0)
    price_tag(img, 80, 57, 9, 16, BERRY, seed)
    # --- docket above the confirm plate: ruled lines only, sealed ---
    ruled_sheet(img, (100, 19, 66, 30), seed, curl='br', behind=WOOD[1])
    # --- left: inkwell and quill on a wall shelf, the hand bell hung beneath
    # it (both straddle cell boundaries), a stack of ledgers ---
    shelf(img, 6, 41, 24, seed + 4)
    quill(img, 12, 24)
    P.vline(img, 18, 46, 48, INK[1])              # bell cord from the shelf
    bell(img, 14, 48)
    book(img, 6, 92, 22, 5, SKY)
    book(img, 8, 87, 19, 5, BERRY)
    book(img, 5, 97, 24, 6, SAGE)
    # --- bottom-left (cells 45-47): the gavel on its block and coins, on a shelf ---
    shelf(img, 8, 119, 38, seed + 5)
    gavel_on_block(img, 11, 109)
    coin_stack(img, 32, 110)
    # --- right of the confirm plate: candle and a standing ledger on a wall
    # shelf that straddles cells 35/44 ---
    shelf(img, 151, 86, 20, seed + 6)
    icons.draw_motif(img, 'candle', 152, 75)
    P.lantern_glow_ring(img, 155, 77, 9, strength=1)
    icons.draw_motif(img, 'ledger', 159, 76)
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    geo.finish_background(img, key)
    return img


def paint_duration_background(key):
    seed = SEED[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    # --- static cell 13 between the 12/15-day tags: plain board crossed by the
    # twine the duration tags hang on (a nail and a berry bow at the knot), so
    # the cell never reads as an item in a slot ---
    P.twine(img, 76, 41, 87, 39, sag=2)
    P.twine(img, 89, 39, 99, 44, sag=2)
    nail(img, 88, 38)
    P.sprite(img, 86, 39, ['y.y', 'xyx', '.x.', 'x.x'], {'y': BERRY[1], 'x': BERRY[0]})
    # --- static cells 18-20 left of Close: shelf with candle clock, ledger, gavel ---
    shelf(img, 8, 65, 52, seed)
    sprite(img, 11, 53, CANDLE_CLOCK_S, K_CANDLE_CLOCK)
    P.lantern_glow_ring(img, 14, 55, 8, strength=1)
    icons.draw_motif(img, 'ledger', 21, 55)
    gavel_short(img, 38, 57)
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    geo.finish_background(img, key)
    return img


# ===========================================================================
# Frames
# ===========================================================================

EMBLEM_FOR = {'auction_watchlist': EMBLEM_EYE, 'auction_duration': EMBLEM_HOURGLASS}


def frame_top(img, a, seed):
    """Top strip: pennant bunting, split around the heading ribbon if any."""
    if not a.heading:
        bunting(img, 12, a.w - 13, 2, seed)
    else:
        half = (L.text_width(a.heading, 'sprig') + 16) // 2 + 4
        bunting(img, 12, a.w // 2 - half, 2, seed)
        bunting(img, a.w // 2 + half, a.w - 13, 2, seed + 1)


def frame_bottom(img, a):
    H = a.h
    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0)
    P.tack(img, 10, H - 5); P.tack(img, a.w - 11, H - 5)


def vine(img, x, y0, y1, seed):
    for k, yy in enumerate(range(y0, y1 - 12, 12)):
        P.ink_line(img, x - (k % 2), yy, x - ((k + 1) % 2), yy + 12, SAGE[0], wobble=0)
        P.leaf(img, x + (1 if k % 2 else -7), yy + 3, 'ne' if k % 2 else 'nw', small=k % 3 == 2)


def frame_market(key, a, seed):
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    frame_top(img, a, seed)
    # --- left panel ---
    lantern_on_rope(img, lp.x + 6, lp.right - 7, 12, lp.x + 16)
    banner(img, lp.x + 9, 36, 22, 30, EMBLEM_FOR.get(key, EMBLEM_GAVEL), BERRY, seed)
    shelf(img, lp.x + 4, 84, lp.w - 8, seed)
    if key == 'auction_search':
        icons.draw_motif(img, 'ledger', lp.x + 6, 74)
        icons.draw_icon(img, 'search', (lp.x + 18, 71, 12, 12))
    elif key == 'auction_mine':
        icons.draw_motif(img, 'ledger', lp.x + 6, 74)
        P.wax_seal(img, lp.x + 25, 78, 5, BERRY, seed, drip=False)
    elif key == 'auction_watchlist':
        icons.draw_motif(img, 'ledger', lp.x + 6, 74)
        watch(img, lp.x + 20, 69)
    else:
        gavel_on_block(img, lp.x + 9, 74)
    # twine of three blank price tags
    P.twine(img, lp.x + 3, 98, lp.right - 4, 98, sag=4)
    for k, (tx, hem) in enumerate(((lp.x + 6, BERRY), (lp.x + 16, BRASS), (lp.x + 26, SAGE))):
        ty = 100 + (2 if k == 1 else 0)
        P.vline(img, tx + 3, ty - 1, ty + 1, PARCHMENT[0])
        price_tag(img, tx, ty + 1, 8, 14, hem, seed + k)
    # the lot docket, sealed
    ruled_sheet(img, (lp.x + 6, 128, 27, 34), seed, curl='br', behind=FW[1])
    # bidding paddle hung on a nail
    nail(img, lp.x + 20, 166)
    paddle(img, lp.x + 15, 167)
    # coins and a ledger at the foot
    shelf(img, lp.x + 4, H - 40, lp.w - 8, seed + 3)
    coin_stack(img, lp.x + 7, H - 49)
    icons.draw_motif(img, 'ledger', lp.x + 19, H - 50)
    icons.draw_motif(img, 'crate', lp.x + 15, H - 27)
    # --- right panel ---
    shelf(img, rp.x + 4, 30, rp.w - 8, seed + 1)
    icons.draw_motif(img, 'candle', rp.x + 8, 19)
    P.lantern_glow_ring(img, rp.x + 10, 21, 10, strength=1)
    hourglass(img, rp.x + 21, 14)
    # a big featured lot tag on twine from a nail
    nail(img, rp.x + 20, 44)
    P.twine(img, rp.x + 20, 45, rp.x + 20, 51)
    price_tag(img, rp.x + 13, 51, 15, 24, BERRY, seed + 4)
    P.wax_seal(img, rp.x + 20, 64, 4, BERRY, seed + 5, drip=False)
    # the auctioneer's hand bell beside the gavel on its block
    nail(img, rp.x + 12, 86)
    bell(img, rp.x + 8, 87)
    gavel_short(img, rp.x + 20, 92)
    sound_block(img, rp.x + 20, 99)
    # a sealed docket and a vine to the foot shelf
    ruled_sheet(img, (rp.x + 5, 116, 28, 30), seed + 2, curl='bl', behind=FW[1], seal=False)
    vine(img, rp.x + 9, 150, H - 50, seed + 1)
    nail(img, rp.x + 26, 154)
    hang(img, rp.x + 26, 155, rp.x + 26, 160)
    price_tag(img, rp.x + 22, 159, 9, 15, SKY, seed + 6)
    shelf(img, rp.x + 4, H - 40, rp.w - 8, seed + 2)
    P.mug(img, rp.x + 6, H - 49, EMBER, steam=True, seed=seed + 1)
    coin_stack(img, rp.x + 22, H - 49)
    frame_bottom(img, a)
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


def frame_short(key, a, seed):
    """Duration frame (184 tall): candle clock and hourglass stations."""
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    frame_top(img, a, seed)
    lantern_on_rope(img, lp.x + 6, lp.right - 7, 12, lp.x + 16)
    shelf(img, lp.x + 4, 58, lp.w - 8, seed)
    candle_clock(img, lp.x + 7, 40)
    P.lantern_glow_ring(img, lp.x + 10, 42, 9, strength=1)
    hourglass(img, lp.x + 20, 42)
    P.twine(img, lp.x + 3, 76, lp.right - 4, 76, sag=4)
    for k, (tx, hem) in enumerate(((lp.x + 6, BERRY), (lp.x + 16, BRASS), (lp.x + 26, SAGE))):
        ty = 78 + (2 if k == 1 else 0)
        P.vline(img, tx + 3, ty - 1, ty + 1, PARCHMENT[0])
        price_tag(img, tx, ty + 1, 8, 14, hem, seed + k)
    ruled_sheet(img, (lp.x + 6, 100, 27, 28), seed, curl='br', behind=FW[1])
    shelf(img, lp.x + 4, H - 40, lp.w - 8, seed + 3)
    coin_stack(img, lp.x + 7, H - 49)
    icons.draw_motif(img, 'ledger', lp.x + 19, H - 50)
    icons.draw_motif(img, 'crate', lp.x + 15, H - 27)
    shelf(img, rp.x + 4, 30, rp.w - 8, seed + 1)
    icons.draw_motif(img, 'candle', rp.x + 8, 19)
    P.lantern_glow_ring(img, rp.x + 10, 21, 10, strength=1)
    gavel_short(img, rp.x + 18, 22)
    banner(img, rp.x + 9, 48, 22, 30, EMBLEM_HOURGLASS, BERRY, seed)
    nail(img, rp.x + 12, 92)
    bell(img, rp.x + 8, 93)
    nail(img, rp.x + 26, 96)
    hang(img, rp.x + 26, 97, rp.x + 26, 102)
    price_tag(img, rp.x + 22, 101, 9, 15, SKY, seed + 6)
    vine(img, rp.x + 30, 118, H - 44, seed + 1)
    shelf(img, rp.x + 4, H - 40, rp.w - 8, seed + 2)
    P.mug(img, rp.x + 6, H - 49, EMBER, steam=True, seed=seed + 1)
    coin_stack(img, rp.x + 22, H - 49)
    frame_bottom(img, a)
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ===========================================================================
# Driver
# ===========================================================================

BACKGROUNDS = {
    'auction_house': paint_market_background,
    'auction_search': paint_market_background,
    'auction_mine': paint_market_background,
    'auction_watchlist': paint_watchlist_background,
    'auction_confirm': paint_confirm_background,
    'auction_duration': paint_duration_background,
}


def paint_frame(key, a):
    seed = SEED[key]
    if key == 'auction_duration':
        return frame_short(key, a, seed)
    return frame_market(key, a, seed)


def paint_skin(key, tex_root):
    s = geo.skin(key)
    written = {'background': 0, 'button': 0, 'frame': 0}
    bg = BACKGROUNDS[key](key)
    C.save_png(bg, Path(tex_root) / 'menu' / f'{key}.png')
    written['background'] += 1
    for b in s.buttons:
        normal = paint_auction_button(key, b.id, SEED[key])
        # close seals get grey-wax disabled frames from the shared button_states
        states = C.button_states(normal, key, b.id)
        C.save_button_states(states, key, b.id, root=tex_root)
        written['button'] += len(states)
    for a in s.art_layers:
        fr = paint_frame(key, a)
        C.save_png(fr, Path(tex_root) / 'frames' / key / f'{a.id}.png')
        written['frame'] += 1
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--skin', choices=SKINS, action='append', help='repaint only this skin (repeatable)')
    ap.add_argument('--out-root', type=Path, help='paint into DIR laid out like pack-source instead')
    args = ap.parse_args(argv)
    tex_root = geo.TEXTURES if args.out_root is None else \
        args.out_root / 'assets' / 'quasar_gui' / 'textures'
    total = {'background': 0, 'button': 0, 'frame': 0}
    for key in args.skin or SKINS:
        w = paint_skin(key, tex_root)
        for k in total:
            total[k] += w[k]
        print(f'painted {key}: {w["background"]} background, {w["button"]} button PNGs, {w["frame"]} frame(s)')
    print(f'total: {total["background"]} backgrounds, {total["button"]} button PNGs, {total["frame"]} frames -> {tex_root}')


if __name__ == '__main__':
    main()
