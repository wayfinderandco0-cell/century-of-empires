# V267 SOUTH native-photographic northern gorge — UNAPPROVED

This is a fictional Alpine game-art prototype, not verified 1780–1880 topography. It stays on the existing isolated V267 branch. No V121 original Matrei image, V123 graph, V94 campaign, sprites, saves, or main/production file is modified.

## Source-level art change

The durable 1536 × 1024 SOUTH source image at art-reviews/v267-original-source/south-river-throat-recomposed-unapproved.webp rebuilds the northern river corridor using the original SOUTH photographic gorge and rigid, unwarped rocky meadow from a different part of that source. The previous northern watercourse at approximately x650 is replaced with natural photographic rock/grass. The water and limestone banks now approach Matrei's downstream water exit around x930–950 at the north edge and converge to the untouched SOUTH river by y445. This is not a digital road stripe or procedural green infill; no extra village or road is added.

The V123 SOUTH cartway corridor x<530 is pixel-identical to the input image, including the fixed x466 northern entrance. Everything at y>=445 is also pixel-identical, including the original stone bridge and lower cartway. 189,867 image pixels differ by more than 8 RGB levels. The source artwork remains preserved and reproducible via scripts/compose_v267_south_road_gorge.py.

The optional review selector is ?southArt=throat. Default SOUTH, ?southArt=continuity, Matrei, WEST, and production remain unchanged.

## Evidence and limitations

- art-reviews/v267-river-throat-source-before-after.jpg compares actual image pixels at identical coordinates. It is not a browser screenshot.
- The source-level join inspection improved river centerline alignment but still shows an abrupt forest/meadow transition at Matrei's lower edge.
- Limestone on the right riverbank has some diagonal stretching because only the narrow gorge corridor is source-registered; the rest of the forest is not globally warped. This remains a visual defect, not a pass.
- The actual Chromium/WebKit phone-size review script also renders the opt-in candidate, creates matching before/after screenshots, and verifies V123 WEST → MATREI → SOUTH touch marching. Passing that check does not constitute user visual approval.
- Preserve the road-free central diamond and the non-playable inlays.

**Approval gate: RED.** No promotion or production integration without physical iPhone visual acceptance and unchanged V94/gameplay regressions.
