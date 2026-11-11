# V193 — mobile camera coverage and gesture bounds (2026-10-25)

**Status:** isolated development-only regression improvement. No GAME visual, historical, geographic, bridge, production, or physical iPhone approval.

## Baseline inspected
- Issue #9 through V191 and latest V192 commits. V192's tested source SHA: `b29bbf06f2848d641b4b3d80ab0a64728958431b` (already on main before this branch was created; V193 made **no** writes to main).
- V192 CI [40216749382](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40216749382) passed route and image-gradient tests in Chromium/WebKit portrait/landscape. Downloaded and visually inspected its actual 12 three-center screenshot captures and whole crossing ([artifact 12608221863](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40216749382/artifacts/12608221863)).
- **Art is not accepted:** Matrei is still a sharply detailed central painted island. Western Pass and Southern Valley have repeated soft synthetic conifer forms and geometrically regular, almost paved-looking tracks; endpoints are explicitly unknown rather than validated onward roads. Numeric detail parity does not resolve this.

## Implemented
- New `minimumTerrainZoom()` ensures the entire current viewport fits inside the existing 7000×9000-world-unit painted underlay, instead of allowing a zoom-out to reveal flat canvas.
- New `clampCamera()` constrains drag and two-pointer pinch movement to that underlay, while preserving the world anchor during valid center pinch.
- Read-only `V192.terrainCamera` exposes current bounds to regression QA. The V121 painted image and V123 graph remain byte-for-byte unchanged.
- `scripts/qa_v193_camera_coverage.py` checks four Chromium/WebKit phone configurations, all three tile centers, deliberate overscroll, simulated pinch anchoring, minimum zoom, and immutable V121/V123 Git blob hashes.
- New branch-only workflow `.github/workflows/qa-v193-camera-coverage.yml`. No production deployment.

## Evidence
- Code commit [6155bb849846](https://github.com/wayfinderandco0-cell/century-of-empires/commit/6155bb849846c611ee37da9ba2def71e9e591530).
- Final CI [40220846883](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40220846883): **PASS 4/4** (Chromium/WebKit × portrait/landscape); pinned source blobs verified.
- Actual V193 screenshots and machine-readable report downloaded and inspected from [artifact 12608894178](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40220846883/artifacts/12608894178). Portrait minimum zoom 0.7695, landscape 0.7574; viewport coverage and pinch anchoring passed in all four simulated browser configurations.
- Earlier workflow-only commit [40220834175](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40220834175) failed before the HTML implementation landed; the **final code commit** above is the authoritative green run.

## Not resolved
- No physical iPhone validation, frame-time/memory benchmark, or art approval.
- No source-registered historical WEST/SOUTH landscapes; no period-verified road destination or bridge-bank alignment.
- No change to V94 campaign, saves, V121/V123 roads, or live game by V193.

**Next high-impact action:** replace illustrative western/southern terrain and paved-looking track treatment with verified, period-safe geography/materials, then inspect each phone center and bridge banks against immutable movement coordinates. Keep all visual/route gates fail-closed.
