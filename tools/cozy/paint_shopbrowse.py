#!/usr/bin/env python3
"""Cozy painter "shopbrowse": the chest-shop browsing screens.

    python tools/cozy/paint_shopbrowse.py                 # all four skins -> pack-source
    python tools/cozy/paint_shopbrowse.py --skin chest_shop_ads
    python tools/cozy/paint_shopbrowse.py --out-root DIR  # DIR laid out like textures/

Skins: chest_shop, chest_shop_owner (chest_3) and chest_shop_ads,
chest_shop_search (chest_6). Every background, every button in all six
states and every outer frame they own.

Family identity (chest_shop: ember accent, wood secondary): a shop front.
A striped ember-and-cream awning hangs under the title sheet and along the
frame tops, a wrought-iron bracket carries a hanging shop sign, and the side
panels are shop shelving: honey jars, burlap sacks, a merchant's balance,
crates and a barrel. The native listing wells are framed as shelf bays whose
boards run out through the margins. The keeper's view (chest_shop_owner)
swaps the goods shelf for an open ledger with a quill and hangs a ring of
keys; the ads board pins notices; the search screen carries a magnifying
glass and a route map. No words beyond the artLayers heading, leftHeading,
rightLines and each button's own label.

Deterministic: fixed seeds, no clock. Only writes this painter's PNGs.

Licence: code MIT; artwork CC0-1.0.
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
from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD  # noqa: E402

SKINS = ('chest_shop', 'chest_shop_owner', 'chest_shop_ads', 'chest_shop_search')
SEED = {'chest_shop': 31, 'chest_shop_owner': 37, 'chest_shop_ads': 41, 'chest_shop_search': 43}

# ---------------------------------------------------------------------------
# Hand-authored sprites (CC0-1.0). Keys map characters to palette colours.
# ---------------------------------------------------------------------------

# Honey jar: cork lid, amber honey behind glass with a cream glint.
JAR = [
    '.ooooo.',
    '.o443o.',
    'ooooooo',
    'og2hhho',
    'o2hhhho',
    'ohhhhHo',
    'ohhhhHo',
    'oHHHHHo',
    '.ooooo.',
]
K_JAR = {'o': INK[1], '4': WOOD[4], '3': WOOD[3], 'g': PARCHMENT[3], '2': EMBER[2],
         'h': EMBER[1], 'H': EMBER[0]}

# Green glass bottle with a cork.
BOTTLE = [
    '.o3o.',
    '.ooo.',
    '.ogo.',
    'oogGo',
    'ogGGo',
    'ogGGo',
    'oGGGo',
    'oGGDo',
    'oDDDo',
    '.ooo.',
]
K_BOTTLE = {'o': INK[1], '3': WOOD[3], 'g': SAGE[2], 'G': SAGE[1], 'D': SAGE[0]}

# Burlap sack tied with a twist of cord.
SACK = [
    '...o..o...',
    '....oo....',
    '...otto...',
    '..o2221o..',
    '.o322221o.',
    'o32222211o',
    'o32222211o',
    'o22222110o',
    'o22221110o',
    '.o111100o.',
    '..oooooo..',
]
K_SACK = {'o': INK[1], 't': WOOD[1], '3': PARCHMENT[2], '2': PARCHMENT[1], '1': PARCHMENT[0],
          '0': WOOD[3]}

# Merchant's balance: brass beam, two pans, a turned foot.
SCALE = [
    '.......o.......',
    '......o3o......',
    'ooooooo2ooooooo',
    'o3222222222221o',
    'ooooooo2ooooooo',
    '.o.....2.....o.',
    'o.o....2....o.o',
    'o322o..2..o322o',
    '.ooo...2...ooo.',
    '.....o321o.....',
    '....ooooooo....',
]
K_SCALE = {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[0]}

# Oak barrel with iron hoops.
BARREL = [
    '..oooooooo..',
    '.o44333322o.',
    '.oiiiiiiIIo.',
    'o3322122111o',
    'o3322122111o',
    'oiiiiiiiIIIo',
    'o3322122111o',
    'o3322122111o',
    'o3322122111o',
    'oiiiiiiiIIIo',
    'o3322122111o',
    '.o32212211o.',
    '.oiiiiiiIIo.',
    '..oooooooo..',
]
K_BARREL = {'o': INK[1], '4': WOOD[4], '3': WOOD[3], '2': WOOD[2], '1': WOOD[1],
            'i': ASH[1], 'I': ASH[0]}

# Stack of three brass coins seen from the side.
COIN_STACK = [
    '.oooo.',
    'o3322o',
    'o1100o',
    'o3322o',
    'o1100o',
    'o3322o',
    'o1100o',
    '.oooo.',
]
K_COINS = {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[1], '0': BRASS[0]}

# Brass key: ring bow, shaft, two-tooth bit.
KEY = [
    '.ooo.........',
    'o332ooooooooo',
    'o3.222222222o',
    'o210ooooo2o2o',
    '.ooo....ooooo',
]
K_KEY = {'o': INK[1], '3': BRASS[3], '2': BRASS[2], '1': BRASS[1], '0': BRASS[0]}

# The same key hanging bit-down from a ring.
KEY_V = [
    '.ooo.',
    'o332o',
    'o3.2o',
    'o210o',
    '.ooo.',
    '.o2o.',
    '.o2o.',
    '.o2o.',
    '.o2oo',
    '.o22o',
    '.o2oo',
    '.o22o',
    '.oooo',
]

# Open ledger: two ruled pages, a red cloth cover edge.
OPEN_LEDGER = [
    '.ooooooo.ooooooo.',
    'o3333333o3333333o',
    'o3iii333o3iiii33o',
    'o3333333o3333333o',
    'o3iiii33o33iii33o',
    'o3333333o3333333o',
    'obbbbbbbobbbbbbbo',
    '.ooooooooooooooo.',
]
K_OPEN_LEDGER = {'o': INK[1], '3': PARCHMENT[2], 'i': SKY[1], 'b': BERRY[0]}

# Ink pot with a quill feather.
QUILL_POT = [
    '.......of',
    '......ofF',
    '.....ofFo',
    '....ofFo.',
    '...ofFo..',
    '...oFo...',
    '..oooo...',
    '.o0000o..',
    'o011110o.',
    'o011110o.',
    '.oooooo..',
]
K_QUILL = {'o': INK[1], 'f': PARCHMENT[3], 'F': PARCHMENT[1], '0': SKY[0], '1': INK[2]}

# Wall nail / hook head.
NAIL = ['.o.', 'o3o', '.o.']
K_NAIL = {'o': INK[1], '3': ASH[2]}

AWNING_EMBER = (EMBER[2], EMBER[1], EMBER[0])
AWNING_CREAM = (PARCHMENT[3], PARCHMENT[2], PARCHMENT[1])


# ---------------------------------------------------------------------------
# Drawing helpers (local to this painter)
# ---------------------------------------------------------------------------

def awning(img, x0, x1, y, phase=0, rod=INK[1]):
    """Striped shop awning, 7 rows from ``y``: rod, shadowed fold, three rows
    of ember / cream stripes (6 px each), a rounded scallop and its ink hem."""
    for x in range(x0, x1 + 1):
        k = (x - x0 + phase) % 12
        ramp = AWNING_EMBER if k < 6 else AWNING_CREAM
        i = k % 6
        P.put(img, x, y, rod)
        P.put(img, x, y + 1, ramp[2] if i else ramp[1])
        body = ramp[0] if i == 0 else ramp[2] if i == 5 else ramp[1]
        for yy in range(y + 2, y + 5):
            P.put(img, x, yy, body)
        P.put(img, x, y + 5, INK[1] if i in (0, 5) else body)
        if i not in (0, 5):
            P.put(img, x, y + 6, INK[1])
    # a few deliberate highlight glints on the ember stripes
    for x in range(x0, x1 + 1):
        k = (x - x0 + phase) % 12
        if k == 2 and (x // 12) % 2 == 0:
            P.put(img, x, y + 2, EMBER[2])


def chain(img, x, y0, y1):
    for y in range(y0, y1 + 1):
        P.put(img, x, y, ASH[2] if (y - y0) % 2 == 0 else INK[1])


def bracket(img, x0, x1, y):
    """Wrought-iron sign arm from a riveted wall plate at x0 out to x1."""
    P.ink_outline(img, (x0, y - 3, 4, 9), 'ink_1', radius=1, fill_colour=ASH[0])
    P.put(img, x0 + 1, y - 2, ASH[2]); P.put(img, x0 + 2, y + 3, ASH[2])
    P.hline(img, x0 + 4, x1, y, INK[1])
    P.hline(img, x0 + 4, x1, y + 1, ASH[1])
    P.hline(img, x0 + 4, x1, y + 2, INK[1])
    for x in range(x0 + 6, x1, 5):
        P.put(img, x, y + 1, ASH[2])
    # scroll curl at the tip
    P.sprite(img, x1 - 1, y - 3, ['.oo.', 'o..o', 'o.oo', 'oo..'], {'o': INK[1]})


def signboard(img, box, seed, text=None, emblem=None):
    """Hanging shop sign: oak board, cream face, brass rings on top."""
    x, y, w, h = box
    P.plank(img, box, WOOD, seed, 'ink_1', radius=1, grain=0.5)
    face = (x + 2, y + 2, w - 4, h - 4)
    P.parchment_panel(img, face, seed, outline='ink_2', fibres=False)
    for rx in (x + 4, x + w - 5):
        P.sprite(img, rx - 1, y - 2, ['.o.', 'o.o', 'o3o'], {'o': BRASS[0], '3': BRASS[2]})
    if text:
        f = L.FACES['sprig']
        L.draw_text_centered(img, face[0] + (face[2] + 1) // 2, face[1] + (face[3] - f.cap_height + 1) // 2,
                             text, 'ink_0', face='sprig')
    if emblem:
        rows, key = emblem
        ew, eh = P.sprite_size(rows)
        P.sprite(img, face[0] + (face[2] - ew) // 2, face[1] + (face[3] - eh) // 2, rows, key)


def shelf(img, x, y, w, seed):
    """Plank shelf (5 px) on two brass brackets."""
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def notice(img, box, seed, ruled=2, seal=False, curl=None, behind=None, tack=True):
    """Pinned paper notice with ruled lines and no words."""
    x, y, w, h = box
    P.parchment_panel(img, box, seed, outline='ink_1', fibres=False)
    top = y + 4
    for k in range(ruled):
        yy = top + k * 3
        if yy < y + h - 2:
            P.stitch_line(img, x + 2, yy, x + w - 4 - (k % 2) * 3, yy, SKY[2], 3, 1, phase=k)
    if curl:
        P.page_curl(img, box, curl, 4, behind=behind)
    if seal:
        sx, sy = x + w - 5, y + h - 5
        P.sprite(img, sx - 1, sy - 1, ['.oo.', 'o21o', 'o10o', '.oo.'],
                 {'o': INK[0], '2': BERRY[2], '1': BERRY[1], '0': BERRY[0]})
    if tack:
        P.tack(img, x + w // 2, y, small=True)


def hanging_tags(img, x0, x1, y, seed, accents=(EMBER, SAGE, EMBER), sag=3):
    """Twine with blank linen shop tags (no prices) dyed at the hem."""
    P.twine(img, x0, y, x1, y, sag=sag)
    n = len(accents)
    span = (x1 - x0) // n
    for k, acc in enumerate(accents):
        tx = x0 + 2 + k * span + (span - 7) // 2
        ty = y + 2 + (1 if k == n // 2 else 0)
        P.vline(img, tx + 3, ty - 1, ty + 1, PARCHMENT[0])
        P.linen_tag(img, (tx, ty + 2, 7, 11), eyelet=None, seed=seed + k)
        P.put(img, tx + 3, ty + 4, INK[0])
        P.fill(img, (tx + 1, ty + 9, 5, 2), acc[1])
        P.hline(img, tx + 1, tx + 5, ty + 8, acc[2])


def big_lens(img, cx, cy, r, handle=(1, 1), hlen=8):
    """Magnifying glass: brass rim around sky glass with a cream glint and a
    turned wooden handle leaving at ``handle`` direction."""
    hx, hy = handle
    # handle first (under the rim)
    k0 = r if (hx == 0 or hy == 0) else int(r * 0.72) + 1
    sx, sy = cx + hx * k0, cy + hy * k0
    for t in range(hlen):
        px, py = sx + hx * t, sy + hy * t
        P.put(img, px, py, WOOD[3] if t % 3 else WOOD[4])
        P.put(img, px + 1, py, WOOD[1])
        P.put(img, px - 1, py, INK[1]); P.put(img, px + 2, py, INK[1])
    ex, ey = sx + hx * hlen, sy + hy * hlen
    P.put(img, ex, ey, INK[1]); P.put(img, ex + 1, ey, INK[1])
    P.put(img, sx, sy, BRASS[1]); P.put(img, sx + 1, sy, BRASS[0])
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 > (r + 0.5) ** 2:
                continue
            if d2 > (r - 0.5) ** 2:
                c = INK[1]
            elif d2 > (r - 1.5) ** 2:
                c = BRASS[2] if (x - cx) + (y - cy) < 0 else BRASS[0]
            elif d2 > (r - 2.5) ** 2:
                c = INK[2]
            else:
                c = SKY[2] if (x - cx) + (y - cy) < r // 2 else SKY[1]
            P.put(img, x, y, c)
    # glint
    for gx, gy in ((-r // 2, -r // 2 + 1), (-r // 2 + 1, -r // 2), (-r // 2, -r // 2 + 2)):
        P.put(img, cx + gx, cy + gy, PARCHMENT[3])
    P.put(img, cx - r + 2, cy - 1, BRASS[3])


def crates(img, x, floor, n_bottom=2, top=True, flip=False):
    """Crates stacked on a floor line (the bottom row of the stack is floor-1)."""
    for k in range(n_bottom):
        icons.draw_motif(img, 'crate', x + k * 10, floor - 10, flip_x=flip and k % 2 == 1)
    if top:
        icons.draw_motif(img, 'crate', x + 5 if n_bottom > 1 else x, floor - 20)


def spr(img, x, y, rows, key, flip_x=False):
    P.sprite(img, x, y, rows, key, flip_x=flip_x)


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def _forbidden(s, bands, ring=3):
    """'L' mask: 255 where decoration must not land (holes + their 3 well
    rings, the light text bands)."""
    m = Image.new('L', (s.width, s.height), 0)
    rects = [r for r in s.masks] + list(s.extra_transparent)
    for r in rects:
        m.paste(255, (max(0, r.x - ring), max(0, r.y - ring),
                      min(s.width, r.right + ring), min(s.height, r.bottom + ring)))
    for b in bands:
        m.paste(255, (b.x, b.y, b.right, b.bottom))
    return m


def _apply(bg, overlay, forbid):
    a = overlay.getchannel('A')
    allowed = Image.eval(forbid, lambda v: 0 if v else 255)
    from PIL import ImageChops
    mask = ImageChops.multiply(a, allowed)
    bg.paste(overlay, (0, 0), mask)


def shelf_stub(img, x0, x1, y):
    """A shelf board end running out through a margin (3 rows: lit, body, shade)."""
    P.hline(img, x0, x1, y - 1, INK[1])
    P.hline(img, x0, x1, y, WOOD[4])
    P.hline(img, x0, x1, y + 1, WOOD[2])
    P.hline(img, x0, x1, y + 2, WOOD[0])
    P.hline(img, x0, x1, y + 3, INK[1])


def _base(key, seed):
    """Shared base, except that the listing bays get the carved wooden lip of
    shop shelving while the player's own inventory keeps the stitched cloth."""
    s = geo.skin(key)
    bg = C.base_background(key, seed=seed, wells='none')
    tband, iband = C.bands(key)
    protect = [tband.tuple(), iband.tuple()]
    P.wood_well(bg, P.merge_holes(s.content_slots), protect=protect)
    P.stitched_well(bg, P.merge_holes(s.player_slots), protect=protect)
    # the title sheet hangs from the rim on two little brass rings
    for rx in (4, s.width - 6):
        P.sprite(bg, rx, 1, ['.o.', 'o.o', '.o.'], {'o': BRASS[1]})
        P.put(bg, rx + 1, 1, BRASS[3])
    geo.finish_background(bg, key)
    return bg


def paint_background(key):
    s = geo.skin(key)
    seed = SEED[key]
    bg = _base(key, seed)
    tband, iband = C.bands(key)
    ov = C.new(s.width, s.height)
    if s.layout == 'chest_3':
        # Shelf boards of the listing bays run out through the left margin at
        # each row boundary; brass pegs carry them. The button column on the
        # right is the shop's till.
        for yb in (33, 51):
            shelf_stub(bg, 1, 5, yb)
            P.put(bg, 2, yb + 4, BRASS[1]); P.put(bg, 3, yb + 4, BRASS[0])
            # the same boards continue behind the till column
            shelf_stub(bg, 169, 174, yb)
            P.put(bg, 172, yb + 4, BRASS[1]); P.put(bg, 173, yb + 4, BRASS[0])
        # inventory band: warm wear at the bottom corners of the sheet
        P.tack(bg, 3, s.height - 4, small=True)
        P.tack(bg, s.width - 4, s.height - 4, small=True)
        geo.finish_background(bg, key)
        return bg

    # --- chest_6: static top strip and static right column ---------------------
    # shop-front awning under the title sheet
    awning(ov, 4, 171, 15)
    P.vline(ov, 3, 15, 20, INK[1]); P.vline(ov, 172, 15, 20, INK[1])
    strip_y = 23           # rows 23..30 sit under the awning, above the well rings
    if key == 'chest_shop_ads':
        # a row of pinned notices and blank tags: the shop's notice line
        P.twine(ov, 6, 23, 171, 23, sag=0)
        xs = [(28, 15), (64, 13), (100, 17), (138, 14)]
        for k, (nx, nw) in enumerate(xs):
            notice(ov, (nx, strip_y, nw, 8), seed + k, ruled=2, seal=(k % 2 == 1), tack=True)
        for k, tx in enumerate((48, 84, 122)):
            P.vline(ov, tx + 2, 24, 24, PARCHMENT[0])
            P.linen_tag(ov, (tx, 25, 5, 6), eyelet=None, seed=seed + 10 + k)
            P.hline(ov, tx + 1, tx + 3, 29, (EMBER if k % 2 == 0 else SAGE)[1])
        P.tack(ov, 6, 22, small=True)
    else:
        # the searcher's bench: a rolled map, a magnifying glass, a crate
        P.parchment_panel(ov, (30, 23, 26, 8), seed, outline='ink_1', fibres=False)
        P.stitch_line(ov, 33, 26, 52, 26, SKY[1], 1, 2)
        P.put(ov, 46, 27, BERRY[1]); P.put(ov, 47, 28, BERRY[1]); P.put(ov, 47, 26, BERRY[1]); P.put(ov, 45, 28, BERRY[1])
        for cx in (30, 55):
            P.ink_outline(ov, (cx - 1, 22, 3, 10), 'ink_1', radius=1, fill_colour=PARCHMENT[1])
            P.put(ov, cx, 23, PARCHMENT[3])
        # lens lying on the bench (rim r4), handle to the right
        big_lens(ov, 82, 26, 4, handle=(1, 0), hlen=9)
        icons.draw_motif(ov, 'ledger', 108, 22)
        spr(ov, 124, 22, JAR, K_JAR)
        spr(ov, 134, 21, BOTTLE, K_BOTTLE)
        notice(ov, (146, 23, 14, 8), seed + 3, ruled=2, tack=True)
        P.tack(ov, 6, 22, small=True)

    # right static column (x155..173): shop shelving that continues the bays
    rx0, rx1 = 155, 173
    for yb in (51, 69, 87):
        shelf_stub(bg, rx0, rx1, yb)
        P.sprite(bg, rx1 - 3, yb + 4, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})
    chain(ov, 163, 22, 25)
    P.lantern(ov, 160, 26)
    spr(ov, 157, 41, JAR, K_JAR)
    spr(ov, 166, 40, BOTTLE, K_BOTTLE)
    if key == 'chest_shop_ads':
        spr(ov, 158, 57, SACK, K_SACK)
        notice(ov, (157, 73, 13, 13), seed + 7, ruled=3, curl='br', behind=WOOD[2], tack=True)
    else:
        spr(ov, 158, 57, SACK, K_SACK)
        big_lens(ov, 162, 79, 4, handle=(1, 1), hlen=4)
    icons.draw_motif(ov, 'crate', 157, 96)
    spr(ov, 167, 98, COIN_STACK, K_COINS)
    _apply(bg, ov, _forbidden(s, [tband, iband]))
    # glow of the little lantern, after the overlay so it lights the shelf wood
    P.lantern_glow_ring(bg, 164, 31, 9, strength=1)
    # restore the inventory band & wells exactly as the base drew them
    base = _base(key, seed)
    fb = _forbidden(s, [tband, iband])
    bg.paste(base, (0, 0), fb)
    geo.finish_background(bg, key)
    return bg


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def ember_hem(img, body):
    """Ember-dyed hem across the foot of an icon tag (chest-shop accent)."""
    x, y, w, h = body
    P.hline(img, x + 2, x + w - 3, y + h - 3, EMBER[1])
    P.hline(img, x + 1, x + w - 2, y + h - 2, EMBER[0])
    for xx in range(x + 3, x + w - 3, 3):
        P.put(img, xx, y + h - 3, EMBER[2])


def balance_banner(key, b, seed):
    """18x72 read-only balance: a linen shop banner hung from an oak rod, purse
    near the top, a coin stack below, ember hem and a swallowtail foot."""
    img = C.new(b.w, b.h)
    x, y, w, h = b.body.tuple()       # (0, 0, 17, 72)
    # cloth with swallowtail cut
    inside = set()
    for j in range(4, h):
        for i in range(w):
            cut = j >= h - 6 and abs(i - (w - 1) / 2) < (j - (h - 7)) - 0.5
            if not cut:
                inside.add((i, j))
    edge = P._edge_pixels(inside)
    for (i, j) in inside:
        P.put(img, x + i, y + j, PARCHMENT[2])
    for (i, j) in edge:
        P.put(img, x + i, y + j, INK[0] if j >= h - 7 else INK[1])
    P.vline(img, x + 1, y + 5, y + h - 9, PARCHMENT[3])
    P.vline(img, x + w - 2, y + 5, y + h - 9, PARCHMENT[1])
    P.stitch_line(img, x + 2, y + 6, x + 2, y + h - 12, 'parch_0', 2, 2)
    P.stitch_line(img, x + w - 3, y + 6, x + w - 3, y + h - 12, 'parch_0', 2, 2, phase=1)
    # ember hem above the swallowtail
    P.hline(img, x + 1, x + w - 2, y + h - 10, EMBER[2])
    P.hline(img, x + 1, x + w - 2, y + h - 9, EMBER[1])
    P.hline(img, x + 1, x + w - 2, y + h - 8, EMBER[0])
    for (i, j) in inside - edge:
        if j >= h - 7:
            P.put(img, x + i, y + j, EMBER[1] if (i + j) % 5 else EMBER[2])
    # oak rod with brass finials
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.3)
    P.sprite(img, x + 1, y + 1, ['32', '10'], {'3': BRASS[3], '2': BRASS[2], '1': BRASS[1], '0': BRASS[0]})
    P.sprite(img, x + w - 3, y + 1, ['32', '10'], {'3': BRASS[3], '2': BRASS[2], '1': BRASS[1], '0': BRASS[0]})
    # purse and coins
    icons.draw_icon(img, 'balance', (x, y + 8, w, 15))
    spr(img, x + (w - 6) // 2, y + 28, COIN_STACK, K_COINS)
    for k in range(3):
        icons.draw_icon(img, 'coin', (x, y + 38 + k * 6, w, 5))
    geo.finish_button(img, key, b.id)
    return img


def notice_plaque(key, b, seed):
    """Read-only info plaque (Create): a small oak-framed placard nailed to the
    shop wall, cream face lettered with the button's own label. It reads as a
    fixture, not as a pressable tag."""
    img = C.new(b.w, b.h)
    x, y, w, h = b.body.tuple()       # (0, 1, 36, 17)
    P.plank(img, (x, y, w, h), WOOD, seed, 'ink_1', radius=1, grain=0.0)
    face = (x + 3, y + 3, w - 6, h - 6)
    P.parchment_panel(img, face, seed, outline=None, fibres=False)
    P.hline(img, face[0], face[0] + face[2] - 1, face[1], PARCHMENT[1])   # sunk under the frame lip
    for nx, ny in ((x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 3), (x + w - 2, y + h - 3)):
        P.put(img, nx, ny, ASH[2])
    P.put(img, x + w - 1, y + h - 1, INK[0])
    C.letter(img, b, (face[0] + 1, face[1] + 1, face[2] - 2, face[3] - 1), 'ink_0')
    geo.finish_button(img, key, b.id)
    return img


def paint_buttons(key):
    s = geo.skin(key)
    seed = SEED[key]
    out = {}
    for b in s.buttons:
        if b.id == 'balance' and b.h > 36:
            normal = balance_banner(key, b, seed)
        elif b.role == 'info' and b.icon is None:
            normal = notice_plaque(key, b, seed)
        else:
            normal = C.paint_button(key, b.id, seed=seed)
            kind = C.button_kind(b)
            if kind == 'icon':
                ember_hem(normal, b.body.tuple())
            geo.finish_button(normal, key, b.id)
        out[b.id] = C.button_states(normal, key, b.id)
    return out


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def side_awnings(img, a):
    lp, rp = a.left_panel, a.right_panel
    awning(img, 1, lp.right - 1, a.container.y, phase=0)
    awning(img, rp.x + 2, rp.right - 2, a.container.y, phase=6)
    P.vline(img, 0, a.container.y, a.container.y + 6, INK[0])
    P.vline(img, a.w - 1, a.container.y, a.container.y + 6, INK[0])


def lines_card(img, box, lines, seed):
    x, y, w, h = box
    P.parchment_panel(img, box, seed, outline='ink_1', fibres=True)
    P.page_curl(img, box, 'br', 4, behind=WOOD[1])
    P.tack(img, x + w // 2, y + 1)
    f = L.FACES['sprig']
    top = y + 5
    for i, t in enumerate(lines):
        L.draw_text_centered(img, x + (w + 1) // 2, top + i * (f.cap_height + 2), t, 'ink_0', face='sprig')


def paint_frame(key):
    s = geo.skin(key)
    a = s.layer()
    seed = SEED[key]
    img = C.base_frame(key, a.id, seed=seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    floor = a.container.bottom          # first row of the bottom beam
    side_awnings(img, a)
    owner = key == 'chest_shop_owner'
    tall = s.layout == 'chest_6'
    L0 = 3                               # left panel usable x
    R0 = rp.x + 4                        # right panel usable x (past cast shadow)

    # ---------------- left panel ----------------
    bracket(img, 2, 33, 20)
    chain(img, 8, 23, 24); chain(img, 29, 23, 24)
    if a.left_heading:
        signboard(img, (4, 25, 30, 15), seed, text=a.left_heading)
        y = 40
    else:
        emb = (icons.CRATE, icons.K_CRATE) if key == 'chest_shop_ads' else (icons.LENS, icons.K_LENS)
        signboard(img, (4, 25, 30, 20), seed, emblem=emb)
        y = 45

    if tall and key == 'chest_shop_ads':
        # notice board: oak frame, pinned notes with ruled lines, a sealed one
        bx, by, bw, bh = 3, y + 6, 34, 74
        P.plank(img, (bx, by, bw, bh), WOOD, seed + 5, 'ink_1', radius=1, grain=0.6)
        P.ink_outline(img, (bx + 3, by + 3, bw - 6, bh - 6), 'ink_1', radius=0, fill_colour=WOOD[3])
        P._grain(img, (bx + 4, by + 4, bw - 8, bh - 8), [WOOD[1], WOOD[2], WOOD[3], WOOD[4], WOOD[4]], seed, 0.4)
        notice(img, (bx + 5, by + 6, 13, 15), seed + 1, ruled=3)
        notice(img, (bx + 20, by + 8, 10, 12), seed + 2, ruled=2, seal=True)
        notice(img, (bx + 6, by + 25, 23, 19), seed + 3, ruled=4, curl='br', behind=WOOD[3])
        P.wax_seal(img, bx + 24, by + 40, 4, BERRY, seed, drip=True)
        notice(img, (bx + 5, by + 49, 11, 15), seed + 4, ruled=3, curl='bl', behind=WOOD[3])
        P.linen_tag(img, (bx + 20, by + 50, 8, 14), eyelet=None, seed=seed)
        P.put(img, bx + 23, by + 52, INK[0])
        P.fill(img, (bx + 21, by + 60, 6, 2), EMBER[1])
        P.tack(img, bx + 24, by + 49, small=True)
        y = by + bh + 6
    elif tall:
        # searcher's corner: magnifying glass on a cord, an inked route map
        spr(img, 13, y + 2, NAIL, K_NAIL)
        P.twine(img, 14, y + 5, 14, y + 9, sag=0)
        big_lens(img, 14, y + 18, 8, handle=(1, 1), hlen=8)
        my = y + 36
        P.parchment_panel(img, (4, my, 32, 28), seed, outline='ink_1', fibres=True)
        P.tack(img, 6, my + 1, small=True); P.tack(img, 33, my + 1, small=True)
        # route: dotted sky path between little sage trees and a hill
        route = [(8, my + 22), (12, my + 19), (16, my + 19), (19, my + 15), (23, my + 13), (27, my + 9)]
        for (ax, ay), (bx2, by2) in zip(route, route[1:]):
            P.stitch_line(img, ax, ay, bx2, by2, SKY[1], 1, 1)
        for tx, ty in ((9, my + 8), (14, my + 6), (28, my + 18)):
            P.sprite(img, tx, ty, ['.g.', 'gGg', '.o.'], {'g': SAGE[1], 'G': SAGE[2], 'o': WOOD[1]})
        P.sprite(img, 17, my + 4, ['..x..', '.x.x.', 'x...x'], {'x': SKY[0]})
        P.sprite(img, 27, my + 8, ['x.x', '.x.', 'x.x'], {'x': BERRY[1]})
        P.page_curl(img, (4, my, 32, 28), 'br', 5, behind=WOOD[1])
        y = my + 34
    else:
        y = 56

    # goods shelf (owner: the keeper's ledger and quill)
    sy = y + 12
    shelf(img, L0 + 1, sy, 32, seed + 11)
    if owner:
        spr(img, L0 + 3, sy - 8, OPEN_LEDGER, K_OPEN_LEDGER)
        spr(img, L0 + 22, sy - 11, QUILL_POT, K_QUILL)
    else:
        spr(img, L0 + 3, sy - 9, JAR, K_JAR)
        spr(img, L0 + 11, sy - 11, SACK, K_SACK)
        spr(img, L0 + 23, sy - 10, BOTTLE, K_BOTTLE)
        spr(img, L0 + 28, sy - 8, COIN_STACK, K_COINS)
    # balance shelf
    sy2 = sy + 36
    shelf(img, L0 + 1, sy2, 32, seed + 12)
    spr(img, L0 + 3, sy2 - 11, SCALE, K_SCALE)
    spr(img, L0 + 21, sy2 - 8, COIN_STACK, K_COINS)
    icons.draw_motif(img, 'coin', L0 + 27, sy2 - 5)
    # tags on twine, or the keeper's ring of keys on a nail
    ty = sy2 + 12
    if owner:
        # the keeper's ring of keys on a nail
        spr(img, 18, ty, NAIL, K_NAIL)
        P.sprite(img, 16, ty + 2, ['.ooo.', 'o...o', 'o...o', '.o.o.', '..o..'],
                 {'o': BRASS[1]})
        P.put(img, 17, ty + 2, BRASS[3])
        spr(img, 14, ty + 6, KEY_V, K_KEY)
        spr(img, 19, ty + 7, KEY_V, K_KEY, flip_x=True)
        spr(img, 6, ty + 4, NAIL, K_NAIL)
        spr(img, 4, ty + 6, ['.o.', 'o2o', 'o1o', 'o2o', 'o1o', 'o2o', '.o.'],
            {'o': INK[1], '2': BRASS[2], '1': BRASS[0]})   # a brass tally tube on its own hook
    else:
        hanging_tags(img, 5, 35, ty, seed)
    # crates on the floor
    crates(img, L0 + 1, floor, 2, top=True)
    if tall:
        P.leaf(img, L0 + 24, floor - 18, 'ne')
        P.ink_line(img, L0 + 25, floor - 12, L0 + 24, floor - 1, SAGE[0], wobble=1, seed=seed)
        P.leaf(img, L0 + 26, floor - 9, 'nw', small=True)

    # ---------------- right panel ----------------
    lines = list(a.right_lines)
    ch = 5 + len(lines) * 7 + 3
    lines_card(img, (R0 + 1, 19, 30, ch), lines, seed)
    if owner:
        spr(img, R0 + 2, 19 + ch + 3, NAIL, K_NAIL)
        spr(img, R0 + 6, 19 + ch + 3, KEY, K_KEY)
    yl = 19 + ch + (12 if owner else 6)
    spr(img, R0 + 14, yl - 4, NAIL, K_NAIL)
    chain(img, R0 + 15, yl - 1, yl + 1)
    P.lantern(img, R0 + 12, yl + 2)
    P.lantern_glow_ring(img, R0 + 15, yl + 7, 12, strength=1)
    # candle and herbs shelf
    s1 = yl + 30
    shelf(img, R0, s1, 32, seed + 21)
    icons.draw_motif(img, 'candle', R0 + 3, s1 - 11)
    P.lantern_glow_ring(img, R0 + 5, s1 - 10, 7, strength=1)
    icons.draw_motif(img, 'herb_pot', R0 + 10, s1 - 12)
    spr(img, R0 + 21, s1 - 9, JAR, K_JAR)
    if tall:
        hanging_tags(img, R0, R0 + 31, s1 + 12, seed + 3, accents=(SAGE, EMBER, SAGE))
        s2 = s1 + 44
    else:
        s2 = s1 + 30
    shelf(img, R0, s2, 32, seed + 22)
    icons.draw_motif(img, 'crate', R0 + 3, s2 - 10)
    if key == 'chest_shop_search':
        big_lens(img, R0 + 20, s2 - 6, 4, handle=(1, 1), hlen=0)
    else:
        spr(img, R0 + 15, s2 - 11, SACK, K_SACK)
        icons.draw_motif(img, 'coin', R0 + 26, s2 - 5)
    if tall:
        s3 = s2 + 32
        shelf(img, R0, s3, 32, seed + 23)
        icons.draw_motif(img, 'ledger', R0 + 3, s3 - 10)
        spr(img, R0 + 16, s3 - 10, BOTTLE, K_BOTTLE)
        spr(img, R0 + 23, s3 - 8, COIN_STACK, K_COINS)
    # a vine trailing from the last shelf bracket
    last = s3 if tall else s2
    vx = R0 + 25
    for k in range((floor - 26 - last) // 12):
        yy = last + 7 + k * 12
        P.ink_line(img, vx - (k % 2), yy, vx - ((k + 1) % 2), yy + 12, SAGE[0], wobble=0)
        P.leaf(img, vx + (1 if k % 2 else -7), yy + 3, 'ne' if k % 2 else 'nw', small=k % 3 == 2)
    # barrel, a crate stack and a sack on the floor
    spr(img, R0 + 1, floor - 14, BARREL, K_BARREL)
    icons.draw_motif(img, 'crate', R0 + 14, floor - 10)
    icons.draw_motif(img, 'crate', R0 + 14, floor - 20)
    P.mug(img, R0 + 15, floor - 29, EMBER, steam=True, seed=seed)
    spr(img, R0 + 24, floor - 11, SACK, K_SACK)

    # bottom strip: a shelf-edge rope between tacks
    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0)
    P.tack(img, 10, H - 5); P.tack(img, a.w - 11, H - 5)
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _paths(key, root):
    s = geo.skin(key)
    if root is None:
        return s.background_path, (lambda lid: s.frame_path(lid))
    root = Path(root)
    return root / 'menu' / f'{key}.png', (lambda lid: root / 'frames' / key / f'{lid}.png')


def paint(key, root=None):
    s = geo.skin(key)
    bg = paint_background(key)
    bpath, fpath = _paths(key, root)
    written = [C.save_png(bg, bpath)]
    for bid, states in paint_buttons(key).items():
        written += C.save_button_states(states, key, bid, root=root)
    for a in s.art_layers:
        written.append(C.save_png(paint_frame(key), fpath(a.id)))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', type=Path, help='write under DIR (laid out like textures/) instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        files = paint(key, args.out_root)
        print(f'{key}: wrote {len(files)} PNGs')


if __name__ == '__main__':
    main()
