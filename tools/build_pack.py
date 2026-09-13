#!/usr/bin/env python3
"""Deterministic Quasar GUI pack/artist-kit builder. Python 3.10+, Pillow 10+."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath
from PIL import Image, ImageDraw, ImageFont
import sample_art
import artist_guides

ROOT = Path(__file__).resolve().parents[1]
# Developer repository stores artist documents in a subfolder; the exported kit
# puts them at its root. Keep both build entry points fully self-contained.
ARTIST_ROOT = ROOT if (ROOT/'START-HERE.md').is_file() else ROOT/'artist-kit'
FONT = 'quasar_gui:menu'
COLORS = {'auction':(90,98,171), 'admin_shop':(46,130,145), 'chest_shop':(174,119,53),
          'economy':(68,134,103), 'trade':(82,127,162), 'ticket':(152,84,135),
          'prefixes':(133,91,164), 'guild_bank':(112,128,73), 'invsee':(153,100,77),
          'utility':(91,115,129)}
ADVANCES = {chr(0xF000+i):2**i for i in range(9)} | {chr(0xF009+i):-(2**i) for i in range(9)}

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def json_bytes(data):
    return (json.dumps(data, indent=2, ensure_ascii=True)+'\n').encode('utf-8')

def write_json(path, data):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(json_bytes(data))

def space(amount):
    if abs(amount)>511:
        raise ValueError('Spacing outside allocated binary range')
    start=0xF000 if amount>=0 else 0xF009
    return ''.join(chr(start+i) for i in reversed(range(9)) if abs(amount)&2**i)

def registry(layouts, skins):
    result={'schemaVersion':1,'font':FONT,'skins':{},'advances':ADVANCES,
            'asciiWidths':read_json(ROOT/'manifests/ascii-widths.json')['widths']}
    for key, skin in skins.items():
        g=layouts[skin['layout']]; anchor=g['titleAnchor'][0]
        result['skins'][key]={'glyph':chr(int(skin['codepoint'][2:],16)),
            'prefix':space(-anchor),'suffix':space(anchor-g['glyphAdvance']),
            'font':FONT,'centered':g['centered'],'textWidth':g['textWidth'],
            'geometry':skin['layout'],'rows':g['rows'],'menuType':g['menuType'],
            'width':g['width'],'height':g['height'],'ascent':g['ascent'],
            'advance':g['glyphAdvance'],'asset':skin['asset'],
            'liveSlots':skin.get('liveSlots',[p['index'] for p in g['slots']]),
            'staticProtectedSlots':skin.get('staticProtectedSlots',[])}
    return result

def rect(draw, box, **kw):
    x,y,w,h=box
    draw.rectangle((x,y,x+w-1,y+h-1),**kw)

def masks(layout, skin):
    dx,dy,w,h=layout['itemClearance']
    result=[]
    for slot in layout['slots'] + layout['playerSlots']:
        if slot in layout['slots'] and slot['index'] not in skin.get('liveSlots',[p['index'] for p in layout['slots'] if p['index'] not in skin['removedDecorations']]):
            continue
        result.append([slot['x']+dx,slot['y']+dy,w,h])
    result += [v['rect'] for v in layout['extraTransparent']]
    return result

def art(layout, skin, key):
    w,h=layout['width'],layout['height']
    accent=COLORS[skin['family']]
    if 'disabled' in key or key=='ticket_invalid': accent=(161,90,90)
    if 'confirm' in key or key=='ticket_valid': accent=(66,143,101)
    image=Image.new('RGBA',(w,h),(220,229,231,255)); draw=ImageDraw.Draw(image)
    draw.rounded_rectangle((0,0,w-1,h-1),radius=4,fill=(51,65,76,255))
    draw.rounded_rectangle((2,2,w-3,h-3),radius=3,fill=(211,223,226,255))
    draw.rectangle((3,3,w-4,15),fill=(237,243,243,255))
    draw.line((4,3,w-5,3),fill=accent+(255,),width=2)
    draw.line((4,h-4,w-5,h-4),fill=accent+(255,),width=2)
    invy=layout['inventoryLabel'][1]
    draw.rectangle((4,invy-1,w-5,invy+10),fill=(234,240,240,255))
    draw.line((5,invy-2,w-6,invy-2),fill=accent+(255,))
    # Replacing protected decoration uses chrome. Native icons retain open wells.
    if key.startswith('trade_') and key!='trade_money':
        left=(79,152,111) if key in ('trade_self_ready','trade_both_ready') else accent
        right=(79,152,111) if key in ('trade_other_ready','trade_both_ready') else accent
        draw.rectangle((79,16,96,126),fill=(83,105,115,255))
        draw.line((6,15,76,15),fill=left+(255,),width=2)
        draw.line((99,15,169,15),fill=right+(255,),width=2)
        draw.rectangle((6,106,169,126),fill=(195,209,215,255))
    if key.startswith('ticket_'):
        draw.rectangle((6,16,169,126),fill=(203,216,218,255))
        draw.rectangle((9,19,166,123),outline=accent+(255,),width=2)
        for x in range(13,165,12):
            draw.line((x,21,x+4,21),fill=accent+(255,))
            draw.line((x,121,x+4,121),fill=accent+(255,))
    # Borders for known singleton native item footprints.
    for role in skin.get('slotRoles',{}):
        if not role.isdecimal(): continue
        slot=next((s for s in layout['slots'] if s['index']==int(role)),None)
        if slot and slot['index'] not in skin['removedDecorations']:
            draw.rectangle((slot['x']-3,slot['y']-3,slot['x']+18,slot['y']+18),outline=accent+(255,))
    sample_art.paint(image,layout,skin,key)
    for box in masks(layout,skin): rect(draw,box,fill=(0,0,0,0))
    if key=='trade_money':
        # Original tiny static label: centered vanilla title contains only the art and
        # fixed spacing, so Unicode/default font settings cannot shift this geometry.
        letters={'O':['01110','10001','10001','10001','10001','10001','01110'],
            'F':['11111','10000','10000','11110','10000','10000','10000'],
            'E':['11111','10000','10000','11110','10000','10000','11111'],
            'R':['11110','10001','10001','11110','10100','10010','10001'],
            'D':['11110','10001','10001','10001','10001','10001','11110'],
            'M':['10001','11011','10101','10101','10001','10001','10001'],
            'N':['10001','11001','10101','10011','10001','10001','10001'],
            'Y':['10001','10001','01010','00100','00100','00100','00100']}
        for i,char in enumerate('OFFERED MONEY'):
            for y,line in enumerate(letters.get(char,[])):
                for x,bit in enumerate(line):
                    if bit=='1':draw.point((12+i*6+x,6+y),fill=(49,65,77,255))
    # Full-width alpha sentinel; never change its alpha or position.
    rect(draw,layout['advancePin'],fill=(51,65,76,255))
    return image

def png_bytes(image):
    out=io.BytesIO(); image.save(out,format='PNG',compress_level=9,optimize=False); return out.getvalue()

def guide(layout,skin,key,image):
    scale=4
    checker=Image.new('RGBA',image.size,(230,234,237,255)); d=ImageDraw.Draw(checker)
    for y in range(0,image.height,4):
        for x in range(0,image.width,4):
            if (x//4+y//4)%2: d.rectangle((x,y,x+3,y+3),fill=(205,214,220,255))
    checker.alpha_composite(image)
    out=checker.convert('RGB').resize((image.width*scale,image.height*scale),Image.Resampling.NEAREST)
    d=ImageDraw.Draw(out)
    for slot in layout['slots']+layout['playerSlots']:
        x,y=slot['x']*scale,slot['y']*scale
        blocked=slot in layout['slots'] and slot['index'] in skin['removedDecorations']
        col=(203,55,63) if blocked else (8,89,143)
        d.rectangle((x,y,x+16*scale-1,y+16*scale-1),outline=col,width=1)
        d.text((x+3,y+2),str(slot['index']),fill=col)
    x,y,tw,th=layout['textSafe'];d.rectangle((x*scale,y*scale,(x+tw)*scale-1,(y+th)*scale-1),outline=(130,58,161),width=2)
    ax,ay=layout['titleAnchor'];d.line((ax*scale-5,ay*scale,ax*scale+5,ay*scale),fill=(210,43,67),width=2)
    d.line((ax*scale,ay*scale-5,ax*scale,ay*scale+5),fill=(210,43,67),width=2)
    return out

def validate_png(raw,layout,skin,name):
    image=Image.open(io.BytesIO(raw))
    if image.mode!='RGBA': raise ValueError(f'{name}: expected RGBA PNG')
    if image.size!=(layout['width'],layout['height']): raise ValueError(f'{name}: changed dimensions')
    alpha=image.getchannel('A')
    for x,y,w,h in masks(layout,skin):
        if alpha.crop((x,y,x+w,y+h)).getbbox(): raise ValueError(f'{name}: opaque pixel in interaction/recipe mask {(x,y,w,h)}')
    x,y,w,h=layout['advancePin']
    if alpha.crop((x,y,x+w,y+h)).getextrema()!=(255,255): raise ValueError(f'{name}: advance pin alpha changed')
    actual=alpha.getbbox()[2]
    advance=int(actual*layout['scale']+0.5)+1
    if advance!=layout['glyphAdvance']: raise ValueError(f'{name}: advance changed to {advance}')

def zip_bytes(files):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED) as z:
        for name,raw in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,raw)
    return out.getvalue()

def validate_pack(raw,layouts,skins):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist()
        if len(names)!=len(set(names)): raise ValueError('Duplicate ZIP paths')
        for name in names:
            p=PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name: raise ValueError('Unsafe ZIP path')
            if name!='pack.mcmeta' and not name.startswith('assets/quasar_gui/'): raise ValueError(f'Unexpected file {name}')
        meta=json.loads(z.read('pack.mcmeta'))
        if meta['pack']['pack_format']!=15 or meta['pack']['supported_formats']!=[9,34]: raise ValueError('Unexpected tested-target metadata')
        providers=json.loads(z.read('assets/quasar_gui/font/menu.json'))['providers']
        cps=[]
        for p in providers:
            if p['type']=='space':
                if p['advances']!=ADVANCES: raise ValueError('Spacing changed')
                cps += list(p['advances'])
            elif p['type']=='bitmap':
                if len(p['chars'])!=1 or len(p['chars'][0])!=1: raise ValueError('Expected single art glyph')
                cps += p['chars']
                key=next((k for k,s in skins.items() if chr(int(s['codepoint'][2:],16))==p['chars'][0]),None)
                if key is None: raise ValueError('Unknown glyph')
                s=skins[key];g=layouts[s['layout']]
                if p['ascent']!=g['ascent'] or p['height']!=g['height']: raise ValueError('Provider metric changed')
                asset='assets/'+p['file'].replace(':','/textures/')
                if asset!=s['asset']: raise ValueError('Asset reference mismatch')
                validate_png(z.read(asset),g,s,key)
            else: raise ValueError('Unexpected font provider')
        if len(cps)!=len(set(cps)): raise ValueError('Duplicate codepoints')
        if len(cps)!=len(skins)+len(ADVANCES): raise ValueError('Missing skin provider')
    return dict(status='passed-static',skinCount=len(skins),fileCount=len(names),
                sha1=hashlib.sha1(raw).hexdigest(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
                actualClientLoading='untested',actualClientRendering='untested')

def build(overrides=None,output=None,kit=True,regenerate_samples=False):
    layouts=read_json(ROOT/'manifests/layouts.json')['layouts']; skins=read_json(ROOT/'manifests/skins.json')['skins']
    controls={s['skin_key']:s for s in read_json(ROOT/'manifests/control-map.json')['screens']}
    runtime=registry(layouts,skins);write_json(ROOT/'manifests/runtime-registry.json',runtime)
    write_json(ROOT/'manifests/codepoints.json',{'font':FONT,'privateUseOnly':True,
        'art':{key:{'codepoint':skin['codepoint'],'asset':skin['asset']} for key,skin in skins.items()},
        'space':{f'U+{ord(c):04X}':v for c,v in ADVANCES.items()}})
    write_json(ROOT/'manifests/resolved-layouts.json',{'schemaVersion':1,
        'skins':{key:{'layout':skin['layout'],'transparentMasks':masks(layouts[skin['layout']],skin),
            'opaqueProtectedDecorationSlots':skin['removedDecorations'],
            'opaqueStaticProtectedSlots':skin.get('staticProtectedSlots',[]),
            'liveSlots':skin.get('liveSlots',[]),
            'slotRoles':skin.get('slotRoles',{})} for key,skin in skins.items()}})
    providers=[{'type':'space','advances':ADVANCES}]
    files={'pack.mcmeta':json_bytes({'pack':{'pack_format':15,'supported_formats':[9,34],
        'description':'Quasar GUI starter - optional menu artwork (1.19.2 / 1.20.1 / 1.21.1; visual QA pending)'}})}
    guide_images=[]
    for key,s in skins.items():
        g=layouts[s['layout']]
        canonical=ROOT/'pack-source'/s['asset']
        if canonical.is_file() and not regenerate_samples:
            raw=canonical.read_bytes();image=Image.open(io.BytesIO(raw)).convert('RGBA')
        else:
            image=art(g,s,key);raw=png_bytes(image)
        override=Path(overrides)/s['asset'] if overrides else None
        if override and override.is_file(): raw=override.read_bytes();image=Image.open(io.BytesIO(raw)).convert('RGBA')
        validate_png(raw,g,s,key);files[s['asset']]=raw
        providers.append({'type':'bitmap','file':s['asset'].replace('assets/quasar_gui/textures/','quasar_gui:'),
            'ascent':g['ascent'],'height':g['height'],'chars':[runtime['skins'][key]['glyph']]})
        if kit:
            p=ARTIST_ROOT/'guides'/f'{key}.png';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(png_bytes(artist_guides.create_guide(g,s,key,image,controls.get(key))))
            guide_images.append((key,image))
    files['assets/quasar_gui/font/menu.json']=json_bytes({'providers':providers})
    raw=zip_bytes(files);report=validate_pack(raw,layouts,skins)
    out=Path(output) if output else ROOT/'deliverables/quasar-gui.zip';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
    out.with_suffix('.zip.sha1').write_text(report['sha1']+'\n',encoding='ascii')
    out.with_suffix('.zip.sha256').write_text(report['sha256']+'\n',encoding='ascii')
    if not overrides:
        for name,data in files.items():
            p=ROOT/'pack-source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    write_json(out.with_suffix('.validation.json'),report)
    if kit:
        explorer_command=[sys.executable,str(ROOT/'tools/build_control_explorer.py')]
        if overrides:explorer_command += ['--overrides',str(Path(overrides).resolve())]
        subprocess.run(explorer_command,check=True)
        sheet=Image.new('RGB',(4*360,math.ceil(len(guide_images)/4)*480),(27,36,44));d=ImageDraw.Draw(sheet)
        for i,(key,image) in enumerate(guide_images):
            x=i%4*360+4;y=i//4*480+26
            d.text((x,y-18),key,fill=(225,237,241))
            sample=Image.new('RGBA',image.size,(158,169,177,255));sample.alpha_composite(image)
            sheet.paste(sample.convert('RGB').resize((352,image.height*2),Image.Resampling.NEAREST),(x,y))
        (ARTIST_ROOT/'contact-sheet.png').write_bytes(png_bytes(sheet))
        examples=('auction_house','trade_self_ready','chest_shop_listing_enabled','auction_confirm','ticket_valid','chest_shop_settings')
        examples_dir=ARTIST_ROOT/'illustrations';examples_dir.mkdir(parents=True,exist_ok=True)
        composite_sheet=Image.new('RGB',(3*560,2*850+64),(239,243,240));cd=ImageDraw.Draw(composite_sheet)
        cd.text((18,15),'LAYOUT ILLUSTRATIONS - NOT GAMEPLAY | Actual artwork + original schematic native icons',font=artist_guides.TITLE,fill=(32,61,76))
        for i,key in enumerate(examples):
            s=skins[key];g=layouts[s['layout']];img=Image.open(io.BytesIO(files[s['asset']])).convert('RGBA')
            (examples_dir/f'{key}.png').write_bytes(png_bytes(artist_guides.illustration(g,s,key,img,controls.get(key))))
            x=i%3*560+16;y=i//3*850+65;cd.text((x,y),key.replace('_',' ').upper(),font=artist_guides.BODY,fill=(31,70,86))
            demo=artist_guides.composite(g,s,key,img,controls.get(key)).resize((528,g['height']*3),Image.Resampling.NEAREST)
            composite_sheet.paste(demo,(x,y+29))
            yy=y+g['height']*3+44
            caption={'auction_house':'Listings above; previous, balance, my listings, search, close, sell, watch, notification, next below.',
                'trade_self_ready':'Own offer left, other offer right. Readiness at slot 13; own money 47, other money 52.',
                'chest_shop_listing_enabled':'Read-only stats/stock, quantity controls, buy/sell toggles and listing enable switch.',
                'auction_confirm':'Hover the preview for price and seller. Slot 24 confirms; slot 53 closes.',
                'ticket_valid':'Ticket preview 22, cancel 29 and valid-only redemption 33. Static panels have no callbacks.',
                'chest_shop_settings':'Statistics 10, upgrade 12, rename 13, refresh 14 and back 8.'}[key]
            for line in artist_guides.lines(caption,510):cd.text((x,yy),line,font=artist_guides.BODY,fill=(56,79,86));yy+=18
        (examples_dir/'contact-sheet.png').write_bytes(png_bytes(composite_sheet))
        s=skins['auction_house'];g=layouts[s['layout']];img=Image.open(io.BytesIO(files[s['asset']])).convert('RGBA')
        (examples_dir/'auction-layer-diagram.png').write_bytes(png_bytes(artist_guides.layer_diagram(g,s,img,controls.get('auction_house'))))
        kitfiles={}
        for directory in ['pack-source','manifests','tools']:
            for p in sorted((ROOT/directory).rglob('*')):
                if directory=='tools' and p.name not in ('build_pack.py','check_artifacts.py','verify_artist_handoff.py','sample_art.py','artist_guides.py','test_pack.py','merge_pack.py','fetch_client_fixtures.py','CheckTargetCodecs.java','CheckReleasedMetadata.java','build_control_explorer.py','control-explorer.template.html'):continue
                if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc',): kitfiles[p.relative_to(ROOT).as_posix()]=p.read_bytes()
        for name,data in files.items():kitfiles['pack-source/'+name]=data
        for name in ('START-HERE.md','CLIENT-COMPATIBILITY.md','LICENSE.txt','README.md','requirements.txt','.python-version','CONTROL-EXPLORER.html','contact-sheet.png'):
            p=ARTIST_ROOT/name
            if p.is_file():kitfiles[name]=p.read_bytes()
        for directory in ('guides','illustrations','docs'):
            for p in sorted((ARTIST_ROOT/directory).rglob('*')):
                if p.is_file():kitfiles[p.relative_to(ARTIST_ROOT).as_posix()]=p.read_bytes()
        for name in ('evidence/target-client-codecs.txt','evidence/26.2-metadata-codec.txt',
                     'evidence/pack-tests/test-results.json','evidence/pack-tests/texture-only-exercise.json'):
            if (ROOT/name).is_file():kitfiles[name]=(ROOT/name).read_bytes()
        kitfiles['quasar-gui.zip']=raw
        kitfiles['deliverables/quasar-gui.zip']=raw
        kitfiles['deliverables/quasar-gui.zip.sha1']=(report['sha1']+'\n').encode('ascii')
        kitraw=zip_bytes(kitfiles)
        (ROOT/'deliverables/quasar-gui-artist-kit.zip').write_bytes(kitraw)
        (ROOT/'deliverables/quasar-gui-artist-kit.zip.sha256').write_text(hashlib.sha256(kitraw).hexdigest()+'\n',encoding='ascii')
    print(json.dumps(report,indent=2))
    return raw,report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--overrides',type=Path);p.add_argument('--output',type=Path);p.add_argument('--no-kit',action='store_true');p.add_argument('--validate',type=Path);p.add_argument('--regenerate-samples',action='store_true',help='Explicitly replace canonical sample PNGs with generator output; never touches overrides')
    a=p.parse_args()
    if a.validate:
        print(json.dumps(validate_pack(a.validate.read_bytes(),read_json(ROOT/'manifests/layouts.json')['layouts'],read_json(ROOT/'manifests/skins.json')['skins']),indent=2))
    else:build(a.overrides,a.output,not a.no_kit,a.regenerate_samples)

if __name__=='__main__':main()
