"""Illustrate real generated overlay layers; no gameplay capture or copied item artwork."""
import json
import math
import argparse
import io
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from button_assets import text
from decorative_assets import compose

ROOT=Path(__file__).resolve().parents[1]
ARTIST_ROOT=ROOT if (ROOT/'START-HERE.md').is_file() else ROOT/'artist-kit'
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--overrides',type=Path);args=parser.parse_args()
def read_asset(asset):
    override=args.overrides/asset if args.overrides else None
    return (override if override and override.is_file() else ROOT/'pack-source'/asset).read_bytes()
def open_asset(asset):return Image.open(io.BytesIO(read_asset(asset))).convert('RGBA')
registry=json.loads((ROOT/'manifests/runtime-registry.json').read_text())
layouts=json.loads((ROOT/'manifests/layouts.json').read_text())['layouts']
screens=json.loads((ROOT/'manifests/button-layouts.json').read_text())['screens']
out=ARTIST_ROOT/'illustrations/redesign';out.mkdir(parents=True,exist_ok=True)
titlefont=ImageFont.load_default(size=22);bodyfont=ImageFont.load_default(size=14)
sheet=Image.new('RGB',(1680,math.ceil(len(screens)/3)*790+58),(230,237,237));sd=ImageDraw.Draw(sheet)
sd.text((20,16),'REDESIGNED CONTROLS | Layout illustration - not gameplay',font=titlefont,fill=(26,50,67))
for n,(key,screen) in enumerate(screens.items()):
    skin=registry['skins'][key];g=layouts[skin['geometry']]
    sample=Image.new('RGBA',(g['width'],g['height']),(155,166,170,255));d=ImageDraw.Draw(sample)
    for p in g['slots']+g['playerSlots']:
        d.rectangle((p['x']-1,p['y']-1,p['x']+16,p['y']+16),fill=(91,103,109,255))
        d.line((p['x']-1,p['y']+16,p['x']+16,p['y']+16,p['x']+16,p['y']-1),fill=(214,222,223,255))
    for i in screen['contentSlots']:
        p=next(p for p in g['slots'] if p['index']==i)
        if key.startswith('trade_') and i not in [0,1,5,14]:continue
        x,y=p['x'],p['y'];d.polygon([(x+8,y+2),(x+13,y+7),(x+9,y+14),(x+3,y+11),(x+2,y+5)],fill=(115,205,216,255))
    sample.alpha_composite(open_asset(skin['asset']))
    for r in skin['buttonRegions']:
        frame=r['states'][r['defaultState']]
        sample.alpha_composite(open_asset(frame['asset']),(r['x'],r['y']))
    d=ImageDraw.Draw(sample)
    if not skin['centered']:text(d,g['titleAnchor'][0],6,key.replace('_',' ').upper()[:25],(235,244,239,255))
    text(d,8,g['inventoryLabel'][1]+1,'INVENTORY',(52,66,72,255))
    sample,view=compose(sample,g,skin.get('artLayers',[]),read_asset)
    left_width=sample.width*4;right=left_width+38
    panel=Image.new('RGB',(left_width+446,max(4*sample.height+102,130+len(screen['buttons'])*80)),(230,237,237));pd=ImageDraw.Draw(panel)
    pd.text((18,14),key.replace('_',' ').upper(),font=titlefont,fill=(26,50,67))
    pd.text((18,44),'LAYOUT ILLUSTRATION - NOT GAMEPLAY. Schematic native items; actual bitmap button layers.',font=bodyfont,fill=(64,83,93))
    panel.paste(sample.convert('RGB').resize((left_width,sample.height*4),Image.Resampling.NEAREST),(18,75))
    yy=80
    for b in screen['buttons']:
        pd.text((right,yy),b['label']+' / '+b['role'],font=bodyfont,fill=(29,73,88));yy+=20
        pd.text((right,yy),'Source action slot: '+str(b['sourceSlot']),font=bodyfont,fill=(58,76,88));yy+=20
        pd.text((right,yy),'Painted cells: '+', '.join(map(str,b['slots'])),font=bodyfont,fill=(58,76,88));yy+=38
    panel.save(out/(key+'.png'))
    sx=n%3*560+16;sy=n//3*790+62
    sd.text((sx,sy),key.replace('_',' ').upper(),font=bodyfont,fill=(26,50,67))
    scale=2 if sample.width>176 else 3
    sheet.paste(sample.convert('RGB').resize((sample.width*scale,sample.height*scale),Image.Resampling.NEAREST),(sx,sy+25))
sheet.save(out/'contact-sheet.png')
region=registry['skins']['economy_hub']['buttonRegions'][0]
strip=Image.new('RGB',(1392,222),(230,237,237));draw=ImageDraw.Draw(strip)
draw.text((16,10),'ONE BUTTON / SIX EDITABLE STATE FRAMES (separate bitmap glyphs)',font=titlefont,fill=(26,50,67))
for i,(state,frame) in enumerate(region['states'].items()):
    draw.text((i*232+10,45),state,font=bodyfont,fill=(26,50,67))
    im=open_asset(frame['asset']).resize((216,144),Image.Resampling.NEAREST)
    strip.paste(im,(i*232+8,65),im)
strip.save(out/'button-state-frames.png')
print('Rendered redesigned layer illustrations for',len(screens),'screens')
