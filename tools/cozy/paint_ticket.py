#!/usr/bin/env python3
"""Cozy painter "ticket": ticket_valid and ticket_invalid.

    python tools/cozy/paint_ticket.py                    # paint both into pack-source
    python tools/cozy/paint_ticket.py --skin ticket_valid
    python tools/cozy/paint_ticket.py --out-root DIR     # DIR laid out like textures/

Family identity: a stamped airmail postcard lying on the workbench. The single
native display slot (22) is the card's featured window, mounted with brass
photo corners. ticket_valid is tied with red-and-cream baker's twine and closed
with a red wax seal pressed with a tick; ticket_invalid is the same card with
its stamp corner torn away, the twine cut, no seal and cooler ash accents.
No words other than the two button labels.

Deterministic: fixed seeds, no clock, no unseeded randomness. Every pixel is
placed here or by the shared cozy primitives (CC0-1.0 artwork, MIT code).
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
from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD, ramp_of, step  # noqa: E402

SKINS = ('ticket_valid', 'ticket_invalid')
SEED = 41
TRANSPARENT = (0, 0, 0, 0)

# The postcard covers the whole static top area (rows 0-5) of the chest_6 sheet.
CARD = (4, 17, 168, 107)          # x 4..171, y 17..123


# ---------------------------------------------------------------------------
# Small hand-drawn helpers (local to this painter)
# ---------------------------------------------------------------------------

def accents(valid):
    """(stripe A, stripe B, postmark ink) for the airmail border and marks."""
    if valid:
        return BERRY[1], SKY[1], SKY[0]
    return ASH[1], SKY[2], ASH[0]


def airmail_border(img, box, valid, width=3):
    """Diagonal airmail stripes just inside the card outline: A, cream, B, cream."""
    a, b, _ = accents(valid)
    x, y, w, h = box
    seq = [a, a, a, PARCHMENT[3], PARCHMENT[3], b, b, b, PARCHMENT[3], PARCHMENT[3]]
    for yy in range(y + 1, y + h - 1):
        for xx in range(x + 1, x + w - 1):
            d = min(xx - x - 1, yy - y - 1, x + w - 2 - xx, y + h - 2 - yy)
            if d >= width:
                continue
            if P.get(img, xx, yy)[3] == 0:
                continue
            P.put(img, xx, yy, seq[(xx + yy) % len(seq)])
    # thin inner rule inside the stripes
    ix, iy, iw, ih = x + 1 + width, y + 1 + width, w - 2 - 2 * width, h - 2 - 2 * width
    P.hline(img, ix, ix + iw - 1, iy, PARCHMENT[1])
    P.vline(img, ix, iy, iy + ih - 1, PARCHMENT[1])
    P.hline(img, ix, ix + iw - 1, iy + ih - 1, PARCHMENT[0])
    P.vline(img, ix + iw - 1, iy, iy + ih - 1, PARCHMENT[0])


STAMP_PICTURE = [
    # 14 x 17 village-at-dusk vignette: sky, sun, cloud, cottage, hills
    'SSSSSSSSSSSSSS',
    'SSSSSSSSSuuSSS',
    'SScSSSSSuUUuSS',
    'SccccSSSuUUuSS',
    'SSSSSSSSSuuSSS',
    'ssssssssssssss',
    'sssssRsssssccs',
    'ssssRrRsssccccs',
    'sssRrrrRssssss',
    'ssRrrrrrRsssss',
    'ssswwwwwsssggg',
    'gggwewwwggGGGG',
    'GGgwwwdwgGGGGG',
    'GGGwwwdwGGGddG',
    'dGGGGGGGGGdddd',
    'ddddGGGGdddddd',
    'dddddddddddddd',
]


PRESSED_FLOWER = [
    '.s.s.......',
    'sSeSs......',
    '.sSs.......',
    '..g........',
    '..g..ll....',
    '...g.lll...',
    '...ggl.....',
    '....g......',
    '.....g.....',
]


def stamp(img, x, y, valid, seed):
    """Perforated postage stamp, 20 x 23, picture in the middle. No numbers."""
    w, h = 20, 23
    # cast shadow onto the card
    P.hline(img, x + 1, x + w, y + h, PARCHMENT[0])
    P.vline(img, x + w, y + 1, y + h, PARCHMENT[0])
    P.fill(img, (x, y, w, h), PARCHMENT[3])
    # perforations: every other pixel of the outer ring is bitten out
    for i in range(w):
        for j in (0, h - 1):
            if i % 2 == 1:
                P.put(img, x + i, y + j, PARCHMENT[1])
    for j in range(h):
        for i in (0, w - 1):
            if j % 2 == 1:
                P.put(img, x + i, y + j, PARCHMENT[1])
    # picture with an ink frame
    px, py = x + 3, y + 3
    P.ink_outline(img, (px - 1, py - 1, 16, 19), 'ink_2', radius=0)
    if valid:
        key = {'S': SKY[1], 's': SKY[2], 'u': EMBER[2], 'U': EMBER[1], 'c': PARCHMENT[3],
               'R': BERRY[0], 'r': BERRY[1], 'w': PARCHMENT[2], 'e': EMBER[1], 'd': SAGE[0],
               'g': SAGE[2], 'G': SAGE[1]}
    else:   # faded, cooled print
        key = {'S': ASH[1], 's': ASH[2], 'u': PARCHMENT[1], 'U': PARCHMENT[0], 'c': PARCHMENT[2],
               'R': ASH[0], 'r': ASH[1], 'w': PARCHMENT[1], 'e': PARCHMENT[0], 'd': ASH[0],
               'g': ASH[2], 'G': ASH[1]}
    P.sprite(img, px, py, [r[:14] for r in STAMP_PICTURE], key)


def postmark(img, cx, cy, r, colour, seed, waves=3, wave_len=22):
    """Hand-inked circular postmark (double ring, star at the centre) with
    wavy cancellation lines running off to the left. No dates, no words."""
    rng = P._rng(seed, 'postmark')
    for rad, skip in ((r, 7), (r - 2, 5)):
        for yy in range(cy - rad - 1, cy + rad + 2):
            for xx in range(cx - rad - 1, cx + rad + 2):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if rad * rad - rad <= d2 <= rad * rad + rad:
                    if rng.randrange(skip):
                        P.put(img, xx, yy, colour)
    P.sprite(img, cx - 2, cy - 2, ['..o..', '.ooo.', 'ooooo', '.o.o.', '.....'], {'o': colour})
    wave = [0, 0, -1, -1, 0, 0, 1, 1]
    for k in range(waves):
        wy = cy - (waves - 1) * 2 + k * 4
        for i in range(wave_len):
            xx = cx - r - 3 - i
            if rng.randrange(9):
                P.put(img, xx, wy + wave[(i + k * 3) % 8], colour)


def shade(img, x, y):
    """Cast-shadow pixel: darken what is already there (paper two steps, the
    rest one step), so a shadow crossing the airmail stripes stays striped."""
    p = P.get(img, x, y)
    if not p[3]:
        return
    rp = ramp_of(p)
    P.put(img, x, y, step(p, -2 if rp and rp[0] == 'parchment' else -1))


def bakers_twine(img, pts, shadow=PARCHMENT[0], vertical=False, a=BERRY[1], b=PARCHMENT[3]):
    """Red-and-cream striped twine along ``pts`` with a 1 px shadow."""
    for x, y in pts:
        if vertical:
            P.put(img, x + 1, y, shadow)
        else:
            P.put(img, x, y + 1, shadow)
    for i, (x, y) in enumerate(pts):
        P.put(img, x, y, a if (i // 2) % 2 == 0 else b)


def photo_corner(img, x, y, corner):
    """5x5 brass photo-mount corner whose point sits at (x, y)."""
    rows = ['ooooo', 'o32o.', 'o2o..', 'oo...', 'o....']
    P.sprite(img, x - (4 if 'r' in corner else 0), y - (4 if 'b' in corner else 0), rows,
             {'o': INK[1], '3': BRASS[3], '2': BRASS[1]}, flip_x='r' in corner, flip_y='b' in corner)


def tear_corner(layer, card, seed):
    """Tear the top-right corner off the card layer: a ragged diagonal cut with
    a pale fibrous edge. Pixels beyond the tear become transparent on the
    LAYER (the wooden board shows through once it is composited)."""
    x, y, w, h = card
    x0, y1 = x + 128, y + 30           # tear from (x0, top) down to (right, y1)
    right, top = x + w - 1, y
    rng = P._rng(seed, 'tear')
    jog = 0
    edge = []
    n = (right - x0)
    for i in range(n + 1):
        if i % 2 == 0:
            jog = max(-2, min(2, jog + rng.choice((-1, 0, 0, 1))))
        cx = x0 + i
        cy = top + round(i * (y1 - top) / n) + jog
        edge.append((cx, cy))
        for yy in range(top, cy):
            P.put(layer, cx, yy, TRANSPARENT)
    # the columns right of the card edge above y1 remain cut by construction;
    # fibrous edge: cream fibres on the tear, a shaded line just inside
    for cx, cy in edge:
        if P.get(layer, cx, cy)[3]:
            P.put(layer, cx, cy, PARCHMENT[3])
            if P.get(layer, cx - 1, cy + 1)[3] and P.get(layer, cx - 1, cy + 1)[:3] in (PARCHMENT[2], PARCHMENT[3]):
                P.put(layer, cx - 1, cy + 1, PARCHMENT[1])
    # a few fibres sticking out of the tear
    for cx, cy in edge[3::7]:
        P.put(layer, cx + 1, cy - 1, PARCHMENT[3])
    return edge


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def paint_postcard(key, valid):
    s = geo.skin(key)
    x, y, w, h = CARD
    layer = C.new(s.width, s.height)
    P.parchment_panel(layer, CARD, SEED, outline='ink_1', radius=1, fibres=True)
    P.ink_outline(layer, CARD, 'ink_1', radius=1, heavy='br')
    airmail_border(layer, CARD, valid)
    _, _, ink = accents(valid)
    rule = SKY[2] if valid else ASH[2]
    # message side (left): ruled lines, no words
    for k, ly in enumerate(range(y + 11, y + 52, 7)):
        P.stitch_line(layer, x + 9, ly, x + 66 - (6 if k == 5 else 0), ly, rule, 5, 1, phase=k * 2)
    # centre divider above the window
    P.vline(layer, x + 84, y + 8, y + 29, PARCHMENT[0])
    # address side (right): three ruled lines under the stamp
    for k, ly in enumerate((y + 40, y + 47, y + 54)):
        P.hline(layer, x + 104 + (8 if k == 0 else 0), x + 160, ly, rule)
    # stamp + postmark
    stamp(layer, x + 141, y + 7, valid, SEED)
    postmark(layer, x + 135, y + 26, 8, ink, SEED + (0 if valid else 3))
    return layer


def paint_background(key):
    valid = key == 'ticket_valid'
    s = geo.skin(key)
    img = C.base_background(key, seed=SEED)
    layer = paint_postcard(key, valid)
    if not valid:
        tear_corner(layer, CARD, SEED)
    img.alpha_composite(layer)
    x, y, w, h = CARD
    # cast shadow of the card onto the board
    for xx in range(x + 2, x + w + 1):
        if P.get(layer, xx, y + h)[3] == 0:
            P.put(img, xx, y + h, WOOD[0])
    for yy in range(y + 2, y + h + 1):
        if P.get(layer, x + w, yy)[3] == 0:
            P.put(img, x + w, yy, WOOD[0])
    if not valid:
        # shadow under the torn edge
        for yy in range(y, y + 45):
            for xx in range(x + 118, x + w + 1):
                if P.get(layer, xx, yy)[3] == 0 and P.get(layer, xx - 1, yy - 1)[3]:
                    P.put(img, xx, yy, WOOD[0])

    # featured window: the native display slot, mounted with brass photo corners
    holes = P.merge_holes(s.content_slots)
    P.well_frame(img, holes, 'stitched', 3, thread='parch_0')
    hx, hy, hw, hh = holes[0]
    photo_corner(img, hx - 4, hy - 4, 'tl')
    photo_corner(img, hx + hw + 3, hy - 4, 'tr')
    photo_corner(img, hx - 4, hy + hh + 3, 'bl')
    photo_corner(img, hx + hw + 3, hy + hh + 3, 'br')

    # buttons lie on the card: soft shadow below / right of each
    for b in s.buttons:
        for xx in range(b.x + 1, b.x + b.w + 1):
            shade(img, xx, b.y + b.h)
        for yy in range(b.y + 1, b.y + b.h):
            shade(img, b.x + b.w, yy)

    # the message runs on beneath the cancel tag; a pressed flower under redeem
    rule = SKY[2] if valid else ASH[2]
    for k, ly in enumerate((111, 117)):
        P.stitch_line(img, x + 6, ly, x + 50 - 12 * k, ly, rule, 5, 1, phase=k * 3)
    fl = {'s': SKY[2], 'S': SKY[1], 'e': EMBER[2], 'g': SAGE[0], 'l': SAGE[1]} if valid else \
         {'s': ASH[2], 'S': ASH[1], 'e': PARCHMENT[0], 'g': ASH[0], 'l': ASH[1]}
    P.sprite(img, x + 146, y + 92, PRESSED_FLOWER, fl)

    cx = hx + hw // 2           # 88
    sy = 92                     # seal / twine knot row (between the buttons)
    if valid:
        # baker's twine tied round the card, knotted under the seal
        bakers_twine(img, [(xx, sy) for xx in range(x + 1, x + w - 1)])
        bakers_twine(img, [(cx, yy) for yy in range(hy + hh + 4, y + h - 1)], vertical=True)
        # bow tails
        bakers_twine(img, P.line_points(cx - 2, sy + 5, cx - 8, sy + 15))
        bakers_twine(img, P.line_points(cx + 2, sy + 5, cx + 9, sy + 14))
        P.wax_seal(img, cx, sy, 7, BERRY, SEED, drip=True, emblem='check')
    else:
        # the twine has been cut: two frayed ends, no seal
        bakers_twine(img, [(xx, sy) for xx in range(x + 1, cx - 9)], a=ASH[1])
        bakers_twine(img, [(xx, sy) for xx in range(cx + 10, x + w - 1)], a=ASH[1])
        for fx, d in ((cx - 9, -1), (cx + 9, 1)):
            P.put(img, fx, sy - 1, ASH[1]); P.put(img, fx + d, sy + 1, PARCHMENT[3])
        # a pale ring where a seal never set
        for yy in range(sy - 7, sy + 8):
            for xx in range(cx - 7, cx + 8):
                d2 = (xx - cx) ** 2 + (yy - sy) ** 2
                if 38 <= d2 <= 50 and (xx + yy) % 2 == 0:
                    P.put(img, xx, yy, PARCHMENT[0])
    geo.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def mini_stamp(img, x, y, valid):
    """7x8 perforated stamp for the cancel tag's corner."""
    rows = ['p.p.p.p', '.33333.', 'p3ssu3p', '.3sss3.', 'p3ggg3p', '.33333.', 'p.p.p.p']
    key = {'p': PARCHMENT[3], '3': PARCHMENT[3], 'S': SKY[1] if valid else ASH[1],
           'u': EMBER[2] if valid else PARCHMENT[1], 's': SKY[2] if valid else ASH[2],
           'g': SAGE[1] if valid else ASH[1]}
    P.sprite(img, x, y, rows, key)
    P.hline(img, x + 1, x + 7, y + 7, PARCHMENT[0])
    P.vline(img, x + 7, y + 1, y + 6, PARCHMENT[0])


def airmail_hem(img, x0, x1, y0, rows, valid):
    a, b, _ = accents(valid)
    seq = [a, a, PARCHMENT[3], b, b, PARCHMENT[3]]
    for yy in range(y0, y0 + rows):
        for xx in range(x0, x1 + 1):
            P.put(img, xx, yy, seq[(xx + yy) % len(seq)])
    P.hline(img, x0, x1, y0 - 1, PARCHMENT[1])
    P.hline(img, x0, x1, y0 + rows, PARCHMENT[0])


def ticket_notch(img, x, y, side):
    """Ticket-stub notch bitten into the brass plate edge (4 rows tall)."""
    rows = ['o..', '2o.', '2o.', 'o..'] if side == 'l' else ['..o', '.o2', '.o2', '..o']
    rows = ['oo.', 'w2o', 'w2o', 'oo.'] if side == 'l' else ['.oo', 'o2w', 'o2w', '.oo']
    P.sprite(img, x, y, rows, {'o': INK[1], '2': WOOD[1], 'w': WOOD[2]})


def paint_buttons(key):
    valid = key == 'ticket_valid'
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        img = C.paint_button(key, b.id, seed=SEED)
        if b.id == 'cancel':
            # linen luggage tag with an airmail hem and a tiny stamp in the corner
            airmail_hem(img, 6, b.w - 4, b.h - 8, 3, valid)
            mini_stamp(img, b.w - 12, 5, valid)
        elif b.id == 'redeem':
            # the brass plate is cut like a ticket: notches on both short sides
            ticket_notch(img, 2, b.h // 2 - 2, 'l')
            ticket_notch(img, b.w - 5, b.h // 2 - 2, 'r')
            # engraved perforation under the lettering
            for xx in range(12, b.w - 12, 2):
                P.put(img, xx, b.h - 8, BRASS[0])
        geo.finish_button(img, key, b.id)
        out[b.id] = C.button_states(img, key, b.id)
    return out


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

INK_POT = [
    '..ooooo..',
    '..o433o..',
    '..ooooo..',
    '.o2SSS2o.',
    'oi00000So',
    'oippppp0o',
    'oS00000So',
    'oS00000So',
    '.ooooooo.',
]
QUILL = [
    '......oo',
    '.....o3o',
    '....o33o',
    '....o32o',
    '...o332o',
    '...o32o.',
    '..o332o.',
    '..o32o..',
    '.o32o...',
    '.o2o....',
    'oio.....',
    'o.......',
]
RUBBER_STAMP = [
    '..ooooo..',
    '.o44331o.',
    '.o43321o.',
    '..oo2oo..',
    '...o2o...',
    '...o1o...',
    '.ooooooo.',
    '.obbbbBo.',
    'ooooooooo',
    'o3222211o',
    'o2221110o',
    'ooooooooo',
    '.sssssss.',
]
PIGEON = [
    '....ooo......',
    '...o221o.....',
    '..o2e21o.....',
    '.yo2s21o.....',
    '..oss221oooo.',
    '..o22221aaaao',
    '.o22222111aao',
    '.o222211111o.',
    '..o2221111o..',
    '...oooooooo..',
    '.....y..y....',
]
SPOOL = [
    'oooooooo',
    'o433332o',
    '.oRCRCo.',
    '.oCRCRo.',
    '.oRCRCo.',
    '.oCRCRo.',
    '.oRCRCo.',
    'o433332o',
    'oooooooo',
]
WAX_STICK = ['.oo', 'o21', 'o21', 'o21', 'o21', 'o21', 'o21', 'o21', '.oo']
SMOKE = ['.s.', 's..', '.s.', '..s']


def envelope(img, x, y, w, h, seed, sealed=True, tone=None):
    """Envelope: parchment body, inked V flap, a wax seal on the point (or not)."""
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=False)
    mid = x + w // 2
    P.ink_line(img, x + 1, y + 1, mid, y + h // 2 + 1, 'ink_2')
    P.ink_line(img, x + w - 2, y + 1, mid, y + h // 2 + 1, 'ink_2')
    P.ink_line(img, x + 1, y + h - 2, mid - 3, y + h // 2 + 3, 'parch_0')
    P.ink_line(img, x + w - 2, y + h - 2, mid + 3, y + h // 2 + 3, 'parch_0')
    if tone:     # airmail edge along the bottom
        a, b2, _ = tone
        for xx in range(x + 2, x + w - 2):
            P.put(img, xx, y + h - 2, (a, PARCHMENT[3], b2, PARCHMENT[3])[(xx // 2) % 4])
    if sealed:
        P.wax_seal(img, mid, y + h // 2 + 1, 4, BERRY, seed, drip=True)


def mini_card(img, x, y, seed, accent, torn=False):
    """A tiny hanging postcard (11x8) with a stamp and ruled lines."""
    P.parchment_panel(img, (x, y, 11, 8), seed, outline='ink_1', fibres=False)
    P.fill(img, (x + 7, y + 2, 2, 2), accent)
    P.hline(img, x + 2, x + 5, y + 3, SKY[2])
    P.hline(img, x + 2, x + 8, y + 5, SKY[2])
    if torn:
        for j, d in enumerate((2, 3, 2, 1, 2, 1, 0, 0)):
            if d:
                P.fill(img, (x + 11 - d, y + j, d, 1), WOOD[1])
            P.put(img, x + 10 - d, y + j, PARCHMENT[3] if 0 < j < 7 else INK[1])


def clothes_peg(img, x, y):
    P.sprite(img, x, y, ['o2o', 'o3o', 'o2o', '.o.'], {'o': INK[1], '2': WOOD[2], '3': WOOD[3]})


def shelf(img, x, y, w, seed):
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def postbox(img, x, y, valid):
    """Wall postbox (20x30): rounded top, brass letter slot, airmail band."""
    w, h = 20, 30
    body = BERRY if valid else [ASH[0], ASH[0], ASH[1]]
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=3, heavy='br', fill_colour=body[1])
    P.vline(img, x + 2, y + 3, y + h - 4, body[2])
    P.vline(img, x + w - 3, y + 3, y + h - 3, body[0])
    P.hline(img, x + 3, x + w - 4, y + 1, body[2])
    P.hline(img, x + 2, x + w - 3, y + 6, INK[1])                 # cap seam
    P.brass_plate(img, (x + 4, y + 9, w - 8, 5), rivets=False, outline='ink_1')
    P.hline(img, x + 6, x + w - 7, y + 11, INK[0])                # letter slot
    a, b2, _ = accents(valid)
    for xx in range(x + 2, x + w - 2):
        for yy in (y + 17, y + 18):
            P.put(img, xx, yy, (a, PARCHMENT[3], b2, PARCHMENT[3])[((xx + yy) // 2) % 4])
    P.ink_outline(img, (x + 6, y + 21, w - 12, 6), 'ink_1', radius=0, fill_colour=body[0])
    P.put(img, x + w // 2 - 1, y + 23, BRASS[2]); P.put(img, x + w // 2 - 1, y + 24, INK[0])
    P.tack(img, x + w // 2, y + 3, small=True)


def letter_crate(img, x, y, valid, seed):
    """A small wooden crate (24x14) full of letters, three envelopes poking out."""
    a, b2, _ = accents(valid)
    # envelopes behind the front board, each at its own height and lean
    for k, (ex, ey, w, h) in enumerate(((x + 2, y + 4, 9, 10), (x + 8, y, 9, 12), (x + 14, y + 3, 9, 10))):
        P.ink_outline(img, (ex, ey, w, h), 'ink_1', radius=0, fill_colour=PARCHMENT[2 if k != 1 else 3])
        P.ink_line(img, ex + 1, ey + 1, ex + w // 2, ey + 4, 'ink_2')
        P.ink_line(img, ex + w - 2, ey + 1, ex + w // 2, ey + 4, 'ink_2')
        if k == 1:
            for xx in range(ex + 1, ex + w - 1):     # airmail edge on the middle one
                P.put(img, xx, ey + h - 2, (a, PARCHMENT[3], b2, PARCHMENT[3])[(xx // 2) % 4])
            if valid:
                P.put(img, ex + w // 2, ey + 5, BERRY[1]); P.put(img, ex + w // 2 - 1, ey + 5, BERRY[0])
                P.put(img, ex + w // 2, ey + 6, BERRY[0])
    # the crate: two boards with a seam, corner brackets
    P.plank(img, (x, y + 9, 24, 14), WOOD, seed, 'ink_1', radius=1, grain=0.6, heavy='br')
    P.hline(img, x + 1, x + 22, y + 15, WOOD[0])
    P.hline(img, x + 1, x + 22, y + 16, WOOD[3])
    for bx in (x + 2, x + 20):
        P.vline(img, bx, y + 11, y + 20, BRASS[1])
        P.put(img, bx, y + 11, BRASS[3])
        P.put(img, bx, y + 20, BRASS[0])


def torn_piece(img, x, y, seed):
    """The corner torn off the invalid card, pinned to the wall: a right-angled
    scrap (top and right edges carry the airmail stripes, the stamp fragment
    sits in the corner) with a ragged hypotenuse."""
    w, h = 22, 20
    rng = P._rng(seed, 'scrap')
    inside = set()
    jog = 0
    for j in range(h):
        if j % 2 == 0:
            jog = max(-1, min(1, jog + rng.choice((-1, 0, 1))))
        start = max(0, round(j * (w - 3) / (h - 1)) + jog)
        for i in range(start, w):
            inside.add((i, j))
    edge = P._edge_pixels(inside)
    a, b2, _ = accents(False)
    seq = [a, a, PARCHMENT[3], b2, b2, PARCHMENT[3]]
    for (i, j) in inside:
        c = PARCHMENT[2]
        if j <= 2 or i >= w - 3:
            c = seq[(i + j) % len(seq)]
        P.put(img, x + i, y + j, c)
    # stamp fragment in the corner
    for j in range(4, 13):
        for i in range(w - 13, w - 4):
            if (i, j) in inside and (i - 1, j + 1) in inside:
                inner = 5 < j < 12 and w - 11 < i < w - 5
                P.put(img, x + i, y + j, (ASH[2] if j < 9 else ASH[1]) if inner else PARCHMENT[3])
    for (i, j) in edge:
        torn = (i - 1, j) not in inside or (i, j + 1) not in inside
        if j == 0 or i == w - 1:
            P.put(img, x + i, y + j, INK[0] if i == w - 1 else INK[1])
        elif torn:
            P.put(img, x + i, y + j, PARCHMENT[3])
    # shadow beneath the ragged edge
    for (i, j) in edge:
        if (i - 1, j + 1) not in inside:
            q = P.get(img, x + i - 1, y + j + 1)
            if q[3] and q[:3] not in (PARCHMENT[3], PARCHMENT[2]):
                P.put(img, x + i - 1, y + j + 1, WOOD[0])
    P.tack(img, x + w - 5, y + 2)


def paint_frame(key):
    valid = key == 'ticket_valid'
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, a.id, seed=SEED)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    tone = accents(valid)
    tw = (BERRY[1], PARCHMENT[3]) if valid else (ASH[1], PARCHMENT[3])

    # ---- left panel: heading tag, writing shelf, letters, sealing candle, sack
    P.rope(img, lp.x + 5, 12, lp.right - 6, 12, sag=2)
    C.side_tag(img, lp, a.left_heading or a.heading or '', 26, SEED, twine_from=(lp.x + 20, 14))
    shelf(img, lp.x + 4, 62, lp.w - 8, SEED)
    P.sprite(img, lp.x + 10, 44, QUILL, {'o': INK[1], '3': PARCHMENT[3], '2': PARCHMENT[1], 'i': SKY[0]})
    P.sprite(img, lp.x + 6, 53, INK_POT, {'o': INK[1], '4': WOOD[4], '3': WOOD[3], '2': SKY[2],
                                         'S': SKY[1], '0': SKY[0], 'i': PARCHMENT[3], 'p': PARCHMENT[2]})
    P.sprite(img, lp.x + 22, 49, RUBBER_STAMP, {'o': INK[1], '4': WOOD[4], '3': WOOD[3], '2': WOOD[2],
                                               '1': WOOD[1], 'B': BRASS[1], 'b': BRASS[2],
                                               's': SKY[0] if valid else ASH[0], '0': INK[0]})
    # a stack of letters tied with baker's twine
    envelope(img, lp.x + 8, 90, 25, 16, SEED + 2, sealed=False, tone=tone)
    envelope(img, lp.x + 5, 84, 25, 16, SEED + 3, sealed=False, tone=tone)
    envelope(img, lp.x + 7, 77, 25, 16, SEED + 4, sealed=valid, tone=tone)
    bakers_twine(img, [(lp.x + 13, yy) for yy in range(77, 106)], vertical=True, a=tw[0], b=tw[1])
    # sealing: candle and a stick of wax on a shelf
    icons.draw_motif(img, 'candle', lp.x + 9, 117)
    if valid:
        P.lantern_glow_ring(img, lp.x + 11, 118, 8, strength=1)
    else:       # snuffed: no flame, a thin curl of smoke
        P.fill(img, (lp.x + 9, 117, 5, 3), WOOD[2])
        P.sprite(img, lp.x + 10, 115, SMOKE, {'s': ASH[2]})
    P.sprite(img, lp.x + 24, 119, WAX_STICK, {'o': INK[1], '2': BERRY[2] if valid else ASH[2],
                                             '1': BERRY[1] if valid else ASH[1]})
    shelf(img, lp.x + 4, 128, lp.w - 8, SEED + 5)
    # a sprig climbing the lower boards
    P.ink_line(img, lp.x + 30, 138, lp.x + 28, 180, SAGE[0], wobble=1, seed=SEED)
    for k, yy in enumerate((144, 154, 164, 174)):
        P.leaf(img, lp.x + (30 if k % 2 else 22), yy, 'ne' if k % 2 else 'nw', small=k == 3)
    letter_crate(img, lp.x + 7, H - 36, valid, SEED)

    # ---- right panel: postcards on a line, postbox, pigeon, twine spool -----
    P.twine(img, rp.x + 3, 14, rp.right - 4, 14, sag=3)
    for k, (cx, acc) in enumerate(((rp.x + 4, BERRY[1]), (rp.x + 15, SKY[1]), (rp.x + 25, SAGE[1]))):
        yy = 17 + (1 if k == 1 else 0)
        mini_card(img, cx, yy, SEED + k, acc if valid else ASH[1], torn=(not valid) and k == 1)
        clothes_peg(img, cx + 4, yy - 3)
    postbox(img, rp.x + 10, 34, valid)
    # perch with a carrier pigeon (valid) / an empty perch and a lost feather
    P.plank(img, (rp.x + 5, 86, 30, 4), WOOD, SEED + 6, 'ink_1', radius=1, grain=0.3)
    if valid:
        P.sprite(img, rp.x + 12, 75, PIGEON, {'o': INK[1], '2': ASH[2], '1': ASH[1], 'e': INK[0],
                                              's': SAGE[1], 'a': SKY[1], 'y': EMBER[1]})
    else:
        P.sprite(img, rp.x + 16, 80, ['....o', '...o3', '..o3o', '.o3o.', 'o2o..', 'o....'],
                 {'o': INK[1], '3': ASH[2], '2': ASH[1]})
    # spool of twine on a nail, its loose end trailing down
    P.tack(img, rp.x + 20, 100)
    P.sprite(img, rp.x + 16, 103, SPOOL, {'o': INK[1], '4': WOOD[4], '3': WOOD[3], '2': WOOD[1],
                                          'R': tw[0], 'C': tw[1]})
    end = P._sag_points(rp.x + 23, 109, rp.x + 30, 140, -2)
    for i, (xx, yy) in enumerate(end):
        P.put(img, xx, yy, tw[0] if (i // 2) % 2 == 0 else tw[1])
    # pinned sheet of stamps (valid) / the torn-off stamp corner (invalid)
    if valid:
        P.parchment_panel(img, (rp.x + 6, 150, 24, 28), SEED, outline='ink_1', fibres=False)
        for i in range(2):
            for j in range(2):
                sx, sy = rp.x + 8 + i * 11, 153 + j * 12
                ramp = (SKY, BERRY, SAGE, EMBER)[i + 2 * j]
                P.fill(img, (sx, sy, 9, 10), PARCHMENT[3])
                P.fill(img, (sx + 2, sy + 2, 5, 6), ramp[1])
                P.fill(img, (sx + 2, sy + 2, 5, 2), ramp[2])
        P.tack(img, rp.x + 18, 151)
    else:
        torn_piece(img, rp.x + 8, 150, SEED)
    shelf(img, rp.x + 4, H - 40, rp.w - 8, SEED + 7)
    P.mug(img, rp.x + 6, H - 49, SKY if valid else [ASH[0], ASH[1], ASH[2]], steam=valid, seed=SEED)
    envelope(img, rp.x + 18, H - 52, 15, 12, SEED + 8, sealed=False)

    # ---- bottom strip: a rope run between two tacks -------------------------
    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0)
    P.tack(img, 10, H - 5); P.tack(img, a.w - 11, H - 5)
    P.highlight_edge(img, (lp.x + 1, 9, lp.w - 2, H - 18), WOOD[2], 'l', broken=4, seed=SEED)
    P.shadow_edge(img, (rp.x, 9, rp.w - 1, H - 18), INK[1], 'r')
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def paint(key, out_root=None):
    s = geo.skin(key)
    root = Path(out_root) if out_root else None
    bg = paint_background(key)
    C.save_png(bg, s.background_path if root is None else root / 'menu' / f'{key}.png')
    for bid, states in paint_buttons(key).items():
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
    for key in a.skin or SKINS:
        paint(key, a.out_root)
    return 0


if __name__ == '__main__':
    sys.exit(main())
