#!/usr/bin/env python3
"""Worked example and quality bar for the Soulrend theme: one throwaway set.

    python tools/soulrend/paint_example.py

Paints, deterministically, into evidence/soulrend/example/assets/quasar_gui/
textures/ (NEVER into pack-source):

* a chest_3 background on template_chest_3 geometry (27 native wells),
* the 54x36 primary button economy_hub/auction in all six states,
* the 256x184 outer frame template_chest_3/menu_frame,

validates each with the builder's own validators, and renders
evidence/soulrend/example/preview.png (composite at 3x, the six button states
at 4x, and the frame alone). It exercises the primitives a painter needs, so
copy its structure for a real paint_<assignment>.py.

Licence: MIT.
"""
from __future__ import annotations

import io
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
import preview  # noqa: E402  (tools/cozy/preview.py, theme-aware)
import primitives as P  # noqa: E402
from palette import BLOOD, EMBER, GOLD, INK, IRON, MOSS, SOUL, STONE, UMBER, VELLUM  # noqa: E402

import build_pack  # noqa: E402
import button_assets  # noqa: E402
import decorative_assets  # noqa: E402

OUT = geo.ROOT / 'evidence' / 'soulrend' / 'example'
TEX = OUT / 'assets' / 'quasar_gui' / 'textures'   # same layout as pack-source
BG_KEY = 'template_chest_3'
BTN_KEY, BTN_ID = 'economy_hub', 'auction'
SEED = 7


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def paint_background():
    s = geo.skin(BG_KEY)
    img = C.base_background(BG_KEY, seed=SEED)          # umber sheet, vellum bands, iron sockets
    tband, iband = C.bands(BG_KEY)
    H, W = s.height, s.width
    # Hand touches in the 4 free rows under the hotbar socket: a gold
    # flourish centred on the sheet, a blood-wax drip, a hairline crack.
    P.gold_filigree(img, W // 2 - 5, H - 4, 'flourish')
    P.sprite(img, 22, H - 5, ['oso', 'oto', '.o.'])
    P.crack(img, W - 26, H - 5, 3, seed=SEED, direction='right', colour='umber_0', branch=False)
    C.finish_background(img, BG_KEY)
    return img


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------

def paint_button():
    b = geo.skin(BTN_KEY).button(BTN_ID)
    img = C.paint_button(BTN_KEY, BTN_ID, seed=SEED)    # iron plate, gold rim, gold label
    # Hand adjustments: a blood gem set in the top rim, a gold flourish
    # engraved under the lettering, a scuffed corner on the plate.
    cx = b.w // 2
    P.sprite(img, cx - 2, 0, ['OttO', 'Osro', '.OO.'])
    P.gold_filigree(img, cx - 5, b.h - 8, 'flourish')
    P.put(img, b.w - 6, 4, IRON[0]); P.put(img, b.w - 7, 5, IRON[0])
    C.finish_button(img, BTN_KEY, BTN_ID)
    return C.button_states(img, BTN_KEY, BTN_ID)


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def ledge(img, x, y, w, seed):
    """A short carved stone ledge on two iron brackets."""
    P.fill(img, (x, y, w, 4), STONE[2])
    P.hline(img, x, x + w - 1, y, STONE[3])
    P.hline(img, x, x + w - 1, y + 3, STONE[0])
    P.ink_outline(img, (x - 1, y - 1, w + 2, 6), 'ink_1', radius=0)
    for bx in (x + 2, x + w - 4):
        P.sprite(img, bx, y + 5, ['oco', '.oa', '..o'])


def sconce(img, x, y, seed, soul=False):
    """An iron wall sconce holding a lit candle; returns the flame centre."""
    P.sprite(img, x - 3, y + 8, ['occcco', '.obao.', '..oo..', '..oa..', '..ob..', '...o..'])
    fx, fy = P.candle(img, x - 1, y, height=6, lit=True, holder=None, seed=seed)
    return fx, fy


def paint_frame():
    s = geo.skin(BG_KEY)
    a = s.layer()
    img = C.base_frame(BG_KEY, seed=SEED)                # masonry, iron border, filigree, plaque
    lp, rp = a.left_panel, a.right_panel
    H = a.h

    # --- left panel: moss banner, sconce with ember light, soul niche, brazier
    P.chain(img, lp.x + 9, 9, lp.x + 9, 13, seed=SEED, shadow=None)
    P.chain(img, lp.x + 29, 9, lp.x + 29, 13, seed=SEED + 1, shadow=None)
    C.side_banner(img, geo.Rect(lp.x + 4, 0, 32, 0), y=15, seed=SEED, ramp=MOSS, crest='tower', h=34)
    fx, fy = sconce(img, lp.x + 20, 60, SEED)
    P.glow(img, fx, fy + 2, 13, 'ember')
    P.arch_niche(img, (lp.x + 9, 92, 22, 30), seed=SEED)
    icons.draw_motif(img, 'mirror', lp.x + 15, 103)
    P.glow(img, lp.x + 20, 109, 9, 'soul')
    ledge(img, lp.x + 7, 123, 26, SEED)
    P.moss_tuft(img, lp.x + 10, 127, 5, seed=SEED)
    P.crack(img, lp.x + 30, 136, 9, seed=SEED, colour=STONE[0], light=STONE[3])
    icons.draw_motif(img, 'brazier', lp.x + 14, H - 30)
    P.glow(img, lp.x + 19, H - 30, 10, 'ember')
    icons.draw_motif(img, 'bone', lp.x + 4, H - 18)

    # --- right panel: blood banner, hanging lantern, ledge with goblet,
    #     ledger and coins, gargoyle corbel ----------------------------------
    C.side_banner(img, geo.Rect(rp.x + 4, 0, 32, 0), y=15, seed=SEED + 1, ramp=BLOOD, crest='chevron', h=30)
    P.chain(img, rp.x + 20, 47, rp.x + 20, 58, seed=SEED + 2)
    icons.draw_motif(img, 'lantern', rp.x + 16, 59)
    P.glow(img, rp.x + 20, 64, 12, 'ember')
    ledge(img, rp.x + 4, 96, 32, SEED + 1)
    icons.draw_motif(img, 'goblet', rp.x + 5, 86)
    icons.draw_motif(img, 'coin_stack', rp.x + 16, 87)
    icons.draw_motif(img, 'candle_clock', rp.x + 27, 82)
    P.glow(img, rp.x + 29, 83, 8, 'ember')
    P.moss_tuft(img, rp.x + 22, 101, 6, seed=SEED + 3)
    icons.draw_motif(img, 'ledger', rp.x + 13, 118)
    P.chain(img, rp.x + 6, 104, rp.x + 6, 150, seed=SEED + 4)
    icons.draw_motif(img, 'key', rp.x + 2, 151)
    icons.draw_motif(img, 'gargoyle', rp.x + 22, H - 26)
    P.crack(img, rp.x + 33, 136, 7, seed=SEED + 5, colour=STONE[0], light=STONE[3])

    # --- top strip: chains from the corners to the heraldic plaque -----------
    P.chain(img, 12, 4, a.w // 2 - 22, 4, sag=2, seed=SEED + 11)
    P.chain(img, a.w // 2 + 21, 4, a.w - 13, 4, sag=2, seed=SEED + 12)

    # --- bottom strip: chains swagged between rivets --------------------------
    for x0, x1 in ((8, 120), (136, a.w - 9)):
        P.chain(img, x0, H - 6, x1, H - 6, sag=2, seed=SEED + x0)
        P.rivet(img, x0 - 2, H - 7, 'gold', 3); P.rivet(img, x1 - 1, H - 7, 'gold', 3)
    P.gold_filigree(img, 123, H - 7, 'fleur')

    C.finish_frame(img, BG_KEY, a.id)
    return img


# ---------------------------------------------------------------------------
# Validation and preview
# ---------------------------------------------------------------------------

def _raw(img):
    out = io.BytesIO()
    C.normalise(img).save(out, format='PNG')
    return out.getvalue()


def validate(bg, states, frame):
    layouts, skins, config = geo.raw_manifests()
    s = skins[BG_KEY]; g = layouts[s['layout']]
    build_pack.validate_png(_raw(bg), g, s, BG_KEY)
    bs = skins[BTN_KEY]; bg_layout = layouts[bs['layout']]
    btn = next(b for b in config['screens'][BTN_KEY]['buttons'] if b['id'] == BTN_ID)
    for st, im in states.items():
        button_assets.validate_button(_raw(im), bg_layout, bs, btn, st)
        assert im.getchannel('A').tobytes() == states['normal'].getchannel('A').tobytes(), st
    layer = config['screens'][BG_KEY]['artLayers'][0]
    decorative_assets.validate(_raw(frame), layer, g)
    from soulrend import palette as PAL
    for name, im in [('background', bg), ('frame', frame)] + list(states.items()):
        assert PAL.off_palette(im) == 0, f'{name}: off-palette pixels'
    print('PASS example background, 6 button states, frame (builder validators + palette)')


def button_strip(states, scale=4):
    b = geo.skin(BTN_KEY).button(BTN_ID)
    pad = 10
    W = len(states) * (b.w * scale + pad) + pad
    img = Image.new('RGBA', (W, b.h * scale + 34), UMBER[1] + (255,))
    d = ImageDraw.Draw(img)
    for i, (st, im) in enumerate(states.items()):
        x = pad + i * (b.w * scale + pad)
        img.alpha_composite(im.resize((b.w * scale, b.h * scale), Image.Resampling.NEAREST), (x, 8))
        d.text((x, b.h * scale + 14), st, fill=VELLUM[2], font=preview._font(13))
    return img


def main():
    bg = paint_background()
    states = paint_button()
    frame = paint_frame()
    validate(bg, states, frame)
    s = geo.skin(BG_KEY)
    C.save_png(bg, TEX / 'menu' / f'{BG_KEY}.png')
    C.save_png(frame, TEX / 'frames' / BG_KEY / f'{s.layer().id}.png')
    C.save_button_states(states, BTN_KEY, BTN_ID, root=TEX)
    comp = preview.render(BG_KEY, overrides_dir=TEX, scale=3, theme='soulrend')
    strip = button_strip(states)
    alone = preview.render_frame_alone(BG_KEY, overrides_dir=TEX, scale=2)
    W = max(comp.width + alone.width + 12, strip.width)
    sheet = Image.new('RGBA', (W, comp.height + strip.height + 12), (24, 20, 22, 255))
    sheet.alpha_composite(comp, (0, 0))
    sheet.alpha_composite(alone, (comp.width + 12, 0))
    sheet.alpha_composite(strip, (0, comp.height + 12))
    out = preview.export(sheet, OUT / 'preview.png',
                         'soulrend example (quality bar) - schematic items/titles; textures in '
                         'evidence/soulrend/example/assets')
    print('WROTE', out)


if __name__ == '__main__':
    main()
