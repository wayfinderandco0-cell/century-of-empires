# Century of Empires — V100 Brenner slice resume checkpoint
Date: 2026-10-20 (America/Chicago)
Development branch: `terrain-v100-brenner-gameplay`
Base: main commit `706c447886ea3e6b337272a23cb2619205b25152` (published V99 preview).

## Confirmed state
- V100 development branch created and isolated from main.
- This checkpoint document is the first V100 commit. **No playable V100 build has yet been committed, mobile-tested, or published.**
- V99 terrain preview exists: `v99-brenner-real-trees-streams.html`, with V97 measured mountain relief, Austrian official orthophoto tiles at close zoom, and V99 88 OSM-mapped local waterway segments (73 streams per prior QA).
- V94 game `v94.html` and campaign-save behavior must remain unchanged. Do not touch V94 or its save keys. Build V100 as a separate file.

## User-approved design decisions — do not re-ask
1. **One vertical slice first**, Innsbruck → Brenner Pass, rather than rebuilding Europe at once.
2. **Very few army routes.** Main geographically credible valley/pass corridor only for prototype; at most one meaningful alternate later if it improves gameplay. Do NOT copy modern road spaghetti or create dozens of bypasses that prevent armies meeting. Soldiers, cavalry, artillery/wagons should be directed to real crossings and mountain passes.
3. Preserve the realistic V97 mountains and V99 close aerial trees and mapped streams; improve blue river/stream blending. Modern image data must not be presented as historically verified 1780 roads/forests/bridges.
4. Zoom LOD:
   - far zoom: terrain and borders only; **no town labels, towns, or army units**.
   - medium zoom: town names and locations appear; army units only simple nation-color dots, no counts or sprites.
   - close zoom: reuse the existing V94 unit artwork for visible units, scaled naturally to map terrain and routes; no giant figures.
   - maintain consistent world coordinates between views and keep switches smooth.
5. Fog of war:
   - player's own armies always visible where appropriate for the zoom level;
   - enemies visible only if within scouting radius of own armies, observed territory, or allied shared-visibility border areas;
   - otherwise **do not reveal enemy army count or exact positions**. Last-known markers may be a later enhancement, clearly marked stale.
   - zoom LOD **never overrides fog of war**.
6. Gameplay goal: army travels along the selected valley route; river crossings and steep gradients affect travel; opposing armies sharing the corridor are capable of meeting/engaging.
7. Test on iPhone-size viewport before promising a user-facing build. Publish only after basic JS, map, touch, and assets pass QA.

## Next action in next active session (no background work)
Create `v100-brenner-slice.html` on `terrain-v100-brenner-gameplay`, borrowing V99 geography layers and V94 unit art, implementing a **minimal interactive demo**:
- One main Innsbruck–Brenner corridor with a known, clearly illustrative path and limited encounter choke point; label historical uncertainty.
- Two sample armies approaching along this route; marching/start-pause-reset controls and collision encounter indication.
- 4-level existing map control with user LOD rules, including no towns/units at level 1, medium town names + dots, and detailed sprites closer in.
- Small simple player sight range and ally share toggle to demonstrate fog; do not expose enemy count outside sight.
- Existing V99 aerial close-up works, mapped streams are kept and water styles improved if feasible.
- All prototype armies and controls isolated, not wired to production V94 save state or combat engine yet.
- Verify behavior and publish a standalone preview only when ready; say what is real vs simplified.

## Explicit blockers / honesty
- Branch creation != playable V100.
- No verified 1780 road or bridge dataset yet; paths require curated historical geography review.
- Existing V94 army movement is province-link based; route-aware pathfinding integration and true combat engine are **not** complete.
- Current V99 aerial-view overlay and regional relief are separate display layers; sprite positions/visibility must be consistent across them.
- No autonomous ongoing coding between chats. Resume work from this checkpoint when user returns.

## Success checklist
- [ ] V100 HTML prototype added and opened successfully
- [ ] Only one visible main strategic movement route in Brenner
- [ ] Far: no towns/labels/units
- [ ] Medium: labels + basic dots only, detected armies only
- [ ] Close: scaled V94 sprites for detected armies, same positions
- [ ] Two opposing troops advance along corridor and can meet
- [ ] Fog hides enemy positions/counts outside scouting/ally sight
- [ ] Streams, aerial canopy and relief appear and load together
- [ ] Mobile visual QA passes
- [ ] Standalone user test URL available
- [x] V94 and user campaign saves preserved by isolated V100 branch
