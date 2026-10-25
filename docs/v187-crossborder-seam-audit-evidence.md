# V187 — cross-provider SOURCE seam and overlap audit (NOT GAME ART)

**2026-10-25.** Isolated branch `terrain-v187-crossborder-seam-audit-20261025`. Main/live, V94 campaign/saves, V121 Matrei painting, and immutable V123 road graph untouched.

## Evidence inspected before implementation

Read issue #9 through V186, V186 successful [Actions run 40202212082](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40202212082), downloaded and opened the actual V186 10-tile candidate image, the authentic V184 60-tile modern mosaic, and the rejected [V171 WebKit phone screenshots](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40142947845/artifacts/12578863866) including whole crossing, Western Pass landscape and Southern Valley portrait. The GAME remains visibly rejected: a small photographic Matrei island, synthetic West/South forest, abrupt terrain contrast, and unknown road termini.

## Implemented

- [V187 seam/overlap auditor](../scripts/v187_crossborder_seam_audit.py) verifies original V184 native JPEGs and V186 candidate/Italian JPEGs and transparent overlay **before** measurement. It never composites pixels or changes terrain.
- Measures 4-neighbor candidate-to-observed Austrian boundary differences at native EPSG:3857 resolution, as well as same-pixel Austrian/South Tyrol two-provider overlap differences. Counts and mean/median/p90/max RGB differences are reproducible, with per-tile counts.
- [Six fail-closed tests](../scripts/test_v187_crossborder_seam_audit.py) cover exact roundtrip, high-contrast seam detection, forged approval/metrics and tampered Austrian/Italian imagery.
- [Dedicated CI](../.github/workflows/qa-v187-crossborder-seams.yml) runs V184 11 + V185 7 + V186 8 + V187 6 tests (**32**), verifies the real source artifacts (with re-acquisition fallback) and publishes a source-only JSON report.

## Verified CI and actual measured result

[GitHub Actions run 40206718020](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40206718020) **SUCCESS**. Downloaded and independently read the generated [artifact 12604125579](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40206718020/artifacts/12604125579).

- **3,544 candidate-to-observed source-edge neighbor pairs**: mean absolute RGB-channel difference **141.660**, median **151.333**, p90 **197.000**, max **243.333**.
- **459,721 same-pixel two-provider overlaps**: mean **22.952**, median **17.333**, p90 **44.333**, max **232.333**.
- All **138,560** V186 candidate pixels accounted for, unchanged and non-composited. Six tiles have candidate pixels and boundary pairs; the other four contribute overlap only.
- The unusually large candidate-edge difference is a **red flag for an abrupt source transition**; it may partly reflect near-white provider/no-data pixels immediately outside the heuristic mask. This metric does not prove a geographic mismatch or identify snow versus missing data. It is **not** a GAME visual quality score and does not justify blending, moving routes or fabricating terrain.

## Remaining blockers and next work

1. Independently classify the near-white Austrian boundary (provider coverage vs snow/cloud) using a geographic border dataset or documented source masks; do not automatically replace Austrian observed pixels or blend a bright border.
2. Review cross-provider overlap by geographic tile, period-exclude modern highways/rail and modern settlements; do not use unmodified 2023 imagery as 1780–1880 game art.
3. Geographically register actual three GAME octagon footprints and historically sourced road/bridge-bank controls before any V121/V123 changes. Rerun unchanged V140/V171 strict four-browser detail/route/seam/movement QA and obtain physical iPhone visual approval.

Every historic, road, bridge, game-art, phone and production approval remains **false**. No main merge, deployment, expense or irreversible action.
