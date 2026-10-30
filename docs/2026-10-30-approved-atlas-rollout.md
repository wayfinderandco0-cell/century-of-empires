# Century of Empires — approved three-octagon art method and Europe rollout

**User decision — 2026-10-30, physical iPhone screenshot at 2:33:** APPROVED the V267 visual/art method displayed in the `?southArt=coherent` preview (WEST original cirque + MATREI + reauthored SOUTH), based on Git commit `456107f28c8db1f87522bbc7511809b2a215f6fb`. The screenshot's preexisting "UNAPPROVED" banner is superseded **for this art-method decision only**. Do not misinterpret this as evidence that production integration, every road seam, historical topography, or Europe-wide tiles are already finished or independently verified.

## Keep the visual method; make different geography
- Use the approved high-detail, natural Alpine art composition/registration method as a **production pattern**: original locally appropriate landscape per octagon, roads physically embedded in terrain, correct native tree/river proportions, continuous visible road surface at occupied sides, non-playable infill without false roads. WEST, MATREI and SOUTH must remain visually distinct.
- Do NOT copy, mirror or stretch identical mountains, houses or trees into every cell. The wider European map needs geography-specific original art: coast, plains, rolling farmland, forests, mountains, rivers and cities appropriate to each region. No global terrain warping, digital highway stripes, arbitrary terrain filler, warped forests or impossible bridges.
- Preserve immutable V121 original Matrei art, V123 route graph and seam mechanics, V94 campaign, units/sprites, controls and saves until tested integration. Keep the approved V267 commit available as fixed fallback/reference.

## Towns and conquest (confirmed by user)
- **Most map area should be terrain, roads, fields, forests, rivers and passes**, NOT a dense network of towns. A scenic hamlet/farm/village can exist without a capture target.
- **Meaningful strategic settlements** (historically appropriate capitals, market cities, forts, ports and important pass towns) establish or control territory through explicit province/strategic-node ownership. They must show national/territorial control changes when conquered, consistently at all zoom levels.
- A scenic settlement does **not** silently grant territory, create an army road node or become conquerable. Do not make every village a prize.
- Maintain per-tile separation: `geometry/biome/art`, `road & bridge graph`, `scenic settlement`, `strategic province/objective`, `owner/controller`, `army`, and `historical evidence/scenario date`. Owner and controller can differ during occupation.
- Existing project issue #9 establishes **European scope around 1780–1880**, an 80-province playable vertical slice before a roughly 1,100-province objective, and a previously validated geographically aligned atlas design of roughly 432 octagons. Treat octagon count, strategic province count and towns as **different units**. Avoid assigning unsupported historical locations, historical roads, or fixed national borders across the entire century; use the chosen scenario date and evidence. Fictitious experimental Alpine artwork must remain labeled as such.

## Implementation stages — code and art, not endless research
1. **Freeze this approved visual sample** in a stable branch/commit, link a working iPhone view and screenshot evidence. Preserve the three original artworks and source process, not only a finished image.
2. **Integrate the approved 3-octagon renderer with the actual game engine** without changing existing saves, sprites or combat. Regression check army taps/march/halt/redirect, road crossings and zoom/pan on real iPhone sizes; do not call it production-complete until integration and tests actually pass.
3. **Generalize the cell pipeline**, not 432 manually cloned HTML pages. Add a reusable art/geometry manifest with octagon ID, bounds/world origin, image/source provenance, biome, seam targets, road graph, bridges, scenic structures, strategic nodes/province IDs, scenario-era labels and approval/verification statuses. Generate reviewable batches with source-based roads and varied terrain, then composited scene tiles.
4. **Build a neighboring 3x3 block / 8–16-cell regional pilot** to prove every direction seam, diagonal decorative inlays, road-free unused borders, river continuity, player-selected marching and performance. Use one canonical graph for rendered and traversable road geometry. No phantom roads across corners.
5. **Scale geographically across the European atlas in batches**, treating land and water regions correctly. Prioritize landmark/strategic province areas and transport corridors; most cells can have no capturable towns. Start the 80-province gameplay slice and only then expand toward ~1,100 provinces/432 world octagons. Do not pretend a complete 432-octagon production world exists before rendered and playable integration tests.
6. **Conquest gate**: after a strategic place is captured, map ownership colors, city/fort flags, province panel, resources/supply and persistence should update consistently without altering scenic-only villages. Equal rules for AI and player.

## Required checks for each batch
- Phone-sized rendered screenshots plus actual visual review: no duplicated landscapes, warped trees, unexplained green squares, obstructive large panels or abrupt seams; terrain remains believable at close zoom.
- Road-to-graph ground contact at border and bridge; scripted WEST→MATREI→SOUTH movement remains unchanged, plus new-tile multi-seam traversal and tap hit areas.
- Exactly one recognized world-space placement for each tile: no visible gaps, duplicated fake roads or overlapped centers; no false road through non-playable inlays.
- Mobile Safari memory/zoom/pan and four zoom-level correspondence; guarded savegame and gameplay regressions. Keep public main separate until validated.

## Active work instruction
The user has said "this is approved" and explicitly directed expanding the method to **all octagons**. Stop seeking another approval for the same three-tile art style; move into integration and scalable multi-tile production. Ask for review only of material design departures or production-release milestone. Use existing hourly development automation; each run must make real, reviewable code/art progress and update issue #9 with evidence. No paid services or spending.
