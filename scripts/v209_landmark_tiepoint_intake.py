#!/usr/bin/env python3
"""V209: evidence-first V123 octagon -> V205 modern-source landmark intake.

No landmark coordinates are asserted in this repository. A candidate similarity
fit requires independent held-out points INSIDE the actual clipped octagon and
inside the corresponding native source panel. Even a candidate is NOT geographic,
historical, artwork, bridge-bank, or production approval.
"""
import argparse
import json
import math
from pathlib import Path
from urllib.parse import urlsplit

import v208_source_game_frame_audit as frames
import v204_contiguous_matrei_sources as source

ROOT = Path(__file__).resolve().parents[1]
CELLS = ("west", "matrei", "south")
ROLES = ("control", "holdout")
NATURAL_FEATURES = ("bedrock_outcrop", "ridge_saddle", "river_confluence", "valley_junction")
FALSE_FLAGS = (
    "sourceRegisteredToV123", "historicalRoadsVerified", "bridgeBanksVerified",
    "westSouthRoadsSurveyed", "periodSafe", "gameArtApproved",
    "physicalIPhoneApproved", "productionApproved",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def point(value, label):
    require(isinstance(value, list) and len(value) == 2
            and all(type(v) in (int, float) and math.isfinite(v) for v in value),
            label + ": expected two finite numbers")
    return tuple(value)


def inside_polygon(p, polygon):
    """Inclusive polygon containment, including genuine shared octagon edges."""
    x, y = p
    inside = False
    for i, a in enumerate(polygon):
        b = polygon[(i + 1) % len(polygon)]
        ax, ay = a
        bx, by = b
        cross = (x - ax) * (by - ay) - (y - ay) * (bx - ax)
        if abs(cross) < 1e-8 and min(ax, bx) <= x <= max(ax, bx) and min(ay, by) <= y <= max(ay, by):
            return True
        if (ay > y) != (by > y):
            crossing_x = ax + (y - ay) * (bx - ax) / (by - ay)
            if x < crossing_x:
                inside = not inside
    return inside


def evidence_url(url, label):
    require(isinstance(url, str), label + ": evidence URL required")
    u = urlsplit(url)
    require(u.scheme == "https" and bool(u.hostname)
            and u.hostname not in ("example.com", "example.org", "example.net", "localhost")
            and not u.username and not u.password, label + ": actual HTTPS evidence URL required")


def fit_two(a, b):
    x0, y0 = a["game"]
    x1, y1 = b["game"]
    u0, v0 = a["source"]
    u1, v1 = b["source"]
    dx, dy = x1 - x0, y1 - y0
    du, dv = u1 - u0, v1 - v0
    d = dx * dx + dy * dy
    require(d >= 60 ** 2 and du * du + dv * dv >= 20 ** 2,
            "control baseline too short for independent source comparison")
    aa = (dx * du + dy * dv) / d
    bb = (dx * dv - dy * du) / d
    return (aa, bb, u0 - aa * x0 + bb * y0, v0 - bb * x0 - aa * y0)


def transform(t, p):
    a, b, tx, ty = t
    return (a * p[0] - b * p[1] + tx, b * p[0] + a * p[1] + ty)


def audit(data):
    game = frames.audit()  # pins V121/V123 blobs and V94/V97/V102 projection identities
    require(game["sourceRegisteredToV123"] is False, "unexpected pre-approved V208 registration")
    require(isinstance(data, dict) and set(data) == {"schemaVersion", "sourceSite", "matches", "humanVisualApproval"},
            "invalid landmark intake schema")
    require(data["schemaVersion"] == 209 and data["sourceSite"] == "forest",
            "wrong version or independently unreviewed source site")
    require(data["humanVisualApproval"] is False, "cannot assert user visual approval")
    require(isinstance(data["matches"], dict) and set(data["matches"]) == set(CELLS),
            "exactly three V123 game cells required")
    modern = source.plan("forest")
    panels = {name: panel for name, panel in zip(CELLS, modern["panels"])}
    game_cells = {cell["gameCell"]: cell for cell in game["gameCells"]}
    findings = {}
    all_urls = set()
    all_ids = set()
    candidate_fits = {}

    for cell in CELLS:
        rows = data["matches"][cell]
        require(isinstance(rows, list), cell + ": landmarks must be an array")
        if not rows:
            findings[cell] = {"status": "BLOCKED_NO_INDEPENDENT_TIEPOINTS",
                              "candidateFit": False, "matchingLandmarks": 0}
            continue
        require(len(rows) == 4, cell + ": require two controls and TWO independent holdouts")
        parsed = []
        game_xy = set()
        source_xy = set()
        panel_x, panel_y = panels[cell]["pixelOriginInContact"]
        for row in rows:
            keys = {"id", "role", "feature", "gameWorldXY", "sourceContactXY",
                    "gameEvidenceUrl", "sourceEvidenceUrl", "reviewedBy"}
            require(isinstance(row, dict) and set(row) == keys, cell + ": malformed evidence fields")
            ident = row["id"]
            require(isinstance(ident, str) and len(ident.strip()) >= 5 and ident not in all_ids,
                    cell + ": invalid or repeated landmark ID")
            all_ids.add(ident)
            require(row["role"] in ROLES and row["feature"] in NATURAL_FEATURES,
                    cell + ": non-natural or invalid feature/role")
            g = point(row["gameWorldXY"], cell + " game")
            s = point(row["sourceContactXY"], cell + " modern source")
            require(inside_polygon(g, game_cells[cell]["gameOctagonPolygonWorldXY"]),
                    cell + ": game landmark outside clipped V123 octagon")
            require(panel_x <= s[0] < panel_x + 512 and panel_y <= s[1] < panel_y + 512,
                    cell + ": source landmark outside native panel")
            require(g not in game_xy and s not in source_xy, cell + ": duplicated point coordinates")
            game_xy.add(g)
            source_xy.add(s)
            for key in ("gameEvidenceUrl", "sourceEvidenceUrl"):
                url = row[key]
                evidence_url(url, cell + " " + key)
                require(url not in all_urls, cell + ": reused evidence URL")
                all_urls.add(url)
            require(isinstance(row["reviewedBy"], str) and len(row["reviewedBy"].strip()) >= 4,
                    cell + ": independent reviewer attribution required")
            parsed.append({"id": ident, "role": row["role"], "game": g, "source": s})
        controls = [r for r in parsed if r["role"] == "control"]
        holdouts = [r for r in parsed if r["role"] == "holdout"]
        require(len(controls) == 2 and len(holdouts) == 2,
                cell + ": require 2 controls and 2 unused holdouts")
        t = fit_two(*controls)
        baseline = math.dist(controls[0]["game"], controls[1]["game"])
        src_baseline = math.dist(controls[0]["source"], controls[1]["source"])
        errors = []
        for h in holdouts:
            require(min(math.dist(h["game"], c["game"]) for c in controls) >= 0.20 * baseline,
                    cell + ": holdout too close to a fitted control")
            area2 = abs((controls[1]["game"][0] - controls[0]["game"][0]) *
                        (h["game"][1] - controls[0]["game"][1]) -
                        (controls[1]["game"][1] - controls[0]["game"][1]) *
                        (h["game"][0] - controls[0]["game"][0]))
            require(area2 >= 0.05 * baseline * baseline,
                    cell + ": holdout too nearly collinear")
            error = math.dist(transform(t, h["game"]), h["source"])
            require(error / src_baseline <= 0.02,
                    cell + ": independent holdout residual exceeds 2%")
            errors.append(error)
        candidate_fits[cell] = t
        findings[cell] = {
            "status": "CANDIDATE_MATHEMATICAL_FIT_ONLY_NOT_GEOGRAPHICALLY_APPROVED",
            "candidateFit": True, "matchingLandmarks": 4,
            "controls": [c["id"] for c in controls],
            "independentHoldouts": [h["id"] for h in holdouts],
            "maxHoldoutResidualSourcePixels": round(max(errors), 5),
            "gameToModernSourceSimilarity": [round(x, 9) for x in t],
        }

    all_candidates = len(candidate_fits) == 3
    if all_candidates:
        # Each native panel belongs to one EPSG:3857 L-shaped source mosaic.
        # Three independent fits must also agree on one world->mosaic transform.
        reference = candidate_fits["matrei"]
        for cell in ("west", "south"):
            other = candidate_fits[cell]
            relative_scale = abs(math.hypot(other[0], other[1]) /
                                 math.hypot(reference[0], reference[1]) - 1)
            angle = abs(math.atan2(other[1], other[0]) -
                        math.atan2(reference[1], reference[0]))
            angle = min(angle, abs(angle - 2 * math.pi))
            require(relative_scale <= 0.02 and angle <= math.radians(2),
                    "three cells lack a coherent source/game scale or rotation")
            origin = game_cells[cell]["gameOrigin"]
            gap = math.dist(transform(reference, origin), transform(other, origin))
            require(gap <= 12, "three cell transforms disagree on shared world registration")
    return {
        "version": 209,
        "purpose": "Evidence intake and independent candidate fit; no gameplay/art changes",
        "sourceSite": "forest",
        "sourceProjection": "EPSG:3857",
        "sourcePanelLayout": "native contiguous 512px L; NOT V123 game geography",
        "gameGeometryPinnedTo": game["gameGeometryPinnedTo"],
        "findings": findings,
        "allThreeCandidateFits": all_candidates,
        "registrationStatus": ("MATHEMATICAL_CANDIDATE_ONLY_NOT_APPROVED"
                               if all_candidates else "BLOCKED_MISSING_REAL_TIEPOINTS"),
        "historicalPeriod": "1780–1880 NOT verified by modern source",
        "sourceLicense": "Datenquelle: basemap.at (CC BY 4.0)",
        **{flag: False for flag in FALSE_FLAGS},
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--evidence", type=Path, default=ROOT / "terrain-grid/v209-unverified-tiepoints.json")
    p.add_argument("--report", type=Path, default=ROOT / "qa/v209-landmark-intake/report.json")
    p.add_argument("--require-registered", action="store_true")
    args = p.parse_args()
    result = audit(json.loads(args.evidence.read_text()))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"registrationStatus": result["registrationStatus"],
                      "allThreeCandidateFits": result["allThreeCandidateFits"]}, indent=2))
    if args.require_registered:
        raise SystemExit(2)  # Candidate fit can NEVER self-authorize geographic approval.


if __name__ == "__main__":
    main()
