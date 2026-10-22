#!/usr/bin/env python3
"""Soulrend painter "utility": trashcan, ender_chest and crafting.

    python tools/soulrend/paint_utility.py                 # all three skins into pack-source
    python tools/soulrend/paint_utility.py --skin crafting
    python tools/soulrend/paint_utility.py --out-root DIR  # DIR/menu/<key>.png, DIR/frames/<key>/<id>.png

Deterministic (fixed seeds, no clock). Paints only:

* trashcan     chest_6 background + 256x238 menu_frame: an ash-pit brazier
               with dying embers and burnt leaves rising up a soot-stained
               wall to an iron flue grate; fire irons on a rail, a ledge with
               a cold candle and an ash pail, a rake leaning in a heap of ash;
               an iron floor grate. A single ember glow.
* ender_chest  chest_3 background + 256x184 menu_frame: obsidian and
               void-purple masonry, carved soul-cyan runes (abstract marks,
               never letters), a hanging void lantern, a rune stele, a void
               niche, a chained key, void crystals.
* crafting     176x166 background, no frame: a blacksmith's anvil with a hot
               ingot and sparks, hammer / chisel / punch / tongs / file on an
               iron rack, leather bellows, a quench bucket, a horseshoe.
               Recipe-book toggle and arrow stay transparent; no painted title.

Every frame is wordless (headings become a wordless plaque and banners);
these skins have no buttons.

Licence: MIT (code); the pixel art it produces is CC0-1.0.
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

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import icons  # noqa: E402
import primitives as P  # noqa: E402
from palette import (BLOOD, EMBER, GOLD, INK, IRON, SOUL, STONE, UMBER,  # noqa: E402
                     VOID, ramp_of, step)

SKINS = ('trashcan', 'ender_chest', 'crafting')
DEFAULT_ROOT = geo.ROOT / 'pack-source' / 'assets' / 'quasar_gui' / 'textures'


# ---------------------------------------------------------------------------
# Small helpers (local to this painter)
# ---------------------------------------------------------------------------

def spr(img, x, y, rows, key=None, flip_x=False):
    """P.sprite with a guard: every row of a hand-authored sprite must be the
    same width (ragged rows would silently shift pixels)."""
    widths = {len(r) for r in rows}
    assert len(widths) == 1, f'ragged sprite rows: {sorted(widths)} {rows[0]!r}'
    P.sprite(img, x, y, rows, key, flip_x=flip_x)


def shape(img, x, y, spans, light, body, dark, top=None, outline='ink_1', heavy='ink_0'):
    """Fill a hand-measured silhouette given as per-row (x0, x1) spans
    (relative to x, y; None for an empty row). The boundary gets an ink
    outline (``heavy`` on bottom/right edges), the first interior row
    ``top`` (or ``light``), the left interior column ``light`` and the right
    interior column ``dark``; the rest is ``body``."""
    inside = set()
    for j, sp in enumerate(spans):
        if sp is None:
            continue
        for i in range(sp[0], sp[1] + 1):
            inside.add((i, j))
    for (i, j) in inside:
        n = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        if any(q not in inside for q in n):
            col = heavy if ((i + 1, j) not in inside or (i, j + 1) not in inside) else outline
        elif (i, j - 2) not in inside:
            col = top or light
        elif (i - 2, j) not in inside:
            col = light
        elif (i + 2, j) not in inside or (i, j + 2) not in inside:
            col = dark
        else:
            col = body
        P.put(img, x + i, y + j, col)
    return inside


def soot(img, cx, y_bottom, y_top, w_bottom, w_top, seed=0):
    """A soot stain rising up masonry from ``y_bottom`` to ``y_top``: a
    tapering, gently wandering band in which stone, moss and iron faces step
    one shade darker (mortar is already darkest and stays); its ragged edge
    and its top quarter thin out to a 50 % checker, so the stain fades the
    way light falls off (ordered, never noise)."""
    r = P._rng(seed, 'soot', cx, y_bottom)
    span = max(1, y_bottom - y_top)
    wob = 0
    for y in range(y_bottom, y_top - 1, -1):
        t = (y_bottom - y) / span                   # 0 at the bottom, 1 at the top
        half = (w_bottom + (w_top - w_bottom) * t) / 2
        if r.random() < 0.18:
            wob = max(-2, min(2, wob + r.choice((-1, 1))))
        fading = t > 0.88
        for x in range(int(cx + wob - half - 1), int(cx + wob + half + 2)):
            p = P.get(img, x, y)
            if p[3] == 0:
                continue
            rr = ramp_of(p)
            if not rr or rr[0] not in ('stone', 'moss', 'iron'):
                continue
            edge = abs(x - wob - cx) > half
            if (edge or fading) and (x + y) % 2:
                continue
            P.put(img, x, y, step(p, -1))


LEAVES = [
    ['...oo.', '..o32o', '.o321o', 'o32eo.', 'o2oo..', 'o.....'],
    ['.ooo..', 'o233o.', 'o2oo2o', '.o..eo', '..ooo.'],
    ['oo....', 'o3oo..', '.o32oo', '..o21o', '...oeo'],
    ['..oo..', '.o32o.', 'o3221o', '.o2eo.', '..oo..', '...o..'],
]


def leaf(img, x, y, kind=0, flip=False):
    """A burnt leaf, 5-6 px: umber body lit top-left, a smouldering ember_0
    edge, ink outline."""
    spr(img, x, y, LEAVES[kind % len(LEAVES)], flip_x=flip)


RUNES = [
    ['..l..', '.l.l.', 'l.L.l', '..l..', '..l..'],
    ['ll...', '..l..', '..Ll.', '.l..l', 'l....'],
    ['.lll.', 'l...l', '..L..', 'l...l', '.l.l.'],
    ['l...l', 'l.L.l', '.l.l.', '..l..', '.l.l.'],
    ['.l...', 'lLl..', '.l.l.', '...Ll', '....l'],
]


def rune(img, x, y, kind=0):
    """A carved soul rune, 5x5: an abstract mark (never a letter) in soul_1
    with a soul_2 heart, cut 1 px deep (a soul_0 shadow down-right)."""
    rows = RUNES[kind % len(RUNES)]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            nj, ni = j + 1, i + 1
            if nj >= 5 or ni >= 5 or rows[nj][ni] == '.':
                P.put(img, x + ni, y + nj, SOUL[0])
    spr(img, x, y, rows)


def ledge(img, x, y, w, ramp=STONE):
    """A short carved ledge on two iron brackets (top surface at row y)."""
    P.fill(img, (x, y, w, 4), ramp[2])
    P.hline(img, x, x + w - 1, y, ramp[3])
    P.hline(img, x, x + w - 1, y + 3, ramp[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0)
    for bx in (x + 2, x + w - 4):
        spr(img, bx, y + 5, ['oco', '.oa', '..o'])


# ---------------------------------------------------------------------------
# Outer frame base with a chosen masonry ramp (obsidian for the ender chest)
# ---------------------------------------------------------------------------

def frame_base(key, seed, ramp=STONE, moss=0.10):
    """compose.base_frame, but with a masonry ``ramp`` and ``moss`` density of
    our choosing (obsidian has no moss). Same rim, iron border, rivets,
    recess, cast shadow, gold corner filigree and wordless plaque."""
    if ramp is STONE and moss == 0.10:
        return C.base_frame(key, seed=seed)
    s = geo.skin(key)
    a = s.layer()
    img = C.new(a.w, a.h)
    P.stone_blocks(img, (1, 1, a.w - 2, a.h - 2), seed, ramp, course=7, moss=moss)
    c = a.container
    P.ink_outline(img, (0, 0, a.w, a.h), 'ink_0', radius=3)
    P.bevel(img, (1, 1, a.w - 2, a.h - 2), IRON[2], IRON[0])
    P.bevel(img, (2, 2, a.w - 4, a.h - 4), IRON[1], INK[1])
    for x in range(10, a.w - 10, 16):
        P.put(img, x, 1, IRON[3]); P.put(img, x, a.h - 2, IRON[3])
    for y in range(12, a.h - 10, 16):
        P.put(img, 1, y, IRON[3]); P.put(img, a.w - 2, y, IRON[3])
    P.hline(img, c.x - 1, c.right, c.y - 1, INK[1])
    P.vline(img, c.x - 1, c.y - 1, c.bottom, INK[1])
    for k in (0, 1):
        P.vline(img, c.right + k, c.y + 2 + k, c.bottom - 1 + k, INK[0])
        P.hline(img, c.x + 2 + k, c.right + k, c.bottom + k, INK[0])
    for corner, (x, y) in (('tl', (3, 3)), ('tr', (a.w - 10, 3)), ('bl', (3, a.h - 10)), ('br', (a.w - 10, a.h - 10))):
        P.gold_filigree(img, x, y, 'corner', corner)
    C.heading_plaque(img, a.w // 2, 0)
    C.finish_frame(img, key, a.id)
    return img


def top_chains(img, a, seed):
    """Chains swagged from the corners to the wordless heading plaque."""
    P.chain(img, 12, 4, a.w // 2 - 22, 4, sag=2, seed=seed + 11)
    P.chain(img, a.w // 2 + 21, 4, a.w - 13, 4, sag=2, seed=seed + 12)


# ---------------------------------------------------------------------------
# TRASHCAN: ash-pit brazier
# ---------------------------------------------------------------------------

BRAZIER = [
    '..........o..........e....',
    '.....e...oFo.............',
    '..........e..............',
    '.........ooooooo.........',
    '......ooopqpcepqpoo......',
    '....oopqpepfepcpqpnoo....',
    '...opqpcpefFFfepnpenno...',
    '..opnpefeffFFFfeepnnmmo..',
    'ooooooooooooooooooooooooo',
    'odddcccccccccccccccbbbbao',
    'obbbbbbbbbbbbbbbbbbbaaaao',
    'ooooooooooooooooooooooooo',
    '.ocbObObObObObObObObObao.',
    '..ocObeObObOeObObObOeao..',
    '..ocbObObObObObObObObbao.',
    '...ocbbbbbbbbbdbbbbbbao..',
    '....oocbbbbbbbbbbbbaoo...',
    '......ooocbbbbbbaooo.....',
    '.........oocbbaoo........',
    '..........ocbbao.........',
    '..........ocbbao.........',
    '.........oocbbaoo........',
    '........ocbo..obao.......',
    '.......ocbo....obao......',
    '......ocbo......obao.....',
    '.....oooo........oooo....',
]
BRAZIER = [r.ljust(25, '.')[:25] for r in BRAZIER]

POKER = ['.oo.', 'oc.o', 'oc.o', '.oco', '.oco', '.oco', '.oco', '.oco', '.oco', '.oco', '.oco',
         '.oco', '.oco', '.oco', 'ocao', 'oco.', '.o..']
SHOVEL = ['..oo...', '.o.o...', '..o2o..', '..o3o..', '..o2o..', '..o3o..', '..o2o..', '..o3o..',
          '..o2o..', '.oocoo.', 'occcbbo', 'odccbao', 'ocvvbao', 'ocbvvao', 'ocbbaao', '.ooooo.']
FIRE_TONGS = ['.oo.oo.', '.oc.ao.', '.oc.ao.', '.oc.ao.', '.oc.ao.', '.oc.ao.', '.oc.ao.', '..ocao.',
              '..odo..', '..oco..', '.oaoco.', '.oao.oc', 'oao..oc', 'oo...oo']
ASH_PAIL = ['..oooooo..', '.o......o.', 'ooooooooooo'[:10], 'odpqppnpao', 'ocvqpnmmao', 'ocbbbbbbao',
            'occcccccao', '.ocbbbbao.', '.ocbbbbao.', '..oooooo..']


def paint_brazier(img, x, y):
    """The ash-pit brazier: a heap of grey ash with dying embers in a riveted
    iron bowl whose grate slots show the last coals, on a stem and three
    splayed legs. Returns the ember centre."""
    spr(img, x, y, BRAZIER)
    return x + 12, y + 6


def ash_heap(img, x, y, w, seed=0, h=None):
    """A low heap of grey ash on the floor (bottom row at y) with a dead
    cinder or two."""
    r = P._rng(seed, 'ash', x, y)
    h = h or max(3, w // 4)
    spans = []
    for j in range(h):
        k = h - j
        inset = int((k - 1) * (w / 2) / h) + (1 if 0 < j < h - 1 and r.random() < 0.3 else 0)
        spans.append((inset, w - 1 - inset))
    shape(img, x, y - h + 1, spans, IRON[3], IRON[2], IRON[1], top=IRON[3])
    for _ in range(max(1, w // 7)):
        px = x + r.randint(3, w - 4); py = y - r.randint(1, max(1, h - 2))
        if P.get(img, px, py)[:3] in (IRON[2], IRON[1]):
            P.put(img, px, py, EMBER[0] if r.random() < 0.4 else INK[2])


def rake(img, x0, y0, x1, y1):
    """A rake leaning against the wall: a 2 px umber shaft (lit left, ink
    outline) from (x0, y0) down to its iron head at (x1, y1); six tines dig
    into the ash."""
    pts = P.line_points(x0, y0, x1, y1)
    for (x, y) in pts:
        P.put(img, x - 1, y, INK[1])
        P.put(img, x + 2, y, INK[0])
    for (x, y) in pts:
        P.put(img, x, y, UMBER[3])
        P.put(img, x + 1, y, UMBER[1])
    spr(img, x0 - 1, y0 - 1, ['oooo'])
    spr(img, x1 - 1, y1 - 2, ['occo', 'obao'])
    spr(img, x1 - 6, y1, ['oooooooooooooo',
                          'oddcccccccbbao',
                          'oooooooooooooo',
                          '.oc.oc.oc.oc.o',
                          '.oc.oc.ob.ob.o',
                          '..o..o..o..o..'])


def iron_grate(img, box, seed=0):
    """A barred iron flue set in the wall: ink_0 rim, an iron frame lit
    top-left, a black flue behind square bars and one cross bar, rivets in
    the corners."""
    x, y, w, h = box
    P.ink_outline(img, box, 'ink_0', radius=1, fill_colour=IRON[1])
    P.hline(img, x + 1, x + w - 2, y + 1, IRON[2]); P.vline(img, x + 1, y + 1, y + h - 2, IRON[2])
    P.hline(img, x + 2, x + w - 2, y + h - 2, IRON[0]); P.vline(img, x + w - 2, y + 2, y + h - 2, IRON[0])
    P.fill(img, (x + 3, y + 3, w - 6, h - 6), INK[0])
    cy = y + h // 2
    for bx in range(x + 4, x + w - 3, 3):
        P.vline(img, bx, y + 3, y + h - 4, IRON[1])
        P.put(img, bx, y + 3, IRON[2])
        P.put(img, bx, y + h - 4, IRON[0])
    P.hline(img, x + 3, x + w - 4, cy, IRON[1]); P.hline(img, x + 3, x + w - 4, cy - 1, IRON[2])
    for (rx, ry) in ((x + 1, y + 1), (x + w - 3, y + 1), (x + 1, y + h - 3), (x + w - 3, y + h - 3)):
        P.rivet(img, rx, ry, 'iron', 2)


def burnt_scrap(img, x, y, w, h, seed=0):
    """A scrap of ruled vellum nailed to the wall, its bottom and right edges
    torn and charred: something thrown away and half burnt. No writing."""
    layer = C.new(img.width, img.height)
    P.vellum_strip(layer, (x, y, w, h), seed, outline='ink_1', deckle='t', fibres=False)
    for ry in range(y + 4, y + h - 3, 3):
        P.hline(layer, x + 2, x + w - 4, ry, 'vellum_0')
    P.torn_edge(layer, (x, y, w, h), 'b', seed=seed, depth=4, burnt=True)
    P.torn_edge(layer, (x, y + 3, w, h - 3), 'r', seed=seed + 1, depth=3, burnt=True)
    img.alpha_composite(layer)
    P.rivet(img, x + w // 2 - 1, y + 1, 'dark', 2)


def floor_grate(img, x0, x1, y, seed=0):
    """An iron floor grate along the bottom strip: bars every 3 px over a
    black ash pit, a few dying ember_0 coals glimpsed between the bars."""
    r = P._rng(seed, 'floor', x0, y)
    P.hline(img, x0, x1, y, INK[0])
    P.hline(img, x0, x1, y + 1, IRON[2])
    for x in range(x0, x1 + 1):
        if (x - x0) % 3 == 0:
            P.put(img, x, y + 2, IRON[1]); P.put(img, x, y + 3, IRON[0])
        else:
            P.put(img, x, y + 2, INK[0]); P.put(img, x, y + 3, INK[1])
            if r.random() < 0.05:
                P.put(img, x, y + 3, EMBER[0])
    P.hline(img, x0, x1, y + 4, INK[0])


def paint_trashcan_bg(seed=21):
    key = 'trashcan'
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    H = s.height
    # the 2 free rows under the hotbar socket: an ash smear and two coals
    for x, col in ((60, STONE[1]), (61, STONE[2]), (62, STONE[1]), (110, STONE[1]), (111, INK[2])):
        P.put(img, x, H - 3, col)
    P.put(img, 88, H - 3, EMBER[0]); P.put(img, 92, H - 2, EMBER[0])
    P.crack(img, 140, H - 3, 3, seed=seed, direction='right', colour='umber_0', branch=False)
    C.finish_background(img, key)
    return img


def paint_trashcan_frame(seed=21):
    key = 'trashcan'
    s = geo.skin(key)
    a = s.layer()
    img = frame_base(key, seed)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    floor = H - 9                                  # last wall row above the bottom strip

    # --- left panel: banner, flue grate, soot plume, the ash-pit brazier ---
    C.side_banner(img, geo.Rect(lp.x + 4, 0, 32, 0), y=16, seed=seed, ramp=BLOOD, crest='flame', h=30)
    gx, gy = lp.x + 9, 64
    bx, by = lp.x + 7, floor - len(BRAZIER) + 1
    soot(img, lp.x + 20, by + 4, gy + 18, 20, 12, seed=seed)
    iron_grate(img, (gx, gy, 22, 18), seed=seed)
    fx, fy = paint_brazier(img, bx, by)
    P.glow(img, fx, fy, 17, 'ember')
    # burnt leaves rising from the pit up the soot towards the flue
    for (dx, dy, k, fl) in ((-9, -14, 0, False), (3, -27, 1, True), (-6, -46, 2, False),
                            (2, -66, 3, True), (-3, -88, 0, True)):
        leaf(img, fx + dx, fy + dy, k, fl)
    for (dx, dy, col) in ((-2, -9, EMBER[1]), (4, -17, EMBER[0]), (-4, -33, EMBER[0]), (1, -55, EMBER[0])):
        P.put(img, fx + dx, fy + dy, col)

    # --- right panel: fire irons on a rail, ledge with a cold candle and an
    #     ash pail, the rake leaning in a heap of ash and burnt leaves -------
    ry = 16
    P.hline(img, rp.x + 3, rp.x + 33, ry, INK[0])
    P.hline(img, rp.x + 3, rp.x + 33, ry + 1, IRON[2])
    P.hline(img, rp.x + 3, rp.x + 33, ry + 2, IRON[0])
    P.hline(img, rp.x + 3, rp.x + 33, ry + 3, INK[0])
    P.rivet(img, rp.x + 4, ry + 1, 'iron', 2); P.rivet(img, rp.x + 31, ry + 1, 'iron', 2)
    spr(img, rp.x + 7, ry + 4, POKER)
    spr(img, rp.x + 14, ry + 4, FIRE_TONGS)
    spr(img, rp.x + 23, ry + 4, SHOVEL)
    P.moss_tuft(img, rp.x + 4, 56, 4, seed=seed)

    lx, ly = rp.x + 4, 96
    ledge(img, lx, ly, 29)
    fxc, _ = P.candle(img, lx + 4, ly - 9, height=7, lit=False, holder='iron', seed=seed)
    spr(img, lx + 15, ly - 10, ASH_PAIL)
    leaf(img, lx + 10, ly - 4, 2)
    P.crack(img, rp.x + 31, 112, 9, seed=seed, colour=STONE[0], light=STONE[3])
    burnt_scrap(img, rp.x + 4, 146, 14, 17, seed=seed)

    ash_heap(img, rp.x + 1, floor, 17, seed=seed + 2, h=5)
    rake(img, rp.x + 31, 136, rp.x + 21, floor - 5)
    for (dx, dy, k, fl) in ((3, -8, 3, False), (12, -4, 1, False), (29, -12, 0, True)):
        leaf(img, rp.x + dx, floor + dy, k, fl)

    # --- strips ---
    top_chains(img, a, seed)
    floor_grate(img, 10, a.w - 11, H - 7, seed=seed)
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------
# ENDER CHEST: obsidian, void-purple, soul runes
# ---------------------------------------------------------------------------

OBSIDIAN = (INK[0], INK[1], VOID[0], VOID[1])     # masonry ramp: mortar, face, alt face, lit edge
VOID_CLOTH = (VOID[0], VOID[1], VOID[1])          # banner cloth: shadow, body, lit column

VOID_LANTERN = [
    '.....oo.....',
    '....o..o....',
    '...oooooo...',
    '..odcccbao..',
    '.oooooooooo.',
    '.odokkkkoao.',
    '.ocokklkoao.',
    '.ocoklLkoao.',
    '.obokllkoao.',
    '.obokkkkoao.',
    '.oooooooooo.',
    '..odccbbao..',
    '...oooooo...',
    '.....oo.....',
]
GOLD_KEY = ['..ooo..', '.oHhgo.', 'oHo.ogo', 'oho.ogo', '.ohhgo.', '..oho..', '..oho..', '..oho..',
            '..ohoo.', '..ohhgo', '..ohoo.', '..ohhgo', '..ohgo.', '..ooo..']
CRYSTALS = [
    '......o........',
    '.....oVo.......',
    '.....oUo...o...',
    '....olUuo.oVo..',
    '.o..oluuo.olo..',
    'oVo.oluuoolUuo.',
    'oluooUuuoolUuo.',
    'oUuooUuuooUuuuo',
    'ooooooooooooooo',
]
VOID_KEY = {'V': SOUL[2], 'U': VOID[1], 'u': VOID[0]}


def paint_ender_bg(seed=33):
    key = 'ender_chest'
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)
    H = s.height
    # under the hotbar socket: two faint soul flecks in the obsidian
    P.put(img, 52, H - 3, SOUL[0]); P.put(img, 124, H - 2, SOUL[0]); P.put(img, 125, H - 3, VOID[1])
    C.finish_background(img, key)
    return img


def paint_ender_frame(seed=33):
    key = 'ender_chest'
    s = geo.skin(key)
    a = s.layer()
    img = frame_base(key, seed, ramp=OBSIDIAN, moss=0.0)
    lp, rp = a.left_panel, a.right_panel
    H = a.h
    floor = H - 9

    # --- left panel: void banner (moon crest), hanging void lantern, rune
    #     stele, obsidian shards ---------------------------------------------
    C.side_banner(img, geo.Rect(lp.x + 4, 0, 32, 0), y=16, seed=seed, ramp=VOID_CLOTH, crest='moon', h=30)
    spr(img, lp.x + 6, 51, ['ooo', 'odo', 'oco', 'obo', 'oco', 'obo', 'ooo'])        # wall plate
    spr(img, lp.x + 9, 53, ['oooooooooooooo', 'odddcccccccbbo', 'oooooooooooooo'])  # bracket arm
    P.chain(img, lp.x + 21, 56, lp.x + 21, 59, seed=seed + 1)
    P.glow(img, lp.x + 21, 67, 13, 'soul')          # light first, so the glass keeps its own tones
    spr(img, lp.x + 15, 60, VOID_LANTERN)
    st = (lp.x + 11, 90, 19, 50)
    P.ink_outline(img, st, 'ink_0', radius=1, fill_colour=VOID[0])
    P.hline(img, st[0] + 1, st[0] + st[2] - 2, st[1] + 1, VOID[1])
    P.vline(img, st[0] + 1, st[1] + 1, st[1] + st[3] - 2, VOID[1])
    P.vline(img, st[0] + st[2] - 2, st[1] + 2, st[1] + st[3] - 2, INK[1])
    P.hline(img, st[0] + 2, st[0] + st[2] - 2, st[1] + st[3] - 2, INK[1])
    for i, k in enumerate((0, 2, 4)):
        rune(img, st[0] + 7, st[1] + 7 + i * 13, k)
    spr(img, st[0] - 2, st[1] + st[3], ['o' * (st[2] + 4), 'o' + 'U' * (st[2] + 2) + 'o', 'o' * (st[2] + 4)],
        VOID_KEY)
    spr(img, lp.x + 10, floor - 8, CRYSTALS, VOID_KEY, flip_x=True)

    # --- right panel: void niche, a chained gold key, runes, ledge with void
    #     crystals ----------------------------------------------------------
    nx, ny = rp.x + 8, 16
    interior = P.arch_niche(img, (nx, ny, 23, 36), seed=seed, ramp=(INK[0], VOID[0], VOID[1], VOID[1]),
                            interior=INK[0])
    swirl = [(11, 9, VOID[0]), (12, 9, VOID[0]), (13, 10, VOID[0]), (14, 12, VOID[1]), (14, 13, VOID[0]),
             (13, 15, VOID[0]), (11, 16, VOID[1]), (9, 15, VOID[0]), (8, 13, VOID[0]), (8, 12, VOID[1]),
             (9, 11, VOID[0]), (10, 21, VOID[0]), (12, 22, VOID[1]), (14, 23, VOID[0]), (16, 21, VOID[0]),
             (7, 24, VOID[0]), (6, 19, VOID[1]), (11, 12, SOUL[0]), (11, 13, SOUL[1]), (15, 28, SOUL[0]),
             (7, 29, SOUL[0]), (12, 31, VOID[0])]
    for (dx, dy, col) in swirl:
        if (nx + dx, ny + dy) in interior:
            P.put(img, nx + dx, ny + dy, col)
    P.glow(img, nx + 11, ny + 13, 9, 'soul')
    P.chain(img, rp.x + 19, 58, rp.x + 19, 76, seed=seed + 2)
    spr(img, rp.x + 16, 77, GOLD_KEY)
    rune(img, rp.x + 5, 98, 1)
    rune(img, rp.x + 27, 108, 3)
    lx, ly = rp.x + 5, 136
    ledge(img, lx, ly, 27, ramp=OBSIDIAN)
    spr(img, lx + 6, ly - 9, CRYSTALS, VOID_KEY)
    P.glow(img, lx + 13, ly - 5, 8, 'soul')
    P.crack(img, rp.x + 30, 150, 10, seed=seed, colour=INK[0], light=VOID[1])
    rune(img, rp.x + 10, 156, 2)

    # --- strips ---
    top_chains(img, a, seed)
    for x0, x1 in ((8, 120), (136, a.w - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=seed + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3); P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur')
    C.finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------
# CRAFTING: blacksmith's anvil and tool rack
# ---------------------------------------------------------------------------

ANVIL_SPANS = [(7, 33), (3, 33), (0, 33), (1, 33), (4, 33), (9, 32), (12, 29), (14, 27), (14, 27),
               (13, 28), (11, 30), (9, 32), (8, 33), (8, 33)]

RACK_HAMMER = ['..ooo..', '..o3o..', '..o2o..', '..o2o..', '..o1o..', 'ooooooo', 'odccbao', 'obbbaao',
               'ooooooo']
RACK_CHISEL = ['ooo', 'odo', 'oco', 'o3o', 'o2o', 'o1o', 'oco', 'obo', '.o.']
RACK_PUNCH = ['ooo', 'odo', 'oco', 'oco', 'obo', 'obo', '.o.']
RACK_TONGS = ['ooo.ooo', 'oco.oao', 'oco.oao', 'oco.oao', 'oco.oao', 'oco.oao', 'oco.oao', '.ocoao.',
              '..odo..', '..oco..', '.oaoco.', 'oao.oco', 'oao.oco', 'oao.oco', 'oo...oo']
RACK_FILE = ['ooo', 'o3o', 'o2o', 'o2o', 'o1o', 'ooo', 'odo', 'oco', 'obo', 'oco', 'obo', 'oco', 'obo',
             'oco', 'obo', '.o.']
RACK_SLEDGE = ['..ooo..', '..o3o..', '..o2o..', '..o2o..', '..o2o..', '..o2o..', '..o1o..', 'ooooooo',
               'odcccbo', 'occcbao', 'obbbaao', 'ooooooo']
HORSESHOE = ['..ooooooo..', '.oddccccbo.', 'odcooooobbo', 'odo.....oao', 'oco.....oao', 'odo.....oao',
             'oco.....obo', 'odo.....oao', 'ooo.....ooo']
BUCKET = [
    '.oooooooooooo.',
    'odcccccccccbao',
    'oiibOOOOOOOOao',
    'ooooooooooooo.',
    '.o32122212210o',
    '.odcccccccbbao',
    '.o32122212210o',
    '.o32122212210o',
    '..o321221220o.',
    '..odccccccbao.',
    '..o321221220o.',
    '..oooooooooo..',
]
BUCKET = [r.ljust(14, '.') for r in BUCKET]


def paint_bellows(img, x, y):
    """Leather bellows hanging from a hook: two wooden boards (umber_3 lit
    top, umber_2 bottom), pleated umber leather between them, handles to the
    left, an iron nozzle to the right."""
    spans = [(1, 9), (0, 13), (0, 16), (0, 19), (0, 22), (0, 22), (0, 19), (0, 16), (0, 13), (1, 9)]
    inside = shape(img, x, y, spans, UMBER[2], UMBER[1], UMBER[0], top=UMBER[2])
    for j in (3, 6):                                            # leather pleats, zigzag
        a, b = spans[j]
        for i in range(a + 2, b - 1):
            jj = j + (1 if (i // 2) % 2 else 0) - (1 if j == 6 else 0)
            if (i, jj) in inside and (i, jj - 1) in inside:
                P.put(img, x + i, y + jj, UMBER[0])
                P.put(img, x + i, y + jj - 1, UMBER[2])
    for j, (a, b) in enumerate(spans):                          # the two boards
        if j in (1, 8):
            P.hline(img, x + a + 1, x + b - 2, y + j, UMBER[3] if j == 1 else UMBER[2])
    P.rivet(img, x + 4, y + 1, 'gold', 2)
    spr(img, x - 5, y, ['ooooo', 'o332o', '.oooo'])          # upper handle
    spr(img, x - 5, y + 7, ['.oooo', 'o221o', 'ooooo'])      # lower handle
    spr(img, x + 22, y + 3, ['ooo..', 'occoo', 'obbao', 'ooooo'])
    P.vline(img, x + 6, y - 2, y - 1, INK[1])                   # hook cord
    return inside


def paint_anvil(img, x, y):
    """A smith's anvil, horn to the left, standing on the inventory band's
    ledge: iron_3 lit face, iron_2 left flank, iron_0 right, a hardy hole."""
    shape(img, x, y, ANVIL_SPANS, IRON[2], IRON[1], IRON[0], top=IRON[3])
    for i in range(5, 10):
        P.put(img, x + i, y + 3, IRON[0])
    P.hline(img, x + 10, x + 31, y + 4, IRON[0])
    P.put(img, x + 28, y + 1, INK[0]); P.put(img, x + 29, y + 1, INK[0])   # hardy hole
    P.put(img, x + 23, y + 2, IRON[0])                                      # hammer pit
    P.hline(img, x + 12, x + 30, y + 11, IRON[2])                           # lit top of the foot
    return x + 18, y - 2


def paint_crafting_bg(seed=45):
    key = 'crafting'
    s = geo.skin(key)
    img = C.base_background(key, seed=seed)

    # --- the iron tool rack: hammer, chisel and punch above the result well;
    #     tongs, file and sledge in the open column to its right ------------
    P.ink_outline(img, (120, 16, 53, 4), 'ink_0', radius=1, fill_colour=IRON[1])
    P.hline(img, 121, 171, 17, IRON[2]); P.hline(img, 122, 171, 18, IRON[0])
    P.put(img, 122, 17, IRON[3]); P.put(img, 123, 17, IRON[3]); P.put(img, 124, 17, IRON[3])
    for rx in (121, 146, 169):
        P.rivet(img, rx, 17, 'dark', 2)
    spr(img, 123, 20, RACK_HAMMER)
    spr(img, 133, 20, RACK_CHISEL)
    spr(img, 139, 20, RACK_PUNCH)
    spr(img, 148, 20, RACK_TONGS)
    spr(img, 157, 20, RACK_FILE)
    spr(img, 162, 20, RACK_SLEDGE)

    # --- above the arrow: leather bellows on a hook --------------------------
    paint_bellows(img, 94, 17)
    # --- left: a horseshoe on a nail above the toggle, quench bucket below --
    spr(img, 9, 19, HORSESHOE)
    P.put(img, 14, 18, INK[0]); P.put(img, 14, 17, IRON[2])
    spr(img, 7, 59, BUCKET)

    # --- the anvil, a hot ingot, sparks ------------------------------------
    ax, ay = 104, 58
    cx, cy = paint_anvil(img, ax, ay)
    spr(img, cx - 3, ay - 2, ['ooooooo', 'oefFFfo'])
    P.glow(img, cx, cy, 10, 'ember')
    sparks = [(-3, -3, EMBER[2]), (-6, -5, EMBER[1]), (-9, -6, EMBER[0]), (3, -4, EMBER[2]),
              (6, -6, EMBER[1]), (10, -7, EMBER[1]), (14, -9, EMBER[0]), (18, -10, EMBER[0]),
              (0, -5, EMBER[1]), (1, -8, EMBER[0])]
    for (dx, dy, col) in sparks:
        P.put(img, cx + dx, ay + dy, col)
    for (x, y, col) in ((149, 55, EMBER[1]), (153, 52, EMBER[0]), (165, 57, EMBER[0])):
        P.put(img, x, y, col)

    C.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------

def out_paths(root, key):
    s = geo.skin(key)
    bg = Path(root) / 'menu' / f'{key}.png'
    frames = {a.id: Path(root) / 'frames' / key / f'{a.id}.png' for a in s.art_layers}
    return bg, frames


def paint(key, root):
    bg_path, frame_paths = out_paths(root, key)
    if key == 'trashcan':
        C.save_png(paint_trashcan_bg(), bg_path)
        C.save_png(paint_trashcan_frame(), frame_paths['menu_frame'])
    elif key == 'ender_chest':
        C.save_png(paint_ender_bg(), bg_path)
        C.save_png(paint_ender_frame(), frame_paths['menu_frame'])
    elif key == 'crafting':
        C.save_png(paint_crafting_bg(), bg_path)
    else:
        raise SystemExit(f'not my skin: {key}')
    print('PAINTED', key, '->', bg_path, *frame_paths.values())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out-root', default=str(DEFAULT_ROOT),
                    help='texture root (default: pack-source/assets/quasar_gui/textures)')
    ap.add_argument('--skin', action='append', choices=SKINS, help='paint only this skin (repeatable)')
    args = ap.parse_args(argv)
    for key in args.skin or SKINS:
        paint(key, args.out_root)


if __name__ == '__main__':
    main()
