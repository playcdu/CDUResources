#!/usr/bin/env python3
"""Soulrend painter "shopbrowse": the chest-shop browsing screens.

    python tools/soulrend/paint_shopbrowse.py                 # all four skins -> pack-source
    python tools/soulrend/paint_shopbrowse.py --skin chest_shop_ads
    python tools/soulrend/paint_shopbrowse.py --out-root DIR  # DIR/{menu,buttons,frames}/...

Skins: chest_shop, chest_shop_owner (chest_3: 24 listing wells and three
right-column icon controls) and chest_shop_ads, chest_shop_search (chest_6:
28 listing wells, an 18x72 balance column, Prev / Find / Create / Next /
Close and a static top row + right column).

Family identity (chest_shop: ember accent, umber secondary): a merchant's
stall under a stone arch, iron-banded crates, an iron lantern, a hanging
emblem sign and sacks. The owner variant is the keeper's view (key ring,
ledger, strongbox); the ads variant carries a pinned sealed notice; the
search variant a scrying lens. Everything is placed deliberately in code,
deterministically (fixed seeds), on the shared Soulrend base, and finished
with compose.finish_* so masks and pins always hold.

Licence: code MIT; the artwork it paints CC0-1.0.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

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
from palette import BLOOD, EMBER, GOLD, INK, IRON, STONE, UMBER, VELLUM, step  # noqa: E402

SKINS = ('chest_shop', 'chest_shop_owner', 'chest_shop_ads', 'chest_shop_search')
RUST = [BLOOD[0], EMBER[0], EMBER[1]]     # the stall's colours: rust cloth, ember-lit
SEED = {'chest_shop': 41, 'chest_shop_owner': 43, 'chest_shop_ads': 47, 'chest_shop_search': 53}

# ---------------------------------------------------------------------------
# Hand-authored sprites (shared key primitives.SK; '.' transparent)
#   O ink_0 o ink_1 i ink_2 | a b c d iron | m n p q stone | 0 1 2 3 umber
#   v w x y vellum | r s t blood | e f F ember | k l L soul | g h H gold
# ---------------------------------------------------------------------------

# burlap grain sack tied with twine, lit from the top-left
SACK = [
    '...o..o.....',
    '..ovowwo....',
    '...ovwo.....',
    '....ohgo....',
    '...o3hg2o...',
    '..ov33322o..',
    '.ov3v33322o.',
    'ov3333332210',
    'ov3333232210',
    'o33332322110',
    'o23333222110',
    'o22333222110',
    '.o222222110O',
    '..ooooooooO.',
]

# a smaller sack slumped sideways
SACK_SMALL = [
    '..o.o.....',
    '.owvwo....',
    '..ohgo....',
    '.o3hg2o...',
    'ov33322oo.',
    'o3v333221o',
    'o33332221o',
    'o23322211o',
    '.o2222110O',
    '..oooooOO.',
]

BARREL = [
    '..oooooooo..',
    '.o33323221o.',
    'ocddcccbbbao',
    'o3323222211o',
    'o3323222211o',
    'o3323222211o',
    'o3323222210o',
    'ocddcccbbbao',
    'o3323222211o',
    'o3323222210o',
    '.o2222221Oo.',
    'ocddcccbbbao',
    '.oOOOOOOOOO.',
]

# small gold chest pictogram for the hanging emblem sign
EMBLEM_CHEST = [
    '.HHHHH.',
    'Hhhhhhg',
    'ggghggg',
    'HhhOhhg',
    '.ggggg.',
]
EMBLEM_CHEST_BIG = [
    '..HHHHHHH..',
    '.HhhhhhhhhH',
    'Hhhhhhhhhhg',
    'gggggHggggg',
    'Hhhhhohhhhg',
    'Hhhhhhhhhhg',
    'Hhhhhhhhhhg',
    '.ggggggggg.',
]

# an iron lantern hanging from a ring (the motif is 8x9; this one is 5x6)
LANTERN_SMALL = [
    '..o..',
    '.oco.',
    'ocdbo',
    'oFfeo',
    'ofFeo',
    'obaao',
    '.ooo.',
]

# a coil of hemp rope hanging on a peg
ROPE_COIL = [
    '...oo....',
    '..obbo...',
    '.ooaooo..',
    'ow3vw32o.',
    'o3ooooo2o',
    'ovo...o2o',
    'o3o...o1o',
    'owo...o2o',
    'o32ooo21o',
    '.o32221oO',
    '..ooooooO',
]

# small wall sconce for a candle
SCONCE = ['occcco', '.obao.', '..oo..', '..oa..', '..ob..', '...o..']

# a keeper's key ring with three keys
KEY_RING = [
    '...oooo....',
    '..oc..do...',
    '.oc....do..',
    '.ob....bo..',
    '..oa..ao...',
    '...oddo....',
    '..odooodo..',
    '..oco.oco..',
    '..oco.oco..',
    '..oco.obo..',
    '..obo.oco..',
    '.odco.oco..',
    '.obco.ocdo.',
    '..ooo.ocbo.',
    '......ooo..',
]

# an open ledger with ruled pages and a ribbon
LEDGER_OPEN = [
    '.oooooo.oooooo.',
    'oyyyyyyoxxxxxxo',
    'oyvvvvyoxvvvvxo',
    'oyyyyyyoxxxxxxo',
    'oyvvvyyoxvvvxxo',
    'oyyyyyyoxxxxxxo',
    'oyvvvvyoxvvxsxo',
    'owwwwwwowwwwswo',
    'o322222o222221o',
    '.ooooooOoooooO.',
]

# an ink pot with a quill
INKPOT = [
    '....y',
    '...yx',
    '..yx.',
    '.oxo.',
    'obObo',
    'oaaao',
    '.ooo.',
]

# clay jar and a glass bottle for the stall shelves
JAR = ['.ooo.', 'o3e2o', 'oeeeo', 'o3ee0', 'oe00o', '.ooo.']
JAR_TALL = ['.oo.', 'o32o', 'oo1o', 'o3e0', 'oee0', 'oee0', '.oo.']
BOTTLE = ['.o.', 'oao', '.o.', 'oZo', 'zZj', 'zzj', 'ojo']
CLOTH_BOLT = ['.ooooo.', 'ottsssr', 'otsssr0', 'ossssro', 'otsssr0', '.ooooo.']

# iron-banded strongbox with a gold lock (owner)
STRONGBOX = [
    '.oooooooooooooo.',
    'o33333332222221o',
    'ocdcccccccccbbao',
    'o32222222222211o',
    'obbbbbbHhbbbbbao',
    'oddcccchgcccbbao',
    'o32o222Og222o11o',
    'o32o2222222o211o',
    'o22o2222222o110o',
    'ocdcccccccccbbao',
    '.oOOOOOOOOOOOOO.',
]

# the scrying lens: iron ring, deep soul glass with a cold glint
LENS_BIG = [
    '....ooooo....',
    '..oodcccboo..',
    '.odcoooooabo.',
    '.ocoLlkkkoao.',
    'odoLlkkkkkoao',
    'ocolkkkkkkoao',
    'ocokkkkkkkoao',
    'oboklkkkkkoao',
    'oboklkkkkkoao',
    '.obokkkkkoao.',
    '.oboooooooao.',
    '..oobaaaaoo..',
    '....ooooo....',
]

# the scrying lens as a hanging lamp: a bezel with a hanging loop, deep
# soul_0 glass with a soul_2 / soul_1 glint top-left, an iron collar below
LENS_HUNG = [
    '...ooo...',
    '..oocoo..',
    '.ocdccbo.',
    'odLlkkkao',
    'oclkkkkao',
    'ockkkkkao',
    'obkkkkbao',
    '.obbbbao.',
    '..ooaoo..',
    '...ooo...',
]

CRATE_PLATE = [
    'oooooooooooooooo',
    'ocdcchHHHhcccbao',
    'oaaaaagggoaaaaao',
]


# ---------------------------------------------------------------------------
# Drawing helpers (my own; the shared modules are never edited)
# ---------------------------------------------------------------------------

def crate(img, x, y, w, h, seed=0, bands=True):
    """Iron-banded wooden crate: umber planks (seams every 3-4 rows), a lit
    top and left edge, iron corner straps with iron_3 rivets, ink outline
    heavy on the bottom/right."""
    r = P._rng(seed, 'crate', x, y, w, h)
    P.fill(img, (x, y, w, h), UMBER[2])
    yy = y + 3
    while yy < y + h - 2:
        P.hline(img, x + 1, x + w - 2, yy, UMBER[0])
        for xx in range(x + 1, x + w - 1):
            if r.random() < 0.55:
                P.put(img, xx, yy + 1, UMBER[3])
        yy += r.choice((3, 4))
    P.hline(img, x + 1, x + w - 2, y + 1, UMBER[3])
    P.vline(img, x + 1, y + 1, y + h - 2, UMBER[3])
    P.vline(img, x + w - 2, y + 1, y + h - 2, UMBER[1])
    P.hline(img, x + 1, x + w - 2, y + h - 2, UMBER[1])
    if bands:
        for bx in (x + 2, x + w - 4):
            P.vline(img, bx, y + 1, y + h - 2, IRON[2])
            P.vline(img, bx + 1, y + 1, y + h - 2, IRON[0])
            P.put(img, bx, y + 2, IRON[3]); P.put(img, bx, y + h - 3, IRON[3])
    P.ink_outline(img, (x - 1, y - 1, w + 2, h + 2), 'ink_1', radius=0, heavy='br')


def ledge(img, x, y, w, seed=0, ramp=STONE, brackets=True):
    """Carved stone ledge on iron brackets."""
    P.fill(img, (x, y, w, 4), ramp[2])
    P.hline(img, x, x + w - 1, y, ramp[3])
    P.hline(img, x, x + w - 1, y + 3, ramp[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0)
    if brackets:
        for bx in (x + 2, x + w - 4):
            P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


def plank_shelf(img, x, y, w):
    """A wooden stall shelf: umber plank, lit top, dark underside, iron
    L-brackets beneath."""
    P.hline(img, x, x + w - 1, y, UMBER[3])
    P.hline(img, x, x + w - 1, y + 1, UMBER[2])
    P.hline(img, x, x + w - 1, y + 2, UMBER[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 5), 'ink_1', radius=0, heavy='b')
    for bx in (x + 2, x + w - 5):
        P.sprite(img, bx, y + 4, ['occ', '.oc', '..o'])


def awning(img, x0, x1, y, depth=7):
    """Striped stall awning hanging from an iron rod: ember_0 and umber_3
    canvas in 4 px stripes, a lit top row, scalloped hem with an ink edge."""
    P.hline(img, x0 - 1, x1 + 1, y, IRON[2])
    P.hline(img, x0 - 1, x1 + 1, y - 1, INK[0])
    P.put(img, x0 - 2, y, INK[0]); P.put(img, x1 + 2, y, INK[0])
    for x in range(x0, x1 + 1):
        k = (x - x0) // 4
        col = EMBER[0] if k % 2 == 0 else UMBER[3]
        dark = UMBER[2] if col == UMBER[3] else BLOOD[1]
        phase = (x - x0) % 4
        hem = depth + (0 if phase in (1, 2) else -1)
        for j in range(1, hem):
            c = col
            if j == 1:
                c = EMBER[1] if col == EMBER[0] else VELLUM[0]
            elif j >= hem - 2:
                c = dark
            P.put(img, x, y + j, c)
        P.put(img, x, y + hem, INK[1] if phase in (1, 2) else INK[0])
    P.vline(img, x0 - 1, y + 1, y + depth - 1, INK[1])
    P.vline(img, x1 + 1, y + 1, y + depth - 1, INK[0])


def hanging_sign(img, cx, y_hook, board_w, board_h, emblem=EMBLEM_CHEST, chain_len=2):
    """Wooden emblem sign hanging on two short chains: umber board, iron
    corner caps, gold rim on larger boards, a gold chest pictogram (wordless)."""
    x = cx - board_w // 2
    y = y_hook + chain_len + 1
    for hx in (x + 2, x + board_w - 3):
        for k in range(chain_len + 1):
            P.put(img, hx, y_hook + k, IRON[2] if k % 2 == 0 else IRON[0])
    P.ink_outline(img, (x, y, board_w, board_h), 'ink_1', radius=1, heavy='br', fill_colour=UMBER[2])
    P.hline(img, x + 1, x + board_w - 2, y + 1, UMBER[3])
    P.hline(img, x + 1, x + board_w - 2, y + board_h - 2, UMBER[1])
    if board_h >= 10:
        P.bevel(img, (x + 1, y + 1, board_w - 2, board_h - 2), GOLD[1], GOLD[0])
        P.put(img, x + 1, y + 1, GOLD[2])
    ew, eh = P.sprite_size(emblem)
    P.sprite(img, cx - ew // 2, y + (board_h - eh) // 2, emblem)
    return (x, y, board_w, board_h)


def wall_arm(img, x, y, length, brace=6):
    """Wrought-iron arm out of the wall: a wall plate with two rivets at x,
    a bar along row y lit on top, a curled finial at the free end and a
    diagonal brace (with an iron scroll) from the plate up into the bar."""
    # wall plate
    P.ink_outline(img, (x, y - 2, 3, brace + 5), 'ink_1', radius=0, heavy='r', fill_colour=IRON[1])
    P.put(img, x + 1, y - 1, IRON[3]); P.put(img, x + 1, y + brace + 1, IRON[3])
    # bar
    P.hline(img, x + 3, x + length, y - 1, INK[1])
    P.hline(img, x + 3, x + length, y, IRON[2])
    P.hline(img, x + 3, x + length, y + 1, INK[1])
    for k in range(x + 5, x + length - 1, 7):
        P.put(img, k, y, IRON[3])
    # curled finial
    P.sprite(img, x + length, y - 2, ['.oo.', 'occo', 'o.bo', '.oo.'])
    # brace from the plate's foot to the bar
    for i in range(brace):
        P.put(img, x + 3 + i, y + brace - i, IRON[1])
        P.put(img, x + 3 + i, y + brace - i + 1, INK[1])
    P.gold_filigree(img, x + 3, y + 2, 'scroll', 'tl', ramp=IRON)


def short_chain(img, x, y0, y1):
    """A short vertical chain of alternating face-on / edge-on links."""
    for k, yy in enumerate(range(y0, y1 + 1)):
        if k % 3 == 1:
            P.put(img, x - 1, yy, INK[1]); P.put(img, x + 1, yy, INK[1]); P.put(img, x, yy, IRON[0])
        else:
            P.put(img, x, yy, IRON[2] if k % 3 == 0 else IRON[1])


def bracket_sign(img, x, y, length, board_w, board_h, emblem):
    """Iron arm out of the wall at (x, y) carrying the stall's emblem sign
    on two short chains."""
    wall_arm(img, x, y, length)
    cx = x + 3 + (length - 3) // 2 + 1
    bx = cx - board_w // 2
    for hx in (bx + 3, bx + board_w - 4):
        short_chain(img, hx, y + 2, y + 4)
    return hanging_sign(img, cx, y + 4, board_w, board_h, emblem, chain_len=0)


def wall_lantern(img, x, y, seed=0, glow_r=13):
    """Iron lantern hanging on a short chain from a wrought wall arm; ember
    light pools round it. (x, y): the arm's wall plate / bar row."""
    wall_arm(img, x, y, 12, brace=5)
    short_chain(img, x + 11, y + 2, y + 5)
    icons.draw_motif(img, 'lantern', x + 7, y + 6)
    cx, cy = x + 11, y + 11
    P.glow(img, cx, cy, glow_r, 'ember')
    return cx, cy


def nail(img, x, y):
    P.sprite(img, x, y, ['od', 'ca'])


def notice(img, x, y, w, h, seed=0, seal=True):
    """A pinned sealed notice: hand-cut vellum, ruled lines (no words), an
    iron nail at the top and a blood-wax seal near the foot."""
    P.vellum_strip(img, (x, y, w, h), seed, outline='ink_1', deckle='b', heavy='br')
    r = P._rng(seed, 'notice', x, y)
    for k, yy in enumerate(range(y + 4, y + h - 4, 2)):
        x0 = x + 2 + (1 if k == 0 else 0)
        x1 = x + w - 3 - r.randint(0, max(1, w // 3)) if k % 3 == 2 else x + w - 3
        for xx in range(x0, x1 + 1):
            if (xx + k) % 7:
                P.put(img, xx, yy, VELLUM[0])
    nail(img, x + w // 2 - 1, y + 1)
    if seal:
        P.wax_seal(img, x + w - 4, y + h - 3, 3, BLOOD, seed)
        P.sprite(img, x + w - 5, y + h, ['st', '.r'])


def candle_sconce(img, x, y, seed=0, glow_r=10):
    P.sprite(img, x - 3, y + 8, SCONCE)
    fx, fy = P.candle(img, x - 1, y, height=6, lit=True, holder=None, seed=seed)
    P.glow(img, fx, fy + 2, glow_r, 'ember')
    return fx, fy


def stall_post(img, x, y0, y1, seed=0):
    """A narrow wooden stall post (4 px) with iron bands and rivets every
    18 px: the right-column controls read as nailed to it."""
    for y in range(y0, y1 + 1):
        P.put(img, x, y, INK[1])
        P.put(img, x + 1, y, UMBER[3])
        P.put(img, x + 2, y, UMBER[2])
        P.put(img, x + 3, y, UMBER[1])
        P.put(img, x + 4, y, INK[0])
    r = P._rng(seed, 'post', x)
    for y in range(y0 + 2, y1 - 1):
        if r.random() < 0.18:
            P.put(img, x + 2, y, UMBER[0])         # grain
    for yb in range(y0 + 2, y1 - 1, 18):
        P.put(img, x + 1, yb, IRON[2]); P.put(img, x + 2, yb, IRON[1]); P.put(img, x + 3, yb, IRON[0])
        P.put(img, x + 1, yb + 1, IRON[3]); P.put(img, x + 2, yb + 1, IRON[1]); P.put(img, x + 3, yb + 1, IRON[0])


def floor(img, x, y, w, h, seed=0):
    """Flagstone floor the stall goods stand on."""
    P.stone_blocks(img, (x, y, w, h), seed, STONE, course=3, moss=0.15)
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y - 1, INK[1])


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def paint_bg_chest3(key):
    """chest_shop / chest_shop_owner: the sheet is almost all wells; the
    identity lives in the margins: the right column's three controls hang
    from an iron chain off the title clasp, iron shelf brackets mark the
    listing shelves, a gold-stamped crate plate sits under the hotbar; the
    keeper's view gets a small iron key."""
    seed = SEED[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    W, H = s.width, s.height
    tband, iband = C.bands(key)
    stall_post(img, 169, tband.bottom, iband.y - 1, seed)
    for yy in (34, 52):
        P.sprite(img, 2, yy - 1, ['b', 'd', 'a'])
    P.sprite(img, W // 2 - 8, H - 5, CRATE_PLATE)
    if key == 'chest_shop_owner':
        P.sprite(img, 22, H - 5, ['.oo.ooooo', 'oc.ocdcbo', '.oo.oo.o.'])
    else:
        P.sprite(img, 22, H - 5, ['oso', 'oto', '.o.'])
    P.crack(img, W - 26, H - 5, 3, seed=seed, direction='right', colour='umber_0', branch=False)
    C.finish_background(img, key)
    return img


def _arch_y(x, x0, x1, top, bottom):
    """Intrados row of a flat segmental arch from (x0, bottom) to (x1, bottom)
    peaking at ``top``."""
    cx = (x0 + x1) / 2
    hw = (x1 - x0) / 2
    t = (x - cx) / hw
    return top + int(round((bottom - top) * t * t))


def paint_bg_chest6(key):
    """chest_shop_ads / chest_shop_search: the static top row and right
    column become a merchant's stall: a flat stone arch springing from the
    balance pillar (left) and a masonry pier (right); an emblem sign hangs
    from the keystone, lanterns from the voussoirs; crates and a sack are
    stacked at the foot of the pier. Ads pins a sealed notice to the pier;
    search hangs a scrying lens from a wrought arm on it."""
    seed = SEED[key]
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    W, H = s.width, s.height
    ads = key == 'chest_shop_ads'

    top_box = (3, 15, 170, 16)          # x3..172, y15..30 (the well ring starts at y31)
    left_pier = (3, 15, 18, 20)         # x3..20, y15..34 (above the balance column)
    right_pier = (154, 15, 19, 92)      # x154..172, y15..106
    for i, b in enumerate((top_box, left_pier, right_pier)):
        P.stone_blocks(img, b, seed + i, STONE, course=5, moss=0.08, cracks=0.3)
    P.hline(img, 3, 172, 15, INK[1])

    x0, x1, top, bottom = 21, 153, 20, 31
    kc = (x0 + x1) // 2
    joints = sorted(list(range(kc - 5, x0 + 3, -9)) + list(range(kc + 5, x1 - 3, 9)))
    for x in range(x0, x1 + 1):
        yi = _arch_y(x, x0, x1, top, bottom)
        for y in range(yi, 31):
            P.put(img, x, y, UMBER[0])               # the shadowed stall interior
        seg = sum(1 for j in joints if j <= x)
        face = STONE[2] if seg % 2 else STONE[1]
        for k in range(1, 4):
            P.put(img, x, yi - k, face)
        P.put(img, x, yi - 4, INK[1])                # extrados joint
        P.put(img, x, yi - 3, step(face, 1) if x < kc else face)   # cold light on the arch's back
        P.put(img, x, yi, INK[0])                    # soffit shadow
        if yi + 1 <= 30:
            P.put(img, x, yi + 1, INK[2])            # the soffit's deep shade under the arch
    for jx in joints:
        yi = _arch_y(jx, x0, x1, top, bottom)
        lean = 0 if abs(jx - kc) < 20 else (-1 if jx < kc else 1)
        P.put(img, jx, yi - 1, INK[1]); P.put(img, jx, yi - 2, INK[1]); P.put(img, jx + lean, yi - 3, INK[1])
    P.sprite(img, kc - 4, 15, [
        'oooooooooo',
        'oqqqqqqppo',
        'oqppppppno',
        'oqpphhppno',
        '.oqppppno.',
        '.oqpppnno.',
        '..oooooO..',
    ])
    for ix, flip in ((14, False), (152, True)):
        P.sprite(img, ix, 27, ['oooooooo', 'oqqqqppo', 'onnnnnmo', 'oooooooO'], flip_x=flip)

    # the stall's emblem sign hangs from the keystone on two short chains
    hanging_sign(img, kc, 22, 21, 8, EMBLEM_CHEST, chain_len=0)
    for hx in (kc - 8, kc + 8):
        P.put(img, hx, 21, IRON[2])

    # iron lanterns hang from the voussoirs; warm light pools in the stall
    for lx in (56, 117):
        yi = _arch_y(lx + 2, x0, x1, top, bottom)
        P.put(img, lx + 2, yi + 1, IRON[1])
        P.sprite(img, lx, yi + 2, LANTERN_SMALL)
        P.glow(img, lx + 2, yi + 6, 6, 'ember')

    # The right column's props are scene pieces, never item-shaped sprites
    # centred in an 18 px static cell: the notice straddles the cell seams,
    # the sconce bridges two cells, the search lens hangs across the 17/26
    # seam and the sack slumps on the crate stack.
    if ads:
        notice(img, 156, 32, 15, 24, seed=seed)
        P.crack(img, 168, 62, 5, seed=seed, colour=STONE[0], light=STONE[3])
    else:
        # The scrying lens hangs like a lamp from a wrought arm bolted to the
        # pier, low across the 17/26 cell seam: a fitting of the stall, never
        # an orb set centred in a static cell like an item. Light first, so
        # the glass keeps its deep soul_0 (a spice, not a fill).
        arm = C.new(18, 14)
        wall_arm(arm, 0, 4, 12, brace=5)
        img.alpha_composite(arm.transpose(Image.FLIP_LEFT_RIGHT), (153, 33))   # plate on the pier, arm reaching left
        P.glow(img, 160, 50, 8, 'soul')
        short_chain(img, 160, 39, 42)
        P.sprite(img, 156, 43, LENS_HUNG)
    candle_sconce(img, 163, 63, seed=seed, glow_r=9)
    crate(img, 155, 95, 17, 11, seed)
    crate(img, 157, 85, 13, 9, seed + 1)
    P.sprite(img, 156, 75, SACK_SMALL)                 # resting on the small crate
    P.hline(img, 166, 168, 85, UMBER[0])               # its cast shadow on the lid

    P.chain(img, 4, 35, 4, 104, seed=seed + 3, shadow=None)
    P.sprite(img, W // 2 - 8, H - 5, CRATE_PLATE)
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def paint_buttons(key):
    """Every region in the shared grammar plus small family touches; the six
    states come from the shared transforms. Returns {button_id: states}."""
    seed = SEED[key]
    s = geo.skin(key)
    out = {}
    for b in s.buttons:
        img = C.paint_button(key, b.id, seed=seed)
        kind = C.button_kind(b)
        bx, by, bw, bh = b.body.tuple()
        if kind == 'icon' and b.role != 'info':
            for tx, ty in ((bx + 1, by + 1), (bx + bw - 2, by + 1), (bx + 1, by + bh - 2), (bx + bw - 2, by + bh - 2)):
                P.put(img, tx, ty, IRON[1])
        elif kind == 'icon' and b.h > 36:
            for yy in (54, 62):
                for xx in range(bx + 2, bx + bw - 2):
                    if (xx + yy) % 5:
                        P.put(img, xx, yy, STONE[2])
        elif kind in ('page_prev', 'page_next'):
            nx = bx + 3 if kind == 'page_next' else bx + bw - 5
            nail(img, nx, by + 2)
        C.finish_button(img, key, b.id)
        out[b.id] = C.button_states(img, key, b.id)
    return out


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def _top_bottom(img, a, seed):
    W, H = a.w, a.h
    # chains swag from the corners to the scroll ends of the wordless plaque
    P.chain(img, 12, 4, W // 2 - 21, 4, sag=2, seed=seed + 11)
    P.chain(img, W // 2 + 21, 4, W - 13, 4, sag=2, seed=seed + 12)
    for xa, xb in ((8, 120), (136, W - 9)):
        P.chain(img, xa, H - 6, xb, H - 6, sag=2, seed=seed + xa)
        P.rivet(img, xa - 2, H - 7, 'gold', 3); P.rivet(img, xb - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur')


def left_panel(img, a, key, seed):
    H = a.h
    x = 4
    bracket_sign(img, x, 13, 24, 24, 15, EMBLEM_CHEST_BIG)
    y = 44
    if key == 'chest_shop_ads':
        bx, by, bw, bh = 6, y, 28, 46
        P.ink_outline(img, (bx, by, bw, bh), 'ink_1', radius=1, heavy='br', fill_colour=UMBER[1])
        P.bevel(img, (bx + 1, by + 1, bw - 2, bh - 2), IRON[2], IRON[0])
        for k in range(by + 4, by + bh - 2, 5):
            P.hline(img, bx + 2, bx + bw - 3, k, UMBER[0])
        notice(img, bx + 3, by + 3, 12, 15, seed=seed + 1)
        notice(img, bx + 15, by + 5, 10, 13, seed=seed + 2, seal=False)
        notice(img, bx + 4, by + 21, 11, 13, seed=seed + 3, seal=False)
        notice(img, bx + 14, by + 22, 11, 19, seed=seed + 4)
        for rx, ry in ((bx + 1, by + 1), (bx + bw - 4, by + 1), (bx + 1, by + bh - 4), (bx + bw - 4, by + bh - 4)):
            P.rivet(img, rx, ry, 'iron', 3)
        y = by + bh + 8
    elif key == 'chest_shop_search':
        P.arch_niche(img, (7, y, 26, 40), seed=seed)
        P.glow(img, 19, y + 19, 15, 'soul')
        P.sprite(img, 13, y + 13, LENS_BIG)
        P.sprite(img, 18, y + 26, ['oco', 'obo', 'oco', 'obo', 'ocdcbo'])
        P.sprite(img, 15, y + 30, ['oocdcboo', 'ocdccbbo', 'oooooooo'])
        ledge(img, 6, y + 40, 28, seed)
        y = y + 50
    else:
        y = 46
    wall_lantern(img, x + 6, y, seed=seed + 5)
    y += 34
    if key in ('chest_shop', 'chest_shop_owner'):
        C.side_banner(img, geo.Rect(x, 0, 32, 0), y=y, seed=seed, ramp=RUST, crest='chevron', h=34)
    else:
        C.side_banner(img, geo.Rect(x, 0, 32, 0), y=y, seed=seed, ramp=BLOOD,
                      crest='key' if key == 'chest_shop_ads' else 'moon', h=40)
    if H < 200:
        # short frame: a candle on a sconce between the banner and the goods
        candle_sconce(img, 29, 118, seed=seed + 2, glow_r=9)
        P.crack(img, 9, 124, 6, seed=seed + 4, colour=STONE[0], light=STONE[3])
    fy = H - 14
    floor(img, 3, fy, 36, 6, seed)
    crate(img, 5, fy - 14, 18, 13, seed + 6)
    crate(img, 8, fy - 24, 13, 9, seed + 7)
    P.sprite(img, 24, fy - 14, SACK)
    P.moss_tuft(img, 30, fy + 1, 3, seed=seed)


def right_panel(img, a, key, seed):
    H = a.h
    x0 = 219
    owner = key == 'chest_shop_owner'
    awning(img, x0, x0 + 32, 12, depth=8)
    plank_shelf(img, x0 + 1, 36, 31)
    if owner:
        P.sprite(img, x0 + 2, 26, LEDGER_OPEN)
        P.sprite(img, x0 + 19, 29, INKPOT)
        P.candle(img, x0 + 27, 29, height=5, lit=True, holder='gold', seed=seed)
        P.glow(img, x0 + 28, 28, 9, 'ember')
    else:
        P.sprite(img, x0 + 2, 30, JAR)
        P.sprite(img, x0 + 8, 29, JAR_TALL)
        icons.draw_motif(img, 'goblet', x0 + 13, 27)
        P.sprite(img, x0 + 23, 29, BOTTLE)
        P.sprite(img, x0 + 27, 30, JAR)
    plank_shelf(img, x0 + 1, 58, 31)
    if owner:
        P.sprite(img, x0 + 4, 42, KEY_RING)
        icons.draw_motif(img, 'coin_stack', x0 + 16, 50)
        icons.draw_motif(img, 'ledger', x0 + 22, 47)
    else:
        P.sprite(img, x0 + 2, 52, CLOTH_BOLT)
        P.sprite(img, x0 + 10, 52, CLOTH_BOLT)
        icons.draw_motif(img, 'coin_stack', x0 + 19, 50)
        P.sprite(img, x0 + 27, 51, JAR_TALL)
    P.rivet(img, x0 + 15, 66, 'iron', 3)
    P.chain(img, x0 + 16, 69, x0 + 16, 80, seed=seed + 8)
    icons.draw_motif(img, 'lantern', x0 + 12, 81)
    P.glow(img, x0 + 16, 86, 13, 'ember')
    # a peg rail with the stall's hanging goods: a rope coil and a sack
    # (the keeper hangs his satchel there instead)
    ry = 104
    P.hline(img, x0 + 1, x0 + 31, ry, UMBER[3])
    P.hline(img, x0 + 1, x0 + 31, ry + 1, UMBER[1])
    P.ink_outline(img, (x0, ry - 1, 33, 4), 'ink_1', radius=0, heavy='b')
    for px_ in (x0 + 6, x0 + 24):
        P.sprite(img, px_ - 1, ry + 2, ['oco', '.bo', '.oa', '..o'])
    P.sprite(img, x0 + 2, ry + 4, ROPE_COIL)
    if owner:
        icons.draw_motif(img, 'satchel', x0 + 19, ry + 5)
    else:
        P.sprite(img, x0 + 19, ry + 4, SACK_SMALL)
    P.crack(img, x0 + 29, ry + 24, 6, seed=seed + 6, colour=STONE[0], light=STONE[3])
    if H > 200:
        # tall market frame: a merchant's banner below the rail
        C.side_banner(img, geo.Rect(x0 - 2, 0, 36, 0), y=134, seed=seed + 3, ramp=RUST, crest='tower', h=36)
        P.moss_tuft(img, x0 + 3, 178, 4, seed=seed + 2)
    fy = H - 14
    floor(img, 217, fy, 36, 6, seed + 1)
    if owner:
        P.sprite(img, x0 + 1, fy - 11, STRONGBOX)
        crate(img, x0 + 3, fy - 21, 13, 9, seed + 9)
    else:
        P.sprite(img, x0 + 1, fy - 13, BARREL)
        crate(img, x0 + 14, fy - 12, 18, 11, seed + 9)
        P.sprite(img, x0 + 19, fy - 23, SACK_SMALL)
    P.crack(img, 250, 120, 7, seed=seed + 5, colour=STONE[0], light=STONE[3])


def paint_frame(key):
    seed = SEED[key]
    s = geo.skin(key)
    a = s.art_layers[0]
    img = C.base_frame(key, a.id, seed=seed)   # wordless plaque, like every Soulrend frame
    left_panel(img, a, key, seed)
    right_panel(img, a, key, seed)
    _top_bottom(img, a, seed)
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def paint_skin(key, out_root=None):
    s = geo.skin(key)
    bg = paint_bg_chest3(key) if s.layout == 'chest_3' else paint_bg_chest6(key)
    states = paint_buttons(key)
    frame = paint_frame(key)
    lid = s.art_layers[0].id
    written = []
    if out_root is None:
        written.append(C.save_png(bg, s.background_path))
        written.append(C.save_png(frame, s.frame_path(lid)))
        for bid, st in states.items():
            written += C.save_button_states(st, key, bid)
    else:
        root = Path(out_root)
        written.append(C.save_png(bg, root / 'menu' / f'{key}.png'))
        written.append(C.save_png(frame, root / 'frames' / key / f'{lid}.png'))
        for bid, st in states.items():
            written += C.save_button_states(st, key, bid, root=root)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description='Paint the Soulrend chest-shop browsing skins.')
    ap.add_argument('--skin', choices=SKINS, action='append', help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', help='write textures under DIR/{menu,buttons,frames} instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        written = paint_skin(key, args.out_root)
        print(f'{key}: wrote {len(written)} PNGs')


if __name__ == '__main__':
    main()
