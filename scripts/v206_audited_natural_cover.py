#!/usr/bin/env python3
"""V206: source-pinned natural-cover candidate crops, NEVER playable game octagons.

Manual visual selection from the actual V205 basemap.at forest contact image.
No inferred 1780 vegetation, invented roads, source-to-V123 registration or
claims of a clean modern-free/historically correct game image.
"""
import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw
import v204_contiguous_matrei_sources as source

# Actual V205 inspected artifact 12627508315. Fail closed if source changes.
SOURCE_SHA256 = {
    "west_reference": "560ac2c3f3848319d5fc07140e83378de8f1ef723efe9c8ccbba976e18c41232",
    "matrei_reference": "574548099c83064c67d91729751de55f75d6d3adbb7163a60e4f39d3078cacc6",
    "south_reference": "db5239fc37ba17600fd051490f4324e7ca6f6b7972a9ff99895c24654b5ab2f4",
}
# 96x96 native pixels per reference panel; actual V205 imagery inspected.
# Rectangles avoid the visibly obvious tracks, hairpins and date imprints.
# They are candidates, NOT a guarantee of no modern land use.
RECTS = {
    "west_reference": (360, 398, 456, 494),
    "matrei_reference": (280, 185, 376, 281),
    "south_reference": (352, 24, 448, 120),
}
FALSE_FLAGS = ("gameArtApproved", "sourceRegisteredToV123",
               "historicalVegetationVerified", "modernFeaturesFullyExcluded",
               "bridgeBanksVerified", "roadsAlignedToGame", "physicalIPhoneApproved")


def require(ok, why):
    if not ok:
        raise ValueError(why)


def geo_bounds(panel, box):
    x, y, _ = panel["nativeOriginXYZ"]
    left, top, right, bottom = box
    n = 1 << source.ZOOM
    lon = lambda px: 360 * px / n - 180
    lat = lambda py: math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * py / n))))
    return [lon(x + left / source.TILE), lat(y + bottom / source.TILE),
            lon(x + right / source.TILE), lat(y + top / source.TILE)]


def inspect_source(folder):
    folder = Path(folder)
    source.verify(folder)  # Native JPEGs, source RGB, seams, contact and manifest.
    manifest = json.loads((folder / "manifest.json").read_text())
    require(manifest["site"] == "forest", "only inspected V205 forest site allowed")
    panels = {p["name"]: p for p in manifest["panels"]}
    require(set(panels) == set(RECTS), "unexpected source panels")
    for name, panel in panels.items():
        require(panel["sourceSha256"] == SOURCE_SHA256[name],
                "inspected V205 source changed; re-inspect before selecting crops: " + name)
    return manifest, panels


def expected(source_folder):
    manifest, panels = inspect_source(source_folder)
    candidates = []
    for name, box in RECTS.items():
        panel = panels[name]
        candidates.append({
            "sourcePanel": name,
            "sourcePanelSha256": SOURCE_SHA256[name],
            "nativeSourceRectXYXY": list(box),
            "nativeEPSG3857FootprintLonLat": geo_bounds(panel, box),
            "candidateImage": name + "-natural-cover-candidate.png",
            "sourceSiteNotV123GameCell": True,
            "visualSelectionOnlyNotHistoricalApproval": True,
        })
    return {
        "version": 206,
        "purpose": "Unaltered native RGB natural-cover candidate samples; NOT playable Alpine octagons",
        "sourceSite": "forest",
        "sourceManifestSha256": source.sha(Path(source_folder) / "manifest.json"),
        "provider": "basemap.at",
        "license": "CC BY 4.0",
        "requiredAttribution": "Datenquelle: basemap.at",
        "selectionNote": "Actual V205 contact visually reviewed; visible roads/date marks avoided in crops only",
        "candidates": candidates,
        **{flag: False for flag in FALSE_FLAGS},
    }


def build(source_folder, output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    manifest = expected(source_folder)
    strip = Image.new("RGB", (96 * 3, 96 + 44), (20, 35, 28))
    for i, candidate in enumerate(manifest["candidates"]):
        name = candidate["sourcePanel"]
        with Image.open(Path(source_folder) / (name + ".png")) as im:
            crop = im.convert("RGB").crop(tuple(candidate["nativeSourceRectXYXY"]))
        require(crop.size == (96, 96), "crop is not native 96px square")
        path = output_folder / candidate["candidateImage"]
        crop.save(path)
        candidate["candidateSha256"] = source.sha(path)
        strip.paste(crop, (i * 96, 0))
    draw = ImageDraw.Draw(strip)
    draw.text((3, 100), "WEST      CENTER      SOUTH", fill="#fff0ce")
    draw.text((3, 116), "MODERN SOURCE ONLY / NOT GAME ART", fill="#fff0ce")
    draw.text((3, 130), "Datenquelle: basemap.at / CC BY 4.0", fill="#fff0ce")
    strip.save(output_folder / "candidate-contact.png")
    manifest["contactImage"] = "candidate-contact.png"
    manifest["contactSha256"] = source.sha(output_folder / "candidate-contact.png")
    (output_folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify(source_folder, output_folder)
    return manifest


def verify(source_folder, output_folder):
    output_folder = Path(output_folder)
    actual = json.loads((output_folder / "manifest.json").read_text())
    control = expected(source_folder)
    require(set(actual) == set(control) | {"contactImage", "contactSha256"},
            "unexpected candidate metadata")
    for key, value in control.items():
        if key != "candidates":
            require(actual.get(key) == value, "candidate source/approval changed: " + key)
    require(len(actual["candidates"]) == 3, "three source candidates required")
    for got, exp in zip(actual["candidates"], control["candidates"]):
        require(set(got) == set(exp) | {"candidateSha256"},
                "unexpected crop metadata")
        for key, value in exp.items():
            require(got.get(key) == value, "candidate coordinates or source changed: " + key)
        name = exp["sourcePanel"]
        path = output_folder / exp["candidateImage"]
        require(path.is_file() and got.get("candidateSha256") == source.sha(path),
                "candidate hash missing or changed")
        with Image.open(Path(source_folder) / (name + ".png")) as original:
            expected_rgb = original.convert("RGB").crop(tuple(exp["nativeSourceRectXYXY"]))
        with Image.open(path) as sample:
            require(sample.size == (96, 96) and sample.convert("RGB").tobytes() ==
                    expected_rgb.tobytes(), "candidate pixels not identical to native source")
    contact = output_folder / "candidate-contact.png"
    require(actual.get("contactImage") == contact.name and contact.is_file()
            and actual.get("contactSha256") == source.sha(contact),
            "candidate contact sheet changed")
    with Image.open(contact) as im:
        require(im.size == (288, 140), "candidate contact size changed")
        for i, candidate in enumerate(actual["candidates"]):
            with Image.open(output_folder / candidate["candidateImage"]) as crop:
                require(im.crop((i * 96, 0, (i + 1) * 96, 96)).convert("RGB").tobytes()
                        == crop.convert("RGB").tobytes(), "contact pixels altered")
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    if args.verify:
        verify(args.source, args.output)
    else:
        build(args.source, args.output)
    print("V206 source RGB verified; game road/bridge/geography/art approval remains FALSE")


if __name__ == "__main__":
    main()
