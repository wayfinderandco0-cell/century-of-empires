# V253 — actual original-source pixels through the real three-octagon game renderer

**Status: ART RED, PRODUCTION RED. No user approval.** This is an isolated QA branch, not an approved new art set.

## Why this change
V251 and V252 only tested full-resolution source-image deformation locally. Their images were **never tested inside the actual iPhone game renderer**; previous V249 browser evidence instead used the rejected V224 Kosovo forest photographs. V253 closes that specific integration-evidence gap without inventing any source tiepoints or changing the game.

## What is implemented
- New `scripts/qa_v253_original_art_playtest.py` accepts optional `WEST_SOURCE` and `SOUTH_SOURCE` native 1536×1024 original PNG/JPEG/WebP files. It hashes original bytes with SHA-256, rejects duplicate sources and incorrect dimensions, serves them same-origin, and opens the **existing V249 game renderer** with the original source pixels and immutable V123 route guide.
- Captures **real Chromium and WebKit** screenshots for WEST, original MATREI and SOUTH in portrait and landscape. While inspecting raw source pixels, army commands must be blocked. Leaving inspection restores the existing exact V123 army graph; three progress samples must remain within 0.001 world units of the road.
- Four source input regressions check wrong dimensions, duplicate images, original hash identity and fail-closed approvals.
- CI defaults to the already **REJECTED** V224 SUHEJLO CC BY 4.0 fixtures. CI artifacts contain actual browser screenshots and a repository snapshot for locally testing original fictional V251/V252 artwork without copying the artwork into production.
- Source hashes, valid image dimensions, browser functionality and route geometry **do not** prove the historical road, natural source/game geographic tiepoints, bridge banks, strict V203 visual quality, licensing of AI-generated fictional images, or human acceptance.

## Sources and actual unresolved art
The previous V251 fictional WEST original (SHA-256 `7326e88c778ed4a0018c241156e701690e95deb1feeb8fa13a298c0f0c74505e`) needs 161.98px warp (>155px limit). The V252 fictional SOUTH original (SHA-256 `3f2be77f71c05923b10bea8e8dd9c5f9ea7de51aa55842cedc2d6872b4ebceb2`) has approximately 150.48px of visible road beyond the immutable V123 endpoint. Both remain **REJECTED**, irrespective of technical browser QA.

V224 fallback source attribution: SUHEJLO, CC BY 4.0, photos of Sharr Mountains in Kosovo (NOT historic Austrian cartways), Wikimedia Commons:
- https://commons.wikimedia.org/wiki/File:Drone_image_of_Sharr_Mountains_during_Spring_Season.jpg
- https://commons.wikimedia.org/wiki/File:Aerial_photo_of_Sharr_Mountains_in_Kosovo.jpg

## Safety
No main changes, merges, deployments, spending, existing game file edits, V94 campaign/saves, Matrei art, army sprite options, or V121/V123 road/bridge geometry changes. CI always ends with a deliberate RED production gate. Do not report the three octagons finished.

## Next
Inspect actual browser screenshots of both original fictional images; reject visual cartway discontinuities and road-end overruns. Obtain independently verified high-resolution WEST/SOUTH sources with real embedded cartways and source/game natural tiepoints before considering any production approval.
