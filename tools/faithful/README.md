# tools/faithful - Faithful theme toolkit

Shared Python 3.12 + Pillow modules for painting the Faithful (vanilla-style)
replacement of every menu background, button state and outer frame. The look
is defined in [docs/FAITHFUL-STYLE-GUIDE.md](../../docs/FAITHFUL-STYLE-GUIDE.md);
read it first, especially **section 0: no Mojang pixels**. Never open, sample
or trace a Minecraft jar, vanilla resource pack or screenshot. Geometry,
masks, pins and validation are the theme-agnostic modules in `tools/cozy/`
(`geometry.py`, `validate.py`, `preview.py`); they are imported, never copied.

Use only the pinned interpreter, from the repository root:

```sh
PY=C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

| Module | Purpose |
|---|---|
| `palette.py` | the 25-colour master palette (ink, grey, green, red, gold, blue, purple, rust; pure black/white allowed), `PANEL_RAMP` / `ENDER_PANEL_RAMP`, `FAMILY_ACCENT` / `SKIN_ACCENT` / `accent_for()` (accent ramp, pictogram, line on/off), `rgba()`, `step()`, `snap()`, `luminance()` |
| `lettering.py` | the original PLAIN (cap 7) and TINY (cap 5) faces: `text_width`, `draw_text`, `draw_text_centered`, `draw_lines_centered`, `fit_face`, `audit_kerning`, `specimen`; run it to write `evidence/faithful/typeface-specimen.png` |
| `primitives.py` | `bevel_panel`, `bevel`, `inset`, `ink_outline`, `stone_texture` (fleck count fixed by area), `stone_button` (plain / gold / red), `flat_plate`, `inset_box`, `accent_line`, `arrow_glyph`, `pictogram`, `pictogram_tile`; wells (`well_frame` with `clear` zones, `inset_well`, `merge_holes`, `tray_top_walls`, `tint_tray_walls`); state transforms (`make_disabled`, `make_selected`, `make_pulse`, `make_state`, `edge_distance`); backdrop/cut registry kept for Soulrend API parity |
| `icons.py` | icons (close X `draw_x`, balance coin with a slash, lens, cog, star, small coin), `icon_pixels`, family `PICTOGRAMS` (coin, gavel, chest, arrows, ticket / ticket_valid / ticket_invalid, shield, banner, nametag, eye / eye_closed, bin, ender), `draw_pictogram` |
| `compose.py` | the shared base look with Soulrend-identical signatures: `base_background`, `base_frame`, `paint_button` (on `aligned_body`, so button rows line up), `button_states`, `save_png`, `save_button_states`, `finish_background/button/frame`, `PIN`, plus `TITLE_ZONE` (rows 5-14: panel only), `bands`, `text_rows`, `draw_accent_line` (tints the trays' top/left walls), `wall_colour`, `frame_parts` (the lean frame's tabs and grips), `static_regions`, `pictogram_tile` (reference sheets only; backgrounds carry no tile), `side_tile` (`side_banner` / `side_tag` aliases), `heading_plaque`, `letter`, `label_layout`, `lettering_mask`, `extras_mask`, `state_masks`, `remember_extras`, `button_kind`, the `*_face` helpers |
| `paint_example.py` | the worked example and quality bar (writes only to `evidence/faithful/example/`) |
| `render_references.py` | regenerates the guide's reference drawings in `evidence/faithful/reference/` |
| `selftest.py` | proves geometry matches the manifests, the fits and kerning hold, and every default composition passes the builder validators, stays on palette, keeps the title zone (rows 5-14) and every static cell pure panel and the text rows light, tints a tray wall on every family skin, keeps frames to their lean tabs and grips, never lets selected or a pulse touch glyphs, dims them in place when disabled, finds them again on a copy, and keeps all six states distinct |
| `fixture_urls.json` | published gallery URLs for `build_fixtures.py --theme faithful` (empty until published) |

## Painter workflow

1. Write `tools/faithful/paint_<assignment>.py`. Import the modules directly:

   ```python
   import sys; from pathlib import Path
   _HERE = Path(__file__).resolve().parent
   sys.path.insert(0, str(_HERE))                      # faithful modules first
   for p in (str(_HERE.parent), str(_HERE.parent / 'cozy')):
       if p not in sys.path:
           sys.path.append(p)                          # tools/ and the shared geometry
   import compose as C, geometry as geo, primitives as P, icons, lettering as L
   from palette import GREY, GOLD, RED, GREEN, BLUE, accent_for

   KEY = 'economy_hub'
   s = geo.skin(KEY)
   bg = C.base_background(KEY, seed=11)          # panel, family-tinted tray walls; static cells plain
   ...nothing in static cells: backgrounds carry no pictogram (it lives on the frame tabs)...
   C.finish_background(bg, KEY)                  # clear masks + stamp pin, always last
   C.save_png(bg, s.background_path)

   for b in s.buttons:
       normal = C.paint_button(KEY, b.id, seed=11)   # shared grammar
       ...optional hand touches outside the label box...
       C.finish_button(normal, KEY, b.id)
       C.save_button_states(C.button_states(normal, KEY, b.id), KEY, b.id)

   for a in s.art_layers:
       fr = C.base_frame(KEY, a.id, seed=11)     # lean frame: pictogram tabs + grips, rest alpha 0
       C.finish_frame(fr, KEY, a.id)
       C.save_png(fr, s.frame_path(a.id))
   ```

   Use `C.finish_*` (or pass `C.PIN` to `geo.finish_*`): they stamp pins in
   `ink_0`. Paint deterministically: fixed seeds, no `random` without a seed,
   no clock. Only touch the PNGs of your assigned skins. Frames carry no
   words. If you draw a glyph-like mark on a button yourself (an arrow, an
   icon), register it with `C.remember_extras(img, button, pixels)` so the
   states protect it like lettering.

   Outside a script in this directory, put `tools/` on `sys.path` and use
   `from faithful import compose, primitives`. Inside the package every
   module imports its siblings as `faithful.<name>`, so Faithful, Soulrend and
   cozy modules with the same names never collide in one process, and
   plain-name and package imports give the same module object.

2. Validate exactly as the builder does, linting against this palette:

   ```sh
   %PY% tools/cozy/validate.py economy_hub --style --theme faithful
   %PY% tools/cozy/validate.py --all --isolated-build --theme faithful   # before handing in
   ```

   `FAIL` lines carry the builder's exact message plus a hint. `WARN STYLE`
   lines flag off-palette pixels, semi-transparency, dark text rows and opaque
   pixels inside a frame's container (pure black/white and transparency
   round the lean frame tabs are allowed in this theme).
   `set QUASAR_GUI_THEME=faithful` does the same as `--theme faithful` for
   validate.py, preview.py and build_fixtures.py; the flag wins.

3. Look at it:

   ```sh
   %PY% tools/cozy/preview.py economy_hub --theme faithful
   %PY% tools/cozy/preview.py economy_hub --theme faithful --buttons-sheet
   %PY% tools/cozy/preview.py economy_hub --theme faithful --outline-clearances --content full --long-title
   ```

   Previews land in `evidence/faithful-previews/`. Compare with
   `evidence/faithful/example/preview.png` and the guide's quality bar.

4. When the whole theme is painted:

   ```sh
   %PY% tools/faithful/selftest.py --pack-source
   %PY% tools/cozy/build_fixtures.py --theme faithful   # evidence/faithful-fixtures/*.html
   ```

   Without `--pack-source`, selftest checks the pack-source buttons of every
   skin whose background is already on the Faithful palette and skips the
   rest, so it is useful while painting is in progress.

Never write to `manifests/`, `deliverables/` or the existing `tools/*.py`,
never edit another painter's `paint_*.py`, and never run `tools/build_pack.py`
in the shared tree; `--isolated-build` exists for that. Preview overlays (grey
item squares, titles, magenta outlines) exist only in `evidence/` images,
never in textures.

Licence: code MIT; glyph and sprite designs CC0-1.0, matching the repository.
