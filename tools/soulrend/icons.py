"""Original hand-authored icon, crest and motif sprites for the Soulrend theme.

Icons sit on the 18x18 icon buttons (close, balance, search, settings, rank)
and the 18x72 balance column. Crests are small heraldic shields for banners,
seals and the prefixes wall. Motifs are decorative sprites for frames and
static protected artwork (never inside item wells). Every sprite is a list of
strings in the shared colour key ``primitives.SK`` ('.' is transparent):

    O ink_0  o ink_1  i ink_2      a b c d  iron_0..3    m n p q  stone_0..3
    0 1 2 3  umber_0..3            v w x y  vellum_0..3  r s t    blood_0..2
    e f F    ember_0..2            k l L    soul_0..2    g h H    gold_0..2
    j z Z    moss_0..2

All drawings are original (CC0-1.0); code MIT. Nothing is traced from the
modpack's assets or from the cozy icons.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

if __name__ == 'icons':                 # imported by its plain name from tools/soulrend
    # one module object per process: if the package copy exists, the plain name
    # becomes it (the import machinery returns sys.modules[name]); else this
    # module also serves as soulrend.icons. Shared state (backdrop, cut and
    # lettering registries) therefore never splits across two copies.
    if 'soulrend.icons' in _sys.modules:
        _sys.modules[__name__] = _sys.modules['soulrend.icons']
    else:
        _sys.modules['soulrend.icons'] = _sys.modules[__name__]
_TOOLS = _Path(__file__).resolve().parents[1]
if str(_TOOLS) not in _sys.path:
    _sys.path.append(str(_TOOLS))

from soulrend import primitives as P  # noqa: E402
from soulrend.palette import BLOOD, INK, IRON  # noqa: E402

# --- Icons (drawn centred in the button body) ---------------------------------

# Balance: a leather coin pouch hanging on a short iron chain, gold drawstring,
# a tarnished coin peeking out at its foot.
PURSE = [
    '....odo.....',
    '...oc.ao....',
    '....oao.....',
    '.....c......',
    '....odo.....',
    '...oc.ao....',
    '..ooHhgoo...',
    '.o32hHg21o..',
    'o332222110o.',
    'o322222110o.',
    'o2222211ooo.',
    'o222211oHHo.',
    '.o21100oHhgo',
    '..oooooohggo',
    '.......oooo.',
]

# Search: a scrying lens. Iron ring, deep soul-glass with a cold glint, an
# iron collar and an umber grip running to the lower right.
LENS = [
    '..oooo......',
    '.odccbo.....',
    'odLlkkao....',
    'oclkkkao....',
    'ockkkkao....',
    'obkkkkao....',
    '.obaaaoo....',
    '..oooobaO...',
    '......Oc2o..',
    '.......o32o.',
    '........o32o',
    '.........oo.',
]

# Settings: a forged iron cog, eight teeth, a black axle, lit top-left.
COG = [
    '....odcbo....',
    '..ooodcbooo..',
    '.odcocccobbo.',
    '.occccccbbbo.',
    'ooocccaaabboo',
    'odccbaOOOabbo',
    'odcbbaOOOabao',
    'ocbbbaOOOaaao',
    'ooobbbaaabaoo',
    '.obbbbbbbaao.',
    '.obbobbbobao.',
    '..ooobbaooo..',
    '....obaao....',
]

# Rank: a heraldic crest. Gold-bordered blood shield with a gold chevron and
# a small iron crown of three points above it.
CREST_RANK = [
    '..o.o.o..',
    '..dodod..',
    '.occcccbo.',
    'ooooooooooo',
    'oHHHhhhhhgo',
    'oHttsssssgo',
    'oHtsHssHrgo',
    'oHsHhssHhgo',
    'oHHhsrsrhgo',
    'ohhsrsssrgo',
    '.ohssssrgo.',
    '.ohsssrrgo.',
    '..ohsrrgo..',
    '...ohrgo...',
    '....ogo....',
    '.....o.....',
]

COIN = ['.ooo.', 'oHHho', 'oHhgo', 'ohggo', '.ooo.']

ICONS = {
    'balance': PURSE,
    'search': LENS,
    'settings': COG,
    'rank': CREST_RANK,
    'coin': COIN,
}

# --- Seal emblems (5x5, pressed into wax) ------------------------------------
EMBLEMS = {
    'x': ['#...#', '.#.#.', '..#..', '.#.#.', '#...#'],
    'cross': ['..#..', '.###.', '..#..', '..#..', '..#..'],
    'crown': ['#.#.#', '#####', '#...#', '#####', '.....'],
    'tower': ['#.#.#', '#####', '.#.#.', '.###.', '.###.'],
    'coin': ['.###.', '#...#', '#.#.#', '#...#', '.###.'],
    'key': ['.##..', '#..#.', '.##..', '..#..', '..##.'],
    'flame': ['..#..', '.##..', '.###.', '#.##.', '.##..'],
    'check': ['....#', '...#.', '#.#..', '.#...', '.....'],
}


def draw_emblem(img, cx, cy, name, ramp=BLOOD):
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
    return P.sprite_size(ICONS[name])


def draw_icon(img, name, box):
    """Centre icon ``name`` inside box (x, y, w, h). Returns its top-left."""
    rows = ICONS[name]
    w, h = P.sprite_size(rows)
    x = box[0] + (box[2] - w) // 2
    y = box[1] + (box[3] - h) // 2
    P.sprite(img, x, y, rows)
    return x, y


def close_seal(img, box, seed=0):
    """The close control: a round blood-wax seal studded with four iron studs
    and pressed with a 2 px X (ink_0 strokes with a blood_2 lit lip
    below-right), filling the body box (diameter = min(w, h) - 1, odd),
    right-aligned so the pin column is wax. Returns (cx, cy, r)."""
    x, y, w, h = box
    r = (min(w, h) - 1) // 2
    cx, cy = x + w - 1 - r, y + h // 2
    P.wax_seal(img, cx, cy, r, BLOOD, seed, studs=4)
    span = max(2, r - 4)
    for k in range(-span, span + 1):
        for (px, py) in ((cx + k, cy + k), (cx + k, cy - k)):
            P.put(img, px + 1, py + 1, BLOOD[2])
    for k in range(-span, span + 1):
        for (px, py) in ((cx + k, cy + k), (cx + k, cy - k)):
            P.put(img, px, py, INK[0])
    return cx, cy, r


# --- Crests: heraldic shields (9x11) for banners, seals, the prefixes wall ----
_SHIELD = [
    'ooooooooo',
    'o#######o',
    'o#######o',
    'o#######o',
    'o#######o',
    'o#######o',
    '.o#####o.',
    '.o#####o.',
    '..o###o..',
    '...o#o...',
    '....o....',
]
CREST_CHARGES = {
    # (field colour key, charge colour key, charge pixels relative to the field)
    'chevron': ('s', 'H', ['.......', '.......', '...#...', '..#.#..', '.#...#.', '#.....#', '.......']),
    'cross':   ('z', 'H', ['...#...', '...#...', '#######', '...#...', '...#...', '...#...', '.......']),
    'tower':   ('b', 'y', ['.#.#.#.', '.#####.', '..###..', '..#.#..', '..###..', '.......', '.......']),
    'flame':   ('s', 'F', ['...#...', '..##...', '..###..', '.#.##..', '.####..', '..##...', '.......']),
    'key':     ('k', 'H', ['..##...', '.#..#..', '..##...', '...#...', '...##..', '...#...', '...##..']),
    'moon':    ('a', 'L', ['..###..', '.##....', '.#.....', '.#.....', '.##....', '..###..', '.......']),
}


def crest_sprite(name):
    """Rows for crest ``name`` (see ``CREST_CHARGES``): a 9x11 shield with a
    lit top-left field edge and the charge in its colour."""
    field, charge, pix = CREST_CHARGES[name]
    rows = [list(r) for r in _SHIELD]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '#':
                rows[j][i] = field
    for j, prow in enumerate(pix):
        for i, ch in enumerate(prow):
            if ch == '#' and rows[j + 1][i + 1] not in 'o.':
                rows[j + 1][i + 1] = charge
    # gold lit rim top-left, tarnish bottom-right
    for i in range(1, 8):
        if rows[1][i] == field:
            rows[1][i] = 'h'
    for j in range(1, 6):
        if rows[j][1] == field:
            rows[j][1] = 'h'
        if rows[j][7] == field:
            rows[j][7] = 'g'
    return [''.join(r) for r in rows]


def crest_size(name):
    return P.sprite_size(crest_sprite(name))


def draw_crest(img, name, x, y):
    P.sprite(img, x, y, crest_sprite(name))
    return crest_size(name)


CRESTS = tuple(CREST_CHARGES)

# --- Motifs for frames and static art ----------------------------------------
MOTIFS = {
    # two-handled goblet of tarnished gold with dark wine
    'goblet': [
        '.ooooooo.',
        'ohHhhhhgo',
        'oHrsssrgo',
        '.ohrrrgo.',
        '..ohhgo..',
        '...oHo...',
        '...ohgo..',
        '..ohhhgo.',
        '.ooooooo.',
    ],
    # judge's gavel: iron-banded umber head, umber handle
    'gavel': [
        '.ooooo.......',
        'o32c21o......',
        'o32c21ooooooo',
        'o21b10o32221o',
        'o21b10ooooooo',
        '.ooooo.......',
    ],
    # coin scales: gold beam on an iron post, two pans
    'scales': [
        '......H......',
        '.....oho.....',
        'ohhhhhHhhhhho',
        '.H....b....H.',
        'H.H...b...H.H',
        'H..H..b..H..H',
        'ohhho.b.ohhho',
        '.ooo..b..ooo.',
        '.....obo.....',
        '...occbbao...',
        '...ooooooo...',
    ],
    # closed ledger bound in umber with an iron clasp and a blood seal ribbon
    'ledger': [
        'ooooooooooo',
        'o333322221o',
        'o3yyyyyyy1o',
        'o2xxxxxxx1db',
        'o2xxxxxxx1ab',
        'o2xwxxxxx1o.',
        'o2xxxxxxx1o',
        'o211111110o',
        'oooosooooo.',
        '....rs.....',
        '....r.s....',
    ],
    # iron-banded crate
    'crate': [
        'oooooooooo',
        'o3222222bo',
        'occccccc0o',
        'o2o2o2o20o',
        'o2o2o2o20o',
        'occccccc0o',
        'o1111111bo',
        'oooooooooo',
    ],
    # iron lantern with ember glass
    'lantern': [
        '...oo...',
        '..o..o..',
        '.oooooo.',
        'ocdccbao',
        'ocFffeao',
        'obfFfeao',
        'obffeeao',
        'oaaaaaao',
        '.oooooo.',
    ],
    # iron key on a ring
    'key': [
        '.ooo.......',
        'oc.do......',
        'od.bo......',
        '.obboooooo.',
        '..oaccccbbo',
        '...oooo.oco',
        '.......o.o.',
    ],
    # anvil on a stone block
    'anvil': [
        'oooooooooooo.',
        'odddcccccbbao',
        '.obbbbbbbbaao',
        '..ooobbbaoo..',
        '....obbao....',
        '...obbbbao...',
        '..obbbbbbao..',
        '.oqqqpppppno.',
        '.opppppnnnmo.',
        '.ooooooooooo.',
    ],
    # smith's hammer, head up
    'hammer': [
        'oooooo..',
        'odccbao.',
        'obbbaao.',
        'oooo2oo.',
        '...o3o..',
        '...o2o..',
        '...o2o..',
        '...o1o..',
        '...ooo..',
    ],
    # tongs
    'tongs': [
        'o...o',
        'co.oa',
        '.cob.',
        '.oco.',
        'ob.ao',
        'b...a',
        'b...a',
        'o...o',
    ],
    # ash-pit brazier with dying embers
    'brazier': [
        '...e.F.e...',
        '..efeFfef..',
        'ooooooooooo',
        'odcccccbbao',
        '.obbbbbbao.',
        '..obbbbao..',
        '...obbao...',
        '..ob...ao..',
        '.oo.....oo.',
    ],
    # scrying mirror: oval of soul glass in a gold frame
    'mirror': [
        '...ooooo...',
        '..oHhhhgo..',
        '.oHkLlkkgo.',
        '.ohLlkkkgo.',
        '.ohlkkkkgo.',
        '.ohkkkkkgo.',
        '.ohkkkk0go.',
        '..ohkkkgo..',
        '...ohhgo...',
        '....oHo....',
        '...ohhgo...',
        '...ooooo...',
    ],
    # leather satchel with a buckle
    'satchel': [
        '...ooooo...',
        '..o.....o..',
        '.ooooooooo.',
        'o333322221o',
        'o322222221o',
        'oooooHoooo.',
        'o2222h22210',
        'o2222222210',
        'o2111111110',
        'ooooooooooo',
    ],
    # a single old bone (the most macabre the theme gets)
    'bone': [
        'oo.......oo',
        'oyo.....oyo',
        '.oyooooowo.',
        '.oxyyyyxxo.',
        '.owoooooowo',
        'owo.....owo',
        'oo.......oo',
    ],
    # rolled writ of passage with a blood seal
    'writ': [
        '.oooooooooo.',
        'oyxxxxxxxxwo',
        'oxyyyyyyyxvo',
        '.oxxxxxxxxo.',
        '.oxwwwwwwxo.',
        '.oxxxxxxsso.',
        'oyxxxxxxstso',
        'oxwwwwwwrsso',
        '.ooooooooro.',
    ],
    # candle clock: a tall candle notched in hours
    'candle_clock': [
        '..F..',
        '.fFf.',
        '..e..',
        '..o..',
        '.oyxo',
        '.oyxo',
        '.ovvo',
        '.oyxo',
        '.oyxo',
        '.ovvo',
        '.oyxo',
        'ohhgo',
        'ooooo',
    ],
    # stack of tarnished coins
    'coin_stack': [
        '.ooooo.',
        'oHHhhgo',
        'ohhhggo',
        'oHHhhgo',
        'ohhhggo',
        'oHHhhgo',
        'ohhhggo',
        '.ooooo.',
    ],
    # a worn gargoyle head on a corbel (stone)
    'gargoyle': [
        '..o...o..',
        '.oqo.oqo.',
        '.oqqqqpo.',
        'oqOqqOpno',
        'oqqqpppno',
        '.oqoppno.',
        '.ooypyno.',
        '..onnnno.',
        '.ooooooo.',
        'opppppnno',
        'ooooooooo',
    ],
}


def motif_size(name):
    return P.sprite_size(MOTIFS[name])


def draw_motif(img, name, x, y, flip_x=False):
    """Draw motif ``name`` with its top-left at (x, y). Returns (w, h)."""
    rows = MOTIFS[name]
    P.sprite(img, x, y, rows, flip_x=flip_x)
    return P.sprite_size(rows)
