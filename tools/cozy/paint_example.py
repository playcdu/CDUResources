#!/usr/bin/env python3
"""Worked example and quality bar: one throwaway demonstration set.

    python tools/cozy/paint_example.py

Paints, deterministically, into evidence/cozy/example/textures/ (NEVER into
pack-source):

* a chest_3 background on template_chest_3 geometry (27 native wells),
* the 54x36 primary button economy_hub/auction in all six states,
* the 256x184 outer frame template_chest_3/menu_frame,

validates each with the builder's own validators, and renders
evidence/cozy/example/preview.png (composite at 3x, the six button states at
4x, and the frame alone). It exercises every primitive in primitives.py, so
copy its structure for a real paint_<assignment>.py.

Licence: MIT.
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
import preview  # noqa: E402
import primitives as P  # noqa: E402
from palette import BERRY, BRASS, EMBER, INK, PARCHMENT, SAGE, SKY, WOOD  # noqa: E402

import build_pack  # noqa: E402  (tools/ is on sys.path via geometry)
import button_assets  # noqa: E402
import decorative_assets  # noqa: E402

OUT = geo.ROOT / 'evidence' / 'cozy' / 'example'
TEX = OUT / 'assets' / 'quasar_gui' / 'textures'   # same layout as pack-source
BG_KEY = 'template_chest_3'
BTN_KEY, BTN_ID = 'economy_hub', 'auction'
SEED = 7


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def paint_background():
    s = geo.skin(BG_KEY)
    img = C.base_background(BG_KEY, seed=SEED)          # planks, bands, stitched wells
    tband, iband = C.bands(BG_KEY)
    # Hand touches: a sprig pressed under the right end of the inventory band
    # (light sage only, kept clear of the live 'Inventory' label at the left).
    P.leaf(img, iband.right - 12, iband.y + 1, 'ne', small=True)
    P.leaf(img, iband.right - 17, iband.y + 3, 'nw', small=True)
    P.twine(img, iband.right - 20, iband.y + 6, iband.right - 7, iband.y + 6, sag=1)
    # Brass tacks holding the sheet at the bottom corners, warm wear marks.
    P.tack(img, 3, s.height - 4, small=True)
    P.tack(img, s.width - 4, s.height - 4, small=True)
    P.dither_patch(img, (1, s.height - 6, 4, 4), WOOD[1], 0.25)
    geo.finish_background(img, BG_KEY)
    return img


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------

def paint_button():
    b = geo.skin(BTN_KEY).button(BTN_ID)
    img = C.paint_button(BTN_KEY, BTN_ID, seed=SEED)    # brass-plated plank + label
    # Hand adjustment: a small engraved laurel under the lettering and a scuff
    # on the plank rim, so the plate does not read as a flat UI rectangle.
    cx = b.w // 2
    for dx in range(-7, 8):
        if abs(dx) > 1 and dx % 2 == 0:
            P.put(img, cx + dx, b.h - 7, BRASS[0])
    P.put(img, cx, b.h - 8, BRASS[3])
    P.put(img, cx - 1, b.h - 7, BRASS[0]); P.put(img, cx + 1, b.h - 7, BRASS[0])
    P.put(img, 5, 1, WOOD[1]); P.put(img, 6, 1, WOOD[1])
    geo.finish_button(img, BTN_KEY, BTN_ID)
    return C.button_states(img, BTN_KEY, BTN_ID)


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def note_card(img, x, y, w, h, seed):
    """A pinned parchment note: ruled lines (no words), wax seal, curled corner."""
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=True)
    for k in range(5, h - 6, 4):
        P.stitch_line(img, x + 3, y + k, x + w - 5, y + k, SKY[2], 3, 1, phase=k)
    P.page_curl(img, (x, y, w, h), 'br', 5, behind=WOOD[0])
    P.tack(img, x + w // 2, y + 1)
    P.wax_seal(img, x + 8, y + h - 9, 6, BERRY, seed, drip=True, emblem='heart')


def envelope(img, x, y, w, h, seed):
    """A sealed letter: parchment body, inked V flap, red wax seal on the point."""
    P.parchment_panel(img, (x, y, w, h), seed, outline='ink_1', fibres=False)
    mid = x + w // 2
    P.ink_line(img, x + 1, y + 1, mid, y + h // 2 + 1, 'ink_2')
    P.ink_line(img, x + w - 2, y + 1, mid, y + h // 2 + 1, 'ink_2')
    P.ink_line(img, x + 1, y + h - 2, mid - 3, y + h // 2 + 3, 'parch_0')
    P.ink_line(img, x + w - 2, y + h - 2, mid + 3, y + h // 2 + 3, 'parch_0')
    P.wax_seal(img, mid, y + h // 2 + 1, 4, BERRY, seed, drip=True)


def shelf(img, x, y, w, seed):
    """A short plank shelf on two brass brackets."""
    P.plank(img, (x, y, w, 5), WOOD, seed, 'ink_1', radius=1, grain=0.5)
    for bx in (x + 3, x + w - 5):
        P.sprite(img, bx, y + 5, ['oo', 'o2', '.o'], {'o': INK[1], '2': BRASS[1]})


def paint_frame():
    s = geo.skin(BG_KEY)
    a = s.layer()
    img = C.base_frame(BG_KEY, seed=SEED)                # boards, rim, corners, ribbon
    lp, rp = a.left_panel, a.right_panel
    H = a.h

    # --- left panel: lantern, heading tag, shelf with mug and herbs, note ---
    P.rope(img, lp.x + 6, 12, lp.right - 7, 12, sag=2)
    P.vline(img, lp.x + 19, 13, 16, INK[1])
    P.lantern(img, lp.x + 16, 17)
    P.lantern_glow_ring(img, lp.x + 19, 22, 13, strength=1)
    C.side_tag(img, lp, a.left_heading or a.heading or '', 34, SEED, twine_from=(lp.x + 20, 26))
    shelf(img, lp.x + 4, 72, lp.w - 8, SEED)
    P.mug(img, lp.x + 6, 63, SKY, steam=True, seed=SEED)
    icons.draw_motif(img, 'herb_pot', lp.x + 22, 60)
    note_card(img, lp.x + 6, 88, 27, 34, SEED)
    for k, yy in enumerate((132, 140, 149)):
        P.leaf(img, lp.x + (8 if k % 2 else 20), yy, 'ne' if k % 2 else 'nw')
    P.ink_line(img, lp.x + 18, 128, lp.x + 16, 160, SAGE[0], wobble=1, seed=SEED)
    icons.draw_motif(img, 'crate', lp.x + 15, H - 26)
    icons.draw_motif(img, 'coin', lp.x + 8, H - 17)

    # --- right panel: candle shelf, hanging twine of linen tags, vine, ledger --
    shelf(img, rp.x + 4, 30, rp.w - 8, SEED + 1)
    icons.draw_motif(img, 'candle', rp.x + 8, 19)
    P.lantern_glow_ring(img, rp.x + 10, 21, 10, strength=1)
    icons.draw_motif(img, 'ledger', rp.x + 20, 20)
    P.twine(img, rp.x + 3, 46, rp.right - 4, 46, sag=4)
    for k, (tx, accent) in enumerate(((rp.x + 7, SAGE), (rp.x + 17, BERRY), (rp.x + 27, SKY))):
        ty = 49 + (2 if k == 1 else 0)
        P.vline(img, tx + 3, ty - 1, ty + 1, PARCHMENT[0])
        P.linen_tag(img, (tx, ty + 2, 7, 12), eyelet=None, seed=SEED + k)
        P.put(img, tx + 3, ty + 4, INK[0])                       # string hole
        P.fill(img, (tx + 1, ty + 10, 5, 2), accent[1])          # dyed hem
        P.hline(img, tx + 1, tx + 5, ty + 9, accent[2])
    for k in range(6):
        yy = 72 + k * 14
        P.ink_line(img, rp.x + 30 - (k % 2), yy, rp.x + 30 - ((k + 1) % 2), yy + 14, SAGE[0], wobble=0)
        P.leaf(img, rp.x + (31 if k % 2 else 23), yy + 3, 'ne' if k % 2 else 'nw', small=k % 3 == 2)
    envelope(img, rp.x + 4, 96, 24, 16, SEED)
    shelf(img, rp.x + 4, H - 40, rp.w - 8, SEED + 2)
    P.mug(img, rp.x + 6, H - 49, EMBER, steam=True, seed=SEED + 1)
    icons.draw_motif(img, 'coin', rp.x + 20, H - 46)
    icons.draw_motif(img, 'coin', rp.x + 24, H - 46)
    icons.draw_motif(img, 'coin', rp.x + 22, H - 49)

    # --- bottom strip: a rope run between two tacks --------------------------
    P.rope(img, 12, H - 4, a.w - 13, H - 4, sag=0)
    P.tack(img, 10, H - 5); P.tack(img, a.w - 11, H - 5)
    P.highlight_edge(img, (lp.x + 1, 9, lp.w - 2, H - 18), WOOD[2], 'l', broken=4, seed=SEED)
    P.shadow_edge(img, (rp.x, 9, rp.w - 1, H - 18), INK[1], 'r')

    geo.finish_frame(img, BG_KEY, a.id, 'ink_0')
    return img


# ---------------------------------------------------------------------------
# Validation and preview
# ---------------------------------------------------------------------------

def _raw(img):
    import io
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
    print('PASS example background, 6 button states, frame (builder validators)')


def button_strip(states, scale=4):
    b = geo.skin(BTN_KEY).button(BTN_ID)
    pad = 10
    W = len(states) * (b.w * scale + pad) + pad
    img = Image.new('RGBA', (W, b.h * scale + 34), (74, 52, 40, 255))
    d = ImageDraw.Draw(img)
    for i, (st, im) in enumerate(states.items()):
        x = pad + i * (b.w * scale + pad)
        img.alpha_composite(im.resize((b.w * scale, b.h * scale), Image.Resampling.NEAREST), (x, 8))
        d.text((x, b.h * scale + 14), st, fill=(240, 228, 200), font=preview._font(13))
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
    comp = preview.render(BG_KEY, overrides_dir=TEX, scale=3)
    strip = button_strip(states)
    alone = preview.render_frame_alone(BG_KEY, overrides_dir=TEX, scale=2)
    W = max(comp.width + alone.width + 12, strip.width)
    sheet = Image.new('RGBA', (W, comp.height + strip.height + 12), (30, 26, 30, 255))
    sheet.alpha_composite(comp, (0, 0))
    sheet.alpha_composite(alone, (comp.width + 12, 0))
    sheet.alpha_composite(strip, (0, comp.height + 12))
    out = preview.export(sheet, OUT / 'preview.png',
                         'cozy example (quality bar) - schematic items/titles; textures in evidence/cozy/example/textures')
    print('WROTE', out)


if __name__ == '__main__':
    main()
