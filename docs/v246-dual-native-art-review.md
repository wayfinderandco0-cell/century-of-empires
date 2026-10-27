# V246 — WEST + SOUTH native physical-cartway pair review (NOT APPROVED)

This is a **two-cell, source-pixel** feasibility tool, not a replacement game map.
It reuses V245's 2D original-pixel landscape remapping and V240's road-pixel
continuity measurement, with V243's pinned immutable V123 WEST/SOUTH coordinates.

**Substantive defect guarded against:** V244's attractive WEST road continued
275px beyond the V123 survey limit. V245's one-cell source manifest could assert
`sourceRoadContinuesBeyondSurvey=false` without recording the full physical
road. V246 requires a *full independently annotated visible road*, a contiguous
playable subset identified by indices, and measures any extra road at BOTH ends.
More than 50px of visually unsupported continuation fails before any warp.

For each source manifest supply: `sourceSha256`, `sourceAttribution`,
`sourceDescription`, `annotationMethod="independent-human-visible-road-trace"`,
`fullVisibleRoadPoints`, `playableStartIndex`, `playableEndIndex`.
Coordinates are native 1536×1024 source pixels; WEST traces run west-to-east,
SOUTH north-to-southeast. Do not copy the V123 points as a supposed independent
source annotation. WEST and SOUTH must be distinct original source files.

Run after source and annotation provenance have been independently reviewed:

```sh
PYTHONPATH=scripts python scripts/v246_dual_native_art_review.py \
  --west /path/to/west.png --south /path/to/south.png \
  --manifest /path/to/independently-reviewed-source-traces.json \
  --out qa/v246-dual-original-pixels
```

Outputs: both original visible-road versus V123 overlays, optional physically
remapped original-pixel images and route overlays, a fail-closed JSON report.
Even if both necessary geometry checks pass, they are **not approved**. Human
visual scrutiny, physically credible bridge banks, independent natural geographic
tiepoints, actual 1780 route evidence, original license verification, Matrei
seam coherence, unchanged strict V203 0.70/0.70 across four phone/browser
configurations, actual iPhone review, and explicit user acceptance remain required.

CI tests *real synthetic pixel relocation* for both routes and negative cases
for 275px WEST / 180px SOUTH extra-road overrun, wrong source hash, missing
human provenance, incomplete road trace and duplicated image sources. Synthetic
images are **NOT game art**. No images are promoted or imported automatically.

The existing generated fictional SOUTH photo-grade study has a promising
north-entry track but continues past the V123 survey endpoint and is not a
verified Austrian location. The V244 WEST study likewise overruns. Both remain
rejected for playable artwork. No main, Matrei, V94 campaign/saves, army sprite,
V121/V123 route graph or core mechanics modifications. Production stays RED.
