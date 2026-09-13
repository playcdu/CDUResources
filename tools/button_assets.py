"""Original editable procedural button artwork and deterministic runtime layer data."""
from pathlib import Path
import io
import json
from PIL import Image,ImageDraw
from sample_art import label as tiny_label

STATES=('normal','disabled','selected','pulse_1','pulse_2','pulse_3')
FIRST_CODEPOINT=0xE400
FONT='quasar_gui:menu'
PAPER_MODEL='assets/minecraft/models/item/paper.json'
MODELS={
 PAPER_MODEL:{'parent':'minecraft:item/generated','textures':{'layer0':'minecraft:item/paper'},'overrides':[
    {'predicate':{'custom_model_data':1},'model':'quasar_gui:item/button_carrier'},
    {'predicate':{'custom_model_data':2},'model':'quasar_gui:item/paper_default'},
    {'predicate':{'custom_model_data':194731},'model':'quasar_gui:item/button_carrier'},
    {'predicate':{'custom_model_data':194732},'model':'quasar_gui:item/paper_default'}]},
 'assets/quasar_gui/models/item/button_carrier.json':{'gui_light':'front','textures':{'particle':'minecraft:item/paper'},'elements':[]},
 'assets/quasar_gui/models/item/paper_default.json':{'parent':'minecraft:item/generated','textures':{'layer0':'minecraft:item/paper'}}}

# Original five-by-seven uppercase pixel alphabet. No third-party font textures.
LETTERS={
 'A':['01110','10001','10001','11111','10001','10001','10001'],
 'B':['11110','10001','10001','11110','10001','10001','11110'],
 'C':['01111','10000','10000','10000','10000','10000','01111'],
 'D':['11110','10001','10001','10001','10001','10001','11110'],
 'E':['11111','10000','10000','11110','10000','10000','11111'],
 'F':['11111','10000','10000','11110','10000','10000','10000'],
 'G':['01111','10000','10000','10111','10001','10001','01110'],
 'H':['10001','10001','10001','11111','10001','10001','10001'],
 'I':['11111','00100','00100','00100','00100','00100','11111'],
 'J':['00111','00010','00010','00010','10010','10010','01100'],
 'K':['10001','10010','10100','11000','10100','10010','10001'],
 'L':['10000','10000','10000','10000','10000','10000','11111'],
 'M':['10001','11011','10101','10101','10001','10001','10001'],
 'N':['10001','11001','11001','10101','10011','10011','10001'],
 'O':['01110','10001','10001','10001','10001','10001','01110'],
 'P':['11110','10001','10001','11110','10000','10000','10000'],
 'Q':['01110','10001','10001','10001','10101','10010','01101'],
 'R':['11110','10001','10001','11110','10100','10010','10001'],
 'S':['01111','10000','10000','01110','00001','00001','11110'],
 'T':['11111','00100','00100','00100','00100','00100','00100'],
 'U':['10001','10001','10001','10001','10001','10001','01110'],
 'V':['10001','10001','10001','10001','10001','01010','00100'],
 'W':['10001','10001','10001','10101','10101','11011','10001'],
 'X':['10001','10001','01010','00100','01010','10001','10001'],
 'Y':['10001','10001','01010','00100','00100','00100','00100'],
 'Z':['11111','00001','00010','00100','01000','10000','11111'],
 '0':['01110','10001','10011','10101','11001','10001','01110'],
 '1':['00100','01100','00100','00100','00100','00100','01110'],
 '2':['01110','10001','00001','00010','00100','01000','11111'],
 '3':['11110','00001','00001','01110','00001','00001','11110'],
 '4':['00010','00110','01010','10010','11111','00010','00010'],
 '5':['11111','10000','10000','11110','00001','00001','11110'],
 '6':['01110','10000','10000','11110','10001','10001','01110'],
 '7':['11111','00001','00010','00100','01000','01000','01000'],
 '8':['01110','10001','10001','01110','10001','10001','01110'],
 '9':['01110','10001','10001','01111','00001','00001','01110'],
 '+':['00000','00100','00100','11111','00100','00100','00000'],
 '-':['00000','00000','00000','11111','00000','00000','00000']}

def encode(value):return (json.dumps(value,indent=2,ensure_ascii=True)+'\n').encode()
def spacing(amount):
    if abs(amount)>511:raise ValueError('Layer spacing outside allocated range')
    start=0xF000 if amount>=0 else 0xF009
    return ''.join(chr(start+i) for i in reversed(range(9)) if abs(amount)&(1<<i))
def png(image):
    out=io.BytesIO();image.save(out,format='PNG',compress_level=9,optimize=False);return out.getvalue()
def rgb(color,delta):return tuple(max(0,min(255,v+delta)) for v in color)

def geometry(layout,button):
    slots={p['index']:p for p in layout['slots']}
    points=[slots[i] for i in button['slots']]
    x=min(p['x'] for p in points)-1;y=min(p['y'] for p in points)-1
    w=max(p['x'] for p in points)-x+17;h=max(p['y'] for p in points)-y+17
    expected={p['index'] for p in layout['slots'] if x<=p['x']<x+w and y<=p['y']<y+h}
    if expected!=set(button['slots']) or w*h!=len(points)*18*18:raise ValueError('Button cells must form a complete rectangle: '+button['id'])
    return x,y,w,h

def load(root,layouts,skins):
    path=root/'manifests/button-layouts.json'
    config=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'screens':{}}
    for key,screen in config['screens'].items():
        skin=skins[key];layout=layouts[skin['layout']];top={s['index'] for s in layout['slots']}
        occupied=set();ids=set()
        for b in screen['buttons']:
            if b['id'] in ids:raise ValueError('Duplicate button id')
            ids.add(b['id']);geometry(layout,b)
            if occupied & set(b['slots']):raise ValueError('Overlapping button cells')
            if b['sourceSlot'] not in top or b['role'] not in ('action','info'):raise ValueError('Invalid source/role')
            occupied.update(b['slots'])
        content=set(screen['contentSlots'])
        if content&occupied or not content|occupied<=top:raise ValueError('Invalid content/button partition')
        if 'contentRegion' in screen:
            region=screen['contentRegion'];sources=region['sourceSlots'];targets=region['slots']
            if not sources or not targets or len(set(sources))!=len(sources) or len(set(targets))!=len(targets):raise ValueError('Content region needs unique nonempty sources and targets')
            if not set(sources)<=top or set(targets)!=content or len(targets)>len(sources):raise ValueError('Invalid native content mapping')
        skin['visibleContentSlots']=sorted(content);skin['paintedControlSlots']=sorted(occupied)
        skin['chromeStyle']='midnight';skin['presentation']=screen.get('presentation','painted_controls')
        skin['liveSlots']=sorted(content|occupied)
        skin['removedDecorations']=sorted(set(skin['removedDecorations'])-(content|occupied))
        skin['staticProtectedSlots']=sorted(top-content-occupied-set(skin['removedDecorations']))
    return config

def masks(layout,skin):
    dx,dy,w,h=layout['itemClearance'];content=set(skin.get('visibleContentSlots',skin['liveSlots']))
    return [(p['x']+dx,p['y']+dy,w,h) for p in layout['slots'] if p['index'] in content]+[(p['x']+dx,p['y']+dy,w,h) for p in layout['playerSlots']]

def advance_pin(layout,skin,button):
    x,y,w,h=geometry(layout,button)
    clear=masks(layout,skin)
    for px in reversed(range(w)):
        for py in sorted(range(h),key=lambda n:abs(n-h//2)):
            if not any(mx<=x+px<mx+mw and my<=y+py<my+mh for mx,my,mw,mh in clear):return px,py
    raise ValueError('Button region has no visible pixels')

def clear_regions(image,layout,skin,origin=(0,0)):
    d=ImageDraw.Draw(image);ox,oy=origin
    for x,y,w,h in masks(layout,skin):d.rectangle((x-ox,y-oy,x+w-1-ox,y+h-1-oy),fill=(0,0,0,0))
    for extra in layout.get('extraTransparent',[]):
        x,y,w,h=extra['rect'];d.rectangle((x-ox,y-oy,x+w-1-ox,y+h-1-oy),fill=(0,0,0,0))
    return image

def text(draw,x,y,line,color):
    for n,char in enumerate(line.upper()):
        for j,row in enumerate(LETTERS.get(char,[])):
            for i,pixel in enumerate(row):
                if pixel=='1':draw.point((x+n*6+i,y+j),fill=color)

def button_image(layout,skin,button,state):
    x,y,w,h=geometry(layout,button)
    image=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(image)
    base={'primary':(27,83,95),'secondary':(39,52,70),'danger':(101,46,59)}[button['style']]
    edge={'primary':(94,219,201),'secondary':(111,144,174),'danger':(241,125,127)}[button['style']]
    ink=(235,244,239)
    if state=='disabled':base=(42,47,57);edge=(86,91,100);ink=(143,150,158)
    elif state=='selected':base=(34,100,69);edge=(144,233,150)
    elif state.startswith('pulse_'):
        delta={'pulse_1':18,'pulse_2':36,'pulse_3':12}[state];base=rgb(base,delta);edge=rgb(edge,delta)
    d.rectangle((0,0,w-1,h-1),fill=(15,22,32,255))
    d.rectangle((1,1,w-2,h-2),fill=base+(255,))
    d.line((2,1,w-3,1),fill=edge+(255,));d.line((1,2,1,h-3),fill=rgb(edge,-27)+(255,))
    d.line((2,h-2,w-2,h-2,w-2,2),fill=rgb(base,-16)+(255,))
    lines=button.get('lines') or [button['label'].upper()]
    if button.get('icon')=='close':
        d.line((5,5,w-6,h-6),fill=ink+(255,),width=2);d.line((w-6,5,5,h-6),fill=ink+(255,),width=2)
        lines=[]
    elif button.get('icon')=='balance':
        cy=h//2-6 if h>=36 else h//2;d.ellipse((3,cy-6,w-4,cy+6),outline=(226,186,92,255),fill=(127,93,48,255))
        tiny_label(d,w//2-1,cy-2,'$',(250,226,164,255))
        if h>=36:tiny_label(d,3,cy+14,'BAL',(215,225,230,255))
        lines=[]
    elif button.get('icon')=='search':
        d.ellipse((4,4,11,11),outline=ink+(255,),width=2);d.line((10,10,14,14),fill=ink+(255,),width=2);lines=[]
    elif button.get('icon')=='settings':
        d.rectangle((7,3,10,14),fill=ink+(255,));d.rectangle((3,7,14,10),fill=ink+(255,))
        d.ellipse((4,4,13,13),fill=ink+(255,));d.ellipse((7,7,10,10),fill=base+(255,));lines=[]
    small=(w<36 or h<25 and len(lines)>1 or max(map(len,lines),default=0)*6-1>w-4)
    if small:
        if max(map(len,lines),default=0)*4-1>w-4:
            short={'Privacy':'PRIVACY','Rank':'RANK'};lines=[short.get(button['label'],button['label'][:max(1,(w-4)//4)]).upper()]
        yy=(h-(len(lines)*6-1))//2
        for line in lines:tiny_label(d,(w-(len(line)*4-1))//2,yy,line,ink+(255,));yy+=6
    else:
        yy=(h-(len(lines)*9-2))//2
        for line in lines:text(d,(w-(len(line)*6-1))//2,yy,line,ink+(255,));yy+=9
    if state=='selected':d.line((w-6,3,w-5,4,w-3,2),fill=edge+(255,))
    clear_regions(image,layout,skin,(x,y))
    d.point(advance_pin(layout,skin,button),fill=(15,22,32,255))
    return image

def background(layout,skin,key):
    w,h=layout['width'],layout['height'];image=Image.new('RGBA',(w,h),(16,23,34,255));d=ImageDraw.Draw(image)
    d.rectangle((1,1,w-2,h-2),outline=(66,89,108,255))
    d.rectangle((3,3,w-4,14),fill=(28,41,55,255));d.line((5,2,w-6,2),fill=(77,187,179,255))
    invy=layout['inventoryLabel'][1]
    d.rectangle((4,invy-1,w-5,invy+10),fill=(214,225,224,255));d.line((5,invy-2,w-6,invy-2),fill=(74,103,123,255))
    if key=='auction_confirm':
        tiny_label(d,30,24,'REVIEW YOUR PURCHASE',(212,229,231,255))
        d.rectangle((33,42,72,88),fill=(29,43,59,255),outline=(72,116,130,255))
        tiny_label(d,39,80,'ITEM',(171,203,211,255))
        tiny_label(d,20,97,'HOVER ITEM + BUY FOR DETAILS',(162,187,200,255))
    if key.startswith('trade_') and key!='trade_money':
        d.rectangle((79,16,96,105),fill=(29,48,63,255))
        for yy in range(20,102,8):d.rectangle((86,yy,89,yy+2),fill=(73,109,126,255))
        # Readiness is independent of offered money. Logical money source52 may
        # be absent at zero, so its disabled info frame cannot carry this signal.
        yours=key in ('trade_self_ready','trade_both_ready')
        theirs=key in ('trade_other_ready','trade_both_ready')
        for label,top,ready in [('YOU',28,yours),('THEM',71,theirs)]:
            color=(133,230,161,255) if ready else (121,150,168,255)
            d.rectangle((80,top-3,95,top+21),fill=(29,48,63,255))
            tiny_label(d,88-(len(label)*4-1)//2,top,label,color)
            if ready:d.line((83,top+13,86,top+16,92,top+9),fill=color,width=2)
            else:d.line((84,top+13,91,top+13),fill=color)
        d.line((6,15,76,15),fill=(133,230,161,255) if yours else (74,103,123,255))
        d.line((99,15,169,15),fill=(133,230,161,255) if theirs else (74,103,123,255))
    if key=='trade_money':
        tiny_label(d,13,27,'OFFER',(169,199,215,255));tiny_label(d,13,36,'VALUE',(169,199,215,255))
        tiny_label(d,122,27,'CLICK',(169,199,215,255));tiny_label(d,122,36,'TO EDIT',(169,199,215,255))
        tiny_label(d,12,6,'OFFERED MONEY',(235,244,239,255))
    if key.startswith('ticket_'):
        tiny_label(d,28,23,'REVIEW TICKET DETAILS',(210,228,231,255))
        d.rectangle((68,42,107,77),fill=(27,45,58,255),outline=(80,130,135,255))
        tiny_label(d,47,116,'INVALID TICKET' if key=='ticket_invalid' else 'SINGLE USE TICKET',
            (230,152,152,255) if key=='ticket_invalid' else (135,221,174,255))
    if key=='auction_duration':tiny_label(d,12,62,'DURATION',(182,207,216,255))
    if key=='chest_shop_settings':
        tiny_label(d,75,44,'SHOP',(182,207,216,255));tiny_label(d,73,53,'TOOLS',(182,207,216,255))
    if key.startswith('chest_shop_listing_'):tiny_label(d,12,99,'LISTING',(182,207,216,255))
    clear_regions(image,layout,skin)
    d.rectangle((w-1,0,w-1,2),fill=(16,23,34,255))
    return image

def compile(root,layouts,skins,config,runtime,regenerate=False,overrides=None,regenerate_buttons=None):
    allocation_path=root/'manifests/button-codepoints.json'
    allocation=json.loads(allocation_path.read_text()) if allocation_path.exists() else {'schemaVersion':1,'regions':{}}
    assigned=[int(v[2:],16) for region in allocation['regions'].values() for v in region.values()]
    next_cp=max(assigned,default=FIRST_CODEPOINT-1)+1
    files={name:encode(model) for name,model in MODELS.items()} if config['screens'] else {}
    providers=[]
    requested=set(regenerate_buttons or [])
    known={key+'/'+button['id'] for key,screen in config['screens'].items() for button in screen['buttons']}
    if requested-known:raise ValueError('Unknown button regeneration binding: '+', '.join(sorted(requested-known)))
    for key,screen in config['screens'].items():
        skin=skins[key];layout=layouts[skin['layout']];anchor=layout['titleAnchor'][0];regions=[]
        for button in screen['buttons']:
            name=key+'/'+button['id'];codes=allocation['regions'].setdefault(name,{})
            x,y,w,h=geometry(layout,button);states={};pin=advance_pin(layout,skin,button);advance=pin[0]+2
            for state in STATES:
                if state not in codes:codes[state]=f'U+{next_cp:04X}';next_cp+=1
                cp=int(codes[state][2:],16)
                if cp>=0xF000:raise ValueError('Button glyph range exhausted')
                asset=f'assets/quasar_gui/textures/buttons/{key}/{button["id"]}/{state}.png'
                canonical=root/'pack-source'/asset
                raw=canonical.read_bytes() if canonical.is_file() and not regenerate and name not in requested else png(button_image(layout,skin,button,state))
                override=Path(overrides)/asset if overrides else None
                if override and override.is_file():raw=override.read_bytes()
                validate_button(raw,layout,skin,button,state)
                files[asset]=raw
                states[state]=dict(glyph=chr(cp),font=FONT,prefix=spacing(x-anchor),suffix=spacing(anchor-x-advance),
                    advance=advance,advancePin=list(pin),ascent=13-y,height=h,asset=asset)
                providers.append(dict(type='bitmap',file=asset.replace('assets/quasar_gui/textures/','quasar_gui:'),
                    ascent=13-y,height=h,chars=[chr(cp)]))
            regions.append(dict(button,x=x,y=y,width=w,height=h,states=states,
                defaultState=screen.get('defaultStates',{}).get(button['id'],'normal'),
                animation=config['animation']))
        runtime['skins'][key]['buttonRegions']=regions
        runtime['skins'][key]['visibleContentSlots']=skin['visibleContentSlots']
        runtime['skins'][key]['paintedControlSlots']=skin['paintedControlSlots']
        runtime['skins'][key]['presentation']=skin['presentation']
        if 'contentRegion' in screen:runtime['skins'][key]['contentRegion']=screen['contentRegion']
    runtime['buttonCarrier']=config.get('carrier',{})
    allocation_path.write_bytes(encode(allocation))
    return files,providers

def validate_button(raw,layout,skin,button,state):
    x,y,w,h=geometry(layout,button);image=Image.open(io.BytesIO(raw))
    if image.mode!='RGBA' or image.size!=(w,h):raise ValueError('Button dimensions/mode changed')
    alpha=image.getchannel('A')
    pin=advance_pin(layout,skin,button)
    if alpha.getpixel(pin)!=255 or alpha.getbbox()[2]!=pin[0]+1:raise ValueError('Button advance pin changed')
    for mx,my,mw,mh in masks(layout,skin):
        bx=max(0,mx-x);by=max(0,my-y);ex=min(w,mx+mw-x);ey=min(h,my+mh-y)
        if bx<ex and by<ey and alpha.crop((bx,by,ex,ey)).getbbox():raise ValueError('Button covers native content/player mask')

def compose(base,regions,read_asset):
    image=base.copy().convert('RGBA')
    for region in regions:
        frame=region['states'][region.get('defaultState','normal')]
        layer=Image.open(io.BytesIO(read_asset(frame['asset']))).convert('RGBA')
        image.alpha_composite(layer,(region['x'],region['y']))
    return image

def mapped_controls(screen,source):
    result=dict(source or {});controls=[]
    for b in screen['buttons']:
        candidates=[c for c in result.get('controls',[]) if b['sourceSlot'] in c['slots']]
        candidates.sort(key=lambda c:(0 if c['label']==b.get('sourceControl') else 1,len(c['slots'])))
        original=candidates[0] if candidates else {}
        controls.append(dict(original,slots=b['slots'],label=b['label']+' (source '+str(b['sourceSlot'])+')',
            native_item='Invisible GUI paper carrier; standard: '+original.get('native_item','original item'),
            trigger=original.get('trigger','Original callback' if b['role']=='action' else 'none'),
            real_effect=original.get('real_effect','Original semantic action' if b['role']=='action' else 'Read-only information')))
    content=set(screen['contentSlots'])
    for original in result.get('controls',[]):
        if 'contentRegion' in screen:
            region=screen['contentRegion']
            visible={target for source,target in zip(region['sourceSlots'],region['slots']) if source in original['slots']}
        else:visible=content&set(original['slots'])
        if visible:controls.append(dict(original,slots=sorted(visible)))
    result['controls']=controls
    return result
