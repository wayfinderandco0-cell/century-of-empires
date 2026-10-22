#!/usr/bin/env python3
"""Inspect all Octagon 1 route candidates against the original, pinned source JPEG.

Contrast is diagnostic only; no historical road or crossing is certified.
"""
import argparse
import io
import json
from pathlib import Path
from statistics import median

from PIL import Image

from qa_octagon_1_raw_road import SW, SH, extract, inspect, verify_source_blob
from qa_octagon_1_diagnostic_spans import low_contrast_runs

FORK_INDEX = 36


def corridor_segments(approach, east, south):
    """Partition original route arrays without dropping their shared approach."""
    if (len(approach) <= FORK_INDEX or len(south) <= FORK_INDEX
            or approach[:FORK_INDEX + 1] != south[:FORK_INDEX + 1]):
        raise ValueError("South branch disagrees with the full shared approach")
    if (approach[FORK_INDEX] != [437, 742] or approach[-1] != [699, 799]
            or not east or east[-1] != [1100, 704] or south[-1] != [315, 842]):
        raise ValueError("Candidate fork or endpoints changed: independent review required")
    routes = {
        "shared_north_to_fork": approach[:FORK_INDEX + 1],
        "fork_to_bridge_arrival": approach[FORK_INDEX:],
        "east_bank_candidate": [approach[-1]] + east,
        "south_branch_candidate": south[FORK_INDEX:],
    }
    if any(len(path) < 2 or any(a == b for a, b in zip(path, path[1:]))
           for path in routes.values()):
        raise ValueError("Missing or zero-length corridor segment")
    return routes


def build_report(editor_text, image_bytes):
    """Fail closed on source identity and geometry before sampling any image."""
    source_sha = verify_source_blob(image_bytes)
    paths = corridor_segments(*(extract(editor_text, name)
                                for name in ("APPROACH", "BASE_EAST", "SOUTH")))
    with Image.open(io.BytesIO(image_bytes)) as im:
        if im.size != (SW, SH):
            raise ValueError("Unexpected source image size")
        art = im.convert("RGB")
    report = {
        "source_git_blob_sha": source_sha,
        "source_identity_verified": True,
        "painted_road_verified": False,
        "historical_road_verified": False,
        "bridge_far_bank_verified": False,
        "neighbor_connection_verified": False,
        "production_ready": False,
        "method": "unaltered source JPEG cross-track contrast; no road classification",
        "segments": {},
    }
    for name, path in paths.items():
        rows = inspect(art, path)
        values = [r["raw_cross_track_contrast"] for r in rows
                  if r["raw_cross_track_contrast"] is not None]
        report["segments"][name] = {
            "start": path[0], "end": path[-1], "vertices": len(path),
            "samples": len(rows), "valid_samples": len(values),
            "median_cross_track_contrast": round(median(values), 2) if values else None,
            "out_of_bounds_samples": len(rows) - len(values),
            "low_contrast_threshold": 18,
            "low_contrast_runs": low_contrast_runs(rows),
            "warning": "Contrast does not establish a painted or historical road.",
        }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path,
                        default=Path("terrain-grid/octagon-1-v119-source.jpg"))
    parser.add_argument("--editor", type=Path,
                        default=Path("octagon-1-road-authoring.html"))
    parser.add_argument("--output", type=Path,
                        default=Path("qa/octagon-1/full-corridor-report.json"))
    args = parser.parse_args()
    report = build_report(args.editor.read_text(encoding="utf-8"),
                          args.image.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
