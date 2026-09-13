# Controls, artwork, and preview behavior

This guide follows Quasar's existing callbacks. The machine-readable companion is [control-map.json](../manifests/control-map.json), containing 30 screen keys, native item choices, slot numbers, guards, transitions, and source references. It was produced by direct source inspection; it does not certify live gameplay testing. Its `preview_implementation` metadata records the implemented demonstration scope. Per-control `preview_proposal` fields describe intended demonstrations and are not a claim that every production branch is simulated.

Slots below are **zero-based top-container indices**. Painted frames and labels describe the native item controls. The callback remains on the original slot; painting a larger button does not enlarge its hitbox. Icons, stack counts, hover feedback, current prices, names, and state-specific lore remain native. Permanently empty protected space can carry explanatory panels. All possible live slots remain transparent; arbitrary configured admin-shop entries and storage need all their item windows.

Preview amounts, listings, player names, privacy, and readiness must be clearly labeled examples. Demonstrations may navigate between example screens, change example values, and report simulated outcomes. They must not buy, sell, transfer items, teleport, grant tickets, change player preferences, or invoke production commands. A command-help control should show its guidance and close, just as the actual callback does. A read-only item must not become a navigation button merely to make a demonstration busier.

## Implemented preview scope

InventoryDebug now provides immutable **left-click teaching fixtures** for representative navigation, auction pages/confirmation/return, shop and owner-settings routes, listing enable/buy/sell flags, quantity selection, upgrade selection/deselection, privacy and notifications, local-trade readiness, offered-money adjustment, and ticket confirm/cancel. Conditional items are omitted where the selected fixture lacks that production control. Close callbacks close the preview; `/invdebug quasar resume` is a separate demonstration command.

Right clicks and shift-click variants are described but suppressed. Numeric changes use the actual left-click step of 10, with clearly identified smaller example bounds for quantity. Numeric listing prices, full upgrade bid/fee calculations, real transactions, permission/service integration, and other unmodeled catalog actions provide explanation only. A representative upgrade selection assumes affordability; the disabled key is a separately inspectable fixture. Locked example trade items do not emulate ownership transfer. The model has no Quasar gameplay API access, and the preview container suppresses native item movement. Automated checks and independent source review do not establish in-game rendering or actual production transaction behavior.

## Auction house

`auction_house`, `auction_search`, and `auction_mine` share the same list controls and preserve their source list and page when refreshing. Items occupy sequential slots 0–44. A buyer clicks a live listing to open `auction_confirm`. A moderator uses **left click** to buy or **shift-right click** to disable. An owner uses **shift-right click** to recover an active listing; an expired or inactive owned listing is recovered by clicking. Recovery/disable refreshes the same list and page. These actor-specific actions must not be combined into one unconditional “Buy” button.

| Slot | Native control | Actual effect |
| --- | --- | --- |
| 45 | Arrow: Previous Page | Previous page, only if page > 0 |
| 46 | Gold ingot: Balance | Read-only current balance |
| 47 | Chest: My Listings | Opens `auction_mine`; shift-right recovers all and closes; no-listings branch gives command help and closes |
| 48 | Compass: Search | Prints `/ah search <query>` guidance and closes |
| 49 | Barrier: Close | Closes |
| 50 | Emerald: Sell Item | Prints `/ah sell <price> [count]` guidance and closes |
| 51 | Observer: My Watchlist | Opens `auction_watchlist`; empty-watchlist branch gives `/ah watch <item>` help and closes |
| 52 | Bell: Notifications | Toggles the saved preference and refreshes the same list/page |
| 53 | Arrow: Next Page | Next page, only when more entries exist |

Slot 47 is omitted when every entry is owned by the viewer. The source uses `allMatch`, so the empty-list case also omits it. Search and Sell do not open text-entry or item-entry forms. There is no built-in Back-to-hub control. Source: [list callbacks](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/AuctionHouseSGui.java#L57).

`auction_confirm` is a six-row chest with exactly three live positions:

| Slot | Native control | Actual effect / artwork wording |
| --- | --- | --- |
| 20 | Selected listing, displayed count 1 | Read-only; lore still carries actual quantity, seller, expiry, and price. Use **Review purchase** panel text. |
| 24 | Lime dye: Confirm Purchase | Cooldown check, purchase attempt, then returns to the captured list key and page. Use **Confirm**. |
| 53 | Barrier: Close | Closes. Use **Close**, not Back. |

There is **no separate Back or Cancel-return callback** on this screen. A simulated confirmation should return to its saved source list/page. The real callback also returns there after a failed purchase attempt. Source: [confirmation and purchase](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/AuctionHouseSGui.java#L279).

`auction_watchlist` shows up to 45 native watched-item icons at 0–44. Clicking one stops watching it, then refreshes or closes if the list becomes empty. Barrier 53 closes. It has no pagination and no Back button. Source: [watchlist](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/AuctionHouseSGui.java#L229).

`auction_duration` uses clocks at 11–15, with stack counts matching the days. The slots are **1 day / 1%**, **3 days / 5%**, **7 days / 15%**, **12 days / 20%**, and **15 days / 30%**. A click closes and calls the existing sale command with the captured arguments and selected duration. Barrier 8 only closes. These are listing-duration choices, not pagination or quantity controls. Sources: [duration callbacks](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/AHSelectTimeToSellSGui.java#L19), [duration enum](../worktrees/1.21/common/src/main/java/anar4732/quasar/storage/shop/QAHData.java#L95).

## Admin shop

`admin_shop_categories` means the configured main page. It can contain listings as well as category links. A secondary page containing only listings/tickets uses `admin_shop_listings`; a mixed secondary page uses `admin_shop_configured`. Search uses `admin_shop_search` and sequential result slots 0–44.

Configured entry slots are operator-authored. There is no universal fixed “Blocks” slot, Back button, details page, price editor, settings menu, or purchase-confirmation screen. An example category at slot 11 is valid **only as an explicitly labeled example configuration**. An operator can create a Back-like page link at an arbitrary position, but generic artwork cannot promise its presence.

| Entry/control | Actual behavior |
| --- | --- |
| Configured page link | Uses the configured icon, destination page name/description, and opens that page |
| Listing | **Left click buys immediately; right click sells immediately**, when enabled; stays on the same page |
| Ticket entry | Left click buys immediately, when enabled |
| Info entry / banned item / invalid entry | Read-only; invalid entry is a barrier with “Please report to staff” lore |
| 45 / 53 arrows | Previous/next **search result** page, conditionally present |
| 48 compass | `/shop search <query>` guidance, then closes |
| 49 barrier | Closes |
| 50 emerald, operators only | “Add Item” prints README configuration guidance and closes; it does not open an editor |

Fixed controls 48/49 and operator 50 are assigned after configured entries, so they can overwrite configured positions. Art should use a general **Browse / left buy / right sell** legend in safe margins, while the native lore specifies whether each individual entry supports those actions. Sources: [page selection and fixed controls](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/AdminShopSGui.java#L35), [entry semantics](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/AdminShopSGui.java#L109).

## Chest-shop main and listing options

`chest_shop_owner` is selected for the owner; other viewers, including non-owner moderators, use `chest_shop`. Both use three rows. Barrier 8 closes and gold ingot 17 displays balance. At 26, the owner sees a **Comparator: Shop Options** leading to `chest_shop_settings`; other viewers see a **Compass: Search** that prints `/cs search <query>` and closes.

Listings fill free slots around those controls. Their original item icons and counts remain visible. Native lore states customer Buy Price, Sell Price, stock, availability, and the permitted click actions:

| Listing click | Actual transition |
| --- | --- |
| Left, shop selling enabled and sufficient stock | `chest_shop_buy` amount choices |
| Right, shop buying enabled | `chest_shop_sell` amount choices |
| Shift-right, owner or moderator | `chest_shop_listing_enabled` / `chest_shop_listing_disabled` |
| Click disabled listing, owner or moderator | Listing options |

A regular click must not become owner settings in a demonstration. Source: [chest-shop main](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/ChestShopSGui.java#L52).

The two `chest_shop_listing_*` variants use five rows:

| Slot(s) | Native control | Actual effect |
| --- | --- | --- |
| 8 | Barrier: Back | Main screen of the same shop |
| 19 | Oak sign: Stats | Read-only total sold/bought |
| 20 | Chest: Stock | Read-only linked-container stock |
| 22 | Apple: Quantity | Read-only quantity per transaction |
| 13 / 31 | Arrows above/below Quantity | Increase/decrease quantity, clamp 1–10000, save immediately |
| 23 | Gold ingot / red dye: Sell Price | Toggle whether the shop sells to customers; customer **pays** this price |
| 14 / 32 | Arrows above/below Sell Price | Adjust enabled sell price, save immediately |
| 24 | Gold ingot / red dye: Buy Price | Toggle whether the shop buys from customers; customer **receives** this price |
| 15 / 33 | Arrows above/below Buy Price | Adjust enabled buy price, save immediately |
| 25 | Red dye: Disable / lime dye: Enable | Toggle listing state and switch the corresponding skin key |

All numeric arrows use **right ±1, left ±10, shift-right ±100, shift-left ±1000**, then clamp to the allowed range. Other click types are ignored. Disabled buy/sell prices have no arrows. Enabling starts at price 1; disabling sets price -1. Tickets cannot be bought by a chest shop; opening their options forces buying off. Changes save immediately, so Back is not “discard changes.” Sources: [listing options](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/ChestShopSGui.java#L178), [shared numeric controls](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/ChestShopSGui.java#L313).

## Chest-shop amount choices

`chest_shop_buy` and `chest_shop_sell` use three rows. Barrier 8 returns to the shop. If more than one lot is available, item 10 is **Buy N / Sell N**, with arrows 1 and 19 selecting the number of lots. The arrows change selection only. Clicking the item executes the transaction attempt; there is no extra confirm button. Native item names show actual item counts, and lore carries Cost/Earnings and failure reasons.

Preset items are packed from slot 12 onward, so their meaning is conditional:

1. Append `floor(maxLots / 4)` if at least 16 lots are available.
2. Append `floor(maxLots / 3)` if at least 9 are available.
3. Append `floor(maxLots / 2)` if at least 4 are available.
4. Append the maximum (sell uses at least 1 for its unavailable example).

For a fixture with 16 lots, slots 12/13/14/15 represent 4/5/8/16 lots. For four lots, slots 12/13 represent 2/4 lots. **Do not paint fixed fraction labels at each preset slot.** Use **Buy options** / **Sell options** and retain each native item's truthful amount. Unaffordable or insufficient-item/stock items have explanation lore and no purchase callback.

After buying, the real callback returns to the main shop if less than one lot remains in stock; otherwise it refreshes the buy screen. After selling it refreshes the sell screen. A fixture can demonstrate these paths with example state only. Sources: [amount-screen construction](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/ChestShopSGui.java#L350), [transaction items](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/ChestShopSGui.java#L588).

## Chest-shop settings and upgrade

`chest_shop_settings` has fixed controls: **Back 8** to main, read-only **Stats 10** (oak sign), **Premium Tier 12** (diamond) to upgrade options, **Rename Shop 13** (anvil), and **Refresh Listings 14** (clock). Rename sends a clickable chat command suggestion and closes. Refresh syncs listings with the linked container, may remove depleted listings, reports the count, and closes. Neither opens a text form or confirmation screen. Source: [shop settings](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/ChestShopSGui.java#L425).

All three upgrade keys share the three-row layout:

| Slot(s) | Native control | Actual effect |
| --- | --- | --- |
| 8 | Barrier: Back | Return to settings without applying pending changes |
| 10 | Emerald: Bid | Read-only selected monthly bid and balance; base tier says bidding unavailable |
| 1 / 19 | Bid arrows | Adjust pending bid only, 0–balance, for premium tiers |
| 12 / 13 / 14 | Iron / gold / diamond block | Select tier 1/2/3; clicking selected tier resets to tier 0 |
| 16 | Lime dye: Confirm | Apply pending tier/bid and return to settings, only when affordable |

`chest_shop_upgrade` has no pending changes and no slot-16 item. `chest_shop_upgrade_confirm` has an affordable pending change and a live Confirm. `chest_shop_upgrade_disabled` shows the same lime-dye item with red name and unaffordable lore **without a callback**. Native lore carries the actual upgrade fee, subscription, bid, and resulting cost. Artwork should not turn the disabled variant into an enabled-looking button. Source: [upgrade state and callbacks](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/ChestShopSGui.java#L491).

## Chest-shop advertisements and search

`chest_shop_ads` and `chest_shop_search` use six rows, listings 0–44, conditional arrows 45/53, read-only balance 46, Search-help-and-close 48, and Close 49. Emerald 50, **Create Your Chest Shop**, is read-only sign-template guidance, not a create wizard.

A tier-3 listing in the same dimension opens its remote shop. Its lore says right click, although the callback does not filter the click type. Otherwise, operator or tier-2+ access teleports and closes. Lower-tier advertisements can be entirely read-only. Use an explicitly identified tier-3 same-dimension example when demonstrating navigation into a shop. A teleport preview should only report simulation and close. Source: [advertisement callbacks](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/ChestShopAdsSGui.java#L47).

## Economy hub

`economy_hub` uses three rows. The seven-item middle row includes real controls and read-only information:

| Slot | Native item / title | Actual effect |
| --- | --- | --- |
| 8 | Barrier: Close | Close |
| 10 | Gold ingot: Balance | Read-only balance, salary, and `/eco pay` guidance |
| 11 | Name tag: Auction House | `auction_house` |
| 12 | Ender chest: Admin Shop | `admin_shop_categories` if configured shop is nonempty |
| 13 | Chest: Chest Shops | `chest_shop_ads` |
| 14 | Book: Economy Log | `economy_log` if history fetch succeeds and is nonempty |
| 15 | Lime/red concrete: Balance Privacy | Toggle Public/Private and reopen hub |
| 16 | Player head: Your Top Balance Rank | Read-only Private / rank / Unranked; not a leaderboard button |

The privacy example should update the slot-16 information consistently. The Balance or Rank display should not act as an invented “Pay” or “Leaderboard” screen. Source: [economy hub](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/EcoHubSGui.java#L20).

## Trade and offered-money editor

The four six-row keys `trade_idle`, `trade_self_ready`, `trade_other_ready`, and `trade_both_ready` reflect the viewer's ready state and the other player's ready state. The left four columns of rows 0–4 are real offered-item slots. The right four columns of those rows are immutable incoming-item slots. A preview should show locked example items; it must not become a second real inventory or accept/extract player items.

| Slot | Native control | Actual effect |
| --- | --- | --- |
| 13 | Paper when neither ready; orange dye when one; green dye when both | Toggle the viewer's ready state; lore identifies who is ready |
| 47 | Emerald: Your Offered Money | Open `trade_money` if balance > 0; otherwise show no-money message and stay |
| 52 | Emerald: Money You Will Receive | Read-only; only present when incoming money > 0 |

For a local trade, `idle → self_ready` and `self_ready → idle` follow clicks on 13. Clicking 13 while `other_ready` makes both ready and **applies the trade immediately**. A truthful harmless demo reports completion and closes; it must not invent a second confirmation stage. A directly selected `trade_both_ready` visual fixture can demonstrate the styling, but is not a guaranteed long-lived local screen. Its ready-toggle click would turn the viewer off, yielding `other_ready`. Remote trade status also depends on network updates.

There is no explicit Cancel/Close item. Closing invokes existing trade cancellation behavior. Item changes reset readiness. Separators are decorative, not buttons. Source: [trade slots and callbacks](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/TradeSGui.java#L24).

`trade_money` is a **3×3 dispenser container**, with only **Increase 1**, **Offered Money 4**, and **Decrease 7**. Arrows use the same right/left/shift step mapping as chest-shop numeric fields, clamped from 0 to balance. They update the proposed trade-bank money and refresh. The center emerald's name shows the live amount, its lore shows balance, and clicking it confirms and returns. Local return resets both ready states; remote return opens with other-side readiness false and sends an update. There is no separate Back/Cancel slot. The themed title is artwork-only for stable centered alignment, so the center item's dynamic information must stay clear. Source: [offered-money editor](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/TradeSGui.java#L169).

## Ticket redemption

`ticket_valid` and `ticket_invalid` are six-row chests. Slot 22 is the actual ticket display. **Red concrete 29: Cancel** plays a click sound and closes. In the valid variant, **lime concrete 33: Confirm** calls the existing ticket-use check and closes. Native lore describes the grant, scope, duration, or permanent status. A preview may show a simulated redemption and close; it must never grant a rank/prefix or consume a ticket.

The invalid variant has **no item or callback at 33**. Keep Confirm absent; a fake barrier button or enabled-looking painted confirmation changes the apparent flow. The 26 perimeter filler slots are decorative and become protected empty elements in themed mode. Source: [ticket callbacks and descriptions](../worktrees/1.21/common/src/main/java/anar4732/quasar/sgui/TicketRedeemSGui.java#L27).

## Confirmed sparse live-slot unions

These sets include every possible native item, information item, and callback carrier across states. Keeping a window for an absent conditional item is safe. Painting an explanatory panel across one of these slots is not.

| Key family | Live-slot union |
| --- | --- |
| `auction_confirm` | 20, 24, 53 |
| `auction_duration` | 8, 11–15 |
| `chest_shop_listing_*` | 8, 13–15, 19, 20, 22–25, 31–33 |
| `chest_shop_buy`, `chest_shop_sell` | 1, 8, 10, 12–15, 19 |
| `chest_shop_settings` | 8, 10, 12–14 |
| `chest_shop_upgrade*` | 1, 8, 10, 12–14, 16, 19 |
| `economy_hub` | 8, 10–16 |
| `trade_money` | 1, 4, 7 |
| `ticket_*` | 22, 29, 33 (33 valid-only) |

Native storage, arbitrary configured pages, and dense listing views retain all potential item windows. This is an artwork boundary, not permission to alter callback logic or add controls.
