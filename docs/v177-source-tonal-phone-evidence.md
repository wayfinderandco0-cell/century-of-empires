# V177 — source-only tonal A/B iPhone-layout inspection (NOT GAME ART)

Date: 2026-10-25. Isolated branch `terrain-v177-tonal-phone-evidence-20261025` based on V176. No changes to main, live, V94 campaign/saves, original V121 Matrei image, or immutable V123 road/bridge graph.

## Evidence reviewed before coding
- Issue #9 latest V176 checkpoint, V171 real screenshot artifact 12578863866 and V176 real candidate artifact 12586577452.
- Opened actual WebKit V171 West, Matrei, South, whole-crossing screenshots: original game Matrei is a sharp photographic island, while West/South are still synthetic and outer roads terminate at unsurveyed question marks. V171 strict GAME-art acceptance remains **0/4**.
- Opened the actual V176 1536×1024 source candidate: genuine geographic tree/meadow texture but large transparent modern asphalt/roof exclusion holes, plus the completely unobserved southwest quadrant. Source sectors are NOT game octagons.

## Implemented
- `v177-source-tonal-ab-review.html`: iPhone-friendly side-by-side-by-toggle **original vs V176 tonal** inspection, preserving identical source-space camera, three geographic source centers and four zoom tiers. Loads SHA256-verified original and candidate images, verifies all candidate and source provenance/false approval flags, checks full 1,572,864-pixel alpha equality against original and modern exclusion mask, rejects RGB in unknown pixels and fabricated approval claims.
- `scripts/qa_v177_source_tonal_phone.py`: Chromium/WebKit × portrait/landscape. Captures original/tonal pairs at each source center and whole L, checks same camera anchors, unknown pixels, full provenance, and tampered manifest rejection. Tests that canvas terrain pixels actually differ between original and tonal modes.
- `.github/workflows/qa-v177-source-tonal-phone.yml`: regenerates and validates original 18 geographic JPEGs, modern exclusions, V174 LOD and V176 tonal candidate; checks immutable V121/V123 pins; executes four-browser QA; uploads evidence.

## Verified GitHub CI and real screenshots
- [GitHub Actions 40165666283](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40165666283) **SUCCESS** on commit `78dffd4f`. All source/LOD/V176 tests, immutable original checks, real JPEG acquisition, regeneration and **4/4 simulated phone-browser A/B tests PASS**.
- [Artifact 12587932541](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40165666283/artifacts/12587932541) downloaded and inspected: 32 original/tonal browser screenshots (three centers + whole L, two modes, four configurations). Actual WebKit portrait and landscape pairs show no scene composition change, only modest color toning; the large checkerboard holes remain conspicuous.
- Real candidate vs real original masked study, retained pixel counts: West **370,771**, Center **330,064**, South **268,387**. Alpha identical in all sectors. Mean absolute RGB-channel difference (retained pixels): West **5.72**, Center **5.98**, South **6.97** on 0–255 scale. All retained pixels changed in at least one channel. This is **tonal variation, not a historical reconstruction**.

## Acceptance and next action
**Three playable GAME octagons: NOT ACCEPTED.** This inspection is a source-only viewer, not game integration, physical iPhone approval, source↔V123 landmark registration, or bridge-bank verification. Existing strict V140/V171 GAME-art visual gates must remain fail-closed (V171 0/4). The source still has 2023 landscape, excluded modern structures and unknown holes; never fill those with invented roads or trees.

Next highest-impact: obtain independently corroborated stable source↔game landmark correspondences or explicitly retire the V121 photo-to-source alignment hypothesis; then author distinct period-appropriate game materials in a consistent geographic coordinate frame. Reinspect real phone images and road/bridge connections before any game-art approval.