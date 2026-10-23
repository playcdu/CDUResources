#!/usr/bin/env python3
"""Self-test for the Faithful toolkit (writes nothing).

    python tools/faithful/selftest.py                      # toolkit + any Faithful-painted pack-source skins
    python tools/faithful/selftest.py --pack-source        # also check EVERY pack-source skin as Faithful art
    python tools/faithful/selftest.py --skip-pack-source   # toolkit checks only

1. geometry (tools/cozy/geometry.py, shared) matches manifests/runtime-registry.json
   (button rects, pins, default states, frame pins) and resolved-layouts.json
   (background masks);
2. the palette has 24 unique colours; the PLAIN fit requirements hold
   (LISTINGS 50, DISABLE LISTING 104, PURCHASE 50, 12 DAYS 68); every
   kerning pair of PLAIN and TINY passes ``lettering.audit_kerning`` (no two
   glyphs touch at 1x); every one of the button labels fits its grammar's
   text box (``paint_button`` raises otherwise);
3. compose.base_background / base_frame / paint_button + button_states
   produce images that pass the builder's own validators for EVERY skin,
   button and state; every pixel is on the Faithful palette with alpha 0 or
   255; the live title and inventory glyph rows are light, and the title
   zone (rows 5-14, x 4-171) holds nothing but panel colour (the dispenser's
   OFFERED MONEY label excepted); every skin with a family accent has a tray
   wall to tint, and invsee_online / invsee_offline differ; frames are lean
   docked tabs: opaque only inside ``compose.frame_parts`` (tabs and grips),
   nothing in the container, the right grip on the pin, left and right
   mirrored; the state transforms leave alpha byte-identical; selected never
   changes a glyph-like pixel (lettering, page arrow, close X, icon) or the
   shadow drawn under it; no pulse changes those pixels or their 1 px halo;
   disabled keeps every glyph-like pixel in place, at the same alpha, in the
   disabled register (grey_5, or ink_0 for an icon's outline); every lettered
   button has detectable lettering; ``compose.lettering_mask`` and
   ``compose.extras_mask`` run on a COPY of the normal frame (so they must
   find the glyphs geometrically, not from the paint registry) cover at
   least 90 % of what was drawn; the six state images of every button are
   pairwise different. (Disabled cracks: not applicable, the Faithful
   disabled state is a flat face.)
4. pack-source: by default every skin whose background is already entirely
   on the Faithful palette (painted in this theme) gets the title-zone,
   lean-frame, lettering, distinct-state and state-preservation checks on
   its PNGs; other skins are
   counted as "not yet Faithful" and skipped. ``--pack-source`` checks every
   skin regardless; ``--skip-pack-source`` checks none.

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
from faithful import compose as C  # noqa: E402
from faithful import lettering as L  # noqa: E402
from faithful import palette as PAL  # noqa: E402

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


def on_palette(img):
    allowed = set(PAL.MASTER)
    return all(tuple(p[:3]) in allowed for p in _pixels(img) if p[3])


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


def frame_errors(key, layer_id, img, label):
    """Lean docked-tab frames: opaque pixels only inside the tabs and grips
    of ``compose.frame_parts`` (alpha 0 everywhere else, the 8 px strips and
    the container included), the right grip reaching the pin at (w-1, h//2),
    and the left and right halves mirror images in alpha."""
    a = geo.skin(key).layer(layer_id)
    parts = C.frame_parts(key, layer_id)
    boxes = parts['tabs'] + parts['grips']
    al = img.getchannel('A').load()
    w, h = img.size
    errs = []
    stray = [(x, y) for y in range(h) for x in range(w)
             if al[x, y] and not any(r.contains(x, y) for r in boxes)]
    if stray:
        errs.append(f'{label}: {len(stray)} opaque pixel(s) outside the tabs and grips, e.g. {stray[:3]}')
    inside = [(x, y) for y in range(a.container.y, a.container.bottom)
              for x in range(a.container.x, a.container.right) if al[x, y]]
    if inside:
        errs.append(f'{label}: {len(inside)} opaque pixel(s) inside the container')
    if al[w - 1, h // 2] != 255 or img.getchannel('A').getbbox()[2] != w:
        errs.append(f'{label}: right grip does not reach the pin ({w - 1}, {h // 2})')
    if any(bool(al[x, y]) != bool(al[w - 1 - x, y]) for y in range(h) for x in range(w // 2)):
        errs.append(f'{label}: left and right halves are not mirror images')
    for r in parts['grips']:
        if any(al[x, y] != 255 for y in range(r.y + 1, r.bottom - 1) for x in range(r.x + 1, r.right - 1)):
            errs.append(f'{label}: grip {r.tuple()} not solid')
    return errs


def title_zone_errors(key, img, label):
    """Rows 5-14 across x 4-171 hold nothing but panel colour (the dispenser
    may also hold its static OFFERED MONEY label in ink_1)."""
    s = geo.skin(key)
    panel = tuple(C.sheet_for(key)[2])
    ok = {panel} | ({PAL.INK[1]} if s.is_dispenser else set())
    z = C.TITLE_ZONE
    bad = [(x, y) for y in range(z.y, z.bottom) for x in range(z.x, z.right)
           if tuple(img.getpixel((x, y))[:3]) not in ok or img.getpixel((x, y))[3] != 255]
    return [f'{label}: {len(bad)} non-panel pixel(s) in the title zone rows 5-14, e.g. {bad[:3]}'] if bad else []


def band_errors(key, img):
    """The live text rows must be light (same rule as validate.py --style)."""
    errs = []
    for r in C.text_rows(key):
        vals = [PAL.luminance(p) for p in _pixels(img.crop(r.crop_box())) if p[3]]
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        dark = sum(1 for v in vals if v < 120) / len(vals)
        if mean < 180 or dark > 0.08:
            errs.append(f'{key}: text rows {r.tuple()} too dark (mean {mean:.0f}, {dark:.0%} dark)')
    return errs


def state_errors(normal, states, button, label):
    """Selected keeps the glyph footprint; pulses keep footprint + halo;
    disabled keeps glyph positions/alpha in the disabled register."""
    errs = []
    glyphs, extras, footprint, protect = C.state_masks(normal, button)
    npx = normal.load()
    spx = states['selected'].load()
    bad = [xy for xy in footprint if spx[xy] != npx[xy]]
    if bad:
        errs.append(f'{label}/selected: changed {len(bad)} glyph/shadow pixel(s), e.g. {sorted(bad)[:3]}')
    for st in ('pulse_1', 'pulse_2', 'pulse_3'):
        ppx = states[st].load()
        bad = [xy for xy in protect if ppx[xy] != npx[xy]]
        if bad:
            errs.append(f'{label}/{st}: changed {len(bad)} pixel(s) of the glyphs, shadow or 1 px halo, '
                        f'e.g. {sorted(bad)[:3]}')
    dpx = states['disabled'].load()
    dead = {PAL.GREY[5], PAL.INK[0]}
    for xy in sorted(glyphs | extras):
        q = dpx[xy]
        if q[3] != npx[xy][3] or tuple(q[:3]) not in dead:
            errs.append(f'{label}/disabled: glyph pixel {xy} not dimmed in place ({q})')
            break
    for st in ('selected', 'pulse_1', 'disabled'):
        if states[st].tobytes() == normal.tobytes():
            errs.append(f'{label}/{st}: state identical to normal')
    return errs, glyphs, extras


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pack-source', action='store_true', help='check every pack-source skin as Faithful art')
    ap.add_argument('--skip-pack-source', action='store_true', help='skip the pack-source checks')
    a = ap.parse_args(argv)
    errors = []
    reg = json.loads((geo.ROOT / 'manifests/runtime-registry.json').read_text(encoding='utf-8'))
    res = json.loads((geo.ROOT / 'manifests/resolved-layouts.json').read_text(encoding='utf-8'))
    layouts, skins, config = geo.raw_manifests()
    if len(PAL.MASTER) != 24 or len(set(PAL.MASTER)) != 24:
        errors.append('palette: expected 24 unique colours')
    for text, limit in L.FIT_CHECKS:
        if L.text_width(text) > limit:
            errors.append(f'lettering: {text!r} is {L.text_width(text)} px > {limit}')
    for face in ('plain', 'tiny'):
        for bad in L.audit_kerning(face):
            errors.append(f'lettering: {face} kerning pair {bad[0]}{bad[1]} {bad[2]}')
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
            errors += title_zone_errors(key, bg, f'{key} background')
            probe = C.base_background(key, seed=1, accent=False)
            tinted = C.draw_accent_line(probe, key)
            if C.accent_colour(key) is not None and C.wall_colour(C.accent_colour(key)) and not tinted:
                errors.append(f'{key}: family accent has no tray wall to tint')
            for layer in config['screens'].get(key, {}).get('artLayers', []):
                fr = C.base_frame(key, layer['id'], seed=1)
                decorative_assets.validate(_raw(fr), layer, g); n_img += 1
                errors += palette_errors(fr, f'{key}/{layer["id"]} frame')
                errors += frame_errors(key, layer['id'], fr, f'{key}/{layer["id"]} frame')
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
                kind = C.button_kind(b)
                if kind not in ('close', 'icon'):
                    layout = C.lettered_pixels(normal, b) or set()
                    if not C.lettering_mask(normal, b, halo=False):
                        errors.append(f'{key}/{b.id}: no lettering detected')
                    drawn = {xy for xy in layout if normal.getpixel(xy)[3]}
                    found = C.lettering_mask(normal.copy(), b, halo=False)
                    cover = len(drawn & found) / len(drawn) if drawn else 0.0
                    covered.append(cover)
                    if cover < 0.9:
                        errors.append(f'{key}/{b.id}: lettering mask covers {cover:.0%} of the drawn label (< 90%)')
                drawn_x = C._recall(C._EXTRAS, normal, b) or set()
                if drawn_x:
                    found_x = C.extras_mask(normal.copy(), b)
                    cover = len(drawn_x & found_x) / len(drawn_x)
                    if cover < 0.9:
                        errors.append(f'{key}/{b.id}: extras mask (arrow / X / icon) covers {cover:.0%} on a copy')
                errors += distinct_errors(states, f'{key}/{b.id}')
                errs, _, _ = state_errors(normal, states, b, f'{key}/{b.id}')
                errors += errs
                n_btn += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f'{key}: {type(exc).__name__}: {exc}')
    on, off = C.base_background('invsee_online', 1), C.base_background('invsee_offline', 1)
    if on.tobytes() == off.tobytes():
        errors.append('invsee_online and invsee_offline backgrounds are identical')
    painted = skipped = 0
    if not a.skip_pack_source:
        for key in geo.all_skins():
            s = geo.skin(key)
            if not a.pack_source and not on_palette(Image.open(s.background_path).convert('RGBA')):
                skipped += 1
                continue
            errors += title_zone_errors(key, Image.open(s.background_path).convert('RGBA'), f'pack-source {key}')
            for la in s.art_layers:
                errors += frame_errors(key, la.id, Image.open(s.frame_path(la.id)).convert('RGBA'),
                                       f'pack-source {key}/{la.id} frame')
            for b in s.buttons:
                normal = Image.open(s.button_path(b.id, 'normal')).convert('RGBA')
                states = {st: Image.open(s.button_path(b.id, st)).convert('RGBA') for st in geo.STATES}
                if C.button_kind(b) not in ('close', 'icon') and not C.lettering_mask(normal, b):
                    errors.append(f'pack-source {key}/{b.id}: no Faithful lettering detected')
                errors += distinct_errors(states, f'pack-source {key}/{b.id}')
                errs, _, _ = state_errors(normal, states, b, f'pack-source {key}/{b.id}')
                errors += errs
                painted += 1
    for e in errors:
        print('FAIL', e)
    print(f'SELFTEST {"FAILED" if errors else "PASSED"}: {len(geo.all_skins())} skins, {n_btn} buttons, '
          f'{n_img} generated images checked with the builder validators, palette, light text rows, title zone, '
          f'family tray tint, lean frames, '
          f'glyph preservation and distinct states'
          + (f', mask coverage min {min(covered):.0%} over {len(covered)} lettered buttons' if covered else '')
          + ('' if a.skip_pack_source else
             f'; pack-source: {painted} Faithful-painted buttons checked, {skipped} skins not yet Faithful (skipped)'))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
