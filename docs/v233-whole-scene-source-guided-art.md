# V233: whole-scene source-guided art experiment (PRODUCTION RED)

2026-10-27. Isolated branch only. No changes to main V192, Matrei, V94, V121/V123 graph, sprites, saves, mechanics or production.

V232 established that the two CC0 Austrian photographic crops were not suitable terrain: WEST 180px obstructed, SOUTH 656px obstructed. V233 explores a materially different method: an entire original source landscape is sampled through a smooth inverse map toward artist-selected clear-ground source coordinates while the V123 game polyline stays fixed. No cloned ground strips, road paint, fake roads, tiled Matrei pixels or procedural detail noise. The method fails closed if source SHA changes, V123 Git blob differs, source guide shifts exceed 80px, the map folds, source pixels fall off-frame, or V232 necessary ground preflight fails. These are necessary conditions, not visual approval.

Actual independent 1536x1024 original AI-generated fictional landscape images were inspected and SHA-256 pinned in terrain-v233/v233-source-guides.json. These are NOT georeferenced Austrian photos or historic evidence; no claim of source-backed V209 tiepoints or 1780 roads. The initial unrestricted deformation visibly stretched mountains, produced seams and blank magenta borders. The fail-closed whole-scene method rejects BOTH: WEST needs 536.0px displacement and SOUTH needs 267.4px, against the 80px safety limit. No rejected images are committed as playable assets.

Source provenance of V232 photos remains documented separately (Stijn te Strake and Volker Schnäbele, CC0 1.0); those photo crops remain rejected. V233 original AI-generated images are fictional illustration, not source-proven geographic terrain.

The new Python script actually performs whole-scene remapping and writes WebP art studies ONLY when geometry and native-ground requirements pass. Unit tests use synthetic fixtures only; their success does not demonstrate game-art realism. No V233 playable screenshots or V203/4-browser acceptance is claimed.

Next substantive task: create two original complete high-resolution compositions WITH the V123 corridor already on open ground, avoiding large warps, and independently source and verify historical/geographic tiepoints if possible. Only then integrate both in an isolated playable preview, run unchanged V203 0.70/0.70 thresholds, four mobile Chromium/WebKit configs, inspect actual screenshots, and seek physical iPhone and user visual approval. Production stays RED.
