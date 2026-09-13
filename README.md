# CDUResources

Canonical editable resource-pack assets and artist tooling for CDU's Quasar GUI redesign.

**Status: foundation being redesigned.** The current 50 audited menu skins and six chest templates preserve the previous native slot layouts. They are useful source material and compatibility contracts, not the completed redesigned interface. New navigation, visual buttons, meaningful states and revised layouts belong in the action-layout design and its matching server adapter. Static validation does not prove gameplay or client rendering.

Edit PNGs in `pack-source/assets/quasar_gui/textures/menu/`. Normal builds preserve those source images. Geometry, fonts and audited control meaning are in `manifests/`; the planned interaction contract is `manifests/action-layouts.json`. This repository contains no Quasar gameplay source or compiled mods.

## Build and verify

Use Python **3.12.14**, pinned in `.python-version`, and the pinned Pillow dependency:

```sh
python -m pip install -r requirements.txt
python tools/check_artifacts.py
```

The check command builds the resource pack, runs the 14 existing pack tests, verifies byte-identical repeated pack and artist-kit builds, and extracts the artist kit into a fresh directory. It rebuilds and tests that portable copy, then checks that a texture override appears in its exported PNG and offline guide while the canonical source remains unchanged. More tests may be added for the redesigned interaction contract.

Outputs are generated under `deliverables/`: `quasar-gui.zip`, `quasar-gui-artist-kit.zip`, their checksum files, and `checksums.json`. Evidence is under `evidence/`. Generated output directories are ignored by Git. The same ZIP currently targets Minecraft Java 1.19.2, 1.20.1 and 1.21.1; read [client compatibility](CLIENT-COMPATIBILITY.md) for format warnings and verification limits.

For an ordinary rebuild, run `python tools/build_pack.py`. Open the generated `CONTROL-EXPLORER.html` to inspect the foundation artwork, audited slots and explanatory diagrams offline. Start with [the artist guide](START-HERE.md) and [texture overrides](docs/ARTIST-OVERRIDES.md). Use `--regenerate-samples` only when intentionally replacing canonical PNGs with procedural defaults.

## GitHub Actions

[Resource pack checks](.github/workflows/resource-pack.yml) runs on pushes to `main`, pull requests targeting `main`, and manual dispatch. It uses pinned Python/Pillow versions and commit-pinned official GitHub actions. Successful runs attach pack, artist-kit and checksum artifacts; verification evidence is attached even after a failed check. Artifacts follow the private repository's access rules and expire after 30 days. The workflow needs only `contents: read` and GitHub's automatic token; it creates no release, public host or deployment.

Changes are committed directly to `main` according to the repository owner's workflow. [CI provenance](docs/CI.md) records action versions and their official sources.

Original artwork/data use CC0-1.0; standalone tooling uses MIT. See [LICENSE.txt](LICENSE.txt).
