#!/usr/bin/env python3
"""Render the Soulrend style guide's reference drawings into evidence/soulrend/reference/.

    python tools/soulrend/render_references.py

palette.png             master palette swatches with names and RGB
wells.png               socket anatomy (d1 lip / d2 stone wall / d3 iron frame, rivets) at 10x
buttons.png             every button grammar in all six states, at 4x
icons.png               icons, crests, seal emblems and motifs at 4x
primitives.png          stone, iron, vellum, cloth, wax, chain, candle, banner,
                        filigree, glow and torn-edge samples at 4x
background-anatomy.png  base_background(template_chest_3) with labelled zones
frame-anatomy.png       base_frame(template_chest_3) with labelled zones
typeface-specimen.png   (in evidence/soulrend/) via lettering.specimen()

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

OUT = geo.ROOT / 'evidence' / 'soulrend' / 'reference'
BG = (24, 20, 22, 255)
FG = (232, 222, 200)
DIM = (170, 156, 136)


def _font(n=13):
    return preview._font(n)


def palette_sheet():
    rows = list(PAL.RAMPS.items())
    sw, sh = 96, 46
    img = Image.new('RGBA', (130 + 4 * sw, 20 + len(rows) * (sh + 8)), BG)
    d = ImageDraw.Draw(img)
    for r, (name, cols) in enumerate(rows):
        y = 14 + r * (sh + 8)
        d.text((10, y + 14), name.upper(), fill=FG, font=_font(14))
        for i, c in enumerate(cols):
            x = 120 + i * sw
            d.rectangle((x, y, x + sw - 6, y + sh), fill=c + (255,))
            t = (24, 18, 18) if PAL.luminance(c) > 120 else (238, 230, 210)
            d.text((x + 4, y + 4), PAL.name_of(c), fill=t, font=_font(12))
            d.text((x + 4, y + 22), '%d,%d,%d' % c, fill=t, font=_font(11))
    return img


def wells_sheet():
    """A two-slot socket and a single socket on the umber sheet, with a vellum
    band protecting the top rows."""
    img = Image.new('RGBA', (86, 44), (0, 0, 0, 0))
    P.umber_panel(img, (0, 0, 86, 44), 3)
    P.vellum_strip(img, (0, 0, 86, 6), 1, deckle='', fibres=False)
    holes = [geo.Rect(5, 8, 20, 20), geo.Rect(23, 8, 20, 20)]
    P.socket_well(img, holes, protect=[(0, 0, 86, 6)])
    P.socket_well(img, [geo.Rect(58, 14, 20, 20)])
    for r in holes + [geo.Rect(58, 14, 20, 20)]:
        P.fill(img, r.tuple(), (0, 0, 0, 0))
    s = 10
    big = Image.new('RGBA', (img.width * s, img.height * s + 130), BG)
    chk = Image.new('RGBA', img.size, (150, 150, 150, 255))
    chk.alpha_composite(img)
    big.alpha_composite(chk.resize((img.width * s, img.height * s), Image.Resampling.NEAREST))
    d = ImageDraw.Draw(big)
    for r in holes + [geo.Rect(58, 14, 20, 20)]:
        d.rectangle((r.x * s, r.y * s, r.right * s - 1, r.bottom * s - 1), outline=(255, 0, 255))
    notes = ['magenta = 20x20 alpha-zero clearance (the vanilla slot shows through)',
             'd1: ink_0 lip all round  |  d2: stone wall, stone_0 on the top/left (shadow), stone_3 bottom/right (lit)',
             'd3: raised iron frame, iron_2 top/left, iron_0 bottom/right; iron_3 rivets at corners and 18 px seams',
             'inside a protected text band only the d1 lip is drawn; adjacent clearances merge into one socket']
    for i, n in enumerate(notes):
        d.text((10, img.height * s + 10 + i * 26), n, fill=FG, font=_font(15))
    return big


REF_BUTTONS = [
    ('primary  (iron plate, gold rim)', 'economy_hub', 'auction'),
    ('primary 36x18', 'auction_house', 'sell'),
    ('primary 54x18, PURCHASE fit', 'auction_confirm', None),
    ('secondary  (riveted vellum strip)', 'economy_hub', 'history'),
    ('secondary, rivets dropped for fit', 'economy_hub', 'privacy'),
    ('secondary, two lines -> RUNE', 'economy_hub', 'chest_shops'),
    ('danger  (blood cloth, iron studs)', 'economy_hub', 'close'),
    ('danger 108x18', 'chest_shop_listing_enabled', 'toggle'),
    ('info  (carved stone tablet)', 'economy_hub', 'balance'),
    ('page turn: previous', 'auction_house', 'previous'),
    ('page turn: next', 'auction_house', 'next'),
    ('close (studded wax seal + X)', 'auction_house', 'close'),
    ('balance icon (pouch on chain), info', 'chest_shop', 'balance'),
    ('search icon (scrying lens)', None, 'search'),
    ('settings icon (iron cog)', None, 'settings'),
    ('rank (heraldic crest), info', 'economy_hub', 'rank'),
    ('balance column 18x72', 'auction_house', 'balance'),
]


def _find(key, bid):
    """Resolve a reference row to (key, button id), searching when needed."""
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
            cell = Image.new('RGBA', im.size, PAL.UMBER[1] + (255,))
            cell.alpha_composite(im)
            img.alpha_composite(cell.resize((im.width * sc, im.height * sc), Image.Resampling.NEAREST),
                                (270 + i * colw, y))
        y += max(states['normal'].height * scale, 30) + 14
    return img


def _grid(cells, scale=4, width=1500, cell_bg=PAL.STONE[1]):
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


def icons_sheet(scale=4):
    cells = []
    seal = Image.new('RGBA', (18, 18), (0, 0, 0, 0))
    icons.close_seal(seal, (0, 0, 18, 18))
    cells.append(('close', seal))
    for n, rows in icons.ICONS.items():
        w, h = P.sprite_size(rows)
        im = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
        P.sprite(im, 1, 1, rows)
        cells.append((n, im))
    for n in icons.CRESTS:
        im = Image.new('RGBA', (11, 13), (0, 0, 0, 0))
        icons.draw_crest(im, n, 1, 1)
        cells.append(('crest:' + n, im))
    for e in icons.EMBLEMS:
        im = Image.new('RGBA', (17, 17), (0, 0, 0, 0))
        P.wax_seal(im, 8, 8, 7, PAL.BLOOD, 2, emblem=e)
        cells.append(('seal:' + e, im))
    for n in icons.MOTIFS:
        w, h = icons.motif_size(n)
        im = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
        icons.draw_motif(im, n, 1, 1)
        cells.append((n, im))
    return _grid(cells, scale * 2 if scale < 6 else scale)


def primitives_sheet(scale=4):
    cells = []

    def cell(name, w, h, fn, base=None):
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        if base == 'umber':
            P.umber_panel(im, (0, 0, w, h), 2)
        elif base == 'stone':
            P.stone_blocks(im, (0, 0, w, h), 2, course=6, moss=0.2)
        fn(im)
        cells.append((name, im))

    cell('stone_blocks (moss)', 48, 30, lambda im: P.stone_blocks(im, (0, 0, 48, 30), 5, course=6, moss=0.3))
    cell('umber_panel', 40, 24, lambda im: P.umber_panel(im, (0, 0, 40, 24), 4))
    cell('stone_tablet', 30, 16, lambda im: P.stone_tablet(im, (0, 0, 30, 16), 1))
    cell('iron_plate gold rim', 36, 18, lambda im: P.iron_plate(im, (0, 0, 36, 18), 'gold', True, seed=1))
    cell('iron_plate iron rim', 36, 18, lambda im: P.iron_plate(im, (0, 0, 36, 18), 'iron', False, seed=1))
    cell('rivets 2/3/4 iron gold dark', 30, 8, lambda im: [P.rivet(im, 1 + i * 5, 2, k, sz) for i, (k, sz) in
                                                           enumerate((('iron', 2), ('iron', 3), ('iron', 4), ('gold', 3), ('dark', 3)))])
    cell('vellum_strip deckle tb', 40, 14, lambda im: P.vellum_strip(im, (0, 0, 40, 14), 3, deckle='tb'))
    cell('torn_edge / burnt', 40, 16, lambda im: (P.vellum_strip(im, (0, 0, 40, 16), 2, deckle=''),
                                                  P.torn_edge(im, (0, 0, 40, 16), 'r', 2, 3),
                                                  P.torn_edge(im, (0, 0, 40, 16), 'b', 3, 2, burnt=True)))
    cell('page_curl br / bl', 40, 14, lambda im: (P.vellum_strip(im, (0, 0, 19, 14), 1, deckle=''),
                                                  P.page_curl(im, (0, 0, 19, 14), 'br', 6),
                                                  P.vellum_strip(im, (21, 0, 19, 14), 1, deckle=''),
                                                  P.page_curl(im, (21, 0, 19, 14), 'bl', 6)))
    cell('cloth_panel (danger)', 40, 18, lambda im: P.cloth_panel(im, (0, 0, 40, 18), PAL.BLOOD, 1))
    cell('wax_seal studs/emblem', 34, 17, lambda im: (P.wax_seal(im, 8, 8, 7, PAL.BLOOD, 1, studs=4),
                                                       P.wax_seal(im, 25, 8, 7, PAL.BLOOD, 2, emblem='crown', drip=True)))
    cell('chain h / v (sag)', 40, 20, lambda im: (P.chain(im, 2, 3, 26, 3, sag=3, seed=1),
                                                  P.chain(im, 34, 1, 34, 18, seed=2)), base='stone')
    cell('candle lit / unlit', 24, 18, lambda im: (P.candle(im, 4, 6, 7, True, seed=1),
                                                   P.candle(im, 15, 6, 7, False, holder='gold', seed=2)), base='stone')
    cell('banner + crest', 22, 34, lambda im: P.banner(im, 4, 3, 13, 28, PAL.MOSS, 1, emblem='tower'), base='stone')
    cell('gold_filigree corner/scroll/fleur/flourish', 36, 10,
         lambda im: (P.gold_filigree(im, 0, 0, 'corner'), P.gold_filigree(im, 9, 0, 'scroll'),
                     P.gold_filigree(im, 16, 0, 'fleur'), P.gold_filigree(im, 23, 0, 'flourish')), base='umber')
    cell('arch_niche', 24, 30, lambda im: P.arch_niche(im, (1, 1, 22, 28), 1), base='stone')
    cell('glow ember / soul', 48, 24, lambda im: (P.glow(im, 12, 12, 11, 'ember'), P.glow(im, 36, 12, 11, 'soul')),
         base='stone')
    cell('crack + moss_tuft', 30, 20, lambda im: (P.crack(im, 8, 2, 14, 3, colour='stone_0', light='stone_3'),
                                                  P.moss_tuft(im, 18, 6, 6, 1)), base='stone')
    return _grid(cells, scale)


def _annotate(img, scale, notes, pad_right=360):
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
        (t.tuple(), (240, 170, 60), 'title band rows 2-14: vellum, iron clasps'),
        (s.text_safe.tuple(), (170, 80, 200), 'text-safe [8,5,160,11]: live title'),
        (inv.tuple(), (90, 170, 230), 'inventory band (live "Inventory")'),
        (s.content_bbox.tuple(), (255, 0, 255), 'native well grid (alpha 0)'),
        (s.player_bbox.tuple(), (255, 0, 255), '36 player wells (alpha 0)'),
        ((0, 16, 6, 56), (120, 220, 120), 'margin 6 px: rim, iron band, sheet, socket'),
        ((1, s.height - 7, 6, 6), (200, 200, 200), 'iron corner brackets'),
        (s.advance_pin.tuple(), (255, 60, 60), 'advance pin [175,0,1,3] alpha 255'),
    ]
    return _annotate(img, 4, notes)


def frame_anatomy():
    key = 'template_chest_3'
    s = geo.skin(key)
    a = s.layer()
    img = C.base_frame(key, seed=4)
    notes = [
        (a.top_strip.tuple(), (240, 170, 60), 'top strip 8 px: iron border, wordless plaque'),
        (a.bottom_strip.tuple(), (240, 170, 60), 'bottom strip 8 px: border, chains, ledge'),
        (a.left_panel.tuple(), (120, 220, 120), 'left panel 40 px: banner, sconce, niche'),
        (a.right_panel.tuple(), (120, 220, 120), 'right panel 40 px: family motifs'),
        (a.container.tuple(), (255, 0, 255), 'native container: fully alpha 0'),
        ((3, 3, 7, 7), (220, 190, 90), 'gold corner filigree'),
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
    spec = geo.ROOT / 'evidence' / 'soulrend' / 'typeface-specimen.png'
    L.specimen().save(spec)
    print('WROTE', spec)


if __name__ == '__main__':
    main()
