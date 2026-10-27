# V230 — source-native Alpine composition and cartway ground contact (NOT APPROVED)

## Why this experiment exists
The actual V229 WebKit three-cell screenshot (Actions run 40439671920, artifact 12705417489) shows WEST dominated by meadow/forest and SOUTH by flat pasture. Original Matrei is far more detailed. The unchanged V203 numeric gate failed ALL FOUR configurations: WEST relative fine-luma 0.488–0.638 and SOUTH 0.418–0.524 (minimum 0.70); WEST/SOUTH relative fine-area also failed. Roads visibly lie over trees/pasture without credible ground contact. The V229 four-browser gameplay/movement and Matrei-preservation steps passed; the artwork did not.

## New actual artwork code
`scripts/build_v230_grounded_alpine_art.py` downloads the SAME TWO independent original 6000×4000 photographs with SHA-256 verification and original photographer credit, then evaluates full contiguous **native-pixel 1536×1024 crops** for actual source fine detail, vegetation, and conservative sky/roof penalties. It does not tile or reuse Matrei pixels. It selects a SINGLE native 1536×112 meadow-material strip from each corresponding original photograph, samples that strip monotonically along the original unchanged V123 polyline, and blends a narrow terrain contact (14px core, fading by 37px) beneath the existing original 22px road. No procedural texture, duplicated scenic buildings, new bridge, invented route or altered navigation coordinates. These are source-derived **illustrative terrain art compositions** and may still be rejected after human inspection.

The native original photos are:
- WEST Michael Kranewitter, [Guggenberg von Norden a.JPG](https://commons.wikimedia.org/wiki/File:Guggenberg_von_Norden_a.JPG), source SHA-256 `273218ffd17e79fc8fb2c1e6db609b53045be955ac7284d60945a588ff383e55`.
- SOUTH Michael Kranewitter, [Bichl von Nordwesten.jpg](https://commons.wikimedia.org/wiki/File:Bichl_von_Nordwesten.jpg), source SHA-256 `afb9f2c80f8e436ad20a3bc085e4cb9badfaee5075ea80c6e39b14746e67fc7d`.
- Original license: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Derivative crops, graph-aligned meadow contact and source selection are modifications. Attribution and share-alike apply to derived assets. Source locations and author/license are verified; **historical roads and source-to-game registration are not**.

## Integration and safety
- New isolated `v230-austrian-source-art-review.html` + SHA-validating `terrain-grid/v230-austrian-source-art.js`; V229, original V121 Matrei, V123/V121 graph, V94 campaign/saves, army sprites and production main untouched.
- Fail-closed manifest rejects invented source/game registration, human approval and altered license/asset hashes. The crop-score heuristic is **not** a semantic human review.
- CI tests unchanged V137/V202 bridge, route, camera and 24-tap regressions, all four Chromium/WebKit portrait/landscape screenshots, identical Matrei camera and center pixels, and strict UNCHANGED V203 on actual V230 screenshots. Human/production approval job deliberately fails.
- No costs or production deployment. The generated WebP assets are CI artifacts, not permanently published in this branch. Browser preview requires the generated assets; do not call the static HTML alone a working published build until assets are available.

## Unresolved blockers
V209 source/game tiepoints remain independently unverified; both outer road termini have no verified onward cartway; actual bridge banks and historic 1780 geometry are not established; source photo perspective and modern material may still conflict with Matrei. Four V100 zoom levels, actual iPhone physical review, strict V203 pass and **user** visual approval are still required. `productionApproved=false` is mandatory. Review actual CI screenshots and scores before accepting or selecting next art work.
