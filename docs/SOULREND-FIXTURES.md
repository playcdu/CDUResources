# Soulrend fixture gallery

The fixture gallery is a set of self-contained HTML pages that show every
texture of the Soulrend dark-fantasy replacement (56 menu backgrounds, 157
painted buttons in six states each, 54 outer frames) so the artwork can be
reviewed in claude.ai without checking out `art/soulrend-theme`. Each page is
one HTML file with every image embedded as a PNG data URI and no external
resources. It is the Soulrend counterpart of the cozy gallery described in
[COZY-FIXTURES.md](COZY-FIXTURES.md); the look itself is defined in
[SOULREND-STYLE-GUIDE.md](SOULREND-STYLE-GUIDE.md).

> **Schematic composites, not gameplay screenshots.** Every picture is drawn by
> [`tools/cozy/preview.py`](../tools/cozy/preview.py) (the theme-agnostic
> preview tool, run with the Soulrend theme) from the pack-source PNGs,
> layered the way the client layers them. The grey item squares (and their
> stack counts), the flat slot backdrop standing in for the vanilla container,
> the dimmed world colour, the titles and the "Inventory" label are synthetic.
> Only the menu background, buttons and frames are real pack textures.

## Generating

```sh
python tools/cozy/build_fixtures.py --theme soulrend          # build every page into evidence/soulrend-fixtures/, then check them
python tools/cozy/build_fixtures.py --theme soulrend --check  # re-check pages already built
```

`QUASAR_GUI_THEME=soulrend` does the same as `--theme soulrend`; the flag wins.
Use the pinned interpreter
`C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
and run from the repository root on `art/soulrend-theme`: the pages always show
the textures in pack-source on the current checkout, so building on another
branch would show that branch's art under Soulrend titles. Output goes to
`evidence/soulrend-fixtures/` (gitignored); the build is deterministic for a
given checkout. It reads pack-source and runs `git show` only, and warns if
textures have uncommitted changes. The check step confirms each page is under
16 MB, has balanced tags, starts with `<title>`, carries the schematic caveat,
embeds only PNG data URIs, keeps colour literals inside the token blocks at the
top of `<style>`, and links only to in-page anchors or `{{URL:…}}` tokens.

Under `--theme soulrend` the builder swaps in the Soulrend palette
(`tools/soulrend/palette.py`), lettering (`tools/soulrend/lettering.py`),
schematic title lettering, page colour tokens (an umber/vellum light mode and
an ink/umber dark mode), titles and URL map; everything else is shared with the
cozy gallery. Images are stored as exact palette PNGs (lossless; checked pixel
for pixel against the RGB render), which keeps every page under 1 MB. If a
family page ever passes the 14 MB budget, the builder splits it into
`family-<family>-1.html`, `-2.html`, … using the groups in `SPLIT_GROUPS`; no
Soulrend family page comes close (the largest, chest_shop, is about 0.95 MB).

## Page contents

- **Index** (`index.html`, "Soulrend GUI Fixtures"): a "what this is" note
  saying the pictures are schematic composites from the preview tool, not
  gameplay screenshots; links to every family page and the before/after page;
  all 56 skins as cards grouped by family (economy, auction, chest_shop,
  trade, ticket, admin_shop, guild_bank, prefixes, invsee, utility), each with
  a 1x composite scaled 2x nearest-neighbour, the skin key, layout and size,
  button count, frame layer(s) and presentation, plus the family motif; the
  36-colour master palette as swatches grouped by its 11 ramps (ink, iron,
  stone, umber, vellum, blood, ember, soul, gold, moss, void) with names and
  RGB values, and the semantic aliases (`OUTLINE`, `OUTLINE_DEEP`,
  `TEXT_DARK`, `TEXT_LIGHT`, `TEXT_GOLD`, `SHADOW`, `GLOW`, `SOUL_GLOW`,
  `TITLE_BAND`, `SHEET`); the GRAVEN / RUNE typeface specimen with its spec
  (GRAVEN cap 7 / x 5 / desc 2 / track 1, a thin medieval serif in mixed case;
  RUNE cap 5 / track 1, carved capitals) and the `lettering.specimen()` image
  at 3x.
- **Family pages** (`family-<family>.html`, "Soulrend <Family> Family"): a back
  link, a table of contents, and for every skin in the family:
  1. the composite at 3x with schematic sample items and a sample title;
  2. a long-title / full-content composite at 3x (every well filled, an
     over-long title clipped to the text-safe width);
  3. every button in all six states (normal, disabled, selected, pulse_1,
     pulse_2, pulse_3) at 4x over its crop of the background, labelled with id,
     size and position, style, role, label (and lettering), icon and default
     state;
  4. each outer frame layer alone on a neutral mid-grey backdrop at 3x;
  5. the raw background at 3x on a grey checker with every alpha-zero
     clearance outlined in magenta.
- **Before / after** (`before-after.html`, "Midnight vs Soulrend"): 20
  representative screens covering all ten families. Each pair is tagged
  "Baseline · midnight" (left, or upper on narrow screens) and
  "Soulrend · replacement" (right, or lower), both at 3x. The baseline
  textures are the midnight placeholder artwork, read with `git show` from
  commit **`037c5ef7cb5dbe6fe5ab04dadcb2d2c44cd0372e`** into a temporary
  directory laid out like `pack-source/assets/quasar_gui/textures/` and
  rendered through `preview.render(key, overrides_dir=…)`; the build refuses to
  run if any baseline texture of those screens is missing, so the two sides
  never mix artwork. Both sides use the same schematic items, title and default
  button states, so only the texture PNGs differ. Screens: economy_hub,
  economy_log, auction_house, auction_confirm, auction_duration, chest_shop,
  chest_shop_listing_enabled, chest_shop_buy, trade_self_ready, trade_money,
  ticket_valid, ticket_invalid, admin_shop_categories, guild_bank_3,
  prefixes_6, invsee_offline, trashcan, ender_chest, crafting,
  template_chest_6.

Cross-page links are generated as `{{URL:<page>}}` placeholders (optionally
followed by `#<skin>`) and resolved at build time from the tracked map
`tools/soulrend/fixture_urls.json` (`{"index": "https://claude.ai/artifact/…",
"family-economy": "…", …}`). Tokens missing from the map stay literal, so an
empty map leaves every link as a placeholder; after publishing, record the
URLs there and rebuild.

## Pages

| Page | File | Title | Contents | URL |
|---|---|---|---|---|
| Index | `index.html` | Soulrend GUI Fixtures | 56 skin cards, palette, typeface | https://claude.ai/artifact/HNmxaaZfjfZESjMJ7JjVFm |
| Economy | `family-economy.html` | Soulrend Economy Family | 2 skins, 11 buttons | https://claude.ai/artifact/MDwBbTEGo7uirddRD2GZrb |
| Auction | `family-auction.html` | Soulrend Auction Family | 6 skins, 38 buttons | https://claude.ai/artifact/E6qqzsEi5o2JxJou33ggdL |
| Chest shop | `family-chest_shop.html` | Soulrend Chest Shop Family | 12 skins, 89 buttons | https://claude.ai/artifact/8bMeH3Z8rHn2z97rZkHGe3 |
| Trade | `family-trade.html` | Soulrend Trade Family | 5 skins, 15 buttons | https://claude.ai/artifact/NwrRQP7HEtUwatufVR6zCk |
| Ticket | `family-ticket.html` | Soulrend Ticket Family | 2 skins, 4 buttons | https://claude.ai/artifact/QYtxgEAQu2gVZiDSHGu2Ay |
| Admin shop | `family-admin_shop.html` | Soulrend Admin Shop Family | 4 skins, native content | https://claude.ai/artifact/U6xXQtGUiRz1LvaqDwAvS9 |
| Guild bank | `family-guild_bank.html` | Soulrend Guild Bank Family | 8 skins, native content | https://claude.ai/artifact/VbzChSy9EEYjuTxjC1MzbN |
| Prefixes | `family-prefixes.html` | Soulrend Prefixes Family | 6 skins, native content | https://claude.ai/artifact/3b75iry1F1yetZRoMp6eJr |
| Invsee | `family-invsee.html` | Soulrend Invsee Family | 2 skins, native content | https://claude.ai/artifact/WXnHBUYkRZC52g9ixkDYtt |
| Utility | `family-utility.html` | Soulrend Utility Family | 9 skins, native content | https://claude.ai/artifact/QCyANRvoW1jokmJREQbSK5 |
| Before / after | `before-after.html` | Midnight vs Soulrend | 20 screens, baseline `037c5ef` vs Soulrend | https://claude.ai/artifact/UGq4vU4SEvKPxpiHrjuUy1 |

Licence: generator code MIT; artwork as in the rest of the repository.
