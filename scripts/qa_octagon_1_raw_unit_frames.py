#!/usr/bin/env python3
"""Inspect candidate army positions on the *unpainted* pinned Octagon 1 JPEG.

No road stroke is rendered. This is a visual QA aid, not road evidence or an
approval to enter a neighboring cell.
"""
import argparse
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw

WIDTH, HEIGHT = 1100, 842
FRACTIONS = (0.15, 0.50, 0.85)


def source_coverage(box, width=WIDTH, height=HEIGHT):
    """Fraction of crop pixels sourced from real art; padding is not evidence."""
    left, top, right, bottom = box
    if (any(type(v) not in (int, float) for v in box)
            or not (right > left and bottom > top)
            or width <= 0 or height <= 0):
        raise ValueError("Invalid crop or source dimensions")
    ix0, iy0 = max(0, left), max(0, top)
    ix1, iy1 = min(width, right), min(height, bottom)
    visible = max(0, ix1 - ix0) * max(0, iy1 - iy0)
    return visible / ((right - left) * (bottom - top))



def render_contact_sheet(source, routes, sampler, fractions=FRACTIONS, radius=92):
    """Render one unaltered-art crop per candidate route/sample position.

    `sampler` is injected so production can use the established raw-road
    arc-length sampler, while synthetic tests need no repository image.
    """
    if source.size != (WIDTH, HEIGHT) or type(radius) is not int or radius < 16 or not routes:
        raise ValueError("Invalid source dimensions, crop radius, or routes")
    if not fractions or any(type(f) not in (int, float) or not 0 <= f <= 1
                            for f in fractions):
        raise ValueError("Fractions must be finite values between 0 and 1")
    tile = radius * 2
    footer = 28
    sheet = Image.new("RGB", (tile * len(fractions),
                               (tile + footer) * len(routes)), (35, 38, 36))
    draw = ImageDraw.Draw(sheet)
    report = []
    for row, (name, path) in enumerate(routes.items()):
        positions = list(sampler(path))
        if len(positions) < 2:
            raise ValueError("A corridor needs at least two samples: " + name)
        for col, fraction in enumerate(fractions):
            sample = positions[round(fraction * (len(positions) - 1))]
            _, x, y, *_ = sample
            if not all(type(v) in (int, float) and -1e6 < v < 1e6
                       for v in (x, y)):
                raise ValueError("Invalid sample coordinate")
            left, top = round(x) - radius, round(y) - radius
            box = (left, top, left + tile, top + tile)
            coverage = source_coverage(box)
            crop = source.crop(box).convert("RGB")
            ox, oy = col * tile, row * (tile + footer)
            sheet.paste(crop, (ox, oy))
            if coverage < 1:
                # Pillow pads out-of-image crops; do not confuse padding with terrain.
                draw.rectangle((ox, oy, ox + tile - 1, oy + tile - 1),
                               outline=(255, 85, 85), width=3)
            # A dot is the ONLY in-art marker: it represents a candidate army, not road paint.
            cx, cy = ox + radius, oy + radius
            draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6),
                         fill=(252, 220, 125), outline=(25, 30, 26), width=2)
            label = f"{name[:18]} {fraction:.0%} ({x:.0f},{y:.0f})"
            if coverage < 1:
                label = f"PARTIAL {coverage:.0%} " + label
            draw.text((ox + 5, oy + tile + 6), label,
                      fill=(255, 120, 120) if coverage < 1 else (240, 230, 205))
            report.append({"segment": name, "fraction": fraction,
                           "source_xy": [round(x, 2), round(y, 2)],
                           "crop_xyxy": list(box),
                           "crop_fully_in_source": coverage == 1,
                           "source_pixel_coverage_fraction": round(coverage, 6),
                           "source_padding_present": coverage < 1,
                           "candidate_center_in_source": 0 <= x < WIDTH and 0 <= y < HEIGHT)
    return sheet, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path,
                        default=Path("terrain-grid/octagon-1-v119-source.jpg"))
    parser.add_argument("--editor", type=Path,
                        default=Path("octagon-1-road-authoring.html"))
    parser.add_argument("--output", type=Path,
                        default=Path("qa/octagon-1/raw-unit"))
    args = parser.parse_args()
    from qa_octagon_1_raw_road import extract, samples, verify_source_blob
    from qa_octagon_1_full_corridor import corridor_segments

    raw = args.image.read_bytes()
    sha = verify_source_blob(raw)
    text = args.editor.read_text(encoding="utf-8")
    routes = corridor_segments(*(extract(text, n) for n in
                                 ("APPROACH", "BASE_EAST", "SOUTH")))
    with Image.open(io.BytesIO(raw)) as source:
        sheet, frames = render_contact_sheet(source.convert("RGB"), routes, samples)
    args.output.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output / "army-on-raw-source.png")
    report = {"source_git_blob_sha": sha, "source_identity_verified": True,
              "source_image_modified": False, "candidate_army_only": True,
              "road_paint_added": False, "painted_road_verified": False,
              "historical_road_verified": False, "bridge_far_bank_verified": False,
              "neighbor_connection_verified": False, "production_ready": False,
              "sampling": "nearest established 16px arc-length sample",
              "partial_source_frame_count": sum(f["source_padding_present"] for f in frames),
              "unobservable_candidate_center_count": sum(not f["candidate_center_in_source"] for f in frames),
              "frames": frames}
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"frames": len(frames), "source_git_blob_sha": sha,
                      "partial_source_frame_count": report["partial_source_frame_count"],
                      "production_ready": False}, indent=2))


if __name__ == "__main__":
    main()
