# Cozy fixture gallery

The fixture gallery is a set of self-contained HTML pages that show every
texture of the cozy replacement (60 menu backgrounds, 169 painted buttons in six
states each, 58 outer frames) so the artwork can be reviewed in claude.ai
without checking out `art/cozy-theme`. Each page is one HTML file with every
image embedded as a PNG data URI and no external resources.

> **Schematic composites, not gameplay screenshots.** Every picture is drawn by
> [`tools/cozy/preview.py`](../tools/cozy/preview.py) from the pack-source PNGs,
> layered the way the client layers them. The grey item squares (and their
> stack counts), the flat slot backdrop standing in for the vanilla container,
> the dimmed world colour, the titles and the "Inventory" label are synthetic.
> Only the menu background, buttons and frames are real pack textures.

## Generating

```sh
python tools/cozy/build_fixtures.py          # build every page into evidence/cozy-fixtures/, then check them
python tools/cozy/build_fixtures.py --check  # re-check pages already built
```

Use the pinned interpreter
`C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
and run from the repository root. Output goes to `evidence/cozy-fixtures/`
(gitignored); the build is deterministic for a given checkout. It reads
pack-source and runs `git show` only, and warns if textures have uncommitted
changes. The check step confirms each page is under 16 MB, has balanced tags,
starts with `<title>`, carries the schematic caveat, embeds only PNG data URIs
and links only to in-page anchors or `{{URL:…}}` tokens.

Images are stored as exact palette PNGs (lossless; checked pixel for pixel
against the RGB render), which keeps every page well under 1 MB. If a family
page ever passes the 14 MB budget, the builder splits it into
`family-<family>-1.html`, `-2.html`, … using the groups in `SPLIT_GROUPS`
(for example chest_shop: storefront and browse / listing and trading /
settings and upgrades) and links the parts to each other.

## Page contents

- **Index** (`index.html`, "Cozy GUI Fixtures"): a "what this is" note; links
  to every family page and the before/after page; all 60 skins as cards grouped
  by family (economy, auction, chest_shop, trade, ticket, admin_shop,
  guild_bank, prefixes, invsee, plot, utility), each with a 1x composite scaled 2x
  nearest-neighbour, the skin key, layout and size, button count, frame layer(s)
  and presentation; the 34-colour master palette as swatches grouped by ramp
  with names and RGB; the HEARTH / SPRIG typeface specimen with its spec
  (HEARTH cap 7 / x 5 / desc 2 / track 1; SPRIG cap 5 / track 1, uppercase).
- **Family pages** (`family-<family>.html`, "Cozy <Family> Family"): a back
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
- **Before / after** (`before-after.html`, "Midnight vs Cozy"): 20
  representative screens covering all ten families, each with the baseline
  midnight artwork beside the cozy replacement at 3x. The baseline textures are
  read with `git show` from commit
  `037c5ef7cb5dbe6fe5ab04dadcb2d2c44cd0372e` into a temporary directory laid
  out like `pack-source/assets/quasar_gui/textures/` and rendered through
  `preview.render(key, overrides_dir=…)`; the build refuses to run if any
  baseline texture of those screens is missing, so the two sides never mix
  artwork. Both sides use the same schematic items, title and default button
  states. Screens: economy_hub, economy_log, auction_house, auction_confirm,
  auction_duration, chest_shop, chest_shop_listing_enabled, chest_shop_buy,
  trade_self_ready, trade_money, ticket_valid, ticket_invalid,
  admin_shop_categories, guild_bank_3, prefixes_6, invsee_offline, trashcan,
  ender_chest, crafting, template_chest_6.

Cross-page links are generated as `{{URL:<page>}}` placeholders (optionally
followed by `#<skin>`) and resolved at build time from the tracked map
`tools/cozy/fixture_urls.json`, which records the published artifact URLs.

## Pages

| Page | File | Title | Contents | URL |
|---|---|---|---|---|
| Index | `index.html` | Cozy GUI Fixtures | 56 skin cards, palette, typeface | https://claude.ai/artifact/2q9qWFHGU16QNXfnnGrEUs |
| Economy | `family-economy.html` | Cozy Economy Family | 2 skins, 11 buttons | https://claude.ai/artifact/JNxtEgTga1tcL3U1XtsJGd |
| Auction | `family-auction.html` | Cozy Auction Family | 6 skins, 38 buttons | https://claude.ai/artifact/DG1UXUcxjxjmMepo1L48in |
| Chest shop | `family-chest_shop.html` | Cozy Chest Shop Family | 12 skins, 89 buttons | https://claude.ai/artifact/UKFLffziCjvmTkKnUw6LKQ |
| Trade | `family-trade.html` | Cozy Trade Family | 5 skins, 15 buttons | https://claude.ai/artifact/Lm4u3kEDR6aYJ9VcRcZX5A |
| Ticket | `family-ticket.html` | Cozy Ticket Family | 2 skins, 4 buttons | https://claude.ai/artifact/64kYaHcdfDbMTzddH3CPZg |
| Admin shop | `family-admin_shop.html` | Cozy Admin Shop Family | 4 skins, native content | https://claude.ai/artifact/HqfJi4bgmPaR2Qm94mfZiR |
| Guild bank | `family-guild_bank.html` | Cozy Guild Bank Family | 8 skins, native content | https://claude.ai/artifact/TnHUiJ6Qoy5Vv3Nn51A1pB |
| Prefixes | `family-prefixes.html` | Cozy Prefixes Family | 6 skins, native content | https://claude.ai/artifact/MBaREmwq5ap4XURfRPJ3b2 |
| Invsee | `family-invsee.html` | Cozy Invsee Family | 2 skins, native content | https://claude.ai/artifact/4qiY57GadNg4HdvRbCocdr |
| Plot | `family-plot.html` | Cozy Plot Family | 4 skins, 12 buttons | https://claude.ai/artifact/B7rkxL1HmL8KgY7y3yu6u1 |
| Utility | `family-utility.html` | Cozy Utility Family | 9 skins, native content | https://claude.ai/artifact/LgnXGZBFdcbFcKQ7LVN8uv |
| Before / after | `before-after.html` | Midnight vs Cozy | 20 screens, baseline `037c5ef` vs cozy | https://claude.ai/artifact/ABYSgTTGoYNZLX472EBAvn |

Licence: generator code MIT; artwork as in the rest of the repository.
