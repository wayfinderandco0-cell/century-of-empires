# Century of Empires — Barrier Terrain and Historical Corridors

Date: 2026-10-20. **Movement access decision recorded, not live campaign integration.**

## User review outcome
Octagon 001's two painted trail candidates were rejected. Neither is a credible continuous troop route. The east-bank strip, in particular, is disconnected and appears to run through difficult cliff terrain. Their 34 newly proposed path dots and 25 earlier legacy candidates are retained solely for diagnostic/provenance purposes, **not gameplay**.

**Authoritative for future puzzle integration:** `ACTIVE-ROUTE-REGISTRY-v1.json`. It makes Octagon 001's **approved route count zero**, Octagon 002's **approved route count zero**, and the square connector `BNR:S:0:-1` **closed**. The 001/002 geometry and existing river alignment have not changed. Existing game routes and saves are not touched by this policy file.

Do NOT misrepresent an artistic mountain valley image as proof no human could historically traverse the entire physical area. Status is **no validated passable route in this prototype pending geological and historical survey**, not a permanent classification of all land within the polygon.

## Player-facing terrain
- Keep the natural-looking Fidlerbach river artwork, meadows, cliffs, spruce forest, and terrain variation.
- Remove the two painted fake roads/strings and **all** white/yellow/red route markers from the player-facing image. The earlier clean river-only source `century_oct001_vnext_natural_river_clean.jpg` is an excellent **illustrative style reference**, not a registered public game asset.
- Hidden debug may display rejected candidates with a crossed-out/no-approved-route legend, but must not suggest they are usable or show functional travel.
- Barrier effect in future gameplay comes from absence of approved graph connections, not just a magic +100% obstruction number painted on octagon. Units can still defend nearby valid approaches and terrain can affect battle; do not grant impossible transit.

## Route review policy: all octagons
1. Each cell may have 0–N actual usable route connections. Structural octagon midpoint portals are **not** roads.
2. Passage requires verified physically plausible corridor, troop-specific suitability, water crossings, historical scenario support and matching canonical edge portals.
3. Rivers, steep cliffs and winter obstruction can block, delay or constrain passage. No imaginary bridge/ford is inserted to make the graph connected.
4. Neighboring visuals should join seamlessly even when travel is blocked. The square connector is a **geometric seam**, not automatic path connectivity.
5. Store three distinct states: `NO_APPROVED_ROUTE`, `NOT_VERIFIED`, and `APPROVED`. Never replace uncertainty with a claim of proven global impassability.
6. Keep candidate paths in provenance files, but **none** may be loaded as active army edges without explicit promotion through the registry.

## Better place to develop our first real Alpine road
Historic sources establish the old Brenner road through the main Wipptal transit valley (Matrei, Steinach, Vinaders / Gries and Brenner Pass). The Brenner road was carriage-passable during the target era; **do not backdate 1833–1845 revised road sections, 1867 railway or modern motorway** into the 1800 scene.

Sources: [University of Innsbruck Brennerpass history](https://orawww.uibk.ac.at/apex/uprod/f?p=LLW:3:0::NO::P3_ID:1179); [Wipptal region geography](https://www.wipptal.at/en/your-wipptal/the-wipptal-valley); [1911 Britannica (road and rail historical chronology)](https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Brenner_Pass).

**Next build:** source and georeference an 1780–1800-era road alignment at a manageable 1km segment of the Wipptal; check route geometry and grade. Only then create the polished road/river/forest artwork and nodes from the same accepted line.

## Freeze
`v94.html`, V100–V106, `v106-atlas-puzzle-proof.html`, campaigns/save keys and all existing gameplay remain unchanged. The new route registry is **design data** and needs explicit integration tests before it can change gameplay.
