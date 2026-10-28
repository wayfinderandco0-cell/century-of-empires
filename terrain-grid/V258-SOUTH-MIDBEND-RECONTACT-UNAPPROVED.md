# V258 — SOUTH physical-cartway mid-bend recontact (isolated, NOT APPROVED)

**2026-10-28.** Based on `terrain-v257-original-west-bridge-cartway-replacement-20261028` at `6d5059e19df57b77a6dc9a356b727c7a8e79f942`. This is a substantive change to actual original SOUTH source-road pixel registration, not a new procedural texture or another inspection-only UI. WEST uses V257 unchanged. Matrei, V94, saves, sprites, `terrain-grid/v123-atlas.js`, V121 and all existing road/bridge gameplay geometry remain unchanged.

## Evidence reviewed before change

Read GitHub issue #9 through V257, current branches, latest V257 Actions `40644742041`, and downloaded V253 real WebKit browser screenshot artifact `12787641727`. The V253 screenshot shows the rejected WEST/SOUTH photos with V123 roads cutting across trees, while Matrei is detailed. Opened actual original 1536x1024 SOUTH image `alpine_valley_path_and_river.png`, V257 transformed image and V257 red-road overlay. The V257 SOUTH mid-bend route cuts through grass below the actual twin-rut road by roughly 15–35px; source-road trace annotations near x570–700 are below the ruts. This is a physical source-pixel defect not visible from training-anchor residuals.

## V258 correction and observed result

Changed the **manual source-image SOUTH centerline** near x520–705, then transported existing cartway and terrain pixels together with the existing V255/V257 bounded remap. The original SOUTH source SHA256 remains `034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3`; WEST remains distinct `2f7b6171c8fa479a61d372a7027e98aa0296ece92e38fc8908bbf65c4d7300fa`. Neither is a historically verified 1780 road or a source-geodesy tiepoint. Original images are generated fictional studies and are **not** published or accepted game assets.

Eight additional original-source road-center holdouts **excluded from the fitting trace** were mapped through the inverse raster warp to unchanged V123 road geometry. V257 median physical-road holdout distance **9.95px**, p90 **26.86px**, max **28.20px**; V258 median **1.79px**, p90 **3.63px**, max **3.79px**. These are independently held-out *manual image-pixel observations* from the same source—not independent geographic tiepoints, not a machine-verified physical road segmentation, and not user approval.

Local full-resolution processing of the exact SHA-pinned PNGs: SOUTH maximum paired displacement **64.19px** (V257 **66.42px**), minimum sampled Jacobian **0.6418**, folded fraction **0**, source coverage **99.8912%**, anchor remap error **0.598px**. WEST remains at V257's **134.99px** displacement, Jacobian **0.5193**, zero folds, source coverage **99.8178%**. Both pass **necessary** mathematical geometry checks; they do not pass art acceptance.

Local Python compilation and seven regression tests passed with both original PNGs present. The GitHub CI environment lacks those images: it can test geometry and SHA guards, but **must skip and disclose actual-image tests**. Tried local Chromium portrait and landscape with the exact WebP art; both were blocked at browser navigation by `ERR_BLOCKED_BY_ADMINISTRATOR`. A separate offline in-memory Chromium attempt did not finish booting within the available execution window. Therefore **NO four-browser exact-V258-art pass is claimed**. Prior V253 four-browser success applies only to old rejected fixtures.

## Critical outstanding acceptance gates

- No independent V209 natural/geographic tiepoints; no 1780 road history verified. Do not infer history from generated art or modern 2023 aerial imagery.
- WEST bridge approaches/banks and both border joins to Matrei not independently source-verified. SOUTH hut-end cartway is a fictional scenic ending, not historical proof.
- Strict V203 microstructure and human realism, exact-art Chromium/WebKit portrait+landscape, actual iPhone inspection, and **user visual approval** are all **RED**.
- Do not promote this to production, publish a playable candidate URL or change immutable V121/V123 routes until those gates are genuinely met.

## Reproduce locally with original images

`PYTHONPATH=scripts python scripts/v258_south_road_recontact.py --west /path/to/winding_track_through_alpine_valley.png --south /path/to/alpine_valley_path_and_river.png --atlas terrain-grid/v123-atlas.js --out /tmp/v258-art`

`V258_WEST_PNG=/path/to/winding_track_through_alpine_valley.png V258_SOUTH_PNG=/path/to/alpine_valley_path_and_river.png PYTHONPATH=scripts python -m unittest -v scripts/test_v258_south_road_recontact.py`

Output images are **unapproved isolated study artifacts**. V123 remains immutable. Production gate remains RED.
