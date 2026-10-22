#!/usr/bin/env python3
"""Produce unpainted, native-pixel evidence of Octagon 1's east art boundary.

The candidate endpoint [1100,704] is a coordinate on the boundary of a
1100-pixel-wide JPEG, not an image pixel or a verified neighbor road.
This tool deliberately does NOT decide whether a road is painted or passable.
"""
import json
from pathlib import Path

from PIL import Image
if __package__:
    from .audit_octagon_1_source_art import SOURCE, OUT, extract, sample
else:
    from audit_octagon_1_source_art import SOURCE, OUT, extract, sample


def crop_native(image, point, radius=64):
    """Return a native-resolution RGB crop, padded where source pixels do not exist."""
    if radius < 1 or type(radius) is not int:
        raise ValueError("radius must be a positive integer")
    x, y = point
    if type(x) is not int or type(y) is not int:
        raise ValueError("pixel coordinates must be integers")
    box = (x - radius, y - radius, x + radius, y + radius)
    source_box = (max(0, box[0]), max(0, box[1]),
                  min(image.width, box[2]), min(image.height, box[3]))
    output = Image.new("RGB", (radius * 2, radius * 2), (45, 45, 45))
    if source_box[0] < source_box[2] and source_box[1] < source_box[3]:
        output.paste(image.crop(source_box),
                     (source_box[0] - box[0], source_box[1] - box[1]))
    return output, source_box


def boundary_status(image_size, candidate_endpoint):
    width, height = image_size
    x, y = candidate_endpoint
    if width <= 0 or height <= 0:
        raise ValueError("invalid image dimensions")
    on_east_boundary = x == width and 0 <= y < height
    inside_pixel = 0 <= x < width and 0 <= y < height
    return {
        "candidate_endpoint": [x, y],
        "source_size": [width, height],
        "endpoint_is_source_pixel": inside_pixel,
        "endpoint_on_east_image_boundary": on_east_boundary,
        "neighbor_art_verified": False,
        "road_surface_verified": False,
        "bridge_continuation_verified": False,
        "production_ready": False,
    }


def run(text, out=None):
    if out is None:
        out = OUT / "east-edge"
    out = Path(out)
    image, raw, route = extract(text)
    status = boundary_status(image.size, route[-1])
    if not status["endpoint_on_east_image_boundary"]:
        raise ValueError("Candidate endpoint no longer matches the source east boundary")
    out.mkdir(parents=True, exist_ok=True)
    frames = []
    # Samples are from the candidate polyline, but every crop contains only
    # source JPEG pixels, never the road overlay or army marker.
    for index, fraction in enumerate((0.65, 0.72, 0.79, 0.86, 0.93, 1.0)):
        point = sample(route, fraction)
        crop, bounds = crop_native(image, point)
        filename = f"source-only-east-{index:02d}.png"
        crop.save(out / filename)
        frames.append({"fraction": fraction, "point": point,
                       "source_bounds": list(bounds), "filename": filename,
                       "point_is_source_pixel": 0 <= point[0] < image.width and 0 <= point[1] < image.height})
    status["frames"] = frames
    status["source_jpeg_bytes"] = len(raw)
    status["review_status"] = "NEIGHBOR_ART_AND_PAINTED_ROAD_UNVERIFIED"
    (out / "edge-audit.json").write_text(json.dumps(status, indent=2) + "\n")
    return status


if __name__ == "__main__":
    result = run(SOURCE.read_text())
    print(result["review_status"], "frames:", len(result["frames"]))
