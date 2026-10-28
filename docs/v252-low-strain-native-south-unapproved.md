# V252 — SOUTH lower-strain native-road source selection (2026-10-27)

**ART/PRODUCTION RED. Not a playable release, historic geography, source approval or user visual approval.**

## Actual evidence inspected first
- GitHub issue #9 through V251, recent terrain branches, and V251 Actions 40608814197 (functional geometry passed; deliberate production gate failed).
- Downloaded V249 Actions 40595149075 artifact 12775609104, opened its **actual WebKit browser contact sheet**. WEST/SOUTH CC-BY source images still show no physical road beneath the immutable V123 route, while Matrei is more detailed.
- Opened the V251 original/warped full-resolution fictional WEST/SOUTH pixel comparison. WEST exceeded the immutable 155px deformation threshold; SOUTH was stretched around the river and its road was visibly off-center in places.

## Substantive source change — not another procedural road stripe
Instead of forcing V251's SOUTH source track approximately **141.16px** onto the unchanged V123 route, inspected a distinct previously generated 1536x1024 **original fictional** Alpine river-valley source with a physical twin-rut cartway already near the V123 geometry. Its PNG SHA256 is:

3f2be77f71c05923b10bea8e8dd9c5f9ea7de51aa55842cedc2d6872b4ebceb2

This source is not a 2023 orthophoto, licensed historic geography, a verified Austrian 1780 road, or independently verified tiepoints. The source trace in code is **manually visually estimated** and remains unapproved.

The new Python script pins source SHA256 and the unchanged V123 atlas blob; rejects wrong source/dimensions; maps **existing image pixels and surrounding terrain** to the V123 SOUTH curve with a low-strain 2D inverse remap; leaves the exact V123 road graph untouched; writes full-resolution candidate and route-overlay files only when the exact original PNG is supplied locally. It does not generate a fake road or change Matrei, army sprites, V94, saves or gameplay.

## Actual 1536x1024 source-image run, manually inspected (NOT GitHub browser gameplay)
- Maximum manually traced source-to-target displacement: **33.423px**, versus V251 SOUTH's **141.16px**.
- Minimum sampled Jacobian: **0.8709**, zero sampled folds; observed source pixel coverage **99.9349%**; arc-length change **1.689%**.
- Annotated mathematical centerline median inverse-map residual **0.013px**, p95 **0.029px**. These numbers verify only the transformation of **annotated points**, not whether the source's true cartway pixels were accurately annotated.
- Visual inspection: road/ground structure is substantially less stretched than V251 and the red V123 guide generally follows the native cartway. **REJECT**: the visible source road continues approximately **150.48px** beyond the immutable V123 endpoint, and local road-centerline/riverbank source correspondence has not been independently certified. Do not disguise the continuation with cosmetic inpainting or pretend it is a verified gameplay route.
- WEST remains **REJECTED**: the V251 WEST source needs ~161.98px deformation (over 155px limit); no accepted WEST replacement. Source/game natural tiepoints, bridge banks, Matrei border continuity, historical road provenance, V203 microstructure and four-browser **new-art** gameplay acceptance remain missing.
- The full-resolution original source PNG and resulting candidate are **not committed**. GitHub CI therefore exercises synthetic image geometry and immutable V123 integrity, not a new photo-art screenshot or gameplay release.

## Verified code tests and limits
Six regression tests cover (1) reduction from V251 displacement, (2) strict deformation quality, (3) identity preservation, (4) explicit unsupported road continuation / fail-closed approval, (5) wrong-source hash rejection, (6) invalid dimensions/large deformation rejection. Workflow deliberately leaves production approval RED.

**Next substantive art task:** create or find a distinct, attribution-safe SOUTH source with a naturally ending/covered road at the immutable endpoint **without unnatural inpaint**, and a separately acceptable WEST landscape with matching borders and cartway. Independently trace physical source pixels and confirm bridge approaches, then run actual iPhone/Chromium/WebKit screenshot and strict V203 tests. Do not deploy or claim three octagons complete.
