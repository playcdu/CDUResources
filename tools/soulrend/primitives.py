"""Hand-drawn pixel primitives for the Soulrend theme.

Every function takes a PIL RGBA image and integer coordinates, draws only
Soulrend palette colours, and is deterministic: anything that varies (scuffs,
mortar joints, chain jitter, torn edges) is driven by an explicit ``seed``, so
the same call always produces the same pixels. Boxes are (x, y, w, h).

Groups
------
pixels      put, get, fill, hline, vline, line, sprite, sprite_size, rounded_mask
lines       ink_line (optional wobble, line weight), crack, chain
edges       highlight_edge, shadow_edge, ink_outline, bevel
materials   umber_panel, stone_blocks, stone_tablet, iron_plate, rivet,
            vellum_strip, torn_edge, page_curl, cloth_panel, wax_seal
backdrops   remember_backdrop, reveal: edge-cutting helpers (deckle, tear,
            page curl, banner tatter) never punch alpha-0 holes through an
            opaque surface; a cut cell shows what was painted underneath
details     candle, banner, gold_filigree, arch_niche, moss_tuft, glow,
            dither_patch
wells       well_frame, socket_well, carved_well, merge_holes
            (never paint inside the hole)
states      make_disabled, make_disabled_seal, make_selected, make_pulse,
            pulse_depths, make_state, edge_distance
            (alpha is never changed; pulses and selected never change
            lettering; disabled dims lettering in place)

Licence: MIT.
"""
from __future__ import annotations

import random
import sys as _sys
import weakref
from collections import deque
from pathlib import Path as _Path

if __name__ == 'primitives':
    _sys.modules.setdefault('soulrend.primitives', _sys.modules[__name__])
_TOOLS = _Path(__file__).resolve().parents[1]
if str(_TOOLS) not in _sys.path:
    _sys.path.append(str(_TOOLS))

from soulrend.palette import (BLOOD, EMBER, GOLD, INK, IRON, MOSS, SOUL, STONE, UMBER,  # noqa: E402
                              VELLUM, luminance, ramp_of, rgba, step)

# One colour key shared by every ASCII sprite in the theme (primitives, icons,
# motifs). '.' and ' ' are transparent.
SK = {
    'O': INK[0], 'o': INK[1], 'i': INK[2],
    'a': IRON[0], 'b': IRON[1], 'c': IRON[2], 'd': IRON[3],
    'm': STONE[0], 'n': STONE[1], 'p': STONE[2], 'q': STONE[3],
    '0': UMBER[0], '1': UMBER[1], '2': UMBER[2], '3': UMBER[3],
    'v': VELLUM[0], 'w': VELLUM[1], 'x': VELLUM[2], 'y': VELLUM[3],
    'r': BLOOD[0], 's': BLOOD[1], 't': BLOOD[2],
    'e': EMBER[0], 'f': EMBER[1], 'F': EMBER[2],
    'k': SOUL[0], 'l': SOUL[1], 'L': SOUL[2],
    'g': GOLD[0], 'h': GOLD[1], 'H': GOLD[2],
    'j': MOSS[0], 'z': MOSS[1], 'Z': MOSS[2],
}

# ---------------------------------------------------------------------------
# Pixels
# ---------------------------------------------------------------------------

def _c(colour):
    return rgba(colour)


def _rng(seed, *salt):
    return random.Random(':'.join(str(s) for s in (seed,) + salt))


def put(img, x, y, colour):
    """Set one opaque pixel (silently clipped)."""
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), _c(colour))


def get(img, x, y):
    if 0 <= x < img.width and 0 <= y < img.height:
        return img.getpixel((x, y))
    return (0, 0, 0, 0)


def fill(img, box, colour):
    x, y, w, h = box
    x0, y0, x1, y1 = max(0, x), max(0, y), min(img.width, x + w), min(img.height, y + h)
    if x0 < x1 and y0 < y1:
        img.paste(_c(colour), (x0, y0, x1, y1))


def hline(img, x0, x1, y, colour):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        put(img, x, y, colour)


def vline(img, x, y0, y1, colour):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        put(img, x, y, colour)


def line_points(x0, y0, x1, y1):
    """Bresenham points from (x0, y0) to (x1, y1) inclusive."""
    pts = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def line(img, x0, y0, x1, y1, colour):
    for x, y in line_points(x0, y0, x1, y1):
        put(img, x, y, colour)


def sprite(img, x, y, rows, key=None, flip_x=False, flip_y=False):
    """Draw a hand-authored ASCII sprite. ``key`` maps characters to colours
    (default: the shared theme key ``SK``); '.' and ' ' are transparent.
    Ragged rows are padded on the right. Unknown characters raise."""
    key = SK if key is None else {**SK, **key}
    rows = list(rows)
    width = max(len(r) for r in rows) if rows else 0
    rows = [r.ljust(width, '.') for r in rows]
    if flip_y:
        rows = rows[::-1]
    for j, row in enumerate(rows):
        if flip_x:
            row = row[::-1]
        for i, ch in enumerate(row):
            if ch in '. ':
                continue
            if ch not in key:
                raise KeyError(f'sprite character {ch!r} has no colour in key')
            put(img, x + i, y + j, key[ch])


def sprite_size(rows):
    rows = list(rows)
    return (max(len(r) for r in rows) if rows else 0), len(rows)


_CORNERS = {
    0: set(),
    1: {(0, 0)},
    2: {(0, 0), (1, 0), (0, 1)},
    3: {(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 1)},
}


def rounded_mask(w, h, radius=1):
    """Set of (x, y) inside a w x h box with pixel-art rounded (or, with
    ``radius`` 'c', chamfered 45-degree) corners."""
    cut = _CORNERS[min(radius, 3)]
    inside = set()
    for y in range(h):
        for x in range(w):
            if (x, y) in cut or (w - 1 - x, y) in cut or (x, h - 1 - y) in cut or (w - 1 - x, h - 1 - y) in cut:
                continue
            inside.add((x, y))
    return inside


def _edge_pixels(inside):
    """Pixels of a shape that touch the outside (4-neighbour)."""
    out = set()
    for (x, y) in inside:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in inside:
                out.add((x, y))
                break
    return out


def _side(inside, x, y):
    """Which outside directions a shape pixel touches: subset of 'tlbr'."""
    s = ''
    if (x, y - 1) not in inside: s += 't'
    if (x - 1, y) not in inside: s += 'l'
    if (x, y + 1) not in inside: s += 'b'
    if (x + 1, y) not in inside: s += 'r'
    return s


# ---------------------------------------------------------------------------
# Lines
# ---------------------------------------------------------------------------

def _wobbled(points, wobble, seed, horizontal):
    """Offset runs of points by +-1 perpendicular, in runs of >= 3 px."""
    if not wobble:
        return points
    r = _rng(seed, 'wobble', len(points))
    out = []
    off = 0
    run = r.randint(3, 7)
    for (x, y) in points:
        if run == 0:
            choices = [o for o in (-1, 0, 1) if abs(o) <= wobble and o != off] or [0]
            off = r.choice(choices) if r.random() < 0.55 else 0
            run = r.randint(3, 8)
        run -= 1
        out.append((x, y + off) if horizontal else (x + off, y))
    return out


def ink_line(img, x0, y0, x1, y1, colour='ink_1', wobble=0, seed=0, weight=1, weight_colour=None):
    """A deliberate 1 px ink line. ``wobble`` (0/1) jogs short runs by one
    pixel; ``weight`` 2 adds a second line on the shadow (down/right) side in
    ``weight_colour`` (default ink_0) for line-weight variation."""
    pts = line_points(x0, y0, x1, y1)
    horizontal = abs(x1 - x0) >= abs(y1 - y0)
    pts = _wobbled(pts, wobble, seed, horizontal)
    for x, y in pts:
        put(img, x, y, colour)
    if weight > 1:
        wc = weight_colour or 'ink_0'
        for x, y in pts:
            put(img, x, y + 1, wc) if horizontal else put(img, x + 1, y, wc)
    return pts


def crack(img, x, y, length=6, seed=0, direction='down', colour='ink_1', light=None, branch=True):
    """A hairline crack in stone or plaster: a 1 px line that steps diagonally
    in short irregular runs (never a straight ruler line), with an optional lit
    edge pixel (``light``) on its lower-right side and one short branch.
    ``direction``: 'down', 'up', 'left' or 'right'. Returns the points."""
    r = _rng(seed, 'crack', x, y)
    dx, dy = {'down': (0, 1), 'up': (0, -1), 'left': (-1, 0), 'right': (1, 0)}[direction]
    pts = []
    cx, cy = x, y
    drift = r.choice((-1, 1))
    for i in range(length):
        pts.append((cx, cy))
        cx += dx; cy += dy
        if r.random() < 0.45:
            if dx == 0:
                cx += drift
            else:
                cy += drift
        if r.random() < 0.2:
            drift = -drift
    for (px, py) in pts:
        put(img, px, py, colour)
    if light is not None:
        for (px, py) in pts[1::2]:
            q = (px + 1, py) if dx == 0 else (px, py + 1)
            if q not in pts and get(img, *q)[3]:
                put(img, q[0], q[1], light)
    if branch and length >= 5:
        bx, by = pts[length // 2]
        for k in range(1, 3):
            put(img, bx + (k * -drift if dx == 0 else k * dx), by + (k * dy if dx == 0 else k * -drift), colour)
    return pts


def _sag_points(x0, y0, x1, y1, sag):
    """Points of a hanging line from (x0,y0) to (x1,y1) with a parabolic sag."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    pts = []
    for i in range(n + 1):
        t = i / n
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t))
        if not pts or pts[-1] != (x, y):
            if pts and abs(pts[-1][1] - y) > 1:   # keep the line connected
                for yy in range(pts[-1][1] + (1 if y > pts[-1][1] else -1), y, 1 if y > pts[-1][1] else -1):
                    pts.append((pts[-1][0], yy))
            pts.append((x, y))
    return pts


# Chain links: an open (face-on) link and an edge-on link, for each run direction.
_LINK_H_OPEN = ['.dc.', 'c..a', '.ba.']
_LINK_H_EDGE = ['cba']
_LINK_V_OPEN = ['.d.', 'c.b', 'c.a', '.a.']
_LINK_V_EDGE = ['c', 'b', 'a']


def chain(img, x0, y0, x1, y1, sag=0, seed=0, shadow='ink_0'):
    """Wrought-iron chain from (x0, y0) to (x1, y1), hanging with ``sag``.
    Face-on and edge-on links alternate every 3 px; a seeded few links sit
    1 px off the line so the chain looks forged, not stamped. Each link drops
    a 1 px ``shadow`` below/right (None to skip). Returns the link centres."""
    pts = _sag_points(x0, y0, x1, y1, sag)
    horizontal = abs(x1 - x0) >= abs(y1 - y0)
    r = _rng(seed, 'chain', x0, y0, x1, y1)
    centres = []
    for i in range(0, len(pts), 3):
        cx, cy = pts[i]
        jitter = 1 if r.random() < 0.18 else 0
        k = i // 3
        if horizontal:
            rows = _LINK_H_OPEN if k % 2 == 0 else _LINK_H_EDGE
            w, h = sprite_size(rows)
            sx, sy = cx - w // 2, cy - h // 2 + (jitter if k % 2 == 0 else 0)
        else:
            rows = _LINK_V_OPEN if k % 2 == 0 else _LINK_V_EDGE
            w, h = sprite_size(rows)
            sx, sy = cx - w // 2 + (jitter if k % 2 == 0 else 0), cy - h // 2
        if shadow is not None:
            for j, row in enumerate(rows):
                for ii, ch in enumerate(row):
                    if ch != '.':
                        q = (sx + ii + (0 if horizontal else 1), sy + j + (1 if horizontal else 0))
                        if get(img, *q)[3]:
                            put(img, q[0], q[1], shadow)
        sprite(img, sx, sy, rows)
        centres.append((cx, cy))
    return centres


# ---------------------------------------------------------------------------
# Edges and outlines
# ---------------------------------------------------------------------------

def highlight_edge(img, box, colour='iron_2', sides='tl', broken=0, seed=0, inset=0):
    """1 px cold light line just inside the top/left of ``box``. ``broken`` > 0
    skips about one pixel in ``broken`` so the highlight looks hand-placed."""
    x, y, w, h = box
    x += inset; y += inset; w -= 2 * inset; h -= 2 * inset
    r = _rng(seed, 'hl', box)
    if 't' in sides:
        for xx in range(x + 1, x + w - 1):
            if not broken or r.randrange(broken) or xx < x + 3:
                put(img, xx, y, colour)
    if 'l' in sides:
        for yy in range(y + 1, y + h - 1):
            if not broken or r.randrange(broken) or yy < y + 3:
                put(img, x, yy, colour)
    if 'b' in sides:
        hline(img, x + 1, x + w - 2, y + h - 1, colour)
    if 'r' in sides:
        vline(img, x + w - 1, y + 1, y + h - 2, colour)


def shadow_edge(img, box, colour='ink_1', sides='br', inset=0):
    """1 px deep shadow just inside the bottom/right of ``box``."""
    x, y, w, h = box
    x += inset; y += inset; w -= 2 * inset; h -= 2 * inset
    if 'b' in sides:
        hline(img, x + 1, x + w - 1, y + h - 1, colour)
    if 'r' in sides:
        vline(img, x + w - 1, y + 1, y + h - 1, colour)
    if 't' in sides:
        hline(img, x, x + w - 2, y, colour)
    if 'l' in sides:
        vline(img, x, y, y + h - 2, colour)


def ink_outline(img, box, colour='ink_1', radius=1, heavy='', heavy_colour='ink_0', fill_colour=None):
    """Rounded 1 px ink outline around ``box``. ``heavy`` sides ('b', 'r', 'br')
    use ``heavy_colour`` (default ink_0) for deliberate line-weight variation.
    Returns the inside pixel set (box-local)."""
    x, y, w, h = box
    inside = rounded_mask(w, h, radius)
    edge = _edge_pixels(inside)
    if fill_colour is not None:
        for (i, j) in inside - edge:
            put(img, x + i, y + j, fill_colour)
    for (i, j) in edge:
        s = _side(inside, i, j)
        put(img, x + i, y + j, heavy_colour if any(c in heavy for c in s if c in 'br') else colour)
    return inside


def bevel(img, box, light, dark, inset=0, corners=True):
    """Raised 1 px bevel just inside ``box``: ``light`` on top/left, ``dark`` on
    bottom/right. ``corners`` False leaves the two mixed corners untouched."""
    x, y, w, h = box
    x += inset; y += inset; w -= 2 * inset; h -= 2 * inset
    if w <= 0 or h <= 0:
        return
    hline(img, x + (0 if corners else 1), x + w - 2, y, light)
    vline(img, x, y + (0 if corners else 1), y + h - 2, light)
    hline(img, x + 1, x + w - 1, y + h - 1, dark)
    vline(img, x + w - 1, y + 1, y + h - 1, dark)


# ---------------------------------------------------------------------------
# Backdrops: what lies under a surface, so cutting its edge reveals it
# ---------------------------------------------------------------------------

_BACKDROPS = {}     # id(img) -> (weakref to img, [(box, snapshot crop), ...])


def remember_backdrop(img, box=None):
    """Record what is painted under ``box`` (default: the whole image) BEFORE
    a surface is painted there. Later ``torn_edge`` / ``page_curl`` calls with
    ``behind=None`` restore these pixels into the cells they cut away, so a
    tear in vellum on a stone wall shows the wall, while on an empty button it
    is still alpha 0. ``vellum_strip`` calls this itself; call it yourself
    before painting paper by hand. Returns the snapshot crop."""
    x, y, w, h = box or (0, 0, img.width, img.height)
    crop = img.crop((x, y, x + w, y + h))
    for k in [k for k, (ref, _) in _BACKDROPS.items() if ref() is None]:
        del _BACKDROPS[k]
    entry = _BACKDROPS.get(id(img))
    if entry is None or entry[0]() is not img:
        entry = (weakref.ref(img), [])
        _BACKDROPS[id(img)] = entry
    entry[1].append(((x, y, w, h), crop))
    return crop


def backdrop_pixel(img, x, y):
    """The most recently remembered backdrop pixel at (x, y), or None."""
    entry = _BACKDROPS.get(id(img))
    if entry is None or entry[0]() is not img:
        return None
    for (bx, by, bw, bh), crop in reversed(entry[1]):
        if bx <= x < bx + bw and by <= y < by + bh:
            return crop.getpixel((x - bx, y - by))
    return None


def reveal(img, x, y, under=None):
    """Cut one cell out of a painted surface: show ``under`` (an image
    snapshot taken before painting) at (x, y), else the remembered backdrop
    (``remember_backdrop``), else alpha 0. Never punches a hole through a
    surface whose backdrop is known to be opaque."""
    if not (0 <= x < img.width and 0 <= y < img.height):
        return
    if under is not None:
        c = under.getpixel((x, y))
    else:
        c = backdrop_pixel(img, x, y) or (0, 0, 0, 0)
    img.putpixel((x, y), c)


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

def umber_panel(img, box, seed=0, ramp=UMBER, scuffs=1.0, pits=1.0):
    """The menu sheet: flat dark umber leather-over-wood (ramp[1]) with a few
    hand-placed scuffs (2-4 px diagonal ramp[0] scratches with a ramp[2] lit
    end) and rare ramp[2] pits. Calm on purpose: wells and text bands carry the
    structure, the sheet only whispers age."""
    x, y, w, h = box
    fill(img, box, ramp[1])
    r = _rng(seed, 'umber', box)
    n = int(w * h / 420 * scuffs)
    for _ in range(n):
        sx = r.randint(x + 1, x + max(1, w - 5)); sy = r.randint(y + 1, y + max(1, h - 5))
        ln = r.randint(2, 4)
        d = r.choice((1, -1))
        for k in range(ln):
            put(img, sx + k, sy + k * d if d == 1 else sy + ln - 1 - k, ramp[0])
        put(img, sx + ln, sy + (ln if d == 1 else -1), ramp[2])
    m = int(w * h / 700 * pits)
    for _ in range(m):
        px, py = r.randint(x, x + w - 1), r.randint(y, y + h - 1)
        put(img, px, py, ramp[2] if r.random() < 0.6 else ramp[0])
        if r.random() < 0.3:
            put(img, px + 1, py, ramp[0])


def stone_blocks(img, box, seed=0, ramp=STONE, course=6, mortar=None, moss=0.0, cracks=0.4, vertical=False):
    """Ashlar masonry filling ``box``: courses ``course`` px tall of blocks 7-16
    px long, offset course to course, 1 px mortar (ramp[0]). Each block takes
    ramp[1] (most), ramp[2] or, rarely, a sunken ramp[0] face (seeded); a broken
    lit top edge one step above its face and a shaded bottom edge one step
    below; some blocks get a chipped corner or a hairline crack; with ``moss``
    > 0 joints grow moss, more often toward the bottom of the box (damp).
    ``vertical`` turns the courses into columns (pillars)."""
    x, y, w, h = box
    mortar = mortar or ramp[0]
    fill(img, box, mortar)
    r = _rng(seed, 'stone', box)
    span, depth = (h, w) if vertical else (w, h)
    lane = 0
    row = 0
    while lane < depth:
        th = min(course, depth - lane)
        pos = -r.randint(0, 9) if row % 2 else -r.randint(3, 12)
        while pos < span:
            ln = r.randint(7, 16)
            a, b = max(0, pos), min(span, pos + ln - 1)     # block body excludes the 1 px joint
            if b - a >= 2 and th >= 3:
                roll = r.random()
                bi = 2 if roll < 0.36 else (0 if roll > 0.93 else 1)
                body = ramp[bi]
                for t in range(a, b):
                    for k in range(0, th - 1):
                        px, py = (x + lane + k, y + t) if vertical else (x + t, y + lane + k)
                        put(img, px, py, body)
                # lit top (or left) edge, broken
                for t in range(a, b):
                    if r.random() < 0.75:
                        px, py = (x + lane, y + t) if vertical else (x + t, y + lane)
                        put(img, px, py, ramp[min(3, bi + 1)])
                # shaded last row
                for t in range(a + 1, b):
                    px, py = (x + lane + th - 2, y + t) if vertical else (x + t, y + lane + th - 2)
                    if th >= 4 and bi > 0:
                        put(img, px, py, ramp[bi - 1])
                if r.random() < 0.18 and not vertical:
                    put(img, x + b - 1, y + lane, mortar)              # chipped corner
                    put(img, x + b - 2, y + lane, mortar)
                if r.random() < cracks * 0.25 and b - a > 6 and not vertical and th >= 5:
                    cx = x + r.randint(a + 2, b - 3)
                    crack(img, cx, y + lane + 1, th - 3, seed=(seed, lane, pos), colour=mortar, branch=False)
                damp = 0.5 + (lane / max(1, depth))
                if moss and r.random() < moss * damp and not vertical:
                    mx = x + r.randint(a, max(a, b - 3))
                    my = y + lane + th - 1
                    moss_tuft(img, mx, my, r.randint(2, 4), seed=(seed, mx, my))
            pos += ln
        lane += th
        row += 1


def stone_tablet(img, box, seed=0, ramp=STONE, outline='ink_1', radius=1):
    """A carved stone tablet face (read-only info): ramp[3] face, chiselled
    INWARD bevel (ramp[1] on the top/left inner edge, ramp[3] stays on the
    bottom/right) so it reads as cut into stone, not raised like a button; two
    seeded chisel marks. Returns the inner box for carved lettering."""
    x, y, w, h = box
    ink_outline(img, box, outline, radius=radius, heavy='br', fill_colour=ramp[3])
    hline(img, x + 1, x + w - 2, y + 1, ramp[1])
    vline(img, x + 1, y + 1, y + h - 2, ramp[1])
    hline(img, x + 2, x + w - 2, y + 2, ramp[2])
    r = _rng(seed, 'tablet', box)
    for _ in range(2):
        cx = r.randint(x + 3, x + max(3, w - 5)); cy = r.randint(y + 3, y + max(3, h - 3))
        put(img, cx, cy, ramp[2]); put(img, cx + 1, cy, ramp[2])
    return (x + 2, y + 2, w - 4, h - 4)


def iron_plate(img, box, rim='gold', rivets=True, outline='ink_0', radius=1, seed=0, glint=True):
    """Blackened iron plate. From the outside in: ``outline`` (rounded); a 1 px
    ``rim`` ring ('gold': gold_1 with gold_2 top/left and gold_0 bottom/right;
    'iron': the same in iron; None: no rim); a raised inner bevel (iron_2
    top/left, ink_1 bottom/right); iron_1 body with a few seeded hammer pits
    (iron_0) and an iron_3 glint at the top-left; rivets at the inner corners
    (gold on a gold rim) when the plate is at least 26 x 12. Returns the
    inner body box."""
    x, y, w, h = box
    ink_outline(img, box, outline, radius=radius, fill_colour=IRON[1])
    inset = 1
    if rim:
        rr = GOLD if rim == 'gold' else IRON
        lit, mid, dark = (rr[2], rr[1], rr[0]) if rim == 'gold' else (IRON[3], IRON[2], IRON[0])
        hline(img, x + 1, x + w - 2, y + 1, lit)
        vline(img, x + 1, y + 1, y + h - 2, lit)
        hline(img, x + 2, x + w - 2, y + h - 2, dark)
        vline(img, x + w - 2, y + 2, y + h - 2, dark)
        put(img, x + w - 2, y + 1, mid); put(img, x + 1, y + h - 2, mid)
        inset = 2
    ix, iy, iw, ih = x + inset, y + inset, w - 2 * inset, h - 2 * inset
    if iw > 2 and ih > 2:
        bevel(img, (ix, iy, iw, ih), IRON[2], INK[1])
        r = _rng(seed, 'plate', box)
        for _ in range(max(1, iw * ih // 60)):
            px = r.randint(ix + 2, ix + max(2, iw - 3)); py = r.randint(iy + 2, iy + max(2, ih - 3))
            put(img, px, py, IRON[0])
        if glint and iw >= 8:
            hline(img, ix + 1, ix + min(4, iw - 3), iy + 1, IRON[3])
            put(img, ix + 1, iy + 2, IRON[3])
        if rivets and w >= 26 and h >= 12:
            kind = 'gold' if rim == 'gold' else 'iron'
            for (rx, ry) in ((ix + 1, iy + 1), (ix + iw - 3, iy + 1), (ix + 1, iy + ih - 3), (ix + iw - 3, iy + ih - 3)):
                rivet(img, rx, ry, kind, size=2)
    return (ix + 1, iy + 1, iw - 2, ih - 2)


RIVETS = {
    2: ['hm', 'md'],
    3: ['.h.', 'hmd', '.d.'],
    4: ['.Oo.', 'Ohmo', 'omdO', '.oO.'],
}


def rivet(img, x, y, kind='iron', size=3):
    """A domed rivet with its top-left corner at (x, y). ``kind`` 'iron'
    (iron_3 / iron_2 / iron_0), 'gold' (gold_2 / gold_1 / gold_0) or 'dark'
    (iron_2 / iron_1 / ink_0, for rivets on lit iron). ``size`` 2, 3 or 4
    (4 has an ink collar for rivets on cloth or stone)."""
    tones = {'iron': (IRON[3], IRON[2], IRON[0]), 'gold': (GOLD[2], GOLD[1], GOLD[0]),
             'dark': (IRON[2], IRON[1], INK[0])}[kind]
    sprite(img, x, y, RIVETS[size], {'h': tones[0], 'm': tones[1], 'd': tones[2]})


def vellum_strip(img, box, seed=0, outline='ink_1', deckle='tb', ramp=VELLUM, fibres=True, radius=0,
                 heavy='b'):
    """Bone-white vellum: ramp[2] body, ramp[3] top inner row, ramp[1] bottom
    inner row, ``outline`` ink rim (``heavy`` sides ink_0). ``deckle`` sides
    ('t', 'b', 'l', 'r') get a hand-cut uneven edge: the outline steps in by
    one pixel in seeded runs of 2-6 px, so the strip reads as cut vellum, not
    a UI rectangle; the pixel the edge gives up shows whatever was there
    before the strip was painted (alpha 0 on a button, the sheet on a
    background). ``fibres`` adds a few short ramp[1] fibre dashes (never
    dark, so the live text bands stay light). Returns the box."""
    x, y, w, h = box
    r = _rng(seed, 'vellum', box)
    under = img.copy()
    remember_backdrop(img, box)
    fill(img, (x + 1, y + 1, w - 2, h - 2), ramp[2])
    hline(img, x + 1, x + w - 2, y + 1, ramp[3])
    if h >= 6:
        hline(img, x + 1, x + w - 2, y + h - 2, ramp[1])
    if fibres:
        for _ in range(max(1, w * h // 120)):
            fx = r.randint(x + 2, x + max(2, w - 5)); fy = r.randint(y + 2, y + max(2, h - 3))
            hline(img, fx, fx + r.randint(1, 2), fy, ramp[1])
    inside = rounded_mask(w, h, radius)
    edge = _edge_pixels(inside)
    for (i, j) in edge:
        s = _side(inside, i, j)
        put(img, x + i, y + j, 'ink_0' if any(c in heavy for c in s if c in 'br') else outline)
    for side in deckle:
        _deckle(img, box, side, r, outline, ramp, under)
    return box


def _deckle(img, box, side, r, outline, ramp, under=None):
    """Step an edge of a painted strip inward by 1 px in irregular runs: the
    old edge pixel gets back what ``under`` (a copy taken before painting)
    held there, or alpha 0, and the ink moves one pixel in."""
    x, y, w, h = box

    def restore(px, py):
        if 0 <= px < img.width and 0 <= py < img.height:
            img.putpixel((px, py), under.getpixel((px, py)) if under is not None else (0, 0, 0, 0))
    if side in 'tb':
        t = 3
        while t < w - 3:
            run = r.randint(2, 6)
            if r.random() < 0.35:
                for k in range(t, min(w - 3, t + run)):
                    ey = y if side == 't' else y + h - 1
                    iy = ey + 1 if side == 't' else ey - 1
                    restore(x + k, ey)
                    put(img, x + k, iy, outline if side == 't' else 'ink_0')
            t += run + r.randint(2, 5)
    else:
        t = 3
        while t < h - 3:
            run = r.randint(2, 4)
            if r.random() < 0.35:
                for k in range(t, min(h - 3, t + run)):
                    ex = x if side == 'l' else x + w - 1
                    ix = ex + 1 if side == 'l' else ex - 1
                    restore(ex, y + k)
                    put(img, ix, y + k, outline)
            t += run + r.randint(2, 5)


def torn_edge(img, box, edge='r', seed=0, depth=3, behind=None, ramp=VELLUM, outline='ink_1', burnt=False,
              under=None):
    """Tear the ``edge`` of already painted paper inside ``box``: a jagged ink
    line up to ``depth`` px deep with a ramp[0] fibre shadow just inside it.
    Pixels beyond the tear become ``behind`` (a colour) or, with
    ``behind=None``, show what was under the paper (``under`` snapshot, else
    the backdrop ``vellum_strip`` / ``remember_backdrop`` recorded, else alpha
    0 - an empty button). A tear never opens a hole through an opaque wall.
    With ``burnt`` the tear is charred: ink_0 edge, ember_0 / umber_0 scorch
    inside."""
    x, y, w, h = box
    r = _rng(seed, 'torn', edge, box)
    n = h if edge in 'lr' else w
    d = r.randint(0, depth)
    for i in range(n):
        if r.random() < 0.55:
            d = max(0, min(depth, d + r.choice((-1, 1))))
        for k in range(0, depth + 1):
            if edge == 'r':
                px, py = x + w - 1 - k, y + i
            elif edge == 'l':
                px, py = x + k, y + i
            elif edge == 'b':
                px, py = x + i, y + h - 1 - k
            else:
                px, py = x + i, y + k
            if k < depth - d:
                if behind is None:
                    reveal(img, px, py, under)
                else:
                    put(img, px, py, behind)
            elif k == depth - d:
                put(img, px, py, 'ink_0' if burnt else outline)
            elif k == depth - d + 1:
                put(img, px, py, ('ember_0' if (i % 3) else 'umber_0') if burnt else ramp[0])
            elif burnt and k == depth - d + 2 and i % 2:
                put(img, px, py, ramp[0])


def page_curl(img, box, corner='br', size=5, ramp=VELLUM, outline='ink_1', behind=None, under=None):
    """Curl the ``corner`` ('br', 'bl', 'tr', 'tl') of already painted vellum.
    Measured from the corner, pixels with i + j < size - 1 become ``behind``
    (or, with ``behind=None``, what was under the page: ``under`` snapshot,
    else the remembered backdrop, else alpha 0); the fold diagonal i + j == size - 1 is ink; the turned flap
    is the removed triangle reflected across the fold, painted ramp[1] (the
    page's underside) with an ink outer edge, a ramp[3] crease along the fold
    and a ramp[0] tip. Returns the flap pixels."""
    x, y, w, h = box
    s = size

    def at(i, j):
        px = x + w - 1 - i if 'r' in corner else x + i
        py = y + h - 1 - j if 'b' in corner else y + j
        return px, py

    for j in range(s):
        for i in range(s - j):
            px, py = at(i, j)
            if i + j < s - 1:
                if behind is None:
                    reveal(img, px, py, under)
                else:
                    put(img, px, py, behind)
            else:
                put(img, px, py, outline)
    flap = []
    for j in range(s):
        for i in range(s):
            if i + j < s - 1:
                fi, fj = s - 1 - j, s - 1 - i          # reflection across the fold
                flap.append((fi, fj))
    out = []
    for (fi, fj) in flap:
        px, py = at(fi, fj)
        edge = fi == s - 1 or fj == s - 1
        crease = fi + fj == s
        put(img, px, py, outline if edge else (ramp[3] if crease else ramp[1]))
        out.append((px, py))
    tip = at(s - 1, s - 1)
    put(img, tip[0], tip[1], 'ink_0')
    inner = at(s - 2, s - 2)
    if s >= 4:
        put(img, inner[0], inner[1], ramp[0])
    return out


def cloth_panel(img, box, ramp=BLOOD, seed=0, outline='ink_0', studs=True, folds=True, radius=1):
    """Heavy blood-red cloth stretched on a frame (the danger grammar):
    ramp[1] body, broken ramp[2] gloss on the top inner row, ramp[0] bottom
    inner row, vertical folds every 10-14 px (a ramp[0] crease with a ramp[2]
    lit ridge beside it), ``outline`` ink rim heavy at the bottom, and iron
    studs (3 px domes) in the corners when ``studs`` and the panel is at least
    24 px wide. Returns the inner box."""
    x, y, w, h = box
    ink_outline(img, box, outline, radius=radius, heavy='b', fill_colour=ramp[1])
    r = _rng(seed, 'cloth', box)
    for xx in range(x + 2, x + w - 2):
        if r.random() < 0.85:
            put(img, xx, y + 1, ramp[2])
    hline(img, x + 1, x + w - 2, y + h - 2, ramp[0])
    vline(img, x + 1, y + 2, y + h - 3, ramp[2])
    if folds and w >= 20:
        fx = x + r.randint(6, 9)
        while fx < x + w - 6:
            for yy in range(y + 2, y + h - 2):
                if (yy - y) % 5 != 4:
                    put(img, fx, yy, ramp[0])
                    put(img, fx + 1, yy, ramp[2]) if (yy - y) % 3 == 0 else None
            fx += r.randint(10, 14)
    if studs and w >= 24 and h >= 10:
        for (sx, sy) in ((x + 1, y + 1), (x + w - 4, y + 1), (x + 1, y + h - 4), (x + w - 4, y + h - 4)):
            rivet(img, sx, sy, 'iron', size=3)
    return (x + 2, y + 2, w - 4, h - 4)


def _blob(w, h, seed, wobble=1):
    """Organic disc-ish mask inside a w x h box (wax). Deterministic."""
    r = _rng(seed, 'blob', w, h)
    cx, cy = (w - 1) / 2, (h - 1) / 2
    rx, ry = w / 2, h / 2
    inside = set()
    jag = [r.choice((0, 0, 0, 1)) * wobble for _ in range(16)]
    for y in range(h):
        for x in range(w):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            import math
            ang = int(((math.atan2(dy, dx) + math.pi) / (2 * math.pi)) * 16) % 16
            lim = 1.0 - jag[ang] * 0.12
            if dx * dx + dy * dy <= lim * 1.02:
                inside.add((x, y))
    return inside


def wax_seal(img, cx, cy, r, ramp=BLOOD, seed=0, emblem=None, studs=0, outline='ink_0', drip=False):
    """Round blood-red wax seal centred at (cx, cy), radius ``r`` (>= 3):
    slightly irregular rim (``outline``), ramp[1] body, a ramp[2] lit crescent
    top-left, a ramp[0] pressed inner ring, optional ``emblem`` (icons.EMBLEMS
    name, r >= 5), ``studs`` iron studs (4 or 8) round the rim, optional drip.
    Returns the inside pixel set (image coordinates)."""
    d = 2 * r + 1
    x0, y0 = cx - r, cy - r
    inside = {(x0 + i, y0 + j) for (i, j) in _blob(d, d, seed, wobble=1 if r >= 5 else 0)}
    edge = {p for p in inside if any((p[0] + dx, p[1] + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    for p in inside - edge:
        put(img, p[0], p[1], ramp[1])
    for p in edge:
        put(img, p[0], p[1], outline)
    # lit crescent (top-left) and shaded rim (bottom-right), one ring inside the edge
    ring = {p for p in inside - edge if any((p[0] + dx, p[1] + dy) in edge for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    for p in ring:
        if p[0] - cx + p[1] - cy < -1:
            put(img, p[0], p[1], ramp[2])
        elif p[0] - cx + p[1] - cy > 1:
            put(img, p[0], p[1], ramp[0])
    if r >= 5:
        rr = r - 3
        for a in range(0, 360, 6):
            import math
            px = round(cx + rr * math.cos(math.radians(a))); py = round(cy + rr * math.sin(math.radians(a)))
            if (px, py) in inside and (px, py) not in ring and (px, py) not in edge:
                put(img, px, py, ramp[0])
    if emblem and r >= 5:
        from soulrend import icons
        icons.draw_emblem(img, cx, cy, emblem, ramp)
    if studs:
        import math
        angles = (45, 135, 225, 315) if studs == 4 else tuple(range(0, 360, 45))
        for a in angles:
            px = round(cx + (r - 1) * math.cos(math.radians(a))); py = round(cy + (r - 1) * math.sin(math.radians(a)))
            put(img, px, py, IRON[3]); put(img, px + 1, py + 1, IRON[0]) if (px + 1, py + 1) in inside else None
    if drip:
        dx = cx + r // 2
        dy = max(p[1] for p in inside if p[0] == dx)
        put(img, dx, dy + 1, ramp[1]); put(img, dx, dy + 2, outline)
        put(img, dx - 1, dy + 1, outline); put(img, dx + 1, dy + 1, outline)
    return inside


# ---------------------------------------------------------------------------
# Details
# ---------------------------------------------------------------------------

CANDLE_FLAME = ['..F..', '.fFf.', '.fFf.', '..e..']
CANDLE_FLAME_SMALL = ['.F.', 'fFf', '.e.']


def candle(img, x, y, height=7, lit=True, width=3, ramp=VELLUM, holder='iron', seed=0):
    """A bone-wax candle whose wick top is at (x + width // 2, y): flame above
    the wick (4 px; 3 px when ``width`` is 2), body ``height`` px of ramp[1]
    with a ramp[3] lit left column and ramp[0] right column, a seeded wax drip,
    and an optional ``holder`` ('iron' dish or 'gold' dish, None for none).
    Unlit candles get a charred ink wick and no flame. Returns the flame
    centre (cx, cy) for ``glow``."""
    cx = x + width // 2
    r = _rng(seed, 'candle', x, y)
    put(img, cx, y, 'ink_1' if lit else 'ink_0')
    for j in range(1, height + 1):
        for i in range(width):
            col = ramp[3] if i == 0 else (ramp[0] if i == width - 1 else ramp[1])
            put(img, x + i, y + j, col)
    # outline
    vline(img, x - 1, y + 1, y + height, 'ink_1')
    vline(img, x + width, y + 1, y + height, 'ink_0')
    hline(img, x, x + width - 1, y + 1, ramp[2])
    if height >= 4:
        dxp = x + (0 if r.random() < 0.5 else width - 1)
        put(img, dxp - (1 if dxp == x else -1), y + 2, ramp[2]); put(img, dxp - (1 if dxp == x else -1), y + 3, ramp[1])
    if holder:
        tones = (IRON[2], IRON[1], INK[0]) if holder == 'iron' else (GOLD[2], GOLD[1], GOLD[0])
        hline(img, x - 2, x + width + 1, y + height + 1, tones[1])
        put(img, x - 2, y + height + 1, tones[0])
        hline(img, x - 1, x + width, y + height + 2, tones[2])
    if lit:
        rows = CANDLE_FLAME if width >= 3 else CANDLE_FLAME_SMALL
        fw, fh = sprite_size(rows)
        sprite(img, cx - fw // 2, y - fh, rows)
        return cx, y - fh // 2 - 1
    return cx, y


def banner(img, x, y, w, h, ramp=MOSS, seed=0, emblem=None, rod=True, trim=GOLD, tatter=True):
    """A hanging heraldic banner: an iron rod with finials across the top
    (when ``rod``), cloth ``ramp`` (ramp[1] body, ramp[2] lit left column,
    ramp[0] right shadow column and folds), a ``trim`` line under the rod, a
    tattered swallowtail bottom with seeded ragged notches (``tatter``), and an
    optional ``emblem`` sprite name from icons.CRESTS centred in the field.
    The banner box is (x, y, w, h) not counting the rod overhang. Tatter
    notches show whatever was painted under the banner (the wall on a frame,
    alpha 0 only where the image was already empty), never a new hole."""
    r = _rng(seed, 'banner', x, y, w, h)
    under = img.copy()
    cut = max(2, w // 3)
    for j in range(h):
        for i in range(w):
            # swallowtail: a V notch rising from the bottom centre
            depth_here = cut - abs(i - (w - 1) / 2) * (2 * cut / max(1, w))
            if j >= h - 1 - max(0, int(depth_here)):
                continue
            col = ramp[1]
            if i == 0:
                col = 'ink_1'
            elif i == w - 1:
                col = 'ink_0'
            elif i == 1:
                col = ramp[2]
            elif i == w - 2:
                col = ramp[0]
            put(img, x + i, y + j, col)
    # bottom ink edge following the swallowtail, with seeded tatter notches
    for i in range(w):
        depth_here = cut - abs(i - (w - 1) / 2) * (2 * cut / max(1, w))
        by = y + h - 1 - max(0, int(depth_here)) - 1
        if tatter and 0 < i < w - 1 and r.random() < 0.3:
            reveal(img, x + i, by, under)
            by -= 1
        put(img, x + i, by, 'ink_0')
    # folds
    if w >= 8:
        for fx in (x + w // 3, x + 2 * w // 3):
            for yy in range(y + 3, y + h - cut - 1):
                if (yy + fx) % 4:
                    put(img, fx, yy, ramp[0])
    if trim:
        hline(img, x + 1, x + w - 2, y + 1, trim[1])
        hline(img, x + 1, x + w - 2, y + 2, trim[0])
        for i in range(1, w - 1, 3):
            put(img, x + i, y + 1, trim[2])
    if rod:
        hline(img, x - 2, x + w + 1, y, IRON[2])
        hline(img, x - 2, x + w + 1, y - 1, 'ink_0')
        put(img, x - 3, y, 'ink_0'); put(img, x + w + 2, y, 'ink_0')
        sprite(img, x - 3, y - 1, ['h', 'H', 'g'])
        sprite(img, x + w + 2, y - 1, ['h', 'H', 'g'])
    if emblem:
        from soulrend import icons
        ew, eh = icons.crest_size(emblem)
        icons.draw_crest(img, emblem, x + (w - ew) // 2, y + 4 + max(0, (h - cut - 6 - eh) // 2))


FILIGREE = {
    # corner scroll: tarnished gold wire curling into the corner (top-left form)
    'corner': ['hHHHh..',
               'H.....',
               'H.hh..',
               'H.h.g.',
               'h..g..',
               '.......',
               '......'],
    # a scroll end for plaques and bands (left form), 5x7
    'scroll': ['.hh..',
               'h..h.',
               'h.Hh.',
               'h.g..',
               '.h...',
               '..hh.',
               '....h'],
    # a small fleur finial, 5x5
    'fleur': ['..H..',
              '.hHh.',
              'h.H.h',
              '..h..',
              '.ggg.'],
    # a horizontal vine flourish, 11x3
    'flourish': ['.hh.....hh.',
                 'h..hHHHh..h',
                 '.g.......g.'],
}


def gold_filigree(img, x, y, kind='corner', corner='tl', ramp=None):
    """Hand-authored tarnished-gold scrollwork: ``kind`` 'corner', 'scroll',
    'fleur' or 'flourish' (see ``FILIGREE``), mirrored to ``corner`` ('tl',
    'tr', 'bl', 'br'). ``ramp`` IRON draws the same scroll in wrought iron."""
    rows = FILIGREE[kind]
    key = None
    if ramp is IRON:
        key = {'h': IRON[2], 'H': IRON[3], 'g': IRON[0]}
    sprite(img, x, y, rows, key, flip_x='r' in corner, flip_y='b' in corner)
    return sprite_size(rows)


def arch_niche(img, box, seed=0, ramp=STONE, interior='ink_1', keystone=True):
    """A round-topped stone niche: dark ``interior`` with an arch of
    alternating voussoir stones (ramp[2] / ramp[1], lit ramp[3] inner edge)
    and an optional keystone. Returns the interior pixel set."""
    x, y, w, h = box
    import math
    rad = (w - 1) / 2
    cx = x + rad
    spring = y + int(rad)
    interior_px = set()
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if yy < spring:
                dist = math.hypot(xx - cx, (yy - spring) * 1.0)
                if dist > rad + 0.3:
                    continue
                if dist > rad - 2.2:
                    seg = int((math.degrees(math.atan2(spring - yy, xx - cx)) + 180) // 22)
                    put(img, xx, yy, ramp[2] if seg % 2 else ramp[1])
                    if dist > rad - 0.7:
                        put(img, xx, yy, 'ink_1')
                    continue
            else:
                if xx < x + 2 or xx > x + w - 3:
                    put(img, xx, yy, ramp[2] if (yy // 4) % 2 else ramp[1])
                    if xx == x or xx == x + w - 1:
                        put(img, xx, yy, 'ink_1')
                    continue
            put(img, xx, yy, interior)
            interior_px.add((xx, yy))
    if keystone:
        k = int(cx)
        sprite(img, k - 1, y - 1, ['oqo', 'oqo', '.p.'])
    return interior_px


def moss_tuft(img, x, y, w=3, seed=0, ramp=MOSS):
    """A few strands of moss hanging from a ledge at row ``y``: ramp[1]
    strands of 1-3 px with ramp[2] lit tips on top, ramp[0] at the ends."""
    r = _rng(seed, 'moss', x, y)
    for i in range(w):
        ln = r.randint(1, 3)
        put(img, x + i, y, ramp[2] if i % 2 == 0 else ramp[1])
        for k in range(1, ln):
            put(img, x + i, y + k, ramp[1] if k < ln - 1 else ramp[0])


BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def dither_patch(img, box, colour, density=0.25, only_opaque=True, phase=(0, 0)):
    """Ordered (4x4 Bayer) dither of ``colour`` over ``box`` at ``density``
    (0..1). Use sparingly for hand-placed shading transitions, never as noise.
    By default only already-opaque pixels change."""
    x, y, w, h = box
    t = int(density * 16 + 0.5)
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if BAYER4[(yy + phase[1]) % 4][(xx + phase[0]) % 4] < t:
                if only_opaque and get(img, xx, yy)[3] == 0:
                    continue
                put(img, xx, yy, colour)


def glow(img, cx, cy, r, kind='ember', strength=1, ring=None):
    """Light pooling around (cx, cy) by hand-placed dither, never a gradient.
    Opaque, non-ink pixels move ``strength`` steps lighter along their own
    ramp in three bands: solid inside 3r/5, a 50 % checker to 3r/4, a sparse
    12 % Bayer to r. Close to the source (inside r/2) the darkest pixels
    (mortar, seams, shadow) also catch a sparse stipple of the light's own
    colour: ember_0 for ``kind`` 'ember', soul_0 for 'soul'. With ``ring=k``
    only a 1 px ring at radius k is lit (pulse illustrations). Ink pixels and
    alpha never change."""
    base = img.copy()
    bpx = base.load()
    tint = SOUL[0] if kind == 'soul' else EMBER[0]
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            if not (0 <= x < img.width and 0 <= y < img.height):
                continue
            p = bpx[x, y]
            if p[3] == 0 or (ramp_of(p) or ('', 0))[0] == 'ink':
                continue
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if ring is not None:
                if (ring - 1) ** 2 < d2 <= ring ** 2 + ring:
                    put(img, x, y, glow_colour(p, kind))
                continue
            b = BAYER4[y % 4][x % 4]
            if d2 <= (r // 2) ** 2 and luminance(p) < 60 and b < 6:
                put(img, x, y, tint)
            elif d2 <= (3 * r // 5) ** 2:
                put(img, x, y, step(p, strength))
            elif d2 <= (3 * r // 4) ** 2:
                if (x + y) % 2 == 0:
                    put(img, x, y, step(p, strength))
            elif d2 <= r * r:
                if b < 2:
                    put(img, x, y, step(p, strength))


def glow_colour(p, kind='ember'):
    """A glow colour that contrasts with the surface it lands on: for ember,
    ember_1 on light vellum and on dark iron/umber/cloth, ember_2 on gold and
    mid stone; for soul, soul_1 on dark and soul_0 on light surfaces."""
    lum = luminance(p)
    if kind == 'soul':
        return SOUL[0] if lum > 150 else SOUL[1]
    return EMBER[1] if lum > 165 else EMBER[2] if lum > 95 else EMBER[1]


# ---------------------------------------------------------------------------
# Item wells: frames around transparent holes. Never paints inside a hole.
# ---------------------------------------------------------------------------

def _as_rects(holes):
    out = []
    if hasattr(holes, 'clearance'):
        holes = [holes]
    if hasattr(holes, 'x') and hasattr(holes, 'w'):
        holes = [holes]
    for h in holes:
        if hasattr(h, 'clearance'):
            h = h.clearance
        if hasattr(h, 'tuple'):
            h = h.tuple()
        out.append(tuple(h))
    return out


def well_frame(img, holes, style='socket', depth=3, protect=(), lip='ink_0', rivets=True, seam=18):
    """Frame the transparent ``holes`` (Rects, Slots or (x,y,w,h) tuples) as a
    recessed socket. Rings are measured outward from the hole (Chebyshev d):

    d=1  ink lip (``lip``) all round: the crisp inner edge of the socket
    d=2  stone wall: the side whose hole lies below/right (the top and left
         walls) is in SHADOW (stone_0); the bottom and right walls catch the
         cold top-left light (stone_3)
    d=3  socket style: a raised iron frame, iron_2 on its top/left runs and
         iron_0 on its bottom/right runs, with a 1 px iron_3 rivet wherever a
         slot seam (every ``seam`` px from the hole's corner) meets the frame
         and at every outer corner;
         carved style: a chiselled stone lip, one ramp step lighter on the
         top/left and darker on the bottom/right of what is underneath.

    Inside ``protect`` rects only the d=1 lip is drawn (the vellum text bands
    stay light). Pixels inside any hole are never touched."""
    rects = _as_rects(holes)
    W, H = img.size
    hole = bytearray(W * H)
    for (x, y, w, h) in rects:
        for yy in range(max(0, y), min(H, y + h)):
            for xx in range(max(0, x), min(W, x + w)):
                hole[yy * W + xx] = 1
    prot = _as_rects(protect)

    def protected(px, py):
        return any(x <= px < x + w and y <= py < y + h for (x, y, w, h) in prot)

    def is_hole(px, py):
        return 0 <= px < W and 0 <= py < H and hole[py * W + px]

    base = img.copy()
    bpx = base.load()
    seams = set()
    if rivets and style == 'socket':
        for (x, y, w, h) in rects:
            for k in range(0, w + 1, seam):
                seams.add((x + k - (1 if k == w else 0), 'v'))
            for k in range(0, h + 1, seam):
                seams.add((y + k - (1 if k == h else 0), 'h'))
    for (x, y, w, h) in rects:
        for py in range(y - depth, y + h + depth):
            for px in range(x - depth, x + w + depth):
                if not (0 <= px < W and 0 <= py < H) or hole[py * W + px]:
                    continue
                d = None
                for k in range(1, depth + 1):
                    if any(is_hole(px + dx, py + dy) for dy in range(-k, k + 1) for dx in range(-k, k + 1)
                           if max(abs(dx), abs(dy)) == k):
                        d = k
                        break
                if d is None:
                    continue
                if protected(px, py) and d > 1:
                    continue
                shadow_side = any(is_hole(px + dx, py + dy) for dx in range(0, d + 1) for dy in range(0, d + 1)
                                  if (dx, dy) != (0, 0))
                under = bpx[px, py]
                if under[3] == 0:
                    under = UMBER[1] + (255,)
                if d == 1:
                    put(img, px, py, lip)
                elif d == 2:
                    put(img, px, py, STONE[0] if shadow_side else STONE[3])
                elif d == 3:
                    if style == 'socket':
                        put(img, px, py, IRON[2] if shadow_side else IRON[0])
                    else:
                        put(img, px, py, step(under, 1) if shadow_side else step(under, -1))
    if rivets and style == 'socket':
        # rivets at outer corners and at slot seams on the d3 iron ring
        for (x, y, w, h) in rects:
            ring = []
            for px in range(x - depth, x + w + depth):
                ring += [(px, y - depth), (px, y + h + depth - 1)]
            for py in range(y - depth, y + h + depth):
                ring += [(x - depth, py), (x + w + depth - 1, py)]
            for (px, py) in ring:
                if not (0 <= px < W and 0 <= py < H) or hole[py * W + px] or protected(px, py):
                    continue
                cur = img.getpixel((px, py))
                if tuple(cur[:3]) not in (IRON[2], IRON[0]):
                    continue
                corner = px in (x - depth, x + w + depth - 1) and py in (y - depth, y + h + depth - 1)
                on_seam = ((px - x) % seam == 0 and py in (y - depth, y + h + depth - 1) and x < px < x + w - 1) or \
                          ((py - y) % seam == 0 and px in (x - depth, x + w + depth - 1) and y < py < y + h - 1)
                if corner or on_seam:
                    put(img, px, py, IRON[3])
    return img


def socket_well(img, holes, protect=(), depth=3, rivets=True):
    """Recessed iron-framed stone socket (see ``well_frame``)."""
    return well_frame(img, holes, 'socket', depth, protect, rivets=rivets)


def carved_well(img, holes, protect=(), depth=3):
    """Recessed socket with a chiselled stone lip (see ``well_frame``)."""
    return well_frame(img, holes, 'carved', depth, protect, rivets=False)


def merge_holes(slots):
    """Merge Slot clearances into maximal row rectangles (fewer, cleaner rects)."""
    rects = sorted({s.clearance.tuple() if hasattr(s, 'clearance') else tuple(s) for s in slots},
                   key=lambda r: (r[1], r[0]))
    rows = []
    for r in rects:
        if rows and rows[-1][1] == r[1] and rows[-1][3] == r[3] and rows[-1][0] + rows[-1][2] >= r[0]:
            x, y, w, h = rows[-1]
            rows[-1] = (x, y, max(x + w, r[0] + r[2]) - x, h)
        else:
            rows.append(r)
    return rows


# ---------------------------------------------------------------------------
# Shared state transforms. Alpha never changes; protected (lettering) pixels
# never change.
# ---------------------------------------------------------------------------

def edge_distance(img, maxd=6):
    """Per-pixel 8-neighbour distance from the shape edge: 0 for opaque pixels
    touching transparency or the image border, 1 for the next ring, ... ;
    None for transparent pixels. Capped at ``maxd``."""
    w, h = img.size
    a = img.getchannel('A').load()
    dist = [[None] * w for _ in range(h)]
    q = deque()
    for y in range(h):
        for x in range(w):
            if a[x, y] == 0:
                continue
            border = x == 0 or y == 0 or x == w - 1 or y == h - 1
            if border or any(a[x + dx, y + dy] == 0 for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                             if 0 <= x + dx < w and 0 <= y + dy < h):
                dist[y][x] = 0
                q.append((x, y))
    while q:
        x, y = q.popleft()
        d = dist[y][x]
        if d >= maxd:
            continue
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and a[nx, ny] and dist[ny][nx] is None:
                    dist[ny][nx] = d + 1
                    q.append((nx, ny))
    for y in range(h):
        for x in range(w):
            if a[x, y] and dist[y][x] is None:
                dist[y][x] = maxd
    return dist


def _is_ink(p):
    rp = ramp_of(p)
    return rp is not None and rp[0] == 'ink'


# luminance -> cold inert colour (the 'cold grey stone' of disabled controls)
_DISABLED_LEVELS = [(42, INK[1]), (88, IRON[1]), (999, IRON[2])]


def _inert(p):
    lum = luminance(p)
    for lim, col in _DISABLED_LEVELS:
        if lum < lim:
            return col
    return IRON[2]


def _inert_letter(p):
    """Dead-stone lettering: ink stays ink; light lettering (gold_2, vellum_3,
    any colour of luminance >= 88) turns iron_3, a cold grey one step above
    the dim face so the label stays legible but no longer shines; dark
    non-ink lettering turns ink_1."""
    if _is_ink(p):
        return tuple(p[:3])
    return IRON[3] if luminance(p) >= 88 else INK[1]


def make_disabled(img, lettering=None, cracks=True, seed=0):
    """Cold grey stone, label included: every non-ink pixel is mapped by
    luminance onto just three flat tones, ink_1 / iron_1 / iron_2 (thresholds
    42 / 88), so gold, blood and vellum all go dead, bevels flatten and glints
    vanish. Pixels in ``lettering`` (the glyph pixels from
    ``compose.lettering_mask(halo=False)``) keep their position and alpha
    exactly but are recoloured into the dead-stone lettering register
    (``_inert_letter``: gold -> iron_3, vellum_3 -> iron_3, ink stays ink), so
    a disabled primary reads grey-on-grey rather than gold-on-grey. With
    ``cracks`` two short hairline cracks (ink_1) are scored across the face,
    kept 1 px clear of the lettering. Alpha unchanged."""
    lettering = lettering or set()
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            p = px[x, y]
            if p[3] == 0:
                continue
            if (x, y) in lettering:
                px[x, y] = _inert_letter(p) + (p[3],)
            elif not _is_ink(p):
                px[x, y] = _inert(p) + (p[3],)
    if cracks and out.width >= 18 and out.height >= 12:
        dist = edge_distance(out, 3)
        near = {(x + dx, y + dy) for (x, y) in lettering for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
        r = _rng(seed, 'disabled', out.size)
        starts = [(2 + r.randint(0, 3), 2), (out.width - 6 - r.randint(0, 3), out.height - 3)]
        for k, (sx, sy) in enumerate(starts):
            cx, cy = sx, sy
            for i in range(5 if out.height < 30 else 8):
                if 0 <= cx < out.width and 0 <= cy < out.height and px[cx, cy][3] and \
                        (cx, cy) not in near and (dist[cy][cx] or 0) >= 1 and not _is_ink(px[cx, cy]):
                    px[cx, cy] = INK[1] + (px[cx, cy][3],)
                cx += 1 if k == 0 else -1
                cy += (1 if k == 0 else -1) if (i % 3 != 1) else 0
    return out


def make_selected(img, protect=None, sparkle=True):
    """Lit with soul-light and raised: every non-ink colour outside
    ``protect`` moves one step lighter on its own ramp; the first interior
    ring becomes a soul-cyan rim (soul_2 on the top/left runs, soul_1 on the
    rest, soul_0 on the bottom/right runs); an optional 3 px soul sparkle sits
    in the top-right interior. Ink and protected lettering are kept. Alpha
    unchanged."""
    protect = protect or set()
    out = img.copy()
    px = out.load()
    dist = edge_distance(out, 2)
    w, h = out.size
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            if p[3] == 0 or _is_ink(p) or (x, y) in protect:
                continue
            d = dist[y][x]
            c = step(p, 1)
            if d == 1:
                up = dist[y - 1][x] if y > 0 else 0
                left = dist[y][x - 1] if x > 0 else 0
                down = dist[y + 1][x] if y < h - 1 else 0
                right = dist[y][x + 1] if x < w - 1 else 0
                if up == 0 or left == 0:
                    c = SOUL[2] if luminance(p) < 150 else SOUL[1]
                elif down == 0 or right == 0:
                    c = SOUL[0]
                else:
                    c = SOUL[1]
            px[x, y] = c + (p[3],)
    if sparkle and w >= 14 and h >= 10:
        sx, sy = w - 6, 2
        for (dx, dy) in ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2)):
            q = px[sx + dx, sy + dy]
            if q[3] and not _is_ink(q) and (sx + dx, sy + dy) not in protect and dist[sy + dy][sx + dx] >= 2:
                px[sx + dx, sy + dy] = (SOUL[2] if (dx, dy) == (1, 1) else SOUL[1]) + (q[3],)
    return out


_PULSE_DEPTHS = (3, 2, 1)   # designed ring depth (px in from the edge) for pulse_1..3


def pulse_depths(dist, protect=None):
    """Ring depths (pulse_1, pulse_2, pulse_3) that stay clear of ``protect``.

    The designed rings sit 3, 2 and 1 px in from the edge, so the glow
    expands outward. When protected pixels (lettering plus its 1 px halo) come
    closer to the edge than that - typical on 18 px tall buttons - the rings
    are compressed into the free band between edge and lettering."""
    if not protect:
        return _PULSE_DEPTHS
    near = min((dist[y][x] for (x, y) in protect if 0 <= y < len(dist) and 0 <= x < len(dist[0])
                and dist[y][x] is not None), default=99)
    room = max(1, min(3, near - 1))
    return {3: (3, 2, 1), 2: (2, 1, 1), 1: (1, 1, 1)}[room]


def make_pulse(img, n, protect=None):
    """Ember glow ring, frame ``n`` of 3, expanding outward and fading:

    pulse_1  bright ember ring 3 px in from the edge; unlettered faces (icons,
             seals) also warm one ramp step in the core
    pulse_2  the ring moves out to 2 px; afterglow (one step lighter) where it was
    pulse_3  a faint checker-dithered ember ring 1 px in, afterglow at 2 px;
             the server's next frame is the resting state

    When the lettering leaves room for only one ring (``pulse_depths`` gives
    1/1/1), pulse_2 cannot move outward, so it alternates bright and
    afterglow pixels along the ring and spreads an afterglow one ring further
    in (never onto ``protect``): the three frames always differ.

    ``protect`` (lettering plus 1 px halo, from ``compose.lettering_mask``)
    never changes. Ring colour contrasts with its surface (``glow_colour``).
    Ink pixels and alpha never change."""
    if n not in (1, 2, 3):
        raise ValueError('pulse frame must be 1, 2 or 3')
    protect = protect or set()
    out = img.copy()
    px = out.load()
    dist = edge_distance(out, 6)
    depths = pulse_depths(dist, protect)
    ring_d = depths[n - 1]
    after_d = None if n == 1 else depths[n - 2]
    if after_d == ring_d:
        after_d = None
    faint = n == 3
    spread = n == 2 and depths[0] == depths[1]     # no room to move outward
    if spread:
        after_d = ring_d + 1
    for y in range(out.height):
        for x in range(out.width):
            p = px[x, y]
            if p[3] == 0 or _is_ink(p) or (x, y) in protect:
                continue
            d = dist[y][x]
            c = None
            if d == ring_d:
                if spread and (x + y) % 2:
                    c = step(p, 1)
                elif not faint:
                    c = glow_colour(p)
                elif (x + y) % 2 == 0:
                    c = EMBER[0] if luminance(p) < 120 else EMBER[1]
            elif after_d is not None and d == after_d:
                c = step(p, 1)
            elif n == 1 and d > ring_d and not protect:
                c = step(p, 1)
            if c is not None:
                px[x, y] = c + (p[3],)
    return out


_WAX_TO_IRON = {BLOOD[0]: IRON[0], BLOOD[1]: IRON[1], BLOOD[2]: IRON[2]}


def make_disabled_seal(img):
    """Disabled state for wax seals (the 18x18 close control): the blood wax
    cools to dead iron-grey (blood_0/1/2 -> iron_0/1/2), the pressed X and the
    rim keep their ink, studs dim. It still reads as a close seal. Alpha
    unchanged."""
    out = img.copy()
    src, px = img.load(), out.load()
    for y in range(out.height):
        for x in range(out.width):
            p = src[x, y]
            if not p[3] or _is_ink(p):
                continue
            rgb = tuple(p[:3])
            px[x, y] = (_WAX_TO_IRON.get(rgb) or _inert(p)) + (p[3],)
    return out


def make_state(img, state, protect=None, seal=False, glyphs=None):
    """Apply the shared transform for a state name to a painted normal frame.

    ``protect``: lettering pixels plus a 1 px halo (pulses never touch them);
    ``glyphs``: the lettering pixels alone (selected keeps them; disabled keeps
    their position and alpha but dims their colour; defaults to ``protect``).
    ``seal``: a wax-seal control (disabled uses ``make_disabled_seal``)."""
    glyphs = protect if glyphs is None else glyphs
    if state == 'normal':
        return img.copy()
    if state == 'disabled':
        return make_disabled_seal(img) if seal else make_disabled(img, glyphs)
    if state == 'selected':
        return make_selected(img, glyphs)
    if state.startswith('pulse_'):
        return make_pulse(img, int(state[-1]), protect)
    raise ValueError(f'unknown state {state!r}')
