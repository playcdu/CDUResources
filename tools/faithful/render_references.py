#!/usr/bin/env python3
"""Render the Faithful style guide's reference drawings into evidence/faithful/reference/.

    python tools/faithful/render_references.py

palette.png             master palette swatches with names and RGB
wells.png               inset well anatomy (dark top/left, white bottom/right, mid corners) at 10x
buttons.png             every button grammar in all six states, at 4x
icons.png               icons and family pictograms at 8x
primitives.png          panel, stone buttons, plate, inset tile, arrows, accent line at 4x
background-anatomy.png  base_background(template_chest_3) with labelled zones
frame-anatomy.png       base_frame(economy_hub) with labelled zones
typeface-specimen.png   (in evidence/faithful/) via lettering.specimen()

Nothing here writes to pack-source. Licence: MIT.
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
for _p in (str(_HERE.parent), str(_HERE.parent / 'cozy')):
    if _p not in sys.path:
        sys.path.append(_p)

from PIL import Image, ImageDraw  # noqa: E402

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import icons  # noqa: E402
import lettering as L  # noqa: E402
import palette as PAL  # noqa: E402
import preview  # noqa: E402
import primitives as P  # noqa: E402

OUT = geo.ROOT / 'evidence' / 'faithful' / 'reference'
BG = (36, 36, 36, 255)
FG = (236, 236, 236)
DIM = (170, 170, 170)


def _font(n=13):
    return preview._font(n)


def palette_sheet():
    rows = list(PAL.RAMPS.items())
    sw, sh = 96, 46
    width = max(len(c) for _, c in rows)
    img = Image.new('RGBA', (130 + width * sw, 20 + len(rows) * (sh + 8)), BG)
    d = ImageDraw.Draw(img)
    for r, (name, cols) in enumerate(rows):
        y = 14 + r * (sh + 8)
        d.text((10, y + 14), name.upper(), fill=FG, font=_font(14))
        for i, c in enumerate(cols):
            x = 120 + i * sw
            d.rectangle((x, y, x + sw - 6, y + sh), fill=c + (255,), outline=(90, 90, 90))
            t = (20, 20, 20) if PAL.luminance(c) > 120 else (240, 240, 240)
            d.text((x + 4, y + 4), PAL.name_of(c), fill=t, font=_font(12))
            d.text((x + 4, y + 22), '%d,%d,%d' % c, fill=t, font=_font(11))
    return img


def wells_sheet():
    """A merged two-slot tray and a single well on the panel."""
    img = Image.new('RGBA', (86, 44), (0, 0, 0, 0))
    P.fill(img, (0, 0, 86, 44), PAL.PANEL)
    holes = [geo.Rect(5, 8, 20, 20), geo.Rect(23, 8, 20, 20)]
    P.inset_well(img, holes)
    P.inset_well(img, [geo.Rect(58, 14, 20, 20)])
    for r in holes + [geo.Rect(58, 14, 20, 20)]:
        P.fill(img, r.tuple(), (0, 0, 0, 0))
    s = 10
    big = Image.new('RGBA', (img.width * s, img.height * s + 130), BG)
    chk = Image.new('RGBA', img.size, (120, 120, 120, 255))
    chk.alpha_composite(img)
    big.alpha_composite(chk.resize((img.width * s, img.height * s), Image.Resampling.NEAREST))
    d = ImageDraw.Draw(big)
    for r in holes + [geo.Rect(58, 14, 20, 20)]:
        d.rectangle((r.x * s, r.y * s, r.right * s - 1, r.bottom * s - 1), outline=(255, 0, 255))
    notes = ['magenta = 20x20 alpha-zero clearance (the slot underneath shows through)',
             'ring just outside the hole: grey_0 on the top/left walls (inner shadow), white on the bottom/right',
             'mixed corners grey_4; top-left outer corner continues the shadow, bottom-right the highlight',
             'adjacent clearances merge into one inset tray; nothing is ever painted inside a hole']
    for i, n in enumerate(notes):
        d.text((10, img.height * s + 10 + i * 26), n, fill=FG, font=_font(15))
    return big


REF_BUTTONS = [
    ('primary  (stone, gold top/left bevel)', 'economy_hub', 'auction'),
    ('primary 36x18', 'auction_house', 'sell'),
    ('primary 54x18, PURCHASE fit', 'auction_confirm', None),
    ('secondary  (plain stone)', 'economy_hub', 'history'),
    ('secondary, TINY fallback', 'economy_hub', 'privacy'),
    ('secondary, two lines -> TINY', 'economy_hub', 'chest_shops'),
    ('danger  (red stone)', 'economy_hub', 'close'),
    ('danger 108x18', 'chest_shop_listing_enabled', 'toggle'),
    ('info  (recessed plate)', 'economy_hub', 'balance'),
    ('page turn: previous', 'auction_house', 'previous'),
    ('page turn: next', 'auction_house', 'next'),
    ('close (red stone + X)', 'auction_house', 'close'),
    ('balance icon (coin with slash), info', 'chest_shop', 'balance'),
    ('search icon (lens)', None, 'search'),
    ('settings icon (cog)', None, 'settings'),
    ('rank (star), info', 'economy_hub', 'rank'),
    ('balance column 18x72', 'auction_house', 'balance'),
]


def _find(key, bid):
    if key and bid:
        return key, bid
    for k in geo.all_skins():
        for b in geo.skin(k).buttons:
            if key and k == key and b.style == 'primary':
                return k, b.id
            if not key and b.icon == bid:
                return k, b.id
    return None


def buttons_sheet(scale=4):
    rows = []
    for title, key, bid in REF_BUTTONS:
        found = _find(key, bid)
        if not found:
            continue
        key, bid = found
        normal = C.paint_button(key, bid, seed=1)
        rows.append((title, key, bid, C.button_states(normal, key, bid)))
    colw = 108 * scale // 2 + 16
    W = 270 + 6 * colw
    H = 34 + sum(max(st['normal'].height * scale, 30) + 14 for *_, st in rows)
    img = Image.new('RGBA', (W, H), BG)
    d = ImageDraw.Draw(img)
    for i, st in enumerate(geo.STATES):
        d.text((270 + i * colw, 10), st, fill=FG, font=_font(14))
    y = 34
    for title, key, bid, states in rows:
        d.text((10, y + 2), title, fill=FG, font=_font(13))
        b = geo.skin(key).button(bid)
        d.text((10, y + 20), f'{key}/{bid} {b.w}x{b.h}', fill=DIM, font=_font(11))
        for i, st in enumerate(geo.STATES):
            im = states[st]
            sc = scale if im.width * scale <= colw - 8 else max(1, (colw - 8) // im.width)
            cell = Image.new('RGBA', im.size, PAL.PANEL + (255,))
            cell.alpha_composite(im)
            img.alpha_composite(cell.resize((im.width * sc, im.height * sc), Image.Resampling.NEAREST),
                                (270 + i * colw, y))
        y += max(states['normal'].height * scale, 30) + 14
    return img


def _grid(cells, scale=4, width=1500, cell_bg=PAL.GREY[4]):
    placed = []
    x, y, rowh = 10, 10, 0
    for n, im in cells:
        sw, shh = im.width * scale, im.height * scale
        if x + max(sw, 96) > width - 10:
            x, y, rowh = 10, y + rowh + 30, 0
        placed.append((n, im, x, y, sw, shh))
        x += max(sw, 96) + 16
        rowh = max(rowh, shh)
    img = Image.new('RGBA', (width, y + rowh + 40), BG)
    d = ImageDraw.Draw(img)
    for n, im, x, y, sw, shh in placed:
        bgc = Image.new('RGBA', im.size, cell_bg + (255,))
        bgc.alpha_composite(im)
        img.alpha_composite(bgc.resize((sw, shh), Image.Resampling.NEAREST), (x, y))
        d.text((x, y + shh + 4), n, fill=FG, font=_font(12))
    return img


def icons_sheet(scale=8):
    cells = []
    im = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
    face = P.stone_button(im, (0, 0, 18, 18), 'red', texture=False)
    icons.draw_x(im, face)
    cells.append(('close', im))
    for n, rows in icons.ICONS.items():
        w, h = P.sprite_size(rows)
        im = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
        P.sprite(im, 1, 1, rows)
        cells.append((n, im))
    for n in icons.PICTOGRAMS:
        w, h = icons.pictogram_size(n)
        im = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
        icons.draw_pictogram(im, n, 1, 1)
        cells.append(('pictogram:' + n, im))
    return _grid(cells, scale, width=1800)


def primitives_sheet(scale=4):
    cells = []

    def cell(name, w, h, fn, base='panel'):
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        if base == 'panel':
            P.fill(im, (0, 0, w, h), PAL.PANEL)
        fn(im)
        cells.append((name, im))

    cell('bevel_panel', 40, 24, lambda im: P.bevel_panel(im, (0, 0, 40, 24)), base=None)
    cell('bevel_panel (ender ramp)', 40, 24, lambda im: P.bevel_panel(im, (0, 0, 40, 24), PAL.ENDER_PANEL_RAMP),
         base=None)
    cell('stone_button plain', 36, 18, lambda im: P.stone_button(im, (0, 0, 36, 18), 'plain', 1))
    cell('stone_button gold', 54, 36, lambda im: P.stone_button(im, (0, 0, 54, 36), 'gold', 1))
    cell('stone_button red', 36, 18, lambda im: P.stone_button(im, (0, 0, 36, 18), 'red', 1))
    cell('flat_plate (info)', 36, 18, lambda im: P.flat_plate(im, (1, 1, 34, 16)))
    cell('inset_box', 24, 24, lambda im: P.inset_box(im, (2, 2, 20, 20)))
    cell('pictogram_tile', 24, 24, lambda im: P.pictogram_tile(im, (0, 0, 24, 24), 'chest', PAL.PANEL))
    cell('arrow_glyph l/r/u/d', 40, 12, lambda im: [P.arrow_glyph(im, x, 2 if d in ('left', 'right') else 4, d)
                                                    for x, d in ((2, 'left'), (9, 'right'), (16, 'up'), (26, 'down'))])
    cell('accent_line (gold, red, green, blue)', 40, 12,
         lambda im: [P.accent_line(im, 2, 37, 2 + 2 * i, c) for i, c in
                     enumerate((PAL.GOLD[1], PAL.RED[1], PAL.GREEN[1], PAL.BLUE[1]))])
    cell('label: white + ink_1 shadow', 54, 18,
         lambda im: (P.stone_button(im, (0, 0, 54, 18), 'plain', 2),
                     L.draw_text_centered(im, 26, 5, 'RETURN', 'grey_7', shadow='ink_1')), base=None)
    cell('dark text on plate', 54, 18,
         lambda im: (P.flat_plate(im, (0, 0, 54, 18)), L.draw_text_centered(im, 27, 5, 'Stock', 'ink_1')),
         base=None)
    return _grid(cells, scale)


def _annotate(img, scale, notes, pad_right=380):
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
    img = Image.new('RGBA', (s.width, s.height), (120, 120, 120, 255))
    img.alpha_composite(C.base_background(key, seed=4))
    t, inv = C.bands(key)
    notes = [
        ((0, 0, s.width, 2), (240, 170, 60), 'outline (black, notched corners) + white top/left bevel'),
        (s.text_safe.tuple(), (170, 80, 200), 'text-safe [8,5,160,11]: live title on the panel'),
        ((s.text_safe.x, C.ACCENT_Y, s.text_safe.w, 1), (230, 200, 60), f'family accent line, row {C.ACCENT_Y}'),
        (inv.tuple(), (90, 170, 230), 'inventory band (live "Inventory")'),
        (s.content_bbox.tuple(), (255, 0, 255), 'native well grid (alpha 0) in an inset tray'),
        (s.player_bbox.tuple(), (255, 0, 255), '36 player wells (alpha 0)'),
        ((s.width - 2, 0, 2, s.height), (120, 220, 120), 'dark grey bottom/right bevel'),
        (s.advance_pin.tuple(), (255, 60, 60), 'advance pin [175,0,1,3] alpha 255'),
    ]
    return _annotate(img, 4, notes)


def frame_anatomy():
    key = 'economy_hub'
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, seed=4)
    c = a.container
    notes = [
        (a.top_strip.tuple(), (240, 170, 60), 'top strip 8 px: bevel only'),
        (a.bottom_strip.tuple(), (240, 170, 60), 'bottom strip 8 px: bevel only'),
        ((0, 0, c.x - 6, a.h), (120, 220, 120), 'left side panel: one pictogram tile'),
        ((c.right + 6, 0, a.w - c.right - 6, a.h), (120, 220, 120), 'right side panel: the same tile'),
        ((c.x - 6, 4, 2, a.h - 8), (90, 170, 230), 'grooves (grey_1 + white) dock the panels'),
        (c.tuple(), (255, 0, 255), 'native container: fully alpha 0'),
        ((c.right, c.y + 2, 1, c.h), (200, 200, 200), 'drop shadow right of / below the container'),
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
        'primitives.png': primitives_sheet(),
        'background-anatomy.png': background_anatomy(),
        'frame-anatomy.png': frame_anatomy(),
    }
    for name, im in outputs.items():
        im.convert('RGB').save(OUT / name)
        print('WROTE', OUT / name)
    spec = geo.ROOT / 'evidence' / 'faithful' / 'typeface-specimen.png'
    L.specimen().save(spec)
    print('WROTE', spec)


if __name__ == '__main__':
    main()
