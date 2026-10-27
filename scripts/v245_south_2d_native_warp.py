#!/usr/bin/env python3
"""V245: image-native SOUTH road/terrain registration with a 2D inverse warp.

Unlike V244's monotone-x-only transform, this handles the immutable SOUTH
north-edge entry (x=466). An independently traced source road is mandatory.
Moves EXISTING road pixels and adjacent terrain; NEVER paints a new road.
Necessary geometry checks only: no source geography, history or approval.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

from v243_road_conditioning import SIZE, load_routes

MAX_DISPLACEMENT = 155.0
MAX_LENGTH_RATIO = 1.22
MIN_JACOBIAN = 0.24
MIN_COVERAGE = 0.997
SIGMA = 130.0


def polyline(points, label):
    a = np.asarray(points, dtype=np.float64)
    if a.ndim != 2 or a.shape[1] != 2 or len(a) < 3:
        raise ValueError(label + ": at least three two-dimensional points required")
    if not np.isfinite(a).all() or np.any(a < 0) or np.any(a[:, 0] > SIZE[0]) or np.any(a[:, 1] > SIZE[1]):
        raise ValueError(label + ": nonfinite or out-of-bounds point")
    lengths = np.linalg.norm(np.diff(a, axis=0), axis=1)
    if np.any(lengths < 3):
        raise ValueError(label + ": duplicate or sub-3px segment")
    return a


def resample(points, step=2.0):
    p = np.asarray(points, dtype=np.float64)
    lengths = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    count = max(3, int(np.ceil(lengths[-1] / step)) + 1)
    t = np.linspace(0, lengths[-1], count)
    return np.column_stack((np.interp(t, lengths, p[:, 0]),
                            np.interp(t, lengths, p[:, 1]))), float(lengths[-1])


def register(image, source_trace, target_trace, sigma=SIGMA):
    """Return warped native RGB image and a strictly fail-closed report.

    Source and destination are arc-length paired. Each destination pixel
    samples from the source using nearest road arc-position displacement
    attenuated with distance from the destination route. No cloned pixels,
    tiling, painted line, altered V123 coordinates or inferred bridge banks.
    """
    if image.size != SIZE:
        raise ValueError("source must be native 1536x1024 pixels")
    src = polyline(source_trace, "independent source road")
    dst = polyline(target_trace, "immutable V123 road")
    src_length = float(np.linalg.norm(np.diff(src, axis=0), axis=1).sum())
    dst_length = float(np.linalg.norm(np.diff(dst, axis=0), axis=1).sum())
    ratio = src_length / dst_length
    if not (1 / MAX_LENGTH_RATIO <= ratio <= MAX_LENGTH_RATIO):
        raise ValueError(f"REJECT: physical road arc-length ratio {ratio:.3f}")
    dst_dense, _ = resample(dst)
    src_dense, _ = resample(src, step=src_length / (len(dst_dense) - 1))
    if len(src_dense) != len(dst_dense):
        # Same normalized arc fractions, regardless of image pixel scale.
        s = np.linspace(0, 1, len(src_dense))
        src_dense = np.column_stack((np.interp(np.linspace(0, 1, len(dst_dense)), s, src_dense[:, 0]),
                                     np.interp(np.linspace(0, 1, len(dst_dense)), s, src_dense[:, 1])))
    displacement = src_dense - dst_dense
    magnitude = float(np.linalg.norm(displacement, axis=1).max())
    if magnitude > MAX_DISPLACEMENT:
        raise ValueError(f"REJECT: landscape displacement {magnitude:.2f}px")
    # Each route pixel stores a displacement to the independently visible
    # source cartway; EDT supplies nearest road arc position for all pixels.
    road = np.zeros((SIZE[1], SIZE[0]), dtype=bool)
    field_x = np.zeros(road.shape, dtype=np.float32)
    field_y = np.zeros(road.shape, dtype=np.float32)
    count = np.zeros(road.shape, dtype=np.float32)
    ix = np.clip(np.rint(dst_dense[:, 0]).astype(int), 0, SIZE[0] - 1)
    iy = np.clip(np.rint(dst_dense[:, 1]).astype(int), 0, SIZE[1] - 1)
    road[iy, ix] = True
    np.add.at(field_x, (iy, ix), displacement[:, 0])
    np.add.at(field_y, (iy, ix), displacement[:, 1])
    np.add.at(count, (iy, ix), 1)
    field_x[road] /= count[road]
    field_y[road] /= count[road]
    distance, nearest = distance_transform_edt(~road, return_indices=True)
    falloff = np.exp(-0.5 * (distance / sigma)**2).astype(np.float32)
    h, w = road.shape
    yy, xx = np.indices((h, w), dtype=np.float32)
    map_x = xx + field_x[tuple(nearest)] * falloff
    map_y = yy + field_y[tuple(nearest)] * falloff
    # Explicit Jacobian check rejects folded/overstretched terrain even when
    # the image appears superficially photographic.
    dx_dx = np.gradient(map_x, axis=1)
    dx_dy = np.gradient(map_x, axis=0)
    dy_dx = np.gradient(map_y, axis=1)
    dy_dy = np.gradient(map_y, axis=0)
    jacobian = dx_dx * dy_dy - dx_dy * dy_dx
    near = distance <= sigma * 2
    min_jac = float(np.min(jacobian[near]))
    if min_jac < MIN_JACOBIAN:
        raise ValueError(f"REJECT: landscape fold/stretch Jacobian {min_jac:.3f}")
    observed = (map_x >= 0) & (map_x <= w - 1) & (map_y >= 0) & (map_y <= h - 1)
    coverage = float(np.mean(observed))
    if coverage < MIN_COVERAGE:
        raise ValueError(f"REJECT: missing original pixels {coverage:.5f}")
    rgb = np.asarray(image.convert("RGB"))
    warped = cv2.remap(rgb, map_x, map_y, cv2.INTER_CUBIC,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return Image.fromarray(warped), {
        "sourceRoadLengthPx": round(src_length, 2),
        "v123RoadLengthPx": round(dst_length, 2),
        "arcLengthRatio": round(ratio, 4),
        "maximumDisplacementPx": round(magnitude, 2),
        "minimumJacobian": round(min_jac, 4),
        "originalPixelCoverage": round(coverage, 5),
        "southNorthEdgeSupported": bool(dst[0, 1] == 0 and dst[0, 0] == 466),
        "independentVisibleRoadReview": False,
        "sourceLicenseVerified": False,
        "sourceRegisteredToV123": False,
        "historicalRoadsVerified": False,
        "bridgeBanksVerified": False,
        "v203VisualPass": False,
        "fourBrowserPass": False,
        "humanVisualApproval": False,
        "productionApproved": False,
        "promotionEligible": False,
    }


def diagnostic(image, route):
    out = image.convert("RGBA")
    over = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(over)
    draw.line([tuple(p) for p in route], fill=(250, 55, 55, 205), width=3)
    for x, y in (route[0], route[-1]):
        draw.ellipse((x-7, y-7, x+7, y+7), outline=(255, 240, 20, 255), width=3)
    return Image.alpha_composite(out, over).convert("RGB")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--atlas", type=Path, default=Path("terrain-grid/v123-atlas.js"))
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    manifest = json.loads(args.manifest.read_text())
    raw = args.source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest.get("sourceSha256"):
        raise ValueError("source SHA256 mismatch")
    if manifest.get("annotationMethod") != "independent-human-visible-road-trace":
        raise ValueError("independent human road annotation required")
    if manifest.get("sourceRoadContinuesBeyondSurvey") is not False:
        raise ValueError("visible road beyond V123 survey limit not ruled out")
    _, routes = load_routes(args.atlas)
    target = routes["south"]
    warped, report = register(Image.open(args.source).convert("RGB"),
                              manifest["visibleRoadPoints"], target)
    args.out.mkdir(parents=True, exist_ok=True)
    warped.save(args.out / "south-2d-warp-UNAPPROVED.png")
    diagnostic(warped, target).save(args.out / "south-2d-warp-review.jpg", quality=91)
    report.update({"sourceSha256": manifest["sourceSha256"],
                   "sourceAttribution": manifest.get("sourceAttribution"),
                   "sourceRoadBeyondSurveyIndependentlyVerified": False,
                   "kind": "ISOLATED_ART_RESEARCH_NOT_GAME_ART"})
    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
