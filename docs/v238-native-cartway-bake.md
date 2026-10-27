# V238 — native photographic cartway bake (ART RED)

This isolated branch tests a substantive physical-road alternative, not another
photographic crop presented as finished game art. It takes the previously
verified 1536×1024 native WEST meadow photograph (Stijn te Strake, Austria,
CC0 1.0; source crop SHA256
425d85e01adb9a34a141d1f2860a2e35575bbad42ba1eda1392301f46ae78b41)
and an **independent** 6000×4000 CC0 photograph, *Peaceful Austrian valley*
(Jace Grandinetti, 2016, Gries am Brenner, Austria; original Wikimedia SHA1
f9cc498c7ff512e40a4d00023e1524a40fd9b898). Original source pages:
https://commons.wikimedia.org/wiki/File:Forested_mountain_valley_(Unsplash).jpg
and https://commons.wikimedia.org/wiki/File:Peaceful_Austrian_valley_(Unsplash).jpg.
Both CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/.

The code bakes a **narrow 25px cartway with verges and wheel-worn bands**
directly along the **unchanged** V123 polylines. It uses high-frequency
material from the original source photograph and local illumination, not
synthetic noise, cloned photo patches, broad brown highway bands, or road
graph edits. The conservative canopy-aware source-ground test runs **before**
any candidate can be exposed as a two-cell gameplay preview. WEST and SOUTH
must **both** pass, or only diagnostic images are saved; a blocked download
or unsuitable source cannot silently fall back to another image.

The SOUTH photo is near Gries am Brenner, not a Matrei-registered survey.
The exact game/source natural tiepoints from V209, 1780 road evidence, valid
bridge banks, matching photographic camera, source-period safety, and
human realism remain **unverified**. A baked road following V123 is an
**illustrative fictional road**, not evidence that the route existed.
A green necessary-ground test does not imply a correct historical road or
acceptable artwork. Human inspection of actual screenshots is mandatory.
The strict unchanged V203 0.70/0.70 test runs on four phone/browser configs
only if both ground tests pass. Production remains deliberately RED.

No changes to main, V94 campaign/saves, Matrei, V121/V123 topology,
army sprite options, core gameplay or live deployment. No paid services.
No completion or user approval is claimed.

Run: python scripts/test_v238_native_cartway.py
CI: .github/workflows/qa-v238-native-cartway.yml
Generated review: qa/v238-native-cartway/
Conditional iPhone-openable preview (only if both sources qualify):
v238-native-cartway-playtest.html on the isolated branch.
