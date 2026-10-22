#!/usr/bin/env python3
"""Soulrend painter "economy": economy_hub and economy_log.

    python tools/soulrend/paint_economy.py                    # paint both skins into pack-source
    python tools/soulrend/paint_economy.py --skin economy_log # one skin
    python tools/soulrend/paint_economy.py --out-root DIR     # write DIR/{menu,buttons,frames}/...

Family identity (docs/SOULREND-STYLE-GUIDE.md section 5): a torchlit counting
vault. Gold accent, ember secondary. Coin scales, a ledger closed with a wax
seal, iron-banded coffers, stacked coin columns (never numbers), torches.

* economy_hub (chest_3, eight controls, no content wells): the sheet is bound
  by iron ledger straps; the outer frame is the treasury wall (a gold-coin
  banner, a torch, coin scales in a niche, coin columns on a ledge, a coffer
  of spilled coins, a hanging lantern, the sealed ledger on a lectern, a
  chained key, stacked coffers and a gargoyle corbel).
* economy_log (chest_6, 28 listing wells): the ledger vault. The static top
  row and side columns are one recessed stone alcove round the iron listing
  cabinet: a shelf of coffers, coin columns, the sealed ledger and the scales
  across the top, a coin banner and an arched strongroom door on the left, a torch, a
  chained ledger and coin columns on the right. Every prop straddles a cell
  boundary; every listing well stays an empty framed socket. The frame is the
  archive: shelves of ledger spines, a quill and inkwell, a candle clock.

Every pixel is placed in code with fixed seeds; nothing here is traced or
copied. Artwork CC0-1.0; this script MIT.
"""
from __future__ import annotations

import argparse
import random
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
from palette import BLOOD, EMBER, GOLD, INK, IRON, MOSS, STONE, UMBER, VELLUM  # noqa: E402

SKINS = ('economy_hub', 'economy_log')
SEED = 41

# A darker stone ramp for recesses cut into the sheet (the vault alcove):
# ink mortar, stone_0 blocks, stone_1 / stone_2 lit edges.
VAULT = [INK[1], STONE[0], STONE[1], STONE[2]]


# ---------------------------------------------------------------------------
# Drawing helpers (economy-only; the shared modules are never edited)
# ---------------------------------------------------------------------------

def ledge(img, x, y, w, brackets=True):
    """A carved stone ledge 4 px tall (top row y) on two iron brackets."""
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.put(img, x + w // 3, y + 1, STONE[1]); P.put(img, x + w // 3 + 1, y + 1, STONE[1])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0, heavy='b')
    if brackets:
        for bx in (x + 2, x + w - 4):
            P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


COIN_EMBLEM = ['..OOO..',
               '.OHHhO.',
               'OHhhhgO',
               'OHhOhgO',
               'OhhhggO',
               '.OhggO.',
               '..OOO..']

LOCK = ['OOOOO',
        'OHhhO',
        'OhOgO',
        'OgOgO',
        'OOOOO']


def coffer(img, x, y, w, h, seed=0, lid=None):
    """An iron-banded coffer: umber planks, a rounded lid with a lit top row,
    two wrought-iron corner straps with rivets, a gold lock plate on the seam
    and a deep bottom shadow."""
    r = random.Random(f'coffer:{seed}:{x}:{y}')
    lid = lid or max(3, h * 2 // 5)
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=1, heavy='br', fill_colour=UMBER[2])
    P.hline(img, x + 2, x + w - 3, y + 1, UMBER[3])
    P.vline(img, x + 1, y + 2, y + h - 3, UMBER[3])
    for xx in range(x + 4, x + w - 3, 4):           # lid and body planks
        P.vline(img, xx + r.choice((0, 0, 1)), y + lid + 2, y + h - 3, UMBER[1])
    P.hline(img, x + 1, x + w - 2, y + h - 2, UMBER[0])
    P.vline(img, x + w - 2, y + 2, y + h - 2, UMBER[1])
    P.hline(img, x + 1, x + w - 2, y + lid, INK[1])  # lid seam
    P.hline(img, x + 1, x + w - 2, y + lid + 1, IRON[1])
    P.hline(img, x + 2, x + w - 3, y + lid + 1, IRON[2])
    for bx in (x + 2, x + w - 5):                    # corner straps
        P.vline(img, bx, y + 1, y + h - 2, IRON[2])
        P.vline(img, bx + 1, y + 1, y + h - 2, IRON[0])
        P.put(img, bx, y + 2, IRON[3]); P.put(img, bx, y + h - 3, IRON[3])
    cx = x + w // 2
    P.sprite(img, cx - 2, y + lid - 1, LOCK)
    # a scuff on the lid
    sx = x + 5 + r.randint(0, max(0, w - 12))
    P.put(img, sx, y + 2, UMBER[1]); P.put(img, sx + 1, y + 3, UMBER[1])


def vault_door(img, x, y, w=15, h=30, seed=0):
    """The strongroom door set into the back of the vault alcove: an arched
    door of umber planks hung on two iron straps with rivets, a gold lock
    plate and an iron ring pull, standing on a stone sill. It is two cells
    tall and stands on the alcove floor, so it reads as architecture and
    never as a chest or a door item lying in one slot."""
    r = random.Random(f'door:{seed}:{x}:{y}')
    # the dressed-stone jamb and arch round the doorway, keystone on top
    P.ink_outline(img, (x - 2, y - 3, w + 4, h + 3), 'ink_1', radius=3, heavy='br', fill_colour=STONE[2])
    P.hline(img, x + 1, x + w - 2, y - 2, STONE[3])
    P.vline(img, x - 1, y + 1, y + h - 1, STONE[3])
    P.vline(img, x + w, y + 1, y + h - 1, STONE[1])
    for jy in (y + 6, y + 14, y + 22):                       # jamb block joints
        P.put(img, x - 1, jy, STONE[1]); P.put(img, x + w, jy + 3, STONE[0])
    P.sprite(img, x + w // 2 - 1, y - 3, ['ooo', 'oqo', 'opo'])  # keystone
    under = img.copy()
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=1, heavy='br', fill_colour=UMBER[2])
    # the arch: corners give back the masonry, the ink follows the curve
    for row, cut in ((0, 4), (1, 2), (2, 1)):
        for i in range(cut):
            for xx in (x + i, x + w - 1 - i):
                img.putpixel((xx, y + row), under.getpixel((xx, y + row)))
    P.hline(img, x + 4, x + w - 5, y, INK[1])
    for xx in (x + 2, x + 3):
        P.put(img, xx, y + 1, INK[1])
    for xx in (x + w - 4, x + w - 3):
        P.put(img, xx, y + 1, INK[0])
    P.put(img, x + 1, y + 2, INK[1]); P.put(img, x + w - 2, y + 2, INK[0])
    P.hline(img, x + 4, x + w - 5, y + 1, UMBER[3])          # lit head of the arch
    P.put(img, x + 2, y + 2, UMBER[3]); P.put(img, x + 3, y + 2, UMBER[3])
    P.vline(img, x + 1, y + 3, y + h - 3, UMBER[3])          # lit left stile
    for sx in range(x + 4, x + w - 3, 4):                    # plank seams
        P.vline(img, sx + r.choice((0, 0, 1)), y + 2, y + h - 3, UMBER[1])
    P.vline(img, x + w - 2, y + 3, y + h - 2, UMBER[1])
    P.hline(img, x + 1, x + w - 2, y + h - 2, UMBER[0])
    for sy in (y + 7, y + h - 9):                            # iron straps
        P.hline(img, x + 1, x + w - 2, sy, IRON[2])
        P.hline(img, x + 1, x + w - 2, sy + 1, IRON[0])
        for rx in (x + 2, x + 6, x + w - 3):
            P.put(img, rx, sy, IRON[3])
    cy = y + h // 2 - 2
    P.sprite(img, x + w // 2 - 2, cy, LOCK)
    P.sprite(img, x + w - 5, cy + 1, ['.c.', 'c.a', '.a.'])   # ring pull
    for _ in range(2):                                       # scuffs in the planks
        sx = r.randint(x + 2, x + w - 4); sy = r.randint(y + 10, y + h - 12)
        P.put(img, sx, sy, UMBER[1])
    P.hline(img, x - 1, x + w, y + h, STONE[2])              # stone sill
    P.put(img, x - 1, y + h, STONE[3]); P.put(img, x, y + h, STONE[3])


def coin_column(img, x, bottom, n, seed=0):
    """A column of ``n`` tarnished coins, 7 px wide, whose base sits on row
    ``bottom``; a few coins sit 1 px off the stack so it looks hand-stacked."""
    r = random.Random(f'coins:{seed}:{x}:{bottom}')
    P.hline(img, x + 1, x + 5, bottom, INK[0])
    off = 0
    for i in range(n):
        yy = bottom - 1 - 2 * i
        if i and r.random() < 0.22:
            off = 1 - off if off == 0 else 0
        P.sprite(img, x + off, yy - 1, ['oHHhhgO', 'ohhhggO'])
    top = bottom - 1 - 2 * (n - 1) - 2
    P.sprite(img, x + off, top, ['.ooooo.'])
    P.put(img, x + off + 2, top + 1, GOLD[2]); P.put(img, x + off + 3, top + 1, GOLD[2])
    return top


def coin_heap(img, x, y):
    """A few loose coins spilled on a floor or shelf (5 rows, 11 px)."""
    P.sprite(img, x, y, ['....ooo....',
                         '...oHhgo...',
                         '.ooohggoo..',
                         'oHhgoooHhgo',
                         '.ooo...ooo.'])


def scales(img, cx, y, tilt=1, h=13):
    """Gold-and-iron coin scales, 17 px wide and ``h`` tall, centred on
    column ``cx``. The left pan holds coins and hangs ``tilt`` px lower."""
    P.sprite(img, cx - 1, y, ['oHo', 'ohg'])                     # finial
    for i in range(-8, 9):                                       # tilted beam
        dy = round(-i * tilt / 8)
        by = y + 3 + dy
        P.put(img, cx + i, by - 1, INK[1])
        P.put(img, cx + i, by, GOLD[2] if i < 0 else GOLD[1])
        P.put(img, cx + i, by + 1, INK[0])
    P.put(img, cx - 9, y + 3 + tilt, INK[1]); P.put(img, cx + 9, y + 3 - tilt, INK[1])
    for yy in range(y + 2, y + h - 2):                           # post
        P.put(img, cx - 1, yy, INK[1]); P.put(img, cx, yy, IRON[2]); P.put(img, cx + 1, yy, IRON[0])
        P.put(img, cx + 2, yy, INK[0])
    P.sprite(img, cx - 1, y + 2, ['oHgO'])                       # pivot
    P.sprite(img, cx - 3, y + h - 2, ['ocdcbaO', 'oooooOO'])      # foot
    for side, end_dy, coins in ((-1, tilt, True), (1, -tilt, False)):
        ex = cx + side * 7
        top = y + 4 + end_dy
        py = top + 5
        P.line(img, ex, top, ex - 3, py - 1, GOLD[1] if side < 0 else GOLD[0])
        P.line(img, ex, top, ex + 3, py - 1, GOLD[0])
        P.sprite(img, ex - 3, py, ['oHHhhgO', '.ooooo.'])
        if coins:
            P.sprite(img, ex - 2, py - 2, ['.oo.', 'oHgo'])


def sealed_ledger(img, x, y, w=19, h=12, seed=0, cover=None):
    """A thick ledger lying closed: tooled leather cover with gold corner caps,
    page edges below and right, an iron strap round it pressed shut with a
    blood-wax seal and a ribbon tail."""
    cover = cover or (UMBER[1], UMBER[2], UMBER[3])
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=1, heavy='br', fill_colour=VELLUM[1])
    for xx in range(x + 2, x + w - 1, 2):                         # page edges
        P.put(img, xx, y + h - 2, VELLUM[0])
    P.vline(img, x + w - 2, y + 2, y + h - 3, VELLUM[0])
    cw, ch = w - 2, h - 3
    P.ink_outline(img, (x, y, cw, ch), 'ink_1', radius=1, fill_colour=cover[1])
    P.hline(img, x + 2, x + cw - 3, y + 1, cover[2])
    P.vline(img, x + 1, y + 2, y + ch - 3, cover[2])
    P.hline(img, x + 2, x + cw - 2, y + ch - 2, cover[0])
    for (gx, gy, rows) in ((x + 1, y + 1, ['Hh', 'h.']), (x + cw - 3, y + 1, ['hh', '.g']),
                           (x + 1, y + ch - 3, ['h.', 'hg']), (x + cw - 3, y + ch - 3, ['.g', 'gg'])):
        P.sprite(img, gx, gy, rows)
    sy = y + ch // 2
    P.hline(img, x, x + w - 1, sy - 1, IRON[2])               # strap round the book
    P.hline(img, x, x + w - 1, sy, IRON[0])
    P.put(img, x - 1, sy - 1, INK[1]); P.put(img, x - 1, sy, INK[1])
    sx = x + cw // 2
    P.wax_seal(img, sx, sy, 3, BLOOD, seed)
    P.sprite(img, sx, sy + 4, ['st', 'so', 'r.'])               # ribbon tail


def torch(img, cx, y):
    """A pitch torch in an iron ring bracket on a wall plate; ``y`` is the
    flame tip. Returns the flame centre for ``glow``."""
    P.sprite(img, cx - 4, y, ['....f....',
                              '....fF...',
                              '...fFf...',
                              '...fFFf..',
                              '..fFFFf..',
                              '..fFFFFf.',
                              '.efFFFFfe',
                              '..eFFFFe.',
                              '..o2ee2O.',
                              '..o3232O.',
                              '..o2121O.',
                              '...o32O..',
                              '.oocdcbao',
                              'oddcccbaO',
                              '.oocdbaoO',
                              '...o32O..',
                              '...o21O..',
                              '...o21O..',
                              '....oO...'])
    return cx, y + 4


def lantern(img, cx, y):
    icons.draw_motif(img, 'lantern', cx - 4, y)
    return cx, y + 5


def coin_banner(img, x, y, w, h, ramp=BLOOD, seed=0):
    """A treasury banner: tattered cloth with gold trim and a struck gold coin."""
    P.banner(img, x, y, w, h, ramp, seed, emblem=None)
    P.sprite(img, x + (w - 7) // 2, y + 5, COIN_EMBLEM)


def books(img, x, base, specs, lean_last=False):
    """A row of ledger spines standing on row ``base``: each spec is
    (width, height, (shadow, body, lit)). Two gold bands per spine."""
    for (w, h, (sh, body, lit)) in specs:
        top = base - h + 1
        P.ink_outline(img, (x, top, w, h), 'ink_1', radius=0, heavy='br', fill_colour=body)
        P.vline(img, x + 1, top + 1, base - 1, lit)
        if w >= 4:
            P.vline(img, x + w - 2, top + 1, base - 1, sh)
        for by in (top + 2, base - 3):
            P.hline(img, x + 1, x + w - 2, by, GOLD[1])
            P.put(img, x + 1, by, GOLD[2])
        if h >= 11 and w >= 4:                                    # blank gold label plate
            P.hline(img, x + 1, x + w - 2, top + h // 2 - 1, GOLD[0])
        x += w
    return x


def quill_inkwell(img, x, y):
    """A bone quill standing in an iron inkwell (13 rows)."""
    P.sprite(img, x, y, ['.........yy',
                         '........yxw',
                         '.......yxwo',
                         '......yxwo.',
                         '.....yxwo..',
                         '....yxwo...',
                         '....xwo....',
                         '...vo......',
                         '..oOo......',
                         '.oacbo.....',
                         'oacbbao....',
                         'oabbbao....',
                         '.ooooo.....'])


MINI_SCALES = ['hHHHHHHHh',
               '.h..h..h.',
               'hhh.h.hhh',
               '...ggg...']


def plaque_emblem(img, w):
    """Replace the wordless plaque's fleur with tiny gold coin scales."""
    cx = w // 2
    P.fill(img, (cx - 6, 2, 13, 4), IRON[0])
    P.sprite(img, cx - 4, 2, MINI_SCALES)


def top_chains(img, a, seed):
    P.chain(img, 12, 4, a.w // 2 - 22, 4, sag=2, seed=seed + 11)
    P.chain(img, a.w // 2 + 21, 4, a.w - 13, 4, sag=2, seed=seed + 12)


def bottom_chains(img, a, seed):
    H = a.h
    mid = a.w // 2
    for x0, x1 in ((8, mid - 8), (mid + 8, a.w - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3); P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.sprite(img, mid - 3, H - 8, COIN_EMBLEM)


# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------

class Out:
    def __init__(self, root=None):
        self.root = Path(root) if root else None

    def background(self, key):
        return geo.skin(key).background_path if self.root is None else self.root / 'menu' / f'{key}.png'

    def frame(self, key, layer_id):
        return geo.skin(key).frame_path(layer_id) if self.root is None else \
            self.root / 'frames' / key / f'{layer_id}.png'

    def buttons(self, states, key, button_id):
        return C.save_button_states(states, key, button_id, root=self.root)


# ---------------------------------------------------------------------------
# Shared button hand touches
# ---------------------------------------------------------------------------

GAVEL = ['.OOOOO.......',
         'OhHHHgO......',
         'OgggggOOOOOO.',
         'OhHHhgOhhhhgO',
         'OgggggOOOOOO.',
         '.OOOOO.......']

CROWN = ['.O...O...O.',
         'OHO.OHO.OHO',
         'OhHOHhHOHhO',
         'OhhHhshHhhO',
         'OgggggggggO',
         '.OOOOOOOOO.']


def plate_touches(img, b, emblem):
    """Economy primary plates: a gold emblem struck above the lettering and a
    gold flourish engraved under it."""
    cx = b.w // 2
    ew = len(emblem[0])
    P.sprite(img, cx - ew // 2, 3, emblem)
    P.gold_filigree(img, cx - 5, b.h - 8, 'flourish')


def tablet_coins(img, b):
    """Two coin roundels incised into the ends of the balance tablet, in
    stone tones only: a groove in shadow (stone_1) on the upper-left of each
    ring, its lit lip (stone_2) lower-right. Cut into the stone, never gold
    studs, so the read-only tablet carries no rivet-like hardware that would
    echo the pressable vellum strips."""
    cy = b.h // 2 - 1
    for x in (3, b.w - 5):
        P.sprite(img, x, cy - 1, ['.n.', 'n.p', '.p.'], {'n': STONE[1], 'p': STONE[2]})


def ledger_bookmark(img, x):
    """A blood ribbon bookmark hanging over the torn top of a ledger page."""
    P.sprite(img, x, 0, ['oso', 'oso', 'oso', 'oso', 'oto', 'r.r'])


def privacy_strip(key, b, seed):
    """The 36 px Privacy strip. Its label only fits in GRAVEN mixed case
    without rivets, and the 'y' descender hangs two rows below the cap
    height; ``compose.letter`` centres the caps, which leaves the descender
    one row off the bottom deckle so every pulse ring ran against it. The
    same strip and label, lettered one row higher: caps rows 5-11 and the
    descender on 12-13, centred on the strip with clear air for the rings."""
    img = C.new(b.w, b.h)
    x, y, w, h = C.secondary_face(img, b.body.tuple(), seed, rivets=False)
    C.letter(img, b, (x, y - 1, w, h), 'ink_0')
    return img


def paint_buttons(key, out, seed):
    s = geo.skin(key)
    for b in s.buttons:
        if key == 'economy_hub' and b.id == 'privacy':
            img = privacy_strip(key, b, seed)
        else:
            img = C.paint_button(key, b.id, seed=seed)
        if key == 'economy_hub':
            if b.id == 'auction':
                plate_touches(img, b, GAVEL)
            elif b.id == 'admin_shop':
                plate_touches(img, b, CROWN)
            elif b.id == 'balance':
                tablet_coins(img, b)
            elif b.id == 'history':
                ledger_bookmark(img, b.w - 8)      # History opens the ledger
        elif key == 'economy_log':
            if b.id == 'next':
                ledger_bookmark(img, 6)
        C.finish_button(img, key, b.id)
        out.buttons(C.button_states(img, key, b.id), key, b.id)


# ---------------------------------------------------------------------------
# economy_hub
# ---------------------------------------------------------------------------

def strap(img, x, y0, y1, rivet_rows):
    """A vertical iron ledger strap 3 px wide with gold rivets."""
    P.vline(img, x - 1, y0, y1, INK[1])
    P.vline(img, x, y0, y1, IRON[2])
    P.vline(img, x + 1, y0, y1, IRON[1])
    P.vline(img, x + 2, y0, y1, IRON[0])
    P.vline(img, x + 3, y0, y1, INK[0])
    for ry in rivet_rows:
        P.rivet(img, x, ry, 'gold', 3)


def hub_background(key, seed):
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    # iron ledger straps binding the control board down both margins
    rows = (21, 39, 57)
    strap(img, 3, 15, 72, rows)
    strap(img, 170, 15, 72, rows)
    # gilt page edge peeping between the title band and the board, and under it
    for x in range(8, 168):
        if x % 7 not in (3,):
            P.put(img, x, 15, GOLD[0])
    P.hline(img, 8, 167, 72, UMBER[0])
    for x in range(9, 167, 9):
        P.put(img, x, 71, GOLD[0])
    C.finish_background(img, key)
    return img


def hub_frame(key, seed):
    a = geo.skin(key).layer()
    img = C.base_frame(key, a.id, seed=seed)
    H = a.h
    lp, rp = a.left_panel, a.right_panel
    plaque_emblem(img, a.w)
    top_chains(img, a, seed)

    # ---- left panel: treasury banner, torch, scales in a niche, coin columns, coffer
    L0 = lp.x
    P.chain(img, L0 + 12, 9, L0 + 12, 13, seed=seed, shadow=None)
    P.chain(img, L0 + 28, 9, L0 + 28, 13, seed=seed + 1, shadow=None)
    coin_banner(img, L0 + 13, 15, 15, 34, BLOOD, seed)
    fx, fy = torch(img, L0 + 20, 56)
    P.glow(img, fx, fy + 2, 14, 'ember')
    P.arch_niche(img, (L0 + 7, 80, 27, 31), seed=seed)
    scales(img, L0 + 20, 92, tilt=1, h=15)
    P.glow(img, L0 + 20, 100, 9, 'ember')
    ledge(img, L0 + 5, 111, 31)
    P.moss_tuft(img, L0 + 8, 115, 4, seed=seed)
    coin_column(img, L0 + 6, 144, 4, seed)
    coin_column(img, L0 + 12, 144, 7, seed + 1)
    coin_column(img, L0 + 18, 144, 5, seed + 2)
    fx, fy = P.candle(img, L0 + 28, 136, height=8, lit=True, holder='gold', seed=seed)
    P.glow(img, fx, fy, 9, 'ember')
    ledge(img, L0 + 4, 145, 32)
    P.crack(img, L0 + 31, 152, 6, seed=seed, colour=STONE[0], light=STONE[3])
    coffer(img, L0 + 6, 160, 24, 14, seed)
    coin_heap(img, L0 + 25, 170)
    icons.draw_motif(img, 'bone', L0 + 3, H - 12)

    # ---- right panel: lantern, ledger on a lectern, chained key, coffers, gargoyle
    R0 = rp.x
    P.chain(img, R0 + 20, 9, R0 + 20, 19, seed=seed + 2)
    fx, fy = lantern(img, R0 + 20, 20)
    P.glow(img, fx, fy, 13, 'ember')
    ledge(img, R0 + 4, 56, 32)
    sealed_ledger(img, R0 + 6, 43, 21, 13, seed)
    fx, fy = P.candle(img, R0 + 31, 46, height=9, lit=True, holder='iron', seed=seed + 1)
    P.glow(img, fx, fy, 9, 'ember')
    P.moss_tuft(img, R0 + 24, 60, 5, seed=seed + 3)
    coin_banner(img, R0 + 13, 76, 13, 28, MOSS, seed + 1)
    P.chain(img, R0 + 7, 66, R0 + 7, 112, seed=seed + 4)
    icons.draw_motif(img, 'key', R0 + 3, 113)
    ledge(img, R0 + 4, 140, 32)
    coffer(img, R0 + 5, 121, 18, 19, seed + 2, lid=6)
    coffer(img, R0 + 23, 130, 12, 10, seed + 3)
    coin_column(img, R0 + 25, 129, 3, seed + 4)
    P.crack(img, R0 + 33, 150, 7, seed=seed + 5, colour=STONE[0], light=STONE[3])
    icons.draw_motif(img, 'gargoyle', R0 + 15, H - 28)

    bottom_chains(img, a, seed)
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------
# economy_log
# ---------------------------------------------------------------------------

def alcove(img, box, seed, shade='tl'):
    """A recess cut into the sheet: dark vault masonry with a deep ink_0 lip
    on the shadowed sides."""
    x, y, w, h = box
    P.stone_blocks(img, box, seed, VAULT, course=6, moss=0.05, cracks=0.3)
    if 't' in shade:
        P.hline(img, x, x + w - 1, y, INK[0])
    if 'l' in shade:
        P.vline(img, x, y, y + h - 1, INK[0])
    if 'r' in shade:
        P.vline(img, x + w - 1, y, y + h - 1, INK[1])


def log_background(key, seed):
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    # the vault alcove: a top shelf niche and two side columns round the cabinet
    alcove(img, (2, 15, 172, 13), seed, 'tl')
    alcove(img, (2, 28, 19, 79), seed + 1, 'l')
    alcove(img, (155, 28, 19, 79), seed + 2, 'r')
    # the shelf the vault's goods stand on (rests on the cabinet's iron frame)
    P.fill(img, (2, 28, 172, 3), STONE[2])
    P.hline(img, 2, 173, 28, STONE[3])
    P.hline(img, 2, 173, 30, STONE[0])
    P.hline(img, 2, 173, 27, INK[1])
    for x in (31, 77, 122, 160):
        P.put(img, x, 29, STONE[1]); P.put(img, x + 1, 29, STONE[1])
    # re-frame the cabinet so the shelf sits on its iron rim
    P.socket_well(img, P.merge_holes(s.content_slots))

    # ---- along the shelf (props stand on row 27, straddling cell edges) ----
    fx1, fy1 = P.candle(img, 6, 20, height=5, lit=True, holder='iron', seed=seed)
    coffer(img, 14, 17, 21, 11, seed)                       # across x 25
    coin_column(img, 37, 27, 3, seed)
    coin_column(img, 42, 27, 5, seed + 1)                   # across x 43
    coin_column(img, 48, 27, 2, seed + 2)
    sealed_ledger(img, 56, 16, 20, 12, seed)                # across x 61
    fx2, fy2 = P.candle(img, 80, 20, height=5, lit=True, holder='gold', seed=seed + 1)
    scales(img, 97, 16, tilt=1, h=12)                       # centred on the x 97 edge
    coin_heap(img, 108, 23)
    coin_column(img, 119, 27, 4, seed + 3)                  # across x 115 .. 125
    coffer(img, 128, 19, 16, 9, seed + 1)                   # across x 133
    coin_column(img, 146, 27, 3, seed + 4)
    coin_column(img, 151, 27, 5, seed + 5)                  # across x 151
    fx3, fy3 = P.candle(img, 164, 20, height=5, lit=True, holder='iron', seed=seed + 2)

    # ---- left column: coin banner, the strongroom door ----
    P.chain(img, 7, 32, 7, 35, seed=seed, shadow=None)
    coin_banner(img, 5, 36, 11, 34, BLOOD, seed)            # spans cells 9 .. 27
    vault_door(img, 5, 76, 13, 30, seed + 2)                # spans cells 27 and 36
    P.moss_tuft(img, 16, 73, 3, seed=seed)

    # ---- right column: torch, chained ledger, coin columns ----
    tx, ty = torch(img, 164, 32)
    P.chain(img, 164, 51, 164, 56, seed=seed + 6)
    sealed_ledger(img, 157, 57, 15, 20, seed + 1, cover=(BLOOD[0], BLOOD[1], BLOOD[2]))  # across y 70
    coin_column(img, 157, 105, 6, seed + 7)                 # across y 88
    coin_column(img, 164, 105, 9, seed + 8)
    P.moss_tuft(img, 170, 85, 3, seed=seed + 1)

    for (gx, gy, rr) in ((fx1, fy1, 8), (fx2, fy2, 9), (fx3, fy3, 8)):
        P.glow(img, gx, gy + 2, rr, 'ember')
    P.glow(img, tx, ty + 2, 14, 'ember')
    C.finish_background(img, key)
    return img


def log_frame(key, seed):
    a = geo.skin(key).layer()
    img = C.base_frame(key, a.id, seed=seed)
    H = a.h
    lp, rp = a.left_panel, a.right_panel
    plaque_emblem(img, a.w)
    top_chains(img, a, seed)

    # ---- left panel: the archive shelves of ledger spines, a torch
    L0 = lp.x
    U = (UMBER[1], UMBER[2], UMBER[3])
    B = (BLOOD[0], BLOOD[1], BLOOD[2])
    M = (MOSS[0], MOSS[1], MOSS[2])
    I = (IRON[0], IRON[1], IRON[2])
    fx, fy = torch(img, L0 + 20, 12)
    P.glow(img, fx, fy + 2, 14, 'ember')
    for k, (sy, specs) in enumerate((
            (52, [(4, 12, U), (5, 14, B), (4, 11, U), (4, 13, M), (5, 14, U), (4, 10, I), (4, 12, B)]),
            (84, [(5, 13, B), (4, 11, U), (4, 14, U), (5, 12, M), (4, 13, B), (4, 9, U)]),
            (116, [(4, 11, M), (5, 14, U), (4, 12, B), (4, 13, U), (5, 11, I)]))):
        books(img, L0 + 6, sy, specs)
        ledge(img, L0 + 4, sy + 1, 32)
    sealed_ledger(img, L0 + 25, 74, 10, 10, seed + 3, cover=B)
    coin_column(img, L0 + 28, 116, 3, seed)
    P.moss_tuft(img, L0 + 8, 121, 4, seed=seed)
    coin_banner(img, L0 + 13, 136, 15, 36, BLOOD, seed)
    P.chain(img, L0 + 9, 128, L0 + 9, 134, seed=seed, shadow=None)
    P.chain(img, L0 + 31, 128, L0 + 31, 134, seed=seed + 1, shadow=None)
    ledge(img, L0 + 4, 205, 32)
    coffer(img, L0 + 6, 188, 22, 17, seed, lid=6)
    coin_heap(img, L0 + 22, 200)
    P.crack(img, L0 + 31, 214, 6, seed=seed, colour=STONE[0], light=STONE[3])
    icons.draw_motif(img, 'bone', L0 + 4, H - 12)

    # ---- right panel: hanging sealed ledger, quill and inkwell, candle clock, scales
    R0 = rp.x
    P.chain(img, R0 + 20, 9, R0 + 20, 16, seed=seed + 2)
    sealed_ledger(img, R0 + 10, 17, 21, 24, seed + 1)
    fx, fy = lantern(img, R0 + 20, 50)
    P.chain(img, R0 + 20, 44, R0 + 20, 49, seed=seed + 7, shadow=None)
    P.glow(img, fx, fy, 13, 'ember')
    ledge(img, R0 + 4, 92, 32)
    quill_inkwell(img, R0 + 6, 79)
    icons.draw_motif(img, 'candle_clock', R0 + 27, 79)
    P.glow(img, R0 + 29, 80, 8, 'ember')
    P.moss_tuft(img, R0 + 20, 96, 5, seed=seed + 3)
    P.arch_niche(img, (R0 + 6, 108, 27, 33), seed=seed)
    scales(img, R0 + 19, 121, tilt=1, h=15)
    P.glow(img, R0 + 19, 128, 9, 'ember')
    ledge(img, R0 + 4, 141, 32)
    coin_column(img, R0 + 7, 172, 4, seed + 1)
    coin_column(img, R0 + 13, 172, 8, seed + 2)
    coin_column(img, R0 + 19, 172, 6, seed + 3)
    coin_column(img, R0 + 26, 172, 3, seed + 4)
    ledge(img, R0 + 4, 173, 32)
    P.crack(img, R0 + 33, 182, 7, seed=seed + 5, colour=STONE[0], light=STONE[3])
    coffer(img, R0 + 5, 192, 20, 13, seed + 5)
    fx, fy = P.candle(img, R0 + 29, 196, height=7, lit=True, holder='iron', seed=seed + 6)
    P.glow(img, fx, fy, 9, 'ember')
    ledge(img, R0 + 4, 205, 32)
    P.moss_tuft(img, R0 + 12, 209, 5, seed=seed + 7)

    bottom_chains(img, a, seed)
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------

PAINTERS = {
    'economy_hub': (hub_background, hub_frame),
    'economy_log': (log_background, log_frame),
}


def paint(key, out):
    bg_fn, frame_fn = PAINTERS[key]
    s = geo.skin(key)
    seed = SEED + (0 if key == 'economy_hub' else 100)
    C.save_png(bg_fn(key, seed), out.background(key))
    paint_buttons(key, out, seed)
    for a in s.art_layers:
        C.save_png(frame_fn(key, seed), out.frame(key, a.id))
    print('painted', key)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out-root', help='write DIR/{menu,buttons,frames}/... instead of pack-source')
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    args = ap.parse_args(argv)
    out = Out(args.out_root)
    for key in args.skin or SKINS:
        paint(key, out)


if __name__ == '__main__':
    main()
