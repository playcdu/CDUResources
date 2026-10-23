"""Faithful pixel lettering: two original hand-authored faces.

PLAIN  - the label face, made to sit comfortably next to the game's own
         chat/GUI text without reproducing it. Cap height 7, x-height 5,
         descender 2, capitals and lowercase mostly 5 px wide, 1 px tracking,
         3 px space glyph (5 px of air between words). Its own traits, chosen
         so it is visibly not the vanilla font: a pointed A; true mid-height
         crossbars and bowl junctions (row 3 of 7) on B E F H P R; open,
         flat-ended C G S 3 5 and c s; a rounded D; a slashed 0; a
         single-storey a with a stem; a footed l; a flat-topped 1 with a
         full base.
TINY   - the compact capitals for tight two-line labels and stack counts.
         Cap height 5, uppercase and digits only, mostly 3 px wide.

Coordinates: ``draw_text(img, x, y, ...)`` puts the TOP of the cap height at
``y``; the baseline is ``y + cap_height - 1``. Lowercase x-height rows are
``y + 2 .. y + 6`` and descenders ``y + 7 .. y + 8`` (PLAIN only). Every glyph
is drawn by hand in this file ('#' ink, '.' empty). Nothing is traced from
another font: not from Minecraft's font (no game asset was opened while
drawing these), not from the cozy HEARTH / SPRIG or Soulrend GRAVEN / RUNE
faces, not from the old generated alphabets in tools/*.py.

Other themes' face names are accepted as aliases ('hearth' and 'graven' ->
'plain', 'sprig' and 'rune' -> 'tiny') so code ported from a cozy or Soulrend
painter, and the theme-aware preview tool, keep working.

Licence: glyph designs CC0-1.0, code MIT.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

if __name__ == 'lettering':                 # imported by its plain name from tools/faithful
    # one module object per process (see palette.py)
    if 'faithful.lettering' in _sys.modules:
        _sys.modules[__name__] = _sys.modules['faithful.lettering']
    else:
        _sys.modules['faithful.lettering'] = _sys.modules[__name__]
_TOOLS = _Path(__file__).resolve().parents[1]
if str(_TOOLS) not in _sys.path:
    _sys.path.append(str(_TOOLS))

from faithful.palette import rgba  # noqa: E402

# ---------------------------------------------------------------------------
# PLAIN capitals: cap height 7. Crossbars and bowl junctions on row 3.
# ---------------------------------------------------------------------------
_PLAIN_UPPER = {
    'A': ['..#..', '.#.#.', '#...#', '#...#', '#####', '#...#', '#...#'],
    'B': ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
    'C': ['.####', '#....', '#....', '#....', '#....', '#....', '.####'],
    'D': ['###..', '#..#.', '#...#', '#...#', '#...#', '#..#.', '###..'],
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
    'F': ['#####', '#....', '#....', '####.', '#....', '#....', '#....'],
    'G': ['.####', '#....', '#....', '#..##', '#...#', '#...#', '.###.'],
    'H': ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'J': ['..###', '...#.', '...#.', '...#.', '...#.', '#..#.', '.##..'],
    'K': ['#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
    'N': ['#...#', '##..#', '##..#', '#.#.#', '#..##', '#..##', '#...#'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'P': ['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'],
    'Q': ['.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'],
    'R': ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
    'S': ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'V': ['#...#', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
    'W': ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '#.#.#', '.#.#.'],
    'X': ['#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'],
    'Y': ['#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'],
    'Z': ['#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'],
}
_PLAIN_DIGITS = {
    '0': ['.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'],
    '1': ['###..', '..#..', '..#..', '..#..', '..#..', '..#..', '#####'],
    '2': ['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'],
    '3': ['####.', '....#', '....#', '.###.', '....#', '....#', '####.'],
    '4': ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'],
    '5': ['#####', '#....', '#....', '####.', '....#', '....#', '####.'],
    '6': ['.###.', '#....', '#....', '####.', '#...#', '#...#', '.###.'],
    '7': ['#####', '....#', '...#.', '..#..', '..#..', '..#..', '..#..'],
    '8': ['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'],
    '9': ['.###.', '#...#', '#...#', '.####', '....#', '....#', '.###.'],
}
_PLAIN_PUNCT = {
    ' ': ['...', '...', '...', '...', '...', '...', '...'],
    '+': ['.....', '.....', '..#..', '..#..', '#####', '..#..', '..#..'],
    '-': ['....', '....', '....', '####', '....', '....', '....'],
    '=': ['....', '....', '####', '....', '####', '....', '....'],
    '$': ['..#..', '.####', '#.#..', '.###.', '..#.#', '####.', '..#..'],
    '.': ['.', '.', '.', '.', '.', '.', '#'],
    ',': ['..', '..', '..', '..', '..', '.#', '#.'],
    ':': ['.', '.', '#', '.', '.', '.', '#'],
    ';': ['..', '..', '.#', '..', '..', '.#', '#.'],
    '!': ['#', '#', '#', '#', '#', '.', '#'],
    '?': ['.###.', '#...#', '....#', '..##.', '..#..', '.....', '..#..'],
    '/': ['....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....'],
    "'": ['#', '#', '.', '.', '.', '.', '.'],
    '"': ['#.#', '#.#', '...', '...', '...', '...', '...'],
    '(': ['..#', '.#.', '#..', '#..', '#..', '.#.', '..#'],
    ')': ['#..', '.#.', '..#', '..#', '..#', '.#.', '#..'],
    '[': ['###', '#..', '#..', '#..', '#..', '#..', '###'],
    ']': ['###', '..#', '..#', '..#', '..#', '..#', '###'],
    '<': ['....', '...#', '..#.', '.#..', '..#.', '...#', '....'],
    '>': ['....', '#...', '.#..', '..#.', '.#..', '#...', '....'],
    '%': ['#...#', '#..#.', '...#.', '..#..', '.#...', '.#..#', '#...#'],
    '&': ['.##..', '#..#.', '.##..', '.#..#', '#.##.', '#..#.', '.##.#'],
    '#': ['.....', '.#.#.', '#####', '.#.#.', '#####', '.#.#.', '.....'],
    '*': ['.....', '#.#.#', '.###.', '#####', '.###.', '#.#.#', '.....'],
    '_': ['.....', '.....', '.....', '.....', '.....', '.....', '#####'],
}
# Lowercase: 9 rows (rows 7-8 descenders); x-height rows 2-6.
_PLAIN_LOWER = {
    'a': ['.....', '.....', '.###.', '#...#', '#...#', '#..##', '.##.#', '.....', '.....'],
    'b': ['#....', '#....', '####.', '#...#', '#...#', '#...#', '####.', '.....', '.....'],
    'c': ['....', '....', '.###', '#...', '#...', '#...', '.###', '....', '....'],
    'd': ['....#', '....#', '.####', '#...#', '#...#', '#...#', '.####', '.....', '.....'],
    'e': ['.....', '.....', '.###.', '#...#', '#####', '#....', '.####', '.....', '.....'],
    'f': ['..##', '.#..', '####', '.#..', '.#..', '.#..', '.#..', '....', '....'],
    'g': ['.....', '.....', '.####', '#...#', '#...#', '#...#', '.####', '....#', '####.'],
    'h': ['#....', '#....', '####.', '#...#', '#...#', '#...#', '#...#', '.....', '.....'],
    'i': ['#', '.', '#', '#', '#', '#', '#', '.', '.'],
    'j': ['..#', '...', '..#', '..#', '..#', '..#', '..#', '..#', '##.'],
    'k': ['#...', '#...', '#..#', '#.#.', '##..', '#.#.', '#..#', '....', '....'],
    'l': ['#.', '#.', '#.', '#.', '#.', '#.', '.#', '..', '..'],
    'm': ['.....', '.....', '####.', '#.#.#', '#.#.#', '#.#.#', '#.#.#', '.....', '.....'],
    'n': ['.....', '.....', '####.', '#...#', '#...#', '#...#', '#...#', '.....', '.....'],
    'o': ['.....', '.....', '.###.', '#...#', '#...#', '#...#', '.###.', '.....', '.....'],
    'p': ['.....', '.....', '####.', '#...#', '#...#', '#...#', '####.', '#....', '#....'],
    'q': ['.....', '.....', '.####', '#...#', '#...#', '#...#', '.####', '....#', '....#'],
    'r': ['....', '....', '#.##', '##..', '#...', '#...', '#...', '....', '....'],
    's': ['....', '....', '.###', '#...', '.##.', '...#', '###.', '....', '....'],
    't': ['.#.', '.#.', '###', '.#.', '.#.', '.#.', '..#', '...', '...'],
    'u': ['.....', '.....', '#...#', '#...#', '#...#', '#...#', '.####', '.....', '.....'],
    'v': ['.....', '.....', '#...#', '#...#', '#...#', '.#.#.', '..#..', '.....', '.....'],
    'w': ['.....', '.....', '#...#', '#...#', '#.#.#', '#.#.#', '.#.#.', '.....', '.....'],
    'x': ['.....', '.....', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '.....', '.....'],
    'y': ['.....', '.....', '#...#', '#...#', '#...#', '#...#', '.####', '....#', '####.'],
    'z': ['.....', '.....', '#####', '...#.', '..#..', '.#...', '#####', '.....', '.....'],
}

# ---------------------------------------------------------------------------
# TINY: cap height 5, compact capitals (uppercase, digits, basic marks).
# Lowercase input is drawn as capitals.
# ---------------------------------------------------------------------------
_TINY = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'],
    'B': ['##.', '#.#', '###', '#.#', '##.'],
    'C': ['.##', '#..', '#..', '#..', '.##'],
    'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'E': ['###', '#..', '##.', '#..', '###'],
    'F': ['###', '#..', '##.', '#..', '#..'],
    'G': ['.##', '#..', '#.#', '#.#', '.##'],
    'H': ['#.#', '#.#', '###', '#.#', '#.#'],
    'I': ['###', '.#.', '.#.', '.#.', '###'],
    'J': ['..#', '..#', '..#', '#.#', '.#.'],
    'K': ['#.#', '#.#', '##.', '#.#', '#.#'],
    'L': ['#..', '#..', '#..', '#..', '###'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'],
    'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'O': ['.#.', '#.#', '#.#', '#.#', '.#.'],
    'P': ['##.', '#.#', '##.', '#..', '#..'],
    'Q': ['.#.', '#.#', '#.#', '##.', '.##'],
    'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['.##', '#..', '.#.', '..#', '##.'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '.##'],
    'V': ['#.#', '#.#', '#.#', '#.#', '.#.'],
    'W': ['#...#', '#...#', '#.#.#', '#.#.#', '.#.#.'],
    'X': ['#.#', '#.#', '.#.', '#.#', '#.#'],
    'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'],
    'Z': ['###', '..#', '.#.', '#..', '###'],
    '0': ['.#.', '#.#', '###', '#.#', '.#.'],
    '1': ['##', '.#', '.#', '.#', '.#'],
    '2': ['##.', '..#', '.#.', '#..', '###'],
    '3': ['##.', '..#', '.#.', '..#', '##.'],
    '4': ['#.#', '#.#', '###', '..#', '..#'],
    '5': ['###', '#..', '##.', '..#', '##.'],
    '6': ['.##', '#..', '##.', '#.#', '.#.'],
    '7': ['###', '..#', '.#.', '.#.', '.#.'],
    '8': ['.#.', '#.#', '.#.', '#.#', '.#.'],
    '9': ['.#.', '#.#', '.##', '..#', '##.'],
    ' ': ['.', '.', '.', '.', '.'],
    '+': ['...', '.#.', '###', '.#.', '...'],
    '-': ['...', '...', '###', '...', '...'],
    '=': ['...', '###', '...', '###', '...'],
    '$': ['.##', '##.', '.#.', '.##', '##.'],
    '.': ['.', '.', '.', '.', '#'],
    ',': ['..', '..', '..', '.#', '#.'],
    ':': ['.', '#', '.', '#', '.'],
    '!': ['#', '#', '#', '.', '#'],
    '?': ['##.', '..#', '.#.', '...', '.#.'],
    '/': ['..#', '..#', '.#.', '#..', '#..'],
    "'": ['#', '#', '.', '.', '.'],
    '&': ['.#.', '#.#', '.#.', '#.#', '.##'],
    '<': ['..#', '.#.', '#..', '.#.', '..#'],
    '>': ['#..', '.#.', '..#', '.#.', '#..'],
    '(': ['.#', '#.', '#.', '#.', '.#'],
    ')': ['#.', '.#', '.#', '.#', '#.'],
    '%': ['#.#', '..#', '.#.', '#..', '#.#'],
    '#': ['#.#', '###', '#.#', '###', '#.#'],
    '*': ['#.#', '.#.', '#.#', '...', '...'],
}


class Face:
    """A bitmap face. ``glyphs`` maps a character to rows of '#'/'.'."""

    def __init__(self, name, glyphs, cap_height, x_height, descender, tracking, kerning, upper_only=False):
        self.name = name
        self.glyphs = glyphs
        self.cap_height = cap_height
        self.x_height = x_height
        self.descender = descender
        self.tracking = tracking
        self.kerning = kerning
        self.upper_only = upper_only
        for ch, rows in glyphs.items():
            if len({len(r) for r in rows}) != 1:
                raise ValueError(f'{name}: ragged glyph {ch!r}')
            if len(rows) not in (cap_height, cap_height + descender):
                raise ValueError(f'{name}: glyph {ch!r} has {len(rows)} rows')
        self.max_width = max(len(rows[0]) for rows in glyphs.values())

    @property
    def line_height(self):
        return self.cap_height + self.descender + 1

    def norm(self, s):
        s = str(s)
        if self.upper_only:
            s = s.upper()
        out = []
        for ch in s:
            if ch in self.glyphs:
                out.append(ch)
            elif ch.upper() in self.glyphs:
                out.append(ch.upper())
            else:
                out.append('?')
        return ''.join(out)

    def glyph(self, ch):
        return self.glyphs[ch]

    def width(self, ch):
        return len(self.glyphs[ch][0])


PLAIN = Face('plain', {**_PLAIN_UPPER, **_PLAIN_DIGITS, **_PLAIN_PUNCT, **_PLAIN_LOWER},
             cap_height=7, x_height=5, descender=2, tracking=1,
             # Every pair is audited by ``audit_kerning`` (and selftest.py): with
             # the -1 kern the two glyphs still have no 8-neighbour contact, so
             # at least one clear column separates them on every row.
             kerning={('L', 'T'): -1, ('L', 'Y'): -1, ('L', 'V'): -1, ('T', 'A'): -1, ('A', 'T'): -1,
                      ('T', '.'): -1, ('Y', '.'): -1, ('P', '.'): -1, ('F', '.'): -1, ('T', ','): -1,
                      ('r', '.'): -1, ('r', ','): -1, ('L', "'"): -1, ('F', 'A'): -1})
# PA was tried and removed: the bowl of P meets the shoulder of A on row 2.
TINY = Face('tiny', _TINY, cap_height=5, x_height=5, descender=0, tracking=1,
            kerning={('L', 'T'): -1, ('T', '.'): -1}, upper_only=True)
FACES = {'plain': PLAIN, 'tiny': TINY}
FACE_ALIASES = {'hearth': 'plain', 'graven': 'plain', 'sprig': 'tiny', 'rune': 'tiny'}
LABEL_FACE = 'plain'
SMALL_FACE = 'tiny'


def _face(face):
    if isinstance(face, Face):
        return face
    return FACES[FACE_ALIASES.get(face, face)]


def _advances(s, face):
    """Yield (char, x offset) pairs for a normalised string."""
    x = 0
    prev = None
    for ch in s:
        if prev is not None:
            x += face.tracking + face.kerning.get((prev, ch), 0)
        yield ch, x
        x += face.width(ch)
        prev = ch


def text_width(s, face='plain'):
    """Ink width in pixels of ``s`` (no outline / shadow). Empty string is 0."""
    f = _face(face)
    s = f.norm(s)
    if not s:
        return 0
    last = 0
    for ch, x in _advances(s, f):
        last = x + f.width(ch)
    return last


def text_height(s, face='plain'):
    """Rows the string occupies from the cap top (includes descenders if used)."""
    f = _face(face)
    s = f.norm(s)
    if not s:
        return 0
    descends = any('#' in ''.join(f.glyph(ch)[f.cap_height:]) for ch in s)
    return f.cap_height + (f.descender if descends else 0)


def fits(s, max_width, face='plain'):
    return text_width(s, face) <= max_width


def _pixels(s, face):
    """Glyph pixels of ``s`` relative to its cap top-left."""
    f = _face(face)
    s = f.norm(s)
    out = []
    for ch, ox in _advances(s, f):
        for yy, row in enumerate(f.glyph(ch)):
            for xx, c in enumerate(row):
                if c == '#':
                    out.append((ox + xx, yy))
    return out


pixels = _pixels


def _put(img, x, y, colour):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), colour)


def draw_text(img, x, y, s, color='ink_1', shadow=None, outline=None, face='plain', mask=None):
    """Draw ``s`` with its cap top at (x, y). Returns the ink width.

    color / shadow / outline accept Faithful palette names ('grey_7') or
    RGB(A) tuples. ``shadow`` draws a 1 px copy offset (+1, +1) beneath the
    letters: the vanilla-style button label is white with an ink_1 shadow.
    ``outline`` draws a 1 px 4-neighbour halo first. ``mask`` (optional
    callable (x, y) -> bool) skips pixels, e.g. masked clearances.
    """
    pts = _pixels(s, face)
    colour = rgba(color)
    keep = (lambda px, py: True) if mask is None else (lambda px, py: not mask(px, py))
    ink = {(x + px, y + py) for px, py in pts}
    if outline is not None:
        oc = rgba(outline)
        halo = set()
        for px, py in ink:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                halo.add((px + dx, py + dy))
        if shadow is not None:
            for px, py in ink:
                halo.add((px + 1, py + 1)); halo.add((px + 2, py + 1)); halo.add((px + 1, py + 2))
        for p in sorted(halo - ink):
            if keep(*p):
                _put(img, p[0], p[1], oc)
    if shadow is not None:
        sc = rgba(shadow)
        for px, py in sorted(ink):
            q = (px + 1, py + 1)
            if q not in ink and keep(*q):
                _put(img, q[0], q[1], sc)
    for p in sorted(ink):
        if keep(*p):
            _put(img, p[0], p[1], colour)
    return text_width(s, face)


def draw_text_centered(img, cx, y, s, color='ink_1', shadow=None, outline=None, face='plain', mask=None):
    """Centre ``s`` on column ``cx`` (left-biased when the width is even). Returns left x."""
    w = text_width(s, face)
    x = cx - w // 2
    draw_text(img, x, y, s, color, shadow, outline, face, mask)
    return x


def draw_lines_centered(img, box, lines, color='ink_1', shadow=None, outline=None, face='plain', gap=2):
    """Centre several lines inside box (x, y, w, h). Returns the top y used."""
    f = _face(face)
    x, y, w, h = box
    total = len(lines) * f.cap_height + (len(lines) - 1) * gap
    top = y + (h - total) // 2
    for i, line in enumerate(lines):
        draw_text_centered(img, x + w // 2, top + i * (f.cap_height + gap), line, color, shadow, outline, face)
    return top


def fit_face(s, max_width):
    """'plain' when it fits, else 'tiny', else None."""
    if text_width(s, 'plain') <= max_width:
        return 'plain'
    if text_width(s, 'tiny') <= max_width:
        return 'tiny'
    return None


def charset(face='plain'):
    return ''.join(_face(face).glyphs)


def audit_kerning(face='plain'):
    """Every kerning pair of ``face`` rendered at 1x: returns the pairs whose
    two glyphs touch (any 8-neighbour contact, so no clear column on some row
    or a corner contact). An empty list means the kerning table is clean."""
    f = _face(face)
    bad = []
    for (a, b), k in sorted(f.kerning.items()):
        if a not in f.glyphs or b not in f.glyphs:
            bad.append((a, b, 'missing glyph'))
            continue
        ax = {(x, y) for y, row in enumerate(f.glyph(a)) for x, c in enumerate(row) if c == '#'}
        off = f.width(a) + f.tracking + k
        bx = {(x + off, y) for y, row in enumerate(f.glyph(b)) for x, c in enumerate(row) if c == '#'}
        if any(max(abs(p[0] - q[0]), abs(p[1] - q[1])) <= 1 for p in ax for q in bx):
            bad.append((a, b, 'touch'))
    return bad


# ---------------------------------------------------------------------------
# Specimen
# ---------------------------------------------------------------------------

FIT_CHECKS = [('LISTINGS', 50), ('DISABLE LISTING', 104), ('PURCHASE', 50), ('12 DAYS', 68)]


def specimen(scale=4):
    """Render the type specimen (both faces, fit checks, kerning, colour
    pairings on the theme's real surfaces) as an image."""
    from PIL import Image, ImageDraw
    from faithful.palette import GOLD, GREEN, GREY, INK, RED
    W = 330
    img = Image.new('RGBA', (W, 320), GREY[6] + (255,))
    d = ImageDraw.Draw(img)
    y = 4
    draw_text(img, 4, y, 'PLAIN  cap 7 / x 5 / desc 2 / track 1', INK[1]); y += 12
    for row in ('ABCDEFGHIJKLM', 'NOPQRSTUVWXYZ', '0123456789 +-=$.,:;!?/\'"()[]<>%&#*_',
                'abcdefghijklm nopqrstuvwxyz'):
        draw_text(img, 4, y, row, INK[1]); y += 12
    draw_text(img, 4, y, 'Sell Price  Privacy  Opt 2  Tier 1  Quantity', INK[1]); y += 14
    draw_text(img, 4, y, 'TINY  cap 5 / track 1  (compact capitals)', INK[1], face='tiny'); y += 9
    for row in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', '0123456789 +-=$.,:!?/\'&<>()%#*'):
        draw_text(img, 4, y, row, INK[1], face='tiny'); y += 8
    y += 4
    draw_text(img, 4, y, 'Fit checks (width / limit):', INK[1]); y += 11
    for s_, lim in FIT_CHECKS:
        w = text_width(s_)
        d.rectangle((4, y - 2, 4 + lim + 1, y + 8), outline=GREY[1] + (255,))
        draw_text(img, 6, y, s_, INK[1])
        draw_text(img, 4 + lim + 8, y + 1, f'{w} / {lim} {"OK" if w <= lim else "OVER"}', GREY[1], face='tiny')
        y += 12
    y += 2
    draw_text(img, 4, y, 'Kerning LT TA AT Y. ->', INK[1])
    x = 4 + text_width('Kerning LT TA AT Y. ->') + 4
    draw_text(img, x, y, 'SALT TAT VOLTA LY.', INK[1]); y += 13
    # colour pairings on the theme surfaces: stone buttons, info plate, danger, selected
    for (bx, bw, face, bevel, dark, text, label) in (
            (4, 70, GREY[3], GOLD[2], GREY[1], 'grey_7', 'PURCHASE'),
            (80, 60, GREY[3], GREY[5], GREY[1], 'grey_7', 'RETURN'),
            (146, 52, RED[1], RED[2], RED[0], 'grey_7', 'CLOSE'),
            (204, 60, GREEN[1], GREY[7], GREEN[0], 'grey_7', 'READY')):
        d.rectangle((bx, y, bx + bw - 1, y + 17), fill=INK[0] + (255,))
        d.rectangle((bx + 1, y + 1, bx + bw - 2, y + 16), fill=dark + (255,))
        d.rectangle((bx + 1, y + 1, bx + bw - 3, y + 15), fill=bevel + (255,))
        d.rectangle((bx + 2, y + 2, bx + bw - 3, y + 15), fill=face + (255,))
        draw_text_centered(img, bx + bw // 2, y + 5, label, text, shadow='ink_1')
    y += 22
    d.rectangle((4, y, 73, y + 17), fill=GREY[1] + (255,))
    d.rectangle((5, y + 1, 73, y + 17), fill=GREY[7] + (255,))
    d.rectangle((5, y + 1, 72, y + 16), fill=GREY[5] + (255,))
    draw_text_centered(img, 39, y + 5, 'BALANCE', 'ink_1')
    d.rectangle((80, y, 139, y + 17), fill=INK[0] + (255,))
    d.rectangle((81, y + 1, 138, y + 16), fill=GREY[0] + (255,))
    draw_text_centered(img, 110, y + 5, 'LOCKED', 'grey_5', shadow='ink_1')
    draw_text(img, 148, y + 1, 'Info plate: dark text,', INK[1], face='tiny')
    draw_text(img, 148, y + 8, 'disabled: mid grey on flat dark grey', INK[1], face='tiny')
    y += 24
    img = img.crop((0, 0, W, y + 2))
    return img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)


if __name__ == '__main__':
    out = _Path(__file__).resolve().parents[2] / 'evidence' / 'faithful' / 'typeface-specimen.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    specimen().save(out)
    for s_, lim in FIT_CHECKS:
        print(f'{s_!r}: {text_width(s_)} px (limit {lim})')
    print('kerning audit PLAIN:', audit_kerning('plain') or 'clean', '| TINY:', audit_kerning('tiny') or 'clean')
    print('WROTE', out)
