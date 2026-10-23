"""Pixel primitives for the Faithful theme: the vanilla inventory language.

Every function takes a PIL RGBA image and integer coordinates, draws only
Faithful palette colours, and is deterministic: anything that varies (stone
flecks on a button face) is driven by an explicit ``seed``, so the same call
always produces the same pixels. Boxes are (x, y, w, h).

Groups
------
pixels      put, get, fill, hline, vline, line, sprite, sprite_size, rounded_mask
edges       bevel (raised: light top/left, dark bottom/right), inset (recessed:
            the reverse), ink_outline
materials   bevel_panel (the light grey container panel), stone_texture,
            stone_button (plain / gold / red), flat_plate (recessed info
            plate), inset_box, accent_line, arrow_glyph, pictogram,
            pictogram_tile
backdrops   remember_backdrop, backdrop_pixel, reveal, restore_cuts: kept for
            API parity with the Soulrend toolkit; no Faithful helper cuts an
            edge, so restore_cuts normally has nothing to undo
wells       well_frame, inset_well (the vanilla-style inset slot: dark top/left,
            white bottom/right, transparent 20x20 centre), merge_holes
            (never paints inside a hole)
states      make_disabled, make_selected, make_pulse, pulse_depths, make_state,
            edge_distance (alpha never changes; selected never changes a
            glyph or shadow pixel, pulses never change a glyph, its shadow or
            its 1 px halo; disabled recolours glyphs in place)

No pixel here is copied, traced or sampled from Minecraft's textures; the
shapes are drawn from a verbal description of the vanilla GUI's general look.

Licence: MIT.
"""
from __future__ import annotations

import random
import sys as _sys
import weakref
from collections import deque
from pathlib import Path as _Path

if __name__ == 'primitives':                 # imported by its plain name from tools/faithful
    # one module object per process (see palette.py)
    if 'faithful.primitives' in _sys.modules:
        _sys.modules[__name__] = _sys.modules['faithful.primitives']
    else:
        _sys.modules['faithful.primitives'] = _sys.modules[__name__]
_TOOLS = _Path(__file__).resolve().parents[1]
if str(_TOOLS) not in _sys.path:
    _sys.path.append(str(_TOOLS))

from faithful.palette import (BLUE, GOLD, GREEN, GREY, INK, PANEL_RAMP, PURPLE, RED, RUST,  # noqa: E402
                              luminance, ramp_of, rgba, step)

# One colour key shared by every ASCII sprite in the theme (primitives, icons,
# pictograms). '.' and ' ' are transparent.
SK = {
    'O': INK[0], 'o': INK[1],
    'a': GREY[0], 'b': GREY[1], 'c': GREY[2], 'd': GREY[3], 'e': GREY[4], 'f': GREY[5], 'g': GREY[6],
    'W': GREY[7],
    'u': GREEN[0], 'v': GREEN[1], 'V': GREEN[2],
    'r': RED[0], 's': RED[1], 't': RED[2],
    'h': GOLD[0], 'H': GOLD[1], 'Y': GOLD[2],
    'm': BLUE[0], 'n': BLUE[1], 'N': BLUE[2],
    'p': PURPLE[0], 'P': PURPLE[1],
    'R': RUST[0],
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
    Ragged rows are padded on the right. Unknown characters raise. Returns
    the set of image pixels drawn."""
    key = SK if key is None else {**SK, **key}
    rows = list(rows)
    width = max(len(r) for r in rows) if rows else 0
    rows = [r.ljust(width, '.') for r in rows]
    if flip_y:
        rows = rows[::-1]
    drawn = set()
    for j, row in enumerate(rows):
        if flip_x:
            row = row[::-1]
        for i, ch in enumerate(row):
            if ch in '. ':
                continue
            if ch not in key:
                raise KeyError(f'sprite character {ch!r} has no colour in key')
            put(img, x + i, y + j, key[ch])
            drawn.add((x + i, y + j))
    return drawn


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
    """Set of (x, y) inside a w x h box with pixel-art rounded corners
    (radius 0-3: 0, 1, 3 or 6 pixels cut per corner)."""
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


# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------

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


def inset(img, box, dark=GREY[0], light=GREY[7], mid=None):
    """Recessed 1 px edge on the outer ring of ``box``: ``dark`` on the
    top/left (the inner shadow), ``light`` on the bottom/right (the inner
    highlight); the two mixed corners take ``mid`` (default: leave them)."""
    x, y, w, h = box
    hline(img, x, x + w - 2, y, dark)
    vline(img, x, y, y + h - 2, dark)
    hline(img, x + 1, x + w - 1, y + h - 1, light)
    vline(img, x + w - 1, y + 1, y + h - 1, light)
    if mid is not None:
        put(img, x + w - 1, y, mid)
        put(img, x, y + h - 1, mid)


def ink_outline(img, box, colour='ink_0', radius=1, fill_colour=None):
    """Rounded 1 px outline around ``box`` (vanilla panels and buttons use
    pure black). Returns the inside pixel set (box-local)."""
    x, y, w, h = box
    inside = rounded_mask(w, h, radius)
    edge = _edge_pixels(inside)
    if fill_colour is not None:
        for (i, j) in inside - edge:
            put(img, x + i, y + j, fill_colour)
    for (i, j) in edge:
        put(img, x + i, y + j, colour)
    return inside


def _shape_bevel(img, box, inside, light, dark, depth=1):
    """Raised bevel ``depth`` px deep inside a rounded shape: pixels whose
    top or left neighbour (within ``depth``) is outline get ``light``, whose
    bottom or right neighbour is outline get ``dark``; mixed corners keep
    their fill."""
    x, y, w, h = box
    edge = _edge_pixels(inside)
    for (i, j) in inside - edge:
        tl = any((i, j - k) in edge or (i - k, j) in edge for k in range(1, depth + 1))
        br = any((i, j + k) in edge or (i + k, j) in edge for k in range(1, depth + 1))
        if tl and not br:
            put(img, x + i, y + j, light)
        elif br and not tl:
            put(img, x + i, y + j, dark)


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

def bevel_panel(img, box, ramp=None, radius=2, corner_pixels=True):
    """The vanilla-style container panel: a ``ramp[0]`` (black) outline with
    radius-``radius`` notched corners, a flat ``ramp[2]`` (light grey) body, a
    1 px ``ramp[3]`` (white) bevel on the top and left and a 1 px ``ramp[1]``
    (dark grey) bevel on the bottom and right. ``corner_pixels`` adds the
    inner corner pixel of each bevel (top-left white, bottom-right dark) so
    the rounded corner reads chunky, not thin. Returns the flat inner box."""
    ramp = ramp or PANEL_RAMP
    x, y, w, h = box
    inside = ink_outline(img, box, ramp[0], radius=radius, fill_colour=ramp[2])
    _shape_bevel(img, box, inside, ramp[3], ramp[1])
    if corner_pixels and radius >= 2 and w >= 8 and h >= 8:
        put(img, x + 2, y + 2, ramp[3])
        put(img, x + w - 3, y + h - 3, ramp[1])
    return (x + 2, y + 2, w - 4, h - 4)


FLECK_AREA = 50              # one fleck per this many face pixels, on every button


def stone_texture(img, box, seed=0, face=GREY[3], dark=GREY[2], light=GREY[4], density=1.0):
    """Sparse stone flecks on a flat button face: short horizontal runs of
    ``dark`` (lengths cycle 1, 2, 2, 3) with a single ``light`` pixel
    above-left of every other fleck (none when ``light`` is None). The fleck
    COUNT is fixed by area, ``round(w * h / FLECK_AREA * density)``, and only
    their placement depends on ``seed``: the cells of a 7 x 4 jittered grid
    are shuffled and the first ``count`` used, so two buttons of one size
    are equally textured whatever their seed. Only pixels that still hold
    ``face`` change, so lettering and bevels are never touched."""
    x, y, w, h = box
    r = _rng(seed, 'stone', box)
    face = tuple(face[:3])
    cells = [(gx, gy) for gy in range(y + 1, y + h - 1, 4)
             for gx in range(x + 1 + (gy // 4 % 2) * 3, x + w - 1, 7)]
    r.shuffle(cells)
    count = min(len(cells), round(w * h / FLECK_AREA * density))
    for i, (gx, gy) in enumerate(cells[:count]):
        px = gx + r.randint(0, 3)
        py = gy + r.randint(0, 2)
        ln = (1, 2, 2, 3)[i % 4]
        for k in range(ln):
            if x <= px + k < x + w and y <= py < y + h and get(img, px + k, py)[:3] == face:
                put(img, px + k, py, dark)
        if light is not None and i % 2 == 0 and x <= px - 1 and y <= py - 1 \
                and get(img, px - 1, py - 1)[:3] == face:
            put(img, px - 1, py - 1, light)


STONE_KINDS = {
    #          outline   top/left light  bottom/right dark  face     fleck dark  fleck light
    'plain':  (INK[0],   GREY[5],        GREY[1],           GREY[3], GREY[2],    GREY[4]),
    'gold':   (INK[0],   GOLD[2],        GREY[1],           GREY[3], GREY[2],    GREY[4]),
    'red':    (INK[0],   RED[2],         RED[0],            RED[1],  RUST[0],    None),
}


def stone_button(img, box, kind='plain', seed=0, radius=1, texture=True):
    """A vanilla-style grey stone button: black outline (radius-1 corners),
    a 1 px raised bevel (light top/left, dark bottom/right), a flat face with
    sparse stone flecks (the same count per area on every kind; on red the
    fleck is ``rust_0``, as far below the face as grey_2 is below grey_3, and
    there is no light fleck). ``kind`` 'plain' (secondary), 'gold' (primary: the
    top/left bevel is gold and a second gold row sits under the top edge on
    plates at least 26 px wide) or 'red' (danger: red face, red bevel).
    Returns the face box (inside the bevel)."""
    x, y, w, h = box
    outline, light, dark, face, fd, fl = STONE_KINDS[kind]
    inside = ink_outline(img, box, outline, radius=radius, fill_colour=face)
    _shape_bevel(img, box, inside, light, dark)
    if kind == 'gold' and w >= 26 and h >= 12:
        # the gold catches the light: a broken second row under the top bevel
        for xx in range(x + 2, x + w - 3):
            if (xx - x) % 6 not in (4, 5):
                put(img, xx, y + 2, GOLD[1])
        put(img, x + 2, y + 3, GOLD[1])
    if texture and w >= 10 and h >= 10:
        stone_texture(img, (x + 2, y + (3 if kind == 'gold' and w >= 26 and h >= 12 else 2), w - 4, h - 4),
                      seed, face, fd, fl)
    return (x + 2, y + 2, w - 4, h - 4)


def flat_plate(img, box, face=GREY[5], dark=GREY[1], light=GREY[7]):
    """The read-only info plate: a flat ``face`` recessed into the panel. No
    outline and no raised bevel: the outer ring is ``dark`` on the top/left and
    ``light`` on the bottom/right (the reverse of a button), so it reads as a
    label, never as something to press. Returns the inner box."""
    x, y, w, h = box
    fill(img, box, face)
    inset(img, box, dark, light, mid=face)
    return (x + 1, y + 1, w - 2, h - 2)


def inset_box(img, box, fill_colour=GREY[4], dark=GREY[0], light=GREY[7]):
    """A recessed square in the slot style (dark top/left, white bottom/right,
    ``fill_colour`` inside, mid-grey mixed corners). Used for pictogram tiles
    on frames and static cells; NOT for item wells (those stay transparent)."""
    x, y, w, h = box
    if fill_colour is not None:
        fill(img, (x + 1, y + 1, w - 2, h - 2), fill_colour)
    inset(img, box, dark, light, mid=GREY[4])
    return (x + 1, y + 1, w - 2, h - 2)


def accent_line(img, x0, x1, y, colour, ends=None):
    """The family accent: a single 1 px line in ``colour`` from x0 to x1,
    optionally capped by one ``ends`` pixel at each end."""
    hline(img, x0, x1, y, colour)
    if ends is not None:
        put(img, x0, y, ends)
        put(img, x1, y, ends)


ARROWS = {
    'right': ['#...', '##..', '###.', '####', '###.', '##..', '#...'],
    'left':  ['...#', '..##', '.###', '####', '.###', '..##', '...#'],
    'up':    ['...#...', '..###..', '.#####.', '#######'],
    'down':  ['#######', '.#####.', '..###..', '...#...'],
}


def arrow_size(direction='right'):
    return sprite_size(ARROWS[direction])


def arrow_glyph(img, x, y, direction='right', colour='grey_7', shadow='ink_1'):
    """A small original arrow glyph (a solid 4x7 triangle for right/left,
    7x4 for up/down) with its top-left at (x, y), drawn like lettering:
    ``colour`` with a (+1, +1) ``shadow``. Returns the glyph pixel set (not
    the shadow)."""
    rows = ARROWS[direction]
    pts = {(x + i, y + j) for j, r in enumerate(rows) for i, c in enumerate(r) if c == '#'}
    if shadow is not None:
        for (px, py) in sorted(pts):
            if (px + 1, py + 1) not in pts:
                put(img, px + 1, py + 1, shadow)
    for (px, py) in sorted(pts):
        put(img, px, py, colour)
    return pts


def pictogram(img, name, x, y):
    """Draw family pictogram ``name`` (icons.PICTOGRAMS) with its top-left at
    (x, y). Returns (w, h). Pictograms belong in static decorative cells and
    on frames only, never in an item well."""
    from faithful import icons
    return icons.draw_pictogram(img, name, x, y)


def pictogram_tile(img, box, name, fill_colour=GREY[4]):
    """A recessed tile (``inset_box``) with pictogram ``name`` centred in it.
    ``name`` None leaves the tile empty. Returns the inner box."""
    from faithful import icons
    inner = inset_box(img, box, fill_colour)
    if name:
        w, h = icons.pictogram_size(name)
        icons.draw_pictogram(img, name, inner[0] + (inner[2] - w) // 2, inner[1] + (inner[3] - h) // 2)
    return inner


BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def dither_patch(img, box, colour, density=0.25, only_opaque=True, phase=(0, 0)):
    """Ordered (4x4 Bayer) dither of ``colour`` over ``box`` at ``density``
    (0..1). The Faithful look is flat: use only for a deliberate hand-placed
    transition, never as texture."""
    x, y, w, h = box
    t = int(density * 16 + 0.5)
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if BAYER4[(yy + phase[1]) % 4][(xx + phase[0]) % 4] < t:
                if only_opaque and get(img, xx, yy)[3] == 0:
                    continue
                put(img, xx, yy, colour)


# ---------------------------------------------------------------------------
# Backdrops and cuts (API parity with tools/soulrend; Faithful never cuts)
# ---------------------------------------------------------------------------

_BACKDROPS = {}     # id(img) -> (weakref to img, [(box, snapshot crop), ...])
_CUTS = {}          # id(img) -> (weakref to img, [(x, y, before RGBA, after RGBA), ...])


def remember_backdrop(img, box=None):
    """Record what is painted under ``box`` (default: the whole image) before a
    surface is painted there, so ``reveal`` can show it again. Returns the crop."""
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
    """Show ``under`` (a snapshot) or the remembered backdrop at (x, y), else
    alpha 0. Never punches a hole through a surface whose backdrop is known."""
    if not (0 <= x < img.width and 0 <= y < img.height):
        return
    c = under.getpixel((x, y)) if under is not None else (backdrop_pixel(img, x, y) or (0, 0, 0, 0))
    img.putpixel((x, y), c)


def restore_cuts(img, x0, x1, y0=None, y1=None):
    """Undo recorded edge cuts in columns x0 .. x1 (rows y0 .. y1). Faithful
    helpers never cut an edge, so this normally returns 0; it exists so code
    ported from the Soulrend toolkit keeps working."""
    entry = _CUTS.get(id(img))
    if entry is None or entry[0]() is not img:
        return 0
    px = img.load()
    keep, n = [], 0
    for cell in entry[1]:
        x, y, before, after = cell
        inside = x0 <= x <= x1 and (y0 is None or y0 <= y <= y1)
        if inside and px[x, y] == after:
            px[x, y] = before
            n += 1
        elif not inside:
            keep.append(cell)
    entry[1][:] = keep
    return n


# ---------------------------------------------------------------------------
# Item wells: the vanilla-style inset round a transparent hole
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


def well_frame(img, holes, dark=GREY[0], light=GREY[7], mid=GREY[4], protect=(), protect_colour=None, clear=()):
    """Frame the transparent ``holes`` (Rects, Slots or (x,y,w,h) tuples) as a
    vanilla-style inset slot: the 1 px ring just outside the hole is ``dark``
    where the hole lies below or right of it (the top and left walls: the
    inner shadow), ``light`` where the hole lies above or left of it (the
    bottom and right walls: the inner highlight) and ``mid`` on the two mixed
    corners. The top-left outer corner continues the shadow, the
    bottom-right outer corner the highlight. Adjacent clearances overlap (18
    px pitch, 20 px clearance), so a grid becomes one merged inset tray.
    Inside ``protect`` rects the dark run is drawn in ``protect_colour``
    (default: left as it was), so live text rows stay light; inside ``clear``
    rects nothing at all is drawn (the title zone, rows 5-14). Pixels inside
    any hole are never touched. Returns the ring pixel set."""
    rects = _as_rects(holes)
    W, H = img.size
    hole = bytearray(W * H)
    for (x, y, w, h) in rects:
        for yy in range(max(0, y), min(H, y + h)):
            for xx in range(max(0, x), min(W, x + w)):
                hole[yy * W + xx] = 1
    prot = _as_rects(protect)
    clr = _as_rects(clear)

    def is_hole(px, py):
        return 0 <= px < W and 0 <= py < H and hole[py * W + px]

    ring = set()
    for (x, y, w, h) in rects:
        for py in range(y - 1, y + h + 1):
            for px in range(x - 1, x + w + 1):
                if not (0 <= px < W and 0 <= py < H) or hole[py * W + px]:
                    continue
                t = is_hole(px, py + 1)        # hole below: top wall
                l_ = is_hole(px + 1, py)       # hole right: left wall
                b = is_hole(px, py - 1)        # hole above: bottom wall
                r = is_hole(px - 1, py)        # hole left: right wall
                if not (t or l_ or b or r):
                    if is_hole(px + 1, py + 1):
                        colour = dark          # top-left outer corner
                    elif is_hole(px - 1, py - 1):
                        colour = light         # bottom-right outer corner
                    elif is_hole(px + 1, py - 1) or is_hole(px - 1, py + 1):
                        colour = mid
                    else:
                        continue
                elif (t or l_) and not (b or r):
                    colour = dark
                elif (b or r) and not (t or l_):
                    colour = light
                else:
                    colour = mid
                if any(qx <= px < qx + qw and qy <= py < qy + qh for (qx, qy, qw, qh) in clr):
                    continue
                if colour == dark and any(qx <= px < qx + qw and qy <= py < qy + qh for (qx, qy, qw, qh) in prot):
                    if protect_colour is None:
                        continue
                    colour = protect_colour
                put(img, px, py, colour)
                ring.add((px, py))
    return ring


def inset_well(img, holes, protect=(), protect_colour=None, clear=()):
    """The Faithful item well (see ``well_frame``)."""
    return well_frame(img, holes, protect=protect, protect_colour=protect_colour, clear=clear)


def tray_top_walls(img, holes, dark=GREY[0], sides='t'):
    """The shadow-wall pixels of the inset trays round ``holes`` that
    currently hold ``dark`` (the inner shadow ``well_frame`` drew): with
    ``sides`` 't' every pixel directly above a hole plus the top-left outer
    corner of each tray; 'tl' adds every pixel directly left of a hole (the
    whole L-shaped inner shadow). Returns them sorted by (y, x)."""
    rects = _as_rects(holes)
    W, H = img.size
    hole = set()
    for (x, y, w, h) in rects:
        hole |= {(xx, yy) for yy in range(max(0, y), min(H, y + h)) for xx in range(max(0, x), min(W, x + w))}
    dark = tuple(dark[:3])
    out = set()
    for (hx, hy) in hole:
        for q in ((hx, hy - 1), (hx - 1, hy - 1)) + (((hx - 1, hy),) if 'l' in sides else ()):
            if q in hole or not (0 <= q[0] < W and 0 <= q[1] < H):
                continue
            if q == (hx - 1, hy - 1) and ((hx - 1, hy) in hole or (hx, hy - 1) in hole):
                continue                       # only the true outer corner, not an inner step
            p = img.getpixel(q)
            if p[3] and tuple(p[:3]) == dark:
                out.add(q)
    return sorted(out, key=lambda q: (q[1], q[0]))


def tint_tray_walls(img, holes, colour, dash=0, dark=GREY[0], sides='t'):
    """The family accent: recolour the top wall of every inset tray (see
    ``tray_top_walls``) in ``colour``; with ``dash`` > 0 only alternate runs
    of ``dash`` px take the colour and the rest keep the grey shadow (a
    broken wall: offline / inactive). Only pixels that still hold the
    ``dark`` shadow change, so tiles, buttons and the clear title zone are
    never touched. Returns the pixels recoloured."""
    done = []
    for (x, y) in tray_top_walls(img, holes, dark, sides):
        if dash and ((x + y) // dash) % 2:
            continue
        put(img, x, y, colour)
        done.append((x, y))
    return done


socket_well = inset_well        # Soulrend-compatible name
carved_well = inset_well


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
# Shared state transforms. Alpha never changes.
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


def _side(dist, x, y):
    """'tl' when the pixel's top or left neighbour is closer to the edge,
    'br' when its bottom or right one is, '' when both or neither."""
    h, w = len(dist), len(dist[0])
    d = dist[y][x]

    def closer(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h):
            return True
        nd = dist[ny][nx]
        return nd is None or nd < d
    tl = closer(x, y - 1) or closer(x - 1, y)
    br = closer(x, y + 1) or closer(x + 1, y)
    if tl and not br:
        return 'tl'
    if br and not tl:
        return 'br'
    return ''


def make_disabled(img, lettering=None, extras=None, cracks=False, seed=0):
    """Vanilla-style disabled: a flat dark grey face, clearly inert.

    * ink_0 (the black outline and sprite outlines) and non-lettering ink_1
      pixels (label shadows) are kept;
    * every pixel in ``lettering`` (the glyph pixels from
      ``compose.lettering_mask(halo=False)``) and ``extras`` (arrow, X, icon)
      keeps its position and alpha and becomes the disabled label grey
      ``grey_5`` (black ink_0 stays: an icon keeps its outline and becomes a
      grey silhouette); dark ink_1 lettering on an info plate turns
      ``grey_5`` too;
    * the outer ring of an un-outlined shape (the info plate's recessed rim)
      becomes ``grey_1``;
    * every other pixel becomes the flat ``grey_0`` face, except white ones
      (an icon's highlights, the close X), which become ``grey_5``.

    Bevels, gold, red, green and stone flecks all go flat. No cracks: the
    Faithful disabled state is vanilla's flat button, so ``cracks`` is
    accepted for API parity and ignored. Alpha unchanged."""
    glyphs = set(lettering or ()) | set(extras or ())
    out = img.copy()
    px = out.load()
    dist = edge_distance(out, 1)
    for y in range(out.height):
        for x in range(out.width):
            p = px[x, y]
            if p[3] == 0:
                continue
            rgb = tuple(p[:3])
            if (x, y) in glyphs:
                c = rgb if _is_ink(p) and rgb == INK[0] else GREY[5]
            elif _is_ink(p):
                continue
            elif dist[y][x] == 0:
                c = GREY[1]
            elif luminance(rgb) >= 240:
                c = GREY[5]
            else:
                c = GREY[0]
            px[x, y] = c + (p[3],)
    return out


# Face colours that turn green when selected (stone face, flecks, plate face).
_SELECT_FACE = {GREY[2]: GREEN[0], GREY[3]: GREEN[1], GREY[4]: GREEN[2], GREY[5]: GREEN[2]}


def make_selected(img, protect=None, sparkle=False):
    """Selected: a green-tinted face with a brighter bevel.

    Outside ``protect`` (the lettering footprint: glyph and shadow pixels;
    see ``compose.button_states``): the stone face, its flecks and the info
    plate face turn green (grey_2/3/4/5 -> green_0/1/2/2); on the first
    interior ring the top/left bevel turns white and the bottom/right bevel
    green_0; an un-outlined rim (the info plate) darkens to green_0 where it
    was dark; every other non-ink colour (gold, red, blue, icon greys) moves
    one step lighter on its own ramp. Ink never changes. Alpha unchanged.
    ``sparkle`` is accepted for API parity and ignored."""
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
            rgb = tuple(p[:3])
            d = dist[y][x]
            if d == 0:
                c = GREEN[0] if luminance(rgb) < 128 else rgb
            elif d == 1 and _side(dist, x, y) == 'tl':
                c = GREY[7]
            elif d == 1 and _side(dist, x, y) == 'br':
                c = GREEN[0]
            elif rgb in _SELECT_FACE:
                c = _SELECT_FACE[rgb]
            else:
                c = step(rgb, 1)
            px[x, y] = c + (p[3],)
    return out


def pulse_depths(dist, protect=None):
    """Ring depths (bevel ring, face ring) the pulse may use, clear of
    ``protect``: normally (1, 2). Kept as a function for API parity with the
    Soulrend toolkit; the pulse simply skips protected pixels."""
    return (1, 2)


def _brighten(rgb):
    """Face highlight for pulse_2: two steps lighter on its own ramp (white
    stays white), so the peak frame reads clearly brighter than pulse_1."""
    return step(rgb, 2)


def pulse_protect(img, protect=None, keep=None):
    """The pixels a pulse must leave alone. Normally ``protect`` (glyphs,
    shadow and their 1 px halo). On an un-outlined shape (the recessed info
    plate, whose outer ring is not black ink) the halo is NOT applied on the
    first interior ring, so the white ring stays continuous where a label's
    halo crosses it; there only ``keep`` (the glyph and shadow footprint,
    default: ``protect``) is respected, so lettering is still untouched."""
    protect = set(protect or ())
    keep = protect if keep is None else set(keep)
    dist = edge_distance(img, 1)
    w, h = img.size
    px = img.load()
    edge = [(x, y) for y in range(h) for x in range(w) if dist[y][x] == 0]
    if edge and not any(_is_ink(px[x, y]) for (x, y) in edge):
        ring1 = {(x, y) for y in range(h) for x in range(w) if dist[y][x] == 1}
        return (protect - ring1) | (keep & ring1)
    return protect


def make_pulse(img, n, protect=None, keep=None):
    """Pulse feedback, frame ``n`` of 3: the bevel brightens, the light
    spreads onto the face, then it fades back to rest.

    pulse_1  the first interior ring (the bevel) turns white all round
    pulse_2  the bevel stays white and the next ring (the outer face ring)
             moves two steps lighter on its own ramp: the face highlight
    pulse_3  fading: the bevel ring is white on alternate pixels only (a
             checker), the face is back at rest; the next frame is the
             resting state

    ``protect`` (lettering glyphs, shadow and their 1 px halo, from
    ``compose.state_masks``) never changes, except that on an un-outlined
    plate the halo does not interrupt the first ring (``pulse_protect``;
    ``keep``, the glyph and shadow footprint, always holds); ink and alpha
    never change.
    When nothing on the face ring can brighten (all protected), pulse_2
    paints its bottom/right bevel run grey_6 instead of white so the three
    frames always differ."""
    if n not in (1, 2, 3):
        raise ValueError('pulse frame must be 1, 2 or 3')
    protect = pulse_protect(img, protect, keep)
    out = img.copy()
    px = out.load()
    dist = edge_distance(out, 3)
    w, h = out.size
    ring1, ring2 = [], []
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            if p[3] == 0 or _is_ink(p) or (x, y) in protect:
                continue
            if dist[y][x] == 1:
                ring1.append((x, y))
            elif dist[y][x] == 2:
                ring2.append((x, y))
    if n == 1:
        for (x, y) in ring1:
            px[x, y] = GREY[7] + (px[x, y][3],)
    elif n == 2:
        changed = False
        for (x, y) in ring2:
            p = px[x, y]
            c = _brighten(tuple(p[:3]))
            if c != tuple(p[:3]):
                changed = True
            px[x, y] = c + (p[3],)
        for (x, y) in ring1:
            colour = GREY[7]
            if not changed and _side(dist, x, y) == 'br':
                colour = GREY[6]
            px[x, y] = colour + (px[x, y][3],)
    else:
        for (x, y) in ring1:
            if (x + y) % 2 == 0:
                px[x, y] = GREY[7] + (px[x, y][3],)
    return out


def make_state(img, state, protect=None, seal=False, glyphs=None, footprint=None, extras=None):
    """Apply the shared transform for a state name to a painted normal frame.

    ``protect``: lettering glyphs plus their 1 px halo (pulses never touch
    them); ``footprint``: the glyph and shadow pixels alone (selected never
    touches them; defaults to ``protect``); ``glyphs``: the glyph pixels
    (disabled recolours them in place; defaults to ``protect``); ``extras``:
    arrow glyph pixels, recoloured by disabled like lettering. ``seal`` is
    accepted for API parity with the Soulrend toolkit and ignored."""
    glyphs = protect if glyphs is None else glyphs
    footprint = protect if footprint is None else footprint
    if state == 'normal':
        return img.copy()
    if state == 'disabled':
        return make_disabled(img, glyphs, extras)
    if state == 'selected':
        return make_selected(img, footprint)
    if state.startswith('pulse_'):
        return make_pulse(img, int(state[-1]), protect, keep=footprint)
    raise ValueError(f'unknown state {state!r}')
