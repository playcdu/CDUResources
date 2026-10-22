#!/usr/bin/env python3
"""Soulrend painter "adminshop": the quartermaster's armoury.

    python tools/soulrend/paint_adminshop.py                 # all four skins
    python tools/soulrend/paint_adminshop.py --skin admin_shop_search
    python tools/soulrend/paint_adminshop.py --out-root DIR  # DIR laid out like textures/

Paints, deterministically, the background and the outer frame of the four
admin shop skins (all chest_6, all 54 top cells native, no buttons):

    admin_shop_categories   a cabinet of wordless drawer fronts
    admin_shop_listings     crates and sacks on the quartermaster's shelves
    admin_shop_search       a scrying lens on the counter
    admin_shop_configured   a writ pinned to the wall with a dagger, wax-sealed

The family (shared by all four): the armoury wall of a dungeon keep. Left
panel: a peg rail of heraldic shields, a weapon rack (spear, bearded axe,
sword hilt-up, flanged mace), a hook of keys, a candle sconce, a heraldic
banner and an ash-pit brazier. Right panel: a hanging lantern, the
per-screen piece, a ledge with the quartermaster's ledger and its seal, hammer
and tongs on pegs and the iron-bound requisition chest. Frames carry no
words. Backgrounds keep the shared base (vellum bands, iron-framed sockets)
with tarnished-gold seam rivets on the native grid and armoury hasps on the
bands. The inventory band stays plain vellum: no motif enters the inventory
text rows (a pale icon after a ruled line there read as a search field or a
UI control the screen does not have).

Licence: code MIT; artwork CC0-1.0.
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

SKINS = ('admin_shop_categories', 'admin_shop_listings', 'admin_shop_search', 'admin_shop_configured')
SEEDS = {'admin_shop_categories': 41, 'admin_shop_listings': 43,
         'admin_shop_search': 47, 'admin_shop_configured': 53}
TEXTURES = geo.ROOT / 'pack-source' / 'assets' / 'quasar_gui' / 'textures'


# ---------------------------------------------------------------------------
# Sprites (original, CC0-1.0). Colour key: primitives.SK
# ---------------------------------------------------------------------------

# arming sword, drawn hilt-up as it stands in a rack
def sword_rows(blade):
    return [
        '...ooo...',
        '..oHhgo..',
        '...ooo...',
        '...o3o...',
        '...o1o...',
        '...o3o...',
        '...o1o...',
        '.ooooooo.',
        'oHHhshhgo',
        '.ooo.ooo.',
    ] + ['..odcbo..'] * 3 + ['..odcao..'] + ['..odcbo..'] * (blade - 4) + [
        '...odo...',
        '...odo...',
        '....o....',
    ]


# leaf-bladed spear, point up; the shaft is extended by draw_polearm
SPEAR_HEAD = [
    '...o...',
    '..odo..',
    '..odo..',
    '.odcbo.',
    '.odcbo.',
    '.odcbo.',
    '..ocbo.',
    '..oco..',
    '..obo..',
    '..oho..',
    '..ogo..',
]

# bearded axe head on its socket; the shaft is extended by draw_polearm
AXE_HEAD = [
    '....o.......',
    '...odo......',
    '...obo...o..',
    '...obo..odo.',
    '.oooboooccdo',
    'odcbbbccccdo',
    '.oooboobcbdo',
    '...obo.obbdo',
    '...obo..obdo',
    '...obo...odo',
    '...oho....o.',
    '...ogo......',
]

# flanged mace head
MACE_HEAD = [
    '..o.o..',
    '.odoco.',
    'odcdcbo',
    'ocdcbbo',
    'odcbcao',
    'obcbbao',
    '.oabao.',
    '..oho..',
    '..ogo..',
]

# iron key hanging bow-up
KEY_V = [
    '.ooo.',
    'od.co',
    'oc.bo',
    '.obo.',
    '.oco.',
    '.obo.',
    '.ocoo',
    '.obco',
    '.ocoo',
    '.obbo',
    '.ooo.',
]
KEY_V_GOLD = [r.replace('d', 'H').replace('c', 'h').replace('b', 'g').replace('a', 'g') for r in KEY_V]

# grain sack tied at the neck (burlap: umber_3 / vellum_0)
SACK = [
    '....o.o....',
    '...ohoho...',
    '....ooo....',
    '...o3v2o...',
    '..o3vv22o..',
    '.o3vv3221o.',
    'o3vv33v221o',
    'o3v33vv221o',
    'o3v3v3v221o',
    'o33v3v2211o',
    'o3322221110',
    '.o2222111o.',
    '..ooooooo..',
]

# dagger driven into the wall, hilt out (pins the writ)
DAGGER = [
    '..ooo..',
    '.oHhgo.',
    '..ooo..',
    '..o3o..',
    '..o1o..',
    '..o3o..',
    'ooooooo',
    'oHhshgo',
    'ooooooo',
    '..odo..',
    '...o...',
]

# inkwell with a quill
INKWELL = [
    '.......y.',
    '......yw.',
    '.....yw..',
    '....yw...',
    '...yw....',
    '..oiooo..',
    '.oOOOOOo.',
    'odcccbbao',
    'ocbbbbbao',
    '.ooooooo.',
]


def _rows_fill(rows, ch_from, ch_to):
    return [r.replace(ch_from, ch_to) for r in rows]


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

HASP = ['oooo', 'obco', 'ocdo', 'obbo', 'obao', 'oOao', 'oOho', 'obao', 'obao', 'ocbo', 'obao', 'oaao', 'oooo']


def paint_background(key):
    s = geo.skin(key)
    seed = SEEDS[key]
    img = C.base_background(key, seed=seed)
    tband, _ = C.bands(key)
    # tarnished-gold seam rivets on the native grid's iron ring: the
    # quartermaster's brass studs (only where the base put an iron_3 rivet)
    cb = s.content_bbox
    for y in range(cb.y - 3, cb.bottom + 3):
        for x in range(cb.x - 3, cb.right + 3):
            if P.get(img, x, y)[:3] == IRON[3] and not (
                    cb.x - 1 <= x <= cb.right and cb.y - 1 <= y <= cb.bottom):
                P.put(img, x, y, GOLD[2])
    # armoury hasps with a keyhole replace the plain clasps on the title band
    for x in (tband.x, tband.right - 4):
        P.sprite(img, x, tband.y, HASP[:tband.h - 1] + ['oooo'])
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frame helpers
# ---------------------------------------------------------------------------

def beam(img, x, y, w, h=3, ramp=UMBER, seed=0):
    """A short timber beam/plank with ink outline, lit top, grain."""
    P.ink_outline(img, (x - 1, y - 1, w + 2, h + 2), 'ink_1', radius=0, heavy='b', fill_colour=ramp[2])
    P.hline(img, x, x + w - 1, y, ramp[3])
    if h >= 3:
        P.hline(img, x, x + w - 1, y + h - 1, ramp[1])
    r = P._rng(seed, 'beam', x, y)
    for _ in range(max(1, w // 9)):
        gx = r.randint(x + 1, x + max(1, w - 4))
        P.hline(img, gx, gx + r.randint(1, 3), y + h // 2, ramp[1])


def post(img, x, y, h, ramp=UMBER):
    """A 3 px timber post (outline included is 5 px)."""
    P.ink_outline(img, (x - 1, y - 1, 5, h + 2), 'ink_1', radius=0, heavy='r', fill_colour=ramp[2])
    P.vline(img, x, y, y + h - 1, ramp[3])
    P.vline(img, x + 2, y, y + h - 1, ramp[1])


def plank_board(img, x, y, w, h, seed=0):
    """A dark backing board of vertical umber planks (iron reads on it)."""
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=0, heavy='br', fill_colour=UMBER[1])
    P.hline(img, x + 1, x + w - 2, y + 1, UMBER[2])
    r = P._rng(seed, 'board', x, y)
    jx = x + 5
    while jx < x + w - 2:
        P.vline(img, jx, y + 1, y + h - 2, UMBER[0])
        jx += 5
    for _ in range(w * h // 90):
        gx, gy = r.randint(x + 1, x + w - 2), r.randint(y + 2, y + h - 4)
        P.vline(img, gx, gy, gy + r.randint(1, 2), UMBER[0] if r.random() < 0.6 else UMBER[2])


def peg(img, x, y):
    P.sprite(img, x, y, ['oco', 'oba', '.o.'])


def draw_polearm(img, head, x, y, total, shaft_col):
    """Head sprite at (x, y); umber shaft continues to row y + total - 1."""
    P.sprite(img, x, y, head)
    hh = len(head)
    sx = x + shaft_col
    for j in range(hh, total - 2):
        P.put(img, sx - 1, y + j, 'ink_1')
        P.put(img, sx + 1, y + j, 'ink_0')
        P.put(img, sx, y + j, UMBER[3] if (j // 5) % 3 == 0 else UMBER[2])
    P.sprite(img, sx - 1, y + total - 2, ['oao', 'ooo'])


def round_shield(img, cx, cy, r=6, seed=0):
    """Round planked shield: iron rim, umber planks, tarnished-gold boss."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 > r * r + r:
                continue
            if d2 > (r - 1) ** 2 + (r - 1):
                P.put(img, x, y, 'ink_1' if x + y < cx + cy else 'ink_0')
            elif d2 > (r - 2) ** 2 + (r - 2):
                P.put(img, x, y, IRON[2] if x + y < cx + cy else IRON[0])
            else:
                plank = (x - cx + r) // 3
                P.put(img, x, y, UMBER[3] if plank % 2 == 0 else UMBER[2])
                if (x - cx + r) % 3 == 2:
                    P.put(img, x, y, UMBER[1])
    P.sprite(img, cx - 2, cy - 2, ['.ooo.', 'oHhgo', 'ohHgo', 'oggOo', '.ooo.'])
    for (dx, dy) in ((-r + 2, 0), (r - 2, 0), (0, -r + 2), (0, r - 2)):
        P.put(img, cx + dx, cy + dy, IRON[3])


def strap(img, x, y0, y1):
    P.vline(img, x, y0, y1, 'ink_1')


def sconce(img, x, y, seed):
    """Iron wall sconce with a lit candle; returns the flame centre."""
    P.sprite(img, x - 3, y + 8, ['occcco', '.obao.', '..oo..', '..oa..', '..ob..', '...o..'])
    return P.candle(img, x - 1, y, height=6, lit=True, holder=None, seed=seed)


def stone_ledge(img, x, y, w, seed=0, brackets=True):
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0, heavy='b')
    if brackets:
        for bx in (x + 2, x + w - 4):
            P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


def floor(img, x, y, w, h=5, seed=0):
    """Worn flagstone floor across a panel: lit lip, dark joints."""
    P.fill(img, (x, y, w, h), STONE[1])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 1, STONE[2])
    P.hline(img, x, x + w - 1, y - 1, 'ink_1')
    r = P._rng(seed, 'floor', x, y)
    jx = x + r.randint(4, 9)
    while jx < x + w - 2:
        P.vline(img, jx, y + 1, y + h - 1, STONE[0])
        jx += r.randint(8, 13)
    P.hline(img, x, x + w - 1, y + h - 1, STONE[0])


def requisition_chest(img, x, y, seed=0):
    """Iron-bound requisition chest, 28x17, with a gold lock plate."""
    w, h = 28, 17
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=1, heavy='br', fill_colour=UMBER[2])
    # lid: a rounded top, lit
    P.hline(img, x + 2, x + w - 3, y + 1, UMBER[3])
    P.hline(img, x + 1, x + w - 2, y + 2, UMBER[3])
    P.hline(img, x + 1, x + w - 2, y + 5, UMBER[1])
    P.hline(img, x + 1, x + w - 2, y + 6, 'ink_1')            # lid seam
    P.hline(img, x + 1, x + w - 2, y + 7, UMBER[3])
    P.hline(img, x + 1, x + w - 2, y + 11, UMBER[1])           # plank joint
    P.hline(img, x + 1, x + w - 2, y + h - 2, UMBER[0])
    r = P._rng(seed, 'chest', x, y)
    for _ in range(4):
        gx = r.randint(x + 6, x + w - 9)
        gy = r.choice((y + 3, y + 9, y + 13))
        P.hline(img, gx, gx + 2, gy, UMBER[1])
    # iron bands with rivets
    for bx in (x + 4, x + w - 7):
        P.vline(img, bx, y + 1, y + h - 2, IRON[2])
        P.vline(img, bx + 1, y + 1, y + h - 2, IRON[1])
        P.vline(img, bx + 2, y + 1, y + h - 2, IRON[0])
        for ry in (y + 3, y + 9, y + 14):
            P.put(img, bx + 1, ry, IRON[3])
    # iron corner caps
    for (cx_, cy_, rows) in ((x, y + h - 4, ['oo..', 'ocb.', 'oba.', 'oooo']),
                             (x + w - 4, y + h - 4, ['..oo', '.bao', '.aao', 'oooo'])):
        P.sprite(img, cx_, cy_, rows)
    # gold lock plate over the seam, keyhole
    lx = x + w // 2 - 3
    P.sprite(img, lx, y + 4, ['ooooooo', 'oHHhhgo', 'oHhOhgo', 'ohhOhgo', 'ohhhggo', '.ohhgo.', '..ooo..'])
    # cast shadow on the floor
    P.hline(img, x + 2, x + w, y + h, 'ink_0')


KEY_RING = ['..ooo..', '.oc.bo.', 'oc...ao', 'ob...ao', '.oa.ao.', '..ooo..']


def hanging_keys(img, x, y, seed=0):
    """A small key board: three keys on iron pegs (the middle one gold)."""
    plank_board(img, x, y, 21, 17, seed + 7)
    P.hline(img, x + 1, x + 19, y + 1, UMBER[3])
    for i, rows in enumerate((KEY_V, KEY_V_GOLD, KEY_V[:9] + ['.ooo.'])):
        kx = x + 2 + i * 6
        P.sprite(img, kx + 1, y + 2, ['oco'])
        P.sprite(img, kx, y + 3 + (i % 2), rows)


def crossed_swords(img, cx, cy, half=10, crest='cross'):
    """Wall trophy: two swords crossed behind a heraldic shield."""
    for sgn in (1, -1):
        x0, y0 = cx - sgn * half, cy - half          # tip (top)
        x1, y1 = cx + sgn * (half - 3), cy + half - 3  # hilt end (bottom)
        pts = P.line_points(x0, y0, x1, y1)
        for (px, py) in pts:
            P.put(img, px, py + 1, 'ink_0')
            P.put(img, px - sgn, py, 'ink_1')
        for k, (px, py) in enumerate(pts):
            hilt = k >= len(pts) - 5
            P.put(img, px, py, (UMBER[2] if k % 2 else UMBER[3]) if hilt else IRON[3 if k < 2 else 2])
            if not hilt:
                P.put(img, px + sgn, py, IRON[1]) if k > 1 else None
        gx, gy = pts[len(pts) - 6]
        P.sprite(img, gx - 2, gy - 2, ['O...O', '.h.h.', '..H..', '.h.g.', 'O...O'] if sgn == 1 else
                 ['O...O', '.h.g.', '..H..', '.h.g.', 'O...O'])
        ex, ey = pts[-1]
        P.sprite(img, ex - 1, ey, ['oHo', '.o.'])
    w, h = icons.crest_size(crest)
    icons.draw_crest(img, crest, cx - w // 2, cy - h // 2)


def brazier(img, x, y):
    """The armoury's ash-pit brazier on a stone plinth; returns flame point."""
    icons.draw_motif(img, 'brazier', x, y)
    P.fill(img, (x + 2, y + 9, 7, 3), STONE[2])
    P.hline(img, x + 2, x + 8, y + 9, STONE[3])
    P.ink_outline(img, (x + 1, y + 8, 9, 5), 'ink_1', radius=0, heavy='br')
    return x + 5, y + 1


# ---------------------------------------------------------------------------
# Per-screen pieces (right panel, box x 219..251, y 28..112)
# ---------------------------------------------------------------------------

def drawer_cabinet(img, x, y, seed=0):
    """Categories: a tall cabinet of wordless drawer fronts, each with a blank
    brass label holder and a ring pull; one drawer stands ajar."""
    w, h = 31, 70
    # cornice
    P.ink_outline(img, (x - 1, y, w + 2, 4), 'ink_1', radius=0, heavy='b', fill_colour=UMBER[2])
    P.hline(img, x, x + w - 1, y + 1, UMBER[3])
    P.ink_outline(img, (x, y + 3, w, h - 3), 'ink_1', radius=0, heavy='br', fill_colour=UMBER[1])
    P.vline(img, x + 1, y + 4, y + h - 2, UMBER[2])
    P.vline(img, x + w // 2, y + 4, y + h - 5, UMBER[0])
    rows = 5
    dh = 11
    for i in range(rows):
        for j in range(2):
            dx = x + 2 + j * 14
            dy = y + 5 + i * 12
            ajar = (i, j) == (2, 1)
            if ajar:
                dy -= 0
                P.hline(img, dx, dx + 12, dy + dh, 'ink_0')
            P.ink_outline(img, (dx, dy, 13, dh), 'ink_1', radius=0, heavy='br', fill_colour=UMBER[2])
            P.hline(img, dx + 1, dx + 11, dy + 1, UMBER[3])
            P.hline(img, dx + 1, dx + 11, dy + dh - 2, UMBER[1])
            # blank brass label holder
            P.sprite(img, dx + 3, dy + 2, ['ggggggg', 'gyxxxwg', 'gxxwxxg', 'hhhhhhg'])
            # ring pull
            P.sprite(img, dx + 5, dy + 6, ['.H.', 'h.g', '.g.'])
            if ajar:
                # the drawer pulled out a pixel: dark gap above, lit edge
                P.hline(img, dx, dx + 12, dy - 1, 'ink_0')
                P.put(img, dx + 13, dy + 1, 'ink_0')
    # plinth and feet
    fy = y + h
    P.ink_outline(img, (x - 1, fy - 1, w + 2, 4), 'ink_1', radius=0, heavy='b', fill_colour=UMBER[2])
    P.hline(img, x, x + w - 1, fy, UMBER[3])
    P.sprite(img, x + 1, fy + 3, ['ooo', 'o2o', 'ooo'])
    P.sprite(img, x + w - 4, fy + 3, ['ooo', 'o2o', 'ooo'])
    return fy + 5


def crate(img, x, y, w, h, seed=0):
    """Plank crate with a diagonal brace and iron corners."""
    P.ink_outline(img, (x, y, w, h), 'ink_1', radius=0, heavy='br', fill_colour=UMBER[2])
    P.ink_outline(img, (x + 1, y + 1, w - 2, h - 2), UMBER[3], radius=0)
    P.hline(img, x + 2, x + w - 3, y + h - 2, UMBER[1])
    P.vline(img, x + w - 2, y + 2, y + h - 2, UMBER[1])
    for py in range(y + 4, y + h - 3, 3):
        P.hline(img, x + 2, x + w - 3, py, UMBER[1])
    P.line(img, x + 2, y + h - 3, x + w - 3, y + 2, UMBER[3])
    P.line(img, x + 2, y + h - 2, x + w - 2, y + 2, UMBER[0])
    for (cx_, cy_) in ((x, y), (x + w - 2, y), (x, y + h - 2), (x + w - 2, y + h - 2)):
        P.fill(img, (cx_, cy_, 2, 2), IRON[1])
        P.put(img, cx_, cy_, IRON[3] if (cx_, cy_) == (x, y) else IRON[2])
    P.hline(img, x + 1, x + w, y + h, 'ink_0')


def crates_and_sacks(img, x, y, seed=0):
    """Listings: the quartermaster's shelves, stocked with crates and sacks."""
    # upper shelf on two iron brackets
    sy = y + 30
    beam(img, x, sy, 32, 3, seed=seed)
    for bx in (x + 3, x + 26):
        P.sprite(img, bx, sy + 4, ['oco', '.oa', '..o'])
    crate(img, x + 1, sy - 13, 14, 13, seed)
    P.sprite(img, x + 17, sy - 13, SACK)
    P.sprite(img, x + 27, sy - 6, ['.oo.', 'o3bo', 'o23o', 'o21o', 'oooo'])
    # lower shelf
    sy2 = y + 70
    beam(img, x, sy2, 32, 3, seed=seed + 1)
    for bx in (x + 3, x + 26):
        P.sprite(img, bx, sy2 + 4, ['oco', '.oa', '..o'])
    crate(img, x + 13, sy2 - 18, 18, 18, seed + 2)
    crate(img, x + 17, sy2 - 27, 11, 9, seed + 3)
    P.sprite(img, x + 1, sy2 - 13, SACK)
    return sy2 + 8


def scrying_counter(img, x, y, seed=0):
    """Search: a scrying lens on a brass stand on the quartermaster's counter;
    cold soul-light pools round the glass."""
    cy = y + 62
    # counter top and front
    P.ink_outline(img, (x - 1, cy, 34, 4), 'ink_1', radius=0, heavy='b', fill_colour=UMBER[2])
    P.hline(img, x, x + 31, cy + 1, UMBER[3])
    P.ink_outline(img, (x + 1, cy + 3, 30, 18), 'ink_1', radius=0, heavy='br', fill_colour=UMBER[1])
    for px in range(x + 3, x + 30, 7):
        P.vline(img, px, cy + 4, cy + 19, UMBER[2])
        P.vline(img, px + 1, cy + 4, cy + 19, UMBER[0])
    P.hline(img, x + 2, x + 29, cy + 10, IRON[1])
    P.hline(img, x + 2, x + 29, cy + 11, IRON[0])
    for px in range(x + 4, x + 29, 7):
        P.put(img, px, cy + 10, IRON[3])
    # lens: gold ring, soul glass
    lx, ly, r = x + 15, y + 34, 9
    for yy in range(ly - r - 1, ly + r + 2):
        for xx in range(lx - r - 1, lx + r + 2):
            d2 = (xx - lx) ** 2 + (yy - ly) ** 2
            if d2 > r * r + r:
                continue
            lit = (xx - lx) + (yy - ly) < 0
            if d2 > (r - 1) ** 2 + (r - 1):
                P.put(img, xx, yy, 'ink_1' if lit else 'ink_0')
            elif d2 > (r - 2) ** 2 + (r - 2):
                P.put(img, xx, yy, GOLD[2] if lit else GOLD[0])
            elif d2 > (r - 3) ** 2 + (r - 3):
                P.put(img, xx, yy, GOLD[1] if lit else 'ink_1')
            else:
                P.put(img, xx, yy, SOUL[0])
    # cold light pools round the glass (the glass itself stays deep)
    P.glow(img, lx, ly, 16, 'soul')
    for yy in range(ly - r + 3, ly + r - 2):
        for xx in range(lx - r + 3, lx + r - 2):
            if (xx - lx) ** 2 + (yy - ly) ** 2 <= (r - 3) ** 2 + (r - 3):
                P.put(img, xx, yy, SOUL[0])
    # glints and depth inside the glass
    P.sprite(img, lx - 5, ly - 5, ['.LL', 'Ll.', 'L..'])
    P.sprite(img, lx - 1, ly - 3, ['l'])
    P.sprite(img, lx + 2, ly + 2, ['..l', '.ll', 'll.'])
    for (dx, dy) in ((-3, 3), (3, -3), (0, 4)):
        P.put(img, lx + dx, ly + dy, INK[1])
    # brass yoke and stand
    P.sprite(img, lx - 1, ly + r, ['ohgo', 'oHgo', 'ohgo', 'oHgo'])
    P.sprite(img, lx - 1, ly + r + 4, ['ohgo'] * (cy - (ly + r + 4) - 3))
    P.sprite(img, lx - 4, cy - 3, ['.oooooooo.', 'oHHhhhhggo', 'oooooooooo'])
    return cy + 22


def pinned_writ(img, x, y, seed=0):
    """Configured: a writ nailed to the wall with a dagger, closed with a
    blood-wax seal and ribbon tails; ruled lines only, never words."""
    wx, wy, ww, wh = x + 4, y + 8, 24, 40
    P.vellum_strip(img, (wx, wy, ww, wh), seed, outline='ink_1', deckle='lr', heavy='br')
    # ruled lines (pale, wordless)
    for k, ly in enumerate(range(wy + 8, wy + wh - 12, 3)):
        r = P._rng(seed, 'rule', ly)
        x0 = wx + 3 + (2 if k == 0 else 0)
        x1 = wx + ww - 4 - r.randint(0, 6)
        P.hline(img, x0, x1, ly, VELLUM[0])
    P.torn_edge(img, (wx, wy + wh - 4, ww, 4), 'b', seed, depth=2)
    # blood seal with ribbon tails at the bottom right
    sx, sy = wx + ww - 7, wy + wh - 9
    P.sprite(img, sx - 2, sy + 4, ['.ss.ss', 'osroto', 'ostorso', '.ro..ro', '.o....o'])
    P.wax_seal(img, sx, sy, 5, BLOOD, seed, emblem='tower')
    # the dagger pinning the writ: blade into the wall, hilt standing out
    dx, dy = wx + ww // 2, wy - 6
    P.sprite(img, dx - 3, dy, DAGGER)
    P.put(img, dx, dy + 10, 'ink_0')
    # a scuff of wax drip below
    P.put(img, sx + 1, sy + 7, BLOOD[1])
    # a small shelf with the inkwell and quill the writ was signed with
    beam(img, x + 2, y + 72, 28, 2, seed=seed)
    for bx in (x + 4, x + 25):
        P.sprite(img, bx, y + 75, ['oco', '.oa', '..o'])
    P.sprite(img, x + 5, y + 62, INKWELL)
    P.sprite(img, x + 17, y + 66, ['.oooooo.', 'o2333321o', 'oxyyyyxwo', 'oooooooooo'[:9]])
    return wy + wh


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def paint_frame(key):
    s = geo.skin(key)
    a = s.layer()
    seed = SEEDS[key]
    img = C.base_frame(key, seed=seed)
    H = a.h
    L0, R0 = a.left_panel.x, a.right_panel.x + 3           # usable left edges

    # ---- top strip: chains from the corners to the plaque ------------------
    P.chain(img, 12, 4, a.w // 2 - 22, 4, sag=2, seed=seed + 11)
    P.chain(img, a.w // 2 + 21, 4, a.w - 13, 4, sag=2, seed=seed + 12)

    # ---- left panel ----------------------------------------------------------
    # peg rail of heraldic shields
    beam(img, L0 + 5, 11, 30, 2, seed=seed)
    for px in (L0 + 9, L0 + 20, L0 + 30):
        P.sprite(img, px - 1, 10, ['oco'])
    icons.draw_crest(img, 'chevron', L0 + 5, 16)
    strap(img, L0 + 9, 13, 15)
    round_shield(img, L0 + 20, 21, 6, seed)
    strap(img, L0 + 20, 13, 14)
    icons.draw_crest(img, 'key', L0 + 26, 16)
    strap(img, L0 + 30, 13, 15)

    # weapon rack: plank back board, posts, weapons, front rails, trough
    rx0, rx1 = L0 + 4, L0 + 33
    plank_board(img, L0 + 6, 50, 28, 56, seed)
    post(img, rx0, 46, 64)
    post(img, rx1, 46, 64)
    draw_polearm(img, SPEAR_HEAD, L0 + 7, 30, 78, 3)
    draw_polearm(img, AXE_HEAD, L0 + 13, 38, 70, 4)
    P.sprite(img, L0 + 20, 49, sword_rows(41))
    draw_polearm(img, MACE_HEAD, L0 + 27, 63, 45, 3)
    beam(img, rx0 - 1, 76, 34, 2, seed=seed + 1)
    beam(img, rx0 - 1, 95, 34, 2, seed=seed + 2)
    beam(img, rx0 - 2, 106, 36, 3, seed=seed + 3)

    # ring of keys on a wall hook and a candle sconce
    hanging_keys(img, L0 + 5, 120, seed)
    fx, fy = sconce(img, L0 + 32, 126, seed)
    P.glow(img, fx, fy + 2, 12, 'ember')
    P.moss_tuft(img, L0 + 4, 113, 5, seed=seed + 9)

    # heraldic banner of the armoury
    C.side_banner(img, geo.Rect(L0 + 4, 0, 32, 0), y=168, seed=seed, ramp=BLOOD, crest='tower', h=32)

    # floor, brazier and a moss-damp corner
    floor(img, L0 + 3, 222, 36, 6, seed)
    bx, by = brazier(img, L0 + 15, 208)
    P.glow(img, bx, by, 12, 'ember')
    P.moss_tuft(img, L0 + 6, 221, 4, seed=seed)
    P.crack(img, L0 + 33, 150, 7, seed=seed, colour=STONE[0], light=STONE[3])

    # ---- right panel ---------------------------------------------------------
    # hanging lantern
    P.chain(img, R0 + 16, 9, R0 + 16, 15, seed=seed + 2)
    icons.draw_motif(img, 'lantern', R0 + 12, 16)
    P.glow(img, R0 + 16, 21, 12, 'ember')

    piece = {'admin_shop_categories': drawer_cabinet,
             'admin_shop_listings': crates_and_sacks,
             'admin_shop_search': scrying_counter,
             'admin_shop_configured': pinned_writ}[key]
    piece(img, R0 + 1, 32, seed)

    # ledge with the quartermaster's ledger, its seal and a candle
    stone_ledge(img, R0 + 2, 132, 30, seed)
    icons.draw_motif(img, 'ledger', R0 + 4, 121)
    P.wax_seal(img, R0 + 20, 128, 3, BLOOD, seed)
    fx, fy = P.candle(img, R0 + 26, 124, height=7, lit=True, holder='iron', seed=seed)
    P.glow(img, fx, fy + 1, 10, 'ember')
    P.moss_tuft(img, R0 + 9, 138, 5, seed=seed + 4)

    # tool board: hammer and tongs on pegs
    plank_board(img, R0 + 3, 150, 28, 22, seed + 5)
    beam(img, R0 + 2, 148, 30, 2, seed=seed + 5)
    icons.draw_motif(img, 'hammer', R0 + 6, 155)
    icons.draw_motif(img, 'tongs', R0 + 19, 155)
    peg(img, R0 + 8, 153)
    peg(img, R0 + 20, 153)
    P.rivet(img, R0 + 26, 166, 'iron', 3)

    # the requisition chest on the floor, a sack leaning on it
    floor(img, a.right_panel.x + 2, 222, 37, 6, seed + 1)
    requisition_chest(img, R0 + 3, 205, seed)
    P.crack(img, R0 + 30, 184, 6, seed=seed + 7, colour=STONE[0], light=STONE[3])
    crossed_swords(img, R0 + 16, 189, 10, 'cross')

    # ---- bottom strip: chains swagged between rivets ---------------------------
    for x0, x1 in ((8, 120), (136, a.w - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3)
        P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur')

    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------

def paint(key, out_root):
    s = geo.skin(key)
    bg = paint_background(key)
    fr = paint_frame(key)
    a = s.layer()
    if out_root is None:
        bp, fp = s.background_path, s.frame_path(a.id)
    else:
        bp = Path(out_root) / 'menu' / f'{key}.png'
        fp = Path(out_root) / 'frames' / key / f'{a.id}.png'
    for img, p, size in ((bg, bp, (s.width, s.height)), (fr, fp, (a.w, a.h))):
        assert img.size == size and img.mode == 'RGBA', (p, img.size, img.mode)
        C.save_png(img, p)
        print('WROTE', p)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out-root', help='directory laid out like textures/ (default: pack-source)')
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        paint(key, args.out_root)


if __name__ == '__main__':
    main()
