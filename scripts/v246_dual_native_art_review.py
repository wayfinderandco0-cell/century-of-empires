#!/usr/bin/env python3
"""V246: inspect BOTH physical road materials against immutable V123 before game import.

No road is drawn. Reuse V245 whole-landscape 2D registration and V240's
original-pixel road evidence. Explicitly measure FULL visible-road overrun,
which a Boolean source manifest could previously conceal. This is a necessary
image/art review tool, not source-to-geography registration or game approval.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw
from v240_cartway_trace_registration import earth_evidence
from v243_road_conditioning import load_routes
from v245_south_2d_native_warp import polyline, register, diagnostic

MAX_UNSUPPORTED_ROAD_PX = 50.0
SOURCE_METHOD = "independent-human-visible-road-trace"
SYNTHETIC_METHOD = "synthetic-test-annotation"


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def path_length(points):
    return sum(distance(a, b) for a, b in zip(points, points[1:]))


def validate_annotation(manifest, source_bytes, *, allow_synthetic=False):
    if hashlib.sha256(source_bytes).hexdigest() != manifest.get("sourceSha256"):
        raise ValueError("source SHA256 mismatch")
    method = manifest.get("annotationMethod")
    if method != SOURCE_METHOD and not (allow_synthetic and method == SYNTHETIC_METHOD):
        raise ValueError("independently traced original-pixel road required")
    for key in ("sourceAttribution", "sourceDescription"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise ValueError("missing source provenance: " + key)
    full = polyline(manifest.get("fullVisibleRoadPoints"), "entire visible road")
    start = manifest.get("playableStartIndex")
    end = manifest.get("playableEndIndex")
    if not isinstance(start, int) or not isinstance(end, int) or not (0 <= start < end < len(full)):
        raise ValueError("invalid source-road survey indices")
    selected = full[start:end + 1]
    before = path_length(full[:start + 1])
    after = path_length(full[end:])
    overrun = max(before, after)
    if overrun > MAX_UNSUPPORTED_ROAD_PX:
        raise ValueError(
            f"visible road beyond immutable survey limit: {overrun:.1f}px "
            f"(before={before:.1f}px, after={after:.1f}px)"
        )
    return selected.tolist(), {
        "extraRoadBeforeSurveyPx": round(before, 2),
        "extraRoadAfterSurveyPx": round(after, 2),
        "maximumExtraRoadPx": round(overrun, 2),
        "wholeRoadTraceCompletenessIndependentlyVerified": False,
        "annotationIndependentVerified": False,
    }


def source_overlay(image, manifest, route):
    review = image.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    full = manifest.get("fullVisibleRoadPoints", [])
    if len(full) >= 2:
        d.line([tuple(p) for p in full], fill=(30, 235, 235, 210), width=4)
    d.line([tuple(p) for p in route], fill=(250, 60, 55, 210), width=4)
    return Image.alpha_composite(review, overlay).convert("RGB")


def audit_pair(atlas, sources, manifests, out, *, allow_synthetic=False):
    """Return fail-closed report; output pixels only for geometrically safe tiles."""
    _, routes = load_routes(atlas)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "version": 246,
        "kind": "ISOLATED_PHYSICAL_CARTWAY_PAIR_REVIEW_NOT_GAME_ART",
        "sourceRegisteredToV123": False,
        "historicalRoadsVerified": False,
        "bridgeBanksVerified": False,
        "sourceLicenseVerified": False,
        "independentRoadAnnotationApproved": False,
        "v203VisualPass": False,
        "fourBrowserPass": False,
        "humanVisualApproval": False,
        "physicalIPhoneApproved": False,
        "productionApproved": False,
        "promotionEligible": False,
        "tiles": {},
    }
    hashes = [hashlib.sha256(Path(sources[t]).read_bytes()).hexdigest()
              for t in ("west", "south")]
    if hashes[0] == hashes[1]:
        raise ValueError("WEST and SOUTH cannot reuse identical source pixels")
    for tile in ("west", "south"):
        target = list(reversed(routes[tile])) if tile == "west" else routes[tile]
        image_path = Path(sources[tile])
        raw = image_path.read_bytes()
        manifest = manifests[tile]
        result = {"status": "REJECTED", "reason": "unverified"}
        try:
            image = Image.open(image_path).convert("RGB")
            if image.size != (1536, 1024):
                raise ValueError("source must be 1536x1024 original pixels")
            source_overlay(image, manifest, target).save(
                out / f"{tile}-original-visible-road-v123.jpg", quality=90)
            selected, overrun = validate_annotation(
                manifest, raw, allow_synthetic=allow_synthetic)
            native = earth_evidence(image, selected)
            if not native["visibleEarthPass"]:
                raise ValueError("original pixels do not show a continuous earth cartway")
            warped, warp = register(image, selected, target)
            after = earth_evidence(warped, target)
            warped.save(out / f"{tile}-native-warp-UNAPPROVED.png")
            diagnostic(warped, target).save(
                out / f"{tile}-v123-overlay-UNAPPROVED.jpg", quality=90)
            if not after["visibleEarthPass"]:
                raise ValueError("relocated original pixels do not follow V123 cartway")
            result = {"status": "NECESSARY_GEOMETRY_ONLY_PASS",
                      "originalRoadEvidence": native,
                      "warpedRoadEvidence": after,
                      "roadSurvey": overrun, "warp": warp,
                      "sourceSha256": hashes[0 if tile == "west" else 1],
                      "artApproved": False}
        except (ValueError, OSError, KeyError, TypeError) as exc:
            result = {"status": "REJECTED", "reason": str(exc),
                      "sourceSha256": hashes[0 if tile == "west" else 1]}
        report["tiles"][tile] = result
    report["bothNecessaryGeometryPassed"] = all(
        r["status"] == "NECESSARY_GEOMETRY_ONLY_PASS"
        for r in report["tiles"].values())
    report["candidateMayEnterSeparateBrowserReview"] = (
        report["bothNecessaryGeometryPassed"] and not allow_synthetic)
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--west", type=Path, required=True)
    p.add_argument("--south", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--atlas", type=Path, default=Path("terrain-grid/v123-atlas.js"))
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    manifests = json.loads(a.manifest.read_text())
    result = audit_pair(a.atlas, {"west": a.west, "south": a.south},
                        manifests, a.out)
    print(json.dumps(result, indent=2), flush=True)
    if not result["bothNecessaryGeometryPassed"]:
        raise SystemExit("ART RED: at least one source has no verified physical V123 cartway")


if __name__ == "__main__":
    main()
