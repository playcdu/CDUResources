"""Optional public audit fixtures. Downloads official Mojang files; no game launch."""
import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'

def get(url):
    with urllib.request.urlopen(url,timeout=60) as r:return r.read()

def fetch(download,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_file() and hashlib.sha1(path.read_bytes()).hexdigest()==download['sha1']:return
    data=get(download['url'])
    if hashlib.sha1(data).hexdigest()!=download['sha1']:raise ValueError('Official SHA-1 mismatch: '+download['url'])
    path.write_bytes(data)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('versions',nargs='*',default=['1.19.2','1.20.1','1.21.1','26.2'])
    args=p.parse_args();index=json.loads(get(BASE))
    for v in args.versions:
        if v not in ('1.19.2','1.20.1','1.21.1','26.2'):raise ValueError('Version outside audited matrix: '+v)
        metadata=json.loads(get(next(e['url'] for e in index['versions'] if e['id']==v)))
        folder=ROOT/'evidence/client-code';folder.mkdir(parents=True,exist_ok=True)
        (folder/(v+'.json')).write_text(json.dumps(metadata,indent=2)+'\n')
        fetch(metadata['downloads']['client'],folder/(v+'-client.jar'))
        if 'client_mappings' in metadata['downloads']:fetch(metadata['downloads']['client_mappings'],folder/(v+'-mappings.txt'))
        prefixes=('com.google.code.gson:','com.google.guava:','com.mojang:datafixerupper:',
            'com.mojang:logging:','it.unimi.dsi:fastutil:','org.slf4j:','org.apache.logging.log4j:',
            'org.apache.commons:commons-lang3:','commons-io:','org.joml:',
            'com.mojang:authlib:','io.netty:','com.mojang:brigadier:')
        for lib in metadata['libraries']:
            if lib['name'].startswith(prefixes) and 'artifact' in lib.get('downloads',{}):
                a=lib['downloads']['artifact'];fetch(a,folder/(v+'-libs')/Path(a['path']).name)
        print(v+': official client, mappings and codec dependencies SHA-1 verified')

if __name__=='__main__':main()
