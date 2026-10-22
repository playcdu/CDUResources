# tools/cozy - cozy theme toolkit

Shared Python 3.12 + Pillow modules for painting the cozy replacement of every
menu background, button state and outer frame. The look is defined in
[docs/COZY-STYLE-GUIDE.md](../../docs/COZY-STYLE-GUIDE.md); read it first.

Use only the pinned interpreter:

```sh
PY=C:\Users\Brandon\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

Run everything from the repository root.

| Module | Purpose |
|---|---|
| `palette.py` | the 34-colour master palette, ramps, `FAMILY_ACCENT`, `rgba()`, `step()`, `snap()` |
| `lettering.py` | the HEARTH (7 px) and SPRIG (5 px) faces: `text_width`, `draw_text`, `draw_text_centered` |
| `geometry.py` | `skin(key)` with masks, buttons, pins and art layers computed by the builder's own code; mask clearing and pin stamping |
| `primitives.py` | hand-drawn helpers (plank, parchment, brass, linen, wax, page curl, wells, tack, rope, leaf, mug, lantern glow, dither) and the shared state transforms |
| `icons.py` | icon sprites (close seal, purse, lens, cog, rosette), seal emblems and frame motifs |
| `compose.py` | the shared base look: `base_background`, `base_frame`, `paint_button`, `button_states` (pulses spare the lettering found by `lettering_mask`; close seals get grey-wax disabled frames), `save_png` |
| `validate.py` | runs the builder's validators on pack-source PNGs; `--isolated-build` runs the real build in a temp copy |
| `preview.py` | composites a skin as the client layers it and writes 3x PNGs under `evidence/cozy-previews/` |
| `paint_example.py` | the worked example and quality bar (writes only to `evidence/cozy/example/`) |
| `render_references.py` | regenerates the guide's reference drawings in `evidence/cozy/reference/` |
| `selftest.py` | proves geometry matches the manifests and every default composition passes the validators |

## Painter workflow

1. Write `tools/cozy/paint_<assignment>.py`. Import the modules directly
   (each module puts `tools/cozy` and `tools/` on `sys.path`):

   ```python
   import sys; from pathlib import Path
   sys.path.insert(0, str(Path(__file__).resolve().parent))
   import compose as C, geometry as geo, primitives as P, icons, lettering as L
   from palette import WOOD, SAGE, BRASS, EMBER, accent_for

   KEY = 'economy_hub'
   s = geo.skin(KEY)
   bg = C.base_background(KEY, seed=11)          # shared base
   ...family identity in static / decorative regions only...
   geo.finish_background(bg, KEY)                # clear masks + stamp pin, always last
   C.save_png(bg, s.background_path)

   for b in s.buttons:
       normal = C.paint_button(KEY, b.id, seed=11)   # shared grammar
       ...optional hand touches...
       geo.finish_button(normal, KEY, b.id)
       C.save_button_states(C.button_states(normal, KEY, b.id), KEY, b.id)

   for a in s.art_layers:
       fr = C.base_frame(KEY, a.id, seed=11)
       ...side-panel motifs...
       geo.finish_frame(fr, KEY, a.id)
       C.save_png(fr, s.frame_path(a.id))
   ```

   Paint deterministically: fixed seeds, no `random` without a seed, no
   reading the clock. Only touch the PNGs of your assigned skins.

2. Validate exactly as the builder does:

   ```sh
   %PY% tools/cozy/validate.py economy_hub --style
   %PY% tools/cozy/validate.py --all --isolated-build     # before handing in
   ```

   `FAIL` lines carry the builder's exact message plus a hint. `WARN STYLE`
   lines flag off-palette pixels, semi-transparency and dark text bands.

3. Look at it:

   ```sh
   %PY% tools/cozy/preview.py economy_hub
   %PY% tools/cozy/preview.py economy_hub --buttons-sheet
   %PY% tools/cozy/preview.py economy_hub --outline-clearances --content full --long-title
   ```

   Open the PNG and compare it with `evidence/cozy/example/preview.png` and the
   guide's quality bar.

Never write to `manifests/`, `deliverables/` or the existing `tools/*.py`, and
never run `tools/build_pack.py` in the shared tree; `--isolated-build` exists
for that. Preview overlays (grey item squares, titles, magenta outlines) exist
only in `evidence/` images, never in textures.

Licence: code MIT; glyph and sprite designs CC0-1.0, matching the repository.
