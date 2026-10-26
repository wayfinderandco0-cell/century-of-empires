#!/usr/bin/env python3
"""V221: original Matrei versus native source-art detail. DIAGNOSTIC ONLY.

This script never changes source imagery, invented routes, sprites, artwork,
historical status or the V203 visual acceptance thresholds. A high texture
score does not imply geographic accuracy, period authenticity, or approval.
"""
import argparse
import base64
import hashlib
import io
import json
import re
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

ROOT = Path(__file__).resolve().parents[1]
NATIVE_SIZE = (1536, 1024)
EDGE_THRESHOLD = 12


def measure(image):
    """Same fine-detail signal as V203, but at ORIGINAL native pixel scale."""
    sample = image.convert("L")
    w, h = sample.size
    sample = sample.crop((int(w * .22), int(h * .22),
                          int(w * .80), int(h * .78)))
    diff = ImageChops.difference(sample, sample.filter(ImageFilter.GaussianBlur(3)))
    hist = diff.histogram()
    return {
        "native_mean_fine_luma": round(ImageStat.Stat(diff).mean[0], 4),
        "native_fine_area_fraction": round(sum(hist[EDGE_THRESHOLD + 1:]) / sum(hist), 5),
        "native_sample_pixels": sample.width * sample.height,
    }


def load_matrei():
    html = (ROOT / "v121-octagon-1-painted-road.html").read_text(encoding="utf-8")
    match = re.search(r"source\.src='data:image/webp;base64,([^']+)'", html)
    if not match:
        raise ValueError("Original V121 Matrei image unavailable; do not substitute another image")
    image = Image.open(io.BytesIO(base64.b64decode(match.group(1)))).convert("RGB")
    if image.size != NATIVE_SIZE:
        raise ValueError("V121 original image dimensions changed")
    return image


def load_sources():
    directory = ROOT / "terrain-v220/assets"
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest["version"] != 220 or manifest["sourceYear"] != 2023:
        raise ValueError("Unexpected V220 source identity/year")
    for flag in ("gameArtApproved", "physicalIPhoneApproved", "productionApproved",
                 "sourceRegisteredToV123", "historicRoadsVerified", "periodSafe"):
        if manifest.get(flag) is not False:
            raise ValueError("Must retain FALSE source/approval status: " + flag)
    if (manifest.get("roadGraphUnchanged") is not True
            or manifest.get("centerMatreiArtworkUnchanged") is not True
            or manifest.get("sourceAreasNotGameGeography") is not True
            or manifest.get("contiguousBetweenGameCells") is not False):
        raise ValueError("V220 unregistered study invariants changed")
    photos = {}
    visited = set()
    cells = manifest["cells"]
    if len(cells) != 2 or [c["cell"] for c in cells] != ["west", "south"]:
        raise ValueError("Expected two original modern source cells")
    for cell in cells:
        name = cell["cell"]
        origin_x, origin_y, level = cell["originXYZ"]
        if len(cell["tiles"]) != 24:
            raise ValueError("V220 source photo is incomplete: " + name)
        for item in cell["tiles"]:
            col, row = item["col"], item["row"]
            if not (0 <= col < 6 and 0 <= row < 4):
                raise ValueError("Source tile outside native mosaic")
            if item["xyz"] != [origin_x + col, origin_y + row, level]:
                raise ValueError("Source tile does not match unaltered map source")
            tile_id = tuple(item["xyz"])
            if tile_id in visited:
                raise ValueError("Duplicated aerial source tile")
            visited.add(tile_id)
            raw = (directory / item["name"]).read_bytes()
            if hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise ValueError("Original 2023 image altered: " + item["name"])
        image = Image.open(directory / cell["file"]).convert("RGB")
        if image.size != NATIVE_SIZE:
            raise ValueError("Native source rescaled: " + name)
        photos[name] = image
    if len(visited) != 48:
        raise ValueError("Expected 48 different original source tiles")
    return manifest, photos


def write_contact(images, scores, filename):
    panel_w, panel_h, pad, heading = 512, 342, 18, 86
    sheet = Image.new("RGB", (3 * panel_w + 4 * pad, panel_h + heading + 2 * pad), "#202721")
    draw = ImageDraw.Draw(sheet)
    labels = (("matrei", "ORIGINAL MATREI GAME ART"),
              ("west", "WEST / MODERN 2023"),
              ("south", "SOUTH / MODERN 2023"))
    for i, (key, title) in enumerate(labels):
        x = pad + i * (panel_w + pad)
        image = images[key].resize((panel_w, panel_h), Image.Resampling.LANCZOS)
        sheet.paste(image, (x, heading))
        s = scores[key]
        draw.text((x + 2, pad), title, fill="#f0efdd")
        draw.text((x + 2, pad + 22),
                  "Fine mean: " + str(s["native_mean_fine_luma"]), fill="#e8d69f")
        draw.text((x + 2, pad + 43),
                  "Fine area: " + str(s["native_fine_area_fraction"]), fill="#e8d69f")
    sheet.save(filename, quality=87, optimize=True)


def audit(output):
    output.mkdir(parents=True, exist_ok=True)
    manifest, neighbors = load_sources()
    images = {"matrei": load_matrei(), **neighbors}
    scores = {key: measure(image) for key, image in images.items()}
    baseline = scores["matrei"]
    relative = {}
    for key in ("west", "south"):
        value = scores[key]
        relative[key] = {
            "native_fine_mean_ratio": round(value["native_mean_fine_luma"]
                                            / max(baseline["native_mean_fine_luma"], .000001), 4),
            "native_fine_area_ratio": round(value["native_fine_area_fraction"]
                                            / max(baseline["native_fine_area_fraction"], .000001), 4),
        }
    report = {
        "version": 221,
        "method": "Original-pixel V203-style blur-radius-3 residual; NOT phone screenshots",
        "sourceYear": 2023,
        "sourceAttribution": manifest["attribution"],
        "nativeSourceDimensions": list(NATIVE_SIZE),
        "nativeMetrics": scores,
        "nativeRelativeToMatrei": relative,
        "interpretation": ("This isolates native image detail from phone-scale renderer loss. "
                           "Differences can also arise from forest, lighting and content; "
                           "do not add fake edge noise or mislabel 2023 roads as historic."),
        "approval": {
            "historicalRoadsVerified": False,
            "sourceRegisteredToGame": False,
            "periodSafeArtwork": False,
            "humanArtApproved": False,
            "physicalIPhoneApproved": False,
            "productionApproved": False,
        },
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    write_contact(images, scores, output / "native-source-contact.jpg")
    print(json.dumps({"version": 221, "nativeRelativeToMatrei": relative,
                      "sourceDetailMeasured": True, "gameArtApproved": False}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "qa/v221-source-detail")
    args = parser.parse_args()
    audit(args.output)

