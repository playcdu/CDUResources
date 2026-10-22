"""Bespoke cozy pixel lettering: two original hand-authored faces.

HEARTH  - the main label face. Cap height 7, x-height 5, descender 2,
          variable width (1-5 px), 1 px tracking, 2 px space glyph
          (4 px of air between words).
SPRIG   - the small sign-writing face for frame headings, side tags and tiny
          captions. Cap height 5, uppercase/digits only, variable width (1-5 px),
          1 px tracking, 1 px space glyph
          (3 px of air between words).

Coordinates: ``draw_text(img, x, y, ...)`` puts the TOP of the cap height at
``y``. The baseline is the last cap row, ``y + cap_height - 1``. Lowercase
x-height rows are ``y + 2 .. y + 6`` and descenders occupy ``y + 7 .. y + 8``
(HEARTH only). Every glyph below is drawn by hand in this file: '#' is ink and
'.' is empty. Nothing is derived from another font, and the old generated
5x7 / 3x5 alphabets in tools/*.py are deliberately not reused.

Licence: glyph designs CC0-1.0, code MIT.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_HERE = str(_Path(__file__).resolve().parent)
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

from palette import rgba  # noqa: E402

# ---------------------------------------------------------------------------
# HEARTH: cap height 7. Storybook traits: lowered A bar, short E/F middle arms,
# tapered S, spurred G, curled J and Q tails, peaked M/W centres, a slab-serif I.
# ---------------------------------------------------------------------------
_HEARTH_UPPER = {
    'A': ['.##.', '#..#', '#..#', '#..#', '####', '#..#', '#..#'],
    'B': ['###.', '#..#', '#..#', '###.', '#..#', '#..#', '###.'],
    'C': ['.##.', '#..#', '#...', '#...', '#...', '#..#', '.##.'],
    'D': ['###.', '#..#', '#..#', '#..#', '#..#', '#..#', '###.'],
    'E': ['####', '#...', '#...', '###.', '#...', '#...', '####'],
    'F': ['####', '#...', '#...', '###.', '#...', '#...', '#...'],
    'G': ['.##.', '#..#', '#...', '#.##', '#..#', '#..#', '.###'],
    'H': ['#..#', '#..#', '#..#', '####', '#..#', '#..#', '#..#'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'J': ['..##', '...#', '...#', '...#', '...#', '#..#', '.##.'],
    'K': ['#..#', '#..#', '#.#.', '##..', '#.#.', '#..#', '#..#'],
    'L': ['#...', '#...', '#...', '#...', '#...', '#...', '####'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
    'N': ['#..#', '##.#', '##.#', '#.##', '#.##', '#..#', '#..#'],
    'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'P': ['###.', '#..#', '#..#', '###.', '#...', '#...', '#...'],
    'Q': ['.##.', '#..#', '#..#', '#..#', '#..#', '#.#.', '.#.#'],
    'R': ['###.', '#..#', '#..#', '###.', '#.#.', '#..#', '#..#'],
    'S': ['.##.', '#..#', '#...', '.##.', '...#', '#..#', '.##.'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'U': ['#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'V': ['#...#', '#...#', '#...#', '.#.#.', '.#.#.', '.#.#.', '..#..'],
    'W': ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'],
    'X': ['#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'],
    'Y': ['#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'],
    'Z': ['####', '...#', '...#', '..#.', '.#..', '#...', '####'],
}
_HEARTH_DIGITS = {
    '0': ['.##.', '#..#', '#.##', '##.#', '#..#', '#..#', '.##.'],
    '1': ['.#.', '##.', '.#.', '.#.', '.#.', '.#.', '###'],
    '2': ['.##.', '#..#', '...#', '..#.', '.#..', '#...', '####'],
    '3': ['###.', '...#', '...#', '.##.', '...#', '...#', '###.'],
    '4': ['..#.', '.##.', '#.#.', '#.#.', '####', '..#.', '..#.'],
    '5': ['####', '#...', '###.', '...#', '...#', '#..#', '.##.'],
    '6': ['.##.', '#...', '#...', '###.', '#..#', '#..#', '.##.'],
    '7': ['####', '...#', '..#.', '..#.', '.#..', '.#..', '.#..'],
    '8': ['.##.', '#..#', '#..#', '.##.', '#..#', '#..#', '.##.'],
    '9': ['.##.', '#..#', '#..#', '.###', '...#', '...#', '.##.'],
}
_HEARTH_PUNCT = {
    ' ': ['..', '..', '..', '..', '..', '..', '..'],
    '+': ['...', '...', '.#.', '###', '.#.', '...', '...'],
    '-': ['...', '...', '...', '###', '...', '...', '...'],
    '=': ['...', '...', '###', '...', '###', '...', '...'],
    '$': ['..#..', '.####', '#.#..', '.###.', '..#.#', '####.', '..#..'],
    '.': ['.', '.', '.', '.', '.', '.', '#'],
    ',': ['..', '..', '..', '..', '..', '.#', '#.'],
    ':': ['.', '.', '#', '.', '.', '#', '.'],
    '!': ['#', '#', '#', '#', '#', '.', '#'],
    '?': ['.##.', '#..#', '...#', '..#.', '.#..', '....', '.#..'],
    '/': ['..#', '..#', '.#.', '.#.', '.#.', '#..', '#..'],
    "'": ['#', '#', '.', '.', '.', '.', '.'],
    '(': ['.#', '#.', '#.', '#.', '#.', '#.', '.#'],
    ')': ['#.', '.#', '.#', '.#', '.#', '.#', '#.'],
    '<': ['...', '..#', '.#.', '#..', '.#.', '..#', '...'],
    '>': ['...', '#..', '.#.', '..#', '.#.', '#..', '...'],
    '%': ['#...#', '#..#.', '...#.', '..#..', '.#...', '.#..#', '#...#'],
    '&': ['.##..', '#..#.', '.##..', '#.#.#', '#..#.', '#..#.', '.##.#'],
    '#': ['.....', '.#.#.', '#####', '.#.#.', '#####', '.#.#.', '.....'],
    '*': ['...', '#.#', '.#.', '#.#', '...', '...', '...'],
}
# Lowercase: 9 rows (rows 7-8 are descenders). x-height rows 2-6.
_HEARTH_LOWER = {
    'a': ['....', '....', '.##.', '...#', '.###', '#..#', '.###', '....', '....'],
    'b': ['#...', '#...', '###.', '#..#', '#..#', '#..#', '###.', '....', '....'],
    'c': ['....', '....', '.##.', '#..#', '#...', '#..#', '.##.', '....', '....'],
    'd': ['...#', '...#', '.###', '#..#', '#..#', '#..#', '.###', '....', '....'],
    'e': ['....', '....', '.##.', '#..#', '####', '#...', '.##.', '....', '....'],
    'f': ['.##', '#..', '###', '#..', '#..', '#..', '#..', '...', '...'],
    'g': ['....', '....', '.###', '#..#', '#..#', '#..#', '.###', '...#', '.##.'],
    'h': ['#...', '#...', '###.', '#..#', '#..#', '#..#', '#..#', '....', '....'],
    'i': ['#', '.', '#', '#', '#', '#', '#', '.', '.'],
    'j': ['.#', '..', '.#', '.#', '.#', '.#', '.#', '.#', '#.'],
    'k': ['#...', '#...', '#..#', '#.#.', '##..', '#.#.', '#..#', '....', '....'],
    'l': ['#.', '#.', '#.', '#.', '#.', '#.', '.#', '..', '..'],
    'm': ['.....', '.....', '##.#.', '#.#.#', '#.#.#', '#.#.#', '#.#.#', '.....', '.....'],
    'n': ['....', '....', '###.', '#..#', '#..#', '#..#', '#..#', '....', '....'],
    'o': ['....', '....', '.##.', '#..#', '#..#', '#..#', '.##.', '....', '....'],
    'p': ['....', '....', '###.', '#..#', '#..#', '#..#', '###.', '#...', '#...'],
    'q': ['....', '....', '.###', '#..#', '#..#', '#..#', '.###', '...#', '...#'],
    'r': ['...', '...', '#.#', '##.', '#..', '#..', '#..', '...', '...'],
    's': ['....', '....', '.###', '#...', '.##.', '...#', '###.', '....', '....'],
    't': ['.#.', '.#.', '###', '.#.', '.#.', '.#.', '..#', '...', '...'],
    'u': ['....', '....', '#..#', '#..#', '#..#', '#..#', '.###', '....', '....'],
    'v': ['.....', '.....', '#...#', '#...#', '.#.#.', '.#.#.', '..#..', '.....', '.....'],
    'w': ['.....', '.....', '#...#', '#...#', '#.#.#', '#.#.#', '.#.#.', '.....', '.....'],
    'x': ['....', '....', '#..#', '#..#', '.##.', '#..#', '#..#', '....', '....'],
    'y': ['....', '....', '#..#', '#..#', '#..#', '#..#', '.###', '...#', '.##.'],
    'z': ['....', '....', '####', '...#', '.##.', '#...', '####', '....', '....'],
}

# ---------------------------------------------------------------------------
# SPRIG: cap height 5, sign-writer's capitals. Rounded 4-wide bowls (O, C, G,
# Q, U, N), lowered A bar, open-bottom S. Uppercase, digits and basic marks.
# Lowercase input is drawn as capitals.
# ---------------------------------------------------------------------------
_SPRIG = {
    'A': ['.#.', '#.#', '#.#', '###', '#.#'],
    'B': ['##.', '#.#', '##.', '#.#', '##.'],
    'C': ['.##.', '#..#', '#...', '#..#', '.##.'],
    'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'E': ['###', '#..', '##.', '#..', '###'],
    'F': ['###', '#..', '##.', '#..', '#..'],
    'G': ['.##.', '#...', '#.##', '#..#', '.###'],
    'H': ['#.#', '#.#', '###', '#.#', '#.#'],
    'I': ['###', '.#.', '.#.', '.#.', '###'],
    'J': ['.##', '..#', '..#', '#.#', '.#.'],
    'K': ['#..#', '#.#.', '##..', '#.#.', '#..#'],
    'L': ['#..', '#..', '#..', '#..', '###'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'],
    'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'O': ['.##.', '#..#', '#..#', '#..#', '.##.'],
    'P': ['##.', '#.#', '##.', '#..', '#..'],
    'Q': ['.##.', '#..#', '#..#', '#.#.', '.#.#'],
    'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['.##', '#..', '.#.', '..#', '##.'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#..#', '#..#', '#..#', '#..#', '.##.'],
    'V': ['#.#', '#.#', '#.#', '.#.', '.#.'],
    'W': ['#...#', '#...#', '#.#.#', '#.#.#', '.#.#.'],
    'X': ['#.#', '#.#', '.#.', '#.#', '#.#'],
    'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'],
    'Z': ['###', '..#', '.#.', '#..', '###'],
    '0': ['.#.', '#.#', '#.#', '#.#', '.#.'],
    '1': ['.#', '##', '.#', '.#', '.#'],
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
    '$': ['.##', '##.', '.#.', '.##', '##.'],
    '.': ['.', '.', '.', '.', '#'],
    ',': ['..', '..', '..', '.#', '#.'],
    ':': ['.', '#', '.', '#', '.'],
    '!': ['#', '#', '#', '.', '#'],
    '?': ['##.', '..#', '.#.', '...', '.#.'],
    '/': ['..#', '..#', '.#.', '#..', '#..'],
    "'": ['#', '#', '.', '.', '.'],
    '&': ['.#..', '#.#.', '.#.#', '#.#.', '.#.#'],
    '<': ['..#', '.#.', '#..', '.#.', '..#'],
    '>': ['#..', '.#.', '..#', '.#.', '#..'],
    '(': ['.#', '#.', '#.', '#.', '.#'],
    ')': ['#.', '.#', '.#', '.#', '#.'],
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
        widths = {len(r) for rows in glyphs.values() for r in rows}
        for ch, rows in glyphs.items():
            if len({len(r) for r in rows}) != 1:
                raise ValueError(f'{name}: ragged glyph {ch!r}')
        self.max_width = max(widths)

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


HEARTH = Face('hearth', {**_HEARTH_UPPER, **_HEARTH_DIGITS, **_HEARTH_PUNCT, **_HEARTH_LOWER},
              cap_height=7, x_height=5, descender=2, tracking=1,
              kerning={('L', 'T'): -1, ('L', 'Y'): -1, ('L', 'V'): -1, ('T', 'A'): -1, ('A', 'T'): -1,
                       ('A', 'V'): -1, ('V', 'A'): -1, ('A', 'Y'): -1, ('Y', 'A'): -1, ('T', '.'): -1,
                       ('Y', '.'): -1, ('F', '.'): -1, ('P', '.'): -1, ('T', 'o'): -1, ('T', 'a'): -1,
                       ('T', 'e'): -1, ('r', '.'): -1, ('1', '1'): -1, ('/', '/'): -1})
SPRIG = Face('sprig', _SPRIG, cap_height=5, x_height=5, descender=0, tracking=1,
             kerning={('L', 'T'): -1, ('T', 'A'): -1, ('A', 'T'): -1, ('L', 'Y'): -1, ('Y', 'A'): -1,
                      ('A', 'Y'): -1, ('T', '.'): -1},
             upper_only=True)
FACES = {'hearth': HEARTH, 'sprig': SPRIG}


def _face(face):
    return face if isinstance(face, Face) else FACES[face]


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


def text_width(s, face='hearth'):
    """Ink width in pixels of ``s`` (no outline / shadow). Empty string is 0."""
    f = _face(face)
    s = f.norm(s)
    if not s:
        return 0
    last = 0
    for ch, x in _advances(s, f):
        last = x + f.width(ch)
    return last


def text_height(s, face='hearth'):
    """Rows the string occupies from the cap top (includes descenders if used)."""
    f = _face(face)
    s = f.norm(s)
    if not s:
        return 0
    descends = any('#' in ''.join(f.glyph(ch)[f.cap_height:]) for ch in s)
    return f.cap_height + (f.descender if descends else 0)


def fits(s, max_width, face='hearth'):
    return text_width(s, face) <= max_width


def _pixels(s, face):
    f = _face(face)
    s = f.norm(s)
    out = []
    for ch, ox in _advances(s, f):
        for yy, row in enumerate(f.glyph(ch)):
            for xx, c in enumerate(row):
                if c == '#':
                    out.append((ox + xx, yy))
    return out


def _put(img, x, y, colour):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), colour)


def draw_text(img, x, y, s, color='ink_0', shadow=None, outline=None, face='hearth', mask=None):
    """Draw ``s`` with its cap top at (x, y). Returns the ink width.

    color / shadow / outline accept palette names ('ink_0') or RGB(A) tuples.
    ``shadow`` draws a 1 px copy offset (+1, +1) beneath the letters (warm
    bottom-right shadow). ``outline`` draws a 1 px 4-neighbour halo first, so
    text reads on busy wood. ``mask`` (optional callable (x, y) -> bool) lets a
    painter skip pixels, e.g. masked clearances.
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


def draw_text_centered(img, cx, y, s, color='ink_0', shadow=None, outline=None, face='hearth', mask=None):
    """Centre ``s`` on column ``cx`` (left-biased when the width is even). Returns left x."""
    w = text_width(s, face)
    x = cx - w // 2
    draw_text(img, x, y, s, color, shadow, outline, face, mask)
    return x


def draw_lines_centered(img, box, lines, color='ink_0', shadow=None, outline=None, face='hearth', gap=2):
    """Centre several lines inside box (x, y, w, h). Returns the top y used."""
    f = _face(face)
    x, y, w, h = box
    total = len(lines) * f.cap_height + (len(lines) - 1) * gap
    top = y + (h - total) // 2
    for i, line in enumerate(lines):
        draw_text_centered(img, x + w // 2, top + i * (f.cap_height + gap), line, color, shadow, outline, face)
    return top


def fit_face(s, max_width):
    """'hearth' when it fits, else 'sprig', else None."""
    if text_width(s, 'hearth') <= max_width:
        return 'hearth'
    if text_width(s, 'sprig') <= max_width:
        return 'sprig'
    return None


def charset(face='hearth'):
    return ''.join(_face(face).glyphs)


# ---------------------------------------------------------------------------
# Specimen
# ---------------------------------------------------------------------------

FIT_CHECKS = [('LISTINGS', 50), ('DISABLE LISTING', 104), ('PURCHASE', 50), ('12 DAYS', 68)]


def specimen(scale=4):
    """Render the type specimen (both faces, fit checks, kerning) as an image."""
    from PIL import Image, ImageDraw
    from palette import PARCHMENT, INK, BERRY, SAGE, BRASS
    W = 300
    img = Image.new('RGBA', (W, 236), PARCHMENT[2] + (255,))
    y = 4
    draw_text(img, 4, y, 'HEARTH  cap 7 / x 5 / desc 2 / track 1', BERRY[1]); y += 12
    for row in ('ABCDEFGHIJKLM', 'NOPQRSTUVWXYZ', '0123456789 +-=$.,:!?/\'()<>%&#*', 'abcdefghijklm nopqrstuvwxyz'):
        draw_text(img, 4, y, row, INK[0]); y += 12
    draw_text(img, 4, y, 'Sell Price  Privacy  Opt 2  Tier 1', INK[0]); y += 14
    draw_text(img, 4, y, 'SPRIG  cap 5 / track 1  (uppercase)', BERRY[1], face='sprig'); y += 9
    for row in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', '0123456789 +-$.,:!?/\'&<>'):
        draw_text(img, 4, y, row, INK[0], face='sprig'); y += 8
    y += 4
    draw_text(img, 4, y, 'Fit checks (width / limit):', BERRY[1]); y += 11
    for s_, lim in FIT_CHECKS:
        w = text_width(s_)
        ImageDraw.Draw(img).rectangle((4, y - 2, 4 + lim + 1, y + 8), outline=SAGE[1] + (255,))
        draw_text(img, 6, y, s_, INK[0])
        draw_text(img, 4 + lim + 8, y + 1, f'{w} / {lim} {"OK" if w <= lim else "OVER"}', SAGE[0], face='sprig')
        y += 12
    y += 2
    draw_text(img, 4, y, 'Kerning: LT TA AV Y. -> ', BERRY[1])
    x = 4 + text_width('Kerning: LT TA AV Y. -> ') + 3
    draw_text(img, x, y, 'LATTE VAT Y.', INK[0]); y += 12
    draw_text(img, 4, y, 'Shadow + outline:', BERRY[1])
    from palette import WOOD
    ImageDraw.Draw(img).rectangle((112, y - 3, 296, y + 10), fill=WOOD[2] + (255,))
    draw_text(img, 116, y, 'BUY NOW', BRASS[3], shadow=WOOD[0])
    draw_text(img, 160, y, 'CLOSE', PARCHMENT[3], outline=INK[0])
    draw_text(img, 200, y, 'REDEEM', INK[0], shadow=BRASS[3])
    img = img.crop((0, 0, W, y + 14))
    return img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)


if __name__ == '__main__':
    out = _Path(__file__).resolve().parents[2] / 'evidence' / 'cozy' / 'typeface-specimen.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    specimen().save(out)
    for s_, lim in FIT_CHECKS:
        print(f'{s_!r}: {text_width(s_)} px (limit {lim})')
    print('WROTE', out)
