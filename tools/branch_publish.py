"""Trusted branch inventory, deterministic pack packaging, and OIDC publication.

Run this file from main. Branch code runs only in the credential-free build job;
the publisher runs on a fresh runner and never executes downloaded artifacts.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

API = 'https://api.playcdu.co/resource-packs'
REPO = 'playcdu/CDUResources'
SHA = re.compile(r'^[a-f0-9]{40}$')
PIPELINE = 1


def request(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'CDU-resource-branches', **(headers or {})})
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.load(response)


def github_branches():
    headers = {'Accept': 'application/vnd.github+json'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    rows = []
    for page in range(1, 7):
        part = request(f'https://api.github.com/repos/{REPO}/branches?per_page=100&page={page}', headers=headers)
        rows.extend({'name': r['name'], 'head': r['commit']['sha']} for r in part)
        if len(part) < 100:
            break
    if len(rows) > 500:
        raise ValueError('More than 500 branches: increase the explicitly bounded publisher capacity')
    return sorted(rows, key=lambda r: r['name'])


def catalog():
    return request(API + '/branches')


def encoded(data):
    return (json.dumps(data, indent=2, ensure_ascii=True) + '\n').encode()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(data))


def plan(output):
    previous = {r['name']: r for r in catalog()['branches']}
    rows = github_branches()
    matrix = []
    for row in rows:
        row['id'] = hashlib.sha256(row['name'].encode()).hexdigest()[:24]
        old = previous.get(row['name'])
        row['needs_build'] = not (old and old['status'] == 'published' and old['head'] == row['head'])
        if row['needs_build']:
            matrix.append(row)
    write_json(output, {'pipeline': PIPELINE, 'branches': rows})
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
            stream.write('matrix=' + json.dumps({'include': matrix}, separators=(',', ':')) + '\n')
            stream.write('changed=' + ('true' if matrix else 'false') + '\n')
    print(json.dumps({'branches': len(rows), 'builds_needed': len(matrix)}))


def validate_zip(raw, variant):
    if not 100 <= len(raw) <= 20 * 1024 * 1024:
        raise ValueError('Pack size outside publication bounds')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        if len(entries) > 10000 or len({i.filename for i in entries}) != len(entries):
            raise ValueError('Duplicate or excessive ZIP entries')
        if sum(i.file_size for i in entries) > 64 * 1024 * 1024:
            raise ValueError('Uncompressed pack exceeds 64 MiB')
        files = {}
        for info in entries:
            path = PurePosixPath(info.filename)
            if info.orig_filename != info.filename or path.is_absolute() or '..' in path.parts or '\\' in info.orig_filename or info.is_dir() or (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Unsafe ZIP path')
            if info.filename != 'pack.mcmeta' and not (info.filename.startswith('assets/') and path.suffix in ('.png', '.json', '.ogg')):
                raise ValueError('Unexpected resource-pack file')
            files[info.filename] = archive.read(info)
    meta = json.loads(files['pack.mcmeta'])['pack']
    if variant == 'legacy':
        if meta.get('pack_format') != 15 or meta.get('supported_formats') != [9, 34]:
            raise ValueError('Unvalidated legacy pack format')
        if 'assets/minecraft/models/item/paper.json' not in files:
            raise ValueError('Legacy carrier missing')
    elif variant == '26.1.2':
        if meta.get('min_format') != 84 or meta.get('max_format') != 84:
            raise ValueError('Unvalidated Minecraft 26 format')
        if 'assets/minecraft/models/item/paper.json' in files or json.loads(files['assets/quasar_gui/items/button_carrier.json']) != {'model': {'type': 'minecraft:empty'}}:
            raise ValueError('Minecraft 26 carrier mismatch')
    else:
        raise ValueError('Unsupported variant; 1.12 is excluded')
    return files


def validate_pair(raw, sidecar, variant):
    files = validate_zip(raw, variant)
    if len(sidecar) > 2 * 1024 * 1024:
        raise ValueError('Layout exceeds publication limit')
    layout = json.loads(sidecar)
    sha = hashlib.sha1(raw).hexdigest()
    if layout.get('schemaVersion') != 1 or layout.get('packSha1') != sha or not isinstance(layout.get('skins'), dict):
        raise ValueError('Layout SHA binding invalid')
    return files, layout


def variant_26(raw, sidecar):
    files, layout = validate_pair(raw, sidecar, 'legacy')
    description = json.loads(files['pack.mcmeta'])['pack']['description']
    files['pack.mcmeta'] = encoded({'pack': {'min_format': 84, 'max_format': 84, 'description': description}})
    del files['assets/minecraft/models/item/paper.json']
    files['assets/quasar_gui/items/button_carrier.json'] = encoded({'model': {'type': 'minecraft:empty'}})
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    result = output.getvalue()
    layout['packSha1'] = hashlib.sha1(result).hexdigest()
    validate_pair(result, encoded(layout), '26.1.2')
    return result, encoded(layout)


def build(source, output, branch, commit):
    if not SHA.fullmatch(commit):
        raise ValueError('Build must use an exact commit')
    actual = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != commit:
        raise ValueError('Source checkout does not match planned commit')
    def run(name):
        subprocess.run([sys.executable, str(source / 'tools' / name)], cwd=source, check=True, timeout=600)
    run('build_pack.py')
    run('test_pack.py')
    first = (source / 'deliverables/quasar-gui.zip').read_bytes()
    run('build_pack.py')
    raw = (source / 'deliverables/quasar-gui.zip').read_bytes()
    if first != raw:
        raise ValueError('Repeated resource-pack build differs')
    sha = hashlib.sha1(raw).hexdigest()
    sidecar = (source / f'deliverables/quasar-gui-layouts-{sha}.json').read_bytes()
    validate_pair(raw, sidecar, 'legacy')
    modern, modern_layout = variant_26(raw, sidecar)
    output.mkdir(parents=True, exist_ok=True)
    for variant, pack, layout in [('legacy', raw, sidecar), ('26.1.2', modern, modern_layout)]:
        directory = output / variant
        directory.mkdir(exist_ok=True)
        (directory / 'pack.zip').write_bytes(pack)
        (directory / 'layout.json').write_bytes(layout)
    write_json(output / 'build.json', {'branch': branch, 'commit': commit, 'pipeline': PIPELINE})
    print(json.dumps({'branch': branch, 'commit': commit, 'legacy_sha1': sha, 'modern_sha1': hashlib.sha1(modern).hexdigest()}))


def oidc_token():
    url = os.environ['ACTIONS_ID_TOKEN_REQUEST_URL'] + '&audience=' + urllib.parse.quote(API, safe='')
    return request(url, headers={'Authorization': 'Bearer ' + os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']})['value']


def publish_pair(directory, variant, token):
    raw, layout = (directory / 'pack.zip').read_bytes(), (directory / 'layout.json').read_bytes()
    validate_pair(raw, layout, variant)  # Trusted publisher validates data; it never imports branch code.
    metadata = {'variant': variant, 'sha1': hashlib.sha1(raw).hexdigest(), 'sha256': hashlib.sha256(raw).hexdigest()}
    boundary = 'CDUPack' + uuid.uuid4().hex
    parts = []
    for name, content, content_type, filename in [('metadata', encoded(metadata), 'application/json', None),
            ('pack', raw, 'application/zip', 'pack.zip'), ('layout', layout, 'application/json', 'layout.json')]:
        disposition = f'Content-Disposition: form-data; name="{name}"' + (f'; filename="{filename}"' if filename else '')
        parts.append(f'--{boundary}\r\n{disposition}\r\nContent-Type: {content_type}\r\n\r\n'.encode() + content + b'\r\n')
    body = b''.join(parts) + f'--{boundary}--\r\n'.encode()
    return request(API + '/publish', body, {'Authorization': 'Bearer ' + token, 'Content-Type': 'multipart/form-data; boundary=' + boundary})


def publish(plan_path, artifacts):
    planned = {r['name']: r for r in json.loads(plan_path.read_text())['branches']}
    previous = {r['name']: r for r in catalog()['branches']}
    token = oidc_token()
    rows, failures = [], []
    for branch in github_branches():  # Recheck current heads; never label a superseded commit as current.
        name, head = branch['name'], branch['head']
        old = previous.get(name, {})
        row = {**branch, 'status': 'pending', 'published_commit': old.get('published_commit'),
            'attempted_commit': None, 'releases': [r['sha1'] for r in old.get('releases', [])]}
        plan_row = planned.get(name)
        if plan_row and plan_row['head'] == head and not plan_row['needs_build']:
            row.update(status='published', attempted_commit=head)
        elif plan_row and plan_row['head'] == head:
            row['attempted_commit'] = head
            directory = artifacts / ('branch-' + plan_row['id'])
            try:
                meta = json.loads((directory / 'build.json').read_text())
                if meta != {'branch': name, 'commit': head, 'pipeline': PIPELINE}:
                    raise ValueError('Artifact provenance does not match planned checkout')
                releases = [publish_pair(directory / variant, variant, token) for variant in ('legacy', '26.1.2')]
                row.update(status='published', published_commit=head, releases=[r['sha1'] for r in releases])
            except Exception as error:
                # Do not expose OIDC credentials or raw upstream responses in logs/catalog.
                row['status'] = 'failed'
                failures.append(name)
                detail = type(error).__name__
                if isinstance(error, urllib.error.HTTPError):
                    try: detail += ': ' + str(json.loads(error.read(4096)).get('error', error.code))
                    except (ValueError, AttributeError): pass
                print(f'Publication failed for {name}: {detail}', file=sys.stderr)
        rows.append(row)
    result = request(API + '/catalog', encoded({'branches': rows}), {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    print(json.dumps({'catalog': API + '/branches', 'branches': len(result['branches']), 'failed': failures}))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as stream:
            stream.write(f'Branch packs: {API}/branches\n\n')
            for row in result['branches']:
                stream.write(f"- `{row['name']}`: {row['status']} (`{row['head'][:12]}`)\n")
                for release in row['releases']:
                    stream.write(f"  - {release['variant']}: {release['url']} — SHA-1 `{release['sha1']}`\n")
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    plan_args = sub.add_parser('plan'); plan_args.add_argument('--output', type=Path, required=True)
    build_args = sub.add_parser('build')
    for name in ('source', 'output'): build_args.add_argument('--' + name, type=Path, required=True)
    for name in ('branch', 'commit'): build_args.add_argument('--' + name, required=True)
    publish_args = sub.add_parser('publish'); publish_args.add_argument('--plan', type=Path, required=True); publish_args.add_argument('--artifacts', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'plan': plan(args.output)
    elif args.command == 'build': build(args.source.resolve(), args.output.resolve(), args.branch, args.commit)
    else: publish(args.plan, args.artifacts)
