# Faithful style guide

This guide defines the Faithful theme: a vanilla-faithful replacement for
every texture in the pack that looks like Minecraft's own container GUIs
(light grey bevelled panels, inset slot wells, grey stone buttons, white
button lettering with a dark shadow) while being 100 % original artwork. It
covers 56 backgrounds, 942 button-state PNGs (157 regions x 6 states) and 54
outer frames. Geometry, codepoints and interaction contracts are frozen; only
the pixels change. The shared tooling lives in
[tools/faithful/](../tools/faithful/README.md), and every rule below names the
helper that satisfies it. Geometry, masks, pins and validation are the
theme-agnostic ones in `tools/cozy/geometry.py` and `tools/cozy/validate.py`;
they are imported, never copied.

Reference drawings are generated, not committed (evidence/ is gitignored).
Regenerate them with:

```sh
python tools/faithful/render_references.py   # evidence/faithful/reference/*.png + typeface specimen
python tools/faithful/paint_example.py       # evidence/faithful/example/preview.png (quality bar)
```

Use the pinned interpreter
`C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
for every command in this guide, run from the repository root.

## 0. No Mojang pixels (absolute)

Vanilla Minecraft's GUI textures and its font are Mojang's copyrighted
assets. This theme recreates their general *visual language* from memory and
description only. Therefore:

- **Never** open, extract, sample, trace or embed any Minecraft jar, vanilla
  resource pack, texture, font bitmap or screenshot crop, not even "just to
  check a colour". The toolkit was built without opening one.
- Every sprite in `tools/faithful/` is drawn from scratch as ASCII rows or
  generated from simple geometry (`icons.shaded`, `icons.disc_mask`).
  Every glyph of PLAIN and TINY is hand-authored in
  `tools/faithful/lettering.py`.
- What we reproduce is the *idea*: a flat light-grey panel, a 1 px white
  top-left bevel and a dark-grey bottom-right bevel, a black outline with
  notched corners, slot wells with a dark top-left inner shadow and a white
  bottom-right inner highlight, grey stone buttons with a dark outline and a
  lighter top-left edge. These are generic, unprotectable ideas; colour values
  (198 / 139 / 85 / 55 greys, white, black) are facts and may be used.
- PLAIN is designed to *sit next to* the game's 5x7-style font, not to copy
  it. It has deliberate traits of its own (section 9). Forced shapes that
  every 5x7 face shares (O, I, L, T) will inevitably resemble any such font;
  everything with a design decision in it is ours.
- No third-party pixels of any kind (texture packs, "faithful" community
  packs, fonts, icon sets). Artwork and data are CC0-1.0; tooling is MIT.

If you are unsure whether something is a copy, draw it differently.

## 1. Direction

**The game's own inventory language, clean and familiar.** A player opening
any Quasar screen should feel this is vanilla Minecraft with painted buttons:
the same calm grey panel, the same inset slots, the same stone buttons. Restraint
is the point. Family identity is a whisper: one 1 px coloured line under the
title, one small flat pictogram in a static cell or on the docked side panels.

Rules of thumb:

- Light comes from the top-left. Raised things (panels, buttons) are white or
  light on their top/left edge and dark grey on their bottom/right edge;
  recessed things (slots, info plates, tiles) are the reverse.
- Outlines are pure black (`ink_0`), 1 px, with notched (rounded) corners:
  radius 2 on panels, radius 1 on buttons.
- Surfaces are flat. The only texture in the whole theme is the sparse stone
  fleck on button faces (`stone_texture`). No gradients, no noise, no dither.
- Colour is for meaning only: gold = primary, red = danger, green = selected /
  ready / valid, blue = information, purple = the ender chest. Everything else
  is grey.

## 2. Master palette

One palette of 24 colours in seven ramps, every ramp dark to light. Pure
black and pure white **are** allowed (the vanilla language is built on them;
`palette.ALLOW_PURE_BW = True`, so `validate.py --style --theme faithful`
does not flag them). Source of truth: `tools/faithful/palette.py` (`NAMED`,
`RAMPS`, `rgba('grey_3')`). Swatch sheet: `evidence/faithful/reference/palette.png`.

| Ramp | 0 (dark) | 1 | 2 | 3 | 4 | 5 | 6 | 7 (light) |
|---|---|---|---|---|---|---|---|---|
| ink | `ink_0` 0,0,0 | `ink_1` 64,64,64 | | | | | | |
| grey | `grey_0` 55,55,55 | `grey_1` 85,85,85 | `grey_2` 100,100,100 | `grey_3` 113,113,113 | `grey_4` 139,139,139 | `grey_5` 160,160,160 | `grey_6` 198,198,198 | `grey_7` 255,255,255 |
| green | `green_0` 52,104,44 | `green_1` 92,152,68 | `green_2` 152,206,112 | | | | | |
| red | `red_0` 104,34,34 | `red_1` 156,58,52 | `red_2` 206,108,96 | | | | | |
| gold | `gold_0` 140,102,22 | `gold_1` 204,162,44 | `gold_2` 252,222,100 | | | | | |
| blue | `blue_0` 40,64,128 | `blue_1` 72,112,184 | `blue_2` 136,172,228 | | | | | |
| purple | `purple_0` 70,52,98 | `purple_1` 190,182,206 | | | | | | |

Jobs:

| Colour | Job |
|---|---|
| `ink_0` | every outline (panels, buttons, sprites); the pin colour |
| `ink_1` | dark text on light plates and the panel (vanilla-style #404040); the (+1, +1) shadow under white lettering |
| `grey_0` | slot / tile inner shadow (top/left); the flat disabled face |
| `grey_1` | panel and button bottom/right bevel; info plate top/left rim; frame grooves and drop shadow |
| `grey_2`, `grey_4` | dark and light stone flecks on button faces |
| `grey_3` | the stone button face |
| `grey_4` | slot-grey mixed corners of insets, tile fill on frames |
| `grey_5` | button top/left bevel; info plate face; disabled lettering |
| `grey_6` | **the panel**: the title and inventory text sit on it |
| `grey_7` | panel top/left bevel, inset bottom/right highlight, button lettering, pulse highlight |
| `green_*` | selected face / bevel, valid stripe, family accent (chest shop, ticket) |
| `red_*` | danger face and bevel, close button, invalid stripe, auction / trashcan accent |
| `gold_*` | primary bevel, coins, the star, economy / guild bank accent |
| `blue_*` | lens, eye, arrows, shield, banner; trade / admin / prefixes / invsee accent |
| `purple_*` | the ender chest panel ramp and its accent only |

Semantic aliases: `OUTLINE = ink_0`, `TEXT_DARK = ink_1`, `TEXT_LIGHT =
grey_7`, `SHADOW = ink_1`, `TEXT_DISABLED = grey_5`, `GLOW = grey_7`,
`TITLE_BAND = SHEET = PANEL = grey_6`, `BEVEL_LIGHT = grey_7`, `BEVEL_DARK =
grey_1`, `SLOT_FILL = grey_4`, `SLOT_SHADOW = grey_0`, `BUTTON_FACE = grey_3`,
`BUTTON_LIT = grey_5`, `DISABLED_FACE = grey_0`. Panel ramps (outline, dark
bevel, panel, light bevel): `PANEL_RAMP` (black, grey_1, grey_6, white) and
`ENDER_PANEL_RAMP` (black, purple_0, purple_1, white); `compose.sheet_for(key)`
picks one.

Only palette colours may appear in a texture, with alpha 0 or 255.
`validate.py --style --theme faithful` reports off-palette and
semi-transparent pixels; `palette.snap(img)` pulls stray colours back.

## 3. Hand-drawn feel (in the vanilla register)

Do:

- **Crisp 1 px structure.** Black outline, one bevel ring, flat face
  (`bevel_panel`, `stone_button`). Corners are notched, never square:
  `rounded_mask` radius 2 for panels (3 pixels cut per corner, plus the inner
  bevel corner pixel for a chunky turn), radius 1 for buttons.
- **Sparse stone on button faces only.** `stone_texture` places 1-3 px
  `grey_2` flecks, each with an occasional `grey_4` pixel above-left, on a
  jittered 7x4 grid with about half the cells empty. Seeded, so it is the
  same every run. Never on panels, plates or tiles.
- **Insets read as holes.** Wells, info plates and pictogram tiles are
  recessed: dark top/left, light bottom/right, mid-grey on the two mixed
  corners (`inset`, `well_frame`, `flat_plate`, `inset_box`).
- **Pictograms are flat.** Black outline, one light and one dark step of a
  single ramp, at most two accent colours, no more than 12x14 px.

Forbidden:

- any Mojang pixel (section 0); copying a community "faithful" pack;
- gradient fills, soft brushes, anti-aliasing, semi-transparency, dither,
  per-pixel noise;
- texture on the panel (vanilla's panel is flat; so is ours);
- the old generated lettering (`LETTERS` in tools/button_assets.py, `PIXELS`
  in tools/sample_art.py, the OFFERED MONEY bitmap in tools/build_pack.py),
  any cozy or Soulrend face, palette or sprite (their toolkits may be reused
  for geometry, validation and preview only);
- fake items, item icons or counts in a well; words a control does not own.

## 4. Shared visual grammar

Every painter uses the same grammar. `compose.paint_button` and
`compose.base_background` implement it; hand touches go on top. Reference
sheets: `evidence/faithful/reference/buttons.png` (every grammar in six
states), `wells.png`, `icons.png`, `primitives.png`.

### 4.1 Empty item well: the inset slot

A well is the vanilla-style inset slot whose 20x20 centre (the clearance) is
fully transparent, so the slot drawn underneath by the client shows through
and reads as empty. Adjacent clearances overlap (18 px pitch, 20 px
clearance), so a grid becomes one merged **inset tray** and only its outside
edge is framed (`primitives.well_frame` / `inset_well`):

| Pixel just outside the hole | Colour |
|---|---|
| hole | alpha 0, never painted (`well_frame` cannot write there) |
| top and left walls (hole below / right) | `grey_0` inner shadow |
| bottom and right walls (hole above / left) | `grey_7` inner highlight |
| top-right and bottom-left mixed corners | `grey_4` |
| top-left outer corner | `grey_0` (continues the shadow) |
| bottom-right outer corner | `grey_7` (continues the highlight) |

Pass the live text rows as `protect` (`compose.text_rows(key)`): inside them
the dark run is not drawn, so the glyph rows stay light. Build hole lists with
`P.merge_holes(skin.content_slots)` and `P.merge_holes(skin.player_slots)`.
Fake items, shading or patterns inside a well are forbidden.

### 4.2 Primary button: stone with a gold bevel

`compose.primary_face` / `primitives.stone_button(kind='gold')`. From the
outside in: `ink_0` outline (radius 1); a 1 px raised bevel with **`gold_2`
on the top and left** and `grey_1` on the bottom and right; on plates at least
26x12 a broken second `gold_1` row under the top edge (gaps every 6 px, as if
the gold catches light unevenly); a `grey_3` face with sparse stone flecks.
Lettering: PLAIN `grey_7` with an `ink_1` shadow at (+1, +1). Text box: the
face minus the shadow column/row (`(x+2, y+3, w-5, h-6)` on tall plates), so
PURCHASE (47 px) fits a 54 px plate.

### 4.3 Secondary button: plain stone

`compose.secondary_face` / `stone_button(kind='plain')`: `ink_0` outline,
`grey_5` top/left bevel, `grey_1` bottom/right bevel, flecked `grey_3` face.
Lettering: PLAIN `grey_7` with an `ink_1` shadow. Text box `(x+2, y+2, w-5,
h-5)`. Fit order: PLAIN capitals, PLAIN mixed case of the label, TINY
capitals (`compose._label_plan`).

### 4.4 Danger button: red stone

`compose.danger_face` / `stone_button(kind='red')`: `ink_0` outline, `red_2`
top/left and `red_0` bottom/right bevel, a `red_1` face with sparse `red_0`
flecks. Lettering: `grey_7` with an `ink_1` shadow. Muted, never gory. The
18x18 close control is the same red stone (no flecks) with a 2 px white **X**
with an `ink_1` shadow (`icons.draw_x`).

### 4.5 Info (read-only): recessed plate

`compose.info_face` / `primitives.flat_plate`, used for every `role: info`
region with a label (balance, stats, stock, quantity, bid, other money,
create shop). A flat `grey_5` face with **no outline and no raised bevel**:
its outer ring is recessed (`grey_1` top/left, `grey_7` bottom/right, face
colour on the mixed corners), so it reads as a label set into the panel,
never as something to press. Lettering: PLAIN `ink_1`, no shadow. Info icons
(balance coin, rank star) sit on the same plate.

### 4.6 Page-turn controls: stone with an arrow

Buttons with id `previous` / `prev` / `next` are plain stone buttons with a
small original arrow glyph (a solid 4x7 triangle, `primitives.arrow_glyph`,
`grey_7` with an `ink_1` shadow) on the side the page turns: right for next
(3 px in from the right bevel), left for previous. The label is centred in
the rest of the face. The arrow is registered as a glyph (`compose.remember_extras`),
so the states treat it exactly like lettering.

### 4.7 States

The server picks one of six PNGs per region. Paint `normal` by hand, then
derive the rest with the shared transforms (`compose.button_states`, which
calls `primitives.make_state`). Every transform keeps alpha byte-identical, so
masks and pins survive. Hand-adjust afterwards if needed and pass the result
through `button_states(..., overrides={'selected': img})`.

| State | Transform | Reads as |
|---|---|---|
| normal | as painted | at rest |
| disabled | `make_disabled`: vanilla's flat disabled button. The black outline (and any black sprite outline) stays; every glyph-like pixel (label, page arrow, close X, icon) keeps its position and alpha and becomes **`grey_5`**, so labels read mid grey and icons become grey silhouettes inside their black outline; label shadows stay `ink_1`; an un-outlined rim (the info plate) becomes `grey_1`; every other pixel becomes the flat **`grey_0`** face (stray whites `grey_5`). Bevels, gold, red, green and flecks all go flat. No cracks (the Soulrend crack rule does not apply). | flat dark grey, mid-grey label: clearly inert |
| selected | `make_selected`: a **green-tinted face with a brighter bevel**. Stone face, flecks and plate face turn green (`grey_2/3/4/5` -> `green_0/1/2/2`); on the bevel ring the top/left turns `grey_7` and the bottom/right `green_0`; an un-outlined dark rim turns `green_0`; other colours (gold, red, blue) move one step lighter. Glyph-like pixels and the shadow drawn under them never change. | chosen, lit, vanilla's "ready" green |
| pulse_1 | `make_pulse(img, 1, protect)`: the bevel ring (first interior ring) turns `grey_7` all round | the bevel flashes |
| pulse_2 | `make_pulse(img, 2, protect)`: the bevel stays white and the next ring (the outer face ring) moves **two** steps lighter on its own ramp: the face highlight. If nothing on that ring can brighten (all protected), the bottom/right bevel run turns `grey_6` instead of white, so the frames still differ | the light spreads onto the face |
| pulse_3 | `make_pulse(img, 3, protect)`: the bevel ring is white on alternate pixels only (a checker), the face is back at rest | fading; the next frame is the resting state |

**What never changes.** `compose.state_masks(normal, button)` returns
(glyphs, extras, footprint, protect): the label's glyph pixels (from the
label geometry, see below), the extras (page arrow, close X, icon pixels),
the footprint (glyphs + extras + the `ink_1` shadow pixels actually drawn
under them) and protect (footprint + a 1 px 8-neighbour halo round every
glyph-like pixel). **Selected never changes a footprint pixel; no pulse
changes a protect pixel; disabled moves no glyph pixel and changes no
alpha.** (Selected may tint the face right up to the letters because a grey
halo round white letters on a green face would read as a dirty outline;
white and `ink_1` are fixed points of the selected tint anyway.)

`compose.lettering_mask` finds the label geometrically, never by guessing
shapes first: (1) the exact glyph pixels `compose.letter` drew on that image;
else (2) a whole-label template search (the label's own lines, face and
spacing; at least 90 % of its pixels in one colour); only for genuinely
hand-lettered labels (3) a word / character shape search whose hits on the
outline and first inner ring are discarded. `compose.extras_mask` does the
same for arrows and the X (white template search) and icons (exact sprite
match). Letter with `lettering.draw_text` or `compose.letter` so the detector
can find your text. `selftest.py` fails if a lettered button has no
detectable lettering, if the mask found on a copy covers less than 90 % of
what was drawn, if selected or a pulse changes a protected pixel, if a
disabled glyph pixel moves or keeps a live colour, or if any two of a
button's six states are identical.

Pulses play once (4 ticks a frame, no repeat) and end on the resting look;
there is no hover state.

### 4.8 Icons

Icon buttons are 18x18 (the body may be trimmed to 17 px by a neighbouring
clearance). Action icons (search, settings) sit on a plain stone button
without flecks; read-only icons (balance, rank) sit on a recessed info
plate; close sits on red stone. The icon is centred in the face. All sprites
are in `tools/faithful/icons.py` and drawn in
`evidence/faithful/reference/icons.png`.

| Icon | Drawing |
|---|---|
| close | 8x8 2 px-stroke X, `grey_7` with an `ink_1` shadow, on red stone |
| balance | 11x11 gold coin disc (`gold_2` lit top-left, `gold_0` shade bottom-right, black rim) crossed by a `gold_0` diagonal slash with a lit edge: our own currency mark. The 18x72 balance column is a tall info plate with the coin near the top and four small 5x5 coins stacked below |
| search | 12x12 lens: grey rim lit top-left, `blue_1`/`blue_0` glass with a white and `blue_2` glint, a grey handle to the lower right |
| settings | 13x13 grey cog, eight teeth, a black axle with a `grey_0` centre, lit top-left |
| rank (label-only 18x18 info control) | 11x11 five-point gold star with a black outline |

The rank control has no `icon` field; the star stands in for its label (no
invented words). Icons are glyph-like: protected in selected and the pulses,
grey silhouettes when disabled.

## 5. Per-family identity

The base (panel, wells, stone buttons) is identical everywhere. Each family
adds exactly two things, both decorative and never in wells, text rows or
lettering areas (`palette.FAMILY_ACCENT`, sub-skins in `SKIN_ACCENT`, lookup
with `accent_for(key)`):

1. **The accent line**: a 1 px line in the accent ramp's middle step on row
   14 (the free row under the title glyph rows 5-13), over the text-safe
   columns 8-167, drawn only on plain panel pixels so it breaks round a
   tray or a button that reaches that row (`compose.draw_accent_line`,
   `compose.ACCENT_Y`). Plain skins have none.
2. **The pictogram**: one 16x16 recessed tile with the family pictogram
   centred in the largest static decorative region of the background
   (`compose.static_regions`, `pictogram_tile`), and one 24x24 tile on each
   docked side panel of the frame (section 7).

| Family / sub-skin | Accent line | Pictogram |
|---|---|---|
| economy | gold_1 | `coin`: gold coin disc with a stamped centre mark |
| auction | red_1 | `gavel`: gold-wood gavel standing on a grey sound block |
| chest_shop | green_1 | `chest`: a chest from the front, lid edge and latch |
| trade | blue_1 | `arrows`: two opposed blue arrows |
| ticket | green_1 | `ticket`: a stub with side notches and a perforated end |
| ticket_valid | green_1 | `ticket_valid`: the stub with a green stripe |
| ticket_invalid | red_1 | `ticket_invalid`: the stub with a red stripe |
| admin_shop | blue_1 | `shield`: a blue shield with a white chevron |
| guild_bank | gold_1 | `banner`: a blue banner on a rod with a gold coin device |
| prefixes | blue_1 | `nametag`: a name-tag shape with a hole and a string |
| invsee | blue_1 | `eye`: an open eye, blue iris |
| invsee_offline | grey_1 | `eye_closed`: a closed eye with lashes |
| trashcan | red_1 | `bin`: a grey waste bin with a lid |
| ender_chest | purple_1 line on the **purple-tinted panel** (`ENDER_PANEL_RAMP`: purple_1 panel, purple_0 dark bevel) | `ender`: a purple orb with a green core |
| crafting | none | none: the plain vanilla crafting look |
| template_chest_1..6 | none | none: plain |

The ender chest panel is a *tint*, not a dark sheet: the live title and
"Inventory" text must sit on light art, so `purple_1` (luminance 187) is the
darkest panel that still passes the light-band rule; the dark purple lives in
the bevel, the accent and the pictogram.

## 6. Background anatomy

Backgrounds are 176 wide (chest heights 132-222; dispenser and crafting
176x166). `compose.base_background(key, seed)` paints the canonical version;
`evidence/faithful/reference/background-anatomy.png` labels it.

| Zone | Rows / columns | Content |
|---|---|---|
| outline | outer 1 px | `ink_0`, radius-2 notched corners |
| bevel | 1 px inside the outline | `grey_7` on the top and left, `grey_1` on the bottom and right, plus the inner corner pixel of each (white top-left, dark bottom-right) |
| panel | everything else | flat `grey_6` (`purple_1` on the ender chest) |
| title rows | x 8-167, rows 5-13 | plain panel: the live title (vanilla dark grey #404040) lands here |
| accent line | row 14, x 8-167 | the family accent (section 5), plain panel pixels only |
| well trays | round content clearances | the inset of section 4.1 |
| inventory rows | label_y-1 .. label_y+7 | plain panel: the live "Inventory" label; the player tray's dark top run sits below it |
| player trays | 36 player clearances | main 3x9 and hotbar 1x9 framed separately (the 4 px seam between them is panel) |
| static cells | `staticProtectedSlots` | plain panel, plus one pictogram tile in the largest region |
| under buttons | button rects | plain panel |
| pin | x 175, rows 0-2 | alpha 255 (the outline / bevel pixels; `compose.finish_background` stamps `ink_0` if needed) |

**The light-band rule is a hard contract.** The live vanilla title at the
title anchor (x=8, y=6; crafting x=29) and the live "Inventory" label must
sit on light art: on the glyph rows the mean luminance must be at least 180
with at most 8 % dark pixels (luminance < 120). The Faithful panel (198)
satisfies this by construction; never put a dark motif, a tray edge or an
accent line on those rows. `validate.py --style --theme faithful` and
`selftest.py` check exactly this.

trade_money is the dispenser exception: its centred title contains only the
art, so the background carries the static label OFFERED MONEY in PLAIN
`ink_1`, centred on x=88 at row 6, like a vanilla title
(`base_background` does this automatically on the dispenser layout). Every
other skin, and every frame, gets no painted title. Crafting's title anchor
is x=29 and its recipe-book toggle [4,33,22,20] and arrow [88,30,28,24] stay
transparent with no frame drawn round them, so the client's own toggle and
arrow show unchanged (the plain vanilla crafting look).

## 7. Frame anatomy

Vanilla has no outer frame, but the contract requires 54 frame textures
(256 wide, at artLayers x=-40, y=-8, height = container + 16) that are opaque
at the pin (w-1, h//2), end at x = w and keep the native container
transparent. The Faithful treatment is a **side-panel extension in the vanilla
bevel language**, like panels docked to the sides of a container screen.
`compose.base_frame(key, layer_id, seed)` paints it;
`evidence/faithful/reference/frame-anatomy.png` labels it.

| Zone | Size | Content |
|---|---|---|
| panel | the whole 256 x h layer | one `bevel_panel`: `ink_0` outline with radius-2 notched corners, `grey_7` top/left bevel, `grey_1` bottom/right bevel, flat `grey_6` (`ENDER_PANEL_RAMP` on the ender chest) |
| container | x 40-215, y 8 .. h-9 | fully alpha 0 (`geometry.clear_frame_container`) |
| drop shadow | 1 px right of and below the container | `grey_1` |
| grooves | columns 34-35 and 220-221, rows 4 .. h-5 | a recessed groove (`grey_1` then `grey_7`) that sets each side panel apart from the rim round the container: the panels read as docked |
| side panels | x 0-33 and 222-255 | one 24x24 recessed tile (`inset_box`, panel fill) centred, its top 4 px below the container top, holding the family pictogram; nothing else. Plain skins (templates) carry no tile |
| top / bottom strips | 8 px each | the bevel only |
| pin | (255, h//2) | alpha 255 on the outline (`compose.finish_frame`) |

Outside the container a frame is opaque everywhere except the 3 notched
pixels in each corner. A transparent pixel anywhere else is a hole through
which the game world shows; `validate.py --style` reports it.

**Frames carry no words.** The only painted title in the pack is OFFERED
MONEY, so the artLayers `heading`, `leftHeading` and `rightLines` are design
notes only. `side_tile(text=...)` and `heading_plaque(text)` can letter TINY
`ink_1` if the art director ever asks; nobody should use them otherwise.
Frames have no click targets. Crafting and trade_money have no frame.

## 8. The "no lies" rule

Textures are static; game state is live. Never bake in:

- prices, balances, amounts, page numbers, counts, dates or durations other
  than a control's own label (the auction "1 Day" ... "15 Days" buttons are
  their labels);
- player, shop, guild or item names;
- fake items, item icons or stack counts in any well or display slot;
- words a control does not own. Button lettering comes only from
  `button-layouts.json` `lines` (preferred) or `label`
  (`geometry.Button.text_lines`); `compose.letter` will not render anything
  else. Mixed case of the label (e.g. "Previous") is allowed for fit;
- controls that are not controls: no fake tabs, fake buttons or fake slots
  on frames or static cells (a pictogram tile is recessed and has no label,
  so it never reads as pressable).

A coin is a pictogram, never a balance.

## 9. Typeface

Two original faces, hand-authored as sprite strings in
`tools/faithful/lettering.py` (specimen:
`evidence/faithful/typeface-specimen.png`). Nothing is traced from the
game's font or any other font (section 0).

| | PLAIN (labels) | TINY (tight fits, counts) |
|---|---|---|
| style | an even, unadorned pixel sans meant to sit beside the game's own text | compact capitals |
| cap height | 7 | 5 |
| x-height | 5 (rows 2-6) | uppercase only |
| descender | 2 (rows 7-8) | none |
| widths | capitals 5 px except I (3); lowercase mostly 5 (c f k r s 4; j t 3; l 2; i 1) | 3 px (M W 5, N 4, 1 2) |
| tracking | 1 px | 1 px |
| word space | 3 px space glyph: 5 px of air between words | 1 px space glyph: 3 px of air |
| own traits | pointed A; true mid-height crossbars and bowl joins on row 3 of 7 (B E F H P R); open flat-ended C G S 3 5 c s (no terminal hooks); rounded D; slashed 0; flat-topped 1 with a full-width base; single-storey a with a stem; footed l | flat-topped digits, open S |
| charset | A-Z, a-z, 0-9, space + - = $ . , : ; ! ? / ' " ( ) [ ] < > % & # * _ (87 glyphs) | A-Z, 0-9, space + - = $ . , : ! ? / ' & < > ( ) % # * (56 glyphs) |

Kerning pairs (-1): PLAIN LT LY LV TA AT T. T, Y. P. F. FA L' r. r, (14
pairs); TINY LT T. (2 pairs). `lettering.audit_kerning(face)` renders every
pair at 1x and reports any 8-neighbour contact; `selftest.py` fails on one.
PA was tried and removed (P's bowl meets A's shoulder on row 2). Add a pair
only after the audit passes.

Coordinates: `draw_text(img, x, y, s, color, shadow=None, outline=None,
face='plain')` puts the top of the cap height at y; the baseline is
`y + cap_height - 1`. API: `text_width(s, face)`, `text_height`, `fits`,
`draw_text`, `draw_text_centered(img, cx, y, s, ...)`,
`draw_lines_centered(img, box, lines, ...)`, `fit_face(s, max_width)`,
`charset`, `audit_kerning`, `specimen()`. The other themes' face names are
aliases: 'hearth' and 'graven' -> 'plain', 'sprig' and 'rune' -> 'tiny'.

Required fits (checked by `selftest.py`): LISTINGS 43/50, DISABLE LISTING
81/104, PURCHASE 47/50, 12 DAYS 39/68. `compose.letter` tries PLAIN capitals,
then PLAIN mixed case of the label, then TINY capitals. Every one of the 157
labels fits: 126 regions use PLAIN capitals, 4 PLAIN mixed case (Previous,
Sell Price), 10 TINY (PRIVACY on its 36 px button and the two-line labels on
18 px buttons: CHEST / SHOPS, YOUR / MONEY, THEIR / MONEY), and 17 are icons.

Labels are centred on their full glyph extent: a mixed-case label with a
descender sits one row higher, so the descender clears the bottom bevel.

Colours: `grey_7` with an `ink_1` shadow on stone (primary, secondary,
danger, page); `ink_1` without shadow on info plates and the panel; `grey_5`
when disabled.

## 10. Quality bar

`python tools/faithful/paint_example.py` paints a throwaway set into
`evidence/faithful/example/` (never pack-source): the whole economy_hub
screen (background, all 8 buttons in six states, frame) and a
template_chest_3 background and frame, validates them with the builder's own
validators plus the palette, light-row and frame-hole checks, and writes
`evidence/faithful/example/preview.png`. Match it: a calm light grey panel
with crisp black notched outline and 1 px bevels, inset trays that frame the
vanilla slots, stone buttons whose white shadowed labels read at a glance, a
gold-edged primary, a muted red danger, recessed read-only plates, one thin
gold line under the title, and docked side panels carrying one small coin
tile each. If your screen looks busier, darker, more colourful or more
textured than the example, it is not done: take something away. Open your
preview PNG next to it before you hand in.

## 11. Validator rules (plain language)

`python tools/cozy/validate.py <skin>... | --all` runs the builder's own
functions (`build_pack.validate_png`, `button_assets.validate_button`,
`decorative_assets.validate`) on pack-source and prints one PASS/FAIL line per
asset; `--isolated-build` also runs the real build in a temp copy. Never run
build_pack.py in the shared tree. Add `--theme faithful` (or set
`QUASAR_GUI_THEME=faithful`; the flag wins) so `--style` / `--strict-style`
lint against the Faithful palette. The contract checks are identical for
every theme.

| Texture | Rule | Helper that satisfies it |
|---|---|---|
| background | RGBA, exact size (176 x layout height) | `compose.new(s.width, s.height)` |
| background | every content-well clearance (slot x-2, y-2, 20x20), all 36 player clearances and the crafting extras are fully alpha 0 | `geometry.clear_background_masks` (inside `compose.finish_background`), called last |
| background | advance pin [175,0,1,3] is alpha 255, so the opaque bbox ends at x=176 | `geometry.stamp_background_pin` (inside `compose.finish_background`) |
| button | RGBA, exact region size (18x18 ... 108x18) | `compose.new(b.w, b.h)` |
| button | the pin `geometry.skin(k).button(id).pin` is alpha 255 and nothing is opaque right of its column (the 18x72 balance pin is (16,36): column 17 belongs to the listing clearances) | `geometry.stamp_button_pin`, `clear_button_masks` (inside `compose.finish_button`) |
| button | every content/player clearance that overlaps the region is alpha 0 inside it (`button.masks`, button-local). Paint into `button.body`, which already excludes trimmed edges | `geometry.clear_button_masks` |
| button | all six states share the normal frame's alpha | `compose.button_states` (transforms never change alpha) |
| frame | RGBA, exact size (256 x container height + 16) | `compose.new(a.w, a.h)` |
| frame | pixel (w-1, h//2) alpha 255 and the bbox ends at w | `geometry.stamp_frame_pin` (inside `compose.finish_frame`) |
| frame | the whole native container rectangle is alpha 0 | `geometry.clear_frame_container` |
| all | 8-bit RGBA PNG, no resampling | `compose.save_png` |

Use `compose.finish_background / finish_button / finish_frame` (or pass
`compose.PIN` to the geometry functions): geometry's own default pin colour
name resolves through whichever palette module is loaded, so the Faithful
wrappers pass an explicit `ink_0`.

Style lint (`--style --theme faithful`, non-fatal unless `--strict-style`):
Faithful palette only (pure black and white allowed), no semi-transparent
pixels (alpha strictly between 0 and 255) in any texture, light title /
inventory glyph rows (mean luminance >= 180, <= 8 % dark pixels), and, for
every frame, no pixel with alpha < 255 outside the native container rectangle
and the rounded rim corners. Until the Faithful art is painted, pack-source
still holds the Soulrend textures, so off-palette warnings are expected; the
contract checks must pass regardless.
