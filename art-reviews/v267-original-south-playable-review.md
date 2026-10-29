# SOUTH original source inside the actual V267 playable preview (UNAPPROVED)

The same isolated V267 browser renderer can now display the durable 1536×1024 original gorge-and-stone-bridge source **without** overwriting the currently road-registered SOUTH tile. Use `?southArt=original` or the **New SOUTH art** button. The default preview remains offline and unchanged.

The alternate view loads `art-reviews/v267-original-source/south-gorge-bridge-original-unapproved.webp` at native resolution, retaining its individually painted trees, gorge, bridge and cartway. It uses the same exact V121 frame, zoom, gap inlays, canonical 100-node V123 movement graph and WEST/MATREI sources. The existing narrow road-join patch is disabled in the alternate so the road discrepancy is **visible rather than concealed**. Fixed-route yellow inspection lines are enabled for this alternate.

**Known hard visual blocker:** the original painted bridge sits around y≈480–500, while the immutable SOUTH V123 route expects a crossing near (1140,585). The photographed road also enters the northern border west of x466. The source is fictional game art, not verified historical geography. This alternate is for real-renderer comparison only, **not a road-aligned playable release**. No V121/V123/V94/sprites/saves or production files changed.

Actual phone-size browser comparisons should be generated with `scripts/v267_clean_visual_review.py` and attached to issue #9. No physical iPhone Safari approval or production promotion.
