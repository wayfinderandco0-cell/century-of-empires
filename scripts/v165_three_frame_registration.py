#!/usr/bin/env python3
"""V165: keep all three V123 corridor landmark fits in ONE honest world frame.

V163 checked three independent mathematical fits, but its 0..4608 x 0..1024
study rectangle did not represent the V123 L-shaped West/Matrei/South atlas.
That could allow three sets of "Matrei" points to masquerade as three tiles,
or three mutually incompatible transforms to pass separately.

No control points are supplied or inferred here. A candidate fit is NEVER
proof of geography, historical roads, bridge banks, artwork or release.
"""
import argparse
import copy
import json
import math
from pathlib import Path
import v163_landmark_registration as legacy

# Pinned to terrain-grid/v123-atlas.js; local octagons are 1536x1024,
# 256px corner cuts. South is BELOW Matrei, not to its right.
ORIGINS = {
    "western_pass": (0, 0),
    "matrei": (1536, 0),
    "southern_valley": (1536, 1024),
}
SIZE = (1536, 1024)
CORNER = 256
SEAMS = (
    ("western_pass", "matrei", (1536, 478)),
    ("matrei", "southern_valley", (2002, 1024)),
)
MAX_SEAM_SOURCE_PX = 3.0
MAX_RELATIVE_SCALE_DRIFT = 0.02
MAX_ANGLE_DRIFT_DEGREES = 2.0


def require(ok, why):
    if not ok:
        raise ValueError(why)


def inside_octagon(local):
    x, y = local
    w, h = SIZE
    return (0 <= x <= w and 0 <= y <= h and
            x+y >= CORNER and (w-x)+y >= CORNER and
            x+(h-y) >= CORNER and (w-x)+(h-y) >= CORNER)


def world_transform(local_fit, origin):
    a, b, tx, ty = local_fit
    ox, oy = origin
    return (a, b, tx-a*ox+b*oy, ty-b*ox-a*oy)


def check_coherence(fits):
    errors = {}
    for left, right, anchor in SEAMS:
        a, b = fits[left], fits[right]
        scale_a, scale_b = math.hypot(*a[:2]), math.hypot(*b[:2])
        scale_drift = abs(scale_a/scale_b-1)
        angle = abs(math.degrees(math.atan2(a[1]*b[0]-a[0]*b[1],
                                                a[0]*b[0]+a[1]*b[1])))
        seam_delta = math.dist(legacy.project(a, anchor),
                               legacy.project(b, anchor))
        require(scale_drift <= MAX_RELATIVE_SCALE_DRIFT,
                f"{left}/{right}: source scale discontinuity")
        require(angle <= MAX_ANGLE_DRIFT_DEGREES,
                f"{left}/{right}: source rotation discontinuity")
        require(seam_delta <= MAX_SEAM_SOURCE_PX,
                f"{left}/{right}: source coordinate seam discontinuity")
        errors[f"{left}_to_{right}"] = {
            "sourceSeamDeltaPx": round(seam_delta, 5),
            "relativeScaleDrift": round(scale_drift, 7),
            "rotationDriftDegrees": round(angle, 6),
        }
    return errors


def audit(data):
    # Reuse the strict V163 manifest/source-frame checks, without asking
    # V163 to interpret the incorrect whole-world 4608x1024 rectangle.
    blank = copy.deepcopy(data)
    if isinstance(blank, dict) and isinstance(blank.get("corridors"), dict):
        blank["corridors"] = {k: [] for k in blank["corridors"]}
    legacy.audit(blank)
    findings, fits = {}, {}
    used_ids, used_source_pixels = set(), set()
    for corridor, origin in ORIGINS.items():
        rows = data["corridors"][corridor]
        require(isinstance(rows, list), f"{corridor}: evidence must be a list")
        local_rows = copy.deepcopy(rows)
        for row in local_rows:
            require(isinstance(row, dict), f"{corridor}: malformed evidence")
            x, y = legacy.point(row.get("game"), f"{corridor} game")
            local = (x-origin[0], y-origin[1])
            require(inside_octagon(local),
                    f"{corridor}: landmark outside its V123 octagon footprint")
            row["game"] = list(local)
            ident = row.get("id")
            require(ident not in used_ids,
                    f"{corridor}: reused landmark ID across corridors")
            used_ids.add(ident)
            source = legacy.point(row.get("source"), f"{corridor} source")
            require(source not in used_source_pixels,
                    f"{corridor}: reused source pixel across corridors")
            used_source_pixels.add(source)
        item = legacy.validate_corridor(corridor, local_rows,
                                        data["sourceFrame"])
        if item["candidateTransformValidated"]:
            local_fit = item.pop("gameToSourceSimilarity")
            fit = world_transform(local_fit, origin)
            fits[corridor] = fit
            item["gameWorldToSourceSimilarity"] = [round(v, 9) for v in fit]
        findings[corridor] = item
    all_present = len(fits) == len(ORIGINS)
    coherence = check_coherence(fits) if all_present else {}
    return {
        "version": 165,
        "v123AtlasLayout": "west=(0,0); matrei=(1536,0); south=(1536,1024)",
        "corridors": findings,
        "allThreeCandidateFitsValidated": all_present,
        "sharedSourceFrameCoherent": all_present and len(coherence) == 2,
        "seamDiagnostics": coherence,
        "gameRouteGeoregistered": False,
        "historicalRoadsVerified": False,
        "bridgeBanksVerified": False,
        "periodArtComplete": False,
        "threeOctagonsVisuallyApproved": False,
        "physicalIPhoneApproved": False,
        "productionApproved": False,
        "note": "Mathematical frame consistency is necessary, not geographic evidence or art approval."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--evidence", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--allow-blocked", action="store_true")
    args = p.parse_args()
    report = audit(json.loads(args.evidence.read_text()))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"candidateFits": report["allThreeCandidateFitsValidated"],
                      "sharedFrame": report["sharedSourceFrameCoherent"],
                      "statuses": {k: v["status"] for k,v in report["corridors"].items()}}, indent=2))
    if not report["sharedSourceFrameCoherent"] and not args.allow_blocked:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
