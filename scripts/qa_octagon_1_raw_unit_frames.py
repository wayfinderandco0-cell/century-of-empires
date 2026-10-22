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


def render_contact_sheet(source, routes, sampler, fractions=FRACTIONS, radius=92):
    """Render one unaltered-art crop per candidate route/sample position.

    `sampler` is injected so production can use the established raw-road
    arc-length sampler, while synthetic tests need no repository image.
    """
    if source.size != (WIDTH, HEIGHT) or radius < 16 or not routes:
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
            if not all(isinstance(v, (int, float)) and -1e6 < v < 1e6
                       for v in (x, y)):
                raise ValueError("Invalid sample coordinate")
            left, top = round(x) - radius, round(y) - radius
            box = (left, top, left + tile, top + tile)
            crop = source.crop(box).convert("RGB")
            ox, oy = col * tile, row * (tile + footer)
            sheet.paste(crop, (ox, oy))
            # A dot is the ONLY overlay: it represents a candidate army, not road paint.
            cx, cy = ox + radius, oy + radius
            draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6),
                         fill=(252, 220, 125), outline=(25, 30, 26), width=2)
            draw.text((ox + 5, oy + tile + 6),
                      f"{name[:18]} {fraction:.0%} ({x:.0f},{y:.0f})",
                      fill=(240, 230, 205))
            report.append({"segment": name, "fraction": fraction,
                           "source_xy": [round(x, 2), round(y, 2)],
                           "crop_xyxy": list(box),
                           "crop_fully_in_source": (left >= 0 and top >= 0
                               and box[2] <= WIDTH and box[3] <= HEIGHT)})
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
              "frames": frames}
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"frames": len(frames), "source_git_blob_sha": sha,
                      "production_ready": False}, indent=2))


if __name__ == "__main__":
    main()
