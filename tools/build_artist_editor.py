"""Generate the optional offline alignment helper; Aseprite remains the artwork editor."""
import argparse
import base64
import io
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATES = ('normal','disabled','selected','pulse_1','pulse_2','pulse_3')

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def build(root=ROOT, output=None, overrides=None):
    root = Path(root).resolve()
    data = {'config':read(root/'manifests/button-layouts.json'),
            'layouts':read(root/'manifests/layouts.json')['layouts'],
            'skins':read(root/'manifests/skins.json')['skins'],
            'runtime':read(root/'manifests/runtime-registry.json')['skins'],
            'controls':{s['skin_key']:s for s in read(root/'manifests/control-map.json')['screens']}, 'assets':{}}
    names = {s['asset'] for s in data['skins'].values()}
    for key, screen in data['config']['screens'].items():
        for button in screen['buttons']:
            names.update(f"assets/quasar_gui/textures/buttons/{key}/{button['id']}/{state}.png" for state in STATES)
        names.update(f"assets/quasar_gui/textures/frames/{key}/{layer['id']}.png" for layer in screen.get('artLayers',[]))
    for name in sorted(names):
        candidate = Path(overrides)/name if overrides else None
        path = candidate if candidate and candidate.is_file() else root/'pack-source'/name
        raw = path.read_bytes()
        with Image.open(io.BytesIO(raw)) as png:
            if png.format != 'PNG': raise ValueError('Helper artwork must be PNG: '+name)
            width,height=png.size
        data['assets'][name] = {'width':width,'height':height,'data':'data:image/png;base64,'+base64.b64encode(raw).decode()}
    template = (root/'tools/layout-editor.template.html').read_text(encoding='utf-8-sig')
    replacements = {'/*__DATA__*/':json.dumps(data,separators=(',',':'),ensure_ascii=True).replace('<','\\u003c'),
                    '/*__MODEL__*/':(root/'tools/layout_model.js').read_text(encoding='utf-8-sig'),
                    '/*__UI__*/':(root/'tools/layout-editor-ui.js').read_text(encoding='utf-8-sig')}
    for marker,value in replacements.items():
        if template.count(marker)!=1: raise ValueError('Missing/duplicate helper template marker: '+marker)
        template=template.replace(marker,value)
    destination=Path(output) if output else (root if (root/'START-HERE.md').is_file() else root/'artist-kit')/'LAYOUT-EDITOR.html'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(template,encoding='utf-8',newline='\n')
    print(f'Built optional offline layout helper: {len(data["skins"])} skins, {len(data["config"]["screens"])} bound layouts, {destination.stat().st_size} bytes')
    return destination

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--overrides',type=Path)
    args=parser.parse_args()
    build(args.root,args.output,args.overrides)
