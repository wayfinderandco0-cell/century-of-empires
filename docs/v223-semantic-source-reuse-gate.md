# V223 — stop false realism passes from overlapping Matrei source pixels

Status: **source reuse REJECTED / human art REJECTED / production RED**. Isolated branch only.

## Why this change exists

The V222 phone screenshot shows duplicated rivers, cottages, roads and tree
patterns in WEST and SOUTH. Yet V222 passed V203 fine-luma thresholds because
both neighbors were made from the same detailed Matrei painting. A unique
**crop origin** is not a unique landscape. This is a real acceptance loophole,
not an excuse to relax the V203 thresholds.

## Implemented

`scripts/qa_v223_semantic_source_reuse.py` calculates an occupancy map for
every source image using every original `sourceRect` from **both** neighboring
cells. It counts original source-pixel reads, original pixels used, and
overlapping/repeated reads. A candidate fails the *necessary* nonreuse gate if
more than 12% of source-pixel reads revisit source pixels. Source identities
are shared across cells, so two copies of Matrei cannot evade the test by
assigning different crop coordinates. The script produces an exact-source
occupancy heatmap (red = repeated) and JSON report. Missing source identity,
out-of-bounds rectangles and false approval flags fail closed.

Negative controls include genuinely independent source identities (necessary
nonreuse gate passes), almost-identical shifted source crops (fails), and
missing/tampered provenance (fails). Passing this gate **never** proves
perspective coherence, unique semantic objects, license suitability, road
alignment, bridge banks, 1780 geography or human visual approval.

## Evidence and protection

Before coding, issue #9 through V222, latest Actions 40387426416, and actual
V222 WebKit portrait WEST/MATREI/SOUTH screenshot were inspected. The visible
river network repeats across the two neighbors and central Matrei. V222 strict
V203 numeric fine-luma PASS is explicitly insufficient.

V223 runs inherited V137/V202 road/bridge/army/camera tests and V222
four-browser Chromium/WebKit portrait/landscape screenshots without changing
the scene. It separately runs unchanged V203 numeric checks. The final human
approval gate remains intentionally RED. The occupancy heatmap is evidence
of repeated *source pixels*, not a newly approved game screenshot.

No source image, V121 Matrei original, V123 route/bridge graph, V94 campaign,
V100 zoom, army sprites, main branch or saved game was changed. No paid
service, deployment or historical/geographic claim. The next art candidate
must use independently authored or independently licensed whole-cell WEST and
SOUTH artwork, coherent in camera angle and terrain composition, with the
immutable roads on supported visual cartways; verify real tiepoints separately.
Do not repeat the Matrei quilt or use modern orthophotos as period-safe roads.

`sourceRegisteredToV123=false; historicalRoadsVerified=false;
gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`.
