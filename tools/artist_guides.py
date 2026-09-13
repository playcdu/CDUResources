"""Readable action legends and original schematic examples, never gameplay evidence."""
import math
from PIL import Image, ImageDraw, ImageFont
from sample_art import label

TITLE=ImageFont.load_default(size=22)
BODY=ImageFont.load_default(size=14)
SMALL=ImageFont.load_default(size=12)

def lines(text,width=500,font=BODY):
    draw=ImageDraw.Draw(Image.new('RGB',(1,1)));out=[];line=''
    for word in str(text).split():
        candidate=(line+' '+word).strip()
        if line and draw.textlength(candidate,font=font)>width:out.append(line);line=word
        else:line=candidate
    if line:out.append(line)
    return out

def range_label(indices):
    values=sorted(set(indices));groups=[]
    for i in values:
        if groups and i==groups[-1][-1]+1:groups[-1].append(i)
        else:groups.append([i])
    return ','.join(str(g[0]) if len(g)==1 else str(g[0])+'-'+str(g[-1]) for g in groups)

def checker(image):
    out=Image.new('RGBA',image.size,(227,233,237,255));draw=ImageDraw.Draw(out)
    for y in range(0,image.height,4):
        for x in range(0,image.width,4):
            if (x//4+y//4)%2:draw.rectangle((x,y,x+3,y+3),fill=(199,210,217,255))
    out.alpha_composite(image);return out.convert('RGB')

def create_guide(layout,skin,key,image,controls=None):
    entries=[]
    if controls:
        for c in controls.get('controls',[]):
            entries.append((range_label(c['slots'])+'  '+c['label'],
                lines(c.get('real_effect',''))+lines('Trigger: '+c.get('trigger',''))+
                lines('When: '+c.get('condition','Always present'))+
                lines('Native icon: '+c.get('native_item','Original ItemStack'))))
    else:
        for group,description in skin.get('slotRoles',{}).items():entries.append((group,lines(description)))
    if not entries:entries=[('0-'+str(len(layout['slots'])-1),lines('Generic template: all top slots remain visible. Assign existing actions in server code before drawing a new control.'))]
    entries += [('Player inventory / hotbar',lines('All 36 native player slots stay transparent. Their interaction follows the original menu; artwork adds no permission or click handler.')),
                ('Protected static artwork',lines('Empty explanatory panels have no callback. Only numbered native action slots can be activated.'))]
    right_height=sum(32+len(text)*18 for heading,text in entries)+155
    w=1280;h=max(layout['height']*4+170,right_height)
    canvas=Image.new('RGB',(w,h),(240,243,240));d=ImageDraw.Draw(canvas)
    d.rectangle((0,0,w,91),fill=(27,44,56));d.text((22,15),key.replace('_',' ').upper(),font=TITLE,fill='white')
    d.text((22,50),f"{layout['menuType']} | {layout['width']} x {layout['height']} px | {skin['codepoint']} | zero-based slot numbers",font=BODY,fill=(185,208,219))
    left=checker(image).resize((704,layout['height']*4),Image.Resampling.NEAREST)
    ld=ImageDraw.Draw(left);live=set(skin.get('liveSlots',[p['index'] for p in layout['slots']]))
    for p in layout['slots']+layout['playerSlots']:
        x,y=p['x']*4,p['y']*4
        is_top=p in layout['slots'];active=not is_top or p['index'] in live
        col=(6,120,154) if active else (162,66,92)
        ld.rectangle((x,y,x+63,y+63),outline=col,width=1)
        ld.rectangle((x+1,y+1,x+21,y+16),fill=(241,246,243))
        ld.text((x+3,y+1),str(p['index']),font=SMALL,fill=col)
    x,y,tw,th=layout['textSafe'];ld.rectangle((x*4,y*4,(x+tw)*4-1,(y+th)*4-1),outline=(142,64,173),width=2)
    ax,ay=layout['titleAnchor'];ld.line((ax*4-5,ay*4,ax*4+5,ay*4),fill=(220,46,70),width=2)
    ld.line((ax*4,ay*4-5,ax*4,ay*4+5),fill=(220,46,70),width=2)
    canvas.paste(left,(20,111))
    d.text((20,layout['height']*4+124),'Checkerboard = alpha-zero window. Blue = native item footprint. Rose = protected static panel.',font=SMALL,fill=(57,76,84))
    d.text((20,layout['height']*4+143),'Minecraft supplies slot hit testing. Purple = title area. Red cross = title anchor.',font=SMALL,fill=(57,76,84))
    d.text((751,110),'CONTROL / ACTION LEGEND',font=TITLE,fill=(29,66,80))
    yy=146
    for heading,body in entries:
        d.rectangle((751,yy,1259,yy+23),fill=(221,231,230));d.text((759,yy+3),heading,font=BODY,fill=(22,63,80));yy+=28
        for line in body:d.text((760,yy),line,font=BODY,fill=(42,56,65));yy+=18
        yy+=4
    return canvas

def icon(draw,x,y,kind,color=(105,197,224)):
    # Deliberately schematic shapes; no Mojang textures or item models are copied.
    if kind in ('previous','back','next'):
        if kind=='next':draw.polygon([(x+3,y+3),(x+11,y+8),(x+3,y+13)],fill=color)
        else:draw.polygon([(x+12,y+3),(x+4,y+8),(x+12,y+13)],fill=color)
    elif kind in ('close','cancel'):
        draw.ellipse((x+2,y+2,x+13,y+13),outline=(229,98,104),width=2);draw.line((x+4,y+4,x+11,y+11),fill=(229,98,104),width=2)
    elif kind in ('confirm','ready'):
        draw.rectangle((x+2,y+2,x+13,y+13),fill=(53,127,88));draw.line((x+4,y+8,x+7,y+11,x+12,y+5),fill=(183,255,203),width=2)
    elif kind in ('money','balance'):
        draw.ellipse((x+2,y+3,x+13,y+12),fill=(235,183,76),outline=(132,86,41));label(draw,x+6,y+5,'$',(105,64,28,255))
    elif kind=='search':
        draw.ellipse((x+2,y+2,x+10,y+10),outline=(153,220,240),width=2);draw.line((x+9,y+9,x+14,y+14),fill=(153,220,240),width=2)
    elif kind in ('increase','decrease'):
        draw.line((x+3,y+8,x+12,y+8),fill=(195,235,205),width=2)
        if kind=='increase':draw.line((x+8,y+3,x+8,y+12),fill=(195,235,205),width=2)
    elif kind in ('watch','notification'):
        draw.polygon([(x+8,y+1),(x+10,y+6),(x+15,y+6),(x+11,y+9),(x+13,y+14),(x+8,y+11),(x+3,y+14),(x+5,y+9),(x+1,y+6),(x+6,y+6)],fill=(238,198,99))
    elif kind in ('settings','listings'):
        draw.rectangle((x+2,y+3,x+13,y+13),fill=(183,136,81),outline=(92,59,31));draw.line((x+3,y+7,x+12,y+7),fill=(238,201,139));draw.rectangle((x+7,y+7,x+9,y+10),fill=(238,201,139))
    elif kind in ('stats','quantity','stock'):
        draw.rectangle((x+3,y+2,x+12,y+14),fill=(231,234,219));draw.line((x+5,y+5,x+10,y+5),fill=(79,122,133));draw.line((x+5,y+8,x+10,y+8),fill=(79,122,133));draw.line((x+5,y+11,x+8,y+11),fill=(79,122,133))
    else:
        draw.polygon([(x+8,y+1),(x+14,y+6),(x+10,y+14),(x+4,y+12),(x+1,y+6)],fill=color,outline=(39,81,105));draw.line((x+3,y+5,x+8,y+3,x+12,y+6),fill=(201,243,248))

def classify(control,slot,key):
    text=(control.get('label','')+' '+control.get('native_item','')).lower()
    if 'increase' in text and 'decrease' in text:
        return 'increase' if slot==min(control.get('slots',[slot])) else 'decrease'
    for word in ('previous','next','close','cancel','search','confirm','ready','increase','decrease','money','balance','watch','notification','settings','stock','quantity','stats','listings','back'):
        if word in text:return word
    return 'item'

def native_layer(layout,skin,key,controls):
    out=Image.new('RGBA',(layout['width'],layout['height']),(187,195,194,255));d=ImageDraw.Draw(out)
    live=set(skin.get('liveSlots',[p['index'] for p in layout['slots']]))
    for p in layout['slots']+layout['playerSlots']:
        x,y=p['x'],p['y'];d.rectangle((x-1,y-1,x+16,y+16),fill=(98,108,111,255));d.line((x-1,y+16,x+16,y+16,x+16,y-1),fill=(221,229,225,255))
    control_by_slot={i:c for c in (controls or {}).get('controls',[]) for i in c['slots']}
    for p in layout['slots']:
        if p['index'] not in live:continue
        c=control_by_slot.get(p['index'],{});kind=classify(c,p['index'],key)
        # Content examples are sparse on purpose; all control slots remain illustrated.
        if key=='auction_house' and p['index']<45 and p['index'] not in (0,1,2,3,4,9,10,11,18):continue
        if key.startswith('trade_') and p['index'] not in (0,1,9,5,14,13,47,52):continue
        icon(d,p['x'],p['y'],kind)
    for i in (0,3,8):
        p=layout['playerSlots'][i];icon(d,p['x'],p['y'],'item',(135,190,125))
    return out

def composite(layout,skin,key,image,controls):
    native=native_layer(layout,skin,key,controls);native.alpha_composite(image);d=ImageDraw.Draw(native)
    if not layout['centered']:
        names={'auction_house':'AUCTION HOUSE / PAGE 2','trade_self_ready':'TRADE WITH EXAMPLE PLAYER',
            'chest_shop_listing_enabled':'SHOP LISTING / EXAMPLE','auction_confirm':'CONFIRM PURCHASE',
            'ticket_valid':'TICKET REDEMPTION','chest_shop_settings':'SHOP OPTIONS'}
        label(d,layout['titleAnchor'][0],6,names.get(key,key.replace('_',' '))[:layout['textWidth']//4],(47,61,68,255))
    label(d,8,layout['inventoryLabel'][1]+1,'INVENTORY',(47,61,68,255))
    return native.convert('RGB')

def illustration(layout,skin,key,image,controls):
    guide=create_guide(layout,skin,key,image,controls)
    d=ImageDraw.Draw(guide);d.rectangle((0,0,1280,91),fill=(24,62,78))
    d.text((22,15),key.replace('_',' ').upper()+' / COMPOSED EXAMPLE',font=TITLE,fill='white')
    d.text((22,50),'LAYOUT ILLUSTRATION - NOT GAMEPLAY. Native icons/text are original schematic examples.',font=BODY,fill=(227,209,157))
    sample=composite(layout,skin,key,image,controls).resize((704,layout['height']*4),Image.Resampling.NEAREST)
    guide.paste(sample,(20,111))
    yy=layout['height']*4+121
    d.rectangle((20,yy,724,yy+45),fill=(240,243,240))
    d.text((20,yy+3),'Actual overlay composited over original schematic items and text. Read actions in the legend.',font=SMALL,fill=(57,76,84))
    d.text((20,yy+22),'Static explanation panels have no callback. Minecraft supplies all native slot hit testing.',font=SMALL,fill=(57,76,84))
    return guide

def layer_diagram(layout,skin,image,controls):
    out=Image.new('RGB',(1680,875),(237,241,238));d=ImageDraw.Draw(out)
    d.rectangle((0,0,1680,105),fill=(24,45,61))
    d.text((24,20),'AUCTION HOUSE: THREE LAYERS, ONE NATIVE CONTAINER',font=TITLE,fill='white')
    d.text((24,58),'Layout illustration - not gameplay. The pack paints chrome; Minecraft draws items; existing slots handle clicks.',font=BODY,fill=(195,218,228))
    for i,(heading,body) in enumerate((('1  NATIVE CONTENT','Schematic item icons and player slots. Item names, counts, prices and lore remain live.'),
        ('2  BITMAP OVERLAY','Actual pack PNG on checkerboard. Transparent wells reveal the native layer.'),
        ('3  EXISTING SLOT POSITIONS','Orange boxes mark 16-pixel item footprints; Minecraft supplies slot hit testing.'))):
        x=24+i*552;d.text((x,124),heading,font=TITLE,fill=(28,68,83))
        for j,line in enumerate(lines(body,510)):d.text((x,156+j*18),line,font=BODY,fill=(54,77,84))
        layer=native_layer(layout,skin,'auction_house',controls).convert('RGB') if i==0 else checker(image) if i==1 else composite(layout,skin,'auction_house',image,controls)
        layer=layer.resize((528,666),Image.Resampling.NEAREST)
        if i==2:
            ld=ImageDraw.Draw(layer)
            for p in layout['slots']:
                x1,y1=p['x']*3,p['y']*3;ld.rectangle((x1,y1,x1+47,y1+47),outline=(229,125,43),width=2)
                if p['index']>=45:ld.text((x1+2,y1+2),str(p['index']),font=SMALL,fill=(255,250,231))
        out.paste(layer,(x,201))
    return out
