# Painted button layers

All 54 audited skins and six chest templates share the new dark framing. Thirty-one screens have painted controls: economy, four auction page types, confirmation and duration, both ticket states, trade money and four readiness states, shop settings, buying/selling, three upgrade states, both listing editors, shop advertisement/search pages, economy history, both main chest-shop modes, and the four plot screens (buy, rent, list and manage; see [CONTROL-MAP.md](CONTROL-MAP.md#plots)). The remaining selection, storage, inspection, configuration-defined shop and crafting screens preserve all native content positions; this is a deliberate content constraint, not an invented action layout. Main chest shops retain 24 listing cells and three compact right-column icon controls. Crafting keeps extra recipe-control masks and omits the outside frame. A generated guide or parser result does not establish successful client interaction.

Each large control is real: every native slot cell under the painted region is assigned to the same original logical action. `manifests/button-layouts.json` records the original `sourceSlot`, all physical `slots`, its label, action/info role, visual style, and native content that must stay visible. For example, economy's Auction House card maps six cells to original slot 11. Information cards retain live tooltips and have no action.

## Editable artwork

Backgrounds remain at `pack-source/assets/quasar_gui/textures/menu/<key>.png`. Controls are independent small PNGs at `pack-source/assets/quasar_gui/textures/buttons/<key>/<button-id>/<state>.png`. Every region provides `normal`, `disabled`, `selected`, `pulse_1`, `pulse_2`, and `pulse_3`. The original procedural source is `tools/button_assets.py`; its palette, five-by-seven text, compact labels, frames and highlight shapes are all editable.

Normal builds preserve edited PNGs. Put replacements under the same path beneath `overrides/`, then run:

```powershell
python tools/build_pack.py --overrides overrides --output deliverables/my-gui-r2.zip
python tools/test_pack.py
```

Normal builds preserve every source PNG and `.aseprite` file. Paint and export with Aseprite; the optional layout helper assists with alignment and existing action bindings. Use `--regenerate-button economy_hub/auction` only when you deliberately want to recreate that button's six default frames, for example after resizing its region. The broader `--regenerate-samples` recreates all defaults and must stay away from finished artwork. `tools/author_button_layouts.py` is a developer authoring command, never part of a normal artist build.

The builder emits `deliverables/quasar-gui-layouts-<ZIP SHA1>.json` beside the ZIP, binding its runtime geometry to that exact pack hash. Deploy both together when moving or resizing buttons. Existing `id`, `sourceSlot` and `role` bindings remain fixed; artist layout changes cannot invent callbacks or consume protected native content.

Paged auction, shop advertisement/search and history layouts retain 28 native items in a 7 × 4 grid. `contentRegion` maps original logical listing sources 0–44 into the 28 physical cells. The server captures the appropriate page capacity for a flow and refuses the mapping if extra source positions still contain items. Decorative `artLayers` extend 40 pixels on each side and eight above/below the native chest screen, without outside click targets. Their individual PNG cells remain within 256 × 256 pixels, and the native container interior stays transparent. See [the redesigned illustrations](../illustrations/redesign/contact-sheet.png).

## Pixel and state contract

Artwork follows native 18-pixel slot pitch. A single native item occupies a 16-pixel footprint, while desktop hit testing expands one pixel on each side. Adjacent two-cell and four-cell buttons therefore cover continuous 36 × 18 and 36 × 36 hit regions. Each mapped slot is still independently protected and dispatched by the GUI library.

`visibleContentSlots` and all 36 player slots require their 20 × 20 alpha-zero clearance. `paintedControlSlots` intentionally receive opaque button artwork, backed by invisible nonempty items. Content clearance can trim one edge pixel from a neighbouring button; the validator handles that overlap. Never hide a real offered item, listing, storage stack, crafting input or result under painted controls.

Each frame's runtime entry records its exact ascent, advance, spacing and `advancePin`. Keep that pinned pixel opaque. Frame dimensions, codepoints and advances are fixed across all six states. Negative ascents position small button glyphs lower in the container; their prefix/glyph/suffix sum to zero horizontal advance, so adding controls does not move the live title.

The three pulse frames are separate bitmap glyphs selected by server state updates. Minecraft does not animate bitmap-font PNGs through `.png.mcmeta`. Pulse feedback must be explicitly triggered by the existing action/state logic and then return to the appropriate normal, selected or disabled state. An animation does not authorize or prove a transaction. Hover stays client-local; this implementation does not promise server-driven hover frames.

## Invisible carriers and merging

Themed controls use protected, nonempty paper display stacks with CustomModelData 194731. Their model has empty geometry, so there is no vanilla paper icon; names and lore still produce Minecraft tooltips. Ordinary paper remains ordinary. The model override resets at 194732. Legacy InventoryDebug's invisible value 1 is preserved, with an ordinary-paper reset at 2.

The only vanilla-namespace pack file is `assets/minecraft/models/item/paper.json`, which selects those exact ranges and the namespaced carrier/default models. Real gameplay items are never converted into carriers. Standard presentation restores original display items and callbacks.

The validator rejects other vanilla-namespace paths, altered carrier ranges, unreviewed metadata fields, modified metrics and opaque content wells. The merge tool rejects conflicting paper models or paper models hidden in an operator overlay. Resolve a real paper-model conflict deliberately; do not silently overwrite another pack's custom item definitions.

The trade divider has independent YOU/THEM readiness marks in each of its four background skins. This keeps readiness visible even when incoming money is zero and the corresponding read-only money carrier is absent. These marks are noninteractive; the Ready action remains the three-cell footer button.

Fixed display items also expose `contentRegion`: auction confirmation retains logical source 20, and both ticket variants retain logical source 22. Their default destination is unchanged, but the artist can move the single display within free native top cells while keeping its source and capacity fixed. Info cards such as quantity, balance and stats already move through their `role: info` button regions. These display mappings do not change pagination. Update the PNG clearances when moving native displays.
