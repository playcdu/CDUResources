#!/usr/bin/env python3
"""Cozy painter "templates": template_chest_1 .. template_chest_6.

    python tools/cozy/paint_templates.py                      # paint all six into pack-source
    python tools/cozy/paint_templates.py --skin template_chest_3
    python tools/cozy/paint_templates.py --out-root DIR       # DIR laid out like pack-source

Generic native-content chest templates (9 .. 54 native wells, heights 132 ..
222) intended for future screens: plain warm wood framing, deliberately
restrained, no family story. Each skin owns one background and one outer
frame (no buttons).

* Background: the shared cozy sheet (oiled planks, parchment title and
  inventory bands, stitched wells) plus quiet hand touches that sit outside
  every well and glyph row: brass L-brackets in the bottom corners and a
  pressed sprig of chamomile pinned at the far right of the inventory band.
* Frame: darker vertical boards, nailed to the top and bottom beams; the
  UTILITY heading ribbon; and side panels that are composed for each height
  (modules are added as the frame grows and spaced evenly, never cropped):
  left - a wooden peg with the UTILITY tag on twine, a shelf with a brass
  chamberstick candle and a ball of twine, bundles of drying herbs on a rail,
  a wicker basket on a peg (h >= 184), a spare blank tag (h >= 220), and a
  potted herb beside a little log pile on the bottom beam; right - a lantern
  hanging from an iron hook, a shelf of folded linens, blank linen tags on
  twine, a trailing ivy, a pinned botanical card with a curled corner
  (h >= 202), and a shelf with a honey jar and a bud vase. No words other
  than the authored UTILITY heading; nothing implies a function.

Deterministic: fixed seeds, no clock. Every pixel is placed by hand-authored
sprites or the shared primitives. Licence: code MIT; artwork CC0-1.0.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import icons  # noqa: E402
import lettering as L  # noqa: E402
import primitives as P  # noqa: E402
from palette import ASH, BRASS, EMBER, INK, PARCHMENT, SAGE, WOOD  # noqa: E402

KEYS = tuple(f'template_chest_{n}' for n in range(1, 7))
# Seeds tuned by eye per skin (board layout, grain, fibres); keep them fixed.
SEEDS = {
    'template_chest_1': 31,
    'template_chest_2': 32,
    'template_chest_3': 33,
    'template_chest_4': 34,
    'template_chest_5': 35,
    'template_chest_6': 36,
}

# ---------------------------------------------------------------------------
# Hand-authored sprites (all original, CC0-1.0)
# ---------------------------------------------------------------------------

K_WOODEN = {'o': INK[1], 'O': INK[0], '0': WOOD[0], '1': WOOD[1], '2': WOOD[2], '3': WOOD[3], '4': WOOD[4]}

# A turned wooden peg seen end-on, driven into the board.
PEG = [
    '.ooo.',
    'o443o',
    'o432o',
    'o321o',
    '.oOo.',
]

# A small round nail head (brass), 2x2 with a lit pixel.
NAIL = ['3n', 'nm']
K_NAIL = {'3': BRASS[3], 'n': BRASS[1], 'm': BRASS[0]}

# Brass chamberstick: tallow candle with a drip, dish and finger loop.
CHAMBERSTICK = [
    '....e........',
    '...eEe.......',
    '...eEe.......',
    '....E........',
    '....O........',
    '..ooooo......',
    '..o332o......',
    '..3322o......',
    '.o33221o.....',
    '.oo3221o.....',
    '..o3221o.....',
    '..o3221o..oo.',
    'ooooooooooo.o',
    'oBbbbbbbbnoo.',
    '.oBnnnnnnmo..',
    '..ooooooooO..',
]
K_CHAMBER = {'e': EMBER[1], 'E': EMBER[2], 'O': INK[0], 'o': INK[1],
             '3': PARCHMENT[3], '2': PARCHMENT[2], '1': PARCHMENT[1],
             'B': BRASS[3], 'b': BRASS[2], 'n': BRASS[1], 'm': BRASS[0]}

# A ball of garden twine, wound in diagonal bands.
TWINE_BALL = [
    '..ooooo..',
    '.o32202o.',
    'o3220221o',
    'o2202201o',
    'o2022011o',
    'o0220101o',
    '.o10110o.',
    '..ooOOo..',
]
K_TWINE = {'o': INK[1], 'O': INK[0], '3': PARCHMENT[3], '2': PARCHMENT[2],
           '1': PARCHMENT[1], '0': PARCHMENT[0]}

# Bundles of herbs hung upside down to dry: twine loop, bound stems, leafy heads.
SAGE_BUNDLE = [
    '....t....',
    '...t.t...',
    '...oto...',
    '..ossso..',
    '..oTtTo..',
    '..osSso..',
    '.ossSsso.',
    '.ogsgsgo.',
    'oGgGgGgdo',
    'ogGdGgGdo',
    'oGgGdGgdo',
    '.ogGgdGo.',
    '.oGdgGdo.',
    '..ogdgo..',
    '...odo...',
    '....o....',
]
CHAMOMILE_BUNDLE = [
    '....t....',
    '...t.t...',
    '...oto...',
    '..ossso..',
    '..oTtTo..',
    '..osSso..',
    '.osgSgso.',
    'owsgsgswo',
    'wywgsgwyw',
    'owGgsgGwo',
    '.gwgwgdg.',
    'owywgwyo.',
    '.owgdgwo.',
    '..ogdgo..',
    '...owo...',
    '....o....',
]
K_HERBS = {'o': INK[1], 't': PARCHMENT[1], 'T': PARCHMENT[0], 's': WOOD[3], 'S': WOOD[2],
           'g': SAGE[1], 'G': SAGE[2], 'd': SAGE[0], 'w': PARCHMENT[3], 'y': BRASS[2]}

# A wicker basket hung by its handle (the peg is drawn separately on top).
BASKET = [
    '....oooooo....',
    '...o443332o...',
    '..o3o....o2o..',
    '..o3o....o2o..',
    'oooooooooooooo',
    'o443443443432o',
    'oooooooooooooo',
    '.o3232323231o.',
    '.o2323232321o.',
    '.o3232323211o.',
    '..o23232321o..',
    '..o32323211o..',
    '...oooooooO...',
]
K_BASKET = {'o': INK[1], 'O': INK[0], '4': WOOD[4], '3': WOOD[3], '2': WOOD[2], '1': WOOD[1]}

# End grain of a split log: bark ring, sapwood, heartwood.
LOG_END = [
    '.oooo.',
    'o1441o',
    'o4334o',
    'o4324o',
    'o1441o',
    '.oOOo.',
]
K_LOG = {'o': INK[1], 'O': INK[0], '1': WOOD[1], '4': WOOD[4], '3': WOOD[3], '2': WOOD[2]}

# Three folded cloths stacked on a shelf: cream linen, sage, striped linen.
LINENS = [
    '.ooooooooooo..',
    'o33333333332o.',
    'o22222222221o.',
    '.oooooooooooo.',
    'oGGGGGGGGGGGgo',
    'oggggggggggddo',
    '.oooooooooooo.',
    'o3e3e3e3e3e31o',
    'o222222222211o',
    '.ooooooooooOO.',
]
K_LINENS = {'o': INK[1], 'O': INK[0], '3': PARCHMENT[3], '2': PARCHMENT[2], '1': PARCHMENT[1],
            'G': SAGE[2], 'g': SAGE[1], 'd': SAGE[0], 'e': EMBER[1]}

# Amber honey in a glass jar, linen cover tied down with twine.
HONEY_JAR = [
    '.oooooooo.',
    'o33333322o',
    'o0tt0tt00o',
    '.o2o2oo2o.',
    '.oooooooo.',
    'o3bbbbbbno',
    'o3bBbbbnmo',
    'obBbbbbnmo',
    'obbbbbnnmo',
    'obbbbnnmmo',
    '.onnnnmmo.',
    '..oooooo..',
]
K_HONEY = {'o': INK[1], '3': PARCHMENT[3], '2': PARCHMENT[1], '0': PARCHMENT[0], 't': WOOD[3],
           'B': BRASS[3], 'b': BRASS[2], 'n': BRASS[1], 'm': BRASS[0]}

# A stoneware bud vase holding a single sprig.
BUD_VASE = [
    '..G.g.',
    '.gGgd.',
    '..gGg.',
    '.d.s..',
    '...s..',
    '..ooo.',
    '..o3o.',
    '.o322o',
    'o32221o',
    'o32211o',
    'o22110o',
    '.o110o.',
    '..ooo..',
]
K_VASE = {'o': INK[1], '3': PARCHMENT[3], '2': PARCHMENT[2], '1': PARCHMENT[1], '0': PARCHMENT[0],
          'g': SAGE[1], 'G': SAGE[2], 'd': SAGE[0], 's': SAGE[0]}

# Iron wall hook from which the lantern hangs.
HOOK = [
    'oooo.',
    'oaao.',
    'oooao',
    '...ao',
    '..oao',
    '..oo.',
]
K_HOOK = {'o': INK[1], 'a': ASH[1]}

# Small brass L-bracket for the background's bottom corners (bottom-left form).
BG_BRACKET = ['n..', 'n..', 'bnm']
K_BG_BRACKET = {'b': BRASS[3], 'n': BRASS[2], 'm': BRASS[0]}

# Pressed chamomile sprig for the inventory band.
PRESSED_SPRIG = [
    '.....w.w....',
    '....wywyw...',
    '.....wsw..g.',
    '.g....s..gG.',
    'gGg..s..gGd.',
    '.dGg.s.gd...',
    '...dss......',
    '....s.......',
]
# A pressed fern frond for the botanical card.
PRESSED_FERN = [
    '.....g....',
    '....gGd...',
    '.G...s..G.',
    'gGd..s.dGg',
    '.dGg.sgGd.',
    '.Gg..s..g.',
    'gGdd.sddGg',
    '....ss....',
    '....s.....',
    '...s......',
]
K_SPRIG = {'w': PARCHMENT[3], 'y': BRASS[2], 's': SAGE[0], 'g': SAGE[1], 'G': SAGE[2], 'd': SAGE[0]}


def sprite(img, x, y, rows, key, flip_x=False):
    rows = [r.ljust(max(len(q) for q in rows), '.') for r in rows]
    P.sprite(img, x, y, rows, key, flip_x=flip_x)
    return P.sprite_size(rows)


# ---------------------------------------------------------------------------
# Small hand-drawn helpers (local to this painter)
# ---------------------------------------------------------------------------

def shelf(img, x, y, w, seed):
    """A short oiled plank shelf (5 rows) on two brass brackets; returns top y."""
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})
    return y


def blank_tag(img, x, y, hem, seed):
    """A 7x12 blank linen tag hanging from twine with a dyed hem (no words)."""
    P.linen_tag(img, (x, y, 7, 12), eyelet=None, seed=seed)
    P.put(img, x + 3, y + 2, INK[0])                     # string hole
    P.put(img, x + 3, y + 1, PARCHMENT[1])
    P.fill(img, (x + 1, y + 9, 5, 2), hem[1])
    P.hline(img, x + 1, x + 5, y + 8, hem[2])


def blank_card(img, x, y, w, h, seed):
    """A pinned botanical card: a pressed sprig, three empty ruled lines (no
    writing), curled bottom-right corner."""
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=False)
    for k in (h - 11, h - 8):
        P.hline(img, x + 3, x + w - 4, y + k, PARCHMENT[1])
    P.hline(img, x + 3, x + w - 8, y + h - 5, PARCHMENT[1])
    sprite(img, x + w // 2 - 5, y + 4, PRESSED_FERN, K_SPRIG)
    P.page_curl(img, (x, y, w, h), 'br', 5, behind=WOOD[0])
    P.tack(img, x + w // 2, y + 1)


def ivy(img, x, y0, y1, seed):
    """A trailing ivy stem from (x, y0) down to y1 with alternating leaves."""
    P.ink_line(img, x, y0, x, y1, SAGE[0], wobble=1, seed=seed)
    k = 0
    for yy in range(y0 + 3, y1 - 4, 9):
        if k % 2:
            P.leaf(img, x + 1, yy, 'ne', small=(k % 3 == 2))
        else:
            P.leaf(img, x - 6 if k % 3 != 2 else x - 4, yy, 'nw', small=(k % 3 == 2))
        k += 1


def board_seams(img, panel, y):
    """x positions of the vertical board seams (ink_1) crossing ``panel`` at row y."""
    seam = INK[1] + (255,)
    return [x for x in range(panel.x + 1, panel.right - 1) if img.getpixel((x, y)) == seam]


def nail_boards(img, a):
    """Two brass nails at the top and bottom of every side board, where it is
    fixed to the beams."""
    c = a.container
    top, bot = c.y + 1, c.bottom - 3
    for panel in (a.left_panel, a.right_panel):
        lo = panel.x + (1 if panel.x == 0 else 3)
        hi = panel.right - (2 if panel.right == a.w else 0)
        edges = [lo - 1] + board_seams(img, panel, c.y + 30) + [hi]
        for e0, e1 in zip(edges, edges[1:]):
            if e1 - e0 < 6:
                continue
            nx = (e0 + e1) // 2
            for ny in (top, bot):
                sprite(img, nx, ny, NAIL, K_NAIL)


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def paint_background(key):
    s = geo.skin(key)
    seed = SEEDS[key]
    img = C.base_background(key, seed=seed)
    tband, iband = C.bands(key)
    # A pressed chamomile sprig pinned at the far right of the inventory band,
    # well clear of the live "Inventory" label on the left.
    sx = iband.right - 18
    sy = iband.y + (iband.h - len(PRESSED_SPRIG)) // 2
    sprite(img, sx, sy, PRESSED_SPRIG, K_SPRIG)
    P.tack(img, sx + 6, sy + 6, small=True)
    # Brass L-brackets screwed over the bottom corners, with a little wear.
    H, W = s.height, s.width
    sprite(img, 1, H - 4, BG_BRACKET, K_BG_BRACKET)
    sprite(img, W - 4, H - 4, BG_BRACKET, K_BG_BRACKET, flip_x=True)
    P.dither_patch(img, (4, H - 4, 3, 2), WOOD[1], 0.25)
    P.dither_patch(img, (W - 8, H - 4, 3, 2), WOOD[1], 0.25)
    geo.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def _distribute(top, bottom, modules):
    """Place module heights evenly between top and bottom (exclusive); returns ys."""
    total = sum(h for h in modules)
    gap = max(3, (bottom - top - total) // (len(modules) + 1))
    ys, y = [], top + gap
    for h in modules:
        ys.append(y)
        y += h + gap
    return ys


def peg_tag(img, lp, text, y, seed):
    """A turned wooden peg with the heading tag hung from it on a twine V."""
    cx = lp.x + 20
    tw = L.text_width(text, 'sprig')
    w = max(tw + 6, 14)
    x = lp.x + (lp.w - w) // 2
    P.twine(img, cx, y - 8, x + 4, y, sag=0)
    P.twine(img, cx, y - 8, x + w - 5, y, sag=0)
    C.side_tag(img, lp, text, y, seed)
    sprite(img, cx - 2, y - 11, PEG, K_WOODEN)


def log_pile(img, x, y):
    """Three split logs stacked end-on (13x11), top-left at (x, y)."""
    sprite(img, x, y + 5, LOG_END, K_LOG)
    sprite(img, x + 7, y + 5, LOG_END, K_LOG)
    sprite(img, x + 3, y, LOG_END, K_LOG)


def paint_left(img, a, seed):
    lp = a.left_panel
    H = a.h
    # -- fixed top: wooden peg, UTILITY tag on a twine V ----------------------
    peg_tag(img, lp, a.left_heading or a.heading or '', 23, seed)
    # -- fixed bottom: potted herb and a little log pile on the bottom beam ---
    base = a.container.bottom - 1          # last board row above the beam
    icons.draw_motif(img, 'herb_pot', lp.x + 4, base - 11)
    log_pile(img, lp.x + 18, base - 10)
    P.leaf(img, lp.x + 14, base - 4, 'ne', small=True)
    # -- middle modules, chosen by height -------------------------------------
    mods = ['candle_shelf', 'herbs']
    if H >= 184:
        mods.append('basket')
    if H >= 220:
        mods.insert(1, 'spare_peg')
    heights = {'candle_shelf': 24, 'herbs': 22, 'basket': 19, 'spare_peg': 19}
    ys = _distribute(34, base - 13, [heights[m] for m in mods])
    for m, y in zip(mods, ys):
        if m == 'candle_shelf':
            sy = y + 17
            shelf(img, lp.x + 4, sy, lp.w - 8, seed + 3)
            sprite(img, lp.x + 6, sy - 16, CHAMBERSTICK, K_CHAMBER)
            sprite(img, lp.x + 23, sy - 8, TWINE_BALL, K_TWINE)
            P.twine(img, lp.x + 31, sy - 3, lp.x + 33, sy + 1, sag=0)
            P.twine(img, lp.x + 33, sy + 5, lp.x + 32, sy + 9, sag=0)
            P.lantern_glow_ring(img, lp.x + 10, sy - 12, 12, strength=1)
        elif m == 'herbs':
            # a short rail on two pegs, two bundles hanging at different lengths
            P.plank(img, (lp.x + 5, y + 1, lp.w - 10, 3), WOOD, seed + 4, 'ink_1', radius=0, grain=0)
            sprite(img, lp.x + 9, y + 3, SAGE_BUNDLE, K_HERBS)
            sprite(img, lp.x + 21, y + 4, CHAMOMILE_BUNDLE, K_HERBS)
            for px in (lp.x + 4, lp.w - 8 + lp.x):
                sprite(img, px, y, ['.oo.', 'o43o', 'o21o', '.oo.'], K_WOODEN)
        elif m == 'basket':
            sprite(img, lp.x + 13, y + 3, BASKET, K_BASKET)
            sprite(img, lp.x + 18, y, PEG, K_WOODEN)
        elif m == 'spare_peg':
            # a single blank tag left hanging on its own peg
            sprite(img, lp.x + 9, y, PEG, K_WOODEN)
            P.twine(img, lp.x + 11, y + 4, lp.x + 15, y + 7, sag=0)
            blank_tag(img, lp.x + 12, y + 7, SAGE, seed + 5)


def paint_right(img, a, seed):
    rp = a.right_panel
    H = a.h
    x0 = rp.x + 2           # first board column right of the cast shadow
    cx = x0 + 18
    # -- fixed top: lantern hanging on a short chain from an iron hook --------
    sprite(img, cx - 4, 9, HOOK, K_HOOK)
    for yy in range(14, 17):
        P.put(img, cx - 1, yy, INK[1] if yy % 2 else ASH[0])
    P.lantern(img, cx - 4, 17)
    P.lantern_glow_ring(img, cx, 22, 14, strength=1)
    # -- fixed bottom: shelf with honey jar and bud vase ----------------------
    sh_y = a.container.bottom - 14
    shelf(img, x0 + 2, sh_y, rp.w - 8, seed + 6)
    sprite(img, x0 + 5, sh_y - 12, HONEY_JAR, K_HONEY)
    sprite(img, x0 + 18, sh_y - 13, BUD_VASE, K_VASE)
    # -- middle -----------------------------------------------------------------
    mods = ['linens', 'tags']
    if H >= 202:
        mods.append('card')
    heights = {'linens': 17, 'tags': 18, 'card': 30}
    ys = _distribute(28, sh_y - 16, [heights[m] for m in mods])
    tags_y = ys[mods.index('tags')]
    for m, y in zip(mods, ys):
        if m == 'linens':
            sy = y + 11
            shelf(img, x0 + 2, sy, rp.w - 8, seed + 8)
            sprite(img, x0 + 6, sy - 10, LINENS, K_LINENS)
            P.leaf(img, x0 + 23, sy - 5, 'ne', small=True)
            P.leaf(img, x0 + 26, sy - 6, 'ne')
        elif m == 'tags':
            P.twine(img, x0 + 1, y, rp.right - 3, y, sag=4)
            for k, (tx, hem) in enumerate(((x0 + 5, (WOOD[1], WOOD[2], WOOD[3])), (x0 + 16, SAGE), (x0 + 26, EMBER))):
                blank_tag(img, tx, y + (3 if k == 1 else 2), hem, seed + 7 + k)
        elif m == 'card':
            blank_card(img, x0 + 4, y + 2, 22, 26, seed + 9)
    # trailing ivy down the outer edge, from under the tags to the shelf
    ivy(img, rp.right - 6, tags_y + 18, sh_y - 1, seed)


def paint_frame(key):
    s = geo.skin(key)
    a = s.layer()
    seed = SEEDS[key]
    img = C.base_frame(key, a.id, seed=seed)
    nail_boards(img, a)
    paint_left(img, a, seed)
    paint_right(img, a, seed)
    # bottom beam: a rope run between two tacks, a sprig tucked into it
    H = a.h
    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0)
    P.tack(img, 10, H - 5)
    P.tack(img, a.w - 11, H - 5)
    # top beam: nails either side of the heading ribbon
    for nx in (24, 72, a.w - 74, a.w - 26):
        sprite(img, nx, 3, NAIL, K_NAIL)
    P.highlight_edge(img, (a.left_panel.x + 1, 9, a.left_panel.w - 2, H - 18), WOOD[2], 'l', broken=4, seed=seed)
    P.shadow_edge(img, (a.right_panel.x, 9, a.right_panel.w - 1, H - 18), INK[1], 'r')
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def paint(key, out_root=None):
    s = geo.skin(key)
    bg = paint_background(key)
    fr = paint_frame(key)
    root = Path(out_root) if out_root else geo.ROOT / 'pack-source'
    bg_path = root / s.asset
    fr_path = root / s.frame_path().relative_to(geo.ROOT / 'pack-source')
    C.save_png(bg, bg_path)
    C.save_png(fr, fr_path)
    return [bg_path, fr_path]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--skin', action='append', choices=KEYS, help='paint only this skin (repeatable)')
    ap.add_argument('--out-root', help='write into DIR laid out like pack-source instead of pack-source')
    args = ap.parse_args(argv)
    for key in args.skin or KEYS:
        for p in paint(key, args.out_root):
            print('WROTE', p)


if __name__ == '__main__':
    main()
