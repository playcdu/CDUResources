#!/usr/bin/env python3
"""Self-test for the cozy toolkit (writes nothing).

    python tools/cozy/selftest.py

1. geometry matches manifests/runtime-registry.json (button rects, pins,
   default states, frame pins) and resolved-layouts.json (background masks);
2. the HEARTH fit requirements hold;
3. compose.base_background / base_frame / paint_button + button_states produce
   images that pass the builder's own validators for EVERY skin, button and
   state, the state transforms leave alpha byte-identical, and pulse frames
   leave every lettering pixel (and its 1 px halo) untouched;
4. the same lettering check on the painted pack-source buttons.

Licence: MIT.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from PIL import Image  # noqa: E402

import compose as C  # noqa: E402
import geometry as geo  # noqa: E402
import lettering as L  # noqa: E402

import build_pack  # noqa: E402
import button_assets  # noqa: E402
import decorative_assets  # noqa: E402


def _raw(img):
    out = io.BytesIO()
    C.normalise(img).save(out, format='PNG')
    return out.getvalue()


def main():
    errors = []
    reg = json.loads((geo.ROOT / 'manifests/runtime-registry.json').read_text(encoding='utf-8'))
    res = json.loads((geo.ROOT / 'manifests/resolved-layouts.json').read_text(encoding='utf-8'))
    layouts, skins, config = geo.raw_manifests()
    n_btn = n_img = 0
    for key in geo.all_skins():
        s = geo.skin(key)
        if [list(m.tuple()) for m in s.masks] != [list(m) for m in res['skins'][key]['transparentMasks']]:
            errors.append(f'{key}: masks differ from resolved-layouts.json')
        for r in reg['skins'][key].get('buttonRegions', []):
            b = s.button(r['id'])
            if (b.x, b.y, b.w, b.h) != (r['x'], r['y'], r['width'], r['height']) or \
                    list(b.pin) != r['states']['normal']['advancePin'] or b.default_state != r['defaultState']:
                errors.append(f'{key}/{b.id}: geometry differs from runtime registry')
        for r in reg['skins'][key].get('artLayers', []):
            if list(s.layer(r['id']).pin) != r['advancePin']:
                errors.append(f'{key}/{r["id"]}: frame pin differs')
        sk = skins[key]; g = layouts[sk['layout']]
        try:
            build_pack.validate_png(_raw(C.base_background(key, seed=1)), g, sk, key); n_img += 1
            for layer in config['screens'][key].get('artLayers', []):
                decorative_assets.validate(_raw(C.base_frame(key, layer['id'], seed=1)), layer, g); n_img += 1
            for bdef in config['screens'][key]['buttons']:
                states = C.button_states(C.paint_button(key, bdef['id'], seed=1), key, bdef['id'])
                alpha = states['normal'].getchannel('A').tobytes()
                for st, im in states.items():
                    button_assets.validate_button(_raw(im), g, sk, bdef, st); n_img += 1
                    if im.getchannel('A').tobytes() != alpha:
                        errors.append(f'{key}/{bdef["id"]}/{st}: transform changed alpha')
                glyphs = C.lettering_mask(states['normal'], s.button(bdef['id']))
                for st in ('pulse_1', 'pulse_2', 'pulse_3'):
                    if any(states[st].getpixel(xy) != states['normal'].getpixel(xy) for xy in glyphs):
                        errors.append(f'{key}/{bdef["id"]}/{st}: pulse touched lettering')
                n_btn += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f'{key}: {exc}')
    painted = 0
    for key in geo.all_skins():
        s = geo.skin(key)
        for b in s.buttons:
            normal = Image.open(s.button_path(b.id, 'normal')).convert('RGBA')
            glyphs = C.lettering_mask(normal, b)
            if C.button_kind(b) not in ('close', 'icon') and not glyphs:
                errors.append(f'pack-source {key}/{b.id}: no lettering detected')
            for st in ('pulse_1', 'pulse_2', 'pulse_3'):
                im = Image.open(s.button_path(b.id, st)).convert('RGBA')
                if any(im.getpixel(xy) != normal.getpixel(xy) for xy in glyphs):
                    errors.append(f'pack-source {key}/{b.id}/{st}: pulse touched lettering')
            painted += 1
    for text, limit in L.FIT_CHECKS:
        if L.text_width(text) > limit:
            errors.append(f'lettering: {text!r} is {L.text_width(text)} px > {limit}')
    for e in errors:
        print('FAIL', e)
    print(f'SELFTEST {"FAILED" if errors else "PASSED"}: {len(geo.all_skins())} skins, {n_btn} buttons, '
          f'{n_img} generated images checked with the builder validators; lettering kept by pulses on '
          f'{painted} painted pack-source buttons')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
