# tools/soulrend - Soulrend theme toolkit

Shared Python 3.12 + Pillow modules for painting the Soulrend (dark-fantasy,
souls-like) replacement of every menu background, button state and outer
frame. The look is defined in
[docs/SOULREND-STYLE-GUIDE.md](../../docs/SOULREND-STYLE-GUIDE.md); read it
first. Geometry, masks, pins and validation are the theme-agnostic modules in
`tools/cozy/` (`geometry.py`, `validate.py`, `preview.py`); they are imported,
never copied.

Use only the pinned interpreter, from the repository root:

```sh
PY=C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

| Module | Purpose |
|---|---|
| `palette.py` | the 36-colour master palette (ink, iron, stone, umber, vellum, blood, ember, soul, gold, moss, void), `FAMILY_ACCENT` / `SKIN_ACCENT` / `accent_for()`, `rgba()`, `step()`, `snap()`, `luminance()` |
| `lettering.py` | the GRAVEN (cap 7) and RUNE (cap 5) faces: `text_width`, `draw_text`, `draw_text_centered`, `draw_lines_centered`, `fit_face`, `specimen`; run it to write `evidence/soulrend/typeface-specimen.png` |
| `primitives.py` | hand-drawn helpers: stone masonry and tablets, umber sheet, iron plate, rivets, chains, vellum strips, torn edges, page curls, blood cloth, wax seals, candles, banners, gold filigree, arch niches, moss, cracks, glow; socket wells; the state transforms (`make_disabled`, `make_selected`, `make_pulse`, `make_disabled_seal`, `make_state`) |
| `icons.py` | icon sprites (close seal, pouch on a chain, scrying lens, iron cog, heraldic crest), seal emblems, heraldic crests, frame motifs |
| `compose.py` | the shared base look with cozy-identical signatures: `base_background`, `base_frame`, `paint_button`, `button_states`, `save_png`, `save_button_states`, plus `bands`, `letter`, `lettering_mask`, `button_kind`, `side_banner`, `heading_plaque`, `finish_background/button/frame` |
| `paint_example.py` | the worked example and quality bar (writes only to `evidence/soulrend/example/`) |
| `render_references.py` | regenerates the guide's reference drawings in `evidence/soulrend/reference/` |
| `selftest.py` | proves geometry matches the manifests, the fits hold, and every default composition passes the builder validators, stays on palette, keeps the text bands light, never lets selected or a pulse touch lettering, and checks disabled dims it in place |
| `fixture_urls.json` | published gallery URLs for `build_fixtures.py --theme soulrend` (empty until published) |

## Painter workflow

1. Write `tools/soulrend/paint_<assignment>.py`. Import the modules directly;
   the workflow is the cozy one with the Soulrend modules:

   ```python
   import sys; from pathlib import Path
   _HERE = Path(__file__).resolve().parent
   sys.path.insert(0, str(_HERE))                      # soulrend modules first
   for p in (str(_HERE.parent), str(_HERE.parent / 'cozy')):
       if p not in sys.path:
           sys.path.append(p)                          # tools/ and the shared geometry
   import compose as C, geometry as geo, primitives as P, icons, lettering as L
   from palette import IRON, STONE, GOLD, BLOOD, EMBER, SOUL, accent_for

   KEY = 'economy_hub'
   s = geo.skin(KEY)
   bg = C.base_background(KEY, seed=11)          # umber sheet, vellum bands, sockets
   ...family identity in static / decorative regions only...
   C.finish_background(bg, KEY)                  # clear masks + stamp pin, always last
   C.save_png(bg, s.background_path)

   for b in s.buttons:
       normal = C.paint_button(KEY, b.id, seed=11)   # shared grammar
       ...optional hand touches...
       C.finish_button(normal, KEY, b.id)
       C.save_button_states(C.button_states(normal, KEY, b.id), KEY, b.id)

   for a in s.art_layers:
       fr = C.base_frame(KEY, a.id, seed=11)
       ...side-panel motifs...
       C.finish_frame(fr, KEY, a.id)
       C.save_png(fr, s.frame_path(a.id))
   ```

   Use `C.finish_*` (or pass `C.PIN` to `geo.finish_*`): they stamp pins in
   Soulrend ink_0. Paint deterministically: fixed seeds, no `random` without a
   seed, no clock. Only touch the PNGs of your assigned skins. Frames carry no
   words (the only painted title in the pack is OFFERED MONEY, which
   `base_background` letters on the dispenser).

   Outside a script in this directory (another tool, a notebook), put
   `tools/` on `sys.path` and use `from soulrend import compose, primitives`.
   Inside the package every module imports its siblings as
   `soulrend.<name>`, so Soulrend and cozy modules with the same names never
   collide in one process.

2. Validate exactly as the builder does, linting against this palette:

   ```sh
   %PY% tools/cozy/validate.py economy_hub --style --theme soulrend
   %PY% tools/cozy/validate.py --all --isolated-build --theme soulrend   # before handing in
   ```

   `FAIL` lines carry the builder's exact message plus a hint. `WARN STYLE`
   lines flag off-palette pixels, semi-transparency and dark text bands.
   `set QUASAR_GUI_THEME=soulrend` does the same as `--theme soulrend` for
   validate.py, preview.py and build_fixtures.py; the flag wins.

3. Look at it:

   ```sh
   %PY% tools/cozy/preview.py economy_hub --theme soulrend
   %PY% tools/cozy/preview.py economy_hub --theme soulrend --buttons-sheet
   %PY% tools/cozy/preview.py economy_hub --theme soulrend --outline-clearances --content full --long-title
   ```

   Previews land in `evidence/soulrend-previews/`. Open the PNG and compare it
   with `evidence/soulrend/example/preview.png` and the guide's quality bar.

4. When the whole theme is painted:

   ```sh
   %PY% tools/soulrend/selftest.py --pack-source
   %PY% tools/cozy/build_fixtures.py --theme soulrend   # evidence/soulrend-fixtures/*.html
   ```

Never write to `manifests/`, `deliverables/` or the existing `tools/*.py`,
never edit another painter's `paint_*.py`, and never run `tools/build_pack.py`
in the shared tree; `--isolated-build` exists for that. Preview overlays (grey
item squares, titles, magenta outlines) exist only in `evidence/` images,
never in textures.

Licence: code MIT; glyph and sprite designs CC0-1.0, matching the repository.
