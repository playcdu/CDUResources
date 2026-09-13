# CDUResources artist kit

**Foundation being redesigned:** this handoff preserves the audited original layouts. The requested redesigned navigation, visual buttons and stateful layouts are still being implemented. See `manifests/action-layouts.json` and [texture overrides](docs/ARTIST-OVERRIDES.md).

The ready `quasar-gui.zip` is the standalone client resource pack. It contains every menu PNG and the font definition. Copy it into a Minecraft Java test profile's `resourcepacks` folder and enable it; no client Quasar or graphics tools are required. Manual installation alone does not tell a production Quasar server that the pack loaded: use the optional server offer and its successful-load response, or the separate InventoryDebug preview commands for local artwork tests. Exporting or copying a pack does not host it.

This is original, functional sample artwork for 50 audited screens plus six generic chest templates. Client loading and actual in-game visuals remain unverified in this environment. Use the handoff checklist before publishing finished artwork. Target clients are 1.19.2, 1.20.1, and 1.21.1. The same ZIP is intended for all three. `pack_format:15` gives 1.19.2 a newer-pack warning because it ignores extended format ranges; 1.20.1 matches 15 and 1.21.1 recognizes the 9..34 range. The released 26.2 metadata codec accepts this structure, but format 88.0 is outside the declared range: its warning and actual client loading/rendering remain unverified. Versions 1.16/1.18 were excluded by the user; 26.2 is not claimed compatible.

## Files to edit

`pack-source/assets/quasar_gui/textures/menu/<skin_key>.png` contains one independent replaceable PNG for every skin. `manifests/skins.json` maps keys to filenames, codepoints and the native slots that must stay transparent. `manifests/menu-coverage.json` gives every audited screen's slot roles; `manifests/control-map.json` adds detailed triggers, effects and conditional states for the functional controls. `manifests/layouts.json` is the geometry authority. Do not invent painted click targets.

Open [CONTROL-EXPLORER.html](CONTROL-EXPLORER.html) in a browser to select a menu or slot, toggle artwork and schematic item layers, and read its action/state legend offline. The [illustrated examples](illustrations/contact-sheet.png) show auction, trade, shop, confirmation and ticket controls together with the actual sample overlays. The [auction layer diagram](illustrations/auction-layer-diagram.png) separates native content, bitmap artwork and existing slot positions. These are clearly labeled layout illustrations, not captured gameplay; example icons and text are original schematic shapes.

`guides/<skin_key>.png` gives every skin a numbered layout and visible action legend, including conditions and native item descriptions where audited. `contact-sheet.png` shows all 56 raw samples on a grey transparency backdrop. Sparse menus include static section labels and explanatory panels; dense listing/storage menus leave every possible native item well open. Readiness, confirmation and disabled variants use distinct artwork as well as the existing native items and lore.

Keep original sample files as your backup. Put finished replacements under a separate directory with the same hierarchy, for example:

```text
overrides/
  assets/quasar_gui/textures/menu/auction_house.png
```

The builder never edits that overrides directory. Finished overrides are applied only to the output ZIP. Alternatively, directly edit a PNG in `pack-source`; normal builds read those PNGs and preserve them. Only the explicit `--regenerate-samples` option replaces canonical sample artwork with procedural defaults. Do not use that option on finished source artwork.

## Rebuild without Java changes

Use Python 3.12.14 and install the pinned image dependency (`python -m pip install -r requirements.txt`). From the extracted kit directory:

```powershell
python tools/build_pack.py --overrides overrides --output deliverables/my-quasar-gui-r2.zip
python tools/build_pack.py --validate deliverables/my-quasar-gui-r2.zip
python tools/test_pack.py
```

Omit `--overrides overrides` when editing `pack-source` directly. The output ZIP has `pack.mcmeta` and `assets/` at its root. The `.zip.sha1` file contains the exact hash of that ZIP. Host the ZIP at a stable, directly downloadable HTTPS URL; configure Quasar with that URL and its SHA-1. Never configure a local filesystem path as the URL. Use a new immutable URL or revision query for changed art; update the hash and pack revision together. Existing success state must be invalidated by the server adapter. Publishing or hosting is an operator step, not performed by these tools.

## Pixel contract

Export ordinary 8-bit-per-channel RGBA PNG, at exact native logical pixel dimensions, with no resampling. Chest textures are 176 wide and 114 + 18 Ã— rows high (132,150,168,186,204,222). Dispenser and crafting are 176 Ã— 166. Bitmap provider height equals texture height; scale is 1. Use nearest-neighbour scaling only for guide previews. PNG colors remain original only when the title glyph is explicitly white, nonbold and nonitalic.

All item/control/player-inventory masks in the manifest must have alpha zero: the title is rendered after slots and hover, so an opaque pixel may cover icons, glint, bars, counts, or hover highlights. Masks include a two-pixel clearance and cover a 20 Ã— 20 rectangle around each item origin. `liveSlots` is the union of every top slot that can display, control or store an item in any audited state; all 36 player slots also stay clear. Rendering tests must still check unusual item models and custom count fonts. Overlapping neighboring masks are intentional. Opaque explanation art is permitted in `staticProtectedSlots`, which are audited never-populated protected slots, and in `removedDecorations`, where the server removes a decorative item while retaining its protection. Every other potential native item well must remain clear. Server-side slot protection is independent of artwork; the texture creates no interactive area.

The `advancePin` at x175,y0,w1,h3 must stay fully opaque. It locks measured bitmap width to 176 and advance to 177. A texture's width alone is not its font advance. Do not move or erase that pin, change provider height/ascent, change codepoints, or alter spacing providers. Ascent 13 places artwork at y0 from the title baseline at y6 (`6 + 7 - 13`). Chest title anchor x8 uses spacing -8 / glyph advance 177 / spacing -169. Crafting uses x29, spacing -29 / glyph advance 177 / spacing -148, and keeps recipe-book controls/arrow regions transparent. Dispenser title is centered by vanilla: its title component contains the art and fixed 160-pixel spacing only, so the anchor stays x8 even with a different normal text font. The sample's static OFFERED MONEY label is artwork; the amount and money controls stay live in slot 4's native item/tooltip, and Quasar's full original title is available through `/quasargui title`. Chest/crafting dynamic titles remain live. Local packs can still override the custom font itself; manual standard mode is the recovery path.

The purple guide rectangle is the title area (live text except for the dispenser's static artwork label), the red cross is the title anchor, blue numbered rectangles mark 16-pixel native item footprints, and rose rectangles mark protected static artwork. Minecraft supplies slot hit testing. The inventory label is rendered as live vanilla text after the title. No fixed sample prices, names, balances, or page numbers are baked into release art. Potential item slots remain visibly empty when unoccupied; do not paint fake items there. Explanatory panels have no callback. Selected/disabled/readiness/confirmation variants are separate files where the audited menu actually changes state; native item icons and lore continue to show detailed state.

## Review before deployment

Test the same output ZIP on all three target clients: every skin, all six chest sizes, dispenser, crafting with recipe book open/closed and narrow/wide windows, several GUI scales, default/Unicode/accessibility fonts, long titles, empty/full pages, all buttons. Check item glint, durability, counts, tooltips, hovered slots and a cursor-carried stack. Test standard mode and loaded mode together with two trade viewers. A contact sheet or static validator is not proof of client rendering.

Run the texture-only exercise with `python tools/test_pack.py`; its evidence writes under `evidence/pack-tests/`, showing that a single changed PNG changes the ZIP hash while codepoints/providers and Java remain unchanged, and that an opaque item well is rejected.

Optional developer codec checks are documented in `CLIENT-COMPATIBILITY.md`. They download only official public client audit files through `python tools/fetch_client_fixtures.py` and require Java 25 for the included source-file runners. They are unnecessary for normal artwork replacement and do not substitute for testing the actual game. The downloaded game files remain local audit fixtures and must not be added to the release pack.

## Existing server packs

Choose one offer owner. On an existing single-server-pack installation, merge the GUI namespace into the operator's pack and offer that merged file. The merge tool refuses path collisions, namespace overlays and metadata filters; it never overwrites input packs or an existing output. It preserves operator metadata unless an explicit reviewed `--metadata` file is supplied.

```powershell
python tools/merge_pack.py operator-pack.zip quasar-gui.zip merged-r2.zip
```

The merge is byte deterministic and emits the actual merged SHA-1. Its success proves conflict checks, not compatibility of someone else's assets or mandatory-pack policy. Do not silently replace an existing pack's metadata with the GUI's range: the other assets may support fewer versions. Configure only the merged URL/hash and one owner; do not interpret an unrelated pack's successful load as this pack's success.

## License

The generated sample PNGs, spacing definitions, layout data and generator are original work for this patch and are provided under CC0-1.0 for artwork/data and MIT for the standalone Python tooling; see `LICENSE.txt`. No Mojang textures, NegativeSpaceFont assets, paid templates or other third-party art are redistributed. Pixel width measurements are numerical facts derived from official client assets. Quasar itself retains its repository license.
