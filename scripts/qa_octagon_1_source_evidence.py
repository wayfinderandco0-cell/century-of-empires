#!/usr/bin/env python3
"""Independent Octagon 1 source-art comparison evidence (NOT playable-road approval).

Reads the embedded original JPEG and candidate coordinates without executing the
HTML renderer. Exports source-only and candidate overlays for visual review.
"""
import argparse
import base64
import hashlib
import io
import json
import re
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def read_candidate(html):
    def value(name):
        match = re.search(r"\bconst\s+" + name + r"\s*=\s*(\[.*?\]);", html, re.S)
        if not match:
            raise ValueError(f"Missing candidate source: {name}")
        return json.loads(match.group(1))

    match = re.search(r'\bconst\s+IMAGE\s*=\s*"data:image/jpeg;base64,([A-Za-z0-9+/=]+)";', html)
    if not match:
        raise ValueError("Missing embedded source JPEG")
    raw = base64.b64decode(match.group(1), validate=True)
    with Image.open(io.BytesIO(raw)) as original:
        original.load()
        image = original.convert("RGB")
    approach, east = value("APPROACH"), value("BASE_EAST")
    if image.size != (1100, 842):
        raise ValueError(f"Unexpected source-art size: {image.size}")
    if approach[-1] != [699, 799] or east[-1] != [1100, 704]:
        raise ValueError("Candidate bridge/exit control point changed")
    points = approach + east
    if not all(isinstance(p, list) and len(p) == 2
               and all(isinstance(n, (int, float)) for n in p)
               and 0 <= p[0] <= image.width and 0 <= p[1] <= image.height
               for p in points):
        raise ValueError("Candidate route outside source-art coordinates")
    return raw, image, approach, east


def render_evidence(html, out):
    raw, source, approach, east = read_candidate(html)
    out.mkdir(parents=True, exist_ok=True)
    # Both images use the exact same unmodified source-art crop.
    bounds = (680, 640, 1100, 842)
    unpainted = source.crop(bounds)
    annotated = unpainted.copy()
    draw = ImageDraw.Draw(annotated)
    route = [approach[-1]] + east
    translated = [(p[0] - bounds[0], p[1] - bounds[1]) for p in route]
    draw.line(translated, fill=(255, 210, 70), width=3, joint="curve")
    for p in translated:
        draw.ellipse((p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2),
                     fill=(25, 55, 255))
    unpainted.save(out / "east-bank-source-only.png")
    annotated.save(out / "east-bank-candidate-over-source.png")
    source.crop((420, 700, 750, 842)).save(out / "bridge-source-only.png")
    report = {
        "source_jpeg_sha256": hashlib.sha256(raw).hexdigest(),
        "source_dimensions": list(source.size),
        "east_crop_source_pixels": list(bounds),
        "fixed_approach_points": len(approach),
        "candidate_east_points": len(east),
        "bridge_endpoint": approach[-1],
        "east_exit": east[-1],
        "next_octagon_source_art_exists": False,
        "independent_historical_road_verified": False,
        "road_pixels_independently_verified": False,
        "approved_for_production": False,
        "note": "Yellow line is an authoring candidate on the unmodified JPEG, not evidence that the source image contains a continuous road.",
    }
    (out / "source-art-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def self_test():
    image = Image.new("RGB", (1100, 842), (45, 65, 30))
    stream = io.BytesIO()
    image.save(stream, format="JPEG")
    encoded = base64.b64encode(stream.getvalue()).decode()
    html = ("const APPROACH=[[680,800],[699,799]];\n"
            "const BASE_EAST=[[720,795],[1100,704]];\n"
            f'const IMAGE="data:image/jpeg;base64,{encoded}";')
    with tempfile.TemporaryDirectory() as directory:
        out = Path(directory)
        result = render_evidence(html, out)
        assert result["source_dimensions"] == [1100, 842]
        assert result["approved_for_production"] is False
        assert ((out / "east-bank-source-only.png").read_bytes()
                != (out / "east-bank-candidate-over-source.png").read_bytes())
        assert Image.open(out / "east-bank-source-only.png").size == (420, 202)
        assert Image.open(out / "bridge-source-only.png").size == (330, 142)
        for invalid in (html.replace("[699,799]", "[700,799]"),
                        html.replace("[1100,704]", "[1101,704]")):
            try:
                render_evidence(invalid, out)
            except ValueError:
                pass
            else:
                raise AssertionError("Expected invalid geometry rejection")
    print("PASS: source decode, independent overlay, dimensions, rejection gates, nonapproval")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--html", type=Path,
                        default=ROOT / "octagon-1-road-authoring.html")
    parser.add_argument("--out", type=Path,
                        default=ROOT / "qa" / "octagon-1" / "source-evidence")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        print(json.dumps(render_evidence(args.html.read_text(), args.out), indent=2))
