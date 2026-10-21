#!/usr/bin/env python3
"""Generate a geographically registered octagon index over the V94 Europe atlas.

The octagons are logical gameplay/LOD cells. The underlying continuous V94
raster remains visible in corner gaps; no geographical holes are introduced.
This generator DOES NOT produce finished close-up artwork or certify routes.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "terrain-v94" / "manifest.json"
DEFAULT_OUT = ROOT / "terrain-grid" / "octagon-index-v116.json"
CUT = 1 / (2 + math.sqrt(2))  # Regular octagon in a square cell.
ALLOWED_KINDS = {"background", "scenic", "route", "strategic"}


def make_index(manifest, annotations=None, cols=24, rows=18):
    if manifest.get("projection") != "equirectangular":
        raise ValueError("Expected V94 equirectangular projection")
    extent = manifest.get("extent")
    game_size = manifest.get("gameSize")
    if (not isinstance(extent, (list, tuple)) or len(extent) != 4 or
            any(type(v) not in (int, float) or not math.isfinite(v) for v in extent)):
        raise ValueError("extent must contain four finite numeric coordinates")
    if (not isinstance(game_size, (list, tuple)) or len(game_size) != 2 or
            any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in game_size)):
        raise ValueError("gameSize must contain two positive finite numeric dimensions")
    west, south, east, north = extent
    width, height = game_size
    if west >= east or south >= north:
        raise ValueError("extent must have increasing west/east and south/north bounds")
    if (type(cols) is not int or type(rows) is not int or
            cols < 1 or rows < 1 or cols * rows > 5000):
        raise ValueError("Invalid requested grid dimensions")
    dx, dy = width / cols, height / rows
    if not math.isclose(dx, dy, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("Octagons need square map-pixel footprints for regular edges")
    annotated = (annotations or {}).get("cells", {})
    if not isinstance(annotated, dict):
        raise ValueError("Annotations 'cells' must be a dictionary")
    known = {f"r{r:02d}-c{c:02d}" for r in range(rows) for c in range(cols)}
    unknown = set(annotated) - known
    if unknown:
        raise ValueError(f"Unknown cell IDs: {sorted(unknown)[:5]}")
    atlas_source = manifest.get("overview")
    if not atlas_source:
        raise ValueError("V94 overview image is missing from manifest")

    def ll(x, y):
        return [round(west + (east - west) * x / width, 6),
                round(north - (north - south) * y / height, 6)]

    cells = []
    for r in range(rows):
        for c in range(cols):
            identifier = f"r{r:02d}-c{c:02d}"
            x0, y0 = c * dx, r * dy
            x1, y1 = x0 + dx, y0 + dy
            cut = dx * CUT
            xy = [(x0 + cut, y0), (x1 - cut, y0),
                  (x1, y0 + cut), (x1, y1 - cut),
                  (x1 - cut, y1), (x0 + cut, y1),
                  (x0, y1 - cut), (x0, y0 + cut)]
            data = annotated.get(identifier, {})
            kind = data.get("kind", "background")
            if kind not in ALLOWED_KINDS:
                raise ValueError(f"{identifier}: invalid kind {kind}")
            evidence = data.get("evidence", [])
            if not isinstance(evidence, list) or not all(isinstance(item, str) and item.strip() for item in evidence):
                raise ValueError(f"{identifier}: evidence must be nonempty source strings")
            # Require an explicitly backed, connected gameplay feature.
            has_access = bool(data.get("verifiedAccessibleRoute") or
                              data.get("verifiedAccessibleObjective") or
                              data.get("verifiedArmyActivity"))
            deep = bool(evidence and has_access and kind in {"route", "strategic"})
            if has_access and not deep:
                raise ValueError(f"{identifier}: accessible cells require evidence and route/strategic classification")
            if kind == "background" and data.get("conquerable"):
                raise ValueError(f"{identifier}: background cannot be a conquest objective")
            if kind == "scenic" and data.get("conquerable"):
                raise ValueError(f"{identifier}: scenic villages cannot be conquered")
            if data.get("conquerable") and kind != "strategic":
                raise ValueError(f"{identifier}: conquest requires strategic classification")
            if kind == "route" and data.get("conquerable"):
                raise ValueError(f"{identifier}: road-only cells cannot be conquest targets")
            if kind == "strategic" and data.get("conquerable") and not data.get("verifiedAccessibleObjective"):
                raise ValueError(f"{identifier}: conquest requires verified accessible objective")
            cells.append({
                "id": identifier, "row": r, "col": c,
                "atlasRectPx": [round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)],
                "octagonWorldPx": [[round(x, 4), round(y, 4)] for x, y in xy],
                "octagonLonLat": [ll(x, y) for x, y in xy],
                "kind": kind,
                "deepZoomEligible": deep,
                "conquerable": bool(data.get("conquerable", False)),
                "evidence": evidence
            })
    return {
        "version": 116,
        "type": "logical_octagon_gameplay_index",
        "source": "terrain-v94/manifest.json",
        "atlasOverview": atlas_source,
        "atlasTiles": manifest.get("tileTemplate"),
        "extentLonLat": [west, south, east, north],
        "gameSize": [width, height],
        "grid": {"columns": cols, "rows": rows, "cells": len(cells)},
        "renderer": "Continuous geographical atlas behind octagon gameplay/LOD overlay. Draw the source map in all square/octagon corner gaps; never expose blank cells.",
        "detailPolicy": "No deep zoom unless a verified playable route, accessible objective, or legitimate army activity exists, backed by evidence. Background mountains and scenic villages stay overview-only.",
        "counts": {
            "planned": len(cells),
            "deepZoomEligible": sum(x["deepZoomEligible"] for x in cells),
            "conquerable": sum(x["conquerable"] for x in cells),
            "closeUpArtworkGenerated": 0
        },
        "cells": cells
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--annotations", type=Path, help="Explicit validated route/settlement evidence, not inferred roads")
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()
    raw = args.manifest.read_bytes()
    manifest = json.loads(raw)
    annotations = json.loads(args.annotations.read_text()) if args.annotations else None
    payload = make_index(manifest, annotations)
    payload["sourceManifestSHA256"] = hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    print("indexed", payload["counts"]["planned"], "octagons;",
          payload["counts"]["deepZoomEligible"], "verified for close zoom;",
          payload["counts"]["closeUpArtworkGenerated"], "close-up artwork images generated")


if __name__ == "__main__":
    main()
