#!/usr/bin/env python3
"""V166: validate the ENTIRE shared V123 octagon borders, not one road anchor.

V165 checks a single crossing on each border. Two individually perfect source
fits can agree at that point yet drift visibly apart at either end of the
512/1024px shared octagon edge. This additional fail-closed test samples the
whole physical border, and rejects candidate projections leaving the declared
source raster. It never supplies real landmarks or approves period game art.
"""
import argparse
import json
import math
from pathlib import Path

import v165_three_frame_registration as v165

# From the pinned V123 1536x1024 octagons with 256px corner cuts.
# Samples include both extreme shared-edge endpoints, midpoint, and the
# immutable V123 road-crossing anchor. Affine difference norm is convex along
# a segment, so testing both endpoints bounds intermediate drift.
SHARED_EDGES = (
    ("western_pass", "matrei", (1536, 256), (1536, 768), (1536, 478)),
    ("matrei", "southern_valley", (1792, 1024), (2816, 1024), (2002, 1024)),
)
MAX_BORDER_SOURCE_DRIFT_PX = 3.0


def require(ok, why):
    if not ok:
        raise ValueError(why)


def project(fit, point):
    a, b, tx, ty = fit
    x, y = point
    return (a * x - b * y + tx, b * x + a * y + ty)


def check_full_borders(report, frame):
    """Only operate on V165-validated three-corridor candidate transforms."""
    require(report["sharedSourceFrameCoherent"],
            "cannot validate complete borders without three coherent candidates")
    width, height = frame["width"], frame["height"]
    diagnostics = {}
    for left, right, first, last, crossing in SHARED_EDGES:
        left_fit = report["corridors"][left]["gameWorldToSourceSimilarity"]
        right_fit = report["corridors"][right]["gameWorldToSourceSimilarity"]
        midpoint = ((first[0] + last[0]) / 2, (first[1] + last[1]) / 2)
        samples = (first, crossing, midpoint, last)
        deltas = []
        for xy in samples:
            require(v165.inside_octagon((xy[0]-v165.ORIGINS[left][0],
                                         xy[1]-v165.ORIGINS[left][1])) and
                    v165.inside_octagon((xy[0]-v165.ORIGINS[right][0],
                                         xy[1]-v165.ORIGINS[right][1])),
                    f"{left}/{right}: sample outside shared V123 octagon border")
            source_left, source_right = project(left_fit, xy), project(right_fit, xy)
            for source in (source_left, source_right):
                require(0 <= source[0] < width and 0 <= source[1] < height,
                        f"{left}/{right}: projected border exits declared source frame")
            deltas.append(math.dist(source_left, source_right))
        worst = max(deltas)
        require(worst <= MAX_BORDER_SOURCE_DRIFT_PX,
                f"{left}/{right}: full-border source discontinuity {worst:.4f}px > 3px")
        diagnostics[f"{left}_to_{right}"] = {
            "worldEdgeEndpoints": [list(first), list(last)],
            "roadCrossingWorld": list(crossing),
            "sampleCount": len(samples),
            "sourceDriftAtEndpointsPx": [round(deltas[0], 5), round(deltas[-1], 5)],
            "sourceDriftAtRoadPx": round(deltas[1], 5),
            "maxSourceBorderDriftPx": round(worst, 5),
            "projectedEndpointsWithinSourceRaster": True,
        }
    return diagnostics


def audit(data):
    base = v165.audit(data)
    base["version"] = 166
    base["fullSharedBordersValidated"] = False
    base["fullBorderDiagnostics"] = {}
    if base["sharedSourceFrameCoherent"]:
        base["fullBorderDiagnostics"] = check_full_borders(base, data["sourceFrame"])
        base["fullSharedBordersValidated"] = True
    # A mathematically coherent projection is NOT proof of actual landmark
    # correspondence, a real road, historical bridge banks, or acceptable art.
    for field in ("gameRouteGeoregistered", "historicalRoadsVerified",
                  "bridgeBanksVerified", "periodArtComplete",
                  "threeOctagonsVisuallyApproved", "physicalIPhoneApproved",
                  "productionApproved"):
        require(base[field] is False, f"approval flag changed unexpectedly: {field}")
    base["note"] = ("Whole-edge candidate continuity is necessary, not proof "
                    "of real landmarks, historical roads, bridge banks, or art approval.")
    return base


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--allow-blocked", action="store_true")
    args = p.parse_args()
    result = audit(json.loads(args.evidence.read_text()))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"candidateFits": result["allThreeCandidateFitsValidated"],
                      "wholeBorders": result["fullSharedBordersValidated"],
                      "statuses": {k: v["status"] for k, v in result["corridors"].items()}},
                     indent=2))
    if not result["fullSharedBordersValidated"] and not args.allow_blocked:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
