"""Hand-drawn pixel primitives for the cozy theme.

Every function takes a PIL RGBA image and integer coordinates, draws only
palette colours, and is deterministic: anything that varies (grain streaks,
wobble, fibres) is driven by an explicit ``seed`` argument, so the same call
always produces the same pixels. Boxes are (x, y, w, h).

Groups
------
pixels      put, fill, hline, vline, line, sprite, rounded_mask
lines       ink_line (optional wobble), stitch_line, rope, twine
edges       highlight_edge, shadow_edge, ink_outline
materials   plank, parchment_panel, brass_plate, linen_tag, wax_seal, page_curl
wells       well_frame, stitched_well, wood_well  (never paint inside the hole)
details     tack, leaf, mug, lantern, lantern_glow_ring, dither_patch
states      make_disabled, make_disabled_seal, make_selected, make_pulse,
            pulse_depths, make_state  (alpha is never changed)

Licence: MIT.
"""
from __future__ import annotations

import random
import sys as _sys
from collections import deque
from pathlib import Path as _Path

_HERE = str(_Path(__file__).resolve().parent)
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

from palette import (ASH, BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, WOOD,  # noqa: E402
                     luminance, ramp_of, rgba, step)

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


def sprite(img, x, y, rows, key, flip_x=False, flip_y=False):
    """Draw a hand-authored ASCII sprite. ``key`` maps characters to palette
    colours; '.' and ' ' are skipped (transparent). Unknown characters raise."""
    rows = list(rows)
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
    return (len(rows[0]) if rows else 0), len(rows)


_CORNERS = {
    0: set(),
    1: {(0, 0)},
    2: {(0, 0), (1, 0), (0, 1)},
    3: {(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 1)},
}


def rounded_mask(w, h, radius=1):
    """Set of (x, y) inside a w x h box with pixel-art rounded corners."""
    cut = _CORNERS[min(radius, 3)]
    inside = set()
    for y in range(h):
        for x in range(w):
            for (cx, cy), (fx, fy) in (((x, y), (1, 1)), ((w - 1 - x, y), (-1, 1)),
                                        ((x, h - 1 - y), (1, -1)), ((w - 1 - x, h - 1 - y), (-1, -1))):
                if (cx, cy) in cut:
                    break
            else:
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
    """Offset runs of points by +-1 perpendicular, in runs of >=3 px."""
    if not wobble:
        return points
    r = _rng(seed, 'wobble', len(points))
    out = []
    off = 0
    run = r.randint(3, 7)
    for i, (x, y) in enumerate(points):
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


def stitch_line(img, x0, y0, x1, y1, colour='parch_2', dash=2, gap=2, phase=0, shadow=None):
    """Running stitch: ``dash`` on, ``gap`` off. ``shadow`` puts a 1 px darker
    pixel after each dash (thread sinking into cloth)."""
    pts = line_points(x0, y0, x1, y1)
    period = dash + gap
    for i, (x, y) in enumerate(pts):
        k = (i + phase) % period
        if k < dash:
            put(img, x, y, colour)
        elif shadow is not None and k == dash:
            put(img, x, y, shadow)


def _sag_points(x0, y0, x1, y1, sag):
    """Points of a hanging cord from (x0,y0) to (x1,y1) with a parabolic sag."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    pts = []
    for i in range(n + 1):
        t = i / n
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t))
        if not pts or pts[-1] != (x, y):
            if pts and abs(pts[-1][1] - y) > 1:   # keep the cord connected
                for yy in range(pts[-1][1] + (1 if y > pts[-1][1] else -1), y, 1 if y > pts[-1][1] else -1):
                    pts.append((pts[-1][0], yy))
            pts.append((x, y))
    return pts


def rope(img, x0, y0, x1, y1, sag=0, light='wood_4', dark='wood_1', outline='ink_1'):
    """Twisted rope, 3 px tall (ink / twist / ink): the core alternates light and
    dark every 2 px so it reads as a twist. ``sag`` makes it hang. Returns points."""
    pts = _sag_points(x0, y0, x1, y1, sag)
    for x, y in pts:
        put(img, x, y - 1, outline)
        put(img, x, y + 1, outline)
    for i, (x, y) in enumerate(pts):
        put(img, x, y, light if (i // 2) % 2 else dark)
    return pts


def twine(img, x0, y0, x1, y1, sag=0, colour='parch_1', knot='parch_0'):
    """Thin 1 px twine with a two-tone twist; returns the points."""
    pts = _sag_points(x0, y0, x1, y1, sag)
    for i, (x, y) in enumerate(pts):
        put(img, x, y, knot if i % 3 == 2 else colour)
    return pts


# ---------------------------------------------------------------------------
# Edges and outlines
# ---------------------------------------------------------------------------

def highlight_edge(img, box, colour='wood_4', sides='tl', broken=0, seed=0, inset=0):
    """1 px light line just inside the top/left of ``box``. ``broken`` > 0
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


def shadow_edge(img, box, colour='wood_0', sides='br', inset=0):
    """1 px warm shadow just inside the bottom/right of ``box``."""
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


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

def _grain(img, box, ramp, seed, density=1.0, vertical=False):
    """Seeded grain streaks: dark runs with a light sheen above, and rare knots."""
    x, y, w, h = box
    r = _rng(seed, 'grain', box)
    span, depth = (h, w) if vertical else (w, h)
    for lane in range(depth):
        pos = r.randint(-6, 4)
        while pos < span:
            length = r.randint(6, 18)
            if r.random() < 0.26 * density:
                for t in range(max(0, pos), min(span, pos + length)):
                    px, py = (x + lane, y + t) if vertical else (x + t, y + lane)
                    put(img, px, py, ramp[1])
                if r.random() < 0.3 and lane > 0:
                    sx = max(0, pos + 1); ex = min(span, pos + length // 2)
                    for t in range(sx, ex):
                        px, py = (x + lane - 1, y + t) if vertical else (x + t, y + lane - 1)
                        put(img, px, py, ramp[3])
            pos += length + r.randint(5, 14)
    knots = int(span * depth / 900 * density)
    for _ in range(knots):
        kx = r.randint(x + 3, x + w - 5) if w > 8 else x + w // 2
        ky = r.randint(y + 1, y + h - 3) if h > 4 else y + h // 2
        sprite(img, kx, ky, ['.11.', '1001', '.11.'] if not vertical else ['.1.', '101', '101', '.1.'],
               {'1': ramp[1], '0': ramp[0]})


def plank(img, box, ramp=WOOD, seed=0, outline='ink_1', radius=1, vertical=False, grain=1.0,
          highlight=True, heavy='b'):
    """Oiled wood plank. Body ramp[2]; seeded grain streaks (ramp[1]) with sheen
    (ramp[3]); broken top-left highlight (ramp[4]); bottom-right shadow (ramp[0]);
    ink outline with a heavier bottom. ``outline=None`` paints a borderless
    board (use for large background fills)."""
    x, y, w, h = box
    inner = (x, y, w, h)
    if outline:
        inside = ink_outline(img, box, outline, radius, heavy=heavy, fill_colour=ramp[2])
        inner = (x + 1, y + 1, w - 2, h - 2)
    else:
        fill(img, box, ramp[2])
    if grain:
        _grain(img, (inner[0], inner[1] + 1, inner[2], max(1, inner[3] - 2)) if not vertical else
               (inner[0] + 1, inner[1], max(1, inner[2] - 2), inner[3]), ramp, seed, grain, vertical)
    if highlight:
        highlight_edge(img, (inner[0] - 1, inner[1] - 1, inner[2] + 2, inner[3] + 2), ramp[4],
                       'tl' if not vertical else 'tl', broken=5, seed=seed, inset=1)
    shadow_edge(img, (inner[0] - 1, inner[1] - 1, inner[2] + 2, inner[3] + 2), ramp[0], 'b' if not vertical else 'br', inset=1)
    return box


def planks(img, box, ramp=WOOD, seed=0, board=10, vertical=False, seams='wood_0', grain=1.0):
    """Fill ``box`` with abutting boards ``board`` px wide, divided by 1 px
    seams, each board with its own grain and highlight. No outer outline."""
    x, y, w, h = box
    span = h if not vertical else w
    pos = 0
    i = 0
    r = _rng(seed, 'planks', box)
    while pos < span:
        size = min(board + r.choice((-1, 0, 0, 1)), span - pos)
        sub = (x, y + pos, w, size) if not vertical else (x + pos, y, size, h)
        fill(img, sub, ramp[2])
        _grain(img, sub, ramp, (seed, i), grain, vertical)
        if not vertical:
            hline(img, x, x + w - 1, y + pos, ramp[3])
            if pos:
                hline(img, x, x + w - 1, y + pos - 1, seams)
        else:
            vline(img, x + pos, y, y + h - 1, ramp[3])
            if pos:
                vline(img, x + pos - 1, y, y + h - 1, seams)
        pos += size + 1
        i += 1


def parchment_panel(img, box, seed=0, outline='ink_2', radius=1, fibres=True, torn='', ramp=PARCHMENT):
    """Cream paper. Body ramp[2]; top-left inner edge ramp[3]; bottom-right inner
    edge ramp[1] then ramp[0]; soft ink_2 outline; sparse 2-3 px fibres.
    ``torn`` lists edges ('r', 'b', ...) drawn as a ragged torn edge instead."""
    x, y, w, h = box
    if outline:
        inside = ink_outline(img, box, outline, radius, fill_colour=ramp[2])
    else:
        fill(img, box, ramp[2])
    highlight_edge(img, box, ramp[3], 'tl', inset=1)
    shadow_edge(img, box, ramp[1], 'br', inset=1)
    if fibres:
        r = _rng(seed, 'fibre', box)
        for _ in range(max(1, w * h // 220)):
            fx = r.randint(x + 3, max(x + 3, x + w - 6)); fy = r.randint(y + 3, max(y + 3, y + h - 4))
            n = r.choice((2, 2, 3))
            for k in range(n):
                put(img, fx + k, fy + (1 if k == 2 else 0), ramp[1])
    for edge in torn:
        _torn_edge(img, box, edge, seed, ramp)
    return box


def _torn_edge(img, box, edge, seed, ramp):
    x, y, w, h = box
    r = _rng(seed, 'torn', edge)
    if edge in 'tb':
        yy = y if edge == 't' else y + h - 1
        inward = 1 if edge == 't' else -1
        depth = 0
        for xx in range(x, x + w):
            depth = max(0, min(3, depth + r.choice((-1, 0, 1))))
            for k in range(depth):
                put(img, xx, yy + k * inward, (0, 0, 0, 0))
            put(img, xx, yy + depth * inward, ramp[0])
            if depth < 3:
                put(img, xx, yy + (depth + 1) * inward, ramp[3])
    else:
        xx = x if edge == 'l' else x + w - 1
        inward = 1 if edge == 'l' else -1
        depth = 0
        for yy in range(y, y + h):
            depth = max(0, min(3, depth + r.choice((-1, 0, 1))))
            for k in range(depth):
                put(img, xx + k * inward, yy, (0, 0, 0, 0))
            put(img, xx + depth * inward, yy, ramp[0])


def brass_plate(img, box, rivets=True, outline='ink_1', radius=1, ramp=BRASS):
    """Brass plate: body ramp[1], lit top row ramp[2] with a 3-5 px ramp[3]
    glint near the top-left, bottom shadow ramp[0], heavy bottom outline,
    optional rivets (ramp[3] over ramp[0]) 2 px in from each corner."""
    x, y, w, h = box
    ink_outline(img, box, outline, radius, heavy='b', fill_colour=ramp[1])
    hline(img, x + 2, x + w - 3, y + 1, ramp[2])
    vline(img, x + 1, y + 2, y + h - 3, ramp[2])
    hline(img, x + 2, x + w - 2, y + h - 2, ramp[0])
    vline(img, x + w - 2, y + 2, y + h - 2, ramp[0])
    glint = min(5, max(2, w // 8))
    hline(img, x + 3, x + 3 + glint - 1, y + 1, ramp[3])
    put(img, x + 1, y + 3, ramp[3])
    if rivets and w >= 12 and h >= 9:
        for rx, ry in ((x + 2, y + 2), (x + w - 3, y + 2), (x + 2, y + h - 3), (x + w - 3, y + h - 3)):
            put(img, rx, ry, ramp[3])
            put(img, rx + (1 if rx < x + w // 2 else -1), ry + (1 if ry < y + h // 2 else -1), ramp[0])
    return box


def linen_tag(img, box, eyelet='left', seed=0, outline='ink_1', ramp=PARCHMENT, stitch='parch_0', notch=2, weave=False):
    """Linen luggage tag: clipped corners on the eyelet side, parchment-linen
    body with a running stitch 2 px inside, brass eyelet. ``eyelet`` is 'left',
    'top' or None. Returns the text box (x, y, w, h) left clear for lettering."""
    x, y, w, h = box
    inside = set()
    for j in range(h):
        for i in range(w):
            cut = False
            if eyelet == 'left':
                cut = (i + j < notch) or (i + (h - 1 - j) < notch)
            elif eyelet == 'top':
                cut = (i + j < notch) or ((w - 1 - i) + j < notch)
            else:
                cut = (i, j) in {(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)}
            if not cut:
                inside.add((i, j))
    edge = _edge_pixels(inside)
    for (i, j) in inside:
        put(img, x + i, y + j, ramp[2])
    for (i, j) in edge:
        s = _side(inside, i, j)
        put(img, x + i, y + j, 'ink_0' if ('b' in s and j == h - 1) else outline)
    # optional weave: short horizontal slubs every 4th row (large tags only)
    if weave:
        r = _rng(seed, 'weave', box)
        for j in range(4, h - 4, 4):
            i = r.randint(3, 8)
            while i < w - 5:
                hline(img, x + i, x + i + 1, y + j, ramp[1])
                i += r.randint(7, 13)
    highlight_edge(img, box, ramp[3], 't', inset=1)
    hline(img, x + 2, x + w - 2, y + h - 2, ramp[1])
    # running stitch, 2 px inside the edge
    if h >= 12 and w >= 14:
        sx0 = x + (notch + 2 if eyelet == 'left' else 2)
        stitch_line(img, sx0, y + 2, x + w - 3, y + 2, stitch, 2, 2)
        stitch_line(img, sx0, y + h - 3, x + w - 3, y + h - 3, stitch, 2, 2, phase=1)
    text = (x + 2, y + 1, w - 4, h - 2)
    if eyelet == 'left' and w >= 30:
        ex, ey = x + 3, y + h // 2 - 1
        sprite(img, ex, ey, ['.b.', 'bdB', '.B.'], {'b': BRASS[2], 'd': INK[0], 'B': BRASS[0]})
        text = (x + 7, y + 1, w - 9, h - 2)
    elif eyelet == 'top' and h >= 30:
        ex, ey = x + w // 2 - 1, y + 3
        sprite(img, ex, ey, ['.b.', 'bdb', '.B.'], {'b': BRASS[2], 'd': INK[0], 'B': BRASS[0]})
        text = (x + 2, y + 7, w - 4, h - 9)
    return text


def _blob(w, h, seed, wobble=1):
    """Organic disc-ish mask inside a w x h box (wax, blobs). Deterministic."""
    r = _rng(seed, 'blob', w, h)
    cx, cy = (w - 1) / 2, (h - 1) / 2
    rx, ry = w / 2, h / 2
    bumps = [r.choice((0, 0, 0, -1)) * wobble for _ in range(12)]
    inside = set()
    import math
    for j in range(h):
        for i in range(w):
            dx, dy = (i - cx) / rx, (j - cy) / ry
            ang = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
            b = bumps[int(ang * 12) % 12]
            lim = 1.0 + b * 0.12
            if dx * dx + dy * dy <= lim * lim * 0.98:
                inside.add((i, j))
    return inside


def wax_seal(img, cx, cy, r, ramp=BERRY, seed=0, drip=True, emblem=None, outline='ink_0'):
    """Round red wax seal centred at (cx, cy) with radius ``r`` (>=4). Blobby
    rim, pressed inner ring (r-3) lit on its lower-right, glossy top-left
    highlight, optional drip at lower-left and an emblem sprite name from
    icons.EMBLEMS ('x', 'check', 'heart', 'star', 'coin', 'leaf')."""
    size = 2 * r + 1
    x, y = cx - r, cy - r
    inside = _blob(size, size, seed)
    edge = _edge_pixels(inside)
    for (i, j) in inside:
        put(img, x + i, y + j, ramp[1])
    for (i, j) in edge:
        put(img, x + i, y + j, outline if (i + j) > size - 2 else ramp[0])
    # glossy highlight arc top-left
    for (i, j) in inside - edge:
        d = (i - r) ** 2 + (j - r) ** 2
        if (r - 2) ** 2 <= d <= (r - 1) ** 2 + 1 and i < r and j < r:
            put(img, x + i, y + j, ramp[2])
    # pressed ring
    if r >= 5:
        rr = r - 3
        for (i, j) in inside:
            d = (i - r) ** 2 + (j - r) ** 2
            if rr * rr - rr <= d <= rr * rr + rr:
                put(img, x + i, y + j, ramp[2] if (i + j) > 2 * r else ramp[0])
    if drip:
        # a short drip below the lower-left rim (extends up to 2 px under the box)
        i0 = r - max(1, r // 2)
        jb = max(j for (i, j) in inside if i == i0)
        put(img, x + i0, y + jb, ramp[1])
        put(img, x + i0, y + jb + 1, ramp[1])
        put(img, x + i0 + 1, y + jb + 1, outline)
        put(img, x + i0, y + jb + 2, outline)
        put(img, x + i0 - 1, y + jb + 1, ramp[0])
    if emblem and r >= 6:          # smaller seals cannot hold a legible emblem
        import icons  # local import: icons depends on primitives
        icons.draw_emblem(img, cx, cy, emblem, ramp)
    return (x, y, size, size)


def wax_slab(img, box, ramp=BERRY, seed=0, outline='ink_0', drips=2):
    """Rectangular red-wax slab for danger buttons: blobby top edge, glossy
    highlight band, ``drips`` short drips along the bottom. The body occupies
    box rows 0..h-3; drips may reach the last two rows."""
    x, y, w, h = box
    body_h = h - 2 if drips else h
    r = _rng(seed, 'slab', box)
    inside = rounded_mask(w, body_h, 2)
    # dents along the top edge give a poured, organic rim
    for i in range(3, w - 3):
        if r.random() < 0.12:
            inside.discard((i, 0))
    drip_cols = []
    for k in range(drips):
        dc = 4 + (k + 1) * (w - 8) // (drips + 1) + r.randint(-2, 2)
        drip_cols.append(dc)
        inside.add((dc, body_h)); inside.add((dc + 1, body_h))
        inside.add((dc, body_h + 1))
    edge = _edge_pixels(inside)
    for (i, j) in inside:
        put(img, x + i, y + j, ramp[1])
    for (i, j) in edge:
        s = _side(inside, i, j)
        put(img, x + i, y + j, outline if ('b' in s or 'r' in s) else ramp[0])
    for i in range(3, w - 3):
        if (i, 1) in inside and (i, 0) in inside and (i * 7) % 11:
            put(img, x + i, y + 1, ramp[2])
    vline(img, x + 1, y + 2, y + body_h - 4, ramp[2])
    for i in range(2, w - 2):
        if (i, body_h - 2) in inside - edge:
            put(img, x + i, y + body_h - 2, ramp[0])
    return (x + 1, y + 1, w - 2, body_h - 2)


def page_curl(img, box, corner='br', size=5, ramp=PARCHMENT, outline='ink_1', behind=None):
    """Curl the ``corner`` ('br', 'bl', 'tr', 'tl') of an already painted paper
    shape: the corner triangle beyond the fold becomes transparent, the fold
    line is inked, and the folded-back flap (the triangle mirrored across the
    fold) is drawn on the page in ramp[1] with an ink rim, a ramp[3] crease
    highlight and a ramp[0] tip. ``behind`` fills the cut corner with a colour
    instead of transparency (use it on frames/backgrounds, where a hole would
    show the world; leave None on buttons)."""
    x, y, w, h = box
    s = size
    gone = (0, 0, 0, 0) if behind is None else behind

    def at(i, j):  # i: px from the corner's vertical edge, j: from its horizontal edge
        return (x + w - 1 - i if 'r' in corner else x + i, y + h - 1 - j if 'b' in corner else y + j)

    for i in range(s):
        for j in range(s):
            if i + j < s - 1:
                put(img, *at(i, j), gone)
            elif i + j == s - 1:
                put(img, *at(i, j), outline)
    for i in range(s):
        for j in range(s):
            if i + j < s - 1:
                fi, fj = s - 1 - j, s - 1 - i
                if i == 0 or j == 0:
                    c = outline
                elif i + j == s - 2:
                    c = ramp[3]
                elif i + j <= 2:
                    c = ramp[0]
                else:
                    c = ramp[1]
                put(img, *at(fi, fj), c)
    return box


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


def well_frame(img, holes, style='stitched', depth=3, thread='parch_2', protect=(), lip='ink_1'):
    """Frame the transparent ``holes`` (Rects, Slots or (x,y,w,h) tuples) as a
    recessed inset. Rings are measured outward from the hole (Chebyshev):

    d=1  ink lip (``lip``) all round - the crisp edge of the recess
    d=2  wall: the side whose hole is below/right is in SHADOW (two ramp steps
         darker than what is underneath); the other side is LIT (one step lighter)
    d=3  stitched: running-stitch ``thread`` dashes 2-on 2-off;
         wood: a raised lip, lit on the top-left, shaded on the bottom-right

    Colours are relative to the pixels already painted, so a well reads as
    recessed on wood, parchment or linen alike. Inside ``protect`` rects only
    the d=1 lip is drawn (keeps title / inventory text bands light). Pixels
    inside any hole are never touched.
    """
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
    for (x, y, w, h) in rects:
        for py in range(y - depth, y + h + depth):
            for px in range(x - depth, x + w + depth):
                if not (0 <= px < W and 0 <= py < H) or hole[py * W + px]:
                    continue
                # Chebyshev distance to the nearest hole pixel (<= depth)
                d = None
                for k in range(1, depth + 1):
                    found = False
                    for dy in range(-k, k + 1):
                        for dx in range(-k, k + 1):
                            if max(abs(dx), abs(dy)) == k and is_hole(px + dx, py + dy):
                                found = True; break
                        if found: break
                    if found:
                        d = k; break
                if d is None:
                    continue
                shadow_side = any(is_hole(px + dx, py + dy) for dx in range(0, d + 1) for dy in range(0, d + 1)
                                  if (dx, dy) != (0, 0))
                under = bpx[px, py]
                if under[3] == 0:
                    under = WOOD[2] + (255,)
                if protected(px, py) and d > 1:
                    continue
                if d == 1:
                    put(img, px, py, lip)
                elif d == 2:
                    put(img, px, py, step(under, -2) if shadow_side else step(under, 1))
                elif d == 3:
                    if style == 'stitched':
                        horiz = is_hole(px, py + 3) or is_hole(px, py - 3)
                        k = px if horiz else py
                        if (k // 2) % 2 == 0:
                            put(img, px, py, thread)
                    else:
                        put(img, px, py, step(under, 1) if shadow_side else step(under, -1))
    return img


def stitched_well(img, holes, thread='parch_2', protect=(), depth=3):
    """Recessed well with a running-stitch border (see ``well_frame``)."""
    return well_frame(img, holes, 'stitched', depth, thread, protect)


def wood_well(img, holes, protect=(), depth=3):
    """Recessed well with a carved wood lip (see ``well_frame``)."""
    return well_frame(img, holes, 'wood', depth, protect=protect)


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
# Small details
# ---------------------------------------------------------------------------

TACK = ['.oo.', 'o32o', 'o21o', '.oo.']
TACK_SMALL = ['.3.', '321', '.1.']


def tack(img, cx, cy, ramp=BRASS, small=False):
    """Brass tack: 4x4 with ink rim (default) or 3x3 rimless. (cx, cy) is the
    top-left of the lit head pixel."""
    if small:
        sprite(img, cx - 1, cy, TACK_SMALL, {'3': ramp[3], '2': ramp[2], '1': ramp[0]})
    else:
        sprite(img, cx - 1, cy - 1, TACK, {'o': INK[1], '3': ramp[3], '2': ramp[2], '1': ramp[0]})


LEAF = ['...ooo', '..o22o', '.o2m2o', 'o2m1o.', 'om1o..', 'oo....']
LEAF_SMALL = ['..oo', '.o2o', 'om1o', 'oo..']


def leaf(img, x, y, direction='ne', ramp=SAGE, small=False):
    """A hand-drawn leaf (sage), stem at the opposite corner of ``direction``
    ('ne', 'nw', 'se', 'sw')."""
    rows = LEAF_SMALL if small else LEAF
    sprite(img, x, y, rows, {'o': ramp[0], '2': ramp[2], '1': ramp[1], 'm': ramp[0]},
           flip_x='w' in direction, flip_y='s' in direction)


MUG = [
    '.oooooo...',
    'o3cccc3o..',
    'oallllaooo',
    'oalaaaao.o',
    'oalaaaao.o',
    'oaaaaado.o',
    'oadaadaooo',
    'oddddddo..',
    '.oooooo...',
]
STEAM = ['.s..s', 's..s.', '.s..s', '..s..']


def mug(img, x, y, ramp=EMBER, steam=True, seed=0):
    """Steaming mug, 10x9 (+4 rows of steam above when ``steam``). Glaze uses
    the given accent ramp; coffee is wood_0; rim highlight parch_3."""
    key = {'o': INK[1], '3': PARCHMENT[3], 'c': WOOD[0], 'a': ramp[1], 'l': ramp[2], 'd': ramp[0]}
    if steam:
        r = _rng(seed, 'steam')
        sprite(img, x + 1 + r.randint(0, 1), y - 4, STEAM, {'s': ASH[2]})
    sprite(img, x, y, MUG, key)


LANTERN = [
    '...oo...',
    '..o33o..',
    '.oooooo.',
    'o2oggo2o',
    'o2gGGg2o',
    'o2gGGg2o',
    'o2oggo2o',
    '.oooooo.',
    '..o11o..',
]


def lantern(img, x, y, ramp=BRASS, glow=EMBER):
    """Small hanging lantern (8x9): brass cage, warm glass panes."""
    sprite(img, x, y, LANTERN, {'o': INK[1], '3': ramp[3], '2': ramp[1], '1': ramp[0],
                                'g': glow[1], 'G': glow[2]})


def lantern_glow_ring(img, cx, cy, r, strength=1, ring=None):
    """Warm light around (cx, cy). Opaque pixels move ``strength`` steps
    lighter along their own ramp in three hand-dithered bands: solid inside
    3r/5, a 50 % checker to 3r/4, a sparse 25 % Bayer to r. The falloff is
    dither, never a gradient. With ``ring=k`` only a 1 px ring at radius k is
    lit in ember (used to show an expanding pulse). Ink pixels and alpha are
    never changed."""
    base = img.copy()
    bpx = base.load()
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
                    put(img, x, y, _glow_colour(p))
                continue
            if d2 <= (3 * r // 5) ** 2:
                lit = True
            elif d2 <= (3 * r // 4) ** 2:
                lit = (x + y) % 2 == 0
            elif d2 <= r * r:
                lit = BAYER4[y % 4][x % 4] < 4
            else:
                lit = False
            if lit:
                put(img, x, y, step(p, strength))


def _glow_colour(p):
    """Lantern light that always contrasts with the surface it lands on:
    ember_1 on light paper/linen, ember_2 on brass and mid wood, ember_1 on
    dark wood and wax."""
    lum = luminance(p)
    return EMBER[1] if lum > 165 else EMBER[2] if lum > 95 else EMBER[1]


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


# ---------------------------------------------------------------------------
# Shared state transforms. Alpha is never changed by any of these.
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


_DISABLED_LEVELS = [(60, INK[1]), (95, INK[2]), (128, ASH[0]), (172, ASH[1]), (999, ASH[2])]


def make_disabled(img, hatch=False):
    """Desaturate and dim onto the inert ramp ink_1 / ink_2 / ash_0..2 by
    luminance, compressing highlights (no glints survive). ``hatch`` adds a
    sparse 45-degree ash_0 hatch on light interior pixels. Alpha unchanged."""
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            p = px[x, y]
            if p[3] == 0:
                continue
            lum = luminance(p)
            for lim, col in _DISABLED_LEVELS:
                if lum < lim:
                    px[x, y] = col + (p[3],)
                    break
            if hatch and lum >= 172 and (x + y) % 6 == 0:
                px[x, y] = ASH[1] + (p[3],)
    return out


def make_selected(img, sparkle=True):
    """Warm highlight + raised emphasis: every non-ink colour moves one step
    lighter on its own ramp; the first interior ring is lit with ember_2 on the
    top/left and deepened one step on the bottom/right; optional 3 px brass
    sparkle in the top-right interior. Ink (outlines, lettering) is kept.
    Alpha unchanged."""
    out = img.copy()
    px = out.load()
    dist = edge_distance(out, 2)
    w, h = out.size
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            if p[3] == 0 or _is_ink(p):
                continue
            d = dist[y][x]
            rp = ramp_of(p)
            if rp and rp[0] == 'parchment':
                c = {3: PARCHMENT[3], 2: BRASS[3], 1: BRASS[2], 0: BRASS[1]}[rp[1]]
            else:
                c = step(p, 1)
            if d == 1:
                up = dist[y - 1][x] if y > 0 else 0
                left = dist[y][x - 1] if x > 0 else 0
                down = dist[y + 1][x] if y < h - 1 else 0
                right = dist[y][x + 1] if x < w - 1 else 0
                if up == 0 or left == 0:
                    c = EMBER[2] if luminance(p) < 165 else EMBER[1]
                elif down == 0 or right == 0:
                    c = step(p, -1)
            px[x, y] = c + (p[3],)
    if sparkle and w >= 14 and h >= 10:
        sx, sy = w - 5, 2
        for (dx, dy) in ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2)):
            q = px[sx + dx, sy + dy]
            if q[3] and not _is_ink(q) and dist[sy + dy][sx + dx] >= 1:
                px[sx + dx, sy + dy] = (BRASS[3] if (dx, dy) == (1, 1) else EMBER[2]) + (q[3],)
    return out


_PULSE_DEPTHS = (3, 2, 1)   # designed ring depth (px in from the edge) for pulse_1..3


def pulse_depths(dist, protect=None):
    """Ring depths (pulse_1, pulse_2, pulse_3) that stay clear of ``protect``.

    The designed rings sit 3, 2 and 1 px in from the edge. When protected
    pixels (lettering and its 1 px halo) come closer to the edge than that -
    typical on 18 px tall buttons - the ring is compressed into the free band
    between the edge and the lettering, so it can never cross a glyph."""
    if not protect:
        return _PULSE_DEPTHS
    near = min((dist[y][x] for (x, y) in protect if 0 <= y < len(dist) and 0 <= x < len(dist[0])
                and dist[y][x] is not None), default=99)
    room = max(1, min(3, near - 1))
    return {3: (3, 2, 1), 2: (2, 1, 1), 1: (1, 1, 1)}[room]


def make_pulse(img, n, protect=None):
    """Lantern-glow ring, frame ``n`` of 3, expanding outward then fading:

    pulse_1  bright ring 3 px in from the edge; on unlettered faces the core
             also warms one ramp step
    pulse_2  ring 2 px in; afterglow (one step lighter) where the ring was
    pulse_3  faint checker-dithered ring 1 px in, afterglow at 2 px; next
             frame the server shows the resting state

    ``protect`` is a set of (x, y) pixels that must not change - pass the
    lettering mask (``compose.lettering_mask``), which includes a 1 px halo so
    letters keep their shadow and contrast. Rings are compressed toward the
    edge when lettering is closer than 4 px (``pulse_depths``). The pulse_1
    core warm-up only happens on unlettered faces, so the area round the
    letters keeps its normal contrast. Ring colour is ember_1 on light
    paper and on dark wood/wax, ember_2 on brass and mid wood. Ink pixels and
    alpha never change."""
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
    for y in range(out.height):
        for x in range(out.width):
            p = px[x, y]
            if p[3] == 0 or _is_ink(p) or (x, y) in protect:
                continue
            d = dist[y][x]
            c = None
            if d == ring_d:
                if not faint or (x + y) % 2 == 0:
                    c = _glow_colour(p)
            elif after_d is not None and d == after_d:
                c = step(p, 1)
            elif n == 1 and d > ring_d and not protect:
                c = step(p, 1)          # unlettered faces (icons, seals): the core warms
            if c is not None:
                px[x, y] = c + (p[3],)
    return out


_WAX_TO_ASH = {BERRY[0]: ASH[0], BERRY[1]: ASH[1], BERRY[2]: ASH[2]}


def make_disabled_seal(img):
    """Disabled state for wax seals (the 18x18 close control). The plain
    luminance map turns berry_1 wax into ink_2, as dark as the pressed X, so
    the seal read as a slashed brown disc. Here the wax cools to grey
    (berry_0/1/2 -> ash_0/1/2), the X and the deepest outline keep ink_0, and
    every other colour follows ``make_disabled``. Alpha unchanged."""
    out = make_disabled(img)
    src, px = img.load(), out.load()
    for y in range(out.height):
        for x in range(out.width):
            p = src[x, y]
            if not p[3]:
                continue
            rgb = tuple(p[:3])
            if rgb in _WAX_TO_ASH:
                px[x, y] = _WAX_TO_ASH[rgb] + (p[3],)
            elif rgb == INK[0]:
                px[x, y] = INK[0] + (p[3],)
    return out


def make_state(img, state, protect=None, seal=False):
    """Apply the shared transform for a state name to a painted normal frame.
    ``protect``: lettering pixels pulses must not touch. ``seal``: the image is
    a wax-seal control (disabled uses ``make_disabled_seal``)."""
    if state == 'normal':
        return img.copy()
    if state == 'disabled':
        return make_disabled_seal(img) if seal else make_disabled(img)
    if state == 'selected':
        return make_selected(img)
    if state.startswith('pulse_'):
        return make_pulse(img, int(state[-1]), protect)
    raise ValueError(f'unknown state {state!r}')
