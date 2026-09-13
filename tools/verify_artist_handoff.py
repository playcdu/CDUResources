"""Extract the shipped artist kit in isolation and rebuild/test it without repo deps."""
import hashlib
import base64
import json
import re
import subprocess
import sys
import tempfile
import zipfile
import io
from pathlib import Path
from PIL import Image
import button_assets
import decorative_assets

ROOT=Path(__file__).resolve().parents[1]
parent=ROOT/'evidence/artist-kit-roundtrip'
parent.mkdir(parents=True,exist_ok=True)
out=Path(tempfile.mkdtemp(prefix='verify-',dir=parent))
with zipfile.ZipFile(ROOT/'deliverables/quasar-gui-artist-kit.zip') as z:
    # Our validated generated artifact only; refuse unsafe paths before extraction.
    for name in z.namelist():
        target=(out/name).resolve()
        if not target.is_relative_to(out.resolve()):raise ValueError(name)
    z.extractall(out)
build=subprocess.run([sys.executable,'tools/build_pack.py'],cwd=out,capture_output=True,text=True)
assert build.returncode==0,build.stdout+build.stderr
tests=subprocess.run([sys.executable,'tools/test_pack.py'],cwd=out,capture_output=True,text=True)
assert tests.returncode==0,tests.stdout+tests.stderr
artist_tests=subprocess.run([sys.executable,'tools/test_artist.py'],cwd=out,capture_output=True,text=True)
assert artist_tests.returncode==0,artist_tests.stdout+artist_tests.stderr
original=(ROOT/'deliverables/quasar-gui.zip').read_bytes()
rebuilt=(out/'deliverables/quasar-gui.zip').read_bytes()
with zipfile.ZipFile(out/'deliverables/quasar-gui-artist-kit.zip') as kit:
    required={'START-HERE.md','LICENSE.txt','CLIENT-COMPATIBILITY.md','CONTROL-EXPLORER.html',
              'README.md','requirements.txt','.python-version','docs/ARTIST-OVERRIDES.md',
              'manifests/button-layouts.json','tools/check_artifacts.py','tools/verify_artist_handoff.py',
              'illustrations/contact-sheet.png','tools/sample_art.py','tools/artist_guides.py',
              'tools/build_control_explorer.py','tools/control-explorer.template.html',
              'LAYOUT-EDITOR.html','Setup Artist Tools.cmd','Build Pack.cmd','Open Layout Helper.cmd',
              'tools/artist.py','tools/artist-tools.cmd','tools/build_artist_editor.py','tools/layout_model.js',
              'tools/layout-editor-ui.js','tools/layout-editor.template.html','tools/test_artist.py','tools/test_layout_model.cjs',
              'manifests/artist-projects.json','manifests/artist-exports.json','artwork/README.md','docs/ARTIST-WORKFLOW.md'}
    assert required <= set(kit.namelist()), 'Standalone kit rebuild must preserve its guides, documentation and tools'
canonical=out/'pack-source/assets/quasar_gui/textures/menu/auction_house.png'
before=canonical.read_bytes()
override=out/'evidence/pack-tests/overrides'
changed=(override/'assets/quasar_gui/textures/menu/auction_house.png').read_bytes()
override_build=subprocess.run([sys.executable,'tools/build_pack.py','--overrides',str(override),
    '--output',str(out/'deliverables/artist-override.zip')],cwd=out,capture_output=True,text=True)
assert override_build.returncode == 0, override_build.stdout+override_build.stderr
assert canonical.read_bytes() == before, 'Override build changed canonical artist source'
guide=(out/'CONTROL-EXPLORER.html').read_text(encoding='utf-8')
data=json.loads(re.search(r'const SCREENS=(.*?);\nconst root=',guide,re.S).group(1))
runtime=json.loads((out/'manifests/runtime-registry.json').read_text())['skins']['auction_house']
layout=data['auction_house']['layout']
def read_asset(asset):
    candidate=override/asset
    return (candidate if candidate.is_file() else out/'pack-source'/asset).read_bytes()
expected=button_assets.compose(Image.open(io.BytesIO(changed)).convert('RGBA'),runtime.get('buttonRegions',[]),read_asset)
expected,_=decorative_assets.compose(expected,layout,runtime.get('artLayers',[]),read_asset)
actual=Image.open(io.BytesIO(base64.b64decode(data['auction_house']['image'].split(',',1)[1]))).convert('RGBA')
assert actual.size==expected.size and actual.tobytes()==expected.tobytes(), 'Guide must composite the edited PNG and every button/decorative layer'
editor=(out/'LAYOUT-EDITOR.html').read_text(encoding='utf-8')
editor_data=json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',editor,re.S).group(1))
assert base64.b64decode(editor_data['assets']['assets/quasar_gui/textures/menu/auction_house.png']['data'].split(',',1)[1])==changed,'Optional alignment helper must embed edited artwork'
with zipfile.ZipFile(out/'deliverables/quasar-gui-artist-kit.zip') as kit:
    assert required <= set(kit.namelist())
    assert kit.read('CONTROL-EXPLORER.html') == (out/'CONTROL-EXPLORER.html').read_bytes()
    assert kit.read('LAYOUT-EDITOR.html') == (out/'LAYOUT-EDITOR.html').read_bytes()
    assert kit.read('pack-source/assets/quasar_gui/textures/menu/auction_house.png') == changed
result=dict(standaloneArtistKitBuild=build.returncode,standaloneArtistKitTests=tests.returncode,
    byteIdenticalPack=original==rebuilt,sha1=hashlib.sha1(rebuilt).hexdigest(),
    freshExtraction=out.relative_to(ROOT).as_posix(),normalBuildPreservesDocumentation=True,
    overrideGuideAndReexportUseEditedArtwork=True,canonicalArtworkPreserved=True,
    buildOutput=build.stdout+build.stderr,testOutput=tests.stdout+tests.stderr)
(ROOT/'evidence/artist-kit-roundtrip.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if not k.endswith('Output')},indent=2))
if build.returncode or tests.returncode or original!=rebuilt:raise SystemExit(1)
