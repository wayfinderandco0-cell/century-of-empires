#!/usr/bin/env python3
"""V198 conservative SOURCE exclusion study; NOT historical GAME artwork.

The annotations below were traced from the actual V197 1536x554 contact sheet.
They quarantine visible year stamps and suspected modern tracks; transparent
pixels are deliberately NOT inpainted, replaced, or declared historically absent.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
import v197_highres_material_samples as v197

SIZE = (512, 512)
# Pixel coordinates within each V197 512x512 modern-source patch.
# A suspect track is quarantined, NOT classified as a non-historic route.
ANNOTATIONS = {
    "western_forest_reference": [
        {"kind": "date_imprint", "rect": [0, 23, 18, 40]},
        {"kind": "date_imprint", "rect": [303, 23, 332, 41]},
        {"kind": "date_imprint", "rect": [306, 345, 333, 366]},
        {"kind": "unverified_track", "polygon": [[373,512],[381,495],[401,482],[432,469],[477,456],[512,461],[512,499],[480,488],[441,505],[419,512]]},
    ],
    "eastern_ridge_reference": [
        {"kind": "date_imprint", "rect": [239, 149, 269, 169]},
        {"kind": "date_imprint", "rect": [239, 471, 270, 490]},
    ],
    "southern_forest_reference": [
        {"kind": "date_imprint", "rect": [174, 215, 203, 234]},
        {"kind": "date_imprint", "rect": [490, 216, 512, 234]},
        {"kind": "unverified_track", "polygon": [[190,316],[205,319],[230,343],[253,378],[260,398],[241,405],[230,379],[213,353],[187,336]]},
        {"kind": "unverified_track", "polygon": [[311,401],[333,405],[360,432],[380,465],[395,490],[415,512],[375,512],[357,485],[338,451],[323,431],[307,420]]},
    ],
}
FALSE_FLAGS = ("gameArtApproved", "gameOctagonsGeoregistered",
               "historicalRoadsVerified", "modernInfrastructureFullyExcluded",
               "bridgeBanksVerified", "physicalIPhoneApproved",
               "productionApproved", "periodSafe")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_annotations():
    require(tuple(ANNOTATIONS) == tuple(s["name"] for s in v197.plan()["samples"]),
            "source identity changed")
    for name, items in ANNOTATIONS.items():
        require(items and len(items) <= 20, "missing or excessive annotations: " + name)
        for item in items:
            require(item["kind"] in ("date_imprint", "unverified_track"),
                    "unreviewed annotation kind")
            require(set(item) == ({"kind", "rect"} if item["kind"] == "date_imprint"
                                   else {"kind", "polygon"}), "annotation shape")
            if "rect" in item:
                x0, y0, x1, y1 = item["rect"]
                require(0 <= x0 < x1 <= 512 and 0 <= y0 < y1 <= 512,
                        "out-of-bounds rectangle")
            else:
                points = item["polygon"]
                require(3 <= len(points) <= 30 and
                        all(len(p) == 2 and 0 <= p[0] <= 512 and
                            0 <= p[1] <= 512 for p in points),
                        "out-of-bounds polygon")
    return True

def exclusion_mask(name):
    validate_annotations()
    require(name in ANNOTATIONS, "unknown source patch")
    mask = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(mask)
    for item in ANNOTATIONS[name]:
        if "rect" in item:
            draw.rectangle(item["rect"], fill=255)
        else:
            draw.polygon(item["polygon"], fill=255)
    pixels = mask.tobytes()
    excluded = pixels.count(255)
    require(set(pixels) <= {0, 255} and 100 < excluded < 0.12 * 512 * 512,
            "mask must be conservative and binary")
    return mask

def render(source, mask):
    require(source.size == SIZE and mask.size == SIZE, "wrong source dimensions")
    rgba = source.convert("RGBA")
    rgba.putalpha(mask.point(lambda x: 255 - x))
    # Never synthesize color or paint over modern features. Alpha is the ONLY edit.
    require(rgba.convert("RGB").tobytes() == source.convert("RGB").tobytes(),
            "source RGB modified")
    preview = source.convert("RGB").copy()
    red = Image.new("RGB", SIZE, (220, 40, 65))
    tinted = Image.blend(preview, red, 0.68)
    preview.paste(tinted, (0, 0), mask)
    return rgba, preview

def expected_meta(source_dir):
    source_dir = Path(source_dir)
    require(v197.verify(source_dir), "V197 source verification failed")
    src = json.loads((source_dir / "manifest.json").read_text())
    require(src["requiredAttribution"] == "Datenquelle: basemap.at",
            "attribution removed")
    return {
        "version": 198,
        "purpose": "Source reference exclusions only; not historical game art",
        "sourceManifestSha256": sha(source_dir / "manifest.json"),
        "provider": src["provider"],
        "license": src["license"],
        "requiredAttribution": src["requiredAttribution"],
        "geographicRegistrationToV123": False,
        "unreviewedModernFeaturesRemain": True,
        "allQuarantinedTracksAreHistoricallyUnverified": True,
        "annotations": copy.deepcopy(ANNOTATIONS),
        **{k: False for k in FALSE_FLAGS},
    }

def produce(source_dir, output_dir):
    source_dir, output_dir = Path(source_dir), Path(output_dir)
    meta = expected_meta(source_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    contact = Image.new("RGB", (1536, 554), (17, 32, 27))
    labels = ImageDraw.Draw(contact)
    samples = []
    for i, sample in enumerate(v197.plan()["samples"]):
        name = sample["name"]
        source_path = source_dir / sample["image"]
        with Image.open(source_path) as im:
            source = im.convert("RGB")
        mask = exclusion_mask(name)
        rgba, preview = render(source, mask)
        rgba_path = output_dir / (name + "-quarantined.png")
        mask_path = output_dir / (name + "-excluded-mask.png")
        rgba.save(rgba_path)
        mask.save(mask_path)
        contact.paste(preview, (512 * i, 0))
        labels.text((512 * i + 8, 518), name + " | red = excluded, NOT repaired",
                    fill=(240, 227, 201))
        samples.append({
            "name": name,
            "sourceImageSha256": sha(source_path),
            "quarantinedImage": rgba_path.name,
            "quarantinedImageSha256": sha(rgba_path),
            "maskImage": mask_path.name,
            "maskImageSha256": sha(mask_path),
            "excludedPixelCount": mask.tobytes().count(255),
            "retainedPixelCount": mask.tobytes().count(0),
            "manualReviewRequired": True,
            "eligibleForGameArt": False,
        })
    contact_path = output_dir / "v198-exclusion-review-contact.png"
    contact.save(contact_path)
    meta["samples"] = samples
    meta["contactImage"] = contact_path.name
    meta["contactImageSha256"] = sha(contact_path)
    (output_dir / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
    verify(source_dir, output_dir)
    return meta

def verify(source_dir, output_dir):
    source_dir, output_dir = Path(source_dir), Path(output_dir)
    expected = expected_meta(source_dir)
    meta = json.loads((output_dir / "manifest.json").read_text())
    for key, value in expected.items():
        require(meta.get(key) == value, "provenance or approvals altered: " + key)
    require(set(meta) == set(expected) | {"samples", "contactImage",
                                        "contactImageSha256"}, "unexpected metadata")
    require(len(meta["samples"]) == 3, "missing source")
    contact = Image.new("RGB", (1536, 554), (17, 32, 27))
    labels = ImageDraw.Draw(contact)
    for i, original in enumerate(v197.plan()["samples"]):
        sample = meta["samples"][i]
        name = original["name"]
        with Image.open(source_dir / original["image"]) as im:
            source = im.convert("RGB")
        mask = exclusion_mask(name)
        rgba, preview = render(source, mask)
        expected_sample = {
            "name": name,
            "sourceImageSha256": sha(source_dir / original["image"]),
            "quarantinedImage": name + "-quarantined.png",
            "maskImage": name + "-excluded-mask.png",
            "excludedPixelCount": mask.tobytes().count(255),
            "retainedPixelCount": mask.tobytes().count(0),
            "manualReviewRequired": True,
            "eligibleForGameArt": False,
        }
        for key, value in expected_sample.items():
            require(sample.get(key) == value, "sample identity altered: " + key)
        for filename_key, hash_key, expected_image in (
            ("quarantinedImage", "quarantinedImageSha256", rgba),
            ("maskImage", "maskImageSha256", mask),
        ):
            path = output_dir / sample[filename_key]
            require(path.is_file() and sample.get(hash_key) == sha(path),
                    "missing or altered output")
            with Image.open(path) as stored:
                require(stored.mode == expected_image.mode and
                        stored.size == expected_image.size and
                        stored.tobytes() == expected_image.tobytes(),
                        "pixel integrity failure")
        require(set(sample) == set(expected_sample) |
                {"quarantinedImageSha256", "maskImageSha256"},
                "unexpected sample fields")
        contact.paste(preview, (512 * i, 0))
        labels.text((512 * i + 8, 518), name + " | red = excluded, NOT repaired",
                    fill=(240, 227, 201))
    path = output_dir / "v198-exclusion-review-contact.png"
    require(meta["contactImage"] == path.name and
            meta["contactImageSha256"] == sha(path), "contact identity changed")
    with Image.open(path) as stored:
        require(stored.convert("RGB").tobytes() == contact.tobytes(),
                "contact pixels changed")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="qa/v197-highres-source-materials")
    parser.add_argument("--output", default="qa/v198-source-exclusions")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify(args.source, args.output)
    else:
        produce(args.source, args.output)
    print("V198 SOURCE quarantine verified; GAME art/historical roads NOT approved")

if __name__ == "__main__":
    main()
