# Released-client source and codec audit

No Minecraft textures or executable client code are included in the GUI ZIP or artist kit. Local downloaded `*-client.jar` files, launcher metadata, mappings, libraries and javap output live under the developer project's `evidence/client-code` directory. Those downloaded audit fixtures are intentionally absent from the artist kit. `manifests/client-audit-downloads.json` records official URLs, expected SHA-1, actual SHA-1, and sizes; all downloaded JAR hashes matched. The numerical geometry and width data is original measurement data.

The current pack has `pack_format:15`, `supported_formats:[9,34]`, no overlays, no `min_format`/`max_format`, no item models and no vanilla namespace changes. Shared base PNGs and native `space`/`bitmap` providers suffice for retained targets. 1.16.5 and 1.18.2 were initially inspected but subsequently explicitly excluded by the user; their legacy spacing needs are not implemented.

## What actually ran

`tools/CheckTargetCodecs.java` ran the released client's own bitmap/space provider parsers against all 56 images' definitions and its metadata parser against the final ZIP. Official classes and matching launcher libraries were loaded into a Java process, without a window, OpenGL, textures or a server. All three retained clients passed these parser checks. The 1.21.1 metadata parser required normal registry bootstrap to initialize text-component codecs; no gameplay session ran. See `evidence/target-client-codecs.txt` for output and `evidence/pack-tests/test-results.json` for independent static validation.

Reproduce after downloading the exact official JARs and launcher-listed dependencies into `<version>-libs`:

```powershell
java --class-path 'evidence/client-code/1.19.2-client.jar;evidence/client-code/1.19.2-libs/*' tools/CheckTargetCodecs.java 1.19.2 deliverables/quasar-gui.zip
java --class-path 'evidence/client-code/1.20.1-client.jar;evidence/client-code/1.20.1-libs/*' tools/CheckTargetCodecs.java 1.20.1 deliverables/quasar-gui.zip
java --class-path 'evidence/client-code/1.21.1-client.jar;evidence/client-code/1.21.1-libs/*' tools/CheckTargetCodecs.java 1.21.1 deliverables/quasar-gui.zip
java --class-path 'evidence/client-code/26.2-client.jar;evidence/client-code/26.2-libs/*' tools/CheckReleasedMetadata.java pack-source/pack.mcmeta
```

These are parser checks, not resource reload, texture upload, client rendering, clicks or protocol negotiation. Those remain untested.

## Geometry from versioned client bytecode

Official mapping names and obfuscated names used:

| Version | Bitmap parser | Generic screen / crafting / dispenser | Container render | Chest / crafting / dispenser menu |
|---|---|---|---|---|
|1.19.2|BitmapProvider.Builder / `ejn$a`|`emu` / `emv` / `emy`|`emk`|`bwt` / `bxb` / `bxd`|
|1.20.1|BitmapProvider.Definition / `erw$a`|`ewa` / `ewb` / `ewf`|`evp`|`cbm` / `cbu` / `cbw`|
|1.21.1|BitmapProvider.Definition / `flm$a`|`fpe` / `fpg` / `fpk`|`fot`|`cqc` / `cqm` / `cqo`|

Inspected with `javap -c -p`. Chest screens are 176 pixels wide and 114 + 18 × rows high. The first chest slot starts at (8,18), with 18-pixel spacing. Player main slots start at (8,31 + 18 × rows), and the hotbar at (8,89 + 18 × rows). The dispenser screen is 176 × 166; its 3 × 3 grid starts at (62,17). Crafting is also 176 × 166, with its input grid at (30,17) and result at (124,35). Both player regions start at (8,84), with the hotbar at y142. Crafting's recipe book can move the entire GUI; every coordinate here is relative to the container origin, so no window-center assumption is used.

TitleLabelX is 8 for chest and 29 for crafting; titleLabelY is 6. Dispenser sets X to `(176-font.width(title))/2` in `init`. Its title contains only artwork and spacing, with a fixed advance of 160, so it starts at x8. Dynamic money remains in the existing slot 4 item and tooltip; artwork contains only a static label. No server approximation of a client-local font is needed for this centered anchor.

Bitmap provider computes scale=providerHeight/cellPixelHeight and advance=`(int)(0.5 + rightmostNonzeroAlphaColumnPlusOne * scale)+1`. Every art cell is 176 wide, with a pinned opaque pixel at x175, scale 1; advance 177. `SheetGlyphInfo.getUp()` computes 7 minus ascent, so ascent 13 gives texture y0 from title y6. No transparent right margin is allowed to change that measured width. Height 222 is the maximum asset height, fitting inside the 256×256 font atlas.

AbstractContainerScreen renders slot items and hover highlighting before `renderLabels`; carried stack handling follows labels, with tooltips subsequently drawn by the screen. Large opaque title art can therefore obscure item/count/hover contents. Every slot in the audited `liveSlots` union and all 36 player slots receive 20×20 alpha-zero clearance. Opaque panels use only audited never-populated protected `staticProtectedSlots` or decorative fillers listed in `removedDecorations` and removed by the SGUI adapter. Inventory label is drawn after title and sits on a pale opaque reserved panel. Crafting recipe toggle and arrow/ghost region remain transparent. Font batching, depth, glint, count overflow, tooltip layering, alternate item models and GUI-scale behavior still require real rendering tests.

The 1.19.2 `Style.Serializer` reads and serializes `font`; the 1.21.1 `Style.Serializer` exposes the resource-location font through its MapCodec. Namespaced custom font selection does not require replacing default-font providers. Full runtime text-style behavior remains covered only by source and serialization tests and must be observed in game.

## Metadata and wider clients

[Mojang's 1.19 release notes](https://feedback.minecraft.net/hc/en-us/articles/6731464524941-Minecraft-Java-Edition-1-19) introduce the native `space` provider, mapping codepoints to advance widths. Actual 1.19.2 client code (`com.mojang.blaze3d.font.SpaceProvider`, `dyv`) accepts our negative and positive advances. Actual 1.20.1/1.21.1 SpaceProvider.Definition codecs accept the same JSON.

[Mojang's 1.20.2 release notes](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-20-2) introduce supported format ranges and overlays; older clients ignore these fields and see the single `pack_format`. Therefore the final format 15 declaration predicts a newer-pack warning on 1.19.2 (format 9), no format warning on 1.20.1 (15), and an accepted declared range on 1.21.1 (34). These UI outcomes are source-derived, not observed screenshots. The range declaration is a compatibility intent, not a claim that every intermediate release was tested.

[25w31a notes](https://www.minecraft.net/en-us/article/minecraft-snapshot-25w31a) describe major/minor formats and min/max fields. Released 26.2 behavior was checked independently using its actual `PackFormat.packCodec(CLIENT_RESOURCES)`, not assumed from that snapshot. The first attempted metadata (format 9 plus range 9..34) was rejected with the diagnostic "Multi-version packs cannot support minimum version of less than 15". Changing only `pack_format` to 15 succeeded with effective range 9.0..34.0. Explicit min/max 9..34 also parsed but is unnecessary for declared retained targets, so it was omitted. See `evidence/26.2-metadata-codec.txt` and its Java reproducer.

[Mojang's 26.2 release notes](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-2) give resource format 88.0 and describe rendering changes. 88.0 lies outside 9..34: an out-of-range warning is expected, but pack loading and rendering are untested and 26.2 is not declared supported. A valid metadata codec result does not establish texture/font render compatibility. There is no Quasar 26.2 server port in this patch, and client-pack compatibility cannot bridge client/server protocol differences. Versions 1.13–1.18 and 1.12 are not claimed by the delivered pack.
