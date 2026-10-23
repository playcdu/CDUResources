"""Faithful master palette: 24 named colours in seven ramps.

Every ramp is ordered dark -> light. Unlike the cozy and Soulrend themes,
pure black (the panel and button outline) and pure white (the top-left bevel,
the inner slot highlight, button lettering) ARE allowed: the vanilla
inventory language is built from them. Colour values are facts, not artwork;
no texture was sampled to choose them (see docs/FAITHFUL-STYLE-GUIDE.md,
section 0). Painters place only colours from this module (``snap`` pulls
transformed pixels back onto the palette).

Ramps and their jobs (see docs/FAITHFUL-STYLE-GUIDE.md section 2):

ink     the black outline (ink_0) and the dark text / label shadow grey (ink_1)
grey    the GUI greys: slot shadow, bevel shade, stone flecks, button face,
        slot fill, lit bevel, the panel and white
green   selected state, ready / valid marks
red     danger buttons, invalid marks, the bin
gold    primary bevel, coins, the star, emphasis
blue    information accents: the lens, the eye, trade arrows
purple  the ender chest panel and its trim only

Licence: MIT (tooling). Colour choices are original.
"""
from __future__ import annotations

import sys as _sys

if __name__ == 'palette':                 # imported by its plain name from tools/faithful
    # one module object per process: if the package copy exists, the plain name
    # becomes it (the import machinery returns sys.modules[name]); else this
    # module also serves as faithful.palette. Shared state (lettering registry)
    # therefore never splits across two copies.
    if 'faithful.palette' in _sys.modules:
        _sys.modules[__name__] = _sys.modules['faithful.palette']
    else:
        _sys.modules['faithful.palette'] = _sys.modules[__name__]

THEME = 'faithful'
ALLOW_PURE_BW = True        # the style lint must not flag (0,0,0) / (255,255,255)

# --- Ramps (dark -> light) ----------------------------------------------------
INK = [
    (0, 0, 0),        # ink_0  outline of panels, buttons and sprites; the pin colour
    (64, 64, 64),     # ink_1  dark text on light plates; the shadow under white labels
]
GREY = [
    (55, 55, 55),     # grey_0 slot inner shadow (top/left), disabled face
    (85, 85, 85),     # grey_1 panel and button bottom/right bevel
    (100, 100, 100),  # grey_2 dark stone fleck on button faces
    (113, 113, 113),  # grey_3 button face
    (139, 139, 139),  # grey_4 slot fill, light stone fleck, recessed tile fill
    (160, 160, 160),  # grey_5 button top/left bevel, info plate face, disabled label
    (198, 198, 198),  # grey_6 the panel: title and inventory bands live on it
    (255, 255, 255),  # grey_7 white: panel top/left bevel, slot inner highlight, labels
]
GREEN = [
    (52, 104, 44),    # green_0 selected bottom/right bevel, dark leaf
    (92, 152, 68),    # green_1 selected face, ready / valid stripe
    (152, 206, 112),  # green_2 selected plate face, lit green
]
RED = [
    (104, 34, 34),    # red_0 danger bottom/right bevel, invalid stripe shade
    (156, 58, 52),    # red_1 danger face
    (206, 108, 96),   # red_2 danger top/left bevel
]
GOLD = [
    (140, 102, 22),   # gold_0 coin rim shade
    (204, 162, 44),   # gold_1 coin body, accent line
    (252, 222, 100),  # gold_2 primary top/left bevel, coin glint, star
]
BLUE = [
    (40, 64, 128),    # blue_0 lens glass shade, iris
    (72, 112, 184),   # blue_1 accent line, arrows
    (136, 172, 228),  # blue_2 glint
]
PURPLE = [
    (70, 52, 98),     # purple_0 ender chest bottom/right bevel and trim
    (190, 182, 206),  # purple_1 ender chest panel (still light: live text sits on it)
]

RAMPS = {
    'ink': INK, 'grey': GREY, 'green': GREEN, 'red': RED, 'gold': GOLD, 'blue': BLUE, 'purple': PURPLE,
}

NAMED = {}
for _ramp, _colours in RAMPS.items():
    for _i, _c in enumerate(_colours):
        NAMED[f'{_ramp}_{_i}'] = _c
MASTER = list(NAMED.values())
assert len(MASTER) == len(set(MASTER)) == 24

# Semantic aliases used throughout the guide and primitives.
OUTLINE = INK[0]
OUTLINE_DEEP = INK[0]
TEXT_DARK = INK[1]            # vanilla-style dark grey text on light plates
TEXT_LIGHT = GREY[7]          # white button lettering
SHADOW = INK[1]               # the (+1, +1) shadow under white lettering
TEXT_DISABLED = GREY[5]       # disabled lettering (mid grey)
GLOW = GREY[7]                # pulse highlight
TITLE_BAND = GREY[6]          # live vanilla title (#404040) sits on this
SHEET = GREY[6]               # the panel body
PANEL = GREY[6]
BEVEL_LIGHT = GREY[7]
BEVEL_DARK = GREY[1]
SLOT_FILL = GREY[4]
SLOT_SHADOW = GREY[0]
BUTTON_FACE = GREY[3]
BUTTON_LIT = GREY[5]
DISABLED_FACE = GREY[0]
TRANSPARENT = (0, 0, 0, 0)

# Family identity: accent ramp (the 1 px line under the title band uses
# accent[1]; ``line`` False = plain), secondary ramp, pictogram, motif summary.
# Accents are decorative only; item wells and button grammar never change
# per family.
FAMILY_ACCENT = {
    'economy':    {'accent': GOLD,  'secondary': GREEN, 'pictogram': 'coin',    'line': True,
                   'motif': 'a gold coin disc'},
    'auction':    {'accent': RED,   'secondary': GOLD,  'pictogram': 'gavel',   'line': True,
                   'motif': 'a gavel silhouette'},
    'chest_shop': {'accent': GREEN, 'secondary': GOLD,  'pictogram': 'chest',   'line': True,
                   'motif': 'a chest-lid silhouette'},
    'trade':      {'accent': BLUE,  'secondary': GREEN, 'pictogram': 'arrows',  'line': True,
                   'motif': 'two opposed arrows'},
    'ticket':     {'accent': GREEN, 'secondary': RED,   'pictogram': 'ticket',  'line': True,
                   'motif': 'a ticket stub'},
    'admin_shop': {'accent': BLUE,  'secondary': GREY,  'pictogram': 'shield',  'line': True,
                   'motif': 'a plain shield'},
    'guild_bank': {'accent': GOLD,  'secondary': BLUE,  'pictogram': 'banner',  'line': True,
                   'motif': 'a hanging banner'},
    'prefixes':   {'accent': BLUE,  'secondary': GOLD,  'pictogram': 'nametag', 'line': True,
                   'motif': 'a name-tag shape'},
    'invsee':     {'accent': BLUE,  'secondary': GREEN, 'pictogram': 'eye',     'line': True,
                   'motif': 'an eye'},
    'utility':    {'accent': GREY,  'secondary': GREY,  'pictogram': None,      'line': False,
                   'motif': 'plain vanilla panel, no story'},
}
# Sub-skins and state variants that override the family entry.
SKIN_ACCENT = {
    'ticket_valid':   {'accent': GREEN,  'secondary': GOLD, 'pictogram': 'ticket_valid', 'line': True,
                       'motif': 'a ticket stub with a green (valid) stripe'},
    'ticket_invalid': {'accent': RED,    'secondary': GREY, 'pictogram': 'ticket_invalid', 'line': True,
                       'motif': 'a ticket stub with a red (invalid) stripe'},
    'invsee_offline': {'accent': GREY,   'secondary': BLUE, 'pictogram': 'eye_closed', 'line': True,
                       'motif': 'a closed eye (offline)'},
    'trashcan':       {'accent': RED,    'secondary': GREY, 'pictogram': 'bin', 'line': True,
                       'motif': 'a waste bin'},
    'ender_chest':    {'accent': PURPLE, 'secondary': GREY, 'pictogram': 'ender', 'line': True,
                       'motif': 'purple-tinted panel variant with an ender-eye pictogram'},
    'crafting':       {'accent': GREY,   'secondary': GREY, 'pictogram': None, 'line': False,
                       'motif': 'plain vanilla crafting look'},
}
for _n in range(1, 7):
    SKIN_ACCENT[f'template_chest_{_n}'] = FAMILY_ACCENT['utility']

# Panel ramps: (outline, dark bevel, panel, light bevel). The ender chest
# swaps in a purple-tinted panel that is still light enough for live text.
PANEL_RAMP = [INK[0], GREY[1], GREY[6], GREY[7]]
ENDER_PANEL_RAMP = [INK[0], PURPLE[0], PURPLE[1], GREY[7]]


def accent_for(key, family=None):
    """Accent entry for a skin key: sub-skin override first, then its family.
    Unknown families fall back to the utility entry."""
    if key in SKIN_ACCENT:
        return SKIN_ACCENT[key]
    if family is None:
        import geometry
        family = geometry.skin(key).family
    return FAMILY_ACCENT.get(family, FAMILY_ACCENT['utility'])


def rgba(name, alpha=255):
    """'grey_3' -> (113, 113, 113, 255). Also accepts an RGB or RGBA tuple."""
    if isinstance(name, tuple):
        return tuple(name[:3]) + ((name[3] if len(name) == 4 else alpha),)
    if name not in NAMED:
        raise KeyError(f'Unknown Faithful palette colour {name!r}; known: {", ".join(NAMED)}')
    return NAMED[name] + (alpha,)


def name_of(colour):
    """Reverse lookup of an exact palette colour; None when off-palette."""
    rgb = tuple(colour[:3])
    for n, c in NAMED.items():
        if c == rgb:
            return n
    return None


def ramp_of(colour):
    """('grey', 3) for grey_3, or None when off-palette."""
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
    data = img.get_flattened_data() if hasattr(img, 'get_flattened_data') else img.getdata()
    return sum(1 for p in data if p[3] and tuple(p[:3]) not in allowed)


def step(colour, delta):
    """Move ``delta`` steps along the colour's own ramp (clamped). Off-palette
    colours are snapped first."""
    rgb = tuple(colour[:3])
    ramp, i = ramp_of(rgb) or ramp_of(nearest(rgb))
    cols = RAMPS[ramp]
    return cols[max(0, min(len(cols) - 1, i + delta))]
