# V244 — native road landscape remap study (2026-10-27)

**STATUS: ART RED, production RED, not playable or approved.** This is a new isolated method that remaps **existing** image roadbed pixels and their surrounding photographic terrain together. It does **not** paint a road stripe over grass. The original V123 graph is read from the pinned source and is never modified.

## Evidence inspected before coding

- GitHub issue #9 through V243, current branches, recent Actions and the V243 actual SOUTH/WEST conditioning guide PNGs from CI artifact 12751825021. The guides are geometry constraints, not art.
- Actual V242 WebKit portrait screenshot from CI artifact 12748747360: Matrei detailed; WEST/SOUTH imported photographic sources still have pasted flat cartways across canopies.
- Actual V240 unpainted WEST source-road screenshot: immutable V123 path is not an existing physical road.
- No independently surveyed V209 tiepoints, historic 1780 cartway proof, or independently verified bridge banks.

## New isolated code

- scripts/v244_native_road_warp.py transforms an existing 1536×1024 source **with** a human-annotated visible cartway using a smooth, monotone whole-landscape pixel remap. It refuses severe displacement (>165px), folds, insufficient source coverage, malformed source-road annotations, wrong source SHA256, and changes to the pinned V123 blob. It reports visible road continuation past the V123 survey limit. It never sets production approval.
- scripts/test_v244_native_road_warp.py tests real native road pixel relocation (not painting), negative controls, and the unregistered SOUTH vertical approach.
- .github/workflows/qa-v244-native-road-warp.yml runs tests and inherited immutable V123 guards, and intentionally keeps production RED.

## Real visual experiment (not committed as accepted game art)

A **new fictional AI-generated image** was inspected and processed locally (not a historic photograph, not a verified Austrian source, no independently verified license/provenance). Image SHA256: 1b0a21aa77f0aac3476093b9a0805dd227211d19246d6e27d3b4652ae362012f. An independent visible-road annotation was made by examining its actual road, **not copied from V123**. The transform moves the original two-rut road and surrounding terrain, avoiding V238/V241's pasted stripe. WEST measured maximum displacement **137.64px**, minimum monotonic image gradient **0.4243**, and observed pixel coverage **0.99902** (with 145px falloff). A rendered red V123 overlay was visually inspected. The scene is more natural than V241's drawn ruts but **fails** because the visible road continues **275px beyond the V123 survey endpoint** and there is a small invalid border; source and game geography remain unregistered. Not suitable for production or gameplay promotion.

SOUTH is **blocked by this particular method**: the immutable V123 route begins with a vertical north entry at x=466 (two equal-x points), which a strictly monotone-x road remap cannot represent. A separate experimental 2D thin-plate deformation of another fictional image was visually/quantitatively rejected (max displacement about 550px; 4.1% fold area; 97.8% observed coverage). Do not force a SOUTH image with a guessed road, modern bridge or unproven bank.

## What this does NOT establish

No historical route, geographic registration, source license acceptance, independent pixel-trace approval, bridge-bank verification, V203 pass, four-browser candidate gameplay pass, physical iPhone pass or human user visual approval. No existing files, Matrei, army sprites, V94 campaign, saves or immutable V121/V123 road/bridge graph changed.

**Next substantive art requirement:** Obtain a distinct, high-resolution SOUTH landscape with an actual physically integrated cartway that **enters from the north**, plus a WEST source whose road naturally terminates at the survey limit. Only then use the V242 import path for four-browser gameplay and strict V203 screenshot review. No more surface-painting or fake historical claims.
