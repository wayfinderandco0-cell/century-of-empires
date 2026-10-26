# V215 — native contiguous Alpine source seam atlas (NOT game art)

Date: 2026-10-26. Isolated branch `terrain-v215-source-native-seam-atlas-20261026` from V214. No edits to main, production, V94 campaigns/saves, the original V121 Matrei photograph, V123 road/bridge/army graph, or original phone movement geometry.

## Pre-work evidence

Read issue #9 through V214, inspected current V214 branch and CI 40324001220 (source-material audit SUCCESS; original four-phone route tests SUCCESS; unchanged strict V203 playable art parity FAILED), inspected actual V213 WebKit portrait three-cell game-versus-authentic-modern-source screenshot and V214 original native material contact. V214 quarantined a visible 2023 imprint that older V207 exclusions missed. V94 is a broad equirectangular European atlas; V97/V102 are modern geographic relief/materials. The V205 native forest source is geographically contiguous but approximately 3.578 km from the independent modern Matrei anchor. It is **not** a surveyed match for the painted V121 Matrei photo or V123 roads.

## Actual code

- `scripts/v215_native_source_seam_atlas.py` composes the three original V205 512×512 modern EPSG:3857 source panels at their exact original L-shaped positions in one 1024×1024 RGBA atlas. WEST adjoins MATREI; MATREI adjoins SOUTH. Southwest has no source and stays fully transparent. No scale, warp, repetition, inpainting, new cartways, or imagined settlements.
- It applies **V207 + V214** reviewed modern-feature/date exclusions as transparent pixels with zero hidden RGB. Visible retained pixels must be byte-for-byte identical to decoded original SHA-pinned source. This is modern photographic source, not an 1780 vegetation inventory.
- Computes original 512px source boundary continuity at the two shared panel edges only where both sides are unmasked, with within-panel RGB-gradient controls and a minimum valid-pair gate. This is **NOT** a Matrei painting seam, bridge-bank survey, route alignment or visual approval.
- Generates a source-only contact with explicit unfilled areas and required basemap.at CC BY 4.0 attribution. The contact labels are review annotations, not geographic content.
- `scripts/test_v215_native_source_seam_atlas.py` tests source hash pinning, exact RGB/alpha, modern exclusions, unsupported source areas, seam coverage, tampered seam metrics, changed pixels, altered contact evidence, and false approval flags.
- `.github/workflows/qa-v215-native-seam-atlas.yml` retains V204–V214 source/geography controls and the unchanged original Chromium/WebKit × portrait/landscape road, bridge, army, camera and **strict V203 photographic-detail gate**.

## Limits

The atlas is **not** placed in playable terrain, because the three modern forest panels do not have independently verified V121/V123 tiepoints and their 512px source frames do not map to 1536×1024 game octagons. It may contain modern features missed by existing masks. This step establishes reproducible natural-source pixel provenance and actual geographic source seams without claiming historical authenticity or drawing counterfeit roads.

Still required: source-to-game independently reviewed landmarks, high-resolution historically plausible West/South artwork with no artificial repeated trees, Matrei/photo and bridge-bank seam alignment, verified meaningful route destinations, all four V100 zoom levels, original real iPhone visual inspection and explicit user acceptance.

`sourceRegisteredToV123=false; periodSafe=false; historicalRoadsVerified=false; bridgeBanksVerified=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`.

CI evidence and actual artifact inspection must be recorded after jobs finish; source-audit PASS cannot override the strict playable-art RED result.
