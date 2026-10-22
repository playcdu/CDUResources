"""Soulrend pixel lettering: two original hand-authored faces.

GRAVEN  - the label face: a thin medieval serif. Cap height 7, x-height 5,
          descender 2, variable width (1-5 px), 1 px tracking, 2 px space glyph
          (4 px of air between words). Traits: inward foot serifs on stems
          (A H K M N R), drooping T arms, spurred E/F/L, an uncial C and G,
          chamfered D, flag serifs on lowercase ascenders and entry strokes.
RUNE    - the compact carved capitals for frame headings, side banners, tight
          two-line labels and tiny captions. Cap height 5, uppercase and digits
          only, mostly 3 px wide with angular, chisel-cut bowls.

Coordinates: ``draw_text(img, x, y, ...)`` puts the TOP of the cap height at
``y``; the baseline is ``y + cap_height - 1``. Lowercase x-height rows are
``y + 2 .. y + 6`` and descenders ``y + 7 .. y + 8`` (GRAVEN only). Every glyph
is drawn by hand in this file ('#' ink, '.' empty). Nothing is traced from
another font: not from the modpack's own fonts, not from the cozy HEARTH /
SPRIG faces, not from the old generated alphabets in tools/*.py.

The cozy face names are accepted as aliases ('hearth' -> 'graven',
'sprig' -> 'rune') so code ported from a cozy painter keeps working.

Licence: glyph designs CC0-1.0, code MIT.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

if __name__ == 'lettering':
    _sys.modules.setdefault('soulrend.lettering', _sys.modules[__name__])
_TOOLS = _Path(__file__).resolve().parents[1]
if str(_TOOLS) not in _sys.path:
    _sys.path.append(str(_TOOLS))

from soulrend.palette import rgba  # noqa: E402

# ---------------------------------------------------------------------------
# GRAVEN capitals: cap height 7.
# ---------------------------------------------------------------------------
_GRAVEN_UPPER = {
    'A': ['..#..', '..#..', '.#.#.', '.#.#.', '#####', '#...#', '##.##'],
    'B': ['####.', '.#..#', '.#.#.', '.###.', '.#..#', '.#..#', '####.'],
    'C': ['..###', '.#...', '#....', '#....', '#....', '.#...', '..###'],
    'D': ['###..', '.#.#.', '.#..#', '.#..#', '.#..#', '.#.#.', '###..'],
    'E': ['#####', '.#..#', '.#...', '.###.', '.#...', '.#..#', '#####'],
    'F': ['#####', '.#..#', '.#...', '.###.', '.#...', '.#...', '###..'],
    'G': ['..###', '.#...', '#....', '#..##', '#...#', '.#..#', '..##.'],
    'H': ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '##.##'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'J': ['.###', '..#.', '..#.', '..#.', '..#.', '#.#.', '.#..'],
    'K': ['#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '##..#'],
    'L': ['###..', '.#...', '.#...', '.#...', '.#...', '.#..#', '#####'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '##.##'],
    'N': ['#...#', '##..#', '#.#.#', '#.#.#', '#..##', '#...#', '##..#'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'P': ['####.', '.#..#', '.#..#', '.###.', '.#...', '.#...', '###..'],
    'Q': ['.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'],
    'R': ['####.', '.#..#', '.#..#', '.###.', '.#.#.', '.#..#', '##..#'],
    'S': ['.###', '#..#', '#...', '.##.', '...#', '#..#', '###.'],
    'T': ['#####', '#.#.#', '..#..', '..#..', '..#..', '..#..', '.###.'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'V': ['#...#', '#...#', '#...#', '.#.#.', '.#.#.', '.#.#.', '..#..'],
    'W': ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'],
    'X': ['#...#', '.#.#.', '.#.#.', '..#..', '.#.#.', '.#.#.', '#...#'],
    'Y': ['#...#', '.#.#.', '.#.#.', '..#..', '..#..', '..#..', '.###.'],
    'Z': ['#####', '#..#.', '...#.', '..#..', '.#...', '.#..#', '#####'],
}
_GRAVEN_DIGITS = {
    '0': ['.##.', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    '1': ['..#.', '.##.', '#.#.', '..#.', '..#.', '..#.', '.###'],
    '2': ['.##.', '#..#', '...#', '..#.', '.#..', '#..#', '####'],
    '3': ['####', '...#', '..#.', '.##.', '...#', '#..#', '.##.'],
    '4': ['...#', '..##', '.#.#', '#..#', '####', '...#', '..##'],
    '5': ['####', '#...', '#...', '###.', '...#', '#..#', '.##.'],
    '6': ['..#.', '.#..', '#...', '###.', '#..#', '#..#', '.##.'],
    '7': ['####', '#..#', '...#', '..#.', '..#.', '.#..', '.#..'],
    '8': ['.##.', '#..#', '#.#.', '.##.', '#..#', '#..#', '.##.'],
    '9': ['.##.', '#..#', '#..#', '.###', '...#', '..#.', '.#..'],
}
_GRAVEN_PUNCT = {
    ' ': ['..', '..', '..', '..', '..', '..', '..'],
    '+': ['...', '...', '.#.', '###', '.#.', '...', '...'],
    '-': ['...', '...', '...', '###', '...', '...', '...'],
    '=': ['...', '...', '###', '...', '###', '...', '...'],
    '$': ['..#..', '.####', '#.#..', '.###.', '..#.#', '####.', '..#..'],
    '.': ['.', '.', '.', '.', '.', '.', '#'],
    ',': ['..', '..', '..', '..', '..', '.#', '#.'],
    ':': ['.', '.', '#', '.', '.', '#', '.'],
    ';': ['..', '..', '.#', '..', '..', '.#', '#.'],
    '!': ['#', '#', '#', '#', '.', '.', '#'],
    '?': ['.##.', '#..#', '...#', '..#.', '..#.', '....', '..#.'],
    '/': ['...#', '..#.', '..#.', '.#..', '.#..', '#...', '#...'],
    "'": ['#', '#', '.', '.', '.', '.', '.'],
    '"': ['#.#', '#.#', '...', '...', '...', '...', '...'],
    '(': ['..#', '.#.', '#..', '#..', '#..', '.#.', '..#'],
    ')': ['#..', '.#.', '..#', '..#', '..#', '.#.', '#..'],
    '[': ['##', '#.', '#.', '#.', '#.', '#.', '##'],
    ']': ['##', '.#', '.#', '.#', '.#', '.#', '##'],
    '<': ['....', '...#', '..#.', '.#..', '..#.', '...#', '....'],
    '>': ['....', '#...', '.#..', '..#.', '.#..', '#...', '....'],
    '%': ['##..#', '##.#.', '...#.', '..#..', '.#...', '.#.##', '#..##'],
    '&': ['.#...', '#.#..', '.#...', '#.#.#', '#..#.', '#..#.', '.##.#'],
    '#': ['.....', '.#.#.', '#####', '.#.#.', '#####', '.#.#.', '.....'],
    '*': ['.#.', '###', '.#.', '#.#', '...', '...', '...'],
    '_': ['....', '....', '....', '....', '....', '....', '####'],
}
# Lowercase: 9 rows (rows 7-8 descenders); x-height rows 2-6. Ascenders carry a
# left flag serif, x-height stems an entry stroke, several letters a foot.
_GRAVEN_LOWER = {
    'a': ['....', '....', '.##.', '#..#', '#..#', '#.##', '.#.#', '....', '....'],
    'b': ['##..', '.#..', '.##.', '.#.#', '.#.#', '.#.#', '.##.', '....', '....'],
    'c': ['...', '...', '.##', '#..', '#..', '#..', '.##', '...', '...'],
    'd': ['..##', '...#', '.###', '#..#', '#..#', '#..#', '.##.', '....', '....'],
    'e': ['...', '...', '.#.', '#.#', '###', '#..', '.##', '...', '...'],
    'f': ['.##', '.#.', '###', '.#.', '.#.', '.#.', '##.', '...', '...'],
    'g': ['....', '....', '.###', '#..#', '#..#', '.###', '...#', '#..#', '.##.'],
    'h': ['##..', '.#..', '.##.', '.#.#', '.#.#', '.#.#', '##.#', '....', '....'],
    'i': ['.#', '..', '##', '.#', '.#', '.#', '.#', '..', '..'],
    'j': ['..#', '...', '.##', '..#', '..#', '..#', '..#', '..#', '##.'],
    'k': ['##..', '.#..', '.#.#', '.#.#', '.##.', '.#.#', '##.#', '....', '....'],
    'l': ['##.', '.#.', '.#.', '.#.', '.#.', '.#.', '..#', '...', '...'],
    'm': ['.....', '.....', '####.', '#.#.#', '#.#.#', '#.#.#', '#.#.#', '.....', '.....'],
    'n': ['....', '....', '###.', '.#.#', '.#.#', '.#.#', '##.#', '....', '....'],
    'o': ['....', '....', '.##.', '#..#', '#..#', '#..#', '.##.', '....', '....'],
    'p': ['....', '....', '###.', '.#.#', '.#.#', '.##.', '.#..', '.#..', '##..'],
    'q': ['....', '....', '.###', '#..#', '#..#', '.###', '...#', '...#', '..##'],
    'r': ['....', '....', '##.#', '.##.', '.#..', '.#..', '##..', '....', '....'],
    's': ['...', '...', '.##', '#..', '.#.', '..#', '##.', '...', '...'],
    't': ['...', '.#.', '###', '.#.', '.#.', '.#.', '..#', '...', '...'],
    'u': ['....', '....', '#..#', '#..#', '#..#', '#.##', '.#.#', '....', '....'],
    'v': ['...', '...', '#.#', '#.#', '#.#', '#.#', '.#.', '...', '...'],
    'w': ['.....', '.....', '#.#.#', '#.#.#', '#.#.#', '#.#.#', '.#.#.', '.....', '.....'],
    'x': ['...', '...', '#.#', '#.#', '.#.', '#.#', '#.#', '...', '...'],
    'y': ['...', '...', '#.#', '#.#', '#.#', '.##', '..#', '..#', '##.'],
    'z': ['...', '...', '###', '..#', '.#.', '#..', '###', '...', '...'],
}

# ---------------------------------------------------------------------------
# RUNE: cap height 5, carved capitals. Chisel-cut (chamfered) bowls, a pointed
# A, an angular S. Uppercase, digits and basic marks; lowercase input is drawn
# as capitals.
# ---------------------------------------------------------------------------
_RUNE = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'],
    'B': ['##.', '#.#', '##.', '#.#', '###'],
    'C': ['.##', '#..', '#..', '#..', '.##'],
    'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'E': ['###', '#..', '###', '#..', '###'],
    'F': ['###', '#..', '###', '#..', '#..'],
    'G': ['.##', '#..', '#.#', '#.#', '.##'],
    'H': ['#.#', '#.#', '###', '#.#', '#.#'],
    'I': ['###', '.#.', '.#.', '.#.', '###'],
    'J': ['###', '..#', '..#', '#.#', '.#.'],
    'K': ['#.#', '#.#', '##.', '#.#', '#.#'],
    'L': ['#..', '#..', '#..', '#..', '###'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'],
    'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'O': ['.#.', '#.#', '#.#', '#.#', '.#.'],
    'P': ['##.', '#.#', '##.', '#..', '#..'],
    'Q': ['.#.', '#.#', '#.#', '#.#', '.##'],
    'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['.##', '#..', '.#.', '..#', '##.'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '###'],
    'V': ['#.#', '#.#', '#.#', '#.#', '.#.'],
    'W': ['#...#', '#...#', '#.#.#', '##.##', '#...#'],
    'X': ['#.#', '#.#', '.#.', '#.#', '#.#'],
    'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'],
    'Z': ['###', '..#', '.#.', '#..', '###'],
    '0': ['###', '#.#', '#.#', '#.#', '###'],
    '1': ['.#', '##', '.#', '.#', '.#'],
    '2': ['##.', '..#', '.#.', '#..', '###'],
    '3': ['###', '..#', '.##', '..#', '###'],
    '4': ['#.#', '#.#', '###', '..#', '..#'],
    '5': ['###', '#..', '##.', '..#', '##.'],
    '6': ['.##', '#..', '###', '#.#', '###'],
    '7': ['###', '..#', '..#', '.#.', '.#.'],
    '8': ['###', '#.#', '.#.', '#.#', '###'],
    '9': ['###', '#.#', '###', '..#', '##.'],
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

    def __init__(self, name, glyphs, cap_height, x_height, descender, tracking, kerning, upper_only=False,
                 space_note=''):
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


GRAVEN = Face('graven', {**_GRAVEN_UPPER, **_GRAVEN_DIGITS, **_GRAVEN_PUNCT, **_GRAVEN_LOWER},
              cap_height=7, x_height=5, descender=2, tracking=1,
              # Every pair keeps at least one clear column between the two glyphs on
              # every row and no edge or corner contact (audited at 1x; WA, AW, LW
              # merged into a 3 px blob and Tr touched diagonally, so they are out).
              kerning={('L', 'T'): -1, ('L', 'Y'): -1, ('L', 'V'): -1, ('T', 'A'): -1, ('A', 'T'): -1,
                       ('A', 'V'): -1, ('V', 'A'): -1, ('A', 'Y'): -1, ('Y', 'A'): -1, ('T', '.'): -1,
                       ('Y', '.'): -1, ('P', '.'): -1, ('F', '.'): -1, ('T', 'o'): -1, ('T', 'a'): -1,
                       ('T', 'e'): -1, ('r', '.'): -1, ('r', ','): -1, ('/', '/'): -1, ('P', 'A'): -1,
                       ('F', 'A'): -1})
RUNE = Face('rune', _RUNE, cap_height=5, x_height=5, descender=0, tracking=1,
            # same audit: YA / AY merged, TA / AT / LV touched diagonally
            kerning={('L', 'T'): -1, ('L', 'Y'): -1, ('T', '.'): -1},
            upper_only=True)
FACES = {'graven': GRAVEN, 'rune': RUNE}
FACE_ALIASES = {'hearth': 'graven', 'sprig': 'rune'}
LABEL_FACE = 'graven'
SMALL_FACE = 'rune'


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


def text_width(s, face='graven'):
    """Ink width in pixels of ``s`` (no outline / shadow). Empty string is 0."""
    f = _face(face)
    s = f.norm(s)
    if not s:
        return 0
    last = 0
    for ch, x in _advances(s, f):
        last = x + f.width(ch)
    return last


def text_height(s, face='graven'):
    """Rows the string occupies from the cap top (includes descenders if used)."""
    f = _face(face)
    s = f.norm(s)
    if not s:
        return 0
    descends = any('#' in ''.join(f.glyph(ch)[f.cap_height:]) for ch in s)
    return f.cap_height + (f.descender if descends else 0)


def fits(s, max_width, face='graven'):
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


def draw_text(img, x, y, s, color='ink_0', shadow=None, outline=None, face='graven', mask=None):
    """Draw ``s`` with its cap top at (x, y). Returns the ink width.

    color / shadow / outline accept Soulrend palette names ('gold_2') or RGB(A)
    tuples. ``shadow`` draws a 1 px copy offset (+1, +1) beneath the letters
    (deep bottom-right shadow; on iron use ink_0). ``outline`` draws a 1 px
    4-neighbour halo first so text reads on busy stone. ``mask`` (optional
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


def draw_text_centered(img, cx, y, s, color='ink_0', shadow=None, outline=None, face='graven', mask=None):
    """Centre ``s`` on column ``cx`` (left-biased when the width is even). Returns left x."""
    w = text_width(s, face)
    x = cx - w // 2
    draw_text(img, x, y, s, color, shadow, outline, face, mask)
    return x


def draw_lines_centered(img, box, lines, color='ink_0', shadow=None, outline=None, face='graven', gap=2):
    """Centre several lines inside box (x, y, w, h). Returns the top y used."""
    f = _face(face)
    x, y, w, h = box
    total = len(lines) * f.cap_height + (len(lines) - 1) * gap
    top = y + (h - total) // 2
    for i, line in enumerate(lines):
        draw_text_centered(img, x + w // 2, top + i * (f.cap_height + gap), line, color, shadow, outline, face)
    return top


def fit_face(s, max_width):
    """'graven' when it fits, else 'rune', else None."""
    if text_width(s, 'graven') <= max_width:
        return 'graven'
    if text_width(s, 'rune') <= max_width:
        return 'rune'
    return None


def charset(face='graven'):
    return ''.join(_face(face).glyphs)


# ---------------------------------------------------------------------------
# Specimen
# ---------------------------------------------------------------------------

FIT_CHECKS = [('LISTINGS', 50), ('DISABLE LISTING', 104), ('PURCHASE', 50), ('12 DAYS', 68)]


def specimen(scale=4):
    """Render the type specimen (both faces, fit checks, kerning, colour
    pairings on the theme's real surfaces) as an image."""
    from PIL import Image, ImageDraw
    from soulrend.palette import BLOOD, EMBER, GOLD, INK, IRON, SOUL, STONE, UMBER, VELLUM
    W = 320
    img = Image.new('RGBA', (W, 300), VELLUM[2] + (255,))
    d = ImageDraw.Draw(img)
    y = 4
    draw_text(img, 4, y, 'GRAVEN  cap 7 / x 5 / desc 2 / track 1', BLOOD[1]); y += 12
    for row in ('ABCDEFGHIJKLM', 'NOPQRSTUVWXYZ', '0123456789 +-=$.,:;!?/\'"()[]<>%&#*_',
                'abcdefghijklm nopqrstuvwxyz'):
        draw_text(img, 4, y, row, INK[0]); y += 12
    draw_text(img, 4, y, 'Sell Price  Privacy  Opt 2  Tier 1  Quantity', INK[0]); y += 14
    draw_text(img, 4, y, 'RUNE  cap 5 / track 1  (carved capitals)', BLOOD[1], face='rune'); y += 9
    for row in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', '0123456789 +-=$.,:!?/\'&<>()%#*'):
        draw_text(img, 4, y, row, INK[0], face='rune'); y += 8
    y += 4
    draw_text(img, 4, y, 'Fit checks (width / limit):', BLOOD[1]); y += 11
    for s_, lim in FIT_CHECKS:
        w = text_width(s_)
        d.rectangle((4, y - 2, 4 + lim + 1, y + 8), outline=STONE[2] + (255,))
        draw_text(img, 6, y, s_, INK[0])
        draw_text(img, 4 + lim + 8, y + 1, f'{w} / {lim} {"OK" if w <= lim else "OVER"}', STONE[0], face='rune')
        y += 12
    y += 2
    draw_text(img, 4, y, 'Kerning LT TA AV Y. ->', BLOOD[1])
    x = 4 + text_width('Kerning LT TA AV Y. ->') + 4
    draw_text(img, x, y, 'LATTER VAT Y.', INK[0]); y += 13
    # colour pairings on the theme surfaces
    d.rectangle((0, y - 2, W, y + 44), fill=UMBER[1] + (255,))
    d.rectangle((4, y + 1, 80, y + 15), fill=IRON[1] + (255,), outline=GOLD[1] + (255,))
    draw_text(img, 10, y + 4, 'PURCHASE', GOLD[2], shadow=INK[0])
    d.rectangle((86, y + 1, 150, y + 15), fill=VELLUM[2] + (255,), outline=INK[1] + (255,))
    draw_text(img, 92, y + 4, 'RETURN', INK[0])
    d.rectangle((156, y + 1, 214, y + 15), fill=BLOOD[1] + (255,), outline=INK[0] + (255,))
    draw_text(img, 162, y + 4, 'CLOSE', VELLUM[3], shadow=BLOOD[0])
    d.rectangle((220, y + 1, 300, y + 15), fill=STONE[3] + (255,), outline=STONE[0] + (255,))
    draw_text(img, 226, y + 4, 'BALANCE', INK[0])
    draw_text(img, 6, y + 22, 'SOULREND', SOUL[1], face='rune')
    draw_text(img, 46, y + 22, 'EMBER', EMBER[1], face='rune')
    draw_text(img, 72, y + 22, 'VELLUM ON UMBER', VELLUM[3], face='rune')
    draw_text(img, 6, y + 31, 'Graven on umber, vellum_3 + outline', VELLUM[3], outline=INK[0])
    y += 46
    img = img.crop((0, 0, W, y + 2))
    return img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)


if __name__ == '__main__':
    out = _Path(__file__).resolve().parents[2] / 'evidence' / 'soulrend' / 'typeface-specimen.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    specimen().save(out)
    for s_, lim in FIT_CHECKS:
        print(f'{s_!r}: {text_width(s_)} px (limit {lim})')
    print('WROTE', out)
