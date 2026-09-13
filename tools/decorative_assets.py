"""Original noninteractive outer artwork, with explicit bounded font-layer metrics."""
from pathlib import Path
import json
import io
from PIL import Image,ImageDraw
from button_assets import encode,png,spacing
from sample_art import label

FONT='quasar_gui:menu'
FIRST_CODEPOINT=0xE200

def draw(layer,layout):
    w,h=layer['width'],layer['height'];x,y=layer['x'],layer['y']
    image=Image.new('RGBA',(w,h),(14,25,37,255));d=ImageDraw.Draw(image)
    d.rectangle((1,1,w-2,h-2),outline=(72,124,139,255));d.rectangle((3,3,w-4,h-4),outline=(31,62,79,255))
    # Broad framing remains separate from the native container and all click targets.
    for yy in range(17,h-16,8):
        d.line((5,yy,6,yy+2),fill=(57,90,111,255));d.line((w-7,yy+2,w-6,yy),fill=(57,90,111,255))
    heading=layer.get('heading','QUASAR MARKET')
    label(d,(w-len(heading)*4+1)//2,2,heading,(138,210,211,255))
    label(d,83,h-6,'HOVER ITEMS FOR DETAILS',(145,174,190,255))
    left_heading=layer.get('leftHeading','MARKET')[:8]
    label(d,20-(len(left_heading)*4-1)//2,16,left_heading,(208,224,231,255))
    label(d,223,16,'ITEM',(208,224,231,255));label(d,219,23,'INFO',(208,224,231,255))
    # Original diamond-market emblem. Its side panel is deliberately not button shaped.
    d.polygon([(20,36),(31,49),(20,64),(9,49)],outline=(89,213,199,255),fill=(25,75,83,255))
    d.line((12,49,28,49,20,60,12,49,20,39,28,49),fill=(171,235,221,255))
    for yy,line in [(h//2-20,'HOVER'),(h//2-10,'ITEMS'),(h//2,'FOR'),(h//2+10,'DETAILS')]:
        label(d,20-(len(line)*4-1)//2,yy,line,(151,186,202,255))
    right_lines=layer.get('rightLines',[])
    for yy,line in list(zip([54,67,80],right_lines)):
        label(d,236-(len(line)*4-1)//2,yy,line,(151,186,202,255))
    if not right_lines:
        # Decorative market marks only; action labels belong to actual buttons.
        d.line((235,47,235,100),fill=(52,91,109,255))
        for yy in (52,73,94):
            d.polygon([(235,yy-4),(239,yy),(235,yy+4),(231,yy)],fill=(84,153,161,255))
    # The complete native container rectangle is clear. This overlay cannot hide
    # its item slots, button layers, title, inventory label, or player inventory.
    d.rectangle((-x,-y,-x+layout['width']-1,-y+layout['height']-1),fill=(0,0,0,0))
    d.point((w-1,h//2),fill=(14,25,37,255))
    return image

def records(root,config,layouts,skins,allocate=False):
    path=root/'manifests/art-codepoints.json'
    data=json.loads(path.read_text()) if path.exists() else {'schemaVersion':1,'layers':{}}
    nxt=max((int(cp[2:],16) for cp in data['layers'].values()),default=FIRST_CODEPOINT-1)+1
    found=[]
    for key,screen in config['screens'].items():
        g=layouts[skins[key]['layout']];anchor=g['titleAnchor'][0]
        for layer in screen.get('artLayers',[]):
            name=key+'/'+layer['id']
            if name not in data['layers']:
                if not allocate:raise ValueError('Missing art layer codepoint')
                if nxt>=0xE400:raise ValueError('Art layer allocation exhausted')
                data['layers'][name]=f'U+{nxt:04X}';nxt+=1
            x,y,w,h=(layer[v] for v in ('x','y','width','height'))
            if not (1<=w<=256 and 1<=h<=256):raise ValueError('Each font texture cell must fit the 256px atlas')
            # These optional layers surround the existing container. Edits cannot
            # cover the entire screen or create arbitrary interactive regions.
            if x < -72 or x+w>g['width']+72 or y < -8 or y+h>g['height']+8:raise ValueError('Decorative layer outside reviewed minimum-window bounds')
            asset=f'assets/quasar_gui/textures/frames/{key}/{layer["id"]}.png'
            runtime=dict(layer,glyph=chr(int(data['layers'][name][2:],16)),font=FONT,
                prefix=spacing(x-anchor),suffix=spacing(anchor-x-w-1),advance=w+1,
                ascent=13-y,asset=asset,advancePin=[w-1,h//2])
            found.append((key,layer,runtime))
    if allocate:path.write_bytes(encode(data))
    return found

def validate(raw,layer,layout):
    image=Image.open(io.BytesIO(raw));w,h=layer['width'],layer['height']
    if image.mode!='RGBA' or image.size!=(w,h):raise ValueError('Decorative layer dimensions/mode changed')
    alpha=image.getchannel('A')
    if alpha.getpixel((w-1,h//2))!=255 or alpha.getbbox()[2]!=w:raise ValueError('Decorative layer advance pin changed')
    x,y=layer['x'],layer['y'];left=max(0,-x);top=max(0,-y);right=min(w,layout['width']-x);bottom=min(h,layout['height']-y)
    if left<right and top<bottom and alpha.crop((left,top,right,bottom)).getbbox():raise ValueError('Decorative outer layer covers native container interior')

def compile(root,config,layouts,skins,runtime,regenerate=False,overrides=None):
    files={};providers=[]
    for key,layer,r in records(root,config,layouts,skins,True):
        canonical=root/'pack-source'/r['asset'];g=layouts[skins[key]['layout']]
        raw=canonical.read_bytes() if canonical.is_file() and not regenerate else png(draw(layer,g))
        override=Path(overrides)/r['asset'] if overrides else None
        if override and override.is_file():raw=override.read_bytes()
        validate(raw,layer,g);files[r['asset']]=raw
        runtime['skins'][key].setdefault('artLayers',[]).append(r)
        providers.append(dict(type='bitmap',file=r['asset'].replace('assets/quasar_gui/textures/','quasar_gui:'),
            ascent=r['ascent'],height=r['height'],chars=[r['glyph']]))
    return files,providers

def bounds(layout,layers):
    x=min([0]+[l['x'] for l in layers]);y=min([0]+[l['y'] for l in layers])
    right=max([layout['width']]+[l['x']+l['width'] for l in layers]);bottom=max([layout['height']]+[l['y']+l['height'] for l in layers])
    return dict(x=x,y=y,width=right-x,height=bottom-y)

def compose(image,layout,layers,read_asset):
    view=bounds(layout,layers)
    expanded=Image.new('RGBA',(view['width'],view['height']))
    expanded.alpha_composite(image,(-view['x'],-view['y']))
    for layer in layers:
        expanded.alpha_composite(Image.open(io.BytesIO(read_asset(layer['asset']))).convert('RGBA'),
            (layer['x']-view['x'],layer['y']-view['y']))
    return expanded,view
