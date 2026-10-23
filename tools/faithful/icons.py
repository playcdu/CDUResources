"""Original icon and pictogram sprites for the Faithful theme.

Icons sit on the 18x18 icon buttons (close, balance, search, settings, rank)
and the 18x72 balance column. Pictograms are the small flat family marks
used in static decorative cells and on outer frames (never inside item
wells). Every sprite is a list of strings in the shared colour key
``primitives.SK`` ('.' is transparent):

    O ink_0  o ink_1     a b c d e f g W  grey_0..7     u v V  green_0..2
    r s t   red_0..2     h H Y  gold_0..2               m n N  blue_0..2
    p P     purple_0..1

Round shapes (coins, the ender orb) are generated from simple geometric masks by
``shaded`` (black outline, light top/left, shade bottom/right), the rest are
drawn by hand below. All drawings are original (CC0-1.0); code MIT. None is
traced from Minecraft's item or GUI sprites, nor from the cozy or Soulrend
icons.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

if __name__ == 'icons':                 # imported by its plain name from tools/faithful
    # one module object per process (see palette.py)
    if 'faithful.icons' in _sys.modules:
        _sys.modules[__name__] = _sys.modules['faithful.icons']
    else:
        _sys.modules['faithful.icons'] = _sys.modules[__name__]
_TOOLS = _Path(__file__).resolve().parents[1]
if str(_TOOLS) not in _sys.path:
    _sys.path.append(str(_TOOLS))

from faithful import primitives as P  # noqa: E402


# ---------------------------------------------------------------------------
# Generated round shapes
# ---------------------------------------------------------------------------

def disc_mask(d, cx=None, cy=None):
    """Pixel disc of diameter ``d`` (odd or even) inside a d x d box."""
    r = d / 2
    cx = (d - 1) / 2 if cx is None else cx
    cy = (d - 1) / 2 if cy is None else cy
    return {(x, y) for y in range(d) for x in range(d) if (x - cx) ** 2 + (y - cy) ** 2 <= (r - 0.35) ** 2}


def shaded(mask, w, h, light, body, dark, outline='O', extra=None):
    """ASCII rows for ``mask``: 4-neighbour edge pixels ``outline``; interior
    pixels next to the outline on their top/left ``light``, on their
    bottom/right ``dark``, else ``body``. ``extra`` maps (x, y) -> char drawn
    last (marks, slashes, holes; '.' makes a pixel transparent)."""
    rows = [['.'] * w for _ in range(h)]
    edge = {p for p in mask if any((p[0] + dx, p[1] + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    for (x, y) in mask:
        if (x, y) in edge:
            c = outline
        else:
            tl = (x, y - 1) in edge or (x - 1, y) in edge
            br = (x, y + 1) in edge or (x + 1, y) in edge
            c = light if tl and not br else dark if br and not tl else body
        rows[y][x] = c
    for (x, y), c in (extra or {}).items():
        if 0 <= x < w and 0 <= y < h:
            rows[y][x] = c
    return [''.join(r) for r in rows]


def _coin(d=11, slash=True):
    """Gold coin disc; with ``slash`` a diagonal mark across its face (the
    balance icon: a coin with a slash, our own currency sign)."""
    m = disc_mask(d)
    extra = {}
    if slash:
        for k in range(-2, 3):
            cx, cy = (d - 1) // 2, (d - 1) // 2
            extra[(cx + k, cy - k)] = 'h'
            extra[(cx + k - 1, cy - k)] = 'Y' if k < 2 else extra.get((cx + k - 1, cy - k), 'H')
    return shaded(m, d, d, 'Y', 'H', 'h', extra=extra)


# ---------------------------------------------------------------------------
# Icons (drawn centred in the button body)
# ---------------------------------------------------------------------------

STAR = [
    '.....O.....',
    '....OYO....',
    '....OYO....',
    'OOOOYHHOOOO',
    'OYYYHHHHHhO',
    '.OHHHHHHhO.',
    '..OHHHHHhO.',
    '..OHHhHHhO.',
    '.OHHhOOhhO.',
    '.OhhO..OhO.',
    'OOOO....OOO',
]

COIN = ['.OOO.', 'OYHHO', 'OHHhO', 'OHhhO', '.OOO.']

COG = [
    '.....OOO.....',
    '..OO.OgO.OO..',
    '.OgOOggeOOeO.',
    '.OOgggggeeOO.',
    '..OggeeeeebO.',
    'OOggeOOOebbOO',
    'OgggeOaObbbeO',
    'OOgeeOOObbeOO',
    '..OeeebbbbbO.',
    '.OOeebbbbbOO.',
    '.OeOObbbOObO.',
    '..OO.ObO.OO..',
    '.....OOO.....',
]

LENS = [
    '..OOOOO.....',
    '.OgggggO....',
    'OgNnnnmfO...',
    'OgnnnnmfO...',
    'OgnnnmmfO...',
    'OgnmmmmfO...',
    'OfmmmmmbO...',
    '.OfbbbbOO...',
    '..OOOOOddO..',
    '.......OddO.',
    '........OddO',
    '.........OO.',
]

ICONS = {
    'balance': _coin(11, slash=True),
    'search': LENS,
    'settings': COG,
    'rank': STAR,
    'coin': COIN,
}


def x_cross(size=8):
    """Glyph pixels of the close X: two 2 px diagonal strokes in a
    ``size`` x ``size`` box (relative to its top-left)."""
    pts = set()
    for k in range(size):
        pts.add((k, k)); pts.add((size - 1 - k, k))
        if k + 1 < size:
            pts.add((k + 1, k))
        if size - 2 - k >= 0:
            pts.add((size - 2 - k, k))
    return pts


def draw_x(img, box, colour='grey_7', shadow='ink_1', size=8):
    """Draw the close X centred in ``box`` like lettering (white with a
    (+1, +1) ink_1 shadow). Returns the glyph pixel set."""
    x, y, w, h = box
    ox = x + (w - size - 1) // 2
    oy = y + (h - size - 1) // 2
    pts = {(ox + i, oy + j) for (i, j) in x_cross(size)}
    for (px, py) in sorted(pts):
        if (px + 1, py + 1) not in pts:
            P.put(img, px + 1, py + 1, shadow)
    for (px, py) in sorted(pts):
        P.put(img, px, py, colour)
    return pts


def icon_size(name):
    return P.sprite_size(ICONS[name])


def icon_origin(name, box):
    """Top-left at which ``draw_icon`` places icon ``name`` in ``box``."""
    w, h = P.sprite_size(ICONS[name])
    return box[0] + (box[2] - w) // 2, box[1] + (box[3] - h) // 2


def icon_pixels(name, box):
    """The image pixels ``draw_icon(img, name, box)`` paints (opaque sprite
    cells), so compose can protect an icon like lettering."""
    x, y = icon_origin(name, box)
    return {(x + i, y + j) for j, r in enumerate(ICONS[name]) for i, c in enumerate(r) if c not in '. '}


def draw_icon(img, name, box):
    """Centre icon ``name`` inside box (x, y, w, h). Returns its top-left.
    'close' draws the X (``draw_x``)."""
    if name == 'close':
        draw_x(img, box)
        return box[0], box[1]
    rows = ICONS[name]
    w, h = P.sprite_size(rows)
    x = box[0] + (box[2] - w) // 2
    y = box[1] + (box[3] - h) // 2
    P.sprite(img, x, y, rows)
    return x, y


# ---------------------------------------------------------------------------
# Family pictograms (static decorative cells and frames only)
# ---------------------------------------------------------------------------

PICTOGRAMS = {
    # economy: a coin disc with a stamped centre mark
    'coin': shaded(disc_mask(10), 10, 10, 'Y', 'H', 'h',
                   extra={(4, 3): 'h', (5, 3): 'h', (4, 4): 'Y', (5, 4): 'h', (4, 5): 'h', (5, 5): 'Y',
                          (4, 6): 'h', (5, 6): 'h'}),
    # auction: a gavel standing on its sound block
    'gavel': [
        '.OOOOOOOOO.',
        'OgfYHHHhfeO',
        'OfeHHHHhebO',
        'OfeHHhhhebO',
        '.OOOOOOOOO.',
        '....OHhO...',
        '....OHhO...',
        '....OHhO...',
        '..OOOOOOOO.',
        '.OgggggggfO',
        '.OfffffffeO',
        '..OOOOOOOO.',
    ],
    # chest shop: a chest seen from the front, lid edge and latch
    'chest': [
        '.OOOOOOOOOO.',
        'OHYYYYYYYYhO',
        'OHHHHHHHHHhO',
        'OOOOOOOOOOOO',
        'OhhhhOWOhhhO',
        'OHHHHOeOHHhO',
        'OHHHHOOOHHhO',
        'OHHHHHHHHHhO',
        'OhhhhhhhhhhO',
        'OOOOOOOOOOOO',
    ],
    # trade: two opposed arrows
    'arrows': [
        '.......O....',
        '.......OO...',
        'OOOOOOOONO..',
        'ONNNNNNNnnO.',
        'OnnnnnnnnmO.',
        'OOOOOOOOmO..',
        '..O....OO...',
        '.OO....O....',
        'ONOOOOOOOOOO',
        'OnnNNNNNNNNO',
        '.OmmnnnnnnnO',
        '..OmOOOOOOOO',
        '...OO.......',
        '....O.......',
    ],
    # ticket: a stub with side notches and a perforated end
    'ticket': [
        'OOOOOOOOOOOO',
        'OWeWWWWeWWfO',
        'OgeggggWggfO',
        '.OeggggeWgO.',
        '.OeggggWggO.',
        'OgeggggeggfO',
        'OfeffffWfffO',
        'OOOOOOOOOOOO',
    ],
    # admin shop: a plain shield with a white chevron
    'shield': [
        'OOOOOOOOOO',
        'ONNNNNNNmO',
        'ONnnnnnnmO',
        'OnnnWWnnmO',
        'OnnWnnWnmO',
        'OnWnnnnWmO',
        'OnnnnnnnmO',
        '.OnnnnnmO.',
        '.OnnnnnmO.',
        '..OnnnmO..',
        '...OnmO...',
        '....OO....',
    ],
    # guild bank: a banner on a rod with a gold coin device
    'banner': [
        'OOOOOOOOOOO',
        'OgggggggggO',
        'OOOOOOOOOOO',
        '.ONNnnnnmO.',
        '.ONnnnnnmO.',
        '.OnnOOOnmO.',
        '.OnOYHHOmO.',
        '.OnOHHhOmO.',
        '.OnnOOOnmO.',
        '.OnnnnnnmO.',
        '.OnnnOnnmO.',
        '.OnnO.OnmO.',
        '.OnO...OmO.',
        '.OO.....OO.',
    ],
    # prefixes: a name-tag shape with a hole and a short string
    'nametag': [
        '..OO........',
        '.O..O.......',
        '.O..O.......',
        '..OOOOOOOOO.',
        '..OWWWWWWWgO',
        '.OWgOWgggggO',
        'OWggggggggfO',
        'OWgfffffffgO',
        '.OfggggggffO',
        '..OffffffffO',
        '...OOOOOOOO.',
    ],
    # invsee: an open eye, blue iris, black pupil
    'eye': [
        '...OOOOOO...',
        '.OOWWWWWWOO.',
        'OWWWWNnWWWWO',
        'OWWWNnOmWWWO',
        'OWWWnOOmWWfO',
        '.OOfWmmWfOO.',
        '...OOOOOO...',
    ],
    # invsee offline: a closed eye with lashes
    'eye_closed': [
        '............',
        '............',
        'O..........O',
        '.OO......OO.',
        '...OOOOOO...',
        '..O..O..O...',
        '.O...O...O..',
    ],
    # trashcan: a waste bin with a lid and grooves
    'bin': [
        '....OOO....',
        'OOOOOfOOOOO',
        'OWWggggggfO',
        'OOOOOOOOOOO',
        '.OgfOfOfeO.',
        '.OgfOfOfeO.',
        '.OgfOfOfeO.',
        '.OgfOfOfeO.',
        '.OgfOfOfeO.',
        '.OffOfOeeO.',
        '..OOOOOOO..',
    ],
    # plots: a wooden signpost (an arrow board pointing right on a post)
    # standing on a grass plot
    'signpost': [
        '..OOOO......',
        '..OYhO......',
        'OOOOOOOOOO..',
        'OYYYYYYYYHO.',
        'OYHHHHHHHHhO',
        'OHhhhhhhhhO.',
        'OOOOOOOOOO..',
        '..OYhO......',
        '..OYhO......',
        '..OYhO......',
        '.OOOOOOOOOO.',
        'OVVVVVVVVVvO',
        'OvvvvvvvvvuO',
        '.OOOOOOOOOO.',
    ],
    # ender chest: a purple orb with a light core (our own mark)
    'ender': shaded(disc_mask(10), 10, 10, 'P', 'p', 'p',
                    extra={(4, 4): 'V', (5, 4): 'v', (4, 5): 'v', (5, 5): 'u', (3, 3): 'P'}),
}


def _ticket(stripe):
    """The ticket stub with its stripe (column 2) in ``stripe``."""
    rows = [list(r) for r in PICTOGRAMS['ticket']]
    for j in range(1, 7):
        rows[j][2] = stripe
    return [''.join(r) for r in rows]


PICTOGRAMS['ticket_valid'] = _ticket('v')
PICTOGRAMS['ticket_invalid'] = _ticket('s')


def pictogram_size(name):
    return P.sprite_size(PICTOGRAMS[name])


def draw_pictogram(img, name, x, y, flip_x=False):
    """Draw pictogram ``name`` with its top-left at (x, y). Returns (w, h)."""
    rows = PICTOGRAMS[name]
    P.sprite(img, x, y, rows, flip_x=flip_x)
    return P.sprite_size(rows)


# Soulrend-compatible names: motifs are the pictograms here.
MOTIFS = PICTOGRAMS
motif_size = pictogram_size
draw_motif = draw_pictogram
