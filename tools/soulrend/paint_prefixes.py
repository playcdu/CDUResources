#!/usr/bin/env python3
"""Soulrend painter for the prefixes family: prefixes_1 .. prefixes_6.

    python tools/soulrend/paint_prefixes.py                      # all six skins into pack-source
    python tools/soulrend/paint_prefixes.py --skin prefixes_3    # one skin
    python tools/soulrend/paint_prefixes.py --out-root DIR       # write under DIR instead

prefixes_N is chest_N (176 x 132/150/168/186/204/222) whose every top cell is
a native well holding a selectable prefix item. The skins own a background and
one outer frame (menu_frame) each; there are no painted buttons.

Family identity (style guide section 5, prefixes: accent gold, secondary
blood): a hall of heraldry. The background is the shared Soulrend sheet whose
prefix grid is mounted like an iron plate on the wall, bolted with gold
rivets at every seam; the frame is a mossy dungeon wall hung with BLANK
heraldic shields and BLANK iron name plates on chains, wall torches pooling
ember light, one crest banner, a great quartered shield, a hanging roll of
name plates and a gargoyle corbel. Every plate is blank: no names, no words.
Panels are composed per height from a stack of elements, never cropped.

``--out-root DIR`` is a pack-source-like root: textures land in
DIR/assets/quasar_gui/textures/{menu,frames}/... (default: pack-source).
Deterministic: fixed seeds, no clock. Only this family's PNGs are written.

Licence: MIT (tooling); the artwork it paints is CC0-1.0.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
for _p in (str(_HERE.parent), str(_HERE.parent / 'cozy')):
    if _p not in sys.path:
        sys.path.append(_p)

from PIL import Image  # noqa: E402

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import icons  # noqa: E402
import primitives as P  # noqa: E402
from palette import BLOOD, EMBER, GOLD, INK, IRON, MOSS, STONE, UMBER, VELLUM, rgba  # noqa: E402

SKINS = tuple(f'prefixes_{n}' for n in range(1, 7))
SEED = 41
TEX_REL = Path('assets') / 'quasar_gui' / 'textures'

# Heraldic tinctures (each a ramp, dark -> light). Soul-cyan never fills.
TINCTURES = {
    'gules': BLOOD,      # blood red
    'vert': MOSS,        # green
    'sable': IRON,       # blackened iron
    'or': GOLD,          # tarnished gold
    'argent': VELLUM,    # bone white
    'tenne': UMBER,      # brown
}


# ---------------------------------------------------------------------------
# Layer helpers: draw an object on its own layer, cast a shadow onto the wall
# ---------------------------------------------------------------------------

def layer_like(img):
    return Image.new('RGBA', img.size, (0, 0, 0, 0))


def stamp(img, layer, shadow=True):
    """Composite ``layer`` onto ``img``; with ``shadow`` every opaque layer
    pixel first casts a 1 px ink_0 shadow down-right onto the wall (only on
    opaque wall pixels the layer leaves uncovered)."""
    lp = layer.load()
    W, H = layer.size
    if shadow:
        ip = img.load()
        for y in range(H):
            for x in range(W):
                if lp[x, y][3] and x + 1 < W and y + 1 < H and not lp[x + 1, y + 1][3] and ip[x + 1, y + 1][3]:
                    ip[x + 1, y + 1] = rgba('ink_0')
    img.alpha_composite(layer)


# ---------------------------------------------------------------------------
# Original family sprites
# ---------------------------------------------------------------------------

def shield_mask(w, h):
    """Heater shield: flat top with clipped corners, straight sides for about
    half the height, then curving to a point. ``w`` should be odd."""
    half = w // 2
    t0 = max(2, (h * 11) // 20)
    inside = set()
    for j in range(h):
        if j < t0:
            inset = 1 if j == 0 else 0
        else:
            f = (j - t0 + 1) / (h - t0)
            inset = round(half * f ** 1.6)
        for i in range(inset, w - inset):
            inside.add((i, j))
    if (0, 0) in inside:
        inside.discard((0, 0)); inside.discard((w - 1, 0))
    return inside


def _division(division, i, j, w, h):
    """True when field pixel (i, j) carries the second tincture."""
    cx = (w - 1) / 2
    if division == 'pale':
        return i > cx
    if division == 'fess':
        return j >= h * 0.45
    if division == 'bend':
        return (i - j * (w / h) * 0.9) > -1
    if division == 'bend_sinister':
        return ((w - 1 - i) - j * (w / h) * 0.9) > -1
    if division == 'quarterly':
        return (i > cx) != (j >= h * 0.42)
    if division == 'chief':
        return j < max(3, h // 3)
    if division == 'chevron':
        d = abs(i - cx)
        return h * 0.30 + d * 0.9 <= j <= h * 0.30 + d * 0.9 + max(2, h // 6)
    if division == 'pall':   # a plain field with a broad pale down the middle
        return abs(i - cx) <= max(1, w // 6)
    return False


def shield(img, x, y, w, h, t1='gules', t2='or', division='pale', rim='gold', boss=False, seed=0):
    """A blank heraldic shield (tinctures and partition only; no charge, no
    letters) with an ink outline (heavy bottom/right), a metal rim lit on the
    top/left, the field shaded one ramp step lighter on its left column and one
    darker on its right, a seeded scuff, and an optional iron boss."""
    inside = shield_mask(w, h)
    edge = P._edge_pixels(inside)
    rim_px = P._edge_pixels(inside - edge)
    field = inside - edge - rim_px
    r1, r2 = TINCTURES[t1], TINCTURES[t2]
    for (i, j) in field:
        ramp = r2 if _division(division, i, j, w, h) else r1
        base = 1 if len(ramp) > 3 else 1
        col = ramp[base]
        left = (i - 1, j) in rim_px
        right = (i + 1, j) in rim_px
        if left:
            col = ramp[min(len(ramp) - 1, base + 1)]
        elif right or (i, j + 1) in rim_px:
            col = ramp[max(0, base - 1)]
        P.put(img, x + i, y + j, col)
    rr = (GOLD[2], GOLD[1], GOLD[0]) if rim == 'gold' else (IRON[3], IRON[2], IRON[0])
    cx = (w - 1) / 2
    for (i, j) in rim_px:
        s = P._side(inside - edge, i, j)
        if 't' in s or ('l' in s and i < cx):
            col = rr[0]
        elif 'b' in s and i > cx or 'r' in s:
            col = rr[2]
        else:
            col = rr[1] if i < cx else rr[2]
        P.put(img, x + i, y + j, col)
    for (i, j) in edge:
        s = P._side(inside, i, j)
        P.put(img, x + i, y + j, 'ink_0' if ('b' in s and i > cx) or 'r' in s else 'ink_1')
    r = P._rng(seed, 'shield', x, y)
    # a scuff: two pixels one step darker on the field
    fl = sorted(field)
    if len(fl) > 20:
        i, j = fl[r.randrange(len(fl))]
        for k in range(2):
            if (i + k, j + k) in field:
                p = P.get(img, x + i + k, y + j + k)
                P.put(img, x + i + k, y + j + k, P.step(p, -1))
    if boss:
        bx, by = x + w // 2 - 1, y + int(h * 0.38) - 1
        P.sprite(img, bx, by, ['odo', 'cba', '.a.'])
    return inside


def peg(img, x, y, kind='iron'):
    """A wall peg / ring bolt (3x3) whose top-left is at (x, y)."""
    P.rivet(img, x, y, kind, size=3)


def vchain(img, x, y0, y1, seed):
    """Short vertical chain whose links are centred on column ``x``."""
    if y1 - y0 < 2:
        P.vline(img, x, y0, y1, IRON[2])
        return
    P.chain(img, x, y0, x, y1, seed=seed, shadow=None)


def name_plate(img, x, y, w, h=9, rim='iron', seed=0):
    """A blank blackened-iron name plate: iron_plate with an incised empty
    cartouche (iron_0 on the top/left of the recess, iron_2 on the
    bottom/right, so it reads cut in) and two ring eyes on its top edge. No
    words, ever."""
    P.iron_plate(img, (x, y, w, h), rim=rim, rivets=False, seed=seed, outline='ink_0', radius=1)
    rx, ry, rw, rh = x + 4, y + 3, w - 8, h - 6
    if rw >= 4 and rh >= 2:
        P.hline(img, rx, rx + rw - 1, ry, IRON[0])
        P.vline(img, rx, ry, ry + rh - 1, IRON[0])
        P.hline(img, rx + 1, rx + rw - 1, ry + rh - 1, IRON[2])
        P.vline(img, rx + rw - 1, ry + 1, ry + rh - 1, IRON[2])
    # gold bolt heads on the short ends
    P.put(img, x + 2, y + h // 2, GOLD[2] if rim == 'iron' else IRON[3])
    P.put(img, x + w - 3, y + h // 2, GOLD[1] if rim == 'iron' else IRON[2])
    return (x + 3, x + w - 4)       # chain columns


TORCH = [
    '...F...',
    '..fFf..',
    '.fFFFe.',
    '.efFfe.',
    '..eFe..',
    '.occco.',
    '.oc0ao.',
    '..o2o..',
    '..o3o..',
    '.oo2oo.',
    'occccao',
    '.oo2oo.',
    '..o2o..',
    '..o1o..',
    '..o2o..',
    '...o...',
]


def torch(img, x, y):
    """A wall torch in an iron bracket; (x, y) is the top-left of the 7x16
    sprite. Returns the flame centre for ``glow``."""
    P.sprite(img, x, y, TORCH)
    return x + 3, y + 2


# ---------------------------------------------------------------------------
# Panel elements: (height, draw(img, cx, y, seed)) composed per height
# ---------------------------------------------------------------------------

class El:
    def __init__(self, h, draw, gap_before=0):
        self.h = h
        self.draw = draw
        self.gap_before = gap_before


def el_banner(h, ramp, crest, w=17):
    """The crest banner, its rod hung from a wall peg by two iron cords."""
    hang = 5

    def draw(img, cx, y, seed):
        x = cx - w // 2
        lay = layer_like(img)
        P.sprite(lay, cx - 2, y, ['ooooo', 'odcbo', 'ooooo'])
        for ex in (x - 1, x + w):
            P.line(lay, ex, y + hang, cx + (-1 if ex < cx else 1), y + 2, IRON[2])
        stamp(img, lay)
        P.banner(img, x, y + hang + 1, w, h - hang - 1, ramp, seed, emblem=crest)
    return El(h, draw)


def el_torch():
    def draw(img, cx, y, seed):
        lay = layer_like(img)
        fx, fy = torch(lay, cx - 3, y)
        stamp(img, lay)
        P.glow(img, fx, fy + 3, 12, 'ember')
        # re-stamp the flame and bracket so the glow never lightens the sprite
        img.alpha_composite(lay)
    return El(16, draw)


def el_mount(sw, sh, t1, t2, division, rim='gold', plate_w=26, boss=False):
    """A blank shield hung from a peg by two chains, and under it a blank
    name plate hung on two chains from two pegs either side of the point."""
    h = 5 + sh + 2 + 4 + 9

    def draw(img, cx, y, seed):
        lay = layer_like(img)
        x = cx - sw // 2
        # peg bar and chains to the shield's shoulders
        P.sprite(lay, cx - 2, y, ['ooooo', 'odcbo', 'ooooo'])
        top = y + 5
        for k, sx in enumerate((x + 2, x + sw - 3)):
            P.line(lay, sx, top - 1, cx + (-1 if sx < cx else 1), y + 2, IRON[2])
            P.put(lay, sx, top - 1, IRON[3])
        shield(lay, x, top, sw, sh, t1, t2, division, rim=rim, boss=boss, seed=seed)
        stamp(img, lay)
        # the name plate under the shield
        lay = layer_like(img)
        py = top + sh + 2 + 4
        px = cx - plate_w // 2
        cols = name_plate(lay, px, py, plate_w, 9, seed=seed + 1)
        for c in cols:
            peg(lay, c - 1, py - 6)
            P.vline(lay, c, py - 3, py - 1, IRON[2])
            P.put(lay, c, py - 2, IRON[0])
        stamp(img, lay)
    return El(h, draw)


def el_great_shield(sw, sh, t1, t2, division):
    """A great quartered shield hung from two chains to a gold-capped bar,
    set in a round-topped stone niche so it stands out of the wall."""
    nw = sw + 10
    top = 9                       # bar row below the niche's crown
    h = top + 8 + sh + 3

    def draw(img, cx, y, seed):
        P.arch_niche(img, (cx - nw // 2, y, nw, h), seed=seed)
        lay = layer_like(img)
        x = cx - sw // 2
        by = y + top
        P.hline(lay, x - 1, x + sw, by + 1, IRON[2])
        P.hline(lay, x - 1, x + sw, by, INK[0])
        P.hline(lay, x - 1, x + sw, by + 2, INK[0])
        P.sprite(lay, x - 3, by, ['h', 'H', 'g'])
        P.sprite(lay, x + sw + 1, by, ['h', 'H', 'g'])
        for sx in (x + 3, x + sw - 4):
            vchain(lay, sx, by + 3, by + 8, seed + sx)
        shield(lay, x, by + 8, sw, sh, t1, t2, division, rim='gold', boss=True, seed=seed)
        stamp(img, lay)
        # a sill under the niche
        P.hline(img, cx - nw // 2 - 1, cx + nw // 2 + 1, y + h, STONE[3])
        P.hline(img, cx - nw // 2 - 1, cx + nw // 2 + 1, y + h + 1, STONE[1])
        P.hline(img, cx - nw // 2 - 1, cx + nw // 2 + 1, y + h + 2, INK[1])
    return El(h + 3, draw)


def el_plate_roll(n, w=28):
    """A hanging roll of ``n`` blank name plates linked by short chains."""
    h = 5 + n * 9 + (n - 1) * 4

    def draw(img, cx, y, seed):
        lay = layer_like(img)
        x = cx - w // 2
        peg(lay, cx - 1, y)
        P.line(lay, cx, y + 3, x + 3, y + 4, IRON[2])
        P.line(lay, cx, y + 3, x + w - 4, y + 4, IRON[2])
        yy = y + 5
        for k in range(n):
            cols = name_plate(lay, x, yy, w, 9, rim='gold' if k == 0 else 'iron', seed=seed + k)
            if k < n - 1:
                for c in cols:
                    P.vline(lay, c, yy + 9, yy + 12, IRON[2])
                    P.put(lay, c, yy + 10, IRON[0])
            yy += 13
        stamp(img, lay)
    return El(h, draw)


def el_ledge_candles(w=28):
    """A carved stone ledge on iron brackets with two candles and a small
    blank shield leaning against the wall."""
    h = 21

    def draw(img, cx, y, seed):
        x = cx - w // 2
        lay = layer_like(img)
        shield(lay, x + 3, y + 4, 9, 11, 'vert', 'argent', 'chief', rim='iron', seed=seed)
        f1 = P.candle(lay, x + w - 9, y + 7, height=6, lit=True, holder=None, seed=seed)
        f2 = P.candle(lay, x + w - 5, y + 9, height=4, lit=True, width=2, holder=None, seed=seed + 1)
        ly = y + 15
        P.fill(lay, (x, ly, w, 4), STONE[2])
        P.hline(lay, x, x + w - 1, ly, STONE[3])
        P.hline(lay, x, x + w - 1, ly + 3, STONE[0])
        P.ink_outline(lay, (x - 1, ly - 1, w + 2, 6), 'ink_1', radius=0)
        for bx in (x + 2, x + w - 4):
            P.sprite(lay, bx, ly + 5, ['oco', '.oa'])
        stamp(img, lay)
        P.glow(img, f1[0], f1[1], 9, 'ember')
        img.alpha_composite(lay)
        P.moss_tuft(img, x + 9, ly + 5, 4, seed=seed)
    return El(h, draw)


def el_gargoyle():
    def draw(img, cx, y, seed):
        lay = layer_like(img)
        icons.draw_motif(lay, 'gargoyle', cx - 4, y)
        stamp(img, lay)
    return El(11, draw)


def compose_panel(img, cx, y0, y1, elements, tail, seed):
    """Fit as many ``elements`` (in order) as the panel holds with at least a
    5 px gap, anchor ``tail`` at the bottom, and spread the spare rows evenly
    between them (so each height is composed, not cropped). Returns the
    placed (element, y) pairs."""
    avail = y1 - y0 - (tail.h + 4 if tail else 0)
    chosen = []
    used = 0
    for e in elements:
        need = used + e.h + 5 * (len(chosen) + 1)
        if need <= avail:
            chosen.append(e)
            used += e.h
        else:
            break
    spare = avail - used
    n = len(chosen)
    gap = spare // (n + 1) if n else 0
    gap = max(5, min(gap, 14))
    # extra rows that the capped gap leaves go to the top margin
    lead = max(gap, (spare - gap * n) // 2) if n else 0
    y = y0 + min(lead, gap + 6)
    out = []
    for k, e in enumerate(chosen):
        e.draw(img, cx, y, seed + 17 * k)
        out.append((e, y))
        y += e.h + gap
    if tail:
        tail.draw(img, cx, y1 - tail.h, seed + 101)
    return out


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def paint_background(key, seed=SEED):
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    W, H = s.width, s.height
    tband, iband = C.bands(key)
    # The prefix grid is an iron plate bolted to the wall: every iron_3 rivet
    # on its outer iron ring (outside the text bands) becomes a gold bolt.
    grid = P.merge_holes(s.content_slots)
    gy0 = min(r[1] for r in grid) - 3
    gy1 = max(r[1] + r[3] for r in grid) + 3
    for y in range(gy0, gy1):
        if tband.y <= y < tband.bottom or iband.y <= y < iband.bottom:
            continue
        for x in (3, W - 4):
            p = P.get(img, x, y)
            if p[3] and tuple(p[:3]) == IRON[3]:
                P.put(img, x, y, GOLD[2])
                P.put(img, x, y + 1, GOLD[0])
    # under the hotbar socket: a gold flourish between two tiny shield studs
    P.gold_filigree(img, W // 2 - 5, H - 4, 'flourish')
    for sx in (W // 2 - 26, W // 2 + 23):
        P.sprite(img, sx, H - 4, ['ohho', 'osso', '.oo.'])
    P.crack(img, 30, H - 4, 3, seed=seed, direction='right', colour='umber_0', branch=False)
    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

LEFT_MOUNTS = [
    (15, 17, 'gules', 'or', 'pale'),
    (15, 17, 'vert', 'argent', 'chevron'),
    (15, 17, 'sable', 'or', 'bend'),
    (15, 17, 'argent', 'gules', 'chief'),
]
RIGHT_MOUNTS = [
    (15, 17, 'vert', 'or', 'bend_sinister'),
    (15, 17, 'gules', 'sable', 'fess'),
]


def left_elements(n_rows):
    els = [el_banner(40 if n_rows > 140 else 34, BLOOD, 'chevron'), el_torch()]
    for k, (w, h, t1, t2, d) in enumerate(LEFT_MOUNTS):
        els.append(el_mount(w, h, t1, t2, d, rim='gold' if k % 2 == 0 else 'iron', boss=(k == 1)))
        if k == 1:
            els.append(el_torch())
    return els


def right_elements(n_rows):
    els = [el_great_shield(17, 21, 'gules', 'or', 'quarterly'), el_torch(),
           el_plate_roll(3 if n_rows > 190 else 2)]
    for k, (w, h, t1, t2, d) in enumerate(RIGHT_MOUNTS):
        els.append(el_mount(w, h, t1, t2, d, rim='iron' if k == 0 else 'gold'))
        if k == 0:
            els.append(el_torch())
    return els


def paint_frame(key, seed=SEED):
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, a.id, seed=seed)
    H, W = a.h, a.w
    lp, rp = a.left_panel, a.right_panel
    lcx = lp.x + 20
    rcx = rp.x + 20
    y0, y1 = 10, H - 10
    rows = y1 - y0
    compose_panel(img, lcx, y0, y1, left_elements(rows), el_ledge_candles() if rows > 150 else None, seed)
    compose_panel(img, rcx, y0, y1, right_elements(rows), el_gargoyle(), seed + 50)
    # hand touches: moss, a crack, per side
    P.crack(img, lp.x + 33, H - 30, 7, seed=seed + 5, colour=STONE[0], light=STONE[3])
    P.crack(img, rp.x + 6, H // 2 + 9, 6, seed=seed + 6, colour=STONE[0], light=STONE[3])
    # top strip: chains from the corners to the plaque
    P.chain(img, 12, 4, W // 2 - 22, 4, sag=2, seed=seed + 11)
    P.chain(img, W // 2 + 21, 4, W - 13, 4, sag=2, seed=seed + 12)
    # two small blank shields hung on the top chains
    for sx, (t1, t2, d) in ((58, ('gules', 'or', 'pale')), (W - 66, ('sable', 'argent', 'chief'))):
        lay = layer_like(img)
        shield(lay, sx, 1, 9, 7, t1, t2, d, rim='gold', seed=seed + sx)
        stamp(img, lay)
    # bottom strip: chains swagged between gold rivets, a fleur in the middle
    for x0, x1 in ((8, W // 2 - 8), (W // 2 + 8, W - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3)
        P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, W // 2 - 2, H - 7, 'fleur')
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def out_paths(key, root):
    s = geo.skin(key)
    if root is None:
        return s.background_path, s.frame_path(s.layer().id)
    tex = Path(root) / TEX_REL
    return tex / 'menu' / f'{key}.png', tex / 'frames' / key / f'{s.layer().id}.png'


def paint(key, root=None):
    s = geo.skin(key)
    bg_path, fr_path = out_paths(key, root)
    with Image.open(s.background_path) as old:
        want_bg = old.size
    with Image.open(s.frame_path(s.layer().id)) as old:
        want_fr = old.size
    bg = paint_background(key)
    fr = paint_frame(key)
    assert bg.size == want_bg and bg.mode == 'RGBA', (key, bg.size, want_bg)
    assert fr.size == want_fr and fr.mode == 'RGBA', (key, fr.size, want_fr)
    C.save_png(bg, bg_path)
    C.save_png(fr, fr_path)
    print('WROTE', bg_path)
    print('WROTE', fr_path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', default=None, help='pack-source-like root to write into (default: pack-source)')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        paint(key, args.out_root)


if __name__ == '__main__':
    main()
