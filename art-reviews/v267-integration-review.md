# V267 original Alpine art + canonical V123 integration (2026-10-28)

**UNAPPROVED / PRODUCTION RED.** This is fictional 1780–1880-inspired WEST/SOUTH game artwork, not verified historical geography. Main, V94 campaign, saves, original V121 Matrei file, army sprite options, and the original V122/V123 source modules were not changed.

## Actual changes on existing isolated V267 branch
- Replaced the independent V267 approximate 98-world-point navigation graph with the original **V122 seam engine and V123 atlas module embedded offline** in the existing one-file playable prototype. The authoritative network has **100 tile-keyed nodes, 98 distinct world positions, and two explicit zero-gap seams**. Both experimental seam checks pass.
- Preserved the distinct WEST/SOUTH original source art, hand-registered physical cartways and the embedded canonical V121 Matrei source; verified the visual road arrays match V123's exact coordinates before allowing movement.
- Restored V123-style army badge, count and flag; added halt with in-edge continuation; made the scene redraw only when moving or camera/UI changes.
- Removed stretched photographic seam aprons and green procedural background. Uncharted surrounding cells now show subdued atlas paper rather than copied terrain. Matrei's source image was not modified.
- No overpainted synthetic road stripes.

## Actual Chromium browser checks
Four mobile viewport tests with the **exact embedded art** (390×844, 844×390, 375×667, 667×375) passed: original Matrei decoded offline, 100 tile nodes/98 unique positions, two V123 seams pass with 0px coordinate gap, real touch on the rendered cartway triggers movement, halt preserves the current road edge, and WEST→MATREI→SOUTH route reaches world coordinate (2806,1629). A typical shortest route traverses 53 tile-keyed points, including both seams. No JavaScript page errors.

- [Actual Chromium screenshot contact sheet](art-reviews/v267-integrated-actual-chromium.jpg)
- [Browser test results](art-reviews/v267-integrated-chromium-results.json)
- [Playable candidate](../v267-three-octagon-original-art-prototype.html)

## Open blockers
- **Not** tested on physical iPhone Safari or WebKit; Chromium emulation is not native Safari.
- User has **not** visually approved the WEST/MATREI/SOUTH composite. Exact original Matrei source is embedded but reprojected for V123 preview; no approval of that transformation.
- Physical cartway-to-graph alignment and river bridge-bank realism require visual acceptance, beyond the 0px abstract V123 seam endpoints. No verified 1780 geographic tiepoints.
- Strict V203 production acceptance not rerun for this new original-art candidate. Production gate stays RED.
