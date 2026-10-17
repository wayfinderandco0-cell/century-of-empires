# Century of Empires — Networked Alpha 0.1

**This is a working multiplayer vertical slice, NOT the full 1780–1880 game.** It runs on a Node 22 server; GitHub Pages alone cannot host its authoritative simulation.

## What is implemented

- One continuously advancing shared 1780 world: 80 named European approximation provinces and 12 nation choices.
- Server-saved campaign file, session seat tokens, state snapshots and Server-Sent Events (real-time updates).
- Server-controlled marching with visible progress, destination orders, ETA, persistent armies, combat, wartime occupation and defensive garrisons.
- Nation resources and continuous provincial workshops and recruitment queues.
- iPhone-first map UI, pinch/drag/zoom, Select Army → Destination → Execute, red marching routes, province inspectors, dispatches.
- Automated server integration acceptance tests covering two players, access controls, movement, occupation, production, restart persistence, and client JavaScript parsing/touch selection.

## Quick start (on a desktop/server with Node 22+)

```bash
node server.js
```

On the computer running Node, open `http://localhost:8787`. On an iPhone connected to the same Wi-Fi, open `http://<computer-LAN-IP>:8787` (not `localhost`). Choose different nations and issue orders. The host computer must remain on for the shared world to advance. By default, 45 real seconds equals one in-game day. You can override `PORT`, `DAY_SEC`, `REALTIME_SCALE` (testing), and `SAVE_FILE` via environment variables. Do not turn on `REALTIME_SCALE` in public campaigns without intentional host-speed rules.

The server persists state to `data/campaign.json`. Store the save on a durable persistent disk before a public deployment. The checked-in `data/world.json` is seed geometry, not a saved campaign.

## Deploying to an always-on service

Choose a Node.js app host that supports **long-lived SSE requests, HTTPS and persistent disk** (or replace file saves with a transactional database). Deploy the `server.js`, `public/index.html`, and `data/world.json` from the same directory. Configure the host's start command as `npm start`. Keep the deployment alive when everyone closes their phones. Put the save under a mounted persistent path using `SAVE_FILE`. Publish the host's HTTPS URL for iPhone Safari; **do not point GitHub Pages at the server without actually deploying it**.

## Known scope / release blockers

- Region geometries are deliberately **80 modern-geographic Voronoi test cells**, not researched 1780 borders. Coastlines are geographically sourced, but legal territorial claims are not historically audited.
- No navy, formal diplomacy, AI order planning, fog of war, peace settlements, technology trees, event engine, authentication, moderated multiplayer or user accounts yet.
- No independently hosted online service: two devices can join only when connected to the same running Node server.
- Save is currently local JSON and seat tokens are demo credentials. Public internet deployment requires real identities/authorization, rate limits, validated game rules, saved-world migrations, monitoring/backups and a database.
- The first atlas is original scalable SVG concept graphics. Its mountains and vegetation are schematic; it is NOT yet the final high-fidelity world map.
- Armies cannot cross disconnected sea boundaries until naval transports are implemented.
- A production campaign needs authoritative server catch-up after downtime; this alpha continues while the server runs, but not when the host is stopped.

## Test

```bash
npm test
```

## Next engineering milestones

1. Stable deployed HTTPS endpoint + durable database and proper accounts.
2. Historically researched 1780 European provinces, topography tiles and true national outer borders.
3. Smooth traffic-aware map interaction + validated pathfinding, fatigue, supply and generals.
4. Naval movement, production economy, diplomacy and AI.
5. Expand to world-scale geography and 30+ players.

This code does not include or copy commercial game source/artwork.