"""Original hand-authored icon and motif sprites for the cozy theme.

Icons sit on 18x18 icon buttons (close, balance, search, settings, rank) and
the 18x72 balance column. Motifs are small decorative sprites for frames and
static protected artwork. Each sprite is a list of strings plus a colour key;
'.' is transparent. Draw with ``draw_icon`` / ``draw_motif`` or
``primitives.sprite``. All drawings are original (CC0-1.0); code MIT.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_HERE = str(_Path(__file__).resolve().parent)
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

from palette import ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD  # noqa: E402
import primitives as P  # noqa: E402

# Shared colour keys --------------------------------------------------------
K_BRASS = {'o': INK[1], 'O': INK[0], '0': BRASS[0], '1': BRASS[1], '2': BRASS[2], '3': BRASS[3]}
K_WOOD = {'o': INK[1], 'O': INK[0], '0': WOOD[0], '1': WOOD[1], '2': WOOD[2], '3': WOOD[3], '4': WOOD[4]}

# --- Icons (drawn centred in the button body) -------------------------------

# Coin purse: leather pouch, twine drawstring, brass coin tucked at its foot.
PURSE = [
    '..o.....o..',
    '...o...o...',
    '....oto....',
    '...o1t1o...',
    '...o232o...',
    '..o23332o..',
    '.o2344332o.',
    'o234433332o',
    'o233333322o',
    'o22333ooooo',
    '.o2222obbBo',
    '..ooooobbBo',
    '.......ooo.',
]
K_PURSE = {'o': INK[1], 't': PARCHMENT[1], '1': WOOD[1], '2': WOOD[2], '3': WOOD[3], '4': WOOD[4],
           'b': BRASS[2], 'B': BRASS[0]}

# Magnifying glass: brass rim, sky glass with a cream glint, wooden handle.
LENS = [
    '..oooo.....',
    '.o2222o....',
    'o2gcss2o...',
    'o2csss12o..',
    'o2sss112o..',
    'o2ss1112o..',
    '.o21111o...',
    '..o2222oo..',
    '...ooooo3o.',
    '.......o33o',
    '........o3o',
    '.........o.',
]
K_LENS = {'o': INK[1], '2': BRASS[2], '1': SKY[1], 's': SKY[2], 'c': PARCHMENT[3], 'g': PARCHMENT[3],
          '3': WOOD[3]}

# Settings: a brass cog with eight teeth around a dark axle.
COG = [
    '....o..o....',
    '...o3oo2o...',
    '.oo.o32o.oo.',
    '.o3oo222oo2o',
    '..o2222221o.',
    'oo222oo2221o',
    'o3221oo1221o',
    '.o2221111oo.',
    '.o2o12111o..',
    '.oo.o11o.oo.',
    '....o00o....',
    '.....oo.....',
]
K_COG = {'o': INK[1], '0': BRASS[0], '1': BRASS[1], '2': BRASS[2], '3': BRASS[3]}

# Rank: a berry rosette with a brass centre and two ribbon tails.
ROSETTE = [
    '...o.o.o...',
    '..o2o2o2o..',
    '.o2211122o.',
    'o221bbb122o',
    '.o21b3b12o.',
    'o221bbb122o',
    '.o2211122o.',
    '..o2o2o2o..',
    '...oo.oo...',
    '...o1o1o...',
    '..o11oo11o.',
    '..o1o..o1o.',
    '..oo....oo.',
]
K_ROSETTE = {'o': INK[1], '1': BERRY[1], '2': BERRY[2], 'b': BRASS[2], '3': BRASS[3]}

# Coin: brass disc, reused by motifs and the balance column.
COIN = ['.ooo.', 'o332o', 'o321o', 'o210o', '.ooo.']
K_COIN = {'o': INK[1], '0': BRASS[0], '1': BRASS[1], '2': BRASS[2], '3': BRASS[3]}

ICONS = {
    'balance': (PURSE, K_PURSE),
    'search': (LENS, K_LENS),
    'settings': (COG, K_COG),
    'rank': (ROSETTE, K_ROSETTE),
    'coin': (COIN, K_COIN),
}

# --- Seal emblems (5x5, pressed into wax) ---------------------------------------
EMBLEMS = {
    'x': ['#...#', '.#.#.', '..#..', '.#.#.', '#...#'],
    'check': ['....#', '...#.', '#.#..', '.#...', '.....'],
    'heart': ['.#.#.', '#####', '#####', '.###.', '..#..'],
    'star': ['..#..', '.###.', '#####', '.###.', '.#.#.'],
    'coin': ['.###.', '#...#', '#.#.#', '#...#', '.###.'],
    'leaf': ['...##', '..###', '.###.', '###..', '#....'],
}


def draw_emblem(img, cx, cy, name, ramp=BERRY):
    """Press a 5x5 emblem into wax centred at (cx, cy): ramp[0] grooves with a
    ramp[2] lit lip on the lower-right of each groove."""
    rows = EMBLEMS[name]
    x0, y0 = cx - 2, cy - 2
    on = {(i, j) for j, r in enumerate(rows) for i, c in enumerate(r) if c == '#'}
    for (i, j) in on:
        if (i + 1, j + 1) not in on:
            P.put(img, x0 + i + 1, y0 + j + 1, ramp[2])
    for (i, j) in on:
        P.put(img, x0 + i, y0 + j, ramp[0])


def icon_size(name):
    return P.sprite_size(ICONS[name][0])


def draw_icon(img, name, box):
    """Centre icon ``name`` inside box (x, y, w, h). Returns its top-left."""
    rows, key = ICONS[name]
    w, h = P.sprite_size(rows)
    x = box[0] + (box[2] - w) // 2
    y = box[1] + (box[3] - h) // 2
    P.sprite(img, x, y, rows, key)
    return x, y


def close_seal(img, box, seed=0):
    """The close control: a round red wax seal pressed with an X, filling the
    body box (diameter = min(w, h) - 1, odd)."""
    x, y, w, h = box
    r = (min(w, h) - 1) // 2
    cx, cy = x + w - 1 - r, y + h // 2   # right-aligned so the pin column is wax
    P.wax_seal(img, cx, cy, r, BERRY, seed, drip=False)
    # 2 px embossed X
    for k in range(-3, 4):
        for (px, py) in ((cx + k, cy + k), (cx + k, cy - k)):
            P.put(img, px + 1, py + 1, BERRY[2])
    for k in range(-3, 4):
        for (px, py) in ((cx + k, cy + k), (cx + k, cy - k)):
            P.put(img, px, py, INK[0])
    return cx, cy, r


# --- Motifs for frames and static art ----------------------------------------
CANDLE = [
    '..e..',
    '.eEe.',
    '..E..',
    '..o..',
    '.o3o.',
    '.o32o',
    '.o32o',
    '.o32o',
    'oo22oo',
    'o1111o',
    '.oooo.',
]
K_CANDLE = {'e': EMBER[1], 'E': EMBER[2], 'o': INK[1], '3': PARCHMENT[3], '2': PARCHMENT[1],
            '1': BRASS[1]}

HERB_POT = [
    '..g...g..',
    '.gGg.gGg.',
    '..gGgGg..',
    '.g.gGg.g.',
    '.Gg.g.gG.',
    '..g.g.g..',
    '.ooooooo.',
    'o2333332o',
    '.o12221o.',
    '.o11111o.',
    '..o111o..',
    '..ooooo..',
]
K_HERB_POT = {'g': SAGE[1], 'G': SAGE[2], 'o': INK[1], '1': EMBER[0], '2': EMBER[1], '3': BRASS[2]}

CRATE = [
    'oooooooooo',
    'o3333333oo',
    'o2o2222o2o',
    'o22o22o22o',
    'o222oo222o',
    'o222oo222o',
    'o22o22o22o',
    'o2o2222o2o',
    'o11111111o',
    'oooooooooo',
]
K_CRATE = {'o': INK[1], '1': WOOD[1], '2': WOOD[2], '3': WOOD[3]}

LEDGER = [
    '.oooooooooo',
    'o33333333po',
    'o3iiii333po',
    'o33333333po',
    'o3iii3333po',
    'o33333333po',
    'o3iiiii33po',
    'o33333333po',
    'obbbbbbbbbo',
    '.oooooooooo',
]
K_LEDGER = {'o': INK[1], '3': PARCHMENT[2], 'i': SKY[1], 'p': BERRY[1], 'b': BERRY[0]}

MOTIFS = {
    'candle': (CANDLE, K_CANDLE),
    'herb_pot': (HERB_POT, K_HERB_POT),
    'crate': (CRATE, K_CRATE),
    'ledger': (LEDGER, K_LEDGER),
    'coin': (COIN, K_COIN),
}


def draw_motif(img, name, x, y, flip_x=False):
    rows, key = MOTIFS[name]
    rows = [r.ljust(max(len(q) for q in rows), '.') for r in rows]
    P.sprite(img, x, y, rows, key, flip_x=flip_x)
    return P.sprite_size(rows)
