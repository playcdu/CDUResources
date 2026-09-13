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
screens['auction_duration']=dict(contentSlots=[],buttons=[
    button('one_day',11,[0,1,2],'1 Day'),button('three_days',12,[3,4,5],'3 Days'),
    button('seven_days',13,[6,7,8],'7 Days'),button('twelve_days',14,[9,10,11,12],'12 Days'),
    button('fifteen_days',15,[14,15,16,17],'15 Days'),button('close',8,[21,22,23,24,25,26],'Close',style='danger')])
for key in ['ticket_valid','ticket_invalid']:
    screens[key]=dict(contentSlots=[22],buttons=[
        button('cancel',29,[27,28,29,36,37,38],'Cancel',style='secondary'),
        button('redeem',33,[33,34,35,42,43,44],'Redeem Ticket',style='primary',lines=['REDEEM','TICKET'])],
        defaultStates={'redeem':'disabled' if key=='ticket_invalid' else 'normal'})
screens['chest_shop_settings']=dict(contentSlots=[],buttons=[
    button('back',8,[0,1],'Back'),button('stats',10,[2,3,4],'Stats','info'),
    button('upgrade',12,[5,6,7,8],'Upgrade',style='primary'),
    button('rename',13,[9,10,11,18,19,20],'Rename Shop',lines=['RENAME','SHOP']),
    button('refresh',14,[15,16,17,24,25,26],'Refresh Listings',lines=['REFRESH','LISTINGS'])])
for key in ['chest_shop_upgrade','chest_shop_upgrade_confirm','chest_shop_upgrade_disabled']:
    screens[key]=dict(contentSlots=[],buttons=[
        button('back',8,[0,1],'Back'),button('bid',10,[2,3,4],'Your Bid','info'),
        button('increase',1,[9,10],'More'),button('decrease',19,[18,19],'Less'),
        button('tier_1',12,[5,6],'Tier 1'),button('tier_2',13,[14,15],'Tier 2'),button('tier_3',14,[23,24],'Tier 3'),
        button('confirm',16,[7,8,16,17,25,26],'Apply',style='primary')],
        defaultStates={'confirm':'disabled' if key.endswith('disabled') else 'normal'})
for action in ['buy','sell']:
    screens['chest_shop_'+action]=dict(contentSlots=[],buttons=[
        button('back',8,[6,7,8],'Back'),button('increase',1,[0,1],'More'),button('decrease',19,[18,19],'Less'),
        button('selected_amount',10,[9,10,11,12],action.upper()+' NOW',style='primary'),
        button('preset_1',12,[3,4,5],'Option 1'),button('preset_2',13,[13,14],'Opt 2'),
        button('preset_3',14,[21,22,23],'Option 3'),button('preset_4',15,[24,25,26],'Option 4')],
        note='Preset slots are packed dynamically. Option numbers identify displayed choices, never a fixed item count or fraction. All amounts remain in original item names and lore.')
for key in ['chest_shop_listing_enabled','chest_shop_listing_disabled']:
    screens[key]=dict(contentSlots=[],buttons=[
        button('back',8,[0,1,2],'Back'),button('stats',19,[3,4,5],'Stats','info'),button('stock',20,[6,7,8],'Stock','info'),
        button('sell_more',14,[9,10,11],'Sell +'),button('sell_price',23,[18,19,20],'Sell Price'),button('sell_less',32,[27,28,29],'Sell -'),
        button('quantity_more',13,[12,13,14],'Qty +'),button('quantity',22,[21,22,23],'Quantity','info'),button('quantity_less',31,[30,31,32],'Qty -'),
        button('buy_more',15,[15,16,17],'Buy +'),button('buy_price',24,[24,25,26],'Buy Price'),button('buy_less',33,[33,34,35],'Buy -'),
        button('toggle',25,[39,40,41,42,43,44],'Enable Listing' if key.endswith('disabled') else 'Disable Listing',
            style='primary' if key.endswith('disabled') else 'danger')])
listing_slots=[row*9+col for row in range(1,5) for col in range(1,8)]
for key in ['auction_house','auction_search','auction_mine']:
    close=button('close',49,[53],'Close',style='danger');close['icon']='close'
    balance=button('balance',46,[9,18,27,36],'Balance','info');balance['icon']='balance'
    screens[key]=dict(contentSlots=listing_slots,
        contentRegion=dict(sourceSlots=list(range(45)),slots=listing_slots),buttons=[
        button('my_listings',47,[0,1,2],'My Items'),button('watchlist',51,[3,4,5],'Watch'),
        button('notifications',52,[6,7,8],'Alerts'),balance,
        button('previous',45,[45,46],'Prev'),button('search',48,[47,48],'Find'),
        button('sell',50,[49,50],'Sell',style='primary'),button('next',53,[51,52],'Next'),close],
        artLayers=[dict(id='market_frame',x=-40,y=-8,width=256,height=238,
            purpose='Noninteractive market frame and outside information; no click targets outside native slots')])
for key in ['auction_watchlist','chest_shop_ads','chest_shop_search','economy_log']:
    if key in ['chest_shop_ads','chest_shop_search']:
        close=button('close',49,[53],'Close',style='danger');close['icon']='close'
        balance=button('balance',46,[9,18,27,36],'Balance','info');balance['icon']='balance'
        controls=[balance,button('previous',45,[45,46],'Prev'),button('search',48,[47,48],'Find'),
            button('create_shop',50,[49,50],'Create','info'),button('next',53,[51,52],'Next'),close]
    else:
        controls=[button('previous',45,[45,46,47],'Previous'),
            button('close',53 if key=='auction_watchlist' else 49,[48,49,50],'Close',style='danger'),
            button('next',52 if key=='auction_watchlist' else 53,[51,52,53],'Next')]
    screens[key]=dict(contentSlots=listing_slots,contentRegion=dict(sourceSlots=list(range(45)),slots=listing_slots),
        buttons=controls,artLayers=[dict(id='market_frame',x=-40,y=-8,width=256,height=238,
            heading='CHEST SHOPS' if key.startswith('chest_shop') else 'WATCHLIST' if key=='auction_watchlist' else 'HISTORY',
            rightLines=['SEARCH','BROWSE','DETAILS'] if key.startswith('chest_shop') else ['REVIEW','PAGES','BELOW'],
            purpose='Noninteractive page frame and outside information; no click targets outside native slots')])
for key,source in [('auction_confirm',20),('ticket_valid',22),('ticket_invalid',22)]:
    screens[key]['contentRegion']=dict(sourceSlots=[source],slots=[source])
    screens[key]['note']='Fixed native display item may move within free native top cells. Original logical source and one-item capacity stay fixed; no pagination change.'
for key in ['chest_shop','chest_shop_owner']:
    close=button('close',8,[8],'Close',style='danger');close['icon']='close'
    balance=button('balance',17,[17],'Balance','info');balance['icon']='balance'
    option=button('options',26,[26],'Settings' if key.endswith('owner') else 'Search')
    option['icon']='settings' if key.endswith('owner') else 'search'
    option['sourceControl']='Shop Options' if key.endswith('owner') else 'Search'
    screens[key]=dict(contentSlots=[i for i in range(27) if i not in [8,17,26]],buttons=[close,balance,option],
        note='All 24 listing cells stay native. Existing right-column controls are painted one-cell icons; larger controls would consume real listings.')
skins=json.loads((ROOT/'manifests/skins.json').read_text())['skins']
layouts=json.loads((ROOT/'manifests/layouts.json').read_text())['layouts']
for key,skin in skins.items():
    screen=screens.setdefault(key,dict(contentSlots=skin['liveSlots'],buttons=[],
        note='Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented.'))
    screen['presentation']='painted_controls' if screen['buttons'] else 'native_content_preserved'
    if skin['layout'].startswith('chest_') and not screen.get('artLayers'):
        family=skin['family'].replace('_',' ').upper()
        screen['artLayers']=[dict(id='menu_frame',x=-40,y=-8,width=256,height=layouts[skin['layout']]['height']+16,
            heading=family,leftHeading=family.split()[0],rightLines=['NATIVE','CONTENT','VISIBLE'] if not screen['buttons'] else ['HOVER','FOR','DETAILS'],
            purpose='Noninteractive outer frame; native content, title and inventory remain unobscured')]
data=dict(schemaVersion=1,carrier=dict(item='minecraft:paper',customModelData=194731,
    model='quasar_gui:item/button_carrier',restoreThreshold=194732,
    legacyInventoryDebug=dict(customModelData=1,restoreThreshold=2)),screens=screens,
    animation=dict(frames=['pulse_1','pulse_2','pulse_3'],ticksPerFrame=4,repeat=False,
        trigger='explicit server action/state feedback; never mouse hover',
        note='Font frames are separate glyphs, not PNG animation metadata. State changes do not authorize actions.'))
(ROOT/'manifests/button-layouts.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print('Authored',len(screens),'reviewed screen layouts')
