# V255 — existing physical-cartway pixels to V123, isolated art experiment

**Status: NOT APPROVED.** Neither WEST nor SOUTH is verified historical geography.
No source-to-game natural tiepoints, bridge-bank validation, V203 acceptance,
four-browser testing with THESE original fictional images, or user visual approval.
Production approval must remain RED.

## Why this is a substantive correction

The V254 warp paired entire roads by normalized arc length and Gaussian-smoothed
the resulting displacement. A geometric pass did not guarantee that road pixels
landed on the immutable V123 centerline: the actual SOUTH middle bend visibly
diverged. V255 instead uses one-to-one *image-pixel* observations for each V123
road anchor and an unblurred continuous falloff remap. Existing source pixels,
including the actual earth cartway and surrounding ground, move together. The
route graph is not touched. This is NOT painting a line onto the terrain.

Original sources: two distinct OpenAI-generated **fictional** 1536x1024 PNG
project studies, not third-party photos or historically registered orthophotos.
WEST SHA256: 7326e88c778ed4a0018c241156e701690e95deb1feeb8fa13a298c0f0c74505e.
SOUTH SHA256: 034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3.
The original PNGs are held in the local art-study archive, NOT committed or
served to gameplay. Image-pixel anchors were sighted manually; they have NOT
been independently verified as geographic source/game control points.

## Locally executed against the ACTUAL two source images

- WEST: maximum paired displacement 149.00px; sampled Jacobian min 0.2583;
  observed source coverage 99.8372%; max anchor remap error 1.012px;
  zero sampled folds; necessary transform geometry PASS.
- SOUTH: maximum paired displacement 82.62px; sampled Jacobian min 0.5073;
  observed source coverage 99.9040%; max anchor remap error 0.000px;
  zero sampled folds; necessary transform geometry PASS.
- Six local unit tests PASS, including transport of a synthetic *existing*
  source road onto the V123 path, wrong SHA rejection, and V123 Git blob guard.

**Important limitation:** 0–1px *mathematical anchor error* does not prove the
manually observed anchors are the true center of the physical road. Human review
of the actual new SOUTH output still finds slight mid-bend road drift, and WEST
is not independently annotated. Real art remains rejected. The V255 CI only
runs synthetic geometry, not the uncommitted original-image render.

The previously downloaded **actual** V253 WebKit three-octagon screenshot shows
the old licensed Kosovo photographs with dashed V123 routes through forest,
not a completed playable map. That screenshot was inspected before V255 work.

## To reproduce local real-pixel experiment

Run with the two original SHA-pinned PNGs and the unchanged V123 atlas:

python scripts/v255_anchored_cartway.py --west ORIGINAL_WEST.png --south ORIGINAL_SOUTH.png --out v255-local-art --atlas terrain-grid/v123-atlas.js

## Remaining blockers

1. Independently trace WEST and SOUTH visible road centers and both endpoint
   terminations in original image pixels, then repeat pixel-contact review.
2. Establish legitimate source-to-game natural geographic tiepoints (V209
   remains unverified); do not call fictional roads historical 1780 routes.
3. Verify Matrei seams and real physical bridge-bank approaches.
4. Host or commit legally usable, high-resolution image assets for exact
   four-browser iPhone Chromium/WebKit portrait/landscape gameplay testing.
5. Run unchanged strict V203 thresholds, inspect actual screenshots, and obtain
   explicit user visual approval. Never promote based only on synthetic tests.

Protected Matrei, V94 campaign, saves, army sprites, V121/V123 roads and core
gameplay remain unchanged. This branch adds only isolated code, tests, workflow
and documentation.
