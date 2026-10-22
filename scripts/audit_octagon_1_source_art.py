#!/usr/bin/env python3
"""Extract raw JPEG samples, never treating route overlay as evidence of a road."""
import base64
import hashlib
import io
import json
import math
import re
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "octagon-1-road-authoring.html"
OUT = ROOT / "qa" / "octagon-1-raw-art"


def extract(text):
    def points(name):
        m = re.search(r"const " + name + r"=(\[\[[^\n;]+\]\]);", text)
        if not m:
            raise ValueError("Missing source points: " + name)
        return json.loads(m.group(1))
    m = re.search(r'const IMAGE="data:image/jpeg;base64,([A-Za-z0-9+/=]+)"', text)
    if not m:
        raise ValueError("Missing original JPEG")
    raw = base64.b64decode(m.group(1), validate=True)
    image = Image.open(io.BytesIO(raw))
    image.load()
    if image.size != (1100, 842) or image.format != "JPEG":
        raise ValueError("Unexpected source image")
    approach, east = points("APPROACH"), points("BASE_EAST")
    if approach[-1] != [699, 799] or east[-1] != [1100, 704]:
        raise ValueError("Unreviewed anchor change")
    route = [approach[-1]] + east
    for a, b in zip(route, route[1:]):
        d = math.dist(a, b)
        if not (0 < d <= 100):
            raise ValueError("Bad route segment")
    return image.convert("RGB"), raw, route


def sample(route, fraction):
    segments = [math.dist(a, b) for a, b in zip(route, route[1:])]
    remaining = sum(segments) * fraction
    for i, length in enumerate(segments):
        if remaining <= length or i == len(segments) - 1:
            t = min(1, remaining / length)
            a, b = route[i], route[i + 1]
            return [round(a[0] + t * (b[0] - a[0])),
                    round(a[1] + t * (b[1] - a[1]))]


def run(text, out=OUT):
    image, raw, route = extract(text)
    out.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (560, 704), "#25382d")
    draw = ImageDraw.Draw(sheet)
    samples = []
    for i in range(16):
        x, y = sample(route, i / 15)
        x0, y0 = x - 70, y - 70
        x1, y1 = x + 70, y + 70
        clipped = x0 < 0 or y0 < 0 or x1 > 1100 or y1 > 842
        bounds = (max(0, x0), max(0, y0), min(1100, x1), min(842, y1))
        crop = Image.new("RGB", (140, 140), "#333333")
        crop.paste(image.crop(bounds), (bounds[0] - x0, bounds[1] - y0))
        col, row = i % 4, i // 4
        sheet.paste(crop, (col * 140, row * 176 + 36))
        draw.text((col * 140 + 3, row * 176 + 3),
                  f"{i+1}: {x},{y}", fill="white")
        draw.text((col * 140 + 3, row * 176 + 19),
                  "EDGE/UNKNOWN" if clipped else "RAW JPEG", fill="#e8c78a")
        samples.append({"pixel": [x, y], "source_boundary_clipped": clipped})
    sheet.save(out / "raw-jpeg-road-contact-sheet.png")
    result = {
        "status": "REVIEW_REQUIRED",
        "source_jpeg_sha256": hashlib.sha256(raw).hexdigest(),
        "bridge_endpoint": [699, 799],
        "candidate_east_exit": [1100, 704],
        "raw_source_samples": samples,
        "road_surface_verified": False,
        "historical_road_verified": False,
        "far_bank_verified": False,
        "neighbor_art_verified": False,
        "production_ready": False,
        "warning": "Candidate route overlay is NOT evidence of a road in the raw painting."
    }
    (out / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    print(run(SOURCE.read_text())["status"])
