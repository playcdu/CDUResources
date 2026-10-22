#!/usr/bin/env python3
"""Render the style guide's reference drawings into evidence/cozy/reference/.

    python tools/cozy/render_references.py

palette.png          master palette swatches with names and RGB
wells.png            well anatomy (d1 lip / d2 wall / d3 stitch) at 10x
buttons.png          every button grammar in all six states, at 4x
icons.png            icon and motif sprites at 8x
background-anatomy.png  base_background(template_chest_3) with labelled zones
frame-anatomy.png    base_frame(template_chest_3) with labelled zones
typeface-specimen.png (in evidence/cozy/) via lettering.specimen()

Nothing here writes to pack-source. Licence: MIT.
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from PIL import Image, ImageDraw  # noqa: E402

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import icons  # noqa: E402
import lettering as L  # noqa: E402
import palette as PAL  # noqa: E402
import preview  # noqa: E402
import primitives as P  # noqa: E402

OUT = geo.ROOT / 'evidence' / 'cozy' / 'reference'
BG = (40, 34, 36, 255)
FG = (238, 226, 200)
DIM = (180, 165, 140)


def _font(n=13):
    return preview._font(n)


def palette_sheet():
    rows = list(PAL.RAMPS.items())
    sw, sh = 92, 46
    img = Image.new('RGBA', (130 + 5 * sw, 20 + len(rows) * (sh + 8)), BG)
    d = ImageDraw.Draw(img)
    for r, (name, cols) in enumerate(rows):
        y = 14 + r * (sh + 8)
        d.text((10, y + 14), name.upper(), fill=FG, font=_font(14))
        for i, c in enumerate(cols):
            x = 120 + i * sw
            d.rectangle((x, y, x + sw - 6, y + sh), fill=c + (255,))
            n = PAL.name_of(c)
            t = (30, 22, 20) if PAL.luminance(c) > 120 else (245, 235, 215)
            d.text((x + 4, y + 4), n, fill=t, font=_font(12))
            d.text((x + 4, y + 22), '%d,%d,%d' % c, fill=t, font=_font(11))
    return img


def wells_sheet():
    """A 3x2 grid of clearances on wood and a single well on parchment."""
    img = Image.new('RGBA', (84, 40), (0, 0, 0, 0))
    P.planks(img, (0, 0, 84, 40), PAL.WOOD, 3, board=9)
    holes = [geo.Rect(5, 6, 20, 20), geo.Rect(23, 6, 20, 20)]
    P.parchment_panel(img, (50, 2, 32, 36), 2, fibres=False)
    P.stitched_well(img, holes)
    P.stitched_well(img, [geo.Rect(56, 10, 20, 20)], thread='parch_0')
    for r in holes + [geo.Rect(56, 10, 20, 20)]:
        P.fill(img, r.tuple(), (0, 0, 0, 0))
    s = 10
    big = Image.new('RGBA', (img.width * s, img.height * s + 120), BG)
    chk = Image.new('RGBA', img.size, (150, 150, 150, 255))
    chk.alpha_composite(img)
    big.alpha_composite(chk.resize((img.width * s, img.height * s), Image.Resampling.NEAREST))
    d = ImageDraw.Draw(big)
    for r in holes + [geo.Rect(56, 10, 20, 20)]:
        d.rectangle((r.x * s, r.y * s, r.right * s - 1, r.bottom * s - 1), outline=(255, 0, 255))
    notes = ['magenta = 20x20 alpha-zero clearance (vanilla slot shows through)',
             'd1: ink_1 lip on every side  |  d2: top/left wall 2 steps darker, bottom/right 1 step lighter',
             'd3: running stitch 2 on / 2 off (thread parch_2 on wood, parch_0 on paper)',
             'adjacent clearances merge into one hole: frames only appear on the outside']
    for i, n in enumerate(notes):
        d.text((10, img.height * s + 10 + i * 24), n, fill=FG, font=_font(15))
    return big


REF_BUTTONS = [
    ('primary  (brass-plated plank)', 'economy_hub', 'auction'),
    ('primary 36x18', 'auction_house', 'sell'),
    ('secondary  (linen tag)', 'economy_hub', 'history'),
    ('secondary, eyelet dropped for fit', 'economy_hub', 'privacy'),
    ('secondary, two lines -> SPRIG', 'economy_hub', 'chest_shops'),
    ('danger  (red wax)', 'economy_hub', 'close'),
    ('danger 108x18', 'chest_shop_listing_enabled', 'toggle'),
    ('page turn: previous', 'auction_house', 'previous'),
    ('page turn: next', 'auction_house', 'next'),
    ('close icon (wax seal + X)', 'auction_house', 'close'),
    ('balance icon (coin purse)', 'chest_shop', 'balance'),
    ('rank icon (rosette)', 'economy_hub', 'rank'),
    ('balance column 18x72', 'auction_house', 'balance'),
]


def buttons_sheet(scale=4):
    rows = []
    for title, key, bid in REF_BUTTONS:
        normal = C.paint_button(key, bid, seed=1)
        rows.append((title, key, bid, C.button_states(normal, key, bid)))
    colw = 108 * scale // 2 + 16
    W = 250 + 6 * colw
    H = 34 + sum(max(st['normal'].height * scale, 30) + 14 for *_, st in rows)
    img = Image.new('RGBA', (W, H), BG)
    d = ImageDraw.Draw(img)
    for i, st in enumerate(geo.STATES):
        d.text((250 + i * colw, 10), st, fill=FG, font=_font(14))
    y = 34
    for title, key, bid, states in rows:
        d.text((10, y + 2), title, fill=FG, font=_font(13))
        b = geo.skin(key).button(bid)
        d.text((10, y + 20), f'{key}/{bid} {b.w}x{b.h}', fill=DIM, font=_font(11))
        for i, st in enumerate(geo.STATES):
            im = states[st]
            sc = scale if im.width * scale <= colw - 8 else max(1, (colw - 8) // im.width)
            cell = Image.new('RGBA', im.size, (96, 70, 52, 255))
            cell.alpha_composite(im)
            img.alpha_composite(cell.resize((im.width * sc, im.height * sc), Image.Resampling.NEAREST),
                                (250 + i * colw, y))
        y += max(states['normal'].height * scale, 30) + 14
    return img


def icons_sheet(scale=8):
    names = list(icons.ICONS) + list(icons.MOTIFS)
    cells = []
    for n in names:
        rows, key = (icons.ICONS.get(n) or icons.MOTIFS[n])
        w, h = P.sprite_size([r.ljust(max(len(q) for q in rows), '.') for r in rows])
        im = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
        if n in icons.MOTIFS:
            icons.draw_motif(im, n, 1, 1)
        else:
            P.sprite(im, 1, 1, rows, key)
        cells.append((n, im))
    seal = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
    icons.close_seal(seal, (0, 0, 18, 18))
    cells.insert(0, ('close', seal))
    for e in icons.EMBLEMS:
        im = Image.new('RGBA', (15, 17), (0, 0, 0, 0))
        P.wax_seal(im, 7, 7, 7, PAL.BERRY, 2, drip=True, emblem=e)
        cells.append(('seal:' + e, im))
    W = 16 + len(cells) * (18 * scale // 2 + 24)
    img = Image.new('RGBA', (min(W, 1500), 20), BG)
    x, y, rowh = 10, 10, 0
    placed = []
    for n, im in cells:
        sw, shh = im.width * scale // 2, im.height * scale // 2
        if x + sw > 1480:
            x, y, rowh = 10, y + rowh + 30, 0
        placed.append((n, im, x, y, sw, shh))
        x += max(sw, 90) + 16
        rowh = max(rowh, shh)
    img = Image.new('RGBA', (1500, y + rowh + 40), BG)
    d = ImageDraw.Draw(img)
    for n, im, x, y, sw, shh in placed:
        bgc = Image.new('RGBA', im.size, (212, 190, 150, 255))
        bgc.alpha_composite(im)
        img.alpha_composite(bgc.resize((sw, shh), Image.Resampling.NEAREST), (x, y))
        d.text((x, y + shh + 4), n, fill=FG, font=_font(12))
    return img


def _annotate(img, scale, notes, pad_right=330):
    big = img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)
    out = Image.new('RGBA', (big.width + pad_right, max(big.height, 40 + 22 * len(notes))), BG)
    out.alpha_composite(big)
    d = ImageDraw.Draw(out)
    for i, (rect, colour, text) in enumerate(notes):
        if rect is not None:
            x, y, w, h = rect
            d.rectangle((x * scale, y * scale, (x + w) * scale - 1, (y + h) * scale - 1), outline=colour, width=2)
        d.rectangle((big.width + 12, 14 + i * 22, big.width + 24, 26 + i * 22), fill=colour)
        d.text((big.width + 30, 12 + i * 22), text, fill=FG, font=_font(13))
    return out


def background_anatomy():
    key = 'template_chest_3'
    s = geo.skin(key)
    img = Image.new('RGBA', (s.width, s.height), (150, 150, 150, 255))
    img.alpha_composite(C.base_background(key, seed=4))
    t, inv = C.bands(key)
    notes = [
        (t.tuple(), (240, 170, 60), 'title band rows 2-14 (parchment)'),
        (s.text_safe.tuple(), (170, 80, 200), 'text-safe [8,5,160,11]: live title'),
        (inv.tuple(), (90, 170, 230), 'inventory band (live "Inventory")'),
        (s.content_bbox.tuple(), (255, 0, 255), 'native well grid (alpha 0)'),
        (s.player_bbox.tuple(), (255, 0, 255), '36 player wells (alpha 0)'),
        ((0, 16, 6, 56), (120, 220, 120), 'side margin 6 px: rim + well frame'),
        (s.advance_pin.tuple(), (255, 60, 60), 'advance pin [175,0,1,3] alpha 255'),
    ]
    return _annotate(img, 4, notes)


def frame_anatomy():
    key = 'template_chest_3'
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, seed=4)
    notes = [
        (a.top_strip.tuple(), (240, 170, 60), 'top strip 8 px: heading ribbon (SPRIG)'),
        (a.bottom_strip.tuple(), (240, 170, 60), 'bottom strip 8 px: beam, rope, tacks'),
        (a.left_panel.tuple(), (120, 220, 120), 'left panel 40 px: tag, shelf, motifs'),
        (a.right_panel.tuple(), (120, 220, 120), 'right panel 40 px: motifs, optional lines'),
        (a.container.tuple(), (255, 0, 255), 'native container: fully alpha 0'),
        ((a.pin[0], a.pin[1], 1, 1), (255, 60, 60), f'advance pin {a.pin} alpha 255'),
    ]
    bg = Image.new('RGBA', img.size, (128, 128, 128, 255))
    bg.alpha_composite(img)
    return _annotate(bg, 3, notes)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        'palette.png': palette_sheet(),
        'wells.png': wells_sheet(),
        'buttons.png': buttons_sheet(),
        'icons.png': icons_sheet(),
        'background-anatomy.png': background_anatomy(),
        'frame-anatomy.png': frame_anatomy(),
    }
    for name, im in outputs.items():
        im.convert('RGB').save(OUT / name)
        print('WROTE', OUT / name)
    spec = geo.ROOT / 'evidence' / 'cozy' / 'typeface-specimen.png'
    L.specimen().save(spec)
    print('WROTE', spec)


if __name__ == '__main__':
    main()
