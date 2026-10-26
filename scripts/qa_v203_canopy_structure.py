#!/usr/bin/env python3
"""V203: fail-closed photographic microstructure audit of three actual phone screenshots.

This is a necessary visual diagnostic, NEVER proof of real geography, source
provenance, period authenticity, human approval, or playable terrain.
"""
import argparse
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ENGINES = ("chromium", "webkit")
ORIENTATIONS = ("portrait", "landscape")
REGIONS = ("west", "matrei", "south")
# Deliberately more demanding than the inherited V192 one-pixel gradient gate.
# Do not lower these to make artificial conifers pass.
MIN_FINE_MEAN_RATIO = .70
MIN_FINE_AREA_RATIO = .70
FINE_EDGE_THRESHOLD = 12
PINNED = {
    "v121-octagon-1-painted-road.html": "4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382",
    "terrain-grid/v123-atlas.js": "09f04b4062e24fbacbb645307462cdddce2b2aa3",
}


def roi(im):
    w, h = im.size
    box = (int(w * .22), int(h * .22), int(w * .80), int(h * .78))
    if box[2] - box[0] < 40 or box[3] - box[1] < 40:
        raise ValueError("Phone screenshot is too small for V203 analysis")
    return im.convert("L").crop(box)


def measure(im):
    sample = roi(im)
    residual = ImageChops.difference(sample, sample.filter(ImageFilter.GaussianBlur(3)))
    histogram = residual.histogram()
    count = sum(histogram)
    if not count:
        raise ValueError("Empty terrain crop")
    return {
        "mean_fine_luma": round(ImageStat.Stat(residual).mean[0], 4),
        "fine_area_fraction": round(sum(histogram[FINE_EDGE_THRESHOLD + 1:]) / count, 5),
        "pixels": count,
    }, residual


def assess(scores):
    center = scores["matrei"]
    if center["mean_fine_luma"] <= 0 or center["fine_area_fraction"] <= 0:
        raise ValueError("Matrei photographic baseline is blank")
    checks = {}
    for name in ("west", "south"):
        candidate = scores[name]
        mean_ratio = candidate["mean_fine_luma"] / center["mean_fine_luma"]
        area_ratio = candidate["fine_area_fraction"] / center["fine_area_fraction"]
        checks[name] = {
            "relative_fine_luma": round(mean_ratio, 4),
            "relative_fine_area": round(area_ratio, 4),
            "passes_necessary_structure": mean_ratio >= MIN_FINE_MEAN_RATIO
                                           and area_ratio >= MIN_FINE_AREA_RATIO,
        }
    return checks


def audit(screenshots, output, *, make_contact=True):
    results, missing, contact_rows = {}, [], []
    for engine in ENGINES:
        for orientation in ORIENTATIONS:
            scores, pictures = {}, []
            for region in REGIONS:
                path = screenshots / f"{engine}-{orientation}-{region}-close.png"
                if not path.is_file():
                    missing.append(path.name)
                    continue
                with Image.open(path) as im:
                    scores[region], residual = measure(im)
                    if make_contact:
                        crop = roi(im)
                        crop.thumbnail((245, 360))
                        fine = ImageOps.autocontrast(residual)
                        fine.thumbnail((245, 360))
                        pictures.append((region, crop.convert("RGB"), fine.convert("RGB")))
            if len(scores) == 3:
                checks = assess(scores)
                results[f"{engine}-{orientation}"] = {
                    "scores": scores, "neighbors": checks,
                    "necessary_structure_gate_pass": all(c["passes_necessary_structure"] for c in checks.values()),
                }
                if make_contact:
                    contact_rows.append((f"{engine}-{orientation}", pictures))
    passed = not missing and len(results) == 4 and all(
        r["necessary_structure_gate_pass"] for r in results.values())
    report = {
        "passed": passed,
        "missing_screenshots": missing,
        "results": results,
        "minimum_relative_fine_luma": MIN_FINE_MEAN_RATIO,
        "minimum_relative_fine_area": MIN_FINE_AREA_RATIO,
        "blur_radius_native_screenshot_pixels": 3,
        "fine_edge_threshold": FINE_EDGE_THRESHOLD,
        "geographicRegistrationVerified": False,
        "periodSafeArtworkVerified": False,
        "historicRoadsAndBridgeBanksVerified": False,
        "humanArtApproved": False,
        "physicalIPhoneApproved": False,
        "productionApproved": False,
        "note": "A passing numeric microstructure test is NEVER artwork approval; artificial noise can also pass. Inspect actual screenshot and independently verify source/registration."
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    if make_contact and contact_rows:
        width = 1510
        row_heights = [max(max(crop.height, fine.height) for _, crop, fine in pictures) + 65
                       for _, pictures in contact_rows]
        sheet = Image.new("RGB", (width, sum(row_heights)), "#15231d")
        draw = ImageDraw.Draw(sheet)
        y = 0
        for (label, pictures), row_h in zip(contact_rows, row_heights):
            draw.text((10, y + 5), label + " | LEFT: screenshot grayscale | RIGHT: high-frequency residual (contrast enhanced)", fill="white")
            for ci, (region, crop, residual) in enumerate(pictures):
                x = 10 + ci * 500
                draw.text((x, y + 27), region.upper(), fill="#f1d7a1")
                sheet.paste(crop, (x, y + 45))
                sheet.paste(residual, (x + 245, y + 45))
            y += row_h
        sheet.save(output / "canopy-structure-contact.jpg", quality=90)
    return report


def verify_pins():
    for path, sha in PINNED.items():
        actual = subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()
        if actual != sha:
            raise ValueError(f"Immutable V121/V123 source changed: {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshots", type=Path, default=ROOT / "qa" / "v192-three-centers")
    parser.add_argument("--output", type=Path, default=ROOT / "qa" / "v203-canopy-structure")
    parser.add_argument("--enforce", action="store_true")
    parser.add_argument("--skip-source-pins", action="store_true", help="Only for offline image-unit tests")
    args = parser.parse_args()
    if not args.skip_source_pins:
        verify_pins()
    report = audit(args.screenshots, args.output)
    print(json.dumps(report, indent=2), flush=True)
    if args.enforce and not report["passed"]:
        raise SystemExit("V203 visual structure REJECTED: neighboring Alpine artwork lacks Matrei-like photographic microstructure")


if __name__ == "__main__":
    main()
