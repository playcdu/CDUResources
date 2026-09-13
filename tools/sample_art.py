"""Original pixel labels, semantic panels and control frames for starter artwork."""
from PIL import Image, ImageDraw

# Original compact 3x5 pixel alphabet. The release art imports no font asset.
PIXELS={
 'A':'010101111101101','B':'110101110101110','C':'011100100100011','D':'110101101101110',
 'E':'111100110100111','F':'111100110100100','G':'011100101101011','H':'101101111101101',
 'I':'111010010010111','J':'001001001101010','K':'101101110101101','L':'100100100100111',
 'M':'101111111101101','N':'101111111111101','O':'010101101101010','P':'110101110100100',
 'Q':'010101101111011','R':'110101110101101','S':'011100010001110','T':'111010010010010',
 'U':'101101101101111','V':'101101101101010','W':'101101111111101','X':'101101010101101',
 'Y':'101101010010010','Z':'111001010100111','0':'111101101101111','1':'010110010010111',
 '2':'110001010100111','3':'110001010001110','4':'101101111001001','5':'111100110001110',
 '6':'011100111101111','7':'111001010010010','8':'111101111101111','9':'111101111001110',
 '+':'000010111010000','-':'000000111000000','>':'100010001010100','<':'001010100010001',
 '/':'001001010100100',':':'000010000010000','.':'000000000000010','!':'010010010000010',
 '?':'110001010000010','=':'000111000111000','%':'101001010100101', '$':'011110010011110'}

def label(draw,x,y,text,color=(239,246,249,255),scale=1):
    for n,c in enumerate(text.upper()):
        bits=PIXELS.get(c,'0'*15)
        for i,bit in enumerate(bits):
            if bit=='1':
                px=x+(n*4+i%3)*scale;py=y+i//3*scale
                draw.rectangle((px,py,px+scale-1,py+scale-1),fill=color)

def centered(draw,x,y,text,color=(239,246,249,255),scale=1):
    label(draw,x-(len(text)*4-1)*scale//2,y,text,color,scale)

def arrow(draw,x,y,direction,color):
    if direction=='right':draw.line((x,y,x+12,y),fill=color,width=2);draw.line((x+8,y-4,x+12,y,x+8,y+4),fill=color,width=2)
    else:draw.line((x+12,y,x,y),fill=color,width=2);draw.line((x+4,y-4,x,y,x+4,y+4),fill=color,width=2)

def panel(draw,box,color,edge=None):
    x,y,w,h=box;draw.rectangle((x,y,x+w-1,y+h-1),fill=color)
    if edge:draw.line((x,y,x+w-1,y),fill=edge,width=1)

def paint(image,layout,skin,key):
    draw=ImageDraw.Draw(image)
    families={'auction':(67,64,115),'admin_shop':(28,86,104),'chest_shop':(97,67,39),
        'economy':(39,89,72),'trade':(37,75,108),'ticket':(98,54,90),'prefixes':(80,54,107),
        'guild_bank':(59,82,49),'invsee':(99,60,46),'utility':(47,70,88)}
    base=families[skin['family']];bright=tuple(min(255,v+72) for v in base)
    sparse=len(skin.get('liveSlots',layout['slots'])) < len(layout['slots'])-3
    if sparse:
        panel(draw,(5,16,166,layout['inventoryLabel'][1]-19),base+(255,),bright+(255,))
        # Restrained woven chrome gives the blank protected canvas a deliberate texture.
        for y in range(19,layout['inventoryLabel'][1]-4,5):
            for x in range(8,169,8):draw.point((x,y),fill=tuple(v+9 for v in base)+(255,))
    # A distinctive stepped border remains visible even on dense item grids.
    for y in range(20,image.height-5,12):
        draw.line((2,y,3,y+4),fill=bright+(255,))
        draw.line((172,y+4,173,y),fill=bright+(255,))
    live=set(skin.get('liveSlots',[p['index'] for p in layout['slots']]))
    for p in layout['slots']:
        if p['index'] in live:
            x,y=p['x'],p['y']
            draw.rectangle((x-3,y-3,x+18,y+18),outline=bright+(255,))
    if key=='auction_confirm':
        centered(draw,88,22,'REVIEW PURCHASE',scale=2)
        panel(draw,(14,39,64,41),(80,78,132,255));panel(draw,(98,39,64,41),(39,112,81,255))
        centered(draw,53,42,'ITEM');centered(draw,124,42,'CONFIRM')
        arrow(draw,80,61,'right',(199,214,232,255))
        centered(draw,88,87,'HOVER ITEM FOR PRICE + SELLER')
        centered(draw,88,98,'CONFIRM TO BUY')
        label(draw,101,116,'CLOSE >')
    elif key=='auction_duration':
        label(draw,12,21,'CHOOSE LISTING DURATION',scale=1)
        for x,text in zip((52,70,88,106,124),('1D','3D','7D','12D','15D')):centered(draw,x,60,text)
    elif key.startswith('chest_shop_listing_'):
        label(draw,12,21,'LISTING CONTROLS')
        panel(draw,(10,36,62,55),(72,54,40,255))
        label(draw,15,40,'STATS');label(draw,45,40,'STOCK')
        label(draw,14,78,'READ ONLY')
        for x,text in ((88,'QTY'),(106,'SELL'),(124,'BUY')):centered(draw,x,27,text)
        label(draw,136,43,'STATE')
        label(draw,137,77,'OFF' if key.endswith('disabled') else 'ON',
            (245,166,166,255) if key.endswith('disabled') else (155,240,192,255))
        centered(draw,88,97,'ARROWS ADJUST / PRICE ICONS TOGGLE')
    elif key in ('chest_shop_buy','chest_shop_sell'):
        label(draw,57,21,'SELECT AMOUNT')
        label(draw,7,41,'EDIT')
        label(draw,59,60,'BUY OPTIONS' if key.endswith('buy') else 'SELL OPTIONS')
    elif key=='chest_shop_settings':
        label(draw,13,21,'SHOP MANAGEMENT')
        for x,text in ((34,'STATS'),(70,'UP'),(88,'NAME'),(106,'SYNC')):centered(draw,x,60,text)
        label(draw,125,46,'ICON',color=(244,207,155,255));label(draw,121,55,'ACTIONS',color=(244,207,155,255))
    elif key.startswith('chest_shop_upgrade'):
        label(draw,54,21,'SELECT PREMIUM TIER')
        label(draw,8,41,'BID')
        for x,text in ((70,'AD'),(88,'TP'),(106,'OPEN')):centered(draw,x,60,text)
        text='APPLY' if key.endswith('confirm') else 'WAIT' if key.endswith('disabled') else 'REVIEW'
        centered(draw,142,60,text,(156,239,186,255) if key.endswith('confirm') else (246,184,166,255))
        if key.endswith('disabled'):draw.line((130,57,155,57),fill=(223,109,109,255),width=2)
        elif key.endswith('confirm'):draw.line((130,57,155,57),fill=(111,227,168,255),width=2)
    elif key=='economy_hub':
        label(draw,13,21,'ECONOMY DIRECTORY')
        for x,text in zip((34,52,70,88,106,124,142),('BAL','AH','SHOP','ADS','LOG','VIEW','RANK')):centered(draw,x,60,text)
    elif key.startswith('trade_') and key!='trade_money':
        left=key in ('trade_self_ready','trade_both_ready');right=key in ('trade_other_ready','trade_both_ready')
        panel(draw,(80,16,16,90),(30,54,75,255))
        label(draw,83,21,'SET')
        for at,ready in ((82,left),(90,right)):
            for y in range(59,92,7):
                draw.rectangle((at,y,at+3,y+3),fill=(99,232,149,255) if ready else (220,163,85,255))
        # The thin center labels identify which readiness indicator belongs to whom.
        label(draw,82,94,'Y');label(draw,90,94,'T')
        panel(draw,(6,107,164,19),(28,55,75,255))
        label(draw,9,110,'YOUR');label(draw,9,118,'MONEY')
        label(draw,64,111,'< EDIT')
        label(draw,105,110,'THEIR');label(draw,105,118,'MONEY')
        label(draw,155,115,'OK' if right else '..',(129,232,167,255) if right else (226,185,118,255))
    elif key=='trade_money':
        # Three labels point at actual increase / return / decrease slots.
        for y,text in ((20,'ADD'),(38,'RETURN'),(56,'LESS')):
            label(draw,34 if text!='RETURN' else 25,y,text);arrow(draw,62,y+2,'right',(167,209,237,255))
        label(draw,108,25,'OFFER');label(draw,105,34,'EDITOR')
        label(draw,109,51,'CLICK');label(draw,105,60,'TO RETURN')
    elif key.startswith('ticket_'):
        valid=key=='ticket_valid'
        status=(140,238,176,255) if valid else (253,163,163,255)
        centered(draw,88,23,'REDEEM TICKET',scale=2)
        centered(draw,88,41,'HOVER TO REVIEW DETAILS')
        centered(draw,88,77,'CHECK')
        centered(draw,52,95,'CANCEL')
        centered(draw,124,95,'REDEEM' if valid else 'UNAVAILABLE',status)
        centered(draw,88,112,'VALID / SINGLE USE' if valid else 'INVALID / CANNOT REDEEM',status)
        draw.line((15,105,160,105),fill=status,width=1)
    elif key=='crafting':
        label(draw,10,21,'3X3',color=(50,75,87,255))
        label(draw,116,21,'OUTPUT',color=(50,75,87,255))
        label(draw,109,62,'TAKE RESULT',color=(50,75,87,255))
