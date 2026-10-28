# V264 — experimental photographic continuity at WEST/MATREI and MATREI/SOUTH (2026-10-28)

**PRODUCTION RED. NOT USER-APPROVED. NOT SOURCE-REGISTERED HISTORICAL GEOGRAPHY.**

## Why this change

Actual V263 mobile Chromium screenshots showed a large smooth/procedural green gap between the sharp Matrei image and the native WEST/SOUTH photographic terrain. The original Matrei photo has an alpha-faded octagon perimeter; at the unchanged V123 joins, the center's synthetic ground remains exposed. The SOUTH cartway enters at local x466 but crosses an artificial-looking region before reaching the Matrei photographic core. This is a visible game-art continuity defect, not a V123 routing defect.

## What the isolated code does

New scripts/v264_photo_edge_continuity.py uses the two exact local V258 WEST and V260 SOUTH 1536×1024 source PNGs (both SHA256 pinned). It creates one 1536×1024 transparent underlay for Matrei's already transparent outskirts, sampling photographic pixels from the neighbor boundaries by reflection and fading them inward. At the shared western boundary, underlay x0 samples WEST x1535; at the southern boundary, underlay y1023 samples SOUTH y0. The overlap in the bottom-left corner is weighted, and alpha tapers from 100% through a 235px fade. It is drawn after the imported neighbors but **under** the unchanged original Matrei image and existing Matrei painted roads/bridge. This avoids drawing a new fake highway. The output is a self-contained experimental offline playable HTML derived from V263.

**Important limitation:** Reflection can duplicate vegetation and rock shapes; it is an artistic fictional infill, NOT new independently sourced landscape, historical route evidence, independently verified V209 tiepoints, licensed orthophoto, proof of bridge-bank continuity, or final seam solution. No new geographic control points or navigation graph edges are introduced.

No changes to main, V94 campaign/saves, sprites, V121 image, V123 graph, original V249 renderer or core mechanics. All changes are additive on an isolated branch. The original WEST/SOUTH PNGs and final HTML are local run artifacts, not committed to GitHub.

## Rebuild

First generate the original V263 candidate with its existing builder and exact two local source PNGs. Then run:

    python scripts/v264_photo_edge_continuity.py /private/V263_UNAPPROVED_Offline_Playable.html /private/west-v258-lossless.png /private/south-v260-single-pass-UNAPPROVED.png /private/V264_UNAPPROVED_Photo_Seam_Experiment.html --patch /private/v264_photo_underlay.png

WEST SHA256: 36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7
SOUTH SHA256: d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb
Immutable V123 Git blob: 09f04b4062e24fbacbb645307462cdddce2b2aa3

## Actual-image local results and limitations

- Examined actual V263 Chromium full crossing screenshot, exact WEST/SOUTH PNGs, and V263 three-center screenshot **before selecting** this correction. The Matrei green procedural border is plainly visible.
- Generated and inspected actual V264 Chromium 390×844 portrait and 844×390 landscape screenshots using the exact V258 WEST/V260 SOUTH PNGs; Chromium reported no page errors.
- Local exact-source V264 test: both images loaded, underlay decoded to 1536×1024, connectedRoute=true, orderTo('south')=true, progress crossed the unchanged V123 graph, productionApproved=false, both V123 seam checks passed.
- At 390×844 DPR1, measured the Matrei/SOUTH transition screen crop x55–340/y430–530 with the same 3px Gaussian residual: fine-luma 13.001 (V263) → 18.289 (V264); fraction of pixels with residual >12: 0.3609 → 0.5664. This is local detail coverage, NOT unchanged V203's three-center score and not human realism approval.
- At 844×390 DPR1 on actual V264 images, unchanged V203 formula gives WEST landscape ~0.749/0.873 PASS, SOUTH landscape ~0.663/0.778 **FAIL** against the 0.70/0.70 minima. These DPR1 measurements are not directly interchangeable with V263's earlier DPR2 report. Strict four-browser **exact** artwork gate remains RED.
- Local 3/3 compositor regressions PASS using original PNGs; CI uses synthetic images for four Chromium/WebKit configurations because the original PNGs are not hosted. Synthetic browser success is NOT exact-art WebKit validation.
- The visible seams still need human assessment. The mirrored photo edges can look repeated, and the broader green Matrei outskirts remain visibly artificial.

## Next

Do not continue small procedural texture changes. The remaining serious task is a geographically registered, appropriately licensed and visually coherent high-resolution Matrei-neighbor landscape that replaces the reflection experiment, with independent source/game control points, physical road/rut and bridge-bank checks, and exact original-art WebKit plus iPhone Safari testing. Keep production RED until strict V203 and user approval.
