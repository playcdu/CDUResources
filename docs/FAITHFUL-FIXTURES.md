# Faithful fixture gallery

The fixture gallery is a set of 12 self-contained HTML pages that show every
texture of the Faithful vanilla-style replacement (56 menu backgrounds, 157
painted buttons in six states each = 942 state PNGs, 54 outer frames) so the
artwork can be reviewed in claude.ai without checking out the `art/faithful`
branch. Each page is one HTML file with every image embedded as a PNG data URI
and no external resources. It is the Faithful counterpart of the cozy and
Soulrend galleries ([COZY-FIXTURES.md](COZY-FIXTURES.md),
[SOULREND-FIXTURES.md](SOULREND-FIXTURES.md)); the look itself is defined in
[FAITHFUL-STYLE-GUIDE.md](FAITHFUL-STYLE-GUIDE.md).

> **Schematic composites, not gameplay screenshots.** Every picture is drawn by
> [`tools/cozy/preview.py`](../tools/cozy/preview.py) (the theme-agnostic
> preview tool, run with the Faithful theme) from the pack-source PNGs,
> layered the way the client layers them. The grey item squares (and their
> stack counts), the flat slot backdrop standing in for the vanilla container,
> the dimmed world colour, the titles and the "Inventory" label are synthetic
> (lettered in the original PLAIN / TINY faces, not the game font). Only the
> menu background, buttons and frames are real pack textures. Every page
> carries this caveat in a note at the top.

> **No Mojang pixels.** Every page also carries the theme's provenance note
> under the caveat, in one sentence: every texture, sprite and PLAIN / TINY
> glyph shown was drawn from scratch for this pack, and no Minecraft jar,
> vanilla resource pack, font bitmap or screenshot was opened, sampled or
> traced to make them (style guide section 0).

## Generating

```sh
python tools/cozy/build_fixtures.py --theme faithful          # build every page into evidence/faithful-fixtures/, then check them
python tools/cozy/build_fixtures.py --theme faithful --check  # re-check pages already built
```

`QUASAR_GUI_THEME=faithful` does the same as `--theme faithful`; the flag wins.
Use the pinned interpreter
`C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
and run from the repository root on the `art/faithful` branch: the pages always
show the textures in pack-source on the current checkout (all Faithful
artwork is committed there; a full build takes about 25 seconds). Output goes
to `evidence/faithful-fixtures/` (gitignored); the build first deletes any
`*.html` already there, and is deterministic for a given checkout. It reads
pack-source and runs `git show` only, and warns if textures have uncommitted
changes. The check step confirms each page is under 16 MB, has balanced tags,
starts with `<title>`, carries the schematic caveat, embeds only PNG data
URIs, keeps colour literals inside the token blocks at the top of `<style>`,
and links only to in-page anchors or `{{URL:…}}` tokens of pages that exist.

Under `--theme faithful` the builder swaps in the Faithful palette
(`tools/faithful/palette.py`, 25 colours in 8 ramps; the palette note says
pure black and white are allowed) and its semantic aliases, lettering
(`tools/faithful/lettering.py`), schematic title lettering, the "No Mojang
pixels" note, page colour tokens (a neutral grey scheme: light `#e4e4e4`
page / `#f2f2f2` surface, dark `#181818` / `#232323`, green accent, blue
links), titles and URL map; everything else is shared with the other
galleries. All of it lives in `THEME_CONFIG['faithful']` in
`tools/cozy/build_fixtures.py`, so the cozy and Soulrend galleries are
unchanged. Images are stored as exact palette PNGs (lossless), which keeps
every page under 1 MB (the largest, chest shop, is about 0.6 MB); no family
page comes near the 14 MB split budget, so every family is one page.

## Page contents

- **Index** (`index.html`, "Faithful GUI Fixtures"): the schematic and
  no-Mojang-pixels notes; the commit the pages were built from; links to
  every family page and the before/after page; all 56 skins as cards grouped
  by family (2x thumbnail of the 1x composite, geometry, button count, frame,
  content mode) with each family's motif; the 25-colour master palette as
  swatches grouped by its 8 ramps (ink 2, grey 8, green 3, red 3, gold 3,
  blue 3, purple 2, rust 1) with names and RGB values, plus the semantic
  aliases of style guide section 2 (`OUTLINE` … `DISABLED_FACE`); the PLAIN /
  TINY typeface specimen with its spec (PLAIN cap 7 / x 5 / desc 2 / track 1;
  TINY cap 5 / track 1) and the `lettering.specimen()` image at 3x (both
  faces, the four required fit checks, kerning pairs, sample buttons).
- **Family pages** (`family-<family>.html`, "Faithful <Family> Family"): for
  every skin, its facts (layout, presentation, buttons, frame, wells, accent,
  background path), the composite at 3x with sample items, a long-title /
  full-content composite at 3x, every button in all six states at 4x (each
  over its own crop of the background), each outer frame alone on mid-grey,
  and the raw background with every alpha-zero clearance outlined in magenta.
  Skins without painted buttons (admin shop, guild bank, prefixes, invsee,
  utility) say so and show their native-content presentation.
- **Before / after** (`before-after.html`, "Midnight vs Faithful"): 20
  representative screens covering all 10 families, each a pair of
  composites at 3x in clearly labelled columns: left (or upper, on a narrow
  screen) tagged **Baseline · midnight**, the midnight artwork from commit
  `037c5ef7cb5dbe6fe5ab04dadcb2d2c44cd0372e` (read with `git show`); right
  (or lower) tagged **Faithful · replacement**, the current pack-source.
  Both sides use the same schematic items, title and default button states,
  so only the textures differ. The screens are economy_hub, economy_log,
  auction_house, auction_confirm, auction_duration, chest_shop,
  chest_shop_listing_enabled, chest_shop_buy, trade_self_ready, trade_money,
  ticket_valid, ticket_invalid, admin_shop_categories, guild_bank_3,
  prefixes_6, invsee_offline, trashcan, ender_chest, crafting,
  template_chest_6. The build refuses to run if the baseline commit lacks any
  of their textures, so the two sides are never mixed.

Cross-page links are generated as `{{URL:<page>}}` placeholders (optionally
followed by `#<skin>`) and resolved at build time from the tracked map
`tools/faithful/fixture_urls.json` (`{"index": "https://claude.ai/artifact/…",
"family-economy": "…", …}`, keyed by the token names in the table below).
Tokens missing from the map stay literal; the map is currently `{}`, so every
link is still a placeholder. After publishing, record the URLs there,
rebuild, republish the pages to the same URLs, and replace the placeholders in
the table below.

## Pages

| Page | File | Title | Contents | URL |
|---|---|---|---|---|
| Index | `index.html` | Faithful GUI Fixtures | 56 skin cards, palette, typeface | `https://claude.ai/artifact/GBW1e8ifngmGsjzjfuCbnz` |
| Economy | `family-economy.html` | Faithful Economy Family | 2 skins, 11 buttons | `https://claude.ai/artifact/RxJevFSwW8nEt7RrBdTR5V` |
| Auction | `family-auction.html` | Faithful Auction Family | 6 skins, 38 buttons | `https://claude.ai/artifact/XzjkCKFeD7RDVXmoXLbbLi` |
| Chest shop | `family-chest_shop.html` | Faithful Chest Shop Family | 12 skins, 89 buttons | `https://claude.ai/artifact/679ffEgdPi77AkwZsFDfgb` |
| Trade | `family-trade.html` | Faithful Trade Family | 5 skins, 15 buttons | `https://claude.ai/artifact/8eKZmm365kszYGcnDEUcD4` |
| Ticket | `family-ticket.html` | Faithful Ticket Family | 2 skins, 4 buttons | `https://claude.ai/artifact/41wcUjv5JpaN6DZ1HNF3ja` |
| Admin shop | `family-admin_shop.html` | Faithful Admin Shop Family | 4 skins, native content | `https://claude.ai/artifact/63nns856osLNTX9VGWhNrZ` |
| Guild bank | `family-guild_bank.html` | Faithful Guild Bank Family | 8 skins, native content | `https://claude.ai/artifact/Fth3fysTK5EePNdzJzGiER` |
| Prefixes | `family-prefixes.html` | Faithful Prefixes Family | 6 skins, native content | `https://claude.ai/artifact/M6snLaH182JM85BJxiaJji` |
| Invsee | `family-invsee.html` | Faithful Invsee Family | 2 skins, native content | `https://claude.ai/artifact/EdBveipCD3f2U9vaoJHsm2` |
| Utility | `family-utility.html` | Faithful Utility Family | 9 skins, native content | `https://claude.ai/artifact/TsFW2NNM6dnoRSdjaMwWs4` |
| Before / after | `before-after.html` | Midnight vs Faithful | 20 screens, baseline `037c5ef` vs Faithful | `https://claude.ai/artifact/YYvUNcJz3RHG2cKoVCGEKX` |

Licence: generator code MIT; artwork as in the rest of the repository.
