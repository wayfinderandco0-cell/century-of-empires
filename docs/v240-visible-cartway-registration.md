# V240 — visible-cartway registration (isolated, ART RED)

Purpose: stop mistaking a photo-grade landscape, an open meadow, or a painted line for a playable cartway. The immutable V123 route remains the gameplay authority. A **separately traced visible road** on the actual 1536×1024 image must match it; both geometry and actual earth-colored pixels are required. A trace copied from V123 is not independent evidence. The tool cannot independently certify the honesty of a human annotation and reports `annotationIndependentVerified=false`.

## Acceptance thresholds (necessary only)
- Symmetric arc-length sampled visible-road/V123 95th percentile distance <=9px.
- Endpoint mismatch <=14px; missing continuation rejected.
- >=68% of the annotated road has earth-colored evidence within its 9×9 neighborhood; no >50px run without evidence.
- Image SHA256, native size, human-visible-road-trace manifest, and exact V123 Git blob SHA1 required.
- Source license, photo-geography registration, period cartways, bridge banks, human/physical-iPhone review, four-browser gameplay, strict V203 0.70/0.70 and production approval are **separate gates**. All remain RED.

## Why this is needed
V237 original WEST photo has genuine photographic texture and open meadow but **no visible road**. V238 painted a uniform road onto it; ground clearance alone cannot prove a physically authored cartway. V239's new SOUTH source was blocked by Wikimedia HTTP 429; that is not a source pass. V240 CI reuses the already pinned V237 original photo from the existing GitHub artifact, with no Wikimedia requests.

Local isolated visual experiment (not a committed game asset): an original 1536×1024 fictional photo-grade Alpine concept with a visibly integrated dirt road was manually traced independently. The V240 metric returned **135.86px p95 misalignment** and **277.35px endpoint error**, although visible earth-color continuity passed. It was rejected, not warped or presented as a playable road. The image is neither Austrian geographic evidence nor period-road proof. The annotation is provisional and not independently audited.

## Usage
```bash
python scripts/v240_cartway_trace_registration.py \
  --image PATH_TO_UNALTERED_OR_AUTHORED_1536x1024_IMAGE \
  --trace PATH_TO_INDEPENDENT_VISIBLE_ROAD_TRACE_JSON \
  --atlas terrain-grid/v123-atlas.js \
  --tile west --output qa/v240-review
```

Trace JSON must include `sourceSha256`, `annotationMethod: "human-visible-road-trace"`, and `visibleRoadPoints: [[x,y], ...]`. Output includes a red immutable graph overlay, cyan visible-road trace, measured distances and fail-closed report. No assets are promoted.

Next meaningful step: author WEST and SOUTH landscapes around the actual V123 centerlines *at creation time*, trace the visible road separately, verify banks and borders, then run all four mobile configurations, strict V203 and physical/user visual acceptance. No new source should be declared historically registered without independent natural tiepoints.
