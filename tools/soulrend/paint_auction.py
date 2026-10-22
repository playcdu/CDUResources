#!/usr/bin/env python3
"""Soulrend painter "auction": every texture of the six auction skins.

    python tools/soulrend/paint_auction.py                 # all six skins -> pack-source
    python tools/soulrend/paint_auction.py --skin auction_confirm
    python tools/soulrend/paint_auction.py --out-root DIR  # DIR laid out like textures/

Skins: auction_house, auction_search, auction_mine (the market, chest_6),
auction_watchlist (chest_6), auction_confirm (chest_6), auction_duration
(chest_3). Each gets its background, all six states of every button and its
outer frame.

Family identity (decorative regions only, never in wells or text bands): the
auction block in a candlelit hall - a gavel resting on a stone block, blank
heraldic banner tags hanging on chains, a candle clock notched in blood, a
bronze bell on a chain, ember light pooling by dither. The three market
screens differ in the prop kept in their stone niche and in the frame's arch
(house: a bound ledger; search: a scrying lens with soul-light; mine: a
sealed writ).

Deterministic: fixed seeds, no clock, no unseeded randomness.
Licence: MIT (artwork produced by it: CC0-1.0).
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
from palette import BLOOD, EMBER, GOLD, INK, IRON, MOSS, SOUL, STONE, UMBER, VELLUM  # noqa: E402

MARKET = ('auction_house', 'auction_search', 'auction_mine')
SKINS = MARKET + ('auction_watchlist', 'auction_confirm', 'auction_duration')
SEEDS = {'auction_house': 31, 'auction_search': 37, 'auction_mine': 41,
         'auction_watchlist': 43, 'auction_confirm': 47, 'auction_duration': 53}
# the prop each market screen keeps in its niche
PROP = {'auction_house': 'ledger', 'auction_search': 'lens', 'auction_mine': 'writ'}

# a darker masonry ramp for recessed alcoves (the wall in shadow)
DEEP = [INK[1], STONE[0], STONE[1], STONE[2]]


# ---------------------------------------------------------------------------
# Hand-authored sprites (original, CC0-1.0). Colour keys: primitives.SK.
# ---------------------------------------------------------------------------

# bronze auction bell, crown loop at the top, iron clapper below the lip
BELL = [
    '....ooo....',
    '....o.o....',
    '...ooooo...',
    '..oHhhhgo..',
    '..oHhhhgo..',
    '.oHHhhhhgo.',
    '.oHhhhhhgo.',
    '.oHhhhhhgo.',
    'oHHhhhhhhgo',
    'ohhhhhhhggo',
    'ooooooooooo',
    '....oco....',
    '.....o.....',
]

SMALL_BELL = [
    '..ooo..',
    '..o.o..',
    '.ooooo.',
    '.oHhgo.',
    'oHhhhgo',
    'ohhhggo',
    'ooooooo',
    '..oco..',
    '...o...',
]

# a blank heraldic banner tag: gold eyelet, gold hem, swallowtail
TAG = [
    '..ooo..',
    '..oHo..',
    'oooHooo',
    'oHhhhgo',
    'otsssro',
    'otsssro',
    'otsssro',
    'otsssro',
    'otssrro',
    'otsosro',
    'oso.oro',
    'oo...oo',
]
TAG_SHORT = [
    '..ooo..',
    '..oHo..',
    'oooHooo',
    'oHhhhgo',
    'otsssro',
    'otsssro',
    'otssrro',
    'otsosro',
    'oso.oro',
    'oo...oo',
]
VELLUM_TAG = {'t': VELLUM[3], 's': VELLUM[2], 'r': VELLUM[0]}
GOLDLESS = {'H': IRON[3], 'h': IRON[2], 'g': IRON[0]}

# watchman's lantern: iron cage, ember glass split by an iron bar
LANTERN = [
    '....ooo....',
    '....o.o....',
    '...ooooo...',
    '..odccbao..',
    '.ooooooooo.',
    '.ocFFbffao.',
    '.ocFFbfeao.',
    '.ocFfbfeao.',
    '.ocffbeeao.',
    '.ocfebeeao.',
    '.ooooooooo.',
    '..obbbbao..',
    '...ooooo...',
]

# hourglass: umber caps, iron posts, dark glass with bone sand
HOURGLASS = [
    'ooooooooo',
    'o3322221o',
    'ooooooooo',
    '.coiiioa.',
    '.coxwxoa.',
    '.c.oxo.a.',
    '.c..w..a.',
    '.c.oio.a.',
    '.coiwioa.',
    '.coxwwoa.',
    'ooooooooo',
    'o3322221o',
    'ooooooooo',
]

# the auctioneer's gavel lying on its side: umber head with a gold band,
# lit umber handle (16 x 7)
GAVEL = [
    '.oooooo.........',
    'o3Hh32o.........',
    'o3Hh21ooooooooo.',
    'o2hg21o33333332o',
    'o2hg10o22222211o',
    'o1gg10ooooooooo.',
    '.oooooo.........',
]

# small sound block the gavel strikes (umber disc, side view)
SOUND_BLOCK = [
    '.oooooo.',
    'o332221o',
    'o221110o',
    '.oooooo.',
]

# scrying lens on a little iron stand (search), soul glass
LENS_STAND = [
    '..ooooo..',
    '.ocdccbo.',
    'ockLlkkao',
    'odLlkkkao',
    'oclkkkkao',
    'ockkkk0ao',
    '.ockkkao.',
    '..ooooo..',
    '....o....',
    '...obo...',
    '..obbao..',
    '.ooooooo.',
]

# sealed writ (mine): a folded vellum packet tied with blood cord, big seal
SEALED_WRIT = [
    'oooooooooooo',
    'oyyyyyyyyyxo',
    'oyxxxxxxxxwo',
    'oxwxxxxxxwwo',
    'osssssssssso',
    'oxxwxoooxwvo',
    'oxxxostsoxvo',
    'oxxxotssovvo',
    'owwwosssowvo',
    'oooooorooooo',
    '......rr....',
    '.....r..r...',
]

# open ledger on a lectern (house), umber boards, two vellum pages, blood ribbon
OPEN_LEDGER = [
    '.oooooo.oooooo.',
    'o2yyyyyoyyyyy1o',
    'o2xwwxxoxwwwx1o',
    'o2xxxxxoxxxxx1o',
    'o2xwwwxoxwwxx1o',
    'o2xxxxxoxxxxs1o',
    'o2wwwwvovwwws1o',
    '.oooooooooooso.',
    '......o2o...s..',
    '......o2o......',
    '.....oo21oo....',
    '....oooooooo...',
]


# ---------------------------------------------------------------------------
# Drawing helpers (this painter's own; shared modules are never edited)
# ---------------------------------------------------------------------------

def ledge(img, x, y, w, brackets=True, ramp=STONE):
    """A carved stone ledge 4 px tall on two little iron brackets."""
    P.fill(img, (x, y, w, 4), ramp[2])
    P.hline(img, x, x + w - 1, y, ramp[3])
    P.hline(img, x, x + w - 1, y + 3, ramp[0])
    P.put(img, x + w // 3, y + 1, ramp[1]); P.put(img, x + 2 * w // 3 + 1, y + 2, ramp[1])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0, heavy='b')
    if brackets:
        for bx in (x + 1, x + w - 4):
            P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


def recess(img, box, seed, ramp=DEEP, course=6, rim=True, moss=0.06):
    """A recessed patch of shadowed masonry with an ink rim (light from the
    top-left: ink_1 lintel on top/left, a stone_3 sill on bottom/right)."""
    x, y, w, h = box
    P.stone_blocks(img, (x + 1, y + 1, w - 2, h - 2), seed, ramp, course=course, moss=moss, cracks=0.3)
    if rim:
        P.ink_outline(img, box, 'ink_0', radius=0)
        P.hline(img, x + 1, x + w - 2, y + 1, INK[1])
        P.vline(img, x + 1, y + 1, y + h - 2, INK[1])
        P.hline(img, x + 2, x + w - 2, y + h - 2, STONE[2])
        P.vline(img, x + w - 2, y + 2, y + h - 2, STONE[2])


def tag(img, x, y, kind='blood', short=False):
    """A blank banner tag with its eyelet top-left at (x, y). Returns (w, h)."""
    rows = TAG_SHORT if short else TAG
    key = VELLUM_TAG if kind == 'vellum' else None
    if kind == 'iron':
        key = {'t': IRON[3], 's': IRON[2], 'r': IRON[1], **GOLDLESS}
    P.sprite(img, x, y, rows, key)
    return P.sprite_size(rows)


def hang_tag(img, cx, y0, y1, kind='blood', short=False, seed=0, cord=False):
    """A chain (or a cord) from (cx, y0) down to a tag whose eyelet is at y1."""
    if y1 - y0 >= 3:
        if cord:
            P.vline(img, cx, y0, y1 - 1, INK[2])
        else:
            P.chain(img, cx, y0, cx, y1 - 1, seed=seed, shadow=None)
    return tag(img, cx - 3, y1, kind, short)


def bell(img, cx, y, small=False):
    rows = SMALL_BELL if small else BELL
    w, h = P.sprite_size(rows)
    P.sprite(img, cx - w // 2, y, rows)
    return w, h


def candle_clock(img, x, y, height=14, seed=0, holder='gold', marks='blood_1'):
    """A tall bone-wax candle notched in hours (blood marks), lit; returns the
    flame centre for glow. Wick top at (x + 1, y)."""
    fx, fy = P.candle(img, x, y, height=height, lit=True, holder=holder, seed=seed)
    for j in range(4, height, 3):
        P.hline(img, x, x + 1, y + j, marks)
    return fx, fy


def gavel_block(img, x, y, seed=0, w=24):
    """The auction block: a squared stone block with a carved front panel and
    a gold-banded top, a sound block on it and the gavel resting beside.
    (x, y) is the block's top-left; returns its box."""
    h = 11
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=1, heavy='br', fill_colour=STONE[2])
    P.hline(img, x + 1, x + w - 2, y + 1, GOLD[1])
    P.put(img, x + 1, y + 1, GOLD[2]); P.put(img, x + 2, y + 1, GOLD[2])
    P.hline(img, x + 1, x + w - 2, y + 2, INK[1])
    P.vline(img, x + 1, y + 3, y + h - 2, STONE[3])
    P.hline(img, x + 2, x + w - 2, y + h - 2, STONE[1])
    P.vline(img, x + w - 2, y + 3, y + h - 2, STONE[1])
    # carved front panel (cut inward: dark top/left, lit bottom/right)
    px0, py0, px1, py1 = x + 4, y + 4, x + w - 5, y + h - 3
    P.hline(img, px0, px1, py0, STONE[0]); P.vline(img, px0, py0, py1, STONE[0])
    P.hline(img, px0 + 1, px1, py1, STONE[3]); P.vline(img, px1, py0 + 1, py1, STONE[3])
    P.crack(img, x + w - 3, y + 4, 4, seed=seed, colour=STONE[0], branch=False)
    if w >= 26:
        P.sprite(img, x + 1, y - 4, SOUND_BLOCK)
        P.sprite(img, x + w - 17, y - 7, GAVEL)
    else:
        P.sprite(img, x + (w - 16) // 2, y - 7, GAVEL)
    return (x, y, w, h)


def sconce(img, x, y, seed):
    """Iron wall sconce holding a lit candle; returns the flame centre."""
    P.sprite(img, x - 3, y + 8, ['occcco', '.obao.', '..oo..', '..oa..', '..ob..', '...o..'])
    return P.candle(img, x - 1, y, height=6, lit=True, holder=None, seed=seed)


def hook(img, x, y):
    """A small iron wall hook (an eye bolt) at (x, y)."""
    P.sprite(img, x - 1, y, ['oco', 'obo', '.o.'])


def bracket_arm(img, x, y, length, right=True):
    """An iron wall bracket arm sticking out horizontally from a wall plate."""
    plate = ['oo', 'co', 'bo', 'ao', 'oo']
    if right:
        P.sprite(img, x, y - 2, plate)
        P.hline(img, x + 2, x + 1 + length, y, IRON[2])
        P.hline(img, x + 2, x + 1 + length, y + 1, INK[0])
        P.hline(img, x + 2, x + 1 + length, y - 1, INK[1])
        P.put(img, x + 2 + length, y, INK[1]); P.put(img, x + 2 + length, y - 1, INK[1])
    else:
        P.sprite(img, x - 1, y - 2, plate, flip_x=True)
        P.hline(img, x - 1 - length, x - 2, y, IRON[2])
        P.hline(img, x - 1 - length, x - 2, y + 1, INK[0])
        P.hline(img, x - 1 - length, x - 2, y - 1, INK[1])
        P.put(img, x - 2 - length, y, INK[1]); P.put(img, x - 2 - length, y - 1, INK[1])


def swag_tags(img, x0, x1, y, kinds, seed, sag=3, drops=None):
    """A chain swagged from (x0, y) to (x1, y) with blank tags hanging from
    it at even spacing; ``drops`` gives each tag's extra chain length."""
    P.chain(img, x0, y, x1, y, sag=sag, seed=seed)
    P.rivet(img, x0 - 1, y - 1, 'gold', 3); P.rivet(img, x1 - 1, y - 1, 'gold', 3)
    n = len(kinds)
    for i, kind in enumerate(kinds):
        t = (i + 1) / (n + 1)
        cx = round(x0 + (x1 - x0) * t)
        cy = round(y + sag * 4 * t * (1 - t)) + 2
        d = (drops or [2] * n)[i]
        hang_tag(img, cx, cy, cy + d, kind, short=(i % 2 == 1), seed=seed + i)


def arch_frame(img, cx, top, rad, seed=0, legs=0, ramp=STONE):
    """An open stone arch (voussoirs only, no fill) of radius ``rad`` whose
    crown is at ``top``; ``legs`` extends 3 px jambs down from the spring."""
    import math
    spring = top + rad
    for yy in range(top - 1, spring + 1):
        for xx in range(cx - rad - 1, cx + rad + 2):
            d = math.hypot(xx - cx, yy - spring)
            if rad - 2.6 < d <= rad + 0.5:
                seg = int((math.degrees(math.atan2(spring - yy, xx - cx)) + 180) // 20)
                col = ramp[2] if seg % 2 else ramp[1]
                if d > rad - 0.6:
                    col = INK[1]
                elif d <= rad - 1.9:
                    col = ramp[3] if xx <= cx else ramp[1]
                P.put(img, xx, yy, col)
    P.sprite(img, cx - 1, top - 1, ['oqo', 'oqo', 'opo'])
    for side in (-1, 1):
        x0 = cx - rad if side < 0 else cx + rad - 2
        for yy in range(spring + 1, spring + 1 + legs):
            P.put(img, x0, yy, INK[1] if side < 0 else ramp[1])
            P.put(img, x0 + 1, yy, ramp[2] if (yy // 4) % 2 else ramp[1])
            P.put(img, x0 + 2, yy, ramp[1] if side < 0 else INK[1])
            if side < 0:
                P.put(img, x0 - 1 + 0, yy, INK[1])


def pedestal(img, cx, y, w_cap=28, w_shaft=16, h_shaft=18):
    """A stone pedestal: capital (4 rows), shaft, plinth (4 rows). (cx, y) is
    the centre of the capital's top row. Returns the plinth bottom y."""
    xc = cx - w_cap // 2
    P.ink_outline(img, (xc, y, w_cap, 4), 'ink_1', radius=1, heavy='b', fill_colour=STONE[2])
    P.hline(img, xc + 1, xc + w_cap - 2, y + 1, STONE[3])
    P.hline(img, xc + 2, xc + w_cap - 3, y + 2, STONE[2])
    xs = cx - w_shaft // 2
    for yy in range(y + 4, y + 4 + h_shaft):
        P.put(img, xs, yy, INK[1]); P.put(img, xs + w_shaft - 1, yy, INK[0])
        P.hline(img, xs + 1, xs + w_shaft - 2, yy, STONE[1])
        P.put(img, xs + 1, yy, STONE[3]); P.put(img, xs + 2, yy, STONE[2])
        P.put(img, xs + w_shaft - 2, yy, STONE[0])
        for fx in range(xs + 5, xs + w_shaft - 3, 4):           # flutes
            P.put(img, fx, yy, STONE[0] if yy % 6 else STONE[1])
            P.put(img, fx - 1, yy, STONE[2] if yy % 6 else STONE[1])
    yb = y + 4 + h_shaft
    P.ink_outline(img, (xc - 1, yb, w_cap + 2, 5), 'ink_1', radius=1, heavy='b', fill_colour=STONE[1])
    P.hline(img, xc, xc + w_cap - 1, yb + 1, STONE[3])
    P.hline(img, xc + 1, xc + w_cap - 2, yb + 3, STONE[0])
    P.crack(img, xc + w_cap - 7, yb + 1, 3, seed=cx, colour=STONE[0], branch=False)
    return yb + 5


def clear_rect(img, box):
    x, y, w, h = box
    for yy in range(max(0, y), min(img.height, y + h)):
        for xx in range(max(0, x), min(img.width, x + w)):
            img.putpixel((xx, yy), (0, 0, 0, 0))


# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------

class Out:
    def __init__(self, root=None):
        self.root = Path(root) if root else None
        self.written = {'background': 0, 'button': 0, 'frame': 0}

    def background(self, img, key):
        s = geo.skin(key)
        p = s.background_path if self.root is None else self.root / 'menu' / f'{key}.png'
        C.save_png(img, p)
        self.written['background'] += 1

    def frame(self, img, key, layer_id):
        s = geo.skin(key)
        p = s.frame_path(layer_id) if self.root is None else self.root / 'frames' / key / f'{layer_id}.png'
        C.save_png(img, p)
        self.written['frame'] += 1

    def states(self, states, key, button_id):
        C.save_button_states(states, key, button_id, root=self.root)
        self.written['button'] += len(states)


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def touch_button(img, key, b, seed):
    """Hand touches on top of the shared grammar, kept clear of lettering:
    the auction family's gold replaces iron on the vellum strips' rivets,
    blood gems are set in the primary plates' rims and the balance tablet
    gets an incised fleur under its coins."""
    kind = C.button_kind(b)
    bx, by, bw, bh = b.body.tuple()
    if kind == 'secondary':
        cy = by + (bh - 3) // 2
        for rx in (bx + 2, bx + bw - 5):
            if P.get(img, rx + 1, cy + 1)[:3] == IRON[2]:
                P.rivet(img, rx, cy, 'gold', 3)
    elif kind == 'primary' and bh < 30:
        cx = bw // 2
        P.sprite(img, bx + cx - 2, by, ['OttO', 'Osro', '.OO.'])
    elif kind == 'primary':
        cx = bw // 2
        P.sprite(img, bx + cx - 2, by, ['OttO', 'Osro', '.OO.'])
        P.sprite(img, bx + cx - 2, by + bh - 3, ['.OO.', 'Otro', 'OrrO'])
        P.put(img, bx + bw - 7, by + bh - 6, IRON[0]); P.put(img, bx + bw - 8, by + bh - 7, IRON[0])
    elif b.icon == 'balance' and bh > 36:
        # an incised fleur (cut into the stone: dark strokes, lit lower edge)
        P.sprite(img, bx + (bw - 7) // 2, by + 52,
                 ['...n...', '..npn..', '.n.n.n.', 'n..n..n', '...n...', '.nnnnn.', '.qqqqq.'],
                 {'n': STONE[1], 'p': STONE[2], 'q': STONE[3]})
    elif kind == 'danger' and bw >= 54:
        P.hline(img, bx + 2, bx + bw - 3, by + bh - 2, BLOOD[0])


def paint_buttons(key, out, seed):
    s = geo.skin(key)
    for b in s.buttons:
        normal = C.paint_button(key, b.id, seed=seed + len(b.id))
        touch_button(normal, key, b, seed)
        C.finish_button(normal, key, b.id)
        out.states(C.button_states(normal, key, b.id), key, b.id)


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def niche_market(img, key, seed):
    """Static right column 17/26/35/44 of the market: a stone niche
    x 155..169, y 35..106. A bell hangs across the 17/26 seam, a candle clock
    stands on a ledge over the 26/35 seam, the screen's prop rests on a ledge
    over the 35/44 seam and a blank tag hangs below it."""
    x, y, w, h = 155, 35, 15, 72
    recess(img, (x, y, w, h), seed, course=6)
    cx = x + w // 2
    hook(img, cx, y + 2)
    P.chain(img, cx, y + 5, cx, y + 7, seed=seed, shadow=None)
    bell(img, cx, y + 7)                                   # y 42..54
    ledge(img, x + 1, 70, w - 2, brackets=False)
    fx, fy = candle_clock(img, x + 4, 59, height=8, seed=seed)
    ledge(img, x + 1, 90, w - 2, brackets=False)
    prop = PROP[key]
    if prop == 'ledger':
        icons.draw_motif(img, 'ledger', x + 1, 79)
    elif prop == 'lens':
        P.sprite(img, x + 3, 78, LENS_STAND)
    else:
        icons.draw_motif(img, 'writ', x + 1, 81)
    P.chain(img, x + 10, 95, x + 10, 95, seed=seed + 3, shadow=None)
    tag(img, x + 7, 96, 'blood', short=True)
    P.moss_tuft(img, x + 2, 94, 3, seed=seed)
    P.glow(img, fx, fy + 2, 11, 'ember')
    if prop == 'lens':
        P.glow(img, x + 7, 82, 7, 'soul')


def paint_market_background(key, seed):
    img = C.base_background(key, seed=seed)
    niche_market(img, key, seed)
    # the bottom margin under the hotbar: a gold flourish and a wax drip
    s = geo.skin(key)
    H = s.height
    P.gold_filigree(img, s.width // 2 - 5, H - 4, 'flourish')
    C.finish_background(img, key)
    return img


def paint_watchlist_background(key, seed):
    img = C.base_background(key, seed=seed)
    # --- top row (static slots 0-8): an iron rail hung with blank tags at
    #     every cell seam, long and short in turn
    recess(img, (6, 15, 164, 17), seed, course=5, moss=0.0)
    rail_y = 16
    P.hline(img, 7, 168, rail_y - 1, INK[0])
    P.hline(img, 7, 168, rail_y, IRON[2])
    P.hline(img, 7, 168, rail_y + 1, IRON[0])
    P.hline(img, 7, 168, rail_y + 2, INK[0])
    P.highlight_edge(img, (7, rail_y, 162, 2), IRON[3], 't', broken=5, seed=seed)
    xs = [25, 43, 61, 79, 97, 115, 133, 151]
    kinds = ['blood', 'vellum', 'blood', 'vellum', 'blood', 'vellum', 'blood', 'vellum']
    for i, (tx, kind) in enumerate(zip(xs, kinds)):
        short = i % 3 == 1
        drop = 2 if short else 0
        hang_tag(img, tx, rail_y + 2, rail_y + 3 + drop, kind, short=short, seed=seed + i)
    for rx in (8, 52, 88, 124, 166):
        P.rivet(img, rx - 1, rail_y - 1, 'gold', 3)
    # --- left column (static 9/18/27/36): the watchman's lantern on a bracket
    recess(img, (6, 33, 16, 74), seed + 1, course=6)
    bracket_arm(img, 7, 40, 8, right=True)
    P.chain(img, 15, 42, 15, 47, seed=seed + 2, shadow=None)
    P.sprite(img, 10, 48, LANTERN)
    P.glow(img, 15, 55, 15, 'ember')
    ledge(img, 8, 88, 12, brackets=True)
    icons.draw_motif(img, 'key', 8, 81)
    P.moss_tuft(img, 9, 92, 4, seed=seed)
    P.chain(img, 17, 93, 17, 93, seed=seed, shadow=None)
    tag(img, 14, 94, 'blood', short=True)
    # --- right column (static 17/26/35/44): chains with blank tags
    recess(img, (154, 33, 16, 74), seed + 2, course=6)
    hook(img, 158, 35)
    hook(img, 166, 35)
    P.chain(img, 158, 38, 158, 66, seed=seed + 3, shadow=None)
    tag(img, 155, 67, 'blood')
    P.chain(img, 166, 38, 166, 50, seed=seed + 4, shadow=None)
    tag(img, 163, 51, 'vellum', short=True)
    P.chain(img, 166, 62, 166, 84, seed=seed + 5, shadow=None)
    P.hline(img, 163, 168, 61, IRON[1])
    tag(img, 163, 85, 'blood', short=True)
    P.moss_tuft(img, 156, 101, 5, seed=seed + 1)
    # the base sockets must stay framed above the recesses
    s = geo.skin(key)
    tband, iband = C.bands(key)
    P.socket_well(img, P.merge_holes(s.content_slots), protect=[tband.tuple(), iband.tuple()])
    H = s.height
    P.gold_filigree(img, s.width // 2 - 5, H - 4, 'flourish')
    C.finish_background(img, key)
    return img


SOUL_RUNE = ['..l..', '.lkl.', 'lkLkl', '.lkl.', '..l..']


def paint_confirm_background(key, seed):
    img = C.base_background(key, seed=seed)
    s = geo.skin(key)
    # the review alcove: shadowed masonry from under the title to the buttons
    recess(img, (6, 15, 164, 92), seed, course=7, moss=0.08)
    # floor ledge across the alcove
    P.fill(img, (7, 101, 162, 5), STONE[2])
    P.hline(img, 7, 168, 101, STONE[3])
    P.hline(img, 7, 168, 105, STONE[0])
    P.hline(img, 7, 168, 100, INK[1])
    for fx in range(15, 168, 23):
        P.put(img, fx, 102, STONE[1]); P.put(img, fx + 1, 103, STONE[1])
    # iron rail under the title; blank banners and tags hang from it
    P.hline(img, 8, 167, 17, IRON[2]); P.hline(img, 8, 167, 18, INK[0]); P.hline(img, 8, 167, 16, INK[0])
    P.highlight_edge(img, (8, 17, 160, 1), IRON[3], 't', broken=5, seed=seed)
    P.banner(img, 12, 20, 11, 26, BLOOD, seed, emblem=None, rod=False)
    P.banner(img, 150, 20, 11, 22, BLOOD, seed + 1, emblem=None, rod=False)
    for bx in (12, 22, 150, 160):
        P.put(img, bx, 19, IRON[1])
    hang_tag(img, 82, 19, 26, 'vellum', seed=seed + 7)
    hang_tag(img, 91, 19, 21, 'blood', short=True, seed=seed + 8)
    swag_tags(img, 9, 33, 54, ['vellum', 'blood'], seed + 9, sag=3, drops=[2, 1])
    # the featured socket: a dark arched shrine with a soul rune over slot 20,
    # a fluted pedestal below
    cx = 52
    for yy in range(34, 50):
        for xx in range(cx - 13, cx + 14):
            if (xx - cx) ** 2 + (yy - 47) ** 2 <= 13 ** 2 + 6:
                P.put(img, xx, yy, INK[1])
    for xx in range(39, 65):
        for yy in range(47, 75):
            P.put(img, xx, yy, INK[1])
    arch_frame(img, cx, 32, 15, seed, legs=0)
    for jx, lit in ((36, True), (65, False)):
        for yy in range(48, 75):
            P.put(img, jx, yy, STONE[3] if lit else STONE[1])
            P.put(img, jx + 1, yy, STONE[2] if (yy // 4) % 2 else STONE[1])
            P.put(img, jx + 2 if lit else jx - 1, yy, INK[1])
    P.sprite(img, cx - 2, 38, SOUL_RUNE)
    for (sx, sy) in ((cx - 5, 41), (cx + 5, 42), (cx - 8, 45), (cx + 8, 44), (cx - 1, 45), (cx + 2, 36)):
        P.put(img, sx, sy, SOUL[0])
    pedestal(img, cx, 76, w_cap=30, w_shaft=16, h_shaft=15)
    # candles flanking the pedestal on iron prickets
    f1 = candle_clock(img, 29, 86, height=9, seed=seed, holder='iron')
    f2 = P.candle(img, 72, 88, height=7, lit=True, holder='iron', seed=seed + 1)
    # left: the gavel resting on the auction block
    gavel_block(img, 9, 91, seed=seed, w=17)
    # right of the plate: a candle clock on a sconce, the sealed docket on a ledge
    ledge(img, 153, 82, 15, brackets=True)
    icons.draw_motif(img, 'writ', 154, 72)
    fx, fy = candle_clock(img, 159, 44, height=11, seed=seed + 2)
    P.sprite(img, 157, 58, ['occcco', '.obao.', '..oo..', '..oa..', '...o..'])
    # bell on a chain in the space above the plate
    P.chain(img, 124, 19, 124, 31, seed=seed + 3, shadow=None)
    bell(img, 124, 32)
    # iron mount behind the Confirm plate (its corners show the mount)
    P.ink_outline(img, (95, 51, 58, 40), 'ink_0', radius=2, fill_colour=IRON[0])
    P.bevel(img, (96, 52, 56, 38), IRON[1], INK[1])
    for g in (f1, f2, (fx, fy)):
        P.glow(img, g[0], g[1] + 2, 12, 'ember')
    # static bottom-left cells (45-47): a shelf with the closed ledger,
    # the sealed docket and a candle stub
    P.fill(img, (7, 106, 54, 1), INK[1])
    ledge(img, 10, 119, 48, brackets=False)
    cs = P.candle(img, 15, 112, height=5, lit=True, holder=None, seed=seed + 4)
    icons.draw_motif(img, 'ledger', 22, 108)
    P.sprite(img, 38, 112, ['.ooooooo.', 'oyyyyyyxo', 'oxxxxxxwo', 'oxwwwwxwo', 'ooooooooo'])
    P.wax_seal(img, 46, 114, 3, BLOOD, seed)
    P.glow(img, cs[0], cs[1] + 2, 9, 'ember')
    # re-frame the socket over the alcove
    tband, iband = C.bands(key)
    P.socket_well(img, P.merge_holes(s.content_slots), protect=[tband.tuple(), iband.tuple()])
    P.gold_filigree(img, s.width // 2 - 5, s.height - 4, 'flourish')
    C.finish_background(img, key)
    return img


def paint_duration_background(key, seed):
    img = C.base_background(key, seed=seed)
    s = geo.skin(key)
    # static slot 13 (x 79..96, y 35..52): a small round-headed niche between
    # the 12 and 15 day strips, an hourglass standing on its sill
    recess(img, (79, 35, 18, 18), seed, course=5, moss=0.0)
    for yy in range(36, 40):
        for xx in range(80, 96):
            if (xx - 87.5) ** 2 + (yy - 42) ** 2 > 7.5 ** 2:
                P.put(img, xx, yy, STONE[1] if (xx + yy) % 5 else STONE[2])
    P.sprite(img, 86, 35, ['oqo', 'opo'])
    P.sprite(img, 84, 36, HOURGLASS)
    P.hline(img, 81, 94, 49, STONE[3]); P.hline(img, 81, 94, 50, STONE[1])
    P.hline(img, 80, 95, 51, INK[0])
    # static slots 18-20 (x 7..60, y 53..70): a shelf scene - candle clock,
    # hourglass, the gavel at rest, a sealed writ
    recess(img, (6, 53, 56, 19), seed + 1, course=6, moss=0.0)
    ledge(img, 8, 66, 52, brackets=False)
    fx, fy = candle_clock(img, 10, 57, height=6, seed=seed)
    P.sprite(img, 17, 53, HOURGLASS)
    P.sprite(img, 28, 59, GAVEL)
    icons.draw_motif(img, 'writ', 46, 57)
    P.glow(img, fx, fy + 2, 13, 'ember')
    P.gold_filigree(img, s.width // 2 - 5, s.height - 4, 'flourish')
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def frame_strips(img, a, seed):
    """Chains from the corners to the plaque; swags along the bottom strip."""
    H, W = a.h, a.w
    P.chain(img, 12, 4, W // 2 - 22, 4, sag=2, seed=seed + 11)
    P.chain(img, W // 2 + 21, 4, W - 13, 4, sag=2, seed=seed + 12)
    for x0, x1 in ((8, 120), (136, W - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3); P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur')


def frame_prop(img, key, cx, top, bottom, seed):
    """The screen's own prop resting on the sill of the frame's arch niche
    (interior from ``top`` to ``bottom``), under a small hanging lamp."""
    P.chain(img, cx, top + 1, cx, top + 4, seed=seed, shadow=None)
    icons.draw_motif(img, 'lantern', cx - 4, top + 5)
    prop = PROP.get(key)
    if prop == 'ledger':
        P.sprite(img, cx - 7, bottom - 11, OPEN_LEDGER)
    elif prop == 'lens':
        icons.draw_motif(img, 'mirror', cx - 5, bottom - 11)
    elif prop == 'writ':
        P.sprite(img, cx - 6, bottom - 11, SEALED_WRIT)
    return cx, top + 10


def paint_market_frame(key, seed):
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    L, R = lp.x, rp.x
    # ---- left panel ----------------------------------------------------
    P.chain(img, L + 9, 9, L + 9, 13, seed=seed, shadow=None)
    P.chain(img, L + 29, 9, L + 29, 13, seed=seed + 1, shadow=None)
    C.side_banner(img, geo.Rect(L + 4, 0, 32, 0), y=15, seed=seed, ramp=BLOOD, crest='chevron', h=36)
    # the bell on its bracket
    bracket_arm(img, L + 4, 62, 14, right=True)
    P.chain(img, L + 19, 64, L + 19, 69, seed=seed + 2, shadow=None)
    bell(img, L + 19, 70)
    # sconce with ember light
    fx, fy = sconce(img, L + 21, 98, seed)
    P.glow(img, fx, fy + 2, 13, 'ember')
    # the auction block on a ledge: gavel resting on stone
    ledge(img, L + 3, 150, 34)
    gavel_block(img, L + 3, 139, seed=seed, w=26)
    cfx, cfy = P.candle(img, L + 33, 141, height=7, lit=True, holder='iron', seed=seed)
    P.glow(img, cfx, cfy + 3, 12, 'ember')
    P.moss_tuft(img, L + 9, 155, 5, seed=seed)
    # a swag of blank tags
    swag_tags(img, L + 5, L + 34, 176, ['blood', 'vellum', 'blood'], seed, sag=3, drops=[1, 3, 1])
    P.crack(img, L + 30, 202, 8, seed=seed, colour=STONE[0], light=STONE[3])
    icons.draw_motif(img, 'bone', L + 5, H - 20)
    # ---- right panel ---------------------------------------------------
    swag_tags(img, R + 6, R + 33, 12, ['vellum', 'blood', 'vellum'], seed + 5, sag=2, drops=[2, 1, 2])
    # arch niche with the screen's prop
    P.arch_niche(img, (R + 8, 36, 24, 34), seed=seed)
    lx, ly = frame_prop(img, key, R + 19, 38, 69, seed)
    P.glow(img, lx, ly, 14, 'ember')
    if PROP.get(key) == 'lens':
        P.glow(img, lx, 63, 12, 'soul')
    ledge(img, R + 6, 70, 28)
    P.moss_tuft(img, R + 12, 75, 5, seed=seed + 2)
    # candle clock and hourglass on a ledge, warm light
    ledge(img, R + 4, 112, 32)
    fx, fy = candle_clock(img, R + 8, 96, height=13, seed=seed + 3)
    P.sprite(img, R + 16, 99, HOURGLASS)
    icons.draw_motif(img, 'coin_stack', R + 27, 104)
    P.glow(img, fx, fy + 2, 12, 'ember')
    # a second banner, hung from a hook
    hook(img, R + 20, 128)
    P.chain(img, R + 20, 131, R + 20, 134, seed=seed + 4, shadow=None)
    C.side_banner(img, geo.Rect(R + 4, 0, 32, 0), y=136, seed=seed + 1, ramp=BLOOD, crest='key', h=30)
    # lantern and gargoyle at the foot
    icons.draw_motif(img, 'brazier', R + 5, 180)
    ledge(img, R + 4, 189, 14)
    P.glow(img, R + 10, 181, 11, 'ember')
    icons.draw_motif(img, 'gargoyle', R + 22, H - 28)
    P.crack(img, R + 33, 160, 7, seed=seed + 5, colour=STONE[0], light=STONE[3])
    frame_strips(img, a, seed)
    C.finish_frame(img, key, a.id)
    return img


def paint_watchlist_frame(key, seed):
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, a.id, seed=seed, heading=True)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    L, R = lp.x, rp.x
    # left: the watch post - a lantern on a long chain, bell, tags
    bracket_arm(img, L + 4, 16, 18, right=True)
    P.chain(img, L + 23, 18, L + 23, 32, seed=seed, shadow=None)
    P.sprite(img, L + 18, 33, LANTERN)
    P.glow(img, L + 23, 40, 16, 'ember')
    swag_tags(img, L + 5, L + 34, 66, ['blood', 'vellum', 'blood'], seed, sag=3, drops=[3, 1, 4])
    hook(img, L + 12, 100)
    P.chain(img, L + 12, 103, L + 12, 113, seed=seed + 1, shadow=None)
    tag(img, L + 9, 114, 'blood')
    hook(img, L + 27, 100)
    P.chain(img, L + 27, 103, L + 27, 110, seed=seed + 2, shadow=None)
    tag(img, L + 24, 111, 'vellum')
    ledge(img, L + 5, 150, 30)
    gavel_block(img, L + 8, 141, seed=seed, w=22)
    fx, fy = sconce(img, L + 20, 172, seed)
    P.glow(img, fx, fy + 2, 12, 'ember')
    icons.draw_motif(img, 'bone', L + 6, H - 20)
    # right: a tall chain of tags, a candle clock, the bell
    C.side_banner(img, geo.Rect(R + 4, 0, 32, 0), y=15, seed=seed + 1, ramp=BLOOD, crest='moon', h=34)
    for i, (cx, top, ln, kind) in enumerate(((R + 9, 58, 30, 'blood'), (R + 20, 58, 12, 'vellum'),
                                              (R + 31, 58, 22, 'blood'))):
        hook(img, cx, top)
        P.chain(img, cx, top + 3, cx, top + 3 + ln, seed=seed + 10 + i, shadow=None)
        tag(img, cx - 3, top + 4 + ln, kind, short=(i == 1))
    ledge(img, R + 6, 136, 28)
    fx, fy = candle_clock(img, R + 12, 120, height=13, seed=seed + 3)
    icons.draw_motif(img, 'ledger', R + 18, 125)
    P.glow(img, fx, fy + 2, 12, 'ember')
    bracket_arm(img, R + 36, 160, 10, right=False)
    P.chain(img, R + 25, 162, R + 25, 167, seed=seed + 4, shadow=None)
    bell(img, R + 25, 168)
    icons.draw_motif(img, 'gargoyle', R + 6, H - 28)
    frame_strips(img, a, seed)
    C.finish_frame(img, key, a.id)
    return img


def paint_menu_frame(key, seed):
    """auction_confirm (238 tall) and auction_duration (184 tall)."""
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, a.id, seed=seed, heading=True)
    L, R = a.left_panel.x, a.right_panel.x
    H = a.h
    tall = H > 200
    # left: banner, the auction block, sconce
    P.chain(img, L + 9, 9, L + 9, 13, seed=seed, shadow=None)
    P.chain(img, L + 29, 9, L + 29, 13, seed=seed + 1, shadow=None)
    C.side_banner(img, geo.Rect(L + 4, 0, 32, 0), y=15, seed=seed, ramp=BLOOD, crest='chevron', h=34)
    fx, fy = sconce(img, L + 21, 62, seed)
    P.glow(img, fx, fy + 2, 13, 'ember')
    ledge(img, L + 5, 108, 30)
    gavel_block(img, L + 8, 99, seed=seed, w=22)
    if tall:
        swag_tags(img, L + 5, L + 34, 130, ['blood', 'vellum', 'blood'], seed, sag=3, drops=[1, 3, 1])
        P.arch_niche(img, (L + 9, 168, 22, 30), seed=seed)
        icons.draw_motif(img, 'brazier', L + 14, 186)
        P.glow(img, L + 19, 186, 10, 'ember')
        ledge(img, L + 7, 199, 26)
        icons.draw_motif(img, 'bone', L + 5, H - 20)
    else:
        P.moss_tuft(img, L + 9, 113, 5, seed=seed)
        swag_tags(img, L + 5, L + 34, 128, ['blood', 'vellum', 'blood'], seed, sag=2, drops=[1, 2, 1])
        P.crack(img, L + 30, 158, 7, seed=seed, colour=STONE[0], light=STONE[3])
    # right: bell, candle clock and the sealed docket, gargoyle
    bracket_arm(img, R + 36, 14, 14, right=False)
    P.chain(img, R + 21, 16, R + 21, 21, seed=seed + 2, shadow=None)
    bell(img, R + 21, 22)
    ledge(img, R + 4, 66, 32)
    fx, fy = candle_clock(img, R + 7, 50, height=13, seed=seed + 3)
    icons.draw_motif(img, 'writ', R + 14, 56)
    P.glow(img, fx, fy + 2, 12, 'ember')
    P.moss_tuft(img, R + 22, 71, 6, seed=seed + 3)
    if tall:
        C.side_banner(img, geo.Rect(R + 4, 0, 32, 0), y=90, seed=seed + 1, ramp=BLOOD, crest='key', h=30)
        P.chain(img, R + 10, 132, R + 10, 142, seed=seed + 6)
        icons.draw_motif(img, 'lantern', R + 6, 143)
        P.glow(img, R + 10, 148, 11, 'ember')
        ledge(img, R + 6, 180, 28)
        P.sprite(img, R + 15, 166, HOURGLASS)
        icons.draw_motif(img, 'gargoyle', R + 22, H - 28)
    else:
        swag_tags(img, R + 6, R + 33, 92, ['vellum', 'blood', 'vellum'], seed + 5, sag=2, drops=[2, 1, 2])
        ledge(img, R + 6, 140, 28)
        P.sprite(img, R + 15, 126, HOURGLASS)
        icons.draw_motif(img, 'gargoyle', R + 22, H - 28)
    frame_strips(img, a, seed)
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def paint_skin(key, out):
    seed = SEEDS[key]
    if key in MARKET:
        bg, fr = paint_market_background(key, seed), paint_market_frame(key, seed)
    elif key == 'auction_watchlist':
        bg, fr = paint_watchlist_background(key, seed), paint_watchlist_frame(key, seed)
    elif key == 'auction_confirm':
        bg, fr = paint_confirm_background(key, seed), paint_menu_frame(key, seed)
    else:
        bg, fr = paint_duration_background(key, seed), paint_menu_frame(key, seed)
    out.background(bg, key)
    out.frame(fr, key, geo.skin(key).layer().id)
    paint_buttons(key, out, seed)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', type=Path, help='write into DIR laid out like textures/ instead of pack-source')
    args = ap.parse_args(argv)
    out = Out(args.out_root)
    for key in args.skin or SKINS:
        paint_skin(key, out)
        print('painted', key)
    w = out.written
    print(f"wrote {w['background']} backgrounds, {w['button']} button states, {w['frame']} frames")


if __name__ == '__main__':
    main()
