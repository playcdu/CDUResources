#!/usr/bin/env python3
"""Validate cozy textures with the builder's own validators.

    python tools/cozy/validate.py auction_house trade_money
    python tools/cozy/validate.py --all
    python tools/cozy/validate.py economy_hub --style          # + cozy style lint
    python tools/cozy/validate.py --all --isolated-build       # + full build in a temp copy

Default mode reads the pack-source PNGs of the named skins and runs, in-process,
exactly the functions ``tools/build_pack.py`` uses:

* backgrounds: ``build_pack.validate_png``
* buttons (6 states each): ``button_assets.validate_button``
* frames: ``decorative_assets.validate``

against the real manifests (after ``button_assets.load`` derives visible content
slots, as the builder does). One line per asset: ``PASS <path>`` or
``FAIL <path>: <exact error>``. Exit status is non-zero on any failure.

``--isolated-build`` additionally copies pack-source, manifests, tools and the
root docs into a fresh temporary directory and runs
``build_pack.py --no-kit --output <temp>/quasar-gui.zip`` there, so nothing in
the shared tree or deliverables/ is written. ``--style`` adds non-fatal cozy
lint (palette conformance, light title / inventory bands, no pure black/white);
``--strict-style`` makes those lint findings fatal.

Licence: MIT.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parents[1]
for _p in (str(_HERE), str(ROOT / 'tools')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import build_pack  # noqa: E402
import button_assets  # noqa: E402
import decorative_assets  # noqa: E402
import geometry  # noqa: E402
import palette  # noqa: E402
from PIL import Image  # noqa: E402

TEX = 'assets/quasar_gui/textures'
HINT = chr(10) + '     hint: '


def _rel(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def button_hint(key, button_id, path):
    """Plain-language diagnosis for a failing button PNG (printed under FAIL)."""
    b = geometry.skin(key).button(button_id)
    try:
        img = Image.open(path)
    except Exception as exc:  # noqa: BLE001
        return f'cannot open: {exc}'
    if img.mode != 'RGBA' or img.size != (b.w, b.h):
        return f'need RGBA {b.w}x{b.h}, got {img.mode} {img.size[0]}x{img.size[1]}'
    a = img.getchannel('A')
    notes = []
    if a.getpixel(b.pin) != 255:
        notes.append(f'pin pixel {b.pin} must be alpha 255 (geometry.stamp_button_pin)')
    bbox = a.getbbox()
    if bbox and bbox[2] != b.pin[0] + 1:
        notes.append(f'opaque pixels must end at column {b.pin[0]}; found up to column {bbox[2] - 1} '
                     '(geometry.clear_button_masks clears right of the pin)')
    for m in b.masks:
        if a.crop(m.crop_box()).getbbox():
            notes.append(f'mask {m.tuple()} (button-local) must be alpha 0 (geometry.clear_button_masks)')
    return '; '.join(notes) or 'see builder message'


def _check(results, path, fn):
    path = Path(path)
    if not path.is_file():
        results.append((False, _rel(path), 'missing file'))
        return None
    raw = path.read_bytes()
    try:
        fn(raw)
    except Exception as exc:  # the builder raises ValueError; report anything verbatim
        results.append((False, _rel(path), f'{exc}'))
        return raw
    results.append((True, _rel(path), ''))
    return raw


def validate_skin(key, source_root=None, style=False):
    """Return a list of (ok, path, message) for every asset of ``key``.

    ``source_root`` defaults to pack-source; pass another directory laid out as
    ``assets/quasar_gui/textures/...`` to validate experiments elsewhere.
    """
    layouts, skins, config = geometry.raw_manifests()
    s = skins[key]
    g = layouts[s['layout']]
    base = Path(source_root) if source_root else ROOT / 'pack-source'
    results = []
    raw = _check(results, base / s['asset'], lambda r: build_pack.validate_png(r, g, s, key))
    if style and raw is not None:
        results += style_lint(key, Image.open(base / s['asset']).convert('RGBA'), 'background',
                              _rel(base / s['asset']))
    screen = config['screens'].get(key, {'buttons': []})
    for b in screen['buttons']:
        for state in button_assets.STATES:
            p = base / TEX / 'buttons' / key / b['id'] / f'{state}.png'
            raw = _check(results, p, lambda r, b=b, state=state: button_assets.validate_button(r, g, s, b, state))
            if results[-1][0] is False and p.is_file():
                ok_, path_, msg_ = results[-1]
                results[-1] = (False, path_, msg_ + HINT + button_hint(key, b['id'], p))
            if style and raw is not None:
                results += style_lint(key, Image.open(p).convert('RGBA'), 'button', _rel(p))
    for layer in screen.get('artLayers', []):
        p = base / TEX / 'frames' / key / f'{layer["id"]}.png'
        raw = _check(results, p, lambda r, layer=layer: decorative_assets.validate(r, layer, g))
        if style and raw is not None:
            results += style_lint(key, Image.open(p).convert('RGBA'), 'frame', _rel(p))
    return results


def _pixels(img):
    return list(img.get_flattened_data() if hasattr(img, 'get_flattened_data') else img.getdata())


def text_rows(key):
    """Rectangles where live vanilla glyphs actually land (cap + descender rows):
    title rows anchor_y-1 .. anchor_y+7 across the text-safe width (none on the
    dispenser) and inventory rows label_y-1 .. label_y+7 across its band."""
    s = geometry.skin(key)
    out = []
    if not s.is_dispenser:
        ay = s.title_anchor[1]
        out.append(('title', geometry.Rect(s.text_safe.x, ay - 1, s.text_safe.w, 9)))
    iv = s.inventory_label
    out.append(('inventory label', geometry.Rect(iv.x, iv.y - 1, iv.w, 9)))
    return out


def style_lint(key, img, kind, label):
    """Cozy style checks. Returns (ok, path, message) tuples tagged 'STYLE'."""
    out = []
    pixels = [p for p in _pixels(img) if p[3]]
    if pixels:
        allowed = set(palette.MASTER)
        off = sum(1 for p in pixels if tuple(p[:3]) not in allowed)
        if off:
            out.append((None, label, f'STYLE {off}/{len(pixels)} opaque pixels are off the master palette'))
        extremes = sum(1 for p in pixels if tuple(p[:3]) in ((0, 0, 0), (255, 255, 255)))
        if extremes:
            out.append((None, label, f'STYLE {extremes} pure black/white pixels'))
        partial = sum(1 for p in pixels if p[3] != 255)
        if partial:
            out.append((None, label, f'STYLE {partial} semi-transparent pixels (use 0 or 255)'))
    if kind == 'background':
        for name, r in text_rows(key):
            crop = img.crop(r.crop_box())
            vals = [palette.luminance(p) for p in _pixels(crop) if p[3]]
            if not vals:
                continue
            mean = sum(vals) / len(vals)
            dark = sum(1 for v in vals if v < 120) / len(vals)
            if mean < 180 or dark > 0.08:
                out.append((None, label, f'STYLE {name} band is not light enough for live dark-grey text '
                                         f'(mean luminance {mean:.0f}, {dark:.0%} dark pixels; want >=180 and <=8%)'))
    return out


def isolated_build(keep=False):
    """Copy the repository inputs to a temp dir and run the real builder there."""
    tmp = Path(tempfile.mkdtemp(prefix='cozy-build-'))
    try:
        ignore = shutil.ignore_patterns('__pycache__', '*.pyc')
        for d in ('pack-source', 'manifests', 'tools'):
            shutil.copytree(ROOT / d, tmp / d, ignore=ignore)
        for f in ('START-HERE.md', 'README.md', 'LICENSE.txt', 'CLIENT-COMPATIBILITY.md', 'requirements.txt',
                  '.python-version'):
            if (ROOT / f).is_file():
                shutil.copy2(ROOT / f, tmp / f)
        if (ROOT / 'docs').is_dir():
            shutil.copytree(ROOT / 'docs', tmp / 'docs', ignore=ignore)
        before = {p.relative_to(tmp).as_posix(): hashlib.sha1(p.read_bytes()).hexdigest()
                  for p in (tmp / 'pack-source').rglob('*') if p.is_file()}
        out = tmp / 'quasar-gui.zip'
        cmd = [sys.executable, str(tmp / 'tools' / 'build_pack.py'), '--no-kit', '--output', str(out)]
        proc = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)
        lines = []
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout).strip().splitlines()[-12:]
            return False, ['FAIL isolated build: build_pack.py exited %d' % proc.returncode] + ['  ' + t for t in tail], tmp
        after = {p.relative_to(tmp).as_posix(): hashlib.sha1(p.read_bytes()).hexdigest()
                 for p in (tmp / 'pack-source').rglob('*') if p.is_file()}
        generated = sorted(set(after) - set(before))
        changed = sorted(k for k in before if k in after and before[k] != after[k])
        ok = True
        if generated:
            ok = False
            lines.append(f'FAIL isolated build generated {len(generated)} missing pack-source file(s), e.g. {generated[:3]}')
        if changed:
            ok = False
            lines.append(f'FAIL isolated build rewrote {len(changed)} pack-source file(s), e.g. {changed[:3]}')
        check = subprocess.run([sys.executable, str(tmp / 'tools' / 'build_pack.py'), '--validate', str(out)],
                               cwd=tmp, capture_output=True, text=True)
        if check.returncode != 0:
            ok = False
            lines.append('FAIL isolated build: --validate of the built zip failed: ' +
                         (check.stderr or check.stdout).strip().splitlines()[-1])
        if ok:
            sha1 = hashlib.sha1(out.read_bytes()).hexdigest()
            lines.append(f'PASS isolated build ({out.stat().st_size} bytes, sha1 {sha1}) in a temp copy; '
                         'shared tree and deliverables untouched')
        return ok, lines, tmp
    finally:
        if not keep:
            shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('skins', nargs='*', help='skin keys to validate')
    ap.add_argument('--all', action='store_true', help='validate all 60 skins')
    ap.add_argument('--isolated-build', action='store_true', help='also run the real builder in a temp copy')
    ap.add_argument('--keep-temp', action='store_true', help='keep the isolated build directory')
    ap.add_argument('--source-root', type=Path, help='validate a directory laid out like pack-source instead')
    ap.add_argument('--style', action='store_true', help='print non-fatal cozy style lint')
    ap.add_argument('--strict-style', action='store_true', help='style lint findings are failures')
    ap.add_argument('--quiet', action='store_true', help='only print failures and the summary')
    a = ap.parse_args(argv)
    keys = geometry.all_skins() if a.all else a.skins
    if not keys and not a.isolated_build:
        ap.error('name at least one skin or pass --all')
    unknown = [k for k in keys if k not in geometry.all_skins()]
    if unknown:
        ap.error('unknown skin(s): ' + ', '.join(unknown))
    failures = 0
    passes = 0
    lint = 0
    for key in keys:
        for ok, path, msg in validate_skin(key, a.source_root, a.style or a.strict_style):
            if ok is True:
                passes += 1
                if not a.quiet:
                    print(f'PASS {path}')
            elif ok is False:
                failures += 1
                print(f'FAIL {path}: {msg}')
            else:
                lint += 1
                print(f'{"FAIL" if a.strict_style else "WARN"} {path}: {msg}')
    if a.strict_style:
        failures += lint
    if keys:
        print(f'SUMMARY {passes} passed, {failures} failed' + (f', {lint} style findings' if lint else '') +
              f' across {len(keys)} skin(s)')
    if a.isolated_build:
        ok, lines, tmp = isolated_build(a.keep_temp)
        for line in lines:
            print(line)
        if a.keep_temp:
            print(f'INFO isolated build directory kept at {tmp}')
        if not ok:
            failures += 1
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
