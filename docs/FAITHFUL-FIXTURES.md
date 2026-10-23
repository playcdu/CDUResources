# Faithful fixture gallery

The fixture gallery is a set of self-contained HTML pages that show every
texture of the Faithful vanilla-style replacement (56 menu backgrounds, 157
painted buttons in six states each, 54 outer frames) so the artwork can be
reviewed in claude.ai without checking out the `art/faithful` branch. Each page is
one HTML file with every image embedded as a PNG data URI and no external
resources. It is the Faithful counterpart of the cozy and Soulrend galleries
([COZY-FIXTURES.md](COZY-FIXTURES.md), [SOULREND-FIXTURES.md](SOULREND-FIXTURES.md));
the look itself is defined in [FAITHFUL-STYLE-GUIDE.md](FAITHFUL-STYLE-GUIDE.md).

> **Schematic composites, not gameplay screenshots.** Every picture is drawn by
> [`tools/cozy/preview.py`](../tools/cozy/preview.py) (the theme-agnostic
> preview tool, run with the Faithful theme) from the pack-source PNGs,
> layered the way the client layers them. The grey item squares (and their
> stack counts), the flat slot backdrop standing in for the vanilla container,
> the dimmed world colour, the titles and the "Inventory" label are synthetic
> (lettered in the original PLAIN / TINY faces, not the game font). Only the
> menu background, buttons and frames are real pack textures.

## Generating

```sh
python tools/cozy/build_fixtures.py --theme faithful          # build every page into evidence/faithful-fixtures/, then check them
python tools/cozy/build_fixtures.py --theme faithful --check  # re-check pages already built
```

`QUASAR_GUI_THEME=faithful` does the same as `--theme faithful`; the flag wins.
Use the pinned interpreter
`C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
and run from the repository root on the `art/faithful` branch: the pages always
show the textures in pack-source on the current checkout. **Until the
painters have finished, pack-source still holds the Soulrend art**, so a
gallery built now shows Soulrend textures under Faithful titles, palette and
typeface; rebuild after painting. Output goes to
`evidence/faithful-fixtures/` (gitignored); the build is deterministic for a
given checkout. It reads pack-source and runs `git show` only, and warns if
textures have uncommitted changes. The check step confirms each page is under
16 MB, has balanced tags, starts with `<title>`, carries the schematic caveat,
embeds only PNG data URIs, keeps colour literals inside the token blocks at the
top of `<style>`, and links only to in-page anchors or `{{URL:…}}` tokens.

Under `--theme faithful` the builder swaps in the Faithful palette
(`tools/faithful/palette.py`, 24 colours in 7 ramps; the palette note says
pure black and white are allowed), lettering (`tools/faithful/lettering.py`),
schematic title lettering, page colour tokens (a neutral grey scheme: light
`#e4e4e4` page / `#f2f2f2` surface, dark `#181818` / `#232323`, green accent,
blue links), titles and URL map; everything else is shared with the other
galleries. Images are stored as exact palette PNGs (lossless), which keeps
every page under 1 MB; no family page comes near the 14 MB split budget.

## Page contents

- **Index** (`index.html`, "Faithful GUI Fixtures"): the schematic note;
  links to every family page and the before/after page; all 56 skins as cards
  grouped by family with the family motif (pictogram); the 24-colour master
  palette as swatches grouped by its 7 ramps (ink, grey, green, red, gold,
  blue, purple) with names, RGB values and the semantic aliases; the PLAIN /
  TINY typeface specimen with its spec (PLAIN cap 7 / x 5 / desc 2 / track 1;
  TINY cap 5 / track 1) and the `lettering.specimen()` image at 3x.
- **Family pages** (`family-<family>.html`, "Faithful <Family> Family"): for
  every skin, the composite at 3x, a long-title / full-content composite, every
  button in all six states at 4x, each outer frame alone, and the raw
  background with every alpha-zero clearance outlined in magenta.
- **Before / after** (`before-after.html`, "Midnight vs Faithful"): the same
  20 representative screens as the other galleries, baseline midnight
  artwork from commit `037c5ef7cb5dbe6fe5ab04dadcb2d2c44cd0372e` beside the
  current pack-source.

Cross-page links are generated as `{{URL:<page>}}` placeholders and resolved
at build time from the tracked map `tools/faithful/fixture_urls.json`
(currently `{}`, so every link stays a placeholder). After publishing, record
the URLs there and rebuild.

## Pages

| Page | File | Title |
|---|---|---|
| Index | `index.html` | Faithful GUI Fixtures |
| Economy | `family-economy.html` | Faithful Economy Family |
| Auction | `family-auction.html` | Faithful Auction Family |
| Chest shop | `family-chest_shop.html` | Faithful Chest Shop Family |
| Trade | `family-trade.html` | Faithful Trade Family |
| Ticket | `family-ticket.html` | Faithful Ticket Family |
| Admin shop | `family-admin_shop.html` | Faithful Admin Shop Family |
| Guild bank | `family-guild_bank.html` | Faithful Guild Bank Family |
| Prefixes | `family-prefixes.html` | Faithful Prefixes Family |
| Invsee | `family-invsee.html` | Faithful Invsee Family |
| Utility | `family-utility.html` | Faithful Utility Family |
| Before / after | `before-after.html` | Midnight vs Faithful |

Licence: generator code MIT; artwork as in the rest of the repository.
