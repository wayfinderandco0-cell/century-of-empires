# V229 Austrian source-art experiment — 2026-10-26 (NOT APPROVED)

**Status: experimental and rejected as final artwork. Production and user visual gates remain RED.** This branch is isolated from `main` (V192). It does not change V121 Matrei painting, V123/V121 road/bridge geometry, V94 campaign or saved games, army sprites, V100 mechanics or production deployment.

## Two independent high-resolution, authentic East Tyrol sources

Both photographs were made by **Michael Kranewitter** and are available under **CC BY-SA 4.0** on Wikimedia Commons. Derived artwork must retain attribution, modification notice, and share-alike obligations.

- WEST: [Guggenberg von Norden a.JPG](https://commons.wikimedia.org/wiki/File:Guggenberg_von_Norden_a.JPG), 6000×4000 original; source SHA-256 `273218ffd17e79fc8fb2c1e6db609b53045be955ac7284d60945a588ff383e55`; 1536×1024 crop `[3600,1950,5136,2974]`.
- SOUTH: [Bichl von Nordwesten.jpg](https://commons.wikimedia.org/wiki/File:Bichl_von_Nordwesten.jpg), 6000×4000 original; source SHA-256 `afb9f2c80f8e436ad20a3bc085e4cb9badfaee5075ea80c6e39b14746e67fc7d`; crop `[400,2400,1936,3424]`.
- License: [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Changes: native-pixel crop, luminance contrast and 28px illustrative V123 road-corridor inpainting. No original Matrei pixels are reused. Each source is independently identified and pinned by SHA-256.

The photos depict **modern East Tyrol**, not surveyed 1780 cartways, bridge banks, or independently registered V209 source/game tiepoints. Source **location** and source **license** are established; source-to-game coordinate registration is NOT established.

## Executable art development

`scripts/build_v229_austrian_source_art.py` downloads pinned originals, validates original SHA-256, generates distinct 1536×1024 WEST/SOUTH WebP assets, and writes an explicit false-approval manifest. A narrow 28px *illustrative* road clearing uses unchanged V123 geometry; it is not a verified roadbed or historical cartway.

`terrain-grid/v229-austrian-source-art.js` validates both independent sources, author/license, SHA-256 of rendered assets, dimensions, and false approval flags before drawing only the WEST and SOUTH octagons. `v229-austrian-source-art-review.html` is an isolated opt-in interactive game-art preview. `scripts/test_v229_austrian_source_art.js` tests positive integrity and negative controls. `scripts/qa_v229_source_art.py` captures real Chromium/WebKit portrait/landscape screenshots, checks Matrei center pixel equality at identical camera settings against V227, and checks original graph/army movement. CI runs unchanged V203 numeric thresholds against the V229 screenshots, then intentionally fails the human/production gate.

## Actual pre-CI artwork inspection and limitations

The generated WEST crop visibly contains meadow and conifer stands, and SOUTH is predominantly a modern pastoral meadow. Their perspective and semantic terrain remain **incompatible with Matrei's steep, rocky river/bridge scene**. Road-corridor inpainting is not a convincing period cartway or a bank reconstruction. These assets are *not* accepted game art; this is an inspectable alternative and provenance experiment, not a production solution. Do not merge or deploy based on source authenticity or numerical V203 results.

Source/game natural tiepoints remain absent; unverified western/southern road endpoints remain unverified. All four V100 zoom levels and physical iPhone/user visual approval remain unverified. Future work must author distinct coherent oblique Alpine landscapes with plausible original-graph cartways and genuine destinations without altering protected geometry.

No spending, no merges, no production/saved game changes.
