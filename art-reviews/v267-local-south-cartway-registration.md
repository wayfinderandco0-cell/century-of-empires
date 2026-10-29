# V267 SOUTH cartway photo registration — isolated visual candidate

**Status: UNAPPROVED; production RED.** This is a source-art change only on the existing V267 branch, not a historical geographic assertion.

The new independently generated SOUTH JPEG already had a convincing natural Alpine river gorge, conifers, stone bridge and a dirt cartway. Its photographed road increasingly diverged from the immutable V123 path toward the east. Earlier experiments tried horizontal registration of up to ~210–265 pixels and visibly bent forests or created ghost roads. They were rejected.

The new art bake `scripts/v267_bake_south_cartway.py` instead registers the source road in **vertical photo space at equal x**. From x≈540 to the eastern edge, the original painted road is generally only about 0–95 pixels above the V123 path. A broad, smoothly tapered, near-road-only displacement relocates the **existing photograph and terrain together**, with no invented digital cartway, no global horizontal warp, no mirrored forest and no duplicated road. The result is baked to `v267-original-source/south-cartway-local-registered-unapproved.jpg` and embedded into the same V267 playable HTML, so iPhone Safari performs no expensive registration.

The original 1536×1024 source remains at `v267-original-source/south-valley-recomposed-unapproved.jpg`. WEST source, V121 Matrei bytes, V123 100-node network, V94 campaign, sprites, saves and production main are unchanged.

**Visual limitations:** This is still fictional prototype terrain. A limited deformation near the road may subtly alter trees or rock geometry. The Matrei/SOUTH **horizontal photographic seam** remains a known problem and the user's physical iPhone acceptance is outstanding. The central diamond remains non-playable. Do not claim final road/bridge realism from a browser test.

Review the committed `art-reviews/v267-road-scene-current.jpg` (real Chromium phone-size screenshots, not synthetic renderings) and the WebKit/Chromium CI screenshots before requesting user approval. No production merge without that approval.
