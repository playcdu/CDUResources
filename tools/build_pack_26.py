#!/usr/bin/env python3
"""Create the immutable 26.1.2 variant from the validated cozy pack.

The older pack stays byte-for-byte intact. Java 26 uses ITEM_MODEL instead of
the old vanilla paper model override; the artwork and font geometry are shared.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA1='54a41989a664e1cf5c127ec3369d246c1386c99b'
BASE_SHA256='f14f87424b79f3058a143d6e5285fb71f3a6b8b04e6be9f0a26f678fb6130772'
REMOVED='assets/minecraft/models/item/paper.json'
CARRIER='assets/quasar_gui/items/button_carrier.json'

def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=True)+'\n').encode()

def build(source,sidecar,output):
    raw=source.read_bytes()
    assert hashlib.sha1(raw).hexdigest()==BASE_SHA1
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA256
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert len(z.namelist())==len(set(z.namelist()))
        files={name:z.read(name) for name in z.namelist()}
    assert REMOVED in files and CARRIER not in files
    for name in files:
        p=PurePosixPath(name)
        assert not p.is_absolute() and '..' not in p.parts and '\\' not in name
    original=dict(files)
    meta=json.loads(files['pack.mcmeta'])
    files['pack.mcmeta']=encoded({'pack':{'min_format':84,'max_format':84,'description':meta['pack']['description']}})
    del files[REMOVED]
    files[CARRIER]=encoded({'model':{'type':'minecraft:empty'}})
    for name,data in original.items():
        if name not in ('pack.mcmeta',REMOVED):assert files[name]==data
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_STORED) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,data)
    result=buffer.getvalue();sha1=hashlib.sha1(result).hexdigest()
    binding=json.loads(sidecar.read_text())
    assert binding['packSha1']==BASE_SHA1 and binding['schemaVersion']==1
    binding['packSha1']=sha1
    layout=encoded(binding)
    output.mkdir(parents=True,exist_ok=True)
    (output/'quasar-gui.zip').write_bytes(result)
    name='quasar-gui-layouts-'+sha1+'.json'
    (output/name).write_bytes(layout)
    report={'minecraft':['26.1.2'],'resource_pack_format':84,'sha1':sha1,'sha256':hashlib.sha256(result).hexdigest(),'bytes':len(result),
            'base_sha1':BASE_SHA1,'base_sha256':BASE_SHA256,'artwork_and_fonts_byte_identical':True,
            'carrier_item_model':'quasar_gui:button_carrier','removed_files':[REMOVED],'added_files':[CARRIER],
            'layout':{'filename':name,'sha256':hashlib.sha256(layout).hexdigest(),'bytes':len(layout)}}
    (output/'build-report.json').write_bytes(encoded(report))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT/'deliverables/quasar-gui.zip')
    p.add_argument('--sidecar',type=Path,default=ROOT/'deliverables'/('quasar-gui-layouts-'+BASE_SHA1+'.json'))
    p.add_argument('--output',type=Path,default=ROOT/'deliverables/26.1.2')
    a=p.parse_args();print(json.dumps(build(a.source,a.sidecar,a.output),indent=2))
