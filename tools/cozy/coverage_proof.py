#!/usr/bin/env python3
"""Coverage proof: compare every baseline texture (from a fixed Git commit) with its replacement.

Reports counts by asset class, changed/unchanged/missing/unexpected assets and
dimension/mode mismatches. "Changed" requires the decoded RGBA pixels to differ;
re-encoding identical pixels does not count. Also confirms authored geometry and
action contracts are byte-identical to the baseline.

Usage: python tools/cozy/coverage_proof.py --baseline <sha> [--json out.json] [--verbose]
"""
from __future__ import annotations
import argparse, io, json, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2] if Path(__file__).resolve().parent.name == 'cozy' else Path.cwd()
TEX = 'pack-source/assets/quasar_gui/textures/'
CONTRACTS = ['manifests/button-layouts.json', 'manifests/layouts.json', 'manifests/skins.json']
CONTRACT_KEYS_IGNORED = set()  # skins.json is rewritten by the build; compare authored fields only

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout

def classify(path):
    rest = path[len(TEX):]
    return rest.split('/', 1)[0]

def decode(raw):
    im = Image.open(io.BytesIO(raw)); im.load()
    return im.mode, im.size, (im.convert('RGBA').tobytes() if im.mode == 'RGBA' else None)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--json', type=Path)
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()
    sha = git('rev-parse', a.baseline).decode().strip()
    baseline_paths = [p for p in git('ls-tree', '-r', '--name-only', sha, '--', 'pack-source/assets/quasar_gui/textures').decode().split('\n') if p]
    current_paths = sorted(str(p.relative_to(ROOT)).replace('\\', '/') for p in (ROOT / TEX).rglob('*.png'))
    expected, current = set(baseline_paths), set(current_paths)
    by_class = {}
    changed, unchanged, missing, mismatched = [], [], [], []
    for path in sorted(expected):
        cls = classify(path); by_class.setdefault(cls, {'expected': 0, 'changed': 0, 'unchanged': 0, 'missing': 0, 'mismatch': 0})
        by_class[cls]['expected'] += 1
        if path not in current:
            missing.append(path); by_class[cls]['missing'] += 1; continue
        old = git('show', f'{sha}:{path}'); new = (ROOT / path).read_bytes()
        omode, osize, opix = decode(old); nmode, nsize, npix = decode(new)
        if (omode, osize) != (nmode, nsize):
            mismatched.append({'path': path, 'baseline': [omode, list(osize)], 'current': [nmode, list(nsize)]}); by_class[cls]['mismatch'] += 1
            continue
        if old == new or opix == npix:
            unchanged.append(path); by_class[cls]['unchanged'] += 1
        else:
            changed.append(path); by_class[cls]['changed'] += 1
    unexpected = sorted(current - expected)
    contract_diff = {}
    for c in CONTRACTS:
        old = json.loads(git('show', f'{sha}:{c}').decode('utf-8-sig')); new = json.loads((ROOT / c).read_text(encoding='utf-8-sig'))
        contract_diff[c] = 'identical' if old == new else 'DIFFERENT'
    report = {
        'baselineCommit': sha, 'byClass': by_class, 'totalExpected': len(expected), 'changed': len(changed),
        'unchanged': len(unchanged), 'missing': len(missing), 'unexpectedAdded': len(unexpected),
        'dimensionOrModeMismatches': len(mismatched), 'contracts': contract_diff,
        'acceptance': (len(changed) == len(expected) and not unchanged and not missing and not unexpected and not mismatched
                       and all(v == 'identical' for v in contract_diff.values())),
        'unchangedPaths': unchanged, 'missingPaths': missing, 'unexpectedPaths': unexpected, 'mismatches': mismatched,
    }
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True); a.json.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    summary = {k: v for k, v in report.items() if k not in ('unchangedPaths', 'missingPaths', 'unexpectedPaths', 'mismatches')}
    print(json.dumps(summary, indent=2))
    if a.verbose or not report['acceptance']:
        for label, items in (('UNCHANGED', unchanged), ('MISSING', missing), ('UNEXPECTED', unexpected)):
            for p in items[:200]: print(f'{label}: {p}')
            if len(items) > 200: print(f'{label}: ... {len(items) - 200} more')
        for m in mismatched[:200]: print('MISMATCH:', m)
    sys.exit(0 if report['acceptance'] else 1)

if __name__ == '__main__':
    main()
