# Octagon 001 — route-locked Alpine art study (2026-10-20)

Status: **ARTWORK ALIGNMENT DEMONSTRATED, NOT A PRODUCTION TILE**.

## Problem solved
Earlier attractive art showed a valley path in one position, while 25 hidden route points followed a different line. Never paint a speculative trail independently of the routing source.

The current study starts with a new top-down Alpine scenery painting **without baked roads or rivers** and composes:
- V102 modern mapped Fidlerbach centreline (68 points within/near 001), overlaid as a narrow natural stream.
- Both saved Octagon 001 candidate paths (17 Fidlerbach-bank nodes + 8 southern pack-trail nodes), painted directly from the **same** vectors used by the hidden graph in `BNR-O-0-0-hidden-routing.json`.
- Developer-only dots/boundary drawn on separate output, not baked into the clean artwork.
- 1000m pitch with 60m rectangular bleed beyond octagon area, 1254×1254 pixels.

The visible route centerline and displayed nodes therefore agree by construction. This is a **design invariant**, not an approval of historical accessibility.

## Tested outputs in the Oct 20 ChatGPT conversation
- `century_oct001_route_locked_clean.png`: visible painting only.
- `century_oct001_route_locked_debug.png`: exact hidden-node and blocked-edge overlay.
- `century_oct001_route_locked_clean.webp`: compressed study art.
- `build_oct001_route_locked_art.py`: rerunnable construction and alignment check; source route vectors snapshot in script.
- `century_oct001_route_locked_qa.json`: checks.
- `century_oct001_route_locked_review_package.zip`: bundles this source/art evidence for user review.

These are **conversation attachments, not GitHub assets**. This checkpoint preserves their names, processing details, and intent; do not claim they have been committed or released.

## Remaining failures and safeguards
- **10 blocked candidate segments** remain visible on developer-only diagnostics: 9 coarse-gradient failures, 1 unverified water crossing. Neither infantry nor artillery should be dispatched on those links.
- The scenery painting is illustrative, not derived from a surveyed 1m landform model. Some rock/forest/cliff shapes still differ from the V97 measured elevation, and the rendered narrow stream can cross existing forest cover. The study has geographic path alignment, **not full landform accuracy**.
- The water and trail guides are not independently verified as circa 1800 road/bridge routes; no historic ford is established. `BNR-O-0-0-hidden-routing.json` remains candidate-only with gameplay disabled.
- The 001 east edge has **not yet** passed a visual seam test against 002 or the square connector.
- The full game, saves and previously published V106 atlas proof remain untouched.

## Next acceptance milestone
Refine the art around the locked path corridor rather than move the route to fit arbitrary scenery: restore accurate V97 landform silhouette under the forest art, ensure bank trails lie on plausible shoulders and switchbacks, and make blocked rocky links visually impassable. Then art-direct the shared seam between Octagons 001 and 002 and test iPhone portrait/landscape with a toggleable diagnostic overlay. Only if the user approves these should the new raster enter a public atlas preview.
