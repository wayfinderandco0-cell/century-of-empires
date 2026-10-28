# V262 — self-contained WEST/SOUTH exact-pixel art review (2026-10-28)

**Production RED; no gameplay integration.** This is an isolated, iPhone-sized, touch/pinch/pan inspection alternative using the actual V258 WEST and V260 SOUTH images, not another generated QA dashboard or fabricated historical map. It displays the exact immutable V123 routes as switchable red dashes. Optional Matrei is **a genuine prior Chromium gameplay screenshot used for context only**, not a georegistered center tile or source asset. The two original fictional images remain unhosted and unapproved.

## Local inputs, immutable geometry

- WEST 1536×1024 PNG SHA256: 36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7
- SOUTH 1536×1024 PNG SHA256: d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb
- V123 Git blob SHA: 09f04b4062e24fbacbb645307462cdddce2b2aa3
- The builder **rejects wrong source hashes** and only embeds the exact native PNG bytes. It never rewrites a game source or V123 path.

Build the self-contained offline HTML with the local exact PNGs by running:

    python scripts/v262_art_review_builder.py --west /private/west-v258-lossless.png --south /private/south-v260-single-pass-UNAPPROVED.png --matrei-context /private/chromium-portrait-matrei-RAW-UNAPPROVED.png --out /private/V262_UNAPPROVED_Art_Review.html

The resulting ~11.6 MB HTML has no network dependencies and offers WEST/SOUTH/Matrei context switching, route overlay toggle, Fit, and pointer/touch pan/pinch. It is **an art review, not a three-tile playable game**. Do not deploy as production without licensing and approval.

## Verified actual pixels and browser checks

Required pre-change inspection: issue #9 through V261, latest branches and Actions run 40671685260, actual V259 Chromium WEST/MATREI/SOUTH screenshots and actual V260 SOUTH + V258 WEST 1536×1024 PNGs. In the genuine V259 browser screenshot, WEST's route visually contacts a cartway in the shown crop, while SOUTH's route still runs offset from the physical road in some portions. The prior V259 SOUTH landscape-mode strict V203 detail ratios remain ~0.638/0.637 versus 0.70 minimum.

- Local **4/4** Python tests passed with both exact source PNGs; SHA mismatch and swapped inputs rejected.
- Generated the real 11,643,002-byte offline HTML using the exact source hashes and actual Matrei Chromium screenshot context.
- Loaded the exact HTML into **real Chromium** using an in-memory page because direct file URL navigation was blocked by the local sandbox. Tested 390×844 portrait and 844×390 landscape, device scale factor 2, mobile touch enabled. All three images loaded, WEST/SOUTH switching and route overlay toggle worked, no JavaScript page errors; opened and inspected real screenshots for both orientations.
- This does **not** establish native iPhone Safari or WebKit behavior, three-tile seams, movement gameplay, V203 pass, historic 1780 geography, or user visual approval. The GitHub CI cannot access the private original PNGs, so exact-image tests explicitly skip there; no fake CI art pass.

## Unresolved and next step

WEST and SOUTH are still fictional visual studies. Independent V209 natural geographic tiepoints, 1780 road provenance, source license documentation, Matrei seam and bridge-bank continuity, actual game renderer with exact V260 art across Chromium/WebKit portrait/landscape, strict V203 >=0.70 and explicit user approval remain blockers. Preserve V94, saves, sprites, Matrei, V121/V123, all game mechanics and production RED. Continue with a source-proven high-resolution replacement/upgrade, not arbitrary texture noise or repeated route-graph tweaks.
