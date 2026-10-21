# Century of Empires — Matrei / Wipptal corridor checkpoint

Date: 2026-10-20; isolated branch `terrain-puzzle-atlas-v1`.

## Working geographic control: validation PASSED
- Target historic transport market: Matrei am Brenner, near 47.130278°N / 11.453056°E (historical streetscape photo geolocation).
- Geographic cell `WIP:O:0:0`: 1,000m-pitch octagon, local metric x east / y north. Not the previous Navis side-valley Octagon 001.
- Extracted eight contiguous modern OSM Brennerstraße/B182 street ways and joined them with **zero endpoint gap** into a single `1,035.69m` polygon-clipped road guide (north border x ≈ −34.714m, south border x ≈ −113.419m).
- Derived **27 candidate invisible waypoints**, **26 consecutive link intervals** along the **actual curved road polyline** (not straight chords); all are **disabled for gameplay**.
- Mapped watercourse overlap found **Waldraster Bach** at local (−47.39126m, +404.53448m). It falls inside the candidate segment from `WIP:O:0:0:R0:N2` to `WIP:O:0:0:R0:N3`. This span is tagged `BLOCKED_UNVERIFIED_CROSSING`. No bridge/ford fabricated.
- Retained V97 coarse elevation: center ~993.2m; maximum interpolated route-screening grade ~11%. Sampling spacing ~160–230m makes this **non-certifying**, especially for artillery or historic wheeled access.
- QA confirms actual route polygon containment, continuous vector, disabled links, explicit crossing block and no fabricated historical exact alignment.
- Geographically registered control image `matrei-modern-road-control.jpg` is a **developer diagram over coarse old V97 relief**. It is NOT finished visual art and should not be promoted as a polished game scene.

## Historical-source distinction
The Brenner passage through Wipptal and Matrei was established by c.1800, and the 1777 upgrade is documented. **Exact road centerline** currently comes from **modern** OSM, so all positions are provisional until period maps or local town sources confirm how the 1780 road ran. The Roman/medieval/historic market road through Matrei is separate evidence for the *existence* of transit, not automatic evidence that every metre of today's B182 follows it. Don't depict railway, motorway, modern signalized junctions or later road structures in 1800 gameplay.

Source links:
- https://orawww.uibk.ac.at/apex/uprod/f?p=LLW:3:0::NO::P3_ID:1179
- https://austria-forum.org/af/AustriaWiki/Brennerstra%C3%9Fe
- https://en.wikipedia.org/wiki/Matrei_am_Brenner
- Modern route geometry © OpenStreetMap contributors, ODbL (OSM 0.6 map extract, attribution in control JSON).

## Next art milestone
Use this locked geographic control as the underlying reference for **one premium period-1800 Matrei market-town road cell**: period-appropriate narrow historic road and buildings, Sill valley, real mapped side streams, realistic forest meadows and mountains. Trail illustration, troop route centerline and invisible nodes must be derived from the same accepted geometry. Do NOT paint a bridge at Waldraster Bach until its historical/scenario provenance is resolved. Develop adjacent art only after this cell and its entry/exit seams are approved.

## Freeze
The original Navis Octagon 001 remains **no approved route**; Octagon 002 unverified; connector closed. Existing V94, V100–V106, game systems, and campaign saves unchanged.
