#!/usr/bin/env python3
"""Merge operator pack + Quasar into ONE ZIP; refuse conflicts, never mutate inputs."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path, PurePosixPath
from build_pack import ROOT, json_bytes, read_json, validate_pack, zip_bytes

def entries(path):
    result={}
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            name=info.filename
            if info.is_dir():continue
            p=PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
                raise ValueError(f'Unsafe ZIP path: {name}')
            if name in result:raise ValueError(f'Duplicate ZIP path: {name}')
            if info.file_size>64*1024*1024:raise ValueError(f'Unreasonably large entry: {name}')
            if sum(map(len,result.values()))+info.file_size>512*1024*1024:raise ValueError('Pack exceeds merge size budget')
            result[name]=z.read(info)
    if 'pack.mcmeta' not in result:raise ValueError('Missing root pack.mcmeta')
    return result

def merge(operator,gui,out,metadata=None):
    if Path(out).resolve() in (Path(operator).resolve(),Path(gui).resolve()):raise ValueError('Output must differ from both inputs')
    if Path(out).exists():raise ValueError('Output already exists; choose a revision filename')
    op=entries(operator);q=entries(gui)
    validate_pack(Path(gui).read_bytes(),read_json(ROOT/'manifests/layouts.json')['layouts'],read_json(ROOT/'manifests/skins.json')['skins'])
    conflicts=[]
    for name,data in q.items():
        if name!='pack.mcmeta' and name in op and op[name]!=data:conflicts.append(name)
    # An operator overlay or filter can override/block our namespace without a root collision.
    original_meta=json.loads(op['pack.mcmeta'])
    for name in op:
        if '/assets/quasar_gui/' in '/'+name and name not in q:conflicts.append(name+' (namespace/overlay collision)')
        if name.endswith('/assets/minecraft/models/item/paper.json'):conflicts.append(name+' (paper carrier overlay collision)')
    if original_meta.get('filter'):conflicts.append('pack.mcmeta filter requires explicit review/removal in operator source')
    if conflicts:raise ValueError('Merge conflicts: '+', '.join(conflicts))
    selected=read_json(metadata) if metadata else original_meta
    if not isinstance(selected.get('pack'),dict):raise ValueError('Invalid merged pack metadata')
    # Metadata policy stays operator-owned. Use --metadata only after validating their assets.
    op.update({n:b for n,b in q.items() if n!='pack.mcmeta'})
    op['pack.mcmeta']=json_bytes(selected)
    raw=zip_bytes(op);Path(out).parent.mkdir(parents=True,exist_ok=True);Path(out).write_bytes(raw)
    digest=hashlib.sha1(raw).hexdigest();Path(str(out)+'.sha1').write_text(digest+'\n',encoding='ascii')
    return dict(output=str(out),sha1=digest,bytes=len(raw),pathConflicts='none',
        metadata='explicit override' if metadata else 'operator preserved',
        warning='Merged metadata/assets still require actual client loading on each target. Configure merged ZIP hash and one offer owner.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operator',type=Path);p.add_argument('gui',type=Path);p.add_argument('output',type=Path);p.add_argument('--metadata',type=Path)
    a=p.parse_args();print(json.dumps(merge(a.operator,a.gui,a.output,a.metadata),indent=2))
