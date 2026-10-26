# V209 — source-to-V123 landmark tie-point intake (candidate math only)

Date: 2026-10-26 UTC. Branch: `terrain-v209-landmark-tiepoint-intake-20261026`. This is an **isolated engineering/evidence tool**, not a game art update.

## Inputs reviewed before changes

- GitHub issue #9 through V208, current V20x branches and V208 source-frame CI 40280001039 (passed).
- Actual V203 Chromium/WebKit portrait/landscape three-center grayscale/high-frequency screenshot contact. Western Pass and Southern Valley are still visibly artificial compared with Matrei; V203 strict art gate remains failed 4/4.
- Actual V208 frame-comparison image, V204/V205 native source plan, immutable V123 atlas geometry and V208 source/game audit. V205 modern forest imagery is **not** registered to the game octagons.
- V163 landmark candidate gate on an earlier branch: its game-coordinate bounds `0<=y<=1024` omit the Southern Valley V123 world frame `1024<=y<=2048`. V209 fixes that by checking the real octagon polygon per cell, rather than a rectangular approximation.

## Actual code

- `scripts/v209_landmark_tiepoint_intake.py` checks that each matched point lies inside its actual V123 clipped octagon and the corresponding native 512-pixel V205 source panel in the EPSG:3857 L mosaic. It requires two widely spaced controls plus **two independent, non-collinear held-out landmarks** for each of the three cells, HTTPS evidence references, natural stable feature types and reviewer attribution.
- Candidate similarities must pass each holdout's <=2% source-baseline residual and agree in scale, rotation and translation across the three cells. This is a **numerical consistency gate only**: cited evidence cannot be independently authenticated by this script. It never treats a candidate as surveyed geography or a 1780 historical reconstruction.
- `terrain-grid/v209-unverified-tiepoints.json` has deliberately empty real matches. Synthetic positive fixtures exist **only** in the test suite; they are not written to production evidence.
- The V208 pinned V121/V123 Git blob checks and V94/V97/V102 source projection checks run before every intake audit. No routes, bridges, movement graph, Matrei photo, HTML, campaign, save or production files were changed.

## CI evidence

- First V209 run 40286663561 failed because of a Python `unittest.assertRaises` test-context typo; corrected without relaxing any gate.
- Final run **40286783612 SUCCESS**: 4 V204 + 3 V205 + 3 V206 + 3 V207 + 5 V208 + **11 V209** tests passed (29 total), source-identity checks passed, and `--require-registered` intentionally returned exit 2. Report artifact **12634466467** is explicitly marked NOT APPROVED.
- The new report says `registrationStatus=BLOCKED_MISSING_REAL_TIEPOINTS` and all geographic, historical, visual, iPhone and production approvals are false.

## Remaining real work

Independently identify and document *real* shared bedrock, ridge, river or valley landmarks in the original V121 Matrei photo and the actual geographic source, with valid pixel coordinates, source identity, and independent review. A mathematical fit is not evidence that a painting or its roads are geographically true. Do not fill the evidence manifest with guesses or synthetic test points.

Only after independent registration: develop period-safe West/South artwork with natural seams, verify physical bridge banks and surveyed road destinations without inventing traversability, preserve the existing four-configuration browser/road/army QA and strict V203 visual parity gate, and request physical iPhone user approval. All four V100 zoom levels also remain unfinished.

**Current status:** sourceRegisteredToV123=false; historicalRoadsVerified=false; bridgeBanksVerified=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false. No merge, deploy or paid services.
