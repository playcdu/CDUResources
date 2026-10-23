# Soulrend style guide

This guide defines the Soulrend theme: a dark-fantasy, souls-like replacement
for every texture in the pack, made for the Soulrend modpack. It covers 60
backgrounds, 1014 button-state PNGs (169 regions x 6 states) and 58 outer
frames. Geometry, codepoints and interaction contracts are frozen; only the
pixels change. The shared tooling lives in
[tools/soulrend/](../tools/soulrend/README.md), and every rule below names the
helper that satisfies it. Geometry, masks, pins and validation are the
theme-agnostic ones in `tools/cozy/geometry.py` and `tools/cozy/validate.py`;
they are imported, never copied.

Reference drawings are generated, not committed (evidence/ is gitignored).
Regenerate them with:

```sh
python tools/soulrend/render_references.py   # evidence/soulrend/reference/*.png + typeface specimen
python tools/soulrend/paint_example.py       # evidence/soulrend/example/preview.png (quality bar)
```

Use the pinned interpreter
`C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
for every command in this guide, run from the repository root.

The modpack's own art (its GUI pack, its title logo, its menu background and
its fonts) was used for mood and palette only. Not one pixel, glyph or sprite
is copied or traced from it; everything here is original and CC0-1.0.

## 1. Direction

**A ruined cathedral and its dungeon, lit by a single bonfire.** The player
opens a dark umber ledger bound in blackened iron that rests in a niche of
mossy slate. Bone-white vellum strips carry the writing; tarnished gold edges
the important plates; blood-red cloth and wax mark what is dangerous; ember
light pools around candles and braziers; a cold cyan soul-light appears only
where something is chosen or magical. Weighty, quiet, elegant, a little
decayed. Tasteful: no gore, no skull piles. A single small bone or a worn
gargoyle is the most macabre it gets.

Rules of thumb:

- Light is cold and comes from the top-left. Highlights sit on top/left edges
  (iron_2/iron_3, stone_3, gold_2, vellum_3); shadows are deep and sit on the
  bottom/right (ink_0, iron_0, stone_0).
- Every object has a deliberate 1 px warm near-black ink outline (ink_1).
  Bottom and right edges may switch to ink_0 for weight.
- Surfaces are flat colour with a few hand-placed marks: a scuff, a hammer
  pit, a chipped block corner, a hairline crack, a moss tuft. No gradients, no
  noise.
- The live text bands are light vellum, always. Item wells are calm. All the
  story lives in frames, static panels and the edges of controls.
- Colour discipline: the sheet is umber, the walls are stone, metal is iron,
  emphasis is gold, danger is blood, warmth is ember, magic is soul. Soul-cyan
  is a spice: the selected state, a scrying glass, a rune. Never a fill.

## 2. Master palette

One palette of 36 colours in eleven ramps, every ramp dark to light. There is
no pure black and no pure white. Source of truth: `tools/soulrend/palette.py`
(`NAMED`, `RAMPS`, `rgba('iron_2')`). Swatch sheet:
`evidence/soulrend/reference/palette.png`.

| Ramp | 0 (dark) | 1 | 2 | 3 (light) | Use |
|---|---|---|---|---|---|
| ink | `ink_0` 18,13,14 | `ink_1` 31,22,22 | `ink_2` 47,34,32 | | outlines (ink_1), heavy edges, lettering on vellum and stone, shadows (ink_0), soft lines (ink_2) |
| iron | `iron_0` 40,42,49 | `iron_1` 62,66,75 | `iron_2` 96,101,110 | `iron_3` 146,150,156 | blackened iron plates, bands, rivets, chains; also the disabled tones |
| stone | `stone_0` 37,46,44 | `stone_1` 55,66,62 | `stone_2` 80,93,85 | `stone_3` 113,124,111 | mossy slate masonry (frames), socket walls, carved tablets |
| umber | `umber_0` 39,29,26 | `umber_1` 51,38,33 | `umber_2` 70,52,44 | `umber_3` 98,74,59 | the menu sheet (umber_1), leather, wood, scuffs |
| vellum | `vellum_0` 166,148,118 | `vellum_1` 198,184,154 | `vellum_2` 222,210,184 | `vellum_3` 238,230,210 | text bands and secondary strips (body vellum_2), highlights, fibres, folds |
| blood | `blood_0` 78,18,24 | `blood_1` 126,30,34 | `blood_2` 176,48,44 | | danger cloth, wax seals, banners, gems |
| ember | `ember_0` 172,76,28 | `ember_1` 228,126,44 | `ember_2` 250,190,104 | | flames, glow stipple, pulse rings |
| soul | `soul_0` 22,90,102 | `soul_1` 52,174,188 | `soul_2` 158,234,236 | | selected rim, scrying glass, runes (sparing) |
| gold | `gold_0` 98,74,36 | `gold_1` 152,118,54 | `gold_2` 204,168,92 | | primary rims and lettering, filigree, coins, rivets |
| moss | `moss_0` 34,50,36 | `moss_1` 56,80,50 | `moss_2` 92,114,66 | | moss tufts, green banners |
| void | `void_0` 34,24,46 | `void_1` 74,50,100 | | | the ender chest sheet only |

Semantic aliases: `OUTLINE = ink_1`, `OUTLINE_DEEP = ink_0`,
`TEXT_DARK = ink_0` (on vellum and stone), `TEXT_LIGHT = vellum_3` (on blood
and umber), `TEXT_GOLD = gold_2` (on iron), `SHADOW = ink_0`,
`GLOW = ember_2`, `SOUL_GLOW = soul_1`, `TITLE_BAND = vellum_2`,
`SHEET = umber_1`. `VOID_SHEET` (ink_1, void_0, void_1, iron_2) replaces the
umber ramp for the ender chest sheet (`compose.sheet_for`).

Only palette colours may appear in a texture, with alpha 0 or 255.
`validate.py --style --theme soulrend` reports off-palette, pure black/white
and semi-transparent pixels; `palette.snap(img)` pulls stray colours back.
Nothing from the cozy palette is reused.

## 3. Hand-drawn feel

Do:

- **Deliberate outlines.** 1 px ink_1 round every object
  (`ink_outline(radius=1)`); bottom/right may be ink_0 (`heavy='br'`). Line
  weight varies on purpose: `ink_line(weight=2)` doubles a stroke on its
  shadow side.
- **Cold, broken highlights.** One pixel on the top/left edge, broken here and
  there so it looks placed (`highlight_edge(broken=6)`), plus a 2-4 px iron_3
  glint on metal (`iron_plate`).
- **Deep shadows.** Bottom/right edges in ink_0 or the darkest ramp step
  (`shadow_edge`, `bevel`); a 2 px cast shadow where the sheet meets the wall
  (`base_frame`).
- **Sparse dithering, only where light falls off.** Candle, brazier and soul
  light pool by ordered dither in three bands (`glow`), with a warm (ember_0) or
  cold (soul_0) stipple on the darkest pixels near the source. Stone grain is
  masonry, not dither. Never dither a whole surface.
- **Irregular forged things.** Chain links alternate face-on and edge-on and a
  few sit 1 px off the line (`chain`); cracks step in short irregular runs
  (`crack`); vellum edges are hand-cut (`vellum_strip(deckle=)`); paper tears
  jag (`torn_edge`); banners end in a ragged swallowtail (`banner`).
- **Cuts reveal, they never punch holes.** Every edge-cutting helper (deckled
  vellum, `torn_edge`, `page_curl`, banner tatters) shows what was painted
  under the surface in the cells it cuts: the wall on a frame, the sheet on a
  background, alpha 0 only on an empty button. `vellum_strip` records its
  backdrop automatically; before painting paper by hand, call
  `P.remember_backdrop(img, box)` (or pass `under=` a snapshot) so a later
  tear knows what to show. `behind=<colour>` still forces a flat fill.
- **No cut under a label.** Deckle notches and tears are recorded as they are
  cut; `compose.letter` undoes any of them in the label's columns plus 1 px
  either side before it letters, so a descender or the pulse ring never sits
  over a notch.
- **Masonry with intent.** Ashlar courses of 7-16 px blocks, mostly stone_1,
  some stone_2, a rare sunken stone_0 block, chipped corners, a crack, moss
  that grows more often toward the damp bottom (`stone_blocks(moss=)`). Tune
  the seed until the wall looks right, then keep it.

Forbidden:

- gradient fills, soft brushes, anti-aliasing or semi-transparency;
- per-pixel procedural noise (random speckle, Perlin, etc.);
- symmetric compositions made by mirroring one half and pasting it (small
  sprites such as a corner scroll may be flipped for the opposite corner);
- the old generated lettering (the 5x7 `LETTERS` in tools/button_assets.py,
  the 3x5 `PIXELS` in tools/sample_art.py, the OFFERED MONEY bitmap in
  tools/build_pack.py), the cozy palette, the cozy HEARTH/SPRIG faces and any
  cozy sprite (the cozy toolkit may be reused for geometry, validation and
  preview only);
- gore, blood splatter, skull piles; soul-cyan used as a fill;
- third-party pixels of any kind, including the modpack's own GUI, title and
  font assets. Every glyph, sprite and motif is original (CC0-1.0).

## 4. Shared visual grammar

Every painter uses the same grammar. `compose.paint_button` and
`compose.base_background` implement it; hand touches go on top. Reference
sheets: `evidence/soulrend/reference/buttons.png` (every grammar in six
states), `wells.png`, `icons.png`, `primitives.png`.

### 4.1 Empty item well: iron-framed stone socket

A well is a recessed socket whose 20x20 centre (the clearance) is fully
transparent so the vanilla slot shows through and reads as empty. Adjacent
clearances overlap (18 px pitch, 20 px clearance), so a grid is one merged
socket and only its outside edge is framed. Anatomy, measured outward from the
hole (`primitives.well_frame`, Chebyshev distance d):

| Ring | Pixels |
|---|---|
| hole | alpha 0, never painted (`well_frame` cannot write there) |
| d1 | ink_0 lip on every side: the sharp inner edge of the socket |
| d2 | stone wall: stone_0 on the top and left walls (in shadow), stone_3 on the bottom and right walls (catching the cold top-left light) |
| d3 | raised iron frame: iron_2 on its top/left runs, iron_0 on its bottom/right runs; iron_3 rivets at every outer corner and wherever an 18 px slot seam meets the frame |

`socket_well` is the default; `carved_well` swaps the iron ring for a
chiselled stone lip (one step lighter top/left, darker bottom/right of what is
underneath) and is used for the crafting recipe-book toggle and arrow. Pass
the text bands as `protect`: inside them only the d1 lip is drawn, keeping
the glyph rows light. Build hole lists with `P.merge_holes(skin.content_slots)`
and `P.merge_holes(skin.player_slots)`. Fake items, shading or patterns inside a
well are forbidden.

### 4.2 Primary button: blackened iron plate, gold rim

`compose.primary_face` / `primitives.iron_plate(rim='gold')`. From the outside
in: ink_0 outline (radius 1); a 1 px tarnished-gold rim (gold_2 top/left,
gold_1 corners, gold_0 bottom/right); a raised inner bevel (iron_2 top/left,
ink_1 bottom/right); an iron_1 body with a few seeded iron_0 hammer pits and a
3-4 px iron_3 glint at the top-left; 2x2 gold rivets in the inner corners when
the plate is at least 26x12. Lettering: GRAVEN gold_2 with an ink_0 shadow at
(+1, +1). Text box: the body inset 4 px left/right and 3 px top/bottom (46 px
wide on a 54 px plate, so CONFIRM / PURCHASE fits in GRAVEN).

### 4.3 Secondary button: riveted vellum strip

`compose.secondary_face` / `primitives.vellum_strip`. A vellum_2 strip with a
vellum_3 top row, vellum_1 bottom row, sparse vellum_1 fibres, an ink_1 rim
(ink_0 bottom/right) and hand-cut (deckled) top and bottom edges. Strips at
least 30 px wide are pinned at both ends by a 3 px iron rivet. Lettering:
GRAVEN ink_0, no shadow. Fit order: GRAVEN with rivets, GRAVEN without rivets,
RUNE with rivets (`paint_button` decides).

### 4.4 Danger button: blood cloth with iron studs

`compose.danger_face` / `primitives.cloth_panel`. Heavy blood_1 cloth with a
broken blood_2 gloss on the top row and down the left, a blood_0 bottom row,
vertical folds every 10-14 px (a blood_0 crease with a blood_2 ridge), an
ink_0 rim heavy at the bottom and 3 px iron studs in the corners when at least
24x10. Lettering: GRAVEN vellum_3 with a blood_0 shadow. The 18x18 close
control is a round blood-wax seal studded with four iron studs and pressed with
a 2 px X (`icons.close_seal`).

### 4.5 Info (read-only): carved stone tablet

`compose.info_face` / `primitives.stone_tablet`, used for every `role: info`
region with a label (balance, stats, stock, quantity, bid, other money, create
shop). A flat stone_3 face whose bevel runs INWARD (stone_1 on the top/left
inner edge, stone_2 under it) with two chisel marks: it is cut into the wall,
not raised, so it never reads as pressable. No rivets, no rim highlight.
Lettering: GRAVEN ink_0, as if incised. Info icons (balance pouch, rank crest)
sit on the same tablet.

### 4.6 Page-turn controls: torn vellum page with a curl

Buttons with id `previous` / `prev` / `next` are vellum strips torn along the
top (`torn_edge(depth=1)`) whose corner curls the way the page turns:
bottom-right for next, bottom-left for previous (`primitives.page_curl`, 5-6
px). On buttons the corner beyond the fold is transparent; on frames and
backgrounds pass `behind=` a colour so no hole opens. The fold is ink_1; the
flap shows the underside in vellum_1 with a vellum_3 crease, an ink outer edge
and an ink_0 tip. Lettering GRAVEN ink_0 on the side away from the curl.

### 4.7 States

The server picks one of six PNGs per region. Paint `normal` by hand, then
derive the rest with the shared transforms (`compose.button_states`, which
calls `primitives.make_state`). Every transform keeps alpha byte-identical, so
masks and pins survive, and every lettering pixel keeps its position and
alpha. Selected and the pulses never change lettering at all; disabled dims
it in place.
Hand-adjust afterwards if needed and pass the result through
`button_states(..., overrides={'selected': img})`.

| State | Transform | Reads as |
|---|---|---|
| normal | as painted | at rest |
| disabled | `make_disabled`: every non-ink face pixel is mapped by luminance onto three flat cold tones, ink_1 / iron_1 / iron_2 (thresholds 42 / 88): gold, blood and vellum go dead, bevels flatten, glints vanish. **The lettering is dimmed too**: each glyph pixel keeps its exact position and alpha but is recoloured into the dead-stone lettering register (light lettering such as gold_2 or vellum_3 becomes iron_3, dark non-ink lettering ink_1, ink stays ink), so a disabled primary reads grey-on-grey, never gold-on-grey; the same applies to GRAVEN and RUNE labels on secondary, danger, info and page faces. Two short ink_1 hairline cracks are scored across the face; every crack pixel keeps two clear pixels from the lettering (Chebyshev distance >= 3, `CRACK_CLEAR`) and any remnant shorter than 3 px after that clipping is dropped, so a crack never reads as a stroke of a glyph. The close seal uses `make_disabled_seal`: blood wax cools to iron_0/1/2, the X keeps its ink | cold grey stone, label included: dim, clearly inert, still legible |
| selected | `make_selected`: every non-ink colour except the lettering and its 1 px border moves one ramp step lighter (raised); the first interior ring becomes a soul-cyan rim (soul_2 on the top/left runs over dark surfaces, soul_1 elsewhere, soul_0 on the bottom/right runs); a 3 px soul sparkle in the top-right interior | lit by soul-light, raised |
| pulse_1 | `make_pulse(img, 1, protect)`: a bright ember ring 3 px in from the edge; unlettered faces (icons, seals) also warm one step in the core | the bonfire flares |
| pulse_2 | `make_pulse(img, 2, protect)`: the ring expands to 2 px in; afterglow (one step lighter) where it was | the glow spreads |
| pulse_3 | `make_pulse(img, 3, protect)`: a faint checker-dithered ring 1 px in (ember_0 on dark, ember_1 on light), afterglow at 2 px | fading; the next frame is the resting state |

**Pulses and selected never touch lettering; disabled only dims it.** `button_states` finds the button's own
lettering in the painted normal frame with `compose.lettering_mask`, from
the label geometry rather than by guessing shapes: (1) the exact glyph pixels
`compose.letter` drew on that image; else (2) a whole-label template search
(the label's own lines, face and spacing; at least 90 % of its pixels in one
colour), which finds lettering on copies and in hand-chosen boxes; only for
genuinely hand-lettered labels (3) the old word / character shape search,
whose hits on the outline and first inner ring are discarded, so a rim or a
clipped corner can never pass for a "1" or an "I" and squeeze the pulse
rings. The 1 px halo round the lettering is always kept in full, even within
2 px of the texture edge, so a pulse ring never touches a descender over a
torn edge.
Selected and every pulse frame keep the glyphs plus that 1 px border (which
holds the text shadow and contrast ring) exactly; disabled recolours the
glyph pixels in place as described above. When lettering comes
closer than 4 px to the edge, as on most 18 px tall buttons, the three ring
depths are compressed into the free band between edge and letters
(`pulse_depths`: 3/2/1 px with room for three, 2/1/1 with room for two,
1/1/1 with room for one), so the glow runs only along the outer rows and
columns. With room for one ring (two RUNE lines or a descender on an 18 px
button) pulse_2 cannot move outward, so it alternates bright and afterglow
pixels along the ring and spreads an afterglow one ring further in (never
onto the lettering halo): the three pulse frames always differ, and
`selftest.py` fails if any two of a button's six states are identical. Letter with `lettering.draw_text` or `compose.letter` so the
detector can find your text; `selftest.py` fails if a lettered button has no
detectable lettering, if selected or a pulse changes a lettering pixel, or if
a disabled lettering pixel moves, changes alpha or keeps a live colour (gold,
vellum, blood, ember, soul).

Ring colour always contrasts with its surface (`glow_colour`): ember_1 on
light vellum and on dark iron, cloth and stone, ember_2 on gold and mid
tones. Ink (outlines and ink lettering) never changes in any transform. Pulses
play once (4 ticks a frame, no repeat) and end on the resting look; there is
no hover state.

### 4.8 Icons

Icon buttons are 18x18 (the body may be trimmed to 17 px by a neighbouring
clearance). Action icons (search, settings) sit on a vellum square; read-only
icons (balance, rank) sit on a carved stone tablet. The icon is centred. All
sprites are in `tools/soulrend/icons.py` and drawn in
`evidence/soulrend/reference/icons.png`.

| Icon | Drawing |
|---|---|
| close | round blood-wax seal (diameter 17, right-aligned so the pin column is wax), irregular ink_0 rim, blood_2 lit crescent, four iron studs on the diagonals, a pressed 2 px X: ink_0 strokes with a blood_2 lip below-right |
| balance | 12x15 umber leather coin pouch hanging on two iron chain links, gold drawstring, a tarnished coin peeking out at its foot. The 18x72 balance column is a tall stone tablet with the pouch on a short chain near the top, three gold coins below and an iron rivet at the foot |
| search | 12x12 scrying lens: iron ring, deep soul_0 glass with a soul_1/soul_2 glint, iron collar, umber grip to the lower right |
| settings | 13x13 forged iron cog, eight teeth, black axle, lit top-left |
| rank (label-only 18x18 info control) | 11x16 heraldic crest: a gold-bordered blood shield with a gold chevron under a small three-pointed iron crown |

The rank control has no `icon` field; the crest stands in for its label (no
invented words). Seal emblems (`icons.EMBLEMS`: x, cross, crown, tower, coin,
key, flame, check) are 5x5 and only used on seals of radius 5 or more.
Heraldic crests (`icons.CRESTS`: chevron, cross, tower, flame, key, moon) are
9x11 shields for banners, seals and the prefixes wall.

Motifs for frames and static art (`icons.MOTIFS`, `draw_motif`): goblet,
gavel, scales, ledger, crate, lantern, key, anvil, hammer, tongs, brazier,
mirror, satchel, bone, writ, candle_clock, coin_stack, gargoyle. Primitives add
candles (`candle`), banners (`banner`), chains (`chain`), arches
(`arch_niche`), gold filigree (`gold_filigree`: corner, scroll, fleur,
flourish), moss (`moss_tuft`), cracks and glow.

## 5. Per-family identity

The base (umber sheet, iron, vellum, stone, ink) is shared everywhere. Each
family adds an accent ramp and a secondary ramp, used only in decorative
regions: frames, static protected slots, the area under or around buttons,
never in wells, text bands or lettering areas (`palette.FAMILY_ACCENT`,
sub-skins in `SKIN_ACCENT`, lookup with `accent_for(key)`).

| Family / sub-skin | Accent | Secondary | Identity motifs (decorative regions only) |
|---|---|---|---|
| economy | gold | ember | torchlit counting vault: coin scales, coin stacks, a ledger closed with a wax seal, a sconce |
| auction | blood | gold | auction block and gavel, banner tags hanging on chains, a candle clock |
| chest_shop | ember | umber | merchant stall under a stone arch, iron-banded crates, an iron lantern |
| trade | gold | blood | two goblets on a stone table, a chain-link handshake knot between the two sides |
| ticket | blood | gold | a wax-sealed writ of passage |
| ticket_valid | blood | gold | the writ closed with an intact blood seal |
| ticket_invalid | ember | iron | the writ burnt and torn (`torn_edge(burnt=True)`), seal broken |
| admin_shop | iron | gold | quartermaster's armoury rack: hammer, tongs, shields on pegs |
| guild_bank | iron | moss | iron vault door, chains, a guild heraldic banner |
| prefixes | gold | blood | heraldic shields (`icons.CRESTS`) and iron name plates on a stone wall |
| invsee | soul | umber | scrying mirror / soul-lens hovering over a leather satchel |
| invsee_offline | iron | soul | the same satchel, cold blue-grey and unlit: no ember, no soul glow |
| trashcan | ember | iron | ash-pit brazier with dying embers (ember_0 stipple) and burnt leaves |
| ender_chest | void | soul | obsidian sheet (`VOID_SHEET`), void-purple, soul-cyan runes |
| crafting | iron | ember | blacksmith's anvil and tool rack (anvil, hammer, tongs) |
| plot (plot_buy, plot_rent, plot_list, plot_manage) | moss | blood | land claimed and recorded: wooden boundary stakes tied with blood rags, a surveyor's chain with brass tallies, a sealed land writ (survey deed with rolled ends, compass rose and a dashed parcel corner; pendant seal pressed with a stake), a carved stone waymarker cut with a benchmark. Buy/rent: the plot preview (slot 22) sits in a socket cut into the waymarker's head; rent alone hangs a brass key from the stone's ring and presses a key into the seal. List: wells stay plain, the frame holds a rack of rolled writs. Manage: a small waymarker between two stakes straddles static cells 22-23 (`tools/soulrend/paint_plots.py`) |
| template_chest_1..6 | iron | stone | plain dark stone and iron framing: the default look, no story |

Motifs never enter item wells, the title text rows, the inventory text rows or
button lettering areas.

## 6. Background anatomy

Backgrounds are 176 wide (chest heights 132-222; dispenser and crafting
176x166). `compose.base_background(key, seed)` paints the canonical version;
`evidence/soulrend/reference/background-anatomy.png` labels it.

| Zone | Rows / columns | Content |
|---|---|---|
| rim | outer 1 px | ink_0, radius 2 corners |
| iron band | 1 px inside the rim | blackened iron: iron_2 / broken iron_3 on top and left, ink_1 on bottom and right |
| sheet | everything else | flat umber_1 with a few hand-placed scuffs and pits (`umber_panel`); obsidian on the ender chest |
| title band | x 3-172, rows 2-14 | **light vellum strip** (vellum_2 body, vellum_3 top row, vellum_1 bottom row, deckled top edge, ink rim), held at both ends by 4 px iron clasps with a gold rivet (x 3-6 and 169-172, outside the live-text columns 8-167). Live title glyphs land on rows 5-13 |
| well grid | content clearances | merged holes framed as iron-framed stone sockets, protected inside the bands |
| inventory band | from the grid's lip row (or label y-1) to the row above the player grid's lip | **light vellum strip** held by iron clasps; the socket lips above and below frame it. Live "Inventory" glyphs land on rows y-1 .. y+7 |
| player grid | 36 player clearances | main 3x9 and hotbar 1x9 socketed separately; the 2-row seam between them carries both lips |
| side margins | x 0-5 and 170-175 | rim, iron band, one column of sheet, the 3-ring socket. Nothing else fits |
| corners | bottom-left / bottom-right | 6x6 blackened-iron L brackets (`corner_bracket`) |
| static panels | `staticProtectedSlots`, button rects | on sparse screens: stone tablets, vellum writs, family motifs, explanatory art without words that lie |
| under buttons | button rects | keep calm umber so rounded corners, torn edges and page curls read as the sheet behind |
| pin | x 175, rows 0-2 | alpha 255 (the rim pixel; `compose.finish_background` stamps ink_0 if needed) |

**The light-band rule is a hard contract, not a style suggestion.** The live
vanilla title (dark grey #404040) at the title anchor (x=8, y=6; crafting x=29)
and the live "Inventory" label must sit on light art. In this dark theme both
bands are bone-white vellum set into the dark sheet: on the glyph rows the
mean luminance must be at least 180 with at most 8 % dark pixels
(luminance < 120). `validate.py --style --theme soulrend` and `selftest.py`
check exactly this.

trade_money is the dispenser exception: its centred title contains only the
art, so the background carries the static label OFFERED MONEY in GRAVEN ink_0
on the vellum title band, centred on x=88 (`base_background` does this
automatically on the dispenser layout). Every other skin, and every frame,
gets no painted title. Crafting's title anchor is x=29 and its recipe-book
toggle [4,33,22,20] and arrow [88,30,28,24] stay transparent
(`base_background` frames them with a 2-ring `carved_well`).

## 7. Frame anatomy

Frames are 256 wide, at artLayers x=-40, y=-8, height = container + 16.
`compose.base_frame(key, layer_id, seed)` paints the canonical version;
`evidence/soulrend/reference/frame-anatomy.png` labels it. The sheet reads as
a ledger resting in a niche of dungeon masonry.

| Zone | Size | Content |
|---|---|---|
| wall | everything outside the container | mossy slate ashlar, 7 px courses (`stone_blocks(moss=0.10)`) |
| rim | outer 1 px | ink_0, radius 3 |
| iron border | 2 px inside the rim | iron_2/iron_0 bevel, then iron_1/ink_1; iron_3 rivets every 16 px |
| corners | 7x7 | tarnished gold filigree scrolls (`gold_filigree('corner')`) |
| container | x 40-215, y 8 .. h-9 | fully alpha 0 (`geometry.clear_frame_container`) |
| recess | 1 px round the container's top and left | ink_1, so the sheet sits in a cut niche |
| cast shadow | 2 px right of and below the container | ink_0 then stone_0 |
| top strip | 8 rows | iron border and a wordless heraldic plaque centred (blackened iron, gold rim, gold flourish, gold scroll ends); chains to the corners are a common hand touch |
| bottom strip | 8 rows | iron border; chains swagged between gold rivets, a fleur, a ledge |
| left / right panels | 40 px each | banners, sconces and candles with ember glow, an arch niche, ledges with goblets and ledgers, chains, a gargoyle corbel, family motifs |
| pin | (255, h//2) | alpha 255 on the rim (`compose.finish_frame`) |

Outside the container a frame is opaque everywhere except the 6 rounded rim
pixels in each corner. A transparent pixel anywhere else is a hole through
which the game world shows; `validate.py --style` reports it (below).

**Frames carry no words.** The brief allows only one painted title in the
whole pack (OFFERED MONEY), so the artLayers `heading`, `leftHeading` and
`rightLines` are treated as design notes: the heading becomes the wordless
plaque, the side headings become wordless heraldic banners (`side_banner`,
crest instead of text). `base_frame(heading=True)` and
`side_banner(text=...)` can letter in RUNE if the art director ever asks;
nobody should use them otherwise. Frames have no click targets. Crafting and
trade_money have no frame.

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
  else. Mixed case of the label (e.g. "Privacy") is allowed for fit.

Decorative vellum may carry ruled lines, seals and crests, never text that
looks like information. Readiness marks on the trade divider are icons
(check / dash, or a lit / unlit candle), not words. A coin stack is a motif,
never a balance.

## 9. Typeface

Two original faces, hand-authored as sprite strings in
`tools/soulrend/lettering.py` (specimen:
`evidence/soulrend/typeface-specimen.png`). Nothing is traced from the
modpack's medieval font or from any other font.

| | GRAVEN (labels) | RUNE (headings, tight fits, counts) |
|---|---|---|
| style | thin medieval serif | carved capitals |
| cap height | 7 | 5 |
| x-height | 5 (rows 2-6) | uppercase only |
| descender | 2 (rows 7-8) | none |
| widths | 1-5 px; capitals 5 (I 3, J and S 4) | 1-5 px; capitals 3 (M W 5, N 4) |
| tracking | 1 px | 1 px |
| word space | 2 px space glyph: 4 px of air between words | 1 px space glyph: 3 px of air |
| traits | inward foot serifs on A H K M N R; drooping T arms; spurred E F L; uncial C and G; chamfered D; flag serifs on lowercase ascenders and entry strokes on x-height stems; uncial a and u | chisel-cut bowls, pointed A, angular S and 0 |
| charset | A-Z, a-z, 0-9, space + - = $ . , : ; ! ? / ' " ( ) [ ] < > % & # * _ (87 glyphs) | A-Z, 0-9, space + - = $ . , : ! ? / ' & < > ( ) % # * (56 glyphs) |

Kerning pairs (-1): GRAVEN LT LY LV TA AT AV VA AY YA T. Y. P. F. To Ta Te
r. r, // PA FA (21 pairs); RUNE LT LY T. (3 pairs). Every kept pair leaves at
least one clear column between the two glyphs on every row and no edge or
corner contact, audited at 1x. WA, AW and LW (GRAVEN) merged the W's stroke
and the next foot into a 3 px blob (WATCH read smudged) and Tr touched
diagonally; RUNE YA / AY merged and TA / AT / LV touched; all were removed.
Add a pair only after rendering it at 1x and checking that rule.

Coordinates: `draw_text(img, x, y, s, color, shadow=None, outline=None,
face='graven')` puts the top of the cap height at y; the baseline is
`y + cap_height - 1`. API: `text_width(s, face)`, `text_height`, `fits`,
`draw_text`, `draw_text_centered(img, cx, y, s, ...)`,
`draw_lines_centered(img, box, lines, ...)`, `fit_face(s, max_width)`,
`charset`, `specimen()`. The cozy face names 'hearth' and 'sprig' are
accepted as aliases for 'graven' and 'rune'.

Required fits (checked by `selftest.py`): LISTINGS 41/50, DISABLE LISTING
78/104, PURCHASE 46/50, 12 DAYS 34/68. `compose.letter` tries GRAVEN capitals,
then GRAVEN mixed case of the label, then RUNE capitals; secondary strips drop
their rivets before falling back to RUNE. Every one of the 169 labels fits:
132 regions use GRAVEN capitals, 10 GRAVEN mixed case (Buy Price, Sell Price,
Decrease, Privacy, Opt 2, Create), 10 RUNE (only the two-line labels on 18 px
buttons: CHEST / SHOPS, YOUR / MONEY, THEIR / MONEY, TOGGLE / PREVIEW), and 17
are icons.

Labels are centred on their full glyph extent: a mixed-case label with a
descender (g j p q y) on an 18 px strip sits one row higher than its caps
alone would, so the descender clears the bottom edge and the pulse rings.

Colours: gold_2 with an ink_0 shadow on iron; ink_0 on vellum and stone;
vellum_3 with a blood_0 shadow on blood cloth; vellum_3 with `outline=ink_0`
on busy umber or stone.

## 10. Quality bar

`python tools/soulrend/paint_example.py` paints a throwaway set into
`evidence/soulrend/example/` (never pack-source): a chest_3 background on
template_chest_3 geometry, the 54x36 primary button economy_hub/auction in
all six states, and the 256x184 frame, validates them with the builder's own
validators plus the palette check, and writes
`evidence/soulrend/example/preview.png`. Match it or exceed it: crisp light
vellum bands set into a dark iron-bound sheet, calm sockets, deliberate ink
outlines, cold top-left highlights and deep shadows, warm light that pools by
dither around candles, a lantern and a brazier, sparing soul-light in a
scrying niche, and side panels that tell a quiet story (a green and a blood
banner with heraldry, a sconce, a niche with a soul mirror, a ledge with a
goblet, coins and a candle clock, a chained key, a ledger, a gargoyle, a
single bone, chains swagged across the strips). If your screen looks flatter,
emptier, brighter or noisier than the example, it is not done. Open your
preview PNG next to it before you hand in.

## 11. Validator rules (plain language)

`python tools/cozy/validate.py <skin>... | --all` runs the builder's own
functions (`build_pack.validate_png`, `button_assets.validate_button`,
`decorative_assets.validate`) on pack-source and prints one PASS/FAIL line per
asset; `--isolated-build` also runs the real build in a temp copy. Never run
build_pack.py in the shared tree. Add `--theme soulrend` (or set
`QUASAR_GUI_THEME=soulrend`; the flag wins) so `--style` / `--strict-style`
lint against the Soulrend palette. The contract checks are identical for
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
name resolves through whichever palette module is loaded, so the Soulrend
wrappers pass an explicit ink_0.

Style lint (`--style --theme soulrend`, non-fatal unless `--strict-style`):
Soulrend palette only, no pure black/white, no semi-transparent pixels (alpha
strictly between 0 and 255) in any texture, light title / inventory glyph rows
(mean luminance >= 180, <= 8 % dark pixels), and, for every frame, no pixel
with alpha < 255 outside the native container rectangle and the radius-3
rounded rim corners (the WARN line names the frame and the first offending
coordinates). Until the
Soulrend art is painted, pack-source still holds the cozy textures, so these
warnings are expected; the contract checks must pass regardless.
