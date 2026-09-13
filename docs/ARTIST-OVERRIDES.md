# Texture overrides and handoff

The current pack is the foundation for a larger GUI redesign. Keep source art editable, and keep a visual target's clickable rectangle tied to a real server-side control.

1. Install Python 3.12 and run `python -m pip install -r requirements.txt`.
2. Copy a canonical PNG to the same relative path under `overrides/`, such as `overrides/assets/quasar_gui/textures/menu/auction_house.png`.
3. Edit the copy in a raster editor. Preserve its RGBA mode, dimensions, protected item masks and advance pin while it uses the foundation layout contract.
4. Run `python tools/build_pack.py --overrides overrides --output deliverables/artist-r2.zip`.
5. Open the generated `CONTROL-EXPLORER.html` and `guides/` images. They show the actual override artwork. Inspect the revised ZIP in the game before accepting it.

The override build preserves both canonical PNGs and the override directory. The exported artist kit includes the edited PNGs as its own canonical source, the corresponding pack and a self-contained guide. It can be extracted anywhere with Python and the pinned dependency; the original repository is unnecessary.

Direct edits to `pack-source` also survive normal builds. Do not pass `--regenerate-samples` to preserve an artist's finished work. The check suite intentionally creates a one-pixel override to verify the exact changed ZIP entry, hash and guide content.

The implemented button/carrier contract is `manifests/button-layouts.json`. Font bitmaps do not animate through texture `.mcmeta` files. Each control has normal, disabled, selected and three pulse PNGs selected explicitly by the server adapter, with four ticks per pulse frame and a static resting state. Painting a frame does not create an action or a mouse-hover event. See [PAINTED-BUTTONS.md](PAINTED-BUTTONS.md) for the full contract and [ARTIST-WORKFLOW.md](ARTIST-WORKFLOW.md) for Aseprite export and optional alignment tools.

The build does not host packs or offer them to players. Publishing a finished immutable ZIP and configuring its URL/SHA-1 are separate operator steps.
