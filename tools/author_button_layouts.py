"""Author the reviewed first-stage redesign maps; normal pack builds do not run this."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def button(id,source,slots,label,role='action',style='secondary',lines=None):
    b=dict(id=id,sourceSlot=source,slots=slots,label=label,role=role,style=style)
    if lines:b['lines']=lines
    return b

screens={
 'economy_hub':dict(contentSlots=[],buttons=[
    button('auction',11,[0,1,2,9,10,11],'Auction House',style='primary',lines=['AUCTION','HOUSE']),
    button('admin_shop',12,[6,7,8,15,16,17],'Admin Shop',style='primary',lines=['ADMIN','SHOP']),
    button('balance',10,[3,4,5],'Balance','info'),
    button('privacy',15,[12,13],'Privacy'),
    button('rank',16,[14],'Rank','info'),
    button('chest_shops',13,[18,19,20],'Chest Shops',lines=['CHEST','SHOPS']),
    button('history',14,[21,22,23],'History'),
    button('close',8,[24,25,26],'Close',style='danger')]),
 'auction_confirm':dict(contentSlots=[20],buttons=[
    button('confirm',24,[23,24,25,32,33,34],'Confirm Purchase',style='primary',lines=['CONFIRM','PURCHASE']),
    button('close',53,[48,49,50,51,52,53],'Close',style='secondary')]),
 'trade_money':dict(contentSlots=[],buttons=[
    button('increase',1,[0,1,2],'Increase',style='primary'),
    button('return',4,[3,4,5],'Return'),
    button('decrease',7,[6,7,8],'Decrease')])}
offers=[row*9+col for row in range(5) for col in [0,1,2,3,5,6,7,8]]
for state in ['idle','self_ready','other_ready','both_ready']:
    screens['trade_'+state]=dict(contentSlots=offers,buttons=[
        button('own_money',47,[45,46,47],'Your Money',lines=['YOUR','MONEY']),
        button('ready',13,[48,49,50],'Ready',style='primary'),
        button('other_money',52,[51,52,53],'Their Money','info',lines=['THEIR','MONEY'])])
    screens['trade_'+state]['defaultStates']={
        'ready':'selected' if state in ['self_ready','both_ready'] else 'normal',
        'other_money':'selected' if state in ['other_ready','both_ready'] else 'normal'}
data=dict(schemaVersion=1,carrier=dict(item='minecraft:paper',customModelData=194731,
    model='quasar_gui:item/button_carrier',restoreThreshold=194732,
    legacyInventoryDebug=dict(customModelData=1,restoreThreshold=2)),screens=screens,
    animation=dict(frames=['pulse_1','pulse_2','pulse_3'],ticksPerFrame=2,repeat=False,
        trigger='explicit server action/state feedback; never mouse hover',
        note='Font frames are separate glyphs, not PNG animation metadata. State changes do not authorize actions.'))
(ROOT/'manifests/button-layouts.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print('Authored',len(screens),'reviewed screen layouts')
