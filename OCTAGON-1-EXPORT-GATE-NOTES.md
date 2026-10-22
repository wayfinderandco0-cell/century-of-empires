# Octagon 1 export evidence gate — October 22, 2026

Branch: `octagon-1-export-evidence-gate-20261022`, based on `octagon-1-fork-bank-route`.

- Added `terrain-grid/octagon-1-east-candidate.json` preserving the unverified crossing status.
- Added `scripts/octagon_1_corridor_gate.js` to reject malformed seam, missing neighbor, unreviewed route/terrain/neighbor evidence, and unknown river crossing. Editor candidate exports are always nontraversable, even if an edge declaration is marked verified.
- Added `scripts/test_octagon_1_corridor_gate.cjs` with seven assertions and a dedicated Node 22 GitHub Actions workflow.
- Verified CI success: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/39804604711
- Independent JS evaluation: eight checks passed.
- Issue #9 comment attempt rejected by connector safety checks.

## Remaining blocker

This gate is standalone, not wired into `octagon-1-road-authoring.html`. The editor file is approximately 806 KB because it embeds the source JPEG; an attempt to update it through the connector was blocked. The existing route export still says `approvedForProduction:false`, but does not yet attach evidence-gate reasons.

No historical road, bridge exit, east neighbor, or painted-road alignment is certified. The underlying artwork and live game were not changed.

## Next action

Integrate the gate into the editor's `Copy route JSON` handler, or refactor the embedded JPEG into a separate source asset on an isolated branch to make small code updates practical. Browser-test exported candidate in Chromium and WebKit; never enable cross-cell movement without independently reviewed source art and terrain evidence.
