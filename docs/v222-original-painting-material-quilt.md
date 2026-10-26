# V222 — original Matrei material quilting, isolated artistic alternative

**Status: UNAPPROVED ART STUDY; not a source-registered landscape, historical road map, or production build.**

## Why this is different from V219/V220

V219's modern orthophoto islands had conspicuous seams and alpha holes. V220's complete modern 2023 aerial mosaics showed contemporary houses, roads and date markings and an incompatible aerial-camera perspective. Both were rejected on actual WebKit screenshots. V221 separately measured native pixels, without changing game art.

V222 instead derives **two new complete 1536×1024 scenic surfaces** from the *original V121 painted Matrei asset*, keeping its perspective, lighting, color language and native pixel scale. It uses deterministic original-pixel material quilting with seam-aware selection from explicitly enumerated rock/forest/meadow source regions. It does not insert a modern 2023 orthophoto, generate fake photographic noise, copy the complete Matrei scene, add a road, move a bridge or claim that the reconstructed landscapes existed in 1780.

The original painting is the source of art **style and material only**, not verified West/South geography. New patch arrangements may look repetitive or visually incoherent; some sampled pixels may contain original manmade features. The source-rect manifest allows exact provenance and independent review. **Human screenshot rejection overrides any numeric pass.**

## Code and tests

- `scripts/v222_original_painting_quilt.py`: 1:1 original V121 material source extraction; two separate deterministic full-cell paintings; source patch provenance, unique crop coordinates, per-cell SHA-256; embedded JS assets for review.
- `scripts/test_v222_original_painting_quilt.py`: rejects altered pixels, false visual approval, fake georegistration, duplicated source crop, incorrect source identity.
- `terrain-grid/v222-painted-neighbors.js`: fail-closed full-cell loader; all historical/geographic/production flags remain false.
- `v222-painterly-west-south-review.html`: independent interactive opt-in scene, unchanged original Matrei center, original V123 graph, road taps and army path, A/B original neighbor toggle.
- `scripts/qa_v222_painted_game_art.py`: actual Chromium/WebKit portrait/landscape, baseline Matrei pixel equality, two changed neighboring cells, real movement graph and blocked unverified endpoints; strict V203 unchanged `>=0.70` necessary microstructure floor and human gate RED.
- `.github/workflows/qa-v222-original-painting-quilt.yml`: source build, four-browser screenshot QA and intentionally fail-closed strict art acceptance.

## Explicit unresolved blockers

1. V209 has no independently verified V121/V123 source-to-game tiepoints: `BLOCKED_MISSING_REAL_TIEPOINTS`. A source-material quilt cannot resolve real geography.
2. V121's painted roads and original V123 west/south road graph remain immutable. West/south unverified road ends stay blocked; no fictional continuations or bridges.
3. Human visual comparison of actual West/Matrei/South portrait and landscape screenshots is required; V203 alone is insufficient.
4. Realistic cartway banks, coherent scenic transitions, all four V100 zoom tiers, historical plausibility, physical iPhone user approval and Europe-scale expansion remain unfinished.
5. No game production, original Matrei, V94 campaign, saves, sprite options or core mechanics may change in this study.

**Approval flags:** `sourceRegisteredToV123=false`, `historicRoadsVerified=false`, `periodSafe=false`, `gameArtApproved=false`, `physicalIPhoneApproved=false`, `productionApproved=false`.

**Decision rule:** If full-cell artwork is visibly repetitive or cartoonish, reject it and keep production gate RED. Do not mask the defect by adjusting numeric thresholds.
