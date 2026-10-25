# V191 — Austrian/South Tyrol source white-region topology (NOT GAME ART)

**2026-10-25.** Isolated branch `terrain-v191-source-white-connectivity-20261025`, derived from the V187 SOURCE audit. No edits to main, the V94 campaign or saves, V121 Matrei painting, V123 roads/bridge graph, or the live preview.

## Why this change exists

V186 reported **138,560 candidate pixels** where the Austrian source looked nearly white and South Tyrol 2023 WMS supplied color. V187 measured a high mean RGB difference (**141.660**) at candidate/observed boundaries. Treating all near-white pixels as provider no-data would risk erasing real Alpine snow/cloud/bright rock. V191 classifies the original candidate mask by four-neighbor connected components, distinguishing a region connected to the bottom of the sampled source rectangle from isolated interior white patches. This is **not** an official Austria–Italy border polygon, and even a bottom-connected region could contain snow.

## Implementation and checks

- `scripts/v191_south_nodata_components.py`: verifies V184/V186 source manifests and candidate mask; refuses replacement over observed non-white pixels, fractional alpha and white replacement; counts four-neighbor connected components; emits a **source-only transparent review mask** and exact reproducible JSON with SHA-256. It does not alter either source image or the game.
- `scripts/test_v191_south_nodata_components.py`: six deterministic tests for disjoint component counts, diagonal separation, unchanged source bytes, and rejection of invalid overlays.
- `.github/workflows/qa-v191-source-white-connectivity.yml`: inherits 32 V184–V187 source tests, adds six new tests, restores and re-verifies original modern-source artifacts, and independently recomputes the component report. Source artifacts are reacquired if their short-lived archives expire.

## Measured independent artifact check

Downloaded and inspected the actual V184 60-tile modern source artifact and V186 ten-tile South Tyrol candidate artifact on 2026-10-25. The classifier reported **138,560** candidate pixels in **56** connected components: one **138,484-pixel** component touching the southern edge of the source rectangle, plus **55 tiny interior components totaling 76 pixels**. The largest component occupies source-local bounding box **[387,154,1141,511]** in the 1280×512 bottom-two-row crop. No candidate touches another outer edge independently. All 138,560 original near-white pixels in that crop had alternative-color candidates; none remained unresolved under the original heuristic. These measurements are topological, not geographic or historical certification.

The actual mask was opened: it shows one broad wedge and isolated small speckles. **Do not infer that this proves the political border, source validity, or an approved seam.** The V187 141.660 mean RGB seam warning still stands, and modern highways/rail/buildings remain in modern source imagery.

**Phone GAME reality:** downloaded and inspected V189's actual 12-screen artifact (run 40211801946), including WebKit portrait west/Matrei/south. West/South remain blurry procedural hills and trees versus Matrei's sharp bridge, river, and rocks. All four strict V189 mobile configurations still reject detail parity. This source audit does not improve that art yet.

## Next action

Independently verify the modern-provider footprint against an authoritative border/coverage polygon and exclude snow/cloud; then build geographically registered, period-safe west/south material. Do not invent V123 road/bridge continuation. Re-run strict four-browser art/movement QA and obtain physical iPhone approval before production.
