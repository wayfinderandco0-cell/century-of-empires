# V207 — conservative native-source exclusions; three playable octagons still RED

## What changed (2026-10-26 UTC)

**Isolated branch:** `terrain-v207-conservative-modern-feature-masks-20261026`, based on V206. This is source-processing code, **not a replacement game landscape**.

Read issue #9 through V205, inspected V206 branch and its CI 40270390637 (source-candidate and inherited mobile QA SUCCESS; separate strict photographic game-art gate FAILURE), and opened the actual V203 four-layout screenshot comparison and V205 original contiguous modern-source image. The game WEST/SOUTH art is still cartoonish relative to Matrei; V205 contains a visibly modern road network and repeated 2023 marks.

New `scripts/v207_conservative_modern_masks.py` traces broad exclusion bands around clearly visible modern tracks and date imprints on all three geographically adjacent **modern source** panels. The upper clearing in the center panel is also quarantined as uncertain forestry context. Each exclusion is specified in native 512x512 source pixels. The code exports original-RGB, source-native RGBA panels with **transparent exclusions**, untouched original JPEG/PNG source, binary masks, a manifest with source hashes and EPSG:3857 XYZ origins, and a human-inspectable red-overlay contact sheet. **No modern pixels are inpainted, and no missing terrain is invented.** Visible exclusions are conservative, not a claim that all modern traces were found.

Retained native-source pixel fractions: WEST **90.4060%**, CENTER **63.2080%**, SOUTH **87.1033%**. These percentages indicate *unmasked modern source pixels*, **not** period-valid forest, V123 registered art, or game coverage. The source mosaic is an L-shaped modern EPSG:3857 reference, **not three playable octagons**.

`scripts/test_v207_conservative_modern_masks.py` checks manually inspected positive/negative pixels, exact retained original RGB under RGBA alpha, false approval rejection, altered source/annotation rejection, tampered binary masks and review contact. It inherits V204/V205/V206 source controls. CI additionally retains V194 road pigment, V192 original V123 road/army and 12 three-center phone-layout frames, V193 camera, V202 road-tap/bridge checks, and strict V203 photographic microstructure gate **without lowering the threshold**.

## Actual artifact review

Downloaded V207 original-source and mask artifact from GitHub Actions run [40274603623](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40274603623). Opened the actual `v207-exclusion-contact.png`: WEST road network and 2023 imprints are red, CENTER's uncertain upper clearing and imprints are red, SOUTH hairpin and lower forestry roads plus date marks are red. Forest detail remains untouched outside those quarantines. **The transparent gaps are not usable historical terrain until justified replacement source is found**.

**FINAL CI VERIFIED:** [run 40274603623](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40274603623) completed with **source-exclusion-integrity SUCCESS** (V204/V205/V206/V207 tests, native imagery and pixel-accurate mask verifier), **inherited-phone-route-camera-geometry SUCCESS** (four Chromium/WebKit portrait/landscape layouts, V194 road pigment, V192 road/army alignment and three-center screenshots, V193 camera, V202 bridge taps), and **strict-visual-art-must-remain-red FAILURE by design**. Actual strict screenshot artifact 12629358324 was downloaded and opened: WEST/SOUTH still look artificial compared with the original Matrei. Strict V203 microstructure parity failed all four configurations (WEST fine-luma 0.533–0.553, SOUTH 0.504–0.528 vs Matrei; minimum 0.70). The overall workflow remains RED, correctly; the game has not been visually approved.

## Explicitly still blocked

- No independently verified source-to-V121 Matrei photo registration or V123 road/crossing alignment.
- No surveyed far-bank road continuation, 1780 roads, period vegetation, historical settlement or destination verification.
- No seamless playable WEST/MATREI/SOUTH replacement, V100 four-zoom visual approval, or physical iPhone acceptance.
- No game-art/production approval. All manifest flags remain FALSE; the original 1536x1024 Matrei image, V121/V123 road graph, game campaign/saves, `main`, and deployment are untouched.
- Masked tracks/date stamps remain **transparent holes**, not synthesized historical cartways.

**Next defensible step:** independently match stable source-image landmarks to the existing Matrei painting and source-backed game positions; then reconstruct source-appropriate candidate terrain and test all three actual phone-layout centers. Do not paste V205's unrelated modern forest source into V123 game cells or invent road continuations.
