# Reproducible checks

The workflow invokes `tools/check_artifacts.py`, the same command used locally. Python 3.12.14 and Pillow 12.3.0 are pinned. The runner image is Ubuntu 24.04. Existing PNGs are canonical, and deterministic ZIP entries have fixed timestamps, paths, permissions and ordering.

The following official release tags and commit refs were checked on 2026-09-13:

| Action | Release | Pinned commit |
| --- | --- | --- |
| [actions/checkout](https://github.com/actions/checkout/releases/tag/v7.0.1) | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| [actions/setup-python](https://github.com/actions/setup-python/releases/tag/v7.0.0) | v7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| [actions/upload-artifact](https://github.com/actions/upload-artifact/releases/tag/v7.0.1) | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |

Refs were resolved through each repository's GitHub REST `git/ref/tags/<version>` endpoint. The [setup-python action inputs](https://github.com/actions/setup-python/blob/v7.0.0/action.yml) support `python-version-file`; the [upload-artifact inputs](https://github.com/actions/upload-artifact/blob/v7.0.1/action.yml) support explicit paths, retention and failure on missing outputs. Both use Node 24 on the hosted runner. Python release provenance: [Python 3.12.14](https://www.python.org/downloads/release/python-31214/). Pillow release provenance: [Pillow 12.3.0](https://pillow.readthedocs.io/en/stable/releasenotes/12.3.0.html).

The 23 pack tests cover asset/provider contracts, coverage/geometry, spacers/title origins, live-slot masks, deterministic ZIP bytes, texture-only replacement, malformed PNG rejection and safe merge behavior. The handoff check verifies a fresh extraction rebuild, copied documentation, and override art in the exported guide and ZIP. `tools/check_artifacts.py` also records SHA-1/SHA-256 for the delivered files and compares repeated artist-kit bytes.

The check also runs 15 Aseprite/export/preview-install tests and 20 pure Node layout-model groups. Node is required in CI and optional for an ordinary local artist build. These checks do not launch Minecraft, validate packet callbacks, or establish successful client rendering. No game JARs, private server source, credentials, server access or repository secrets are required by the workflow.
