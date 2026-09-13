# Design coverage

All 50 audited skins and six generic chest templates use the dark visual language. Painted controls are used where audited action slots permit them. Native selection, storage, inspection, crafting and configuration-defined content remain visible and keep their original slot positions.

Crafting preserves its recipe controls and uses no outside frame. Chest frames add only noninteractive decoration outside the container. A generated guide proves layout composition, not live game interaction.

| Skin | Painted regions | Native cells | Outside layers | Constraint |
|---|---:|---:|---:|---|
| economy_hub | 8 | 0 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| auction_confirm | 2 | 1 | 1 | Fixed native display item may move within free native top cells. Original logical source and one-item capacity stay fixed; no pagination change. |
| trade_money | 3 | 0 | 0 | Every painted cell dispatches its bound original action; live item content remains native. |
| trade_idle | 3 | 40 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| trade_self_ready | 3 | 40 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| trade_other_ready | 3 | 40 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| trade_both_ready | 3 | 40 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| auction_duration | 6 | 0 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| ticket_valid | 2 | 1 | 1 | Fixed native display item may move within free native top cells. Original logical source and one-item capacity stay fixed; no pagination change. |
| ticket_invalid | 2 | 1 | 1 | Fixed native display item may move within free native top cells. Original logical source and one-item capacity stay fixed; no pagination change. |
| chest_shop_settings | 5 | 0 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| chest_shop_upgrade | 8 | 0 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| chest_shop_upgrade_confirm | 8 | 0 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| chest_shop_upgrade_disabled | 8 | 0 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| chest_shop_buy | 8 | 0 | 1 | Preset slots are packed dynamically. Option numbers identify displayed choices, never a fixed item count or fraction. All amounts remain in original item names and lore. |
| chest_shop_sell | 8 | 0 | 1 | Preset slots are packed dynamically. Option numbers identify displayed choices, never a fixed item count or fraction. All amounts remain in original item names and lore. |
| chest_shop_listing_enabled | 13 | 0 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| chest_shop_listing_disabled | 13 | 0 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| auction_house | 9 | 28 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| auction_search | 9 | 28 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| auction_mine | 9 | 28 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| auction_watchlist | 3 | 28 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| chest_shop_ads | 6 | 28 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| chest_shop_search | 6 | 28 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| economy_log | 3 | 28 | 1 | Every painted cell dispatches its bound original action; live item content remains native. |
| chest_shop | 3 | 24 | 1 | All 24 listing cells stay native. Existing right-column controls are painted one-cell icons; larger controls would consume real listings. |
| chest_shop_owner | 3 | 24 | 1 | All 24 listing cells stay native. Existing right-column controls are painted one-cell icons; larger controls would consume real listings. |
| admin_shop_categories | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| admin_shop_listings | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| admin_shop_search | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| admin_shop_configured | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| prefixes_1 | 0 | 9 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| prefixes_2 | 0 | 18 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| prefixes_3 | 0 | 27 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| prefixes_4 | 0 | 36 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| prefixes_5 | 0 | 45 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| prefixes_6 | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| guild_bank_select_1 | 0 | 9 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| guild_bank_select_3 | 0 | 27 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| guild_bank_1 | 0 | 9 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| guild_bank_2 | 0 | 18 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| guild_bank_3 | 0 | 27 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| guild_bank_4 | 0 | 36 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| guild_bank_5 | 0 | 45 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| guild_bank_6 | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| invsee_online | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| invsee_offline | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| trashcan | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| ender_chest | 0 | 27 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| crafting | 0 | 10 | 0 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| template_chest_1 | 0 | 9 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| template_chest_2 | 0 | 18 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| template_chest_3 | 0 | 27 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| template_chest_4 | 0 | 36 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| template_chest_5 | 0 | 45 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
| template_chest_6 | 0 | 54 | 1 | Native content and configuration-defined selection/storage slots are preserved. Only framing changes; no callback is invented. |
