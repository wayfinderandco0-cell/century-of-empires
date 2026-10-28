# V251 — original fictional WEST/SOUTH physical-road scene study (2026-10-27)

**ART/PRODUCTION RED. This is not verified 1780 geography, approved imagery, or a playable release.**

## Why this branch exists
The actual V249 WebKit source-pair screenshot (Actions run 40595149075, artifact 12775609104) was opened before development. It shows roadless WEST/SOUTH CC-BY photographs beneath the V123 dashed line; Matrei remains detailed. V250 traces original pixels but supplies no new art. This V251 experiment instead tests **two distinct new original fictional 1536×1024 landscape studies containing physical twin-rut tracks**, with whole-scene deformation that moves real image pixels and their surroundings, not overpainted synthetic road stripes. The two original fictional image files are **not committed** as accepted art. They are available only in the working conversation and cannot yet support a GitHub-hosted playable build.

## Source identity / nonhistorical status
- WEST: original fictional AI-generated Alpine rocky meadow/cartway scene, original PNG SHA256 `7326e88c778ed4a0018c241156e701690e95deb1feeb8fa13a298c0f0c74505e`.
- SOUTH: distinct original fictional AI-generated Alpine valley/cartway/river scene, original PNG SHA256 `74ebf7ff4eedcaf9a23ba6cb109bed972a9081a8df5c0a6e94e21b0a46e3363d`.
- The original source-road coordinates in `SOURCE` are **visually estimated, not independently verified**. These are not modern orthophotos, historic maps, verified cartways or source/game geographic tiepoints. Source-use rights and attribution for any future production release must be reviewed separately. No historical claims are made.

## Code and real-pixel test
`scripts/v251_fictional_cartway_pair.py` pins the unchanged V123 atlas Git blob and exact WEST/SOUTH route points; samples each full physical road by arc length; remaps **existing image pixels** and nearby terrain with a bounded 2D deformation; uses smoothed displacement to prevent local folds; writes full-resolution scene and V123 centerline overlays plus fail-closed JSON. It never edits army sprites, campaign saves, original Matrei, V94, road/bridge graph, or production.

Local original-image run (not GitHub CI, no browser acceptance):
- WEST: maximum displacement **161.98px**, sampled minimum Jacobian **0.400**, observed pixels **99.935%**, zero sampled folds. **FAILS the existing V245 155px maximum**. Visual road is substantially more physically integrated than V248's overpainted stripe but the trace is not independently verified, and WEST is rejected.
- SOUTH: maximum displacement **141.16px**, sampled minimum Jacobian **0.451**, observed pixels **99.7535%**, zero sampled folds, arc-length stretch about **17.5%**. **Necessary V245 geometry thresholds pass**, but original-road annotation is unverified. 1:1 visual review shows some centerline drift toward a rut edge and local hillside stretching; human art review remains **FAIL**.
- Both source landscapes remain fictional, are not proven to match Matrei border geography, and contain no verified bridge-bank continuation. The strict V203 visual gate and four Chromium/WebKit iPhone configurations **have not been run on this new pair**. A geometry pass is not artwork approval.

## Tests and decision
`scripts/test_v251_fictional_cartway_pair.py` has six controls: valid route geometry, identity preservation, excessive displacement rejection, degenerate road rejection, WEST must remain red, SOUTH geometry-only status. The isolated workflow runs these and the immutable V123 pin, then deliberately fails the production gate. It does not falsely claim a gameplay screenshot or a finished octagon.

**Next:** Obtain an independently reviewed, license-attributed **pair** of high-resolution physically roaded source landscapes, verify original-pixel road traces and both borders/bridge banks, then run strict V203 and four-browser actual-game screenshot tests. The V251 fictional pair is only a visually inspectable alternative and must not be promoted. `humanArtApproved=false; productionApproved=false`.
