# Cozy style guide

This guide defines the cozy replacement for every texture in the pack: 56
backgrounds, 942 button-state PNGs (157 regions x 6 states) and 54 outer
frames. Geometry, codepoints and interaction contracts are frozen; only the
pixels change. The shared tooling lives in [tools/cozy/](../tools/cozy/README.md),
and every rule below names the helper that satisfies it.

Reference drawings are generated, not committed (evidence/ is gitignored).
Regenerate them with:

```sh
python tools/cozy/render_references.py     # evidence/cozy/reference/*.png + typeface specimen
python tools/cozy/paint_example.py         # evidence/cozy/example/preview.png (quality bar)
```

Use the pinned interpreter
`C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
for every command in this guide.

## 1. Direction

**A warm village workshop at dusk.** The player looks down at a workbench:
oiled wooden boards, cream parchment sheets pinned with brass tacks, linen
tags on twine, red wax seals, wool stitching, potted herbs, a steaming mug,
and candle and lantern light pooling on the wood. References are cozy
management games and hand-painted board-game components: chunky, tactile,
friendly, slightly imperfect. It is not sci-fi, not glossy, and not a flat
web UI.

Rules of thumb:

- Light comes from the top-left. Highlights sit on top/left edges, warm
  shadows on bottom/right edges.
- Every object has a deliberate 1 px warm-brown ink outline. Bottom and
  right edges may be one weight heavier (ink_0).
- Surfaces are flat colour with a few hand-placed details: grain streaks,
  paper fibres, a stitch line, a glint. No gradients, no noise.
- Item wells and live text bands stay calm. Personality lives in frames,
  static panels and the edges of controls.

## 2. Master palette

One palette of 34 colours, ten ramps, every ramp dark to light. There is no
pure black or pure white. Outlines use INK. Source of truth:
`tools/cozy/palette.py` (`NAMED`, `RAMPS`, `rgba('wood_2')`). Swatch sheet:
`evidence/cozy/reference/palette.png`.

| Ramp | 0 (dark) | 1 | 2 | 3 | 4 (light) | Use |
|---|---|---|---|---|---|---|
| ink | `ink_0` 46,28,27 | `ink_1` 68,42,36 | `ink_2` 97,64,50 | | | outlines (ink_1), heavy edges and lettering (ink_0), soft paper rims (ink_2) |
| wood | `wood_0` 84,50,36 | `wood_1` 114,71,45 | `wood_2` 146,95,58 | `wood_3` 180,126,77 | `wood_4` 210,160,104 | boards; body wood_2, grain wood_1, sheen wood_3, highlight wood_4, shadow/seam wood_0 |
| parchment | `parch_0` 190,163,124 | `parch_1` 216,193,152 | `parch_2` 236,218,181 | `parch_3` 248,238,212 | | paper and linen; body parch_2, highlight parch_3, shade parch_1, fold parch_0 |
| brass | `brass_0` 128,88,40 | `brass_1` 180,132,56 | `brass_2` 222,178,84 | `brass_3` 247,222,140 | | plates, tacks, coins, corner brackets |
| sage | `sage_0` 72,92,62 | `sage_1` 112,136,88 | `sage_2` 164,182,124 | | | herbs, leaves, awnings (accent) |
| berry | `berry_0` 112,40,46 | `berry_1` 164,60,60 | `berry_2` 212,108,92 | | | wax seals, danger controls (accent) |
| sky | `sky_0` 60,78,104 | `sky_1` 98,126,156 | `sky_2` 156,182,198 | | | dusk blue, airmail, glass, ruled lines (accent) |
| ember | `ember_0` 198,96,40 | `ember_1` 240,152,64 | `ember_2` 252,212,138 | | | candle and lantern light, pulse and selected glow |
| plum | `plum_0` 52,40,74 | `plum_1` 96,74,132 | `plum_2` 164,138,196 | | | ender dusk, name tags (accent) |
| ash | `ash_0` 92,84,80 | `ash_1` 132,122,114 | `ash_2` 176,166,152 | | | iron bands, offline and disabled states |

Semantic aliases: `OUTLINE = ink_1`, `TEXT_DARK = ink_0`,
`TEXT_LIGHT = parch_3`, `SHADOW = wood_0`, `GLOW = ember_2`,
`TITLE_BAND = parch_2`. `ENDER_WOOD` is the indigo board ramp
(plum_0, ink_1, plum_1, wood_1, plum_2) for the ender chest.

Only palette colours may appear in a texture, with alpha 0 or 255.
`validate.py --style` reports off-palette, pure black/white and
semi-transparent pixels. `palette.snap(img)` pulls stray colours back.

### Family accents

The base (wood, parchment, brass, ink) is shared everywhere. Each family adds
an accent ramp and a secondary ramp, used only in decorative regions
(`palette.FAMILY_ACCENT`, sub-skins in `SKIN_ACCENT`, lookup with
`accent_for(key)`).

| Family / sub-skin | Accent | Secondary | Identity motifs (decorative regions only) |
|---|---|---|---|
| economy | sage | brass | market-stall awning (sage and cream stripes), coin purse, account ledger |
| auction | berry | brass | gavel, hanging price tags on twine, ledger |
| chest_shop | ember | wood | shop-front sign board, shelves, crates |
| trade | sky | ember | two mugs on a shared table, a handshake rope knot |
| ticket | sky | berry | stamped postcard with airmail edge |
| ticket_valid | sky | berry | the postcard is closed with a red wax seal |
| ticket_invalid | ash | berry | the postcard has a torn edge (`parchment_panel(torn='r')`) and no seal |
| admin_shop | brass | sage | quartermaster's counter: a long brass-edged counter top, ledger, stamp |
| guild_bank | ash | sage | iron-banded strongbox, hanging guild banner |
| prefixes | plum | ember | name tags pinned to a corkboard (wood_3 board, plum/ember tags, tacks) |
| invsee | sky | brass | a magnifying glass over a leather satchel |
| invsee_offline | ash | sky | same satchel under blue-grey moonlight; no lantern glow |
| trashcan | sage | wood | slatted compost bin and fallen leaves |
| ender_chest | plum | plum | indigo-dark wood (`ENDER_WOOD`), soft purple lantern light |
| crafting | wood | brass | workbench top, tool loop (hammer, saw, chisel hanging on a rope) |
| template_chest_1..6 | wood | brass | plain warm wood framing only: the default look, no story |

Motifs never enter item wells, the title text rows, the inventory text rows
or button lettering areas.

## 3. Hand-drawn feel

Do:

- **Deliberate outlines.** 1 px ink_1 around every object, corners rounded by
  one pixel (`ink_outline(radius=1)`); bottom/right may switch to ink_0 for
  weight (`heavy='br'`). Paper uses the softer ink_2.
- **Selective highlights.** One pixel on the top/left edge, broken in a few
  places so it looks placed by hand (`highlight_edge(broken=5)`), plus one
  short glint on metal.
- **Warm shadows.** Bottom/right edges one or two ramp steps darker
  (`shadow_edge`), and a 2 px cast shadow where a sheet lies on a board
  (`base_frame` does this round the container).
- **Sparse dithering.** Only where light falls off (lantern glow, worn
  corners), using the ordered 4x4 pattern at 25 % or 50 % (`dither_patch`,
  `lantern_glow_ring`). Never across a whole surface.
- **Organic lines.** Straps, twine, vines and stitching jog by one pixel in
  runs of three or more (`ink_line(wobble=1)`, `twine(sag=)`, `rope(sag=)`).
- **Grain with intent.** Wood grain is a few long streaks per board with a
  sheen above some of them and a rare knot (`plank`, `planks`). Seeds keep it
  reproducible; tune the seed until the board looks right, then keep it.

Forbidden:

- gradient fills, soft brushes, anti-aliased edges or semi-transparency;
- per-pixel procedural noise (random speckle, Perlin, etc.);
- symmetric compositions made by mirroring one half and pasting it (small
  sprites such as a leaf may be flipped to point the other way);
- any reuse of the old generated lettering (the 5x7 `LETTERS` in
  tools/button_assets.py, the 3x5 `PIXELS` in tools/sample_art.py, the
  OFFERED MONEY bitmap in tools/build_pack.py) or of the midnight palette;
- third-party pixels of any kind. Every glyph, sprite and motif is original
  (CC0-1.0).

## 4. Shared visual grammar

Every painter uses the same grammar. `compose.paint_button` and
`compose.base_background` implement it; hand touches go on top. Reference
sheets: `evidence/cozy/reference/buttons.png` (all grammars in six states),
`wells.png`, `icons.png`.

### 4.1 Empty item well

A well is a recessed inset whose 20x20 centre (the clearance) is fully
transparent so the vanilla slot shows through. Adjacent clearances overlap
(18 px pitch, 20 px clearance), so a grid is one merged hole and only its
outside edge gets a frame. Anatomy, measured outward from the hole
(`primitives.well_frame`, Chebyshev distance d):

| Ring | Pixels |
|---|---|
| hole | alpha 0, never painted (`well_frame` cannot write there) |
| d1 | ink_1 lip on every side: the crisp edge of the recess |
| d2 | wall. Sides above/left of the hole are in shadow: two ramp steps darker than the surface underneath. Sides below/right are lit: one step lighter |
| d3 | `stitched_well`: running stitch 2 on / 2 off (parch_2 thread on wood, parch_0 on paper). `wood_well`: a carved lip, lit top-left, shaded bottom-right |

Colours are relative to what is underneath, so the same call reads as a
recess on wood, parchment or linen. Pass the text bands as `protect`: inside
them only the d1 lip is drawn, keeping glyph rows light. Use
`P.merge_holes(skin.content_slots)` and `P.merge_holes(skin.player_slots)` to
build the hole lists. Fake items, shading or patterns inside a well are
forbidden: an empty well must read as empty.

### 4.2 Primary button: brass-plated plank

`compose.primary_face`. Outline ink_1 (radius 1, heavy bottom ink_0); a 1 px
oiled-wood rim (wood_2 with wood_4 broken highlight top-left, wood_0
bottom); a brass plate inset 2 px with a brass_0 rim, brass_2 top row and
left column, a 2-5 px brass_3 glint at the top-left, brass_0 bottom/right
inner edge, and brass_3 rivets 2 px in from each plate corner when the plate
is at least 30x12. Lettering: HEARTH ink_0 with a brass_3 1 px shadow at
(+1, +1), so it reads as engraved.

### 4.3 Secondary button: linen tag

`compose.secondary_face` / `primitives.linen_tag`. Parchment-linen body
(parch_2), ink_1 outline with an ink_0 bottom, parch_3 top highlight, parch_1
bottom shade, a parch_0 running stitch 2 px inside the top and bottom edges
(tags at least 14x12). Wide tags clip their left corners (2 px) and carry a
3x3 brass eyelet at the left middle; tall narrow tags put the eyelet at the
top. The eyelet is dropped automatically when the label needs the room.
Lettering ink_0, no shadow.

### 4.4 Danger button: red wax

`compose.danger_face` / `primitives.wax_slab`. A berry_1 slab with a slightly
dented poured top edge, berry_2 gloss along the top row and left column,
berry_0 rim on top/left and ink_0 on bottom/right, and one or two short drips
that hang into the last two rows. Buttons at least 50 px wide carry a pressed
round seal (`wax_seal`, r <= 5) at the left. Lettering parch_3 with a berry_0
shadow. The 18x18 close control is a full round seal pressed with an X
(`icons.close_seal`).

### 4.5 Page-turn controls: curled parchment corner

Buttons with id `previous` / `next` are parchment sheets
(`compose.page_face`) whose corner curls the way the page turns:
bottom-right for next, bottom-left for previous (`primitives.page_curl`,
5-6 px). The corner beyond the fold is transparent on buttons; on frames and
backgrounds pass `behind=` a colour so no hole opens. The fold line is ink_1,
the flap parch_1 with a parch_3 crease and a parch_0 tip. Lettering ink_0
on the side away from the curl.

### 4.6 States

The server picks one of six PNGs per region. Paint `normal` by hand, then
derive the rest with the shared transforms (`compose.button_states`, which
calls `primitives.make_state`). All transforms keep alpha byte-identical, so
masks and pins survive; hand-adjust afterwards if needed and pass the result
through `button_states(..., overrides={'selected': img})`.

| State | Transform | Reads as |
|---|---|---|
| normal | as painted | at rest |
| disabled | `make_disabled`: every pixel mapped by luminance onto ink_1 / ink_2 / ash_0 / ash_1 / ash_2 (thresholds 60 / 95 / 128 / 172). Glints vanish, contrast drops, lettering stays legible | desaturated, dimmed, clearly inert |
| selected | `make_selected`: non-ink colours move one ramp step lighter; parchment turns golden (parch_2 to brass_3, parch_1 to brass_2, parch_0 to brass_1); the first interior ring gets ember_2 (ember_1 on pale surfaces) on top/left and one step darker on bottom/right; a 3 px brass_3/ember_2 sparkle sits in the top-right interior | warm highlight, raised |
| pulse_1 | `make_pulse(img, 1)`: a bright ember ring 3 px inside the edge, the core one step warmer | the lantern flares |
| pulse_2 | `make_pulse(img, 2)`: the ring moves to 2 px in; afterglow (one step lighter) where it was | the glow spreads |
| pulse_3 | `make_pulse(img, 3)`: a faint checker-dithered ring 1 px in, afterglow at 2 px | fading; the next frame is the resting state |

Ring colour always contrasts with its surface: ember_1 on paper/linen and
on dark wood or wax, ember_2 on brass and mid wood. Ink (outlines and
lettering) never changes in any transform. Pulses play once (4 ticks a frame,
no repeat) and end on the resting look; there is no hover state.

### 4.7 Icons

Icon buttons are 18x18 (body may be trimmed to 17 px by a neighbouring
clearance). The face is a small linen tag without an eyelet; the icon is
centred. All sprites are in `tools/cozy/icons.py` and drawn in
`evidence/cozy/reference/icons.png`.

| Icon | Drawing |
|---|---|
| close | full red wax seal (diameter 17, right-aligned so the pin column is wax) pressed with a 2 px X: ink_0 strokes with a berry_2 lit lip below-right |
| balance | 11x13 leather coin purse: wood_1-4 pouch, parch_1 twine drawstring tied at the neck, a brass coin (brass_2/brass_0) tucked at its foot. The 18x72 balance column is a tall linen tag with a tack top and bottom, the purse near the top and a stack of three coins below |
| search | 11x12 magnifying glass: brass_2 rim, sky_2/sky_1 glass with a parch_3 glint, wood_3 handle to the lower right |
| settings | 12x12 brass cog with eight teeth around a dark brass_0 axle, lit top-left |
| rank (label-only 18x18 control) | 11x13 rosette: berry petals around a brass boss with two ribbon tails |

The rank control has no `icon` field; the rosette stands in for its label
(still no invented words). Seal emblems (`icons.EMBLEMS`: x, check, heart,
star, coin, leaf) are 5x5 and only used on seals of radius 6 or more.

## 5. Background anatomy

Backgrounds are 176 wide (chest heights 132-222; dispenser and crafting
176x166). `compose.base_background(key, seed)` paints the canonical
version; `evidence/cozy/reference/background-anatomy.png` labels it.

| Zone | Rows / columns | Content |
|---|---|---|
| rim | outer 1 px | ink_1, radius 2 corners, heavy bottom/right; broken wood_4 highlight inside top/left |
| board | everything else | horizontal oiled planks about 9 px tall with wood_0 seams (`planks`) |
| title band | x 3-172, rows 2-14 | parchment panel (ink_2 rim) pinned by small brass tacks at both ends, outside the text-safe columns. Live title glyphs land on rows 5-13; the well lip may sit on row 15 |
| well grid | content clearances | merged holes framed by `stitched_well`, protected inside the bands |
| inventory band | rows between the content-grid lip and the player-grid lip (chests: label y-1 .. y+7) | parchment with no ink rim (the well lips frame it). Live "Inventory" glyphs land on rows y-1 .. y+7 |
| player grid | 36 player clearances | main 3x9 and hotbar 1x9 framed separately; the 2-row seam between them carries both lips |
| side margins | x 0-5 and 170-175 | rim + 2 px of board + the 3-ring well frame. Nothing else fits |
| static panels | `staticProtectedSlots`, button rects | on sparse screens: parchment sheets, ledgers, family motifs, explanatory art without words that lie |
| under buttons | button rects | keep a calm board (wood_1/wood_2) so rounded corners and page curls read as wood behind |
| pin | x 175, rows 0-2 | alpha 255 (the rim pixel); `stamp_background_pin` |

Text bands must stay light: parch_2/parch_3 behind the live dark-grey
(#404040) text, mean luminance at least 180 and at most 8 % dark pixels on the
glyph rows (`validate.py --style` checks exactly this). trade_money is the
dispenser exception: its centred title contains only the art, so the
background carries the static label OFFERED MONEY (paint it in HEARTH
ink_0 on the parchment band, centred on x=88); every other skin gets no
painted title. Crafting's title anchor is x=29 and its recipe-book toggle
[4,33,22,20] and arrow [88,30,28,24] are transparent (`base_background`
frames them with a 2-ring `wood_well`).

## 6. Frame anatomy

Frames are 256 wide, at artLayers x=-40, y=-8, height = container + 16.
`compose.base_frame(key, layer_id, seed)` paints the canonical version;
`evidence/cozy/reference/frame-anatomy.png` labels it.

| Zone | Size | Content |
|---|---|---|
| container | x 40-215, y 8 .. h-9 | fully alpha 0 (`clear_frame_container`) |
| top strip | 8 rows | horizontal beam; the artLayers `heading` on a parchment ribbon (SPRIG, 8 rows: ink, cream, 5 glyph rows, ink) with swallowtail ends, centred |
| bottom strip | 8 rows | horizontal beam; rope, tacks or a shelf edge |
| left panel | 40 px | vertical boards: the `leftHeading` on a hanging linen tag (`side_tag`), shelves, lantern, family motifs |
| right panel | 40 px | vertical boards: family motifs; `rightLines` optional |
| rim | outer 1 px | ink_0, radius 3, brass L-brackets in the four corners |
| cast shadow | 2 px right of and below the container | ink_1 then the darkest board colour |
| pin | (255, h//2) | alpha 255 on the rim (`stamp_frame_pin`) |

The board is one step darker than the sheet (`compose.FRAME_WOOD`), so the
menu reads as a sheet lying on a workbench. Words allowed in a frame: the
`heading` text; `leftHeading` and `rightLines` are optional. No other words.
Frames have no click targets. Crafting and trade_money have no frame.

## 7. The "no lies" rule

Textures are static; game state is live. Never bake in:

- prices, balances, amounts, page numbers, counts, dates or durations other
  than a control's own label (the auction "1 Day" ... "15 Days" buttons are
  their labels);
- player, shop or item names;
- fake items, item icons or stack counts in any well or display slot;
- words a control does not own. Button lettering comes only from
  `button-layouts.json` `lines` (preferred) or `label`
  (`geometry.Button.text_lines`); `compose.letter` will not render anything
  else. Mixed case of the label (e.g. "Privacy") is allowed for fit.

Decorative paper may carry ruled lines, stamps and seals, never text that
looks like information. Readiness marks on the trade divider are icons
(check / dash), not words.

## 8. Typeface

Two original faces, hand-authored as sprite strings in
`tools/cozy/lettering.py` (specimen: `evidence/cozy/typeface-specimen.png`).

| | HEARTH (labels) | SPRIG (headings, tight fits) |
|---|---|---|
| cap height | 7 | 5 |
| x-height | 5 (rows 2-6) | uppercase only |
| descender | 2 (rows 7-8) | none |
| widths | 1-5 px, most capitals 4 | 1-5 px, most capitals 3 |
| tracking | 1 px | 1 px |
| word space | 2 px space glyph: 4 px of air between words | 1 px space glyph: 3 px of air |
| traits | lowered A bar, short E/F middle arms, tapered S, spurred G, curled J and Q tails, peaked M/W, slab-serif I | rounded 4-wide bowls (O C G Q U N), lowered A bar |
| charset | A-Z, a-z, 0-9, space + - = $ . , : ! ? / ' ( ) < > % & # * | A-Z, 0-9, space + - $ . , : ! ? / ' ( ) < > & |

Coordinates: `draw_text(img, x, y, s, color, shadow=None, outline=None,
face='hearth')` puts the top of the cap height at y; the baseline is
`y + cap_height - 1`. Kerning pairs (-1): HEARTH LT LY LV TA AT AV VA AY YA
T. Y. F. P. To Ta Te r. 11 //; SPRIG LT TA AT LY YA AY T. API:
`text_width(s, face)`, `draw_text`, `draw_text_centered(img, cx, y, s, ...)`,
`draw_lines_centered(img, box, lines, ...)`, `fit_face(s, max_width)`.

Required fits (checked by `selftest.py`): LISTINGS 38/50, DISABLE LISTING
70/104, PURCHASE 39/50, 12 DAYS 31/68. `compose.letter` tries HEARTH
capitals, then HEARTH mixed case of the label, then SPRIG capitals; every
one of the 157 labels fits. Two-line labels on 18-px buttons fall back to
SPRIG (two 5-px rows and a 1-px gap).

Colours: ink_0 on parchment, linen and brass; parch_3 with a berry_0 or
wood_0 shadow on wax and dark wood; `outline=` only on busy wood.

## 9. Quality bar

`python tools/cozy/paint_example.py` paints a throwaway set into
`evidence/cozy/example/` (never pack-source): a chest_3 background on
template_chest_3 geometry, the 54x36 primary button economy_hub/auction in
all six states, and the 256x184 frame, and writes
`evidence/cozy/example/preview.png`. It uses every primitive. Match it or
exceed it: calm readable wells, light text bands, crisp ink outlines,
purposeful highlights, warm light that pools by dither rather than
gradients, and side panels that tell a small story (lantern on a rope, a
shelf with a steaming mug and herbs, a pinned note with a seal and curled
corner, tags on twine, a trailing vine, a sealed envelope, coins). If your
screen looks flatter, emptier or noisier than the example, it is not done.
Open your preview PNG next to it before you hand in.

## 10. Validator rules (plain language)

`python tools/cozy/validate.py <skin>... | --all` runs the builder's own
functions (`build_pack.validate_png`, `button_assets.validate_button`,
`decorative_assets.validate`) on pack-source and prints one PASS/FAIL line per
asset; `--isolated-build` also runs the real build in a temp copy. Never run
build_pack.py in the shared tree.

| Texture | Rule | Helper that satisfies it |
|---|---|---|
| background | RGBA, exact size (176 x layout height) | `compose.new(s.width, s.height)` |
| background | every content-well clearance (slot x-2, y-2, 20x20), all 36 player clearances and the crafting extras are fully alpha 0 | `geometry.clear_background_masks` (inside `finish_background`), called last |
| background | advance pin [175,0,1,3] is alpha 255, so the opaque bbox ends at x=176 | `geometry.stamp_background_pin` |
| button | RGBA, exact region size (18x18 ... 108x18) | `compose.new(b.w, b.h)` |
| button | the pin `geometry.skin(k).button(id).pin` is alpha 255 and nothing is opaque right of its column (the 18x72 balance pin is (16,36): column 17 belongs to the listing clearances) | `geometry.stamp_button_pin`, `clear_button_masks` (clears right of the pin) |
| button | every content/player clearance that overlaps the region is alpha 0 inside it (`button.masks`, button-local). Paint into `button.body`, which already excludes trimmed edges | `geometry.clear_button_masks` (inside `finish_button`) |
| button | all six states share the normal frame's alpha | `compose.button_states` (transforms never change alpha) |
| frame | RGBA, exact size (256 x container height + 16) | `compose.new(a.w, a.h)` |
| frame | pixel (w-1, h//2) alpha 255 and the bbox ends at w | `geometry.stamp_frame_pin` |
| frame | the whole native container rectangle is alpha 0 | `geometry.clear_frame_container` (inside `finish_frame`) |
| all | 8-bit RGBA PNG, no resampling | `compose.save_png` |

Style lint (`--style`, non-fatal unless `--strict-style`): palette-only
colours, no pure black/white, alpha 0 or 255, and light title/inventory glyph
rows.
