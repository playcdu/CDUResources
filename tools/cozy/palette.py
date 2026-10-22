"""Cozy master palette: one shared set of 34 named colours in ten ramps.

Every ramp is ordered dark -> light. No colour is pure black or pure white;
outlines use the warm INK ramp. Painters should only place colours from this
module (``snap`` pulls transformed pixels back onto the palette).

Licence: MIT (tooling). Colour choices are original.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_HERE = str(_Path(__file__).resolve().parent)
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

RGB = tuple
RGBA = tuple

# --- Base ramps (dark -> light) --------------------------------------------
INK = [
    (46, 28, 27),    # ink_0  deepest outline, creases, lettering on paper
    (68, 42, 36),    # ink_1  standard 1px outline
    (97, 64, 50),    # ink_2  soft outline / lighter line weight
]
WOOD = [
    (84, 50, 36),    # wood_0 deep grain, plank seams, warm shadow
    (114, 71, 45),   # wood_1 shadowed plank
    (146, 95, 58),   # wood_2 plank body
    (180, 126, 77),  # wood_3 lit plank
    (210, 160, 104), # wood_4 top-left highlight
]
PARCHMENT = [
    (190, 163, 124), # parch_0 paper shadow / fold / linen weave
    (216, 193, 152), # parch_1 paper body (shaded)
    (236, 218, 181), # parch_2 paper body (title and inventory bands)
    (248, 238, 212), # parch_3 cream highlight (never white)
]
BRASS = [
    (128, 88, 40),   # brass_0 brass shadow
    (180, 132, 56),  # brass_1 brass body
    (222, 178, 84),  # brass_2 lit brass
    (247, 222, 140), # brass_3 specular glint
]
# --- Accent ramps -----------------------------------------------------------
SAGE = [(72, 92, 62), (112, 136, 88), (164, 182, 124)]     # herbs, awnings
BERRY = [(112, 40, 46), (164, 60, 60), (212, 108, 92)]     # wax, danger
SKY = [(60, 78, 104), (98, 126, 156), (156, 182, 198)]     # dusk sky, airmail
EMBER = [(198, 96, 40), (240, 152, 64), (252, 212, 138)]   # lantern / candle glow
PLUM = [(52, 40, 74), (96, 74, 132), (164, 138, 196)]      # ender dusk, name tags
ASH = [(92, 84, 80), (132, 122, 114), (176, 166, 152)]     # iron, disabled, offline

RAMPS = {
    'ink': INK, 'wood': WOOD, 'parchment': PARCHMENT, 'brass': BRASS,
    'sage': SAGE, 'berry': BERRY, 'sky': SKY, 'ember': EMBER, 'plum': PLUM, 'ash': ASH,
}
_SHORT = {'parchment': 'parch'}

NAMED = {}
for _ramp, _colours in RAMPS.items():
    for _i, _c in enumerate(_colours):
        NAMED[f'{_SHORT.get(_ramp, _ramp)}_{_i}'] = _c
MASTER = list(NAMED.values())
assert len(MASTER) == len(set(MASTER)) == 34

# Semantic aliases used throughout the guide and primitives.
OUTLINE = INK[1]
OUTLINE_DEEP = INK[0]
TEXT_DARK = INK[0]            # lettering on parchment / linen / brass
TEXT_LIGHT = PARCHMENT[3]     # lettering on dark wood / wax
SHADOW = WOOD[0]
GLOW = EMBER[2]
TITLE_BAND = PARCHMENT[2]     # live vanilla title (#404040) sits on this
TRANSPARENT = (0, 0, 0, 0)

# Family identity: accent ramp, secondary ramp, motif summary. Accents are
# decorative only; item wells and button grammar never change per family.
FAMILY_ACCENT = {
    'economy':    {'accent': SAGE,  'secondary': BRASS, 'motif': 'market-stall awning, coin purse, account ledger'},
    'auction':    {'accent': BERRY, 'secondary': BRASS, 'motif': 'gavel, hanging price tags, ledger'},
    'chest_shop': {'accent': EMBER, 'secondary': WOOD,  'motif': 'shop-front sign, shelves, crates'},
    'trade':      {'accent': SKY,   'secondary': EMBER, 'motif': 'two mugs on a shared table, handshake rope knot'},
    'ticket':     {'accent': SKY,   'secondary': BERRY, 'motif': 'stamped postcard; valid has a wax seal, invalid a torn edge'},
    'admin_shop': {'accent': BRASS, 'secondary': SAGE,  'motif': "quartermaster's counter"},
    'guild_bank': {'accent': ASH,   'secondary': SAGE,  'motif': 'iron-banded strongbox, guild banner'},
    'prefixes':   {'accent': PLUM,  'secondary': EMBER, 'motif': 'name tags pinned to a corkboard'},
    'invsee':     {'accent': SKY,   'secondary': BRASS, 'motif': 'magnifying glass over a satchel'},
    'utility':    {'accent': WOOD,  'secondary': BRASS, 'motif': 'plain warm wood framing'},
}
# Utility sub-skins and state variants that override the family entry.
SKIN_ACCENT = {
    'invsee_offline': {'accent': ASH,  'secondary': SKY,   'motif': 'satchel under blue-grey moonlight (offline)'},
    'ticket_valid':   {'accent': SKY,  'secondary': BERRY, 'motif': 'postcard closed with a red wax seal'},
    'ticket_invalid': {'accent': ASH,  'secondary': BERRY, 'motif': 'postcard with a torn edge and no seal'},
    'trashcan':       {'accent': SAGE, 'secondary': WOOD,  'motif': 'compost bin and fallen leaves'},
    'ender_chest':    {'accent': PLUM, 'secondary': PLUM,  'motif': 'indigo-dark wood, soft purple lantern light'},
    'crafting':       {'accent': WOOD, 'secondary': BRASS, 'motif': 'workbench and tool loop'},
}
for _n in range(1, 7):
    SKIN_ACCENT[f'template_chest_{_n}'] = FAMILY_ACCENT['utility']

# Ender chest uses indigo-dark wood instead of WOOD. Same structure, dark -> light.
ENDER_WOOD = [PLUM[0], INK[1], PLUM[1], WOOD[1], PLUM[2]]


def accent_for(key, family=None):
    """Accent entry for a skin key: sub-skin override first, then its family."""
    if key in SKIN_ACCENT:
        return SKIN_ACCENT[key]
    if family is None:
        import geometry
        family = geometry.skin(key).family
    return FAMILY_ACCENT[family]


def rgba(name, alpha=255):
    """'wood_2' -> (146, 95, 58, 255). Also accepts an RGB or RGBA tuple."""
    if isinstance(name, tuple):
        return tuple(name[:3]) + ((name[3] if len(name) == 4 else alpha),)
    if name not in NAMED:
        raise KeyError(f'Unknown palette colour {name!r}; known: {", ".join(NAMED)}')
    return NAMED[name] + (alpha,)


def name_of(colour):
    """Reverse lookup of an exact palette colour; None when off-palette."""
    rgb = tuple(colour[:3])
    for n, c in NAMED.items():
        if c == rgb:
            return n
    return None


def ramp_of(colour):
    """('wood', 2) for wood_2, or None when off-palette."""
    rgb = tuple(colour[:3])
    for ramp, cols in RAMPS.items():
        if rgb in cols:
            return ramp, cols.index(rgb)
    return None


def luminance(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def nearest(colour, choices=None):
    """Nearest palette colour by the 'redmean' weighted RGB distance."""
    r, g, b = colour[:3]
    best, bd = None, float('inf')
    for c in (choices or MASTER):
        rm = (r + c[0]) / 2
        d = (2 + rm / 256) * (r - c[0]) ** 2 + 4 * (g - c[1]) ** 2 + (2 + (255 - rm) / 256) * (b - c[2]) ** 2
        if d < bd:
            best, bd = c, d
    return best


def snap(img, choices=None):
    """Copy of ``img`` with every opaque pixel snapped to the palette. Alpha unchanged."""
    out = img.copy()
    px = out.load()
    cache = {}
    for y in range(out.height):
        for x in range(out.width):
            p = px[x, y]
            if p[3] == 0:
                continue
            k = p[:3]
            if k not in cache:
                cache[k] = nearest(k, choices)
            px[x, y] = cache[k] + (p[3],)
    return out


def off_palette(img):
    """Count of opaque pixels whose RGB is not in the master palette."""
    allowed = set(MASTER)
    return sum(1 for p in img.getdata() if p[3] and tuple(p[:3]) not in allowed)


def step(colour, delta):
    """Move ``delta`` steps along the colour's own ramp (clamped). Off-palette colours
    are snapped first."""
    rgb = tuple(colour[:3])
    found = ramp_of(rgb) or ramp_of(nearest(rgb))
    ramp, i = found
    cols = RAMPS[ramp]
    return cols[max(0, min(len(cols) - 1, i + delta))]
