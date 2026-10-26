#!/usr/bin/env python3
"""V214: select unaltered native aerial MATERIAL samples, not geographic game tiles.

Only uses V205 SHA-pinned modern basemap.at imagery and V207 manually audited
exclusion masks. No interpolation, synthetic noise, inpainting, source-to-game
registration, historic vegetation assertion, or road/army edits.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

import v204_contiguous_matrei_sources as source
import v206_audited_natural_cover as v206
import v207_conservative_modern_masks as masks

SIZE = 128
MARGIN = 12
STEP = 8
PANELS = ("west_reference", "matrei_reference", "south_reference")
FALSE_FLAGS = (
    "sourceRegisteredToV123", "periodSafe", "historicalVegetationVerified",
    "allModernFeaturesExcluded", "historicalRoadsVerified",
    "bridgeBanksVerified", "roadsAlignedToGame", "gameArtApproved",
    "physicalIPhoneApproved", "productionApproved",
)


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def choose_native_patch(rgb, mask, size=SIZE, margin=MARGIN, step=STEP):
    """Find the highest-detail entirely retained 1:1 RGB crop; never fill gaps."""
    require(rgb.mode == "RGB" and mask.mode == "L" and rgb.size == mask.size,
            "native source/mask size or mode mismatch")
    w, h = rgb.size
    require(0 < margin < size < min(w, h) and step > 0 and margin % 1 == 0,
            "invalid native crop geometry")
    require(set(mask.getdata()) <= {0, 255}, "mask must be strictly binary")
    # Conservative buffer: even the crop's surrounding 12px must be unmasked.
    clear = mask.filter(ImageFilter.MinFilter(margin * 2 + 1))
    gray = rgb.convert("L")
    gradient = ImageChops.difference(gray, ImageChops.offset(gray, 1, 0))
    best = None
    for y in range(margin, h - size - margin + 1, step):
        for x in range(margin, w - size - margin + 1, step):
            box = (x, y, x + size, y + size)
            if clear.crop(box).getextrema() != (255, 255):
                continue
            score = ImageStat.Stat(gradient.crop(box)).mean[0]
            # Ranking is diagnostic, not a substitute for visual art review.
            candidate = (score, -y, -x, box)
            if best is None or candidate > best:
                best = candidate
    require(best is not None, "no completely retained source-native patch")
    return best[3], round(best[0], 6)


def expected(source_folder):
    source_folder = Path(source_folder)
    source.verify(source_folder)
    exclusion = masks.plan(source_folder)  # Pins V205 source hashes and V207 tracing.
    require(exclusion["sourceSite"] == "forest", "wrong source site")
    require(all(exclusion[k] is False for k in masks.FALSE_FLAGS),
            "upstream modern-feature approval unexpectedly true")
    originals = json.loads((source_folder / "manifest.json").read_text())
    by_name = {p["name"]: p for p in originals["panels"]}
    require(set(by_name) == set(PANELS), "missing native geographic source panels")
    rows = []
    for name in PANELS:
        with Image.open(source_folder / (name + ".png")) as im:
            rgb = im.convert("RGB")
        box, detail = choose_native_patch(rgb, masks.mask_for(name))
        rows.append({
            "sourcePanel": name,
            "sourcePanelSha256": v206.SOURCE_SHA256[name],
            "nativeRectXYXY": list(box),
            "nativeFootprintLonLat": v206.geo_bounds(by_name[name], box),
            "sourceMask": "V207_CONSERVATIVE_MANUAL_EXCLUSIONS",
            "sourcePixelsUnmodified": True,
            "detailScoreDiagnosticOnly": detail,
            "image": name + "-native-material.png",
            "geographicallyRegisteredToGame": False,
            "periodSafeMaterial": False,
        })
    return {
        "version": 214,
        "purpose": "Source-native unaltered 128px photographic material candidates ONLY",
        "site": "V205 modern forest, not original painted Matrei location",
        "sourceManifestSha256": sha(source_folder / "manifest.json"),
        "sourceProjection": "EPSG:3857",
        "license": "CC BY 4.0",
        "requiredAttribution": "Datenquelle: basemap.at",
        "selection": "highest native horizontal luminance detail among fully retained V207-mask crops; no synthetic detail",
        "nativePixelsPerCandidate": [SIZE, SIZE],
        "sourceNotPlacedInPlayableGame": True,
        "candidates": rows,
        **{flag: False for flag in FALSE_FLAGS},
    }


def make_contact(folder, rows):
    sheet = Image.new("RGB", (SIZE * 3, SIZE + 48), (18, 35, 28))
    for index, row in enumerate(rows):
        with Image.open(folder / row["image"]) as im:
            sheet.paste(im.convert("RGB"), (index * SIZE, 0))
    draw = ImageDraw.Draw(sheet)
    draw.text((5, SIZE + 3), "WEST          MATREI        SOUTH", fill="#fff2d4")
    draw.text((5, SIZE + 18), "NATIVE MODERN MATERIAL ONLY / NOT PLAYABLE GAME ART", fill="#fff2d4")
    draw.text((5, SIZE + 33), "Datenquelle: basemap.at / CC BY 4.0", fill="#fff2d4")
    return sheet


def build(source_folder, output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    report = expected(source_folder)
    for row in report["candidates"]:
        with Image.open(Path(source_folder) / (row["sourcePanel"] + ".png")) as im:
            crop = im.convert("RGB").crop(tuple(row["nativeRectXYXY"]))
        require(crop.size == (SIZE, SIZE), "crop was resized or distorted")
        path = output_folder / row["image"]
        crop.save(path)
        row["imageSha256"] = sha(path)
    contact = output_folder / "v214-native-material-contact.png"
    make_contact(output_folder, report["candidates"]).save(contact)
    report["contactImage"] = contact.name
    report["contactSha256"] = sha(contact)
    (output_folder / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    verify(source_folder, output_folder)
    return report


def verify(source_folder, output_folder):
    output_folder = Path(output_folder)
    actual = json.loads((output_folder / "manifest.json").read_text())
    control = expected(source_folder)
    require(set(actual) == set(control) | {"contactImage", "contactSha256"},
            "unexpected material metadata")
    for key, value in control.items():
        if key != "candidates":
            require(actual.get(key) == value, "source/approval metadata altered: " + key)
    require(len(actual["candidates"]) == len(control["candidates"]) == 3,
            "missing original source candidate")
    for row, expected_row in zip(actual["candidates"], control["candidates"]):
        require(set(row) == set(expected_row) | {"imageSha256"},
                "unexpected material candidate metadata")
        for key, value in expected_row.items():
            require(row.get(key) == value, "material provenance/coordinates changed: " + key)
        path = output_folder / row["image"]
        require(path.is_file() and sha(path) == row["imageSha256"],
                "source-native candidate missing or altered")
        with Image.open(Path(source_folder) / (row["sourcePanel"] + ".png")) as src:
            pixels = src.convert("RGB").crop(tuple(row["nativeRectXYXY"])).tobytes()
        with Image.open(path) as crop:
            require(crop.mode == "RGB" and crop.size == (SIZE, SIZE)
                    and crop.tobytes() == pixels,
                    "candidate pixels not bit-identical to original decoded source")
        require(masks.mask_for(row["sourcePanel"]).crop(tuple(row["nativeRectXYXY"])).getextrema()
                == (255, 255), "candidate intersects excluded modern features")
    contact = output_folder / "v214-native-material-contact.png"
    require(contact.is_file() and actual.get("contactImage") == contact.name
            and sha(contact) == actual.get("contactSha256"),
            "contact evidence missing or changed")
    with Image.open(contact) as saved:
        require(saved.convert("RGB").tobytes() ==
                make_contact(output_folder, actual["candidates"]).tobytes(),
                "contact not reproducible from native samples")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify(args.source, args.output)
    else:
        build(args.source, args.output)
    print("V214 original source material audit passed; GAME ART/GEOGRAPHY NOT APPROVED")


if __name__ == "__main__":
    main()
