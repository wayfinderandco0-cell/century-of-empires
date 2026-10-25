# V176 — source-first interpretive tonal material, NOT completed Alpine game art

Date: 2026-10-25 (America/Chicago). Isolated branch: terrain-v176-source-first-tonal-candidate-20261025, based on V175. No main/live/V94 saves/V121 painting/V123 road graph changes.

## Evidence reviewed before coding

Opened actual V175 WebKit iPhone-layout West, Center, South and whole-L screenshot artifact 12585208358 from successful run 40158163038. Authentic geographic source has sharp forest/meadow detail in all three sectors, but modern asphalt/roofs and the unacquired southwest remain large transparent checkerboard holes. This is a modern source inspection, **not** V123 geographic registration or a historically accurate game surface. Original V171 GAME-art gate remains **0/4**; no new V171 art acceptance claim.

## Code and scope

- scripts/v176_source_tonal_candidate.py generates a separate 1536×1024 RGBA source-only candidate from the *verified* V169 muted source study using **only three monotonic per-channel color LUTs**. It does not resample, clone, invent roads, houses, rivers, bridges or fill any excluded/unknown pixels.
- Source study and modern-exclusion mask SHA-256 are checked. Exact 1,536-block V174 alpha coverage and sector counts are verified before generation; the output is byte/pixel-reconstructed in verification. A candidate manifest binds source identities and attribution and marks **all** game/historical/route/phone approval flags false.
- scripts/test_v176_source_tonal_candidate.py: nine synthetic tests including forged V169/V174 approval rejection, alpha/unknown preservation, block-count tampering, and incorrect source/modern claims.
- .github/workflows/qa-v176-source-tonal-candidate.yml: pinned Pillow, immutable V121/V123 guard, original V168/V169/V174 tests, 18 real geographic JPEG acquisition, exclusion/LOD regeneration, V176 tests and output artifact.

## Acceptance

The candidate is a **color/material experiment** on present-day geographic source pixels, **not period-authentic 1780–1880 art**. Visual inspection of the locally generated candidate shows photographic natural detail remains and transparent exclusions remain conspicuous. It is **not a three-octagon playable game**, and cannot replace Matrei or the V123 road graph. No source↔game landmark transform or historical bridge-bank continuation has been established.

Local verification using the actual V175 artifact's V169/V174 manifests and masked PNG: 9/9 new tests PASS; V176 generate + byte/pixel verify PASS. GitHub Actions run 40161690727: check final status separately; do not infer green from this note.

Next: inspect real V176 CI artifact and independent phone views at matching zoom, then obtain geological registration controls or explicitly retire V121↔source transform. A separate source-first period-art game candidate needs evidence-backed landcover, genuine 1780–1880 material interpretation, coherent three-sector composition, and no holes silently filled. Rerun unchanged V140/V171 game visual gates and all road/bridge/movement tests before seeking actual iPhone approval.

productionApproved=false; periodArtComplete=false; v123RoadsGeoregistered=false; physicalIPhoneApproved=false.
