#!/usr/bin/env python3
"""Self-test for the Soulrend toolkit (writes nothing).

    python tools/soulrend/selftest.py                      # toolkit + painted pack-source checks
    python tools/soulrend/selftest.py --skip-pack-source   # toolkit checks only

1. geometry (tools/cozy/geometry.py, shared) matches manifests/runtime-registry.json
   (button rects, pins, default states, frame pins) and resolved-layouts.json
   (background masks);
2. the palette has 36 unique colours without pure black/white, and the GRAVEN
   fit requirements hold (LISTINGS 50, DISABLE LISTING 104, PURCHASE 50,
   12 DAYS 68); every one of the button labels fits its grammar's text box;
3. compose.base_background / base_frame / paint_button + button_states produce
   images that pass the builder's own validators for EVERY skin, button and
   state; every pixel is on the Soulrend palette with alpha 0 or 255; the
   live title and inventory glyph rows are light vellum (the --style lint);
   the state transforms leave alpha byte-identical; selected never changes a
   lettering pixel and pulses never change a lettering pixel or its 1 px halo;
   disabled keeps every lettering pixel in place but only in the dead-stone
   register (ink or iron_3 / ink_1, never gold, vellum, blood, ember or soul);
   every lettered button has detectable lettering; the six state images of
   every button are pairwise different (pulse_1 != pulse_2 != pulse_3); and
   ``compose.lettering_mask`` run on a COPY of the normal frame (so it must
   find the label geometrically, not from ``letter``'s record) covers at
   least 90 % of the label pixels ``compose.letter`` drew;
4. unless ``--skip-pack-source``: on the painted pack-source buttons, the six
   states are pairwise different, lettering is detected on every lettered
   button, and no pulse touches the lettering or its halo.

Licence: MIT.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _p in (str(_HERE.parent), str(_HERE.parent / 'cozy')):
    if _p not in sys.path:
        sys.path.append(_p)

from PIL import Image  # noqa: E402

import geometry as geo  # noqa: E402
from soulrend import compose as C  # noqa: E402
from soulrend import lettering as L  # noqa: E402
from soulrend import palette as PAL  # noqa: E402

import build_pack  # noqa: E402
import button_assets  # noqa: E402
import decorative_assets  # noqa: E402


def _raw(img):
    out = io.BytesIO()
    C.normalise(img).save(out, format='PNG')
    return out.getvalue()


def _pixels(img):
    return list(img.get_flattened_data() if hasattr(img, 'get_flattened_data') else img.getdata())


def palette_errors(img, label):
    allowed = set(PAL.MASTER)
    errs = []
    px = [p for p in _pixels(img) if p[3]]
    off = sum(1 for p in px if tuple(p[:3]) not in allowed)
    if off:
        errs.append(f'{label}: {off} off-palette pixels')
    partial = sum(1 for p in px if p[3] != 255)
    if partial:
        errs.append(f'{label}: {partial} semi-transparent pixels')
    return errs


def distinct_errors(states, label):
    """Every pair of the six state images must differ."""
    errs = []
    names = list(states)
    raw = {st: states[st].tobytes() for st in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if raw[a] == raw[b]:
                errs.append(f'{label}: {a} and {b} are identical')
    return errs


def band_errors(key, img):
    """The live text rows must be light (same rule as validate.py --style)."""
    s = geo.skin(key)
    rows = []
    if not s.is_dispenser:
        rows.append(('title', geo.Rect(s.text_safe.x, s.title_anchor[1] - 1, s.text_safe.w, 9)))
    iv = s.inventory_label
    rows.append(('inventory', geo.Rect(iv.x, iv.y - 1, iv.w, 9)))
    errs = []
    for name, r in rows:
        vals = [PAL.luminance(p) for p in _pixels(img.crop(r.crop_box())) if p[3]]
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        dark = sum(1 for v in vals if v < 120) / len(vals)
        if mean < 180 or dark > 0.08:
            errs.append(f'{key}: {name} band too dark (mean {mean:.0f}, {dark:.0%} dark)')
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pack-source', action='store_true', help='(default; kept for compatibility)')
    ap.add_argument('--skip-pack-source', action='store_true', help='skip the painted pack-source button checks')
    a = ap.parse_args(argv)
    a.pack_source = not a.skip_pack_source
    errors = []
    reg = json.loads((geo.ROOT / 'manifests/runtime-registry.json').read_text(encoding='utf-8'))
    res = json.loads((geo.ROOT / 'manifests/resolved-layouts.json').read_text(encoding='utf-8'))
    layouts, skins, config = geo.raw_manifests()
    if len(PAL.MASTER) != 36 or len(set(PAL.MASTER)) != 36:
        errors.append('palette: expected 36 unique colours')
    for text, limit in L.FIT_CHECKS:
        if L.text_width(text) > limit:
            errors.append(f'lettering: {text!r} is {L.text_width(text)} px > {limit}')
    n_btn = n_img = 0
    covered = []
    for key in geo.all_skins():
        s = geo.skin(key)
        if key in res['skins'] and \
                [list(m.tuple()) for m in s.masks] != [list(m) for m in res['skins'][key]['transparentMasks']]:
            errors.append(f'{key}: masks differ from resolved-layouts.json')
        for r in reg['skins'].get(key, {}).get('buttonRegions', []):
            b = s.button(r['id'])
            if (b.x, b.y, b.w, b.h) != (r['x'], r['y'], r['width'], r['height']) or \
                    list(b.pin) != r['states']['normal']['advancePin'] or b.default_state != r['defaultState']:
                errors.append(f'{key}/{b.id}: geometry differs from runtime registry')
        for r in reg['skins'].get(key, {}).get('artLayers', []):
            if list(s.layer(r['id']).pin) != r['advancePin']:
                errors.append(f'{key}/{r["id"]}: frame pin differs')
        sk = skins[key]; g = layouts[sk['layout']]
        try:
            bg = C.base_background(key, seed=1)
            build_pack.validate_png(_raw(bg), g, sk, key); n_img += 1
            errors += palette_errors(bg, f'{key} background')
            errors += band_errors(key, bg)
            for layer in config['screens'].get(key, {}).get('artLayers', []):
                fr = C.base_frame(key, layer['id'], seed=1)
                decorative_assets.validate(_raw(fr), layer, g); n_img += 1
                errors += palette_errors(fr, f'{key}/{layer["id"]} frame')
            for bdef in config['screens'].get(key, {}).get('buttons', []):
                b = s.button(bdef['id'])
                normal = C.paint_button(key, bdef['id'], seed=1)
                states = C.button_states(normal, key, bdef['id'])
                alpha = states['normal'].getchannel('A').tobytes()
                for st, im in states.items():
                    button_assets.validate_button(_raw(im), g, sk, bdef, st); n_img += 1
                    if im.getchannel('A').tobytes() != alpha:
                        errors.append(f'{key}/{b.id}/{st}: transform changed alpha')
                    errors += palette_errors(im, f'{key}/{b.id}/{st}')
                glyphs = C.lettering_mask(normal, b, halo=False)
                halo = C.lettering_mask(normal, b, halo=True)
                if C.button_kind(b) not in ('close', 'icon'):
                    if not glyphs:
                        errors.append(f'{key}/{b.id}: no lettering detected')
                    drawn = {xy for xy in (C.lettered_pixels(normal, b) or ()) if normal.getpixel(xy)[3]}
                    found = C.lettering_mask(normal.copy(), b, halo=False)
                    cover = len(drawn & found) / len(drawn) if drawn else 0.0
                    covered.append(cover)
                    if cover < 0.9:
                        errors.append(f'{key}/{b.id}: lettering mask covers {cover:.0%} of the drawn label (< 90%)')
                errors += distinct_errors(states, f'{key}/{b.id}')
                if any(states['selected'].getpixel(xy) != normal.getpixel(xy) for xy in glyphs):
                    errors.append(f'{key}/{b.id}/selected: transform touched lettering')
                dead = {PAL.IRON[3], PAL.INK[0], PAL.INK[1], PAL.INK[2]}
                for xy in glyphs:
                    q = states['disabled'].getpixel(xy)
                    if q[3] != normal.getpixel(xy)[3] or tuple(q[:3]) not in dead:
                        errors.append(f'{key}/{b.id}/disabled: lettering pixel {xy} not dimmed to dead stone')
                        break
                for st in ('pulse_1', 'pulse_2', 'pulse_3'):
                    if any(states[st].getpixel(xy) != normal.getpixel(xy) for xy in halo):
                        errors.append(f'{key}/{b.id}/{st}: pulse touched lettering')
                for st in ('selected', 'pulse_1'):
                    if states[st].tobytes() == normal.tobytes():
                        errors.append(f'{key}/{b.id}/{st}: state identical to normal')
                n_btn += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f'{key}: {type(exc).__name__}: {exc}')
    painted = 0
    if a.pack_source:
        for key in geo.all_skins():
            s = geo.skin(key)
            for b in s.buttons:
                normal = Image.open(s.button_path(b.id, 'normal')).convert('RGBA')
                glyphs = C.lettering_mask(normal, b)
                if C.button_kind(b) not in ('close', 'icon') and not glyphs:
                    errors.append(f'pack-source {key}/{b.id}: no Soulrend lettering detected')
                states = {st: Image.open(s.button_path(b.id, st)).convert('RGBA') for st in geo.STATES}
                for st in ('pulse_1', 'pulse_2', 'pulse_3'):
                    if any(states[st].getpixel(xy) != normal.getpixel(xy) for xy in glyphs):
                        errors.append(f'pack-source {key}/{b.id}/{st}: pulse touched lettering')
                errors += distinct_errors(states, f'pack-source {key}/{b.id}')
                painted += 1
    for e in errors:
        print('FAIL', e)
    print(f'SELFTEST {"FAILED" if errors else "PASSED"}: {len(geo.all_skins())} skins, {n_btn} buttons, '
          f'{n_img} generated images checked with the builder validators, palette, light text bands and '
          f'lettering preservation, distinct states'
          + (f', mask coverage min {min(covered):.0%} over {len(covered)} lettered buttons' if covered else '')
          + (f'; {painted} painted pack-source buttons checked' if a.pack_source else ''))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
