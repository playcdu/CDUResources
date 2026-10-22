#!/usr/bin/env python3
"""Cozy painter "shopconfig": the chest-shop configuration screens.

    python tools/cozy/paint_shopconfig.py                    # all eight skins -> pack-source
    python tools/cozy/paint_shopconfig.py --skin chest_shop_buy
    python tools/cozy/paint_shopconfig.py --out-root DIR     # DIR laid out like textures/

Skins (background, every button in six states, outer frame):
chest_shop_settings, chest_shop_buy, chest_shop_sell, chest_shop_upgrade,
chest_shop_upgrade_confirm, chest_shop_upgrade_disabled,
chest_shop_listing_enabled, chest_shop_listing_disabled.

Family identity (CHEST SHOP, ember accent): a village shop front. Shop-front
posts flank the controls, hanging shop signs carry a little storefront
pictogram (lit, or shuttered when the listing is off), shelves hold crates,
action tags have an ember-dipped end, read-only cards are parchment notes
pinned with tacks, preset options are tags with a stamped number, primary
plates carry small engraved emblems. Everything is hand-placed from the
sprite strings below; seeds are fixed so the output is deterministic.

Licence: code MIT; sprite designs CC0-1.0.
"""
from __future__ import annotations

import argparse
import sys
import zlib
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import icons  # noqa: E402
import lettering as L  # noqa: E402
import primitives as P  # noqa: E402
from palette import (ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD,  # noqa: E402
                     ramp_of, rgba, step)

SKINS = [
    'chest_shop_settings', 'chest_shop_buy', 'chest_shop_sell', 'chest_shop_upgrade',
    'chest_shop_upgrade_confirm', 'chest_shop_upgrade_disabled',
    'chest_shop_listing_enabled', 'chest_shop_listing_disabled',
]
SEED = 23
OUT_ROOT = None   # set by --out-root: a directory laid out like textures/


def seed_for(*parts):
    return zlib.crc32(':'.join(str(p) for p in parts).encode()) % 9973


# ===========================================================================
# Sprite library (hand-authored, CC0)
# ===========================================================================

K_W = {'o': INK[1], 'O': INK[0], '0': WOOD[0], '1': WOOD[1], '2': WOOD[2], '3': WOOD[3], '4': WOOD[4]}

# X-braced crate, 9x9
CRATE9 = [
    'ooooooooo',
    'o4333332o',
    'o2o222o1o',
    'o22o2o21o',
    'o222o221o',
    'o22o2o21o',
    'o2o222o1o',
    'o1111111o',
    'ooooooooo',
]
# slatted crate, 11x9
SLAT11 = [
    'ooooooooooo',
    'o433333332o',
    'o222222221o',
    'o011111100o',
    'o433333332o',
    'o222222221o',
    'o011111100o',
    'o122222221o',
    'ooooooooooo',
]
# small crate, 7x7
CRATE7 = [
    'ooooooo',
    'o43332o',
    'o2o2o1o',
    'o22o21o',
    'o2o2o1o',
    'o11110o',
    'ooooooo',
]
# open crate with straw, 11x9
OPEN_CRATE = [
    '.s.ss..s.s.',
    'ssSssSsssSs',
    'ooooooooooo',
    'o433333332o',
    'o2o22222o1o',
    'o22o222o21o',
    'o222ooo221o',
    'o111111110o',
    'ooooooooooo',
]
K_OPEN = dict(K_W, s=BRASS[2], S=BRASS[3])

# Storefront pictogram, 15x11: striped ember awning, walls, two windows, door.
STOREFRONT = [
    '..ooooooooooo..',
    '.oEeEeEeEeEeEo.',
    'oEeEeEeEeEeEeEo',
    'oEeEeEeEeEeEeEo',
    '.oEoEoEoEoEoEo.',
    '.o33333333333o.',
    '.o3ww3ddd3ww3o.',
    '.o3ww3ddd3ww3o.',
    '.o3333ddb3333o.',
    '.o2222ddd2222o.',
    'ooooooooooooooo',
]


def storefront_key(mode):
    """'day' (sky windows), 'lit' (warm light inside), 'shut' (boarded)."""
    k = {'o': INK[1], 'E': EMBER[1], 'e': PARCHMENT[3], '3': WOOD[3], '2': WOOD[2], 'b': BRASS[2]}
    if mode == 'lit':
        k.update(w=EMBER[2], d=EMBER[1])
    elif mode == 'shut':
        k.update(E=ASH[1], e=ASH[2], w=WOOD[1], d=WOOD[1], b=ASH[0])
    else:
        k.update(w=SKY[2], d=WOOD[1])
    return k


def storefront(img, x, y, mode='day'):
    P.sprite(img, x, y, STOREFRONT, storefront_key(mode))
    if mode == 'shut':
        # boards nailed across the windows and the door
        for wx in (x + 3, x + 10):
            P.put(img, wx, y + 6, WOOD[3]); P.put(img, wx + 1, y + 7, WOOD[3])
        P.line(img, x + 6, y + 6, x + 8, y + 9, WOOD[3])
        P.line(img, x + 8, y + 6, x + 6, y + 9, WOOD[3])


# Toolbox, 13x10: ember-painted box, brass handle and latch.
TOOLBOX = [
    '....ooooo....',
    '....o...o....',
    '.ooooooooooo.',
    'oEEEEEEEEEEdo',
    'oeeeeebbeeedo',
    'ooooooBBooooo',
    'oeeeeeeeeeedo',
    'oeeeeeeeeeedo',
    'oddddddddddoo',
    'ooooooooooooo',
]
K_TOOLBOX = {'o': INK[1], 'E': EMBER[2], 'e': EMBER[1], 'd': EMBER[0], 'b': BRASS[3], 'B': BRASS[1]}

# Hammer, 7x10 (iron head, wood handle)
HAMMER = [
    'ooooooo',
    'oAAAaao',
    'ooooozo',
    '..o3o..',
    '..o3o..',
    '..o2o..',
    '..o2o..',
    '..o2o..',
    '..o1o..',
    '..ooo..',
]
K_HAMMER = {'o': INK[1], 'A': ASH[2], 'a': ASH[1], 'z': ASH[0], '3': WOOD[4], '2': WOOD[3], '1': WOOD[2]}

# Wrench, 5x11
WRENCH = [
    'o...o',
    'oAoAo',
    'oaAao',
    '.oao.',
    '.oAo.',
    '.oao.',
    '.oAo.',
    '.oao.',
    'oaAao',
    'oA.ao',
    '.o.o.',
]
K_WRENCH = {'o': INK[1], 'A': ASH[2], 'a': ASH[1]}

# Padlock, 7x8 (iron)
PADLOCK = [
    '..ooo..',
    '.oAAao.',
    '.o...o.',
    'ooooooo',
    'oAAAAao',
    'oaaOaao',
    'oaaOazo',
    'ooooooo',
]
K_PADLOCK = {'o': INK[1], 'O': INK[0], 'A': ASH[2], 'a': ASH[1], 'z': ASH[0]}

# Corner cobweb (top-left corner; flip_x for top-right), 6x6: the two
# anchor strands along the corner, a diagonal and one curved catch thread.
COBWEB = [
    'AAAAAA',
    'AA..A.',
    'A.A.A.',
    'A..A..',
    'AAA...',
    'A.....',
]

# Chalk arrow pointing right, 7x5
ARROW_R = ['...cc..', '....cc.', 'ccccccc', '....cc.', '...cc..']

# Steps glyph for the tier shelf / Apply plate (engraved), 9x6
STEPS = ['......###', '......#.#', '...####.#', '...#....#', '####....#', '#########']

# --- small glyphs for lettered controls ('#' = ink / engraving) -------------
G_BACK = ['..##', '.##.', '##..', '.##.', '..##']
G_UP = ['.#.', '###']
G_DOWN = G_UP[::-1]
G_PLUS = ['.#.', '###', '.#.']
G_UPGRADE = ['...#...', '..###..', '.##.##.', '##...##', '...#...', '..###..', '.##.##.']
G_PURSE = ['.#...#.', '..#.#..', '..###..', '.#####.', '#######', '#######', '.#####.']
G_CRATE = ['#######', '##...##', '#.#.#.#', '#..#..#', '#.#.#.#', '##...##', '#######']
G_SHOP = ['#########', '#.#.#.#.#', '.#######.', '.#.....#.', '.#.##..#.', '.#.##..#.', '.#######.']
G_CHECK = ['......#', '.....##', '#...##.', '##.##..', '.###...', '..#....']

# coloured glyphs for cards / tags
I_STATS = ['......ed.', '......ed.', '...ed.ed.', '...ed.ed.', 'ed.ed.ed.', 'ed.ed.ed.', 'ooooooooo']
I_QTY = ['..ooooo..', '..o332o..', '..o221o..', 'ooooooooo', 'o332o332o', 'o221o221o', 'ooooooooo']
I_CRATE = CRATE7
K_GLYPH = {'o': INK[1], 'e': EMBER[1], 'd': EMBER[0], '4': WOOD[4], '3': WOOD[3], '2': WOOD[2],
           '1': WOOD[1], '0': WOOD[0]}

# Rename: an ember quill with an ink nib, 9x9
QUILL = [
    '.......oo',
    '......oeo',
    '.....oeEo',
    '....oeEo.',
    '...oeEo..',
    '..oeEo...',
    '..oEo....',
    '.oOo.....',
    'oO.......',
]
K_QUILL = {'o': INK[1], 'O': INK[0], 'e': EMBER[1], 'E': EMBER[2]}

# Refresh: two chasing arrows, 11x10
REFRESH = [
    '...ooooo...',
    '..o.....o.o',
    '.o.......oo',
    '.o......ooo',
    '...........',
    '...........',
    'ooo......o.',
    'oo.......o.',
    'o.o.....o..',
    '...ooooo...',
]


def glyph(img, x, y, rows, colour):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == '#':
                P.put(img, x + i, y + j, colour)


def engrave(img, x, y, rows, ramp=BRASS, groove=INK[2]):
    """Cut a '#' glyph into brass: dark grooves, ramp[3] lit lip below-right."""
    on = {(i, j) for j, r in enumerate(rows) for i, ch in enumerate(r) if ch == '#'}
    for (i, j) in on:
        if (i + 1, j + 1) not in on:
            P.put(img, x + i + 1, y + j + 1, ramp[3])
    for (i, j) in on:
        P.put(img, x + i, y + j, groove)


def gsize(rows):
    return max(len(r) for r in rows), len(rows)


# ===========================================================================
# Output paths
# ===========================================================================

def _target(path):
    if OUT_ROOT is None:
        return path
    return Path(OUT_ROOT) / Path(path).relative_to(geo.TEXTURES)


def save_background(img, key):
    C.save_png(img, _target(geo.skin(key).background_path))


def save_frame(img, key):
    C.save_png(img, _target(geo.skin(key).frame_path()))


def save_states(states, key, bid):
    root = None if OUT_ROOT is None else Path(OUT_ROOT)
    C.save_button_states(states, key, bid, root=root)


# ===========================================================================
# Button grammar for this family
# ===========================================================================

def _plan(b, box, lines=None):
    """(lines, face, gap) that fit ``box``: HEARTH caps, HEARTH mixed, SPRIG."""
    if lines is None:
        return C._label_plan(b, box)
    for face in ('hearth', 'sprig'):
        f = L.FACES[face]
        gap = 2 if face == 'hearth' else 1
        tall = len(lines) * f.cap_height + (len(lines) - 1) * gap
        if all(L.text_width(t, face) <= box[2] for t in lines) and tall <= box[3]:
            return lines, face, gap
    raise ValueError(f'{b.id}: {lines} does not fit {box}')


def letter_row(img, b, box, colour='ink_0', shadow=None, lead=None, lead_draw=None, gap=3, lines=None):
    """Letter the label centred in ``box``, optionally preceded by a glyph of
    size ``lead`` (w, h) drawn by ``lead_draw(img, x, y)``. Returns text x."""
    x, y, w, h = box
    lw = lead[0] + gap if lead else 0
    lines, face, lgap = _plan(b, (x, y, w - lw, h), lines)
    f = L.FACES[face]
    tw = max(L.text_width(t, face) for t in lines)
    total = len(lines) * f.cap_height + (len(lines) - 1) * lgap
    left = x + (w - (lw + tw) + 1) // 2
    top = y + (h - total + 1) // 2
    if lead:
        lead_draw(img, left, top + (total - lead[1] + 1) // 2 - (0 if lead[1] <= total else 0))
    for i, t in enumerate(lines):
        tx = left + lw + (tw - L.text_width(t, face) + 1) // 2
        L.draw_text(img, tx, top + i * (f.cap_height + lgap), t, colour, shadow, face=face)
    return left + lw


def dip(img, body, ramp=EMBER, width=3):
    """Ember-dipped right end of a linen tag (dye soaked into the last columns)."""
    x, y, w, h = body
    x0 = x + w - 1 - width
    for yy in range(y + 1, y + h - 1):
        for xx in range(x0, x + w - 1):
            if P.get(img, xx, yy)[3]:
                P.put(img, xx, yy, ramp[1])
        if (yy - y) % 3 != 1 and P.get(img, x0 - 1, yy)[3]:
            P.put(img, x0 - 1, yy, ramp[1])          # dye wicking into the weave
    P.hline(img, x0, x + w - 2, y + 1, ramp[2])
    P.hline(img, x0, x + w - 2, y + h - 2, ramp[0])
    P.vline(img, x + w - 2, y + 2, y + h - 3, ramp[0])
    for yy in range(y + 3, y + h - 3, 3):
        P.put(img, x0 + 1, yy, ramp[2])              # sheen on the soaked threads
    return width + 1


def tag(key, b, glyph_rows=None, glyph_colour='ink_0', eyelet='auto', dyed=True, studs=0):
    """Secondary action: linen tag, ember-dipped end, optional leading glyph."""
    img = C.new(b.w, b.h)
    body = b.body.tuple()
    x, y, w, h = body
    seed = seed_for(key, b.id)
    lead = gsize(glyph_rows) if glyph_rows else None

    def layout(ey):
        trial = C.new(b.w, b.h)
        tb = P.linen_tag(trial, body, eyelet=ey, seed=seed)
        bx, by, bw, bh = tb[0] + 1, tb[1] + 2, tb[2] - 2, tb[3] - 4
        if dyed:
            bw -= 4
        return (bx, by, bw, bh)

    choices = ['left', None] if eyelet == 'auto' and w >= 36 and h <= 20 else [eyelet if eyelet != 'auto' else None]
    if eyelet == 'auto' and h >= 30:
        choices = ['left', None]
    chosen = None
    for ey in choices:
        box = layout(ey)
        lw = (lead[0] + (2 if lead[0] <= 3 else 3)) if lead else 0
        try:
            lines, face, _ = _plan(b, (box[0], box[1], box[2] - lw, box[3]))
        except ValueError:
            continue
        if face == 'hearth' and lines == b.text_lines:
            chosen = ey
            break
        if chosen is None:
            chosen = ey
    P.linen_tag(img, body, eyelet=chosen, seed=seed)
    if dyed:
        dip(img, body)
    box = layout(chosen)
    if studs:
        cx = box[0] + box[2] // 2
        for k in range(studs):
            sx = cx - (studs - 1) * 2 - 1 + k * 4
            P.sprite(img, sx, y + h - 5, ['32', '10'], {'3': BRASS[3], '2': BRASS[2], '1': BRASS[1], '0': BRASS[0]})
    if glyph_rows:
        letter_row(img, b, box, lead=lead, gap=2 if lead[0] <= 3 else 3,
                   lead_draw=lambda im, gx, gy: glyph(im, gx, gy, glyph_rows, glyph_colour))
    else:
        letter_row(img, b, box)
    return geo.finish_button(img, key, b.id)


def tall_tag(key, b, icon_rows, icon_key):
    """54x36 two-line tag: eyelet left, an emblem above the two label lines."""
    img = C.new(b.w, b.h)
    body = b.body.tuple()
    x, y, w, h = body
    seed = seed_for(key, b.id)
    tb = P.linen_tag(img, body, eyelet='left', seed=seed, weave=True)
    dip(img, body)
    bx, by, bw, bh = tb[0] + 1, tb[1] + 2, tb[2] - 6, tb[3] - 4
    iw, ih = gsize(icon_rows)
    P.sprite(img, bx + (bw - iw) // 2, y + 4, icon_rows, icon_key)
    letter_row(img, b, (bx, y + 4 + ih + 2, bw, h - (4 + ih + 2) - 4))
    return geo.finish_button(img, key, b.id)


def card(key, b, icon_rows=None, icon_key=None):
    """Read-only info card: a parchment note pinned flat with two brass tacks.
    No eyelet, no heavy bottom, no dipped end: clearly not a pressable tag."""
    img = C.new(b.w, b.h)
    body = b.body.tuple()
    x, y, w, h = body
    seed = seed_for(key, b.id)
    P.parchment_panel(img, body, seed, outline='ink_1', radius=1, fibres=True)
    # ruled faint line along the bottom, like a ledger slip
    P.stitch_line(img, x + 4, y + h - 4, x + w - 5, y + h - 4, SKY[2], 3, 1)
    P.tack(img, x + 2, y + 2, small=True)
    P.tack(img, x + w - 3, y + 2, small=True)
    box = (x + 4, y + 3, w - 8, h - 7)
    if icon_rows:
        lead = gsize(icon_rows)
        letter_row(img, b, box, lead=lead, gap=3,
                   lead_draw=lambda im, gx, gy: P.sprite(im, gx, gy, icon_rows, icon_key))
    else:
        letter_row(img, b, box)
    return geo.finish_button(img, key, b.id)


def option_tag(key, b):
    """Preset option: a linen tag whose number is stamped on an ember chip.
    The number only identifies the preset (it is part of the label)."""
    img = C.new(b.w, b.h)
    body = b.body.tuple()
    x, y, w, h = body
    seed = seed_for(key, b.id)
    word, num = b.label.rsplit(' ', 1)
    word = word.upper()
    eyelet = 'left' if w >= 54 else None
    tb = P.linen_tag(img, body, eyelet=eyelet, seed=seed)
    bx, by, bw, bh = tb[0] + 1, tb[1] + 2, tb[2] - 2, tb[3] - 4
    tw = L.text_width(word, 'hearth')
    chip_w, chip_h = L.text_width(num, 'hearth') + 4, 11
    total = tw + 3 + chip_w
    left = bx + (bw - total + 1) // 2
    ty = by + (bh - 7 + 1) // 2
    L.draw_text(img, left, ty, word, 'ink_0')
    cx, cy = left + tw + 3, ty - 2
    P.ink_outline(img, (cx, cy, chip_w, chip_h), 'ink_1', radius=1, heavy='b', fill_colour=EMBER[1])
    P.hline(img, cx + 1, cx + chip_w - 2, cy + 1, EMBER[2])
    P.hline(img, cx + 1, cx + chip_w - 2, cy + chip_h - 2, EMBER[0])
    L.draw_text(img, cx + 2, cy + 2, num, 'ink_0')
    return geo.finish_button(img, key, b.id)


def plate(key, b, glyph_rows=None):
    """Primary: brass-plated plank with an engraved emblem before the label."""
    img = C.new(b.w, b.h)
    seed = seed_for(key, b.id)
    box = C.primary_face(img, b.body.tuple(), seed)
    if glyph_rows:
        lead = gsize(glyph_rows)
        letter_row(img, b, box, 'ink_0', 'brass_3', lead=lead, gap=4,
                   lead_draw=lambda im, gx, gy: engrave(im, gx, gy, glyph_rows))
    else:
        letter_row(img, b, box, 'ink_0', 'brass_3')
    P.put(img, 5, 1, WOOD[1]); P.put(img, 6, 1, WOOD[1])           # scuff on the rim
    return geo.finish_button(img, key, b.id)


def apply_plate(key, b):
    """36x54 Apply: tall brass plate, engraved steps above, check below."""
    img = C.new(b.w, b.h)
    x, y, w, h = b.body.tuple()
    seed = seed_for(key, b.id)
    box = C.primary_face(img, (x, y, w, h), seed)
    bx, by, bw, bh = box
    sw, sh = gsize(STEPS)
    engrave(img, x + (w - sw) // 2, y + 10, STEPS)
    # engraved rule either side of the label
    for yy in (y + 20, y + 33):
        for xx in range(x + 9, x + w - 9):
            if xx % 2 == 0:
                P.put(img, xx, yy, BRASS[0])
    letter_row(img, b, (bx, y + 23, bw, 9), 'ink_0', 'brass_3')
    cw, ch = gsize(G_CHECK)
    engrave(img, x + (w - cw) // 2, y + 38, G_CHECK)
    P.put(img, 5, 1, WOOD[1]); P.put(img, 6, 1, WOOD[1])
    return geo.finish_button(img, key, b.id)


def wax(key, b):
    img = C.paint_button(key, b.id, seed=seed_for(key, b.id))
    return geo.finish_button(img, key, b.id)


def paint_buttons(key):
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        bid = b.id
        if b.role == 'info':
            icon = {'stats': (I_STATS, K_GLYPH), 'stock': (I_CRATE, K_GLYPH),
                    'quantity': (I_QTY, K_GLYPH), 'bid': (icons.COIN, icons.K_COIN)}[bid]
            img = card(key, b, *icon)
        elif b.style == 'danger':
            img = wax(key, b)
        elif bid == 'confirm':
            img = apply_plate(key, b)
        elif b.style == 'primary':
            g = {'upgrade': G_UPGRADE, 'toggle': G_SHOP}.get(bid)
            if bid == 'selected_amount':
                g = G_PURSE if key == 'chest_shop_buy' else G_CRATE
            img = plate(key, b, g)
        elif bid.startswith('preset_'):
            img = option_tag(key, b)
        elif bid == 'rename':
            img = tall_tag(key, b, QUILL, K_QUILL)
        elif bid == 'refresh':
            img = tall_tag(key, b, REFRESH, {'o': EMBER[0]})
        elif bid == 'back':
            img = tag(key, b, G_BACK)
        elif bid == 'increase':
            img = tag(key, b, G_UP)
        elif bid == 'decrease':
            img = tag(key, b, G_DOWN)
        elif bid.startswith('tier_'):
            img = tag(key, b, dyed=False, eyelet=None, studs=int(bid[-1]))
        elif bid in ('sell_price', 'buy_price'):
            img = tag(key, b, dyed=False, eyelet=None)
        else:
            img = tag(key, b)
        out[bid] = C.button_states(img, key, bid)
    return out


# ===========================================================================
# Background art
# ===========================================================================

def shop_posts(img, key, y0, y1):
    """Shop-front posts in the side margins beside the controls."""
    s = geo.skin(key)
    for side in ('l', 'r'):
        if side == 'l':
            cols = [(1, WOOD[4]), (2, WOOD[3]), (3, WOOD[3]), (4, WOOD[2]), (5, INK[1])]
        else:
            cols = [(170, INK[1]), (171, WOOD[4]), (172, WOOD[3]), (173, WOOD[2]), (174, WOOD[1])]
        for x, c in cols:
            P.vline(img, x, y0, y1, c)
        # grain flecks
        gx = 3 if side == 'l' else 172
        for yy in range(y0 + 4, y1 - 3, 7):
            P.put(img, gx, yy + (yy // 7) % 3, WOOD[1])
        # brass collars top and bottom
        x0 = 1 if side == 'l' else 170
        for yy in (y0, y1 - 2):
            P.hline(img, x0, x0 + 4, yy, INK[1])
            P.hline(img, x0, x0 + 4, yy + 1, BRASS[2])
            P.put(img, x0 + 1, yy + 1, BRASS[3])
            P.hline(img, x0, x0 + 4, yy + 2, BRASS[0])


def inventory_tag(img, key):
    """A blank price tag on twine pressed at the right end of the inventory band
    (light colours only, away from the live 'Inventory' label)."""
    _, iband = C.bands(key)
    y = iband.y + 1
    xr = iband.right - 6
    tx = xr - 10
    P.twine(img, xr - 34, y + 3, tx + 1, y + 2, sag=2, colour='parch_0', knot='parch_1')
    P.sprite(img, tx, y, ['..ooooooo', '.oppppppo', 'ophpppppo', '.osssssso', '..ooooooo'],
             {'o': INK[2], 'p': PARCHMENT[3], 'h': PARCHMENT[0], 's': PARCHMENT[1]})
    P.hline(img, tx + 5, tx + 7, y + 2, EMBER[2])


def hanging_sign(img, x, y, w, h, mode='day', rope_from=None, extra=None, seed=0):
    """A shop sign board: wood rim with brass corner nails, parchment inset
    with the storefront pictogram (and an optional extra sprite)."""
    if rope_from:
        for (rx, ry), sx in zip(rope_from, (x + 4, x + w - 5)):
            P.ink_line(img, rx, ry, sx, y, 'ink_1')
            P.put(img, sx, y - 1, ASH[1])
    P.plank(img, (x, y, w, h), WOOD, seed, 'ink_1', radius=1, grain=0.4)
    ix, iy, iw, ih = x + 2, y + 2, w - 4, h - 4
    P.parchment_panel(img, (ix, iy, iw, ih), seed, outline='ink_2', fibres=False,
                      ramp=PARCHMENT if mode != 'shut' else [ASH[1], ASH[2], PARCHMENT[1], PARCHMENT[2]])
    for (nx, ny) in ((x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 2), (x + w - 2, y + h - 2)):
        P.put(img, nx, ny, BRASS[2])
    sw = len(STOREFRONT[0])
    if extra:
        rows, key = extra
        ew = gsize(rows)[0]
        total = sw + 3 + ew
        sx = ix + (iw - total + 1) // 2
        storefront(img, sx, iy + (ih - 11 + 1) // 2, mode)
        P.sprite(img, sx + sw + 3, iy + (ih - gsize(rows)[1] + 1) // 2, rows, key)
    else:
        storefront(img, ix + (iw - sw + 1) // 2, iy + (ih - 11 + 1) // 2, mode)


def shelf(img, x, y, w, seed, brackets=True):
    """Short plank shelf (4 px) on two brass brackets."""
    P.plank(img, (x, y, w, 4), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    if brackets:
        for bx in (x + 3, x + w - 5):
            P.sprite(img, bx, y + 4, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def cast_shadow(img, x, y, w):
    """A short warm shadow under an object standing on a board."""
    P.hline(img, x + 1, x + w, y, WOOD[0])


# Service bell on the buy counter, 7x5 (smaller than an item icon, standing
# on the counter top with the counter's shadow line under it).
BELL = ['...o...', '..o3o..', '.o3221o', 'o32221o', 'ooooooo']
K_BELL = {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[0]}
# Twine-tied parcel on the sell counter, 8x5.
PARCEL = ['oooooooo', 'o33t333o', 'ottttttO', 'o22t222O', 'oOOOOOOO']
K_PARCEL = {'o': INK[1], 'O': INK[0], '3': PARCHMENT[1], '2': PARCHMENT[0], 't': WOOD[3]}
# A coin lying flat on the counter, 5x3.
COIN_FLAT = ['.ooo.', 'o321o', '.ooo.']
K_COIN_FLAT = {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[0]}


def stall_awning(img, x0, x1, y):
    """A striped ember-and-cream shop awning on a brass rail, running the full
    width between two controls, with a pointed hem and a dithered shade under
    it. ``y`` is the rail's top row; the hem tips land on y + 11."""
    P.hline(img, x0, x1, y, INK[1])
    P.hline(img, x0, x1, y + 1, BRASS[2])
    P.hline(img, x0 + 1, x0 + 2, y + 1, BRASS[3])
    P.hline(img, x0, x1, y + 2, INK[1])
    for x in range(x0, x1 + 1):
        k = (x - x0) // 3
        ramp = EMBER if k % 2 == 0 else [PARCHMENT[1], PARCHMENT[2], PARCHMENT[3]]
        P.put(img, x, y + 3, ramp[2])                       # lit fold under the rail
        for yy in range(y + 4, y + 8):
            P.put(img, x, yy, ramp[1])
        P.put(img, x, y + 8, ramp[0])                       # shaded lower edge
        # pointed hem: each stripe tapers to an ink tip
        pos = (x - x0) % 3
        if pos == 1:
            P.put(img, x, y + 9, ramp[0])
            P.put(img, x, y + 10, INK[1])
        else:
            P.put(img, x, y + 9, INK[1])
    # the awning's shade falls on the boards below it, fading out
    P.dither_patch(img, (x0, y + 11, x1 - x0 + 1, 1), WOOD[0], density=0.5)
    P.dither_patch(img, (x0, y + 12, x1 - x0 + 1, 1), WOOD[0], density=0.25)


def stall_counter(img, x0, x1, y0, y1, buy):
    """The stall's counter: an oiled counter top running the full width with a
    boarded front below it, and two small things on top (a service bell and a
    coin to buy; a tied parcel and a coin to sell)."""
    top = y1 - 10
    # counter top (3 rows) with ink edges, lit front lip
    P.hline(img, x0, x1, top, INK[1])
    P.hline(img, x0, x1, top + 1, WOOD[4])
    for x in range(x0, x1 + 1):
        if (x - x0) % 7 in (2, 5):
            P.put(img, x, top + 1, WOOD[3])                  # broken highlight
    P.hline(img, x0, x1, top + 2, WOOD[3])
    P.hline(img, x0, x1, top + 3, INK[0])
    # boarded front under the overhang
    P.hline(img, x0, x1, top + 4, WOOD[0])
    for yy in range(top + 5, y1):
        for x in range(x0, x1 + 1):
            P.put(img, x, yy, WOOD[0] if (x - x0) % 5 == 4 else WOOD[1])
    for x in range(x0 + 1, x1 + 1, 5):
        P.put(img, x, top + 6, WOOD[2])                       # nail heads
        P.put(img, x + 1, top + 5, WOOD[2])
    P.hline(img, x0, x1, y1, INK[0])
    # things on the counter, standing on its top edge
    if buy:
        P.sprite(img, x0 + 3, top - 5, BELL, K_BELL)
        P.sprite(img, x0 + 12, top - 3, COIN_FLAT, K_COIN_FLAT)
    else:
        P.sprite(img, x0 + 2, top - 5, PARCEL, K_PARCEL)
        P.sprite(img, x0 + 12, top - 3, COIN_FLAT, K_COIN_FLAT)


def bg_settings(key):
    s = geo.skin(key)
    img = C.base_background(key, seed=SEED)
    shop_posts(img, key, 15, 72)
    # static centre (61, 35, 54, 36): brass rail, hanging shop sign, tool shelf
    rx0, rx1 = 64, 111
    P.hline(img, rx0, rx1, 36, INK[1])
    P.hline(img, rx0 + 1, rx1 - 1, 37, BRASS[2])
    P.hline(img, rx0, rx1, 38, INK[1])
    P.put(img, rx0 + 3, 37, BRASS[3]); P.put(img, rx0 + 4, 37, BRASS[3])
    for ex in (rx0, rx1):
        P.sprite(img, ex - 1, 35, ['ooo', 'o3o', 'ooo', '.o.'], {'o': INK[1], '3': BRASS[1]})
    P.lantern_glow_ring(img, 88, 48, 22, strength=1)
    hanging_sign(img, 66, 40, 44, 16, 'day', rope_from=[(70, 38), (105, 38)],
                 extra=(icons.COG, icons.K_COG), seed=SEED)
    # tool shelf under the sign: toolbox, a small crate, hammer and wrench
    P.sprite(img, 104, 56, WRENCH, K_WRENCH)
    shelf(img, 63, 66, 50, SEED + 3)
    P.sprite(img, 67, 56, TOOLBOX, K_TOOLBOX)
    P.sprite(img, 82, 59, CRATE7, K_W)
    P.sprite(img, 94, 56, HAMMER, K_HAMMER)
    geo.finish_background(img, key)
    return img


def bg_trade(key):
    """chest_shop_buy / chest_shop_sell."""
    buy = key == 'chest_shop_buy'
    img = C.base_background(key, seed=SEED + (1 if buy else 2))
    shop_posts(img, key, 15, 72)
    # cell A (43, 17, 18, 18) and cell C (43, 53, 18, 18): the column between
    # the controls is a market-stall front, not two props in two cells. Both
    # pieces run edge to edge and continue behind the neighbouring controls,
    # so nothing sits centred in a cell like an item icon.
    stall_awning(img, 43, 60, 17)
    stall_counter(img, 43, 60, 53, 70, buy)
    # cell B (115, 35, 54, 18): a shelf where the exchange happens
    shelf(img, 117, 48, 50, SEED + 7)
    left = (icons.PURSE, icons.K_PURSE) if buy else (SLAT11, K_W)
    right = (SLAT11, K_W) if buy else (icons.PURSE, icons.K_PURSE)
    lw, lh = gsize(left[0])
    rw, rh = gsize(right[0])
    P.sprite(img, 124, 48 - lh, left[0], left[1])
    P.sprite(img, 136, 40, ARROW_R, {'c': PARCHMENT[2]})
    P.sprite(img, 147, 48 - rh, right[0], right[1])
    if buy:
        icons.draw_motif(img, 'coin', 159, 43)
    else:
        P.sprite(img, 159, 41, CRATE7, K_W)
    geo.finish_background(img, key)
    return img


def tier_cabinet(img, mood):
    """Static strip (43, 35, 54, 36) of the upgrade screens: a three-tier shelf
    unit, one crate on the top tier, two on the middle, three below; brass pips
    on each shelf edge echo the Tier 1/2/3 tags."""
    x0, y0, x1, y1 = 45, 36, 94, 70
    accent = {'ready': EMBER, 'inert': ASH}.get(mood, BRASS)
    # back boards (slightly darker), posts
    P.fill(img, (x0 + 1, y0, x1 - x0 - 1, y1 - y0), WOOD[1])
    for xx in range(x0 + 9, x1 - 1, 10):
        P.vline(img, xx, y0, y1 - 1, WOOD[0])
    for px in (x0, x1 - 2):
        P.plank(img, (px, y0 - 1, 3, y1 - y0 + 2), WOOD, SEED + px, 'ink_1', radius=0, vertical=True, grain=0)
    shelves = (46, 58, 69)
    for k, sy in enumerate(shelves):
        P.hline(img, x0 + 1, x1 - 2, sy, WOOD[4])
        P.hline(img, x0 + 1, x1 - 2, sy + 1, WOOD[2])
        P.hline(img, x0, x1 - 1, sy + 2, INK[1])
        for p in range(k + 1):
            px = x0 + 22 + p * 3
            P.put(img, px, sy + 1, accent[2]); P.put(img, px, sy, accent[1] if mood != 'inert' else ASH[2])
    # crates
    tops = [(46, [(65, 37)]), (58, [(55, 49), (73, 49)]), (69, [(49, 60), (64, 60), (79, 60)])]
    for sy, spots in tops:
        for (cx, cy) in spots:
            P.sprite(img, cx, sy - 9, CRATE9, K_W)
    if mood == 'ready':
        # a ribbon bow on the top crate and warm light over the cabinet
        P.sprite(img, 67, 33, ['e.e', '.E.', 'e.e'], {'e': EMBER[1], 'E': EMBER[0]})
        P.lantern_glow_ring(img, 69, 50, 26, strength=1)
        for (sx, sy) in ((58, 38), (84, 41), (47, 50)):
            P.put(img, sx, sy, EMBER[2]); P.put(img, sx - 1, sy, BRASS[3]); P.put(img, sx + 1, sy, BRASS[3])
            P.put(img, sx, sy - 1, BRASS[3]); P.put(img, sx, sy + 1, BRASS[3])
    elif mood == 'inert':
        # cooled to moonlight: the cabinet goes blue-grey. Back boards drop to
        # the darkest iron so the crates (one step lighter, lit top edge) stay
        # separate; the shelf lips catch a cold sky_2 glint instead of warm
        # wood_4, and a small cobweb fills the top-left corner by the post.
        lum_map = {0: INK[2], 1: ASH[0], 2: ASH[1], 3: ASH[2], 4: ASH[2]}
        for yy in range(y0 - 1, y1 + 1):
            for xx in range(x0, x1):
                p = P.get(img, xx, yy)
                rp = ramp_of(p)
                if p[3] and rp and rp[0] in ('wood', 'brass'):
                    P.put(img, xx, yy, lum_map[rp[1]] if rp[0] == 'wood' else ASH[1])
        for k, sy in enumerate(shelves):
            for xx in range(x0 + 1, x1 - 2):
                if (xx + k) % 7 not in (3, 4):                    # broken, hand-placed glint
                    P.put(img, xx, sy, SKY[2])
            for p_ in range(k + 1):                               # pips stay readable
                P.put(img, x0 + 22 + p_ * 3, sy, ASH[2])
        P.sprite(img, x0 + 3, y0, COBWEB, {'A': ASH[2]})


def bg_upgrade(key):
    mood = {'chest_shop_upgrade_confirm': 'ready', 'chest_shop_upgrade_disabled': 'inert'}.get(key, 'plain')
    img = C.base_background(key, seed=SEED + 4)
    shop_posts(img, key, 15, 72)
    tier_cabinet(img, mood)
    geo.finish_background(img, key)
    return img


def bg_listing(key):
    on = key == 'chest_shop_listing_enabled'
    img = C.base_background(key, seed=SEED + 5)
    shop_posts(img, key, 15, 108)
    # static cells 36-38 (7, 89, 54, 18): wall bracket, hanging shop sign, crate
    P.sprite(img, 7, 89, ['oo', 'o3', 'o2', 'oo'], {'o': INK[1], '3': BRASS[2], '2': BRASS[0]})
    P.hline(img, 9, 30, 90, INK[1]); P.hline(img, 9, 30, 91, ASH[1] if not on else BRASS[1]); P.hline(img, 9, 30, 92, INK[1])
    P.put(img, 31, 91, INK[1])
    P.put(img, 13, 93, INK[1]); P.put(img, 27, 93, INK[1])
    hanging_sign(img, 10, 94, 21, 14, 'lit' if on else 'shut', seed=SEED + 5)
    if on:
        P.lantern_glow_ring(img, 20, 101, 14, strength=1)
    # crate with a blank price tag (open) or a padlock (closed)
    P.sprite(img, 39, 97, SLAT11, K_W)
    cast_shadow(img, 39, 106, 11)
    if on:
        P.ink_line(img, 49, 98, 54, 93, 'parch_1')
        P.linen_tag(img, (52, 91, 7, 9), eyelet=None)
        P.put(img, 55, 93, INK[0])
        P.hline(img, 53, 57, 97, EMBER[1])
        P.sprite(img, 33, 99, CRATE7, K_W)
    else:
        P.sprite(img, 41, 100, PADLOCK, K_PADLOCK)
        for k, xx in enumerate(range(37, 53)):     # a chain across the crate lid
            P.put(img, xx, 96, ASH[2] if k % 2 else INK[1])
        P.sprite(img, 52, 99, CRATE7, K_W)
    geo.finish_background(img, key)
    return img


def paint_background(key):
    if key == 'chest_shop_settings':
        img = bg_settings(key)
    elif key in ('chest_shop_buy', 'chest_shop_sell'):
        img = bg_trade(key)
    elif key.startswith('chest_shop_upgrade'):
        img = bg_upgrade(key)
    else:
        img = bg_listing(key)
    inventory_tag(img, key)
    s = geo.skin(key)
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    return geo.finish_background(img, key)


# ===========================================================================
# Outer frame
# ===========================================================================

def note(img, x, y, w, lines, seed):
    """Pinned parchment note with SPRIG lines (always-true static hint)."""
    h = 6 + len(lines) * 6 + 2
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=False)
    P.tack(img, x + w // 2, y + 1)
    for i, t in enumerate(lines):
        L.draw_text_centered(img, x + (w + 1) // 2, y + 5 + i * 6, t, 'ink_0', face='sprig')
    return h


def price_tags(img, x0, x1, y, seed, colours):
    P.twine(img, x0, y, x1, y, sag=3)
    n = len(colours)
    for k, accent in enumerate(colours):
        tx = x0 + 3 + k * (x1 - x0 - 6) // max(1, n - 1) - 3 if n > 1 else (x0 + x1) // 2 - 3
        ty = y + 2 + (1 if k % 2 else 0) + (2 if 0 < k < n - 1 else 0)
        P.vline(img, tx + 3, ty - 1, ty + 1, PARCHMENT[0])
        P.linen_tag(img, (tx, ty + 2, 7, 11), eyelet=None, seed=seed + k)
        P.put(img, tx + 3, ty + 4, INK[0])
        P.fill(img, (tx + 1, ty + 9, 5, 2), accent[1])
        P.hline(img, tx + 1, tx + 5, ty + 8, accent[2])


def paint_frame(key):
    s = geo.skin(key)
    a = s.layer()
    seed = SEED + SKINS.index(key)
    img = C.base_frame(key, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    mood = 'plain'
    if key in ('chest_shop_upgrade_confirm',):
        mood = 'ready'
    elif key in ('chest_shop_upgrade_disabled', 'chest_shop_listing_disabled'):
        mood = 'inert'
    lit = mood != 'inert'

    # --- left panel: lantern on a rope, CHEST tag, hanging shop sign, shelf ---
    P.rope(img, lp.x + 6, 12, lp.right - 7, 12, sag=2)
    P.vline(img, lp.x + 19, 13, 16, INK[1])
    P.lantern(img, lp.x + 16, 17, glow=EMBER if lit else SKY)
    if lit:
        P.lantern_glow_ring(img, lp.x + 19, 22, 16 if mood == 'ready' else 13, strength=1)
    C.side_tag(img, lp, a.left_heading or 'CHEST', 34, seed, twine_from=(lp.x + 20, 26))
    # wall bracket and shop sign
    by = 52
    P.hline(img, 2, 34, by, INK[1]); P.hline(img, 2, 34, by + 1, BRASS[1] if lit else ASH[1])
    P.hline(img, 2, 34, by + 2, INK[1])
    P.sprite(img, 2, by + 3, ['o.', 'oo', 'o2o', 'o.2o', 'oooo'], {'o': INK[1], '2': BRASS[1]})
    sign_mode = {'chest_shop_listing_disabled': 'shut', 'chest_shop_upgrade_disabled': 'day'}.get(key, 'lit')
    hanging_sign(img, 10, by + 6, 23, 17, sign_mode, rope_from=[(13, by + 3), (29, by + 3)], seed=seed)
    # shelf with goods
    sy = 104
    shelf(img, lp.x + 3, sy, lp.w - 6, seed + 1)
    P.mug(img, lp.x + 5, sy - 9, EMBER, steam=lit, seed=seed)
    P.sprite(img, lp.x + 17, sy - 9, CRATE9, K_W)
    icons.draw_motif(img, 'coin', lp.x + 28, sy - 5)
    icons.draw_motif(img, 'coin', lp.x + 30, sy - 8)
    # trailing vine down the post
    for k in range(4):
        yy = sy + 10 + k * 12
        P.ink_line(img, lp.x + 31 - (k % 2), yy, lp.x + 31 - ((k + 1) % 2), yy + 12, SAGE[0])
        P.leaf(img, lp.x + (32 if k % 2 else 25), yy + 3, 'ne' if k % 2 else 'nw', small=k % 3 == 2)
    # crate stack at the foot
    P.sprite(img, lp.x + 4, H - 28, SLAT11, K_W)
    P.sprite(img, lp.x + 15, H - 28, SLAT11, K_W)
    P.sprite(img, lp.x + 9, H - 37, CRATE9, K_W)
    if not lit:
        # a cobweb in the corner under the goods shelf, against its left bracket
        P.sprite(img, lp.x + 8, sy + 4, COBWEB, {'A': ASH[2]})

    # --- right panel: hint note, family motifs per screen ---------------------
    hint = list(a.right_lines) or []
    ny = 14
    if hint:
        ny += note(img, rp.x + 5, 14, 30, hint, seed) + 6
    shelf(img, rp.x + 4, ny + 16, rp.w - 8, seed + 2)
    if key == 'chest_shop_settings':
        P.sprite(img, rp.x + 6, ny + 6, TOOLBOX, K_TOOLBOX)
        P.sprite(img, rp.x + 22, ny + 2, icons.COG, icons.K_COG)
        P.sprite(img, rp.x + 8, ny + 26, HAMMER, K_HAMMER)
        P.sprite(img, rp.x + 22, ny + 25, WRENCH, K_WRENCH)
        P.put(img, rp.x + 11, ny + 24, INK[1]); P.put(img, rp.x + 24, ny + 23, INK[1])
    elif key == 'chest_shop_buy':
        P.sprite(img, rp.x + 5, ny + 3, icons.PURSE, icons.K_PURSE)
        icons.draw_motif(img, 'coin', rp.x + 19, ny + 11)
        icons.draw_motif(img, 'coin', rp.x + 23, ny + 11)
        icons.draw_motif(img, 'coin', rp.x + 21, ny + 8)
        P.sprite(img, rp.x + 6, ny + 28, OPEN_CRATE, K_OPEN)
        P.sprite(img, rp.x + 19, ny + 29, ['..c..', '..c..', 'c.c.c', '.ccc.', '..c..'], {'c': PARCHMENT[2]})
    elif key == 'chest_shop_sell':
        P.sprite(img, rp.x + 5, ny + 7, SLAT11, K_W)
        P.sprite(img, rp.x + 17, ny + 7, CRATE9, K_W)
        P.sprite(img, rp.x + 11, ny - 2, CRATE9, K_W)
        P.sprite(img, rp.x + 21, ny + 28, ['..c..', '.ccc.', 'c.c.c', '..c..', '..c..'], {'c': PARCHMENT[2]})
        P.sprite(img, rp.x + 6, ny + 27, icons.PURSE, icons.K_PURSE)
    elif key.startswith('chest_shop_upgrade'):
        for k in range(3):
            P.sprite(img, rp.x + 5 + k * 10, ny + 7 - k * 0, CRATE9, K_W)
        P.sprite(img, rp.x + 10, ny - 2, CRATE9, K_W)
        P.sprite(img, rp.x + 20, ny - 2, CRATE9, K_W)
        if mood == 'ready':
            icons.draw_motif(img, 'candle', rp.x + 30, ny - 4)
            P.lantern_glow_ring(img, rp.x + 18, ny + 4, 16, strength=1)
        elif mood == 'inert':
            # cobweb under the crate shelf, against its right bracket
            bx = rp.x + 4 + (rp.w - 8) - 5
            P.sprite(img, bx - 6, ny + 20, COBWEB, {'A': ASH[2]}, flip_x=True)
    else:
        price_tags(img, rp.x + 3, rp.right - 4, ny + 1, seed,
                   [EMBER, BRASS, SAGE] if lit else [ASH, ASH, ASH])
        P.sprite(img, rp.x + 6, ny + 26, SLAT11, K_W)
        if not lit:
            P.sprite(img, rp.x + 8, ny + 27, PADLOCK, K_PADLOCK)
    # middle right: blank price tags on twine (or a herb pot on the listing screens)
    my = ny + 44
    if key.startswith('chest_shop_listing'):
        shelf(img, rp.x + 6, my + 14, rp.w - 12, seed + 4)
        icons.draw_motif(img, 'herb_pot', rp.x + 9, my + 2)
        P.mug(img, rp.x + 20, my + 5, SKY, steam=lit, seed=seed + 1)
    else:
        price_tags(img, rp.x + 3, rp.right - 4, my, seed + 5,
                   [EMBER, SAGE, BRASS] if lit else [ASH, ASH, ASH])
    # lower right: a second shelf with a candle and a ledger, coins below
    ly = H - 52
    shelf(img, rp.x + 4, ly, rp.w - 8, seed + 3)
    icons.draw_motif(img, 'candle', rp.x + 8, ly - 11)
    if lit:
        P.lantern_glow_ring(img, rp.x + 10, ly - 9, 10, strength=1)
    icons.draw_motif(img, 'ledger', rp.x + 20, ly - 10)
    P.sprite(img, rp.x + 7, H - 32, CRATE9, K_W)
    P.sprite(img, rp.x + 17, H - 32, SLAT11, K_W)
    # bottom strip rope between tacks
    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0)
    P.tack(img, 10, H - 5); P.tack(img, a.w - 11, H - 5)
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ===========================================================================
# Driver
# ===========================================================================

def paint_skin(key):
    save_background(paint_background(key), key)
    for bid, states in paint_buttons(key).items():
        save_states(states, key, bid)
    save_frame(paint_frame(key), key)
    s = geo.skin(key)
    return 1, len(s.buttons) * len(geo.STATES), len(s.art_layers)


def main(argv=None):
    global OUT_ROOT
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out-root', type=Path, help='write into DIR laid out like textures/ instead of pack-source')
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    args = ap.parse_args(argv)
    OUT_ROOT = args.out_root
    totals = [0, 0, 0]
    for key in args.skin or SKINS:
        n = paint_skin(key)
        totals = [t + k for t, k in zip(totals, n)]
        print(f'painted {key}: background, {n[1]} button PNGs, {n[2]} frame')
    print(f'TOTAL backgrounds={totals[0]} buttons={totals[1]} frames={totals[2]}'
          f' -> {OUT_ROOT or geo.TEXTURES}')


if __name__ == '__main__':
    main()
