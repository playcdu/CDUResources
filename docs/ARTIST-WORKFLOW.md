# Aseprite artist workflow

Aseprite is the primary artwork editor. The optional `LAYOUT-EDITOR.html` helps align native button regions and preview exported PNGs; it does not replace your painting tools. The repository builds from committed PNGs, so GitHub Actions never needs Aseprite, its license, or an Aseprite download.

## First setup on Windows

1. Install or use an existing **Python 3.12** from the [official Windows downloads page](https://www.python.org/downloads/windows/). Any Python 3.12 patch release works locally; CI pins 3.12.14. The helper checks the Python launcher, PATH and usual install folders. Set `PYTHON_EXE` to your Python executable if needed.
2. Double-click **Setup Artist Tools.cmd**. It creates only this repository's `.venv` and installs `requirements.txt` (Pillow 12.3.0). It does not change execution policy, system settings or global packages. Re-running setup reuses the matching environment.
3. Open PNGs or your `.aseprite` sources in your own Aseprite installation. Discovery checks `ASEPRITE_EXE`, PATH and common standalone/Steam locations. For a custom location, set `ASEPRITE_EXE` to `Aseprite.exe` in your terminal before launching the helper. Nothing downloads Aseprite.
4. Double-click **Build Pack.cmd**. It exports registered changed Aseprite sources if your binary is available, verifies source-to-PNG receipts, validates the pack, runs tests and checks deterministic outputs. PNG-only projects work without Aseprite.

Use a normal writable checkout. If a missing Python message appears, install Python 3.12, or set `PYTHON_EXE`; the helper deliberately does not install system software automatically. Do not commit `.venv`, `.cache` or generated `deliverables`.

## Artwork and indexed frame exports

Put editable `.aseprite` or `.ase` documents under `artwork/`, alongside the committed canonical PNG tree in `pack-source/assets/quasar_gui/textures/`. Register each source in `manifests/artist-projects.json`. The initial empty list means PNG-only editing is available immediately.

Example registration (replace paths and dimensions with an actual binding):

```json
{
  "schemaVersion": 1,
  "projects": [{
    "id": "economy-auction",
    "source": "artwork/economy-auction.aseprite",
    "canvas": {"width": 54, "height": 36},
    "outputs": [
      {"frame": 0, "tag": "normal", "asset": "assets/quasar_gui/textures/buttons/economy_hub/auction/normal.png"},
      {"frame": 1, "tag": "disabled", "asset": "assets/quasar_gui/textures/buttons/economy_hub/auction/disabled.png"},
      {"frame": 2, "tag": "selected", "asset": "assets/quasar_gui/textures/buttons/economy_hub/auction/selected.png"},
      {"frame": 3, "tag": "pulse_1", "asset": "assets/quasar_gui/textures/buttons/economy_hub/auction/pulse_1.png"},
      {"frame": 4, "tag": "pulse_2", "asset": "assets/quasar_gui/textures/buttons/economy_hub/auction/pulse_2.png"},
      {"frame": 5, "tag": "pulse_3", "asset": "assets/quasar_gui/textures/buttons/economy_hub/auction/pulse_3.png"}
    ]
  }]
}
```

Frame indexes start at **zero**. The `tag` is a human-readable note; the integer `frame` selects the actual exported frame. Width and height must match both the Aseprite canvas and target artwork. Keep all six declared button states present. These are distinct bitmap glyph frames selected by the mod; `.png.mcmeta` does not animate a font bitmap.

The tool uses Aseprite's documented batch CLI with a single `--frame-range N,N`, RGB conversion and `--save-as`. It never saves over the Aseprite document, scales, crops, trims, runs scripts, or silently changes canvas dimensions. PNG output is normalized to RGBA with the pinned Pillow encoder. Header checks follow the [official Aseprite file specification](https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md); CLI options are documented in [Aseprite's official CLI reference](https://www.aseprite.org/docs/cli/).

```powershell
.venv\Scripts\python.exe tools\artist.py export
.venv\Scripts\python.exe tools\artist.py verify-exports
```

The generated `manifests/artist-exports.json` records SHA-256 hashes of each source, its mapping and every PNG output. Commit the source, mapping, PNGs and receipt together. CI rejects changed sources or PNGs with stale receipts. If a PNG was edited independently while its registered source stayed unchanged, ordinary export refuses to replace it. Preserve that PNG by removing its project registration for PNG-only work, update the Aseprite source, or explicitly choose `export --force` when replacing the PNG is intended. The tool validates all pending exported frames before replacing generated assets.

## Optional alignment helper

Double-click **Open Layout Helper.cmd**, or open the generated `LAYOUT-EDITOR.html` directly. It embeds the current manifests and images and works offline with no network calls or account. Rebuild the helper after repository updates.

- Pick a screen, then an existing audited action or information binding. The original ID, callback source slot, role, content source identities and decorative frame geometry are locked.
- Move its rectangle, or choose **Redraw** and drag between native slots. Complete 18-pixel rectangles only: overlap, protected content and off-grid hit regions are rejected. Player inventory stays protected.
- Select **Native item display** on the seven paged display screens or the auction confirmation / valid and invalid ticket screens to move their existing display rectangle. The number of visible cells stays fixed. Choose **Swap native display order**, select an original source item in the dropdown, then click another cell in that rectangle to swap their displayed positions. This changes destination order only. Other storage, crafting and redirect slots cannot acquire a new mapping. Repaint any changed transparency wells in Aseprite before building; the builder rejects artwork that obscures moved native content.
- Edit labels or fallback style. This updates metadata; finished artwork stays untouched. Paint replacement frames in Aseprite, or explicitly regenerate that one binding using `python tools/build_pack.py --regenerate-button skin/id`. Regeneration replaces only that binding's six PNGs. It never edits `.aseprite` documents.
- Preview normal, disabled, selected and three pulse frames. The helper's loop demonstrates the frames; actual timing and trigger behavior belong to the mod's runtime registry.
- Import a PNG to check it against the expected dimensions. Nothing is silently resized. Exporting a selected PNG downloads the original artwork bytes, without grid numbers or masks. Save it at the displayed `pack-source/` path. After resizing a region, provide six matching-size state PNGs before building.
- **Save helper project** preserves all screens, optional manifest fields and imported PNGs for later editing. **Export button-layouts.json** creates the actual compatible layout manifest; place it under `manifests/`. Export any imported PNGs separately to their displayed paths. The helper cannot write into your repository by itself.

The protected overlay is an alignment aid. The real builder also checks pixel transparency masks, frame dimensions, glyph advance pins and semantic layout contracts. Decorative art can extend outside the native inventory while native content remains visible. Decorative pixels do not create additional click targets.

## Refresh a local Minecraft preview without rebuilding the mod

Install the matching InventoryDebug preview mod once. After a successful resource build, explicitly select your **own Minecraft instance directory** (the folder containing that profile's `resourcepacks` and `config` folders):

```powershell
.venv\Scripts\python.exe tools\artist.py install-preview --minecraft "D:\Minecraft\Artist Profile"
```

The command copies the built pack to `resourcepacks/quasar-gui-artist-preview.zip` and its hash-bound layout sidecar to `config/invdebug-layouts/current.json`. It creates an ownership receipt beside the sidecar. Repeated installs replace only files whose hashes still match that receipt; existing unowned files or independent edits are preserved and cause a clear error. It does not edit `options.txt`, enable packs, change server configuration or install mods.

Enable **quasar-gui-artist-preview** once in Minecraft's Resource Packs screen. For later iterations: build, install-preview, press **F3+T**, then run **`/invdebug quasar reload`**. Open the demo again with `/invdebug quasar`. The registry sidecar is bound to the exact built pack SHA-1, so stale layout/pack pairs are rejected by the preview mod. A layout or texture change does not need a Java rebuild when the existing audited action bindings remain compatible.

`deliverables/quasar-gui-layouts-<sha1>.json` travels with that pack. For a merged pack, use the sidecar whose filename and `packSha1` match the **merged ZIP**. Server installation is a separate operator workflow; this local helper never changes a live server.

## Commit to main and collect Actions artifacts

Review the changed art, layout and receipts. Use your Git client, or:

```powershell
git status --short
git add artwork pack-source manifests tools docs "Setup Artist Tools.cmd" "Build Pack.cmd" "Open Layout Helper.cmd"
git commit -m "Update GUI artwork and layouts"
git push origin main
```

The push-to-main Actions workflow validates committed PNG freshness, pack geometry and deterministic generation, then publishes build artifacts inside the repository's Actions run. Download the pack, matching hash-bound layout sidecar, artist kit and checksums from the successful run. It does not publish a public release or host a pack URL automatically.

The source tests simulate Aseprite subprocess output to check export failure handling and hashes. They do not claim an actual Aseprite binary or Minecraft rendering session was exercised. Real art appearance should be reviewed in Aseprite and the local Minecraft preview.
