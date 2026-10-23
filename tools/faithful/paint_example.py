#!/usr/bin/env python3
"""Worked example and quality bar for the Faithful theme: one throwaway set.

    python tools/faithful/paint_example.py

Paints, deterministically, into evidence/faithful/example/assets/quasar_gui/
textures/ (NEVER into pack-source):

* the whole economy_hub screen: background, all 8 buttons in six states and
  its 256x184 outer frame (painted controls, the gold coin family),
* a chest_3 background and frame on template_chest_3 geometry (27 native
  wells, the plain utility look),

validates every image with the builder's own validators plus the palette,
light-band and lean-frame checks, and renders
evidence/faithful/example/preview.png (both composites at 3x, the six states
of economy_hub/auction at 4x, and the template frame alone). It exercises the
helpers a painter needs, so copy its structure for a real
paint_<assignment>.py.

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
import preview  # noqa: E402  (tools/cozy/preview.py, theme-aware)
from palette import GREY, luminance  # noqa: E402

import build_pack  # noqa: E402
import button_assets  # noqa: E402
import decorative_assets  # noqa: E402

OUT = geo.ROOT / 'evidence' / 'faithful' / 'example'
TEX = OUT / 'assets' / 'quasar_gui' / 'textures'   # same layout as pack-source
HUB = 'economy_hub'
TPL = 'template_chest_3'
BTN_ID = 'auction'
SEED = 7


# ---------------------------------------------------------------------------
# Painting (what a painter's script does)
# ---------------------------------------------------------------------------

def paint_hub():
    """economy_hub: base background, every button through the shared grammar,
    the base frame. Restraint is the point: the only family identity is the
    gold tint on the inset trays' top/left walls and the coin on each docked
    tab of the lean frame. (An earlier draft added a coin cell to the BALANCE plate; it
    forced the label into TINY and was dropped: never shrink a label for
    decoration.)"""
    s = geo.skin(HUB)
    bg = C.base_background(HUB, seed=SEED)        # panel, inset trays with gold-tinted walls
    C.finish_background(bg, HUB)                  # clear masks + stamp pin, always last
    buttons = {}
    for b in s.buttons:
        normal = C.paint_button(HUB, b.id, seed=SEED)
        # hand touches go here, outside the label box; then re-finish
        C.finish_button(normal, HUB, b.id)
        buttons[b.id] = C.button_states(normal, HUB, b.id)
    frame = C.base_frame(HUB, seed=SEED)          # lean frame: coin tabs and grips
    return bg, buttons, frame


def paint_template():
    """template_chest_3: the plain utility look, nothing added."""
    return C.base_background(TPL, seed=SEED), C.base_frame(TPL, seed=SEED)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _raw(img):
    out = io.BytesIO()
    C.normalise(img).save(out, format='PNG')
    return out.getvalue()


def _stray(key, img):
    """Opaque frame pixels outside the lean tabs and grips (must be none)."""
    parts = C.frame_parts(key)
    boxes = parts['tabs'] + parts['grips']
    a = img.getchannel('A').load()
    return [(x, y) for y in range(img.height) for x in range(img.width)
            if a[x, y] and not any(r.contains(x, y) for r in boxes)]


def _pixels(img):
    return list(img.get_flattened_data() if hasattr(img, 'get_flattened_data') else img.getdata())


def _bands_light(key, img):
    for r in C.text_rows(key):
        vals = [luminance(p) for p in _pixels(img.crop(r.crop_box())) if p[3]]
        mean = sum(vals) / len(vals)
        dark = sum(1 for v in vals if v < 120) / len(vals)
        assert mean >= 180 and dark <= 0.08, f'{key}: text rows {r} too dark ({mean:.0f}, {dark:.0%})'


def validate(hub, tpl):
    from faithful import palette as PAL
    layouts, skins, config = geo.raw_manifests()
    for key, (bg, buttons, frame) in ((HUB, hub), (TPL, (tpl[0], {}, tpl[1]))):
        sk = skins[key]; g = layouts[sk['layout']]
        build_pack.validate_png(_raw(bg), g, sk, key)
        _bands_light(key, bg)
        layer = config['screens'][key]['artLayers'][0]
        decorative_assets.validate(_raw(frame), layer, g)
        assert not _stray(key, frame), f'{key}: frame paints outside its tabs and grips'
        for bid, states in buttons.items():
            bdef = next(b for b in config['screens'][key]['buttons'] if b['id'] == bid)
            for st, im in states.items():
                button_assets.validate_button(_raw(im), g, sk, bdef, st)
                assert im.getchannel('A').tobytes() == states['normal'].getchannel('A').tobytes(), (bid, st)
                assert PAL.off_palette(im) == 0, f'{bid}/{st}: off-palette pixels'
        for name, im in (('background', bg), ('frame', frame)):
            assert PAL.off_palette(im) == 0, f'{key} {name}: off-palette pixels'
    print('PASS example: economy_hub background, 8 buttons x 6 states, frame; template_chest_3 background '
          'and frame (builder validators, palette, light text rows, lean frame parts only)')


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------

def button_strip(states, scale=4):
    b = geo.skin(HUB).button(BTN_ID)
    pad = 10
    W = len(states) * (b.w * scale + pad) + pad
    img = Image.new('RGBA', (W, b.h * scale + 34), GREY[6] + (255,))
    d = ImageDraw.Draw(img)
    for i, (st, im) in enumerate(states.items()):
        x = pad + i * (b.w * scale + pad)
        img.alpha_composite(im.resize((b.w * scale, b.h * scale), Image.Resampling.NEAREST), (x, 8))
        d.text((x, b.h * scale + 14), st, fill=(40, 40, 40), font=preview._font(13))
    return img


def main():
    hub = paint_hub()
    tpl = paint_template()
    validate(hub, tpl)
    bg, buttons, frame = hub
    s = geo.skin(HUB)
    C.save_png(bg, TEX / 'menu' / Path(s.asset).name)
    C.save_png(frame, TEX / 'frames' / HUB / f'{s.layer().id}.png')
    for bid, states in buttons.items():
        C.save_button_states(states, HUB, bid, root=TEX)
    t = geo.skin(TPL)
    C.save_png(tpl[0], TEX / 'menu' / Path(t.asset).name)
    C.save_png(tpl[1], TEX / 'frames' / TPL / f'{t.layer().id}.png')
    preview.set_theme('faithful')
    a = preview.render(HUB, overrides_dir=TEX, scale=3, theme='faithful')
    b = preview.render(TPL, overrides_dir=TEX, scale=3, theme='faithful', content='full')
    strip = button_strip(buttons[BTN_ID])
    alone = preview.render_frame_alone(TPL, overrides_dir=TEX, scale=2)
    W = max(a.width + b.width + 12, strip.width + alone.width + 12)
    H = max(a.height, b.height) + 12 + max(strip.height, alone.height)
    sheet = Image.new('RGBA', (W, H), (36, 36, 36, 255))
    sheet.alpha_composite(a, (0, 0))
    sheet.alpha_composite(b, (a.width + 12, 0))
    y = max(a.height, b.height) + 12
    sheet.alpha_composite(strip, (0, y))
    sheet.alpha_composite(alone, (strip.width + 12, y))
    out = preview.export(sheet, OUT / 'preview.png',
                         'faithful example (quality bar) - schematic items/titles; textures in '
                         'evidence/faithful/example/assets')
    print('WROTE', out)


if __name__ == '__main__':
    main()
