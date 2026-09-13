"""Build a self-contained, offline artist guide from the actual menu/geometry/PNG sources."""
from pathlib import Path
import argparse
import base64
import json
import io
from PIL import Image
import button_assets
import decorative_assets

ROOT = Path(__file__).resolve().parents[1]
ARTIST_ROOT = ROOT if (ROOT / "START-HERE.md").is_file() else ROOT / "artist-kit"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--overrides", type=Path, help="Use the same optional texture replacements as the pack builder")
args = parser.parse_args()
runtime=json.loads((ROOT/'manifests/runtime-registry.json').read_text())
button_path=ROOT/'manifests/button-layouts.json'
button_screens=json.loads(button_path.read_text())['screens'] if button_path.exists() else {}
layouts = json.loads((ROOT / "manifests/layouts.json").read_text())["layouts"]
skins = json.loads((ROOT / "manifests/skins.json").read_text())["skins"]
coverage = {row["skin_key"]: row for row in json.loads((ROOT / "manifests/menu-coverage.json").read_text(encoding="utf-8"))["screens"]}
control_path = ROOT / "manifests/control-map.json"
controls = {row["skin_key"]: row for row in json.loads(control_path.read_text(encoding="utf-8"))["screens"]} if control_path.exists() else {}
screens = {}
def read_asset(name):
    candidate=args.overrides/name if args.overrides else None
    return (candidate if candidate and candidate.is_file() else ROOT/'pack-source'/name).read_bytes()
for key, skin in skins.items():
    row = coverage.get(key, {})
    asset = ROOT / "pack-source" / skin["asset"]
    override = args.overrides / skin["asset"] if args.overrides else None
    if override and override.is_file():
        asset = override
    regions=runtime['skins'][key].get('buttonRegions',[])
    image_bytes=asset.read_bytes()
    if regions:
        image_bytes=button_assets.png(button_assets.compose(Image.open(io.BytesIO(image_bytes)),regions,read_asset))
    layers=runtime['skins'][key].get('artLayers',[])
    expanded,view=decorative_assets.compose(Image.open(io.BytesIO(image_bytes)).convert('RGBA'),layouts[skin['layout']],layers,read_asset)
    image_bytes=button_assets.png(expanded)
    screen_controls=button_assets.mapped_controls(button_screens[key],controls.get(key)) if key in button_screens else controls.get(key,{})
    screens[key] = {"layout": layouts[skin["layout"]], "roles": skin.get("slotRoles", {}),
        "states": row.get("states", []), "source": row.get("source", "Generic geometry template"),
        "entry": row.get("entry_point", "template"), "asset": skin["asset"],
        "dynamic": row.get("dynamic_content", "Native slot content"),
        "removed": skin.get("removedDecorations", []), "controls": screen_controls.get("controls", []),
        "visibleContentSlots":skin.get('visibleContentSlots',skin.get('liveSlots',[])),
        "paintedControlSlots":skin.get('paintedControlSlots',[]),"buttonRegions":regions,"artLayers":layers,"viewBounds":view,
        "liveSlots": skin.get("liveSlots", [p["index"] for p in layouts[skin["layout"]]["slots"]]),
        "staticProtectedSlots": skin.get("staticProtectedSlots", []),
        "image": "data:image/png;base64," + base64.b64encode(image_bytes).decode()}
payload = json.dumps(screens, separators=(",", ":"), ensure_ascii=True).replace("</", "<\\/")
template = (ROOT / "tools/control-explorer.template.html").read_text(encoding="utf-8")
out = ARTIST_ROOT / "CONTROL-EXPLORER.html"
out.write_text(template.replace("/*__MENU_DATA__*/", payload), encoding="utf-8", newline="\n")
print(f"Built offline control explorer: {len(screens)} screens, {out.stat().st_size} bytes")
