"""Soulrend master palette: 36 named colours in eleven ramps.

Every ramp is ordered dark -> light. There is no pure black and no pure white:
the darkest colour is the warm near-black ``ink_0`` and the lightest is the
bone-white ``vellum_3``. Painters place only colours from this module
(``snap`` pulls transformed pixels back onto the palette).

Ramps and their jobs (see docs/SOULREND-STYLE-GUIDE.md section 2):

ink     warm near-black outlines, lettering on vellum and stone
iron    cool dark greys: blackened iron plates, rims, rivets, chains, disabled
stone   mossy slate: dungeon masonry, carved tablets, socket walls
umber   dark wood and leather, the menu sheet (the Excalibur register)
vellum  bone-white to aged parchment: the live text bands, secondary strips
blood   deep red cloth and wax: danger controls, seals, banners
ember   orange bonfire and candle glow, pulse rings
soul    cold cyan soul-light: selected rim, runes, a few magical accents
gold    tarnished gold: primary rims and lettering, filigree, coins
moss    muted green: moss tufts, tattered banners
void    obsidian purple: the ender chest only

Licence: MIT (tooling). Colour choices are original.
"""
from __future__ import annotations

import sys as _sys

if __name__ == 'palette':                 # imported by its plain name from tools/soulrend
    # one module object per process: if the package copy exists, the plain name
    # becomes it (the import machinery returns sys.modules[name]); else this
    # module also serves as soulrend.palette. Shared state (backdrop, cut and
    # lettering registries) therefore never splits across two copies.
    if 'soulrend.palette' in _sys.modules:
        _sys.modules[__name__] = _sys.modules['soulrend.palette']
    else:
        _sys.modules['soulrend.palette'] = _sys.modules[__name__]

THEME = 'soulrend'

# --- Ramps (dark -> light) ----------------------------------------------------
INK = [
    (18, 13, 14),     # ink_0  deepest outline, heavy bottom/right edges, lettering on vellum
    (31, 22, 22),     # ink_1  standard 1 px outline
    (47, 34, 32),     # ink_2  soft outline / lighter line weight
]
IRON = [
    (40, 42, 49),     # iron_0 blackened iron body in shadow
    (62, 66, 75),     # iron_1 iron body
    (96, 101, 110),   # iron_2 lit iron, rivet heads
    (146, 150, 156),  # iron_3 cold specular glint (top-left)
]
STONE = [
    (37, 46, 44),     # stone_0 mortar, deep recess
    (55, 66, 62),     # stone_1 slate body in shadow
    (80, 93, 85),     # stone_2 slate body
    (113, 124, 111),  # stone_3 lit slate edge, carved tablet face
]
UMBER = [
    (39, 29, 26),     # umber_0 seams, scuffs
    (51, 38, 33),     # umber_1 sheet body (Excalibur register)
    (70, 52, 44),     # umber_2 lit leather / wood
    (98, 74, 59),     # umber_3 worn highlight
]
VELLUM = [
    (166, 148, 118),  # vellum_0 aged fold, deckled edge shade
    (198, 184, 154),  # vellum_1 vellum in shade, fibres
    (222, 210, 184),  # vellum_2 vellum body: title and inventory bands
    (238, 230, 210),  # vellum_3 bone-white highlight (never white)
]
BLOOD = [
    (78, 18, 24),     # blood_0 wax / cloth shadow
    (126, 30, 34),    # blood_1 wax / cloth body
    (176, 48, 44),    # blood_2 gloss, lit fold
]
EMBER = [
    (172, 76, 28),    # ember_0 dying coal, faint glow
    (228, 126, 44),   # ember_1 flame body, pulse ring on dark
    (250, 190, 104),  # ember_2 flame core, pulse ring on light
]
SOUL = [
    (22, 90, 102),    # soul_0 deep soul glow
    (52, 174, 188),   # soul_1 soul-light, selected rim
    (158, 234, 236),  # soul_2 soul flare (sparing)
]
GOLD = [
    (98, 74, 36),     # gold_0 tarnish, shadow
    (152, 118, 54),   # gold_1 tarnished gold body
    (204, 168, 92),   # gold_2 lit gold, lettering on iron
]
MOSS = [
    (34, 50, 36),     # moss_0 deep moss, banner shadow
    (56, 80, 50),     # moss_1 moss / banner body
    (92, 114, 66),    # moss_2 lit moss
]
VOID = [
    (34, 24, 46),     # void_0 obsidian
    (74, 50, 100),    # void_1 void purple
]

RAMPS = {
    'ink': INK, 'iron': IRON, 'stone': STONE, 'umber': UMBER, 'vellum': VELLUM,
    'blood': BLOOD, 'ember': EMBER, 'soul': SOUL, 'gold': GOLD, 'moss': MOSS, 'void': VOID,
}

NAMED = {}
for _ramp, _colours in RAMPS.items():
    for _i, _c in enumerate(_colours):
        NAMED[f'{_ramp}_{_i}'] = _c
MASTER = list(NAMED.values())
assert len(MASTER) == len(set(MASTER)) == 36
assert (0, 0, 0) not in MASTER and (255, 255, 255) not in MASTER

# Semantic aliases used throughout the guide and primitives.
OUTLINE = INK[1]
OUTLINE_DEEP = INK[0]
TEXT_DARK = INK[0]            # lettering on vellum and carved stone
TEXT_LIGHT = VELLUM[3]        # lettering on blood wax and dark umber
TEXT_GOLD = GOLD[2]           # lettering on blackened iron
SHADOW = INK[0]
GLOW = EMBER[2]
SOUL_GLOW = SOUL[1]
TITLE_BAND = VELLUM[2]        # live vanilla title (#404040) sits on this
SHEET = UMBER[1]              # the menu sheet body
TRANSPARENT = (0, 0, 0, 0)

# Family identity: accent ramp, secondary ramp, motif summary. Accents are
# decorative only; item wells and button grammar never change per family.
FAMILY_ACCENT = {
    'economy':    {'accent': GOLD,  'secondary': EMBER, 'motif': 'torchlit counting vault, coin scales, ledger with wax seal'},
    'auction':    {'accent': BLOOD, 'secondary': GOLD,  'motif': 'auction block, gavel, hanging banner tags, candle clock'},
    'chest_shop': {'accent': EMBER, 'secondary': UMBER, 'motif': 'merchant stall under a stone arch, crates, iron lantern'},
    'trade':      {'accent': GOLD,  'secondary': BLOOD, 'motif': 'two goblets on a stone table, a chain-link handshake knot'},
    'ticket':     {'accent': BLOOD, 'secondary': GOLD,  'motif': 'wax-sealed writ of passage'},
    'admin_shop': {'accent': IRON,  'secondary': GOLD,  'motif': "quartermaster's armoury rack"},
    'guild_bank': {'accent': IRON,  'secondary': MOSS,  'motif': 'iron vault door, chains, guild heraldic banner'},
    'prefixes':   {'accent': GOLD,  'secondary': BLOOD, 'motif': 'heraldic shields and name plates on a stone wall'},
    'invsee':     {'accent': SOUL,  'secondary': UMBER, 'motif': 'scrying mirror / soul-lens over a satchel'},
    'plot':       {'accent': MOSS,  'secondary': BLOOD, 'motif': "boundary stakes and surveyor's chain, a sealed land writ, a stone waymarker"},
    'utility':    {'accent': IRON,  'secondary': STONE, 'motif': 'plain dark stone and iron framing'},
}
# Sub-skins and state variants that override the family entry.
SKIN_ACCENT = {
    'invsee_offline': {'accent': IRON,  'secondary': SOUL,  'motif': 'the same satchel, cold blue-grey and unlit (offline)'},
    'ticket_valid':   {'accent': BLOOD, 'secondary': GOLD,  'motif': 'writ of passage closed with an intact blood-red seal'},
    'ticket_invalid': {'accent': EMBER, 'secondary': IRON,  'motif': 'burnt and torn writ, broken seal'},
    'trashcan':       {'accent': EMBER, 'secondary': IRON,  'motif': 'ash-pit brazier with dying embers and burnt leaves'},
    'ender_chest':    {'accent': VOID,  'secondary': SOUL,  'motif': 'obsidian and void-purple with soul-cyan runes'},
    'crafting':       {'accent': IRON,  'secondary': EMBER, 'motif': "blacksmith's anvil and tool rack"},
}
for _n in range(1, 7):
    SKIN_ACCENT[f'template_chest_{_n}'] = FAMILY_ACCENT['utility']

# The ender chest sheet: obsidian instead of umber. Same structure, dark -> light.
VOID_SHEET = [INK[1], VOID[0], VOID[1], IRON[2]]


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
    """'iron_2' -> (96, 101, 110, 255). Also accepts an RGB or RGBA tuple."""
    if isinstance(name, tuple):
        return tuple(name[:3]) + ((name[3] if len(name) == 4 else alpha),)
    if name not in NAMED:
        raise KeyError(f'Unknown Soulrend palette colour {name!r}; known: {", ".join(NAMED)}')
    return NAMED[name] + (alpha,)


def name_of(colour):
    """Reverse lookup of an exact palette colour; None when off-palette."""
    rgb = tuple(colour[:3])
    for n, c in NAMED.items():
        if c == rgb:
            return n
    return None


def ramp_of(colour):
    """('iron', 2) for iron_2, or None when off-palette."""
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
