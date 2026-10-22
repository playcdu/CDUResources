#!/usr/bin/env python3
"""Soulrend painter "trade": every texture of the five TRADE skins.

    python tools/soulrend/paint_trade.py                 # paint into pack-source
    python tools/soulrend/paint_trade.py --skin trade_idle
    python tools/soulrend/paint_trade.py --out-root DIR  # DIR laid out like textures/

Skins: trade_idle, trade_self_ready, trade_other_ready, trade_both_ready
(chest_6, 40 offer wells either side of a stone divider, three footer
buttons, one outer frame each) and trade_money (dispenser, three stacked
buttons, no frame).

Family identity (docs/SOULREND-STYLE-GUIDE.md section 5): two goblets on a
stone table and a chain-link handshake knot between the two sides.

The divider (cells 4/13/22/31/40) is the table's centre post. It carries two
independent, wordless readiness marks: YOU in the upper half, THEM in the
lower half. Each mark is a candle above a goblet above a chain end:

    not ready   cold candle (charred wick, no light), goblet turned upside
                down (dull iron, empty), chain end hanging open on a hook
    ready       lit candle with ember light pooling on the post, goblet set
                upright with dark wine and a gold glint, chain end closed
                into a gold link pulled down (or up) to the knot

Only when both sides are ready do the two gold links interlock: the knot
closes and catches a fleck of soul-light. The outer frame tells the same
story in its side panels (left = you, right = them): each side's wall
sconce is lit only when that side is ready, and the top plaque's chain knot
is closed only on trade_both_ready.

Deterministic (fixed seeds, no clock). Licence: MIT (code); artwork CC0-1.0.
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
from palette import BLOOD, EMBER, GOLD, INK, IRON, SOUL, STONE, UMBER, VELLUM  # noqa: E402

SEED = 23
CHEST_SKINS = ('trade_idle', 'trade_self_ready', 'trade_other_ready', 'trade_both_ready')
MONEY_SKIN = 'trade_money'
ALL_SKINS = CHEST_SKINS + (MONEY_SKIN,)

# (you_ready, them_ready) per chest skin
READY = {
    'trade_idle': (False, False),
    'trade_self_ready': (True, False),
    'trade_other_ready': (False, True),
    'trade_both_ready': (True, True),
}


# ---------------------------------------------------------------------------
# Small hand-drawn helpers (local to this painter)
# ---------------------------------------------------------------------------

# upright goblet, set down with dark wine (9x9)
GOBLET_SET = [
    '.ooooooo.',
    'ohHhhhhgo',
    'oHrsstrgo',
    '.ohrrrgo.',
    '..ohhgo..',
    '...oHo...',
    '...ohgo..',
    '..ohhhgo.',
    '.ooooooo.',
]
# the same goblet turned upside down: cold, dull iron, empty (9x9)
GOBLET_DOWN = [
    '.ooooooo.',
    '..obbbao.',
    '...obao..',
    '...oco...',
    '..ocbao..',
    '.ocbbbao.',
    'ocbbbbbao',
    'occbbbbao',
    '.ooooooo.',
]

# chain end closed into a tarnished-gold link (7 wide x 9 tall; transparent eye)
LINK_GOLD = [
    '..ooo..',
    '.oHHho.',
    'oH...go',
    'oH...go',
    'oh...go',
    'oh...go',
    'oh...go',
    '.ohggo.',
    '..ooo..',
]
# chain end left open: a cold iron link sprung on the right, short of the knot (5x7)
HOOK_OPEN = [
    '.ooo.',
    'odcco',
    'od...',
    'oc...',
    'oc...',
    'obbao',
    '.ooo.',
]
# the knot's iron eye-bolt in the post (both sides anchor here)
EYE_BOLT = [
    '.ooo.',
    'oc.ao',
    'ob.ao',
    '.ooo.',
]


# iron chain links on a dark recess: open (3x4) and edge-on (1x3)
_LINK_OPEN = ['.d.', 'd.c', 'c.b', '.b.']
_LINK_EDGE = ['d', 'c', 'b']
# a slack chain lying coiled on the recess floor (8 x 4)
CHAIN_HEAP = [
    '..d...d.',
    '.d.c.d.c',
    'dc.dcb.b',
    'cbdcb.cb',
]


def vlinks(img, x, y0, y1, phase=0):
    """A straight (taut) iron chain from row y0 to y1 centred on column x."""
    k = phase
    y = y0
    while y <= y1:
        if k % 2 == 0:
            P.sprite(img, x - 1, y, _LINK_OPEN[:max(1, min(4, y1 - y + 1))])
            y += 3
        else:
            P.sprite(img, x, y, _LINK_EDGE[:max(1, min(3, y1 - y + 1))])
            y += 2
        k += 1


def shelf(img, x, y, w):
    """A thin carved stone shelf across the post: lit top, shaded under."""
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 1, STONE[2])
    P.hline(img, x, x + w - 1, y + 2, INK[1])


def readiness_mark(img, cx, top, ready, seed):
    """One side's mark on the post: a candle (flame rows top .. top+3, lit
    only when ready) on a gold dish, a shelf, and a goblet under it (set
    upright with wine when ready, turned down and cold otherwise). Returns
    the row just below the goblet."""
    fx, fy = P.candle(img, cx - 1, top + 4, height=7, lit=ready, holder='gold', seed=seed)
    gy = top + 15
    shelf(img, cx - 4, gy - 1, 10)
    P.sprite(img, cx - 4, gy + 2, GOBLET_SET if ready else GOBLET_DOWN)
    if ready:
        P.glow(img, fx, fy + 3, 9, 'ember')
    return gy + 11


def post_body(img, x0, y0, x1, y1, seed):
    """Hand-cut slate drums: flat stone_1, lit left column, shaded right
    column, a drum joint every 9-12 rows, two chips."""
    P.fill(img, (x0, y0, x1 - x0 + 1, y1 - y0 + 1), STONE[1])
    P.vline(img, x0, y0, y1, STONE[2])
    P.vline(img, x1, y0, y1, STONE[0])
    r = P._rng(seed, 'post')
    y = y0 + r.randint(5, 8)
    while y < y1 - 3:
        P.hline(img, x0, x1, y, STONE[0])
        P.hline(img, x0 + 1, x1 - 1, y + 1, STONE[2])
        y += r.randint(9, 12)


def paint_post(img, you, them, seed):
    """The divider: a slate pillar between the two offer grids carrying the
    independent YOU (upper) and THEM (lower) readiness marks and the knot."""
    x0, x1 = 83, 92           # free columns between the two sockets' iron rings
    y0, y1 = 15, 106
    cx = 87
    post_body(img, x0, y0, x1, y1, seed)
    # capital and plinth: blackened iron bands with a gold rivet
    for (yy, lit) in ((y0, True), (y1 - 3, False)):
        P.hline(img, x0, x1, yy, IRON[2] if lit else IRON[1])
        P.hline(img, x0, x1, yy + 1, IRON[1])
        P.hline(img, x0, x1, yy + 2, INK[1])
        P.put(img, cx, yy + 1, GOLD[2]); P.put(img, cx + 1, yy + 1, GOLD[0])
    P.hline(img, x0, x1, y1, INK[0])
    # --- the knot recess between the two marks ------------------------------
    ry0, ry1 = 45, 73
    P.fill(img, (x0, ry0, x1 - x0 + 1, ry1 - ry0 + 1), INK[1])
    P.hline(img, x0, x1, ry0, STONE[0])            # recess ceiling in shadow
    P.vline(img, x0, ry0, ry1, STONE[0])
    P.vline(img, x1, ry0 + 1, ry1, STONE[3])       # lit far wall
    P.hline(img, x0 + 1, x1, ry1, STONE[3])        # lit floor
    P.sprite(img, cx - 1, ry0 + 1, ['cda', '.b.'])         # ceiling eye-bolt
    ky = (ry0 + ry1) // 2                          # knot centre row (59)
    # --- YOU (upper) and THEM (lower) ---------------------------------------
    readiness_mark(img, cx, 18, you, seed)
    readiness_mark(img, cx, 75, them, seed + 1)
    if you and them:
        vlinks(img, cx, ry0 + 3, ky - 7)
        vlinks(img, cx, ky + 7, ry1 - 2, phase=1)
        P.sprite(img, cx - 3, ky - 2, LINK_GOLD)          # THEM's link (behind)
        P.sprite(img, cx - 3, ky - 7, LINK_GOLD)          # YOU's link (front)
        # THEM's link passes back over YOU's on the right: the knot is closed
        for yy in (ky - 1, ky, ky + 1):
            P.put(img, cx + 2, yy, GOLD[0])
        P.put(img, cx + 3, ky - 1, INK[1]); P.put(img, cx + 3, ky, INK[1])
        # a fleck of soul-light where the oath is bound
        P.put(img, cx, ky, SOUL[2]); P.put(img, cx - 1, ky + 1, SOUL[1])
        return
    if you:           # taut: drawn down to the centre, closed in gold
        vlinks(img, cx, ry0 + 3, ky - 6)
        P.sprite(img, cx - 3, ky - 5, LINK_GOLD)
    else:             # slack: the open link hangs straight off the eye-bolt
        P.sprite(img, cx - 2, ry0 + 3, HOOK_OPEN)
    if them:          # taut: drawn up from the floor to the centre
        P.sprite(img, cx - 1, ry1 - 1, ['.c.'])
        P.sprite(img, cx - 3, ky - 3, LINK_GOLD)
        vlinks(img, cx, ky + 6, ry1 - 2, phase=1)
    else:             # slack: the chain lies coiled on the floor, its end open
        P.sprite(img, cx - 4, ry1 - 4, CHAIN_HEAP)
        P.sprite(img, cx - 2, ry1 - 10, HOOK_OPEN, flip_x=True)


# ---------------------------------------------------------------------------
# Chest backgrounds (trade_idle / self_ready / other_ready / both_ready)
# ---------------------------------------------------------------------------

def paint_chest_background(key):
    s = geo.skin(key)
    you, them = READY[key]
    img = C.base_background(key, seed=SEED)
    paint_post(img, you, them, SEED)
    H, W = s.height, s.width
    # rows under the hotbar socket: a gold flourish, a blood-wax drip, a crack
    P.gold_filigree(img, W // 2 - 5, H - 4, 'flourish')
    P.chain(img, 14, H - 3, 70, H - 3, sag=0, seed=SEED + 5, shadow=None)
    P.chain(img, 106, H - 3, W - 15, H - 3, sag=0, seed=SEED + 6, shadow=None)
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# trade_money background (dispenser): static side panels
# ---------------------------------------------------------------------------

def stone_table(img, x, y, w, leg_h):
    """A carved stone table: slab ``w`` x 4 with its top row at ``y`` (lit
    top, shaded front edge, ink outline heavy below) on two squat legs."""
    for lx in (x + 3, x + w - 6):
        P.ink_outline(img, (lx - 1, y + 3, 5, leg_h + 2), 'ink_1', radius=0, heavy='br', fill_colour=STONE[1])
        P.vline(img, lx, y + 4, y + 3 + leg_h, STONE[2])
        P.vline(img, lx + 2, y + 4, y + 3 + leg_h, STONE[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0, heavy='br', fill_colour=STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.put(img, x + w // 3, y + 1, STONE[1]); P.put(img, x + w // 3 + 1, y + 1, STONE[1])


def alcove(img, box, seed):
    """A recessed slate alcove cut into the umber sheet: masonry inside, an
    ink recess line top/left, a lit sill bottom/right, iron corner brackets."""
    x, y, w, h = box
    P.stone_blocks(img, (x + 1, y + 1, w - 2, h - 2), seed, STONE, course=6, moss=0.12, cracks=0.3)
    P.ink_outline(img, box, 'ink_0', radius=1)
    P.hline(img, x + 1, x + w - 2, y + 1, INK[1])
    P.vline(img, x + 1, y + 1, y + h - 2, INK[1])
    P.hline(img, x + 2, x + w - 2, y + h - 2, STONE[3])
    P.vline(img, x + w - 2, y + 2, y + h - 2, STONE[3])
    C.corner_bracket(img, x - 1, y - 1, 'tl')
    C.corner_bracket(img, x + w - 5, y - 1, 'tr')


def gold_knot(img, cx, cy, closed=True):
    """The family's chain-link handshake knot: two tarnished-gold links
    hanging interlocked (closed) or apart (open), centred at (cx, cy)."""
    if closed:
        P.sprite(img, cx - 2, cy - 1, LINK_GOLD)
        P.sprite(img, cx - 4, cy - 7, LINK_GOLD)
        for yy in (cy, cy + 1):
            P.put(img, cx + 1, yy, GOLD[0])
        P.put(img, cx + 2, cy, INK[1])
    else:
        P.sprite(img, cx - 9, cy - 4, LINK_GOLD)
        P.sprite(img, cx + 2, cy - 4, LINK_GOLD)


def paint_money_background(key=MONEY_SKIN):
    s = geo.skin(key)
    img = C.base_background(key, seed=SEED)      # letters OFFERED MONEY on the title band
    # --- left third: coin scales hanging in an arched niche, the pouch on the sill
    alcove(img, (8, 18, 50, 51), SEED)
    P.arch_niche(img, (17, 22, 25, 39), seed=SEED)
    P.chain(img, 29, 23, 29, 30, seed=SEED, shadow=None)
    icons.draw_motif(img, 'scales', 23, 31)
    fx, fy = P.candle(img, 22, 51, height=6, lit=True, holder='iron', seed=SEED)
    P.glow(img, fx, fy + 3, 10, 'ember')
    P.hline(img, 16, 43, 61, STONE[3]); P.hline(img, 16, 43, 62, STONE[2]); P.hline(img, 16, 43, 63, INK[1])
    icons.draw_icon(img, 'balance', (43, 46, 12, 17))
    # --- right third: two goblets on a stone table under the handshake knot
    alcove(img, (118, 18, 50, 51), SEED + 3)
    P.chain(img, 143, 20, 143, 24, seed=SEED + 4, shadow=None)
    gold_knot(img, 143, 31, closed=True)
    P.put(img, 142, 32, SOUL[2])
    stone_table(img, 123, 52, 41, 11)
    fx, fy = P.candle(img, 136, 45, height=5, lit=True, holder=None, seed=SEED + 2)
    P.glow(img, fx, fy + 2, 12, 'ember')
    icons.draw_motif(img, 'goblet', 125, 43)
    icons.draw_motif(img, 'goblet', 153, 43, flip_x=True)
    icons.draw_motif(img, 'coin_stack', 142, 44)
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

COIN = icons.COIN                                   # 5x5 tarnished coin with ink rim
# a coin incised into a stone tablet: cut edge in shadow top-left (5x5)
COIN_CARVED = ['.nnn.', 'n...p', 'n.n.p', 'n...p', '.ppp.']
# two small interlocked links engraved in gold on the iron plate (5x3)
LINKS_ENGRAVED = ['hh.hh', 'h.H.g', 'gg.gg']
# the same, lit by soul-light once you have sworn (selected)
LINKS_SWORN = {'h': SOUL[1], 'H': SOUL[2], 'g': SOUL[0]}
# a blood-wax gem set in the top rim (5x3) and a gold coin boss (5x3)
GEM_BLOOD = ['.ooo.', 'ostso', '.oro.']
BOSS_COIN = ['.ooo.', 'oHHgo', '.ogo.']


def coin_pinned_strip(key, b):
    """Vellum strip pinned by two gold coins instead of iron rivets."""
    img = C.new(b.w, b.h)
    body = b.body.tuple()
    x, y, w, h = body
    C.secondary_face(img, body, SEED, rivets=False)
    box = (x + 6, y + 2, w - 12, h - 4)               # same text box as the riveted strip
    C.letter(img, b, box, 'ink_0')
    cy = y + (h - 5) // 2
    P.sprite(img, x + 2, cy, COIN)
    P.sprite(img, x + w - 7, cy, COIN)
    return img


def paint_buttons(key):
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        selected_touch = None
        if b.id in ('own_money', 'return', 'decrease'):
            img = coin_pinned_strip(key, b)
        else:
            img = C.paint_button(key, b.id, seed=SEED)
        bx, by, bw, bh = b.body.tuple()
        if b.id == 'ready':
            # the handshake knot engraved either side of the word, a blood
            # seal set in the top rim
            cy = by + (bh - 3) // 2
            spots = ((bx + 6, cy), (bx + bw - 11, cy))
            for (ex, ey) in spots:
                P.sprite(img, ex, ey, LINKS_ENGRAVED)
            P.sprite(img, bx + bw // 2 - 3, by, GEM_BLOOD)

            def selected_touch(im, spots=spots):
                for (ex, ey) in spots:
                    P.sprite(im, ex, ey, LINKS_ENGRAVED, LINKS_SWORN)
        elif b.id == 'other_money':
            cy = by + (bh - 5) // 2
            spots = ((bx + 5, cy), (bx + bw - 10, cy))
            for (ex, ey) in spots:
                P.sprite(img, ex, ey, COIN_CARVED)

            def selected_touch(im, spots=spots):
                for (ex, ey) in spots:
                    P.sprite(im, ex, ey, COIN_CARVED, {'n': SOUL[0], 'p': SOUL[1]})
        elif b.id == 'increase':
            P.sprite(img, bx + bw // 2 - 3, by, BOSS_COIN)
        C.finish_button(img, key, b.id)
        states = C.button_states(img, key, b.id)
        if selected_touch:
            sel = states['selected'].copy()
            selected_touch(sel)
            states['selected'] = C.finish_button(sel, key, b.id)
        out[b.id] = states
    return out


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def ledge(img, x, y, w):
    """A short carved stone ledge on two iron brackets."""
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0)
    for bx in (x + 2, x + w - 4):
        P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


def sconce(img, x, y, lit, seed):
    """Iron wall sconce with a candle; ember light only when lit."""
    P.sprite(img, x - 3, y + 8, ['occcco', '.obao.', '..oo..', '..oa..', '..ob..', '...o..'])
    fx, fy = P.candle(img, x - 1, y, height=6, lit=lit, holder=None, seed=seed)
    if lit:
        P.glow(img, fx, fy + 2, 13, 'ember')


def paint_frame(key):
    s = geo.skin(key)
    a = s.layer()
    you, them = READY[key]
    img = C.base_frame(key, seed=SEED)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    # banners of the two parties: yours on the left, theirs on the right
    P.chain(img, lp.x + 9, 9, lp.x + 9, 13, seed=SEED, shadow=None)
    P.chain(img, lp.x + 29, 9, lp.x + 29, 13, seed=SEED + 1, shadow=None)
    C.side_banner(img, geo.Rect(lp.x + 4, 0, 32, 0), y=15, seed=SEED, ramp=BLOOD, crest='chevron', h=34)
    P.chain(img, rp.x + 9, 9, rp.x + 9, 13, seed=SEED + 2, shadow=None)
    P.chain(img, rp.x + 29, 9, rp.x + 29, 13, seed=SEED + 3, shadow=None)
    C.side_banner(img, geo.Rect(rp.x + 4, 0, 32, 0), y=15, seed=SEED + 1, ramp=BLOOD, crest='key', h=34)
    # readiness sconces: each side's candle burns only once that side is ready
    sconce(img, lp.x + 20, 60, you, SEED)
    sconce(img, rp.x + 20, 60, them, SEED + 1)
    # the stone table, split by the ledger: one goblet each side
    stone_table(img, lp.x + 5, 104, 30, 9)
    icons.draw_motif(img, 'goblet', lp.x + 19, 95)
    icons.draw_motif(img, 'coin_stack', lp.x + 8, 96)
    stone_table(img, rp.x + 5, 104, 30, 9)
    icons.draw_motif(img, 'goblet', rp.x + 8, 95, flip_x=True)
    icons.draw_icon(img, 'balance', (rp.x + 20, 88, 12, 16))
    P.moss_tuft(img, lp.x + 12, 108, 4, seed=SEED)
    P.moss_tuft(img, rp.x + 22, 108, 3, seed=SEED + 1)
    # lower left: the coin scales in an arched niche, a ledger on a ledge
    P.arch_niche(img, (lp.x + 7, 130, 25, 40), seed=SEED)
    P.chain(img, lp.x + 19, 131, lp.x + 19, 141, seed=SEED + 7, shadow=None)
    icons.draw_motif(img, 'scales', lp.x + 13, 142)
    P.hline(img, lp.x + 6, lp.x + 32, 170, STONE[3])
    P.hline(img, lp.x + 6, lp.x + 32, 171, INK[1])
    icons.draw_motif(img, 'coin_stack', lp.x + 10, 162)
    P.sprite(img, lp.x + 22, 165, COIN)
    P.moss_tuft(img, lp.x + 8, 172, 5, seed=SEED + 2)
    ledge(img, lp.x + 7, 196, 26)
    icons.draw_motif(img, 'satchel', lp.x + 14, 186)
    P.crack(img, lp.x + 31, 178, 8, seed=SEED, colour=STONE[0], light=STONE[3])
    icons.draw_motif(img, 'bone', lp.x + 5, H - 20)
    # lower right: chain hanging from the table to a slack loop, a ledge with
    # coins and a ledger, the gargoyle corbel
    P.chain(img, rp.x + 10, 112, rp.x + 10, 150, seed=SEED + 8)
    P.chain(img, rp.x + 10, 150, rp.x + 30, 150, sag=6, seed=SEED + 9)
    P.chain(img, rp.x + 30, 112, rp.x + 30, 150, seed=SEED + 10)
    ledge(img, rp.x + 6, 186, 28)
    icons.draw_motif(img, 'coin_stack', rp.x + 9, 177)
    icons.draw_motif(img, 'ledger', rp.x + 19, 175)
    P.crack(img, rp.x + 6, 160, 9, seed=SEED + 4, colour=STONE[0], light=STONE[3])
    icons.draw_motif(img, 'gargoyle', rp.x + 16, H - 26)
    # top strip: each party's chain runs from its corner to the plaque, where
    # the handshake knot closes only when both are ready
    P.chain(img, 12, 4, a.w // 2 - 22, 4, sag=2, seed=SEED + 11)
    P.chain(img, a.w // 2 + 21, 4, a.w - 13, 4, sag=2, seed=SEED + 12)
    plaque_knot(img, a.w // 2, you, them)
    # bottom strip: chains swagged between rivets, a gold fleur
    for x0, x1 in ((8, 120), (136, a.w - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=SEED + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3); P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur')
    C.finish_frame(img, key, a.id)
    return img


# horizontal chain link for the plaque (6x4): gold when its side is ready
LINK_H = ['.HHhg.', 'H....g', 'h....g', '.hggg.']
_IRON_KEY = {'H': IRON[3], 'h': IRON[2], 'g': IRON[1]}


def plaque_knot(img, cx, you, them):
    """Replace the plaque's fleur with the handshake knot: the left (your)
    link and the right (their) link, gold when that side is ready, iron when
    not; interlocked only when both are ready."""
    P.fill(img, (cx - 12, 2, 24, 4), INK[1])
    if you and them:
        P.sprite(img, cx - 5, 2, LINK_H)
        P.sprite(img, cx - 1, 2, LINK_H)
        P.put(img, cx, 2, GOLD[2]); P.put(img, cx, 3, GOLD[1])     # left link passes over
        P.put(img, cx - 2, 3, SOUL[2])
    else:
        P.sprite(img, cx - 9, 2, LINK_H, None if you else _IRON_KEY)
        P.sprite(img, cx + 3, 2, LINK_H, None if them else _IRON_KEY)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def paint(key, root=None):
    s = geo.skin(key)
    tex = Path(root) if root else None
    written = []
    if key == MONEY_SKIN:
        bg = paint_money_background(key)
    else:
        bg = paint_chest_background(key)
    written.append(C.save_png(bg, (tex / 'menu' / f'{key}.png') if tex else s.background_path))
    for bid, states in paint_buttons(key).items():
        written += C.save_button_states(states, key, bid, root=tex)
    if key != MONEY_SKIN:
        for a in s.art_layers:
            fr = paint_frame(key)
            written.append(C.save_png(fr, (tex / 'frames' / key / f'{a.id}.png') if tex else s.frame_path(a.id)))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', action='append', choices=ALL_SKINS, help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', type=Path, help='write under DIR (laid out like textures/) instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or ALL_SKINS:
        files = paint(key, args.out_root)
        print(f'{key}: {len(files)} files')


if __name__ == '__main__':
    main()
