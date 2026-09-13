# Aseprite source artwork

Keep editable `.aseprite` files here and commit them alongside their exported PNGs in `pack-source/`. Register frame-to-asset mappings in `manifests/artist-projects.json` for automatic local export and CI freshness checks. Unregistered PNGs can be edited directly in any image editor.

See [the Windows artist workflow](../docs/ARTIST-WORKFLOW.md). The optional layout helper aligns real hit regions; Aseprite remains the primary artwork tool. No setup or build command overwrites `.aseprite` sources.
