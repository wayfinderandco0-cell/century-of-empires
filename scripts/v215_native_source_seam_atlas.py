#!/usr/bin/env python3
"""V215: one native EPSG:3857 L-shaped modern Alpine source atlas.

Source material ONLY. No resampling, artificial trees, inferred road extensions,
game-camera registration, historical vegetation claims, or Matrei-photo edits.
Unknown/modern-feature pixels stay transparent, never inpainted.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

import v204_contiguous_matrei_sources as source
import v206_audited_natural_cover as v206
import v214_source_native_material_bank as bank

PANEL = 512
SIZE = (1024, 1024)
ORDER = ("west_reference", "matrei_reference", "south_reference")
FALSE_FLAGS = bank.FALSE_FLAGS + (
    "nativeAtlasIsV123GameTerrain", "sourceSeamsVisuallyApproved",
    "maskedPixelsReconstructed", "realThreeOctagonArtworkComplete",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_sources(folder):
    folder = Path(folder)
    # V214 verifies original V205 SHA-pinned pixels, the modern mask source,
    # reviewed 2023 date quarantine and V121/V123/V94/V97/V102 invariants.
    bank.expected(folder)
    original = json.loads((folder / "manifest.json").read_text())
    require(original["site"] == "forest", "wrong native source location")
    panels = {p["name"]: p for p in original["panels"]}
    require(set(panels) == set(ORDER), "missing native panels")
    return original, panels


def seam_stats(first, second, mask_a, mask_b, direction):
    require(direction in ("vertical", "horizontal"), "invalid seam direction")
    gaps = []
    interior = []
    for i in range(PANEL):
        if direction == "vertical":
            a, b = (511, i), (0, i)
            a_in, b_in = (510, i), (1, i)
        else:
            a, b = (i, 511), (i, 0)
            a_in, b_in = (i, 510), (i, 1)
        if mask_a.getpixel(a) != 255 or mask_b.getpixel(b) != 255:
            continue
        rgb_a, rgb_b = first.getpixel(a), second.getpixel(b)
        gaps.append(sum(abs(x - y) for x, y in zip(rgb_a, rgb_b)) / 3)
        if mask_a.getpixel(a_in) == 255 and mask_b.getpixel(b_in) == 255:
            interior.append((
                sum(abs(x - y) for x, y in zip(first.getpixel(a), first.getpixel(a_in))) +
                sum(abs(x - y) for x, y in zip(second.getpixel(b), second.getpixel(b_in)))
            ) / 6)
    # This is a coverage gate, NOT a claim that an edge looks natural.
    require(len(gaps) >= 64 and len(interior) >= 64,
            "too few adjacent unmasked source pixels for a seam audit")
    return {
        "pairedNativePixels": len(gaps),
        "pairedFraction": round(len(gaps) / PANEL, 6),
        "meanSourceBoundaryDifferenceRGB": round(sum(gaps) / len(gaps), 5),
        "meanWithinPanelDifferenceRGB": round(sum(interior) / len(interior), 5),
        "seamIsGeographicSourceOnly": True,
        "gameSeamOrRoadAlignmentVerified": False,
        "visualSeamApproved": False,
    }


def compose(folder):
    _, panels = read_sources(folder)
    atlas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    images = {}
    masks = {}
    placements = []
    for name in ORDER:
        panel = panels[name]
        ox, oy = panel["pixelOriginInContact"]
        require(ox in (0, PANEL) and oy in (0, PANEL),
                "invalid native source placement")
        with Image.open(Path(folder) / panel["sourceImage"]) as im:
            rgb = im.convert("RGB")
        require(rgb.size == (PANEL, PANEL), "native panel size changed")
        mask = bank.reviewed_mask(name)
        require(mask.size == rgb.size, "source exclusion mask changed dimensions")
        # Transparent regions are zero RGBA; not even hidden RGB road pixels.
        retained = Image.new("RGBA", rgb.size, (0, 0, 0, 0))
        retained.paste(rgb.convert("RGBA"), (0, 0), mask)
        atlas.paste(retained, (ox, oy))
        images[name], masks[name] = rgb, mask
        placements.append({
            "name": name,
            "nativeXYZ": panel["nativeOriginXYZ"],
            "nativeOffsetXY": [ox, oy],
            "sourceSha256": v206.SOURCE_SHA256[name],
            "footprintLonLat": panel["footprintLonLat"],
            "pixelsNeverResampled": True,
            "maskedPixelsTransparent": True,
        })
    require(atlas.getpixel((0, 800)) == (0, 0, 0, 0),
            "unsurveyed southwest source area must remain transparent")
    seams = {
        "westToMatrei": seam_stats(images[ORDER[0]], images[ORDER[1]],
                                    masks[ORDER[0]], masks[ORDER[1]], "vertical"),
        "matreiToSouth": seam_stats(images[ORDER[1]], images[ORDER[2]],
                                    masks[ORDER[1]], masks[ORDER[2]], "horizontal"),
    }
    return atlas, placements, seams


def contact(atlas):
    # Diagnostic overlay only; no label or checkerboard becomes source art.
    sheet = Image.new("RGBA", (1024, 1102), (35, 28, 28, 255))
    sheet.alpha_composite(atlas, (0, 0))
    d = ImageDraw.Draw(sheet)
    for x, y, label in ((0, 0, "WEST"), (512, 0, "MATREI REFERENCE"),
                        (512, 512, "SOUTH")):
        d.rectangle((x, y, x + 511, y + 511), outline=(237, 193, 117, 255), width=2)
        d.rectangle((x + 8, y + 8, x + 170, y + 26), fill=(19, 35, 29, 225))
        d.text((x + 13, y + 11), label, fill=(255, 239, 204, 255))
    d.text((16, 1041), "MODERN SOURCE ONLY / TRANSPARENT = QUARANTINED OR UNKNOWN; NO INPAINTING",
           fill=(255, 234, 198, 255))
    d.text((16, 1061), "NOT REGISTERED TO V123 / NOT 1780 TERRAIN / NOT PLAYABLE ART",
           fill=(255, 234, 198, 255))
    d.text((16, 1081), "Datenquelle: basemap.at / CC BY 4.0", fill=(255, 234, 198, 255))
    return sheet.convert("RGB")


def expected(folder):
    original, _ = read_sources(folder)
    _, placements, seams = compose(folder)
    return {
        "version": 215,
        "purpose": "Three contiguous source-native modern Alpine panels; NOT playable game art",
        "site": "V205 forest source ~3.578km from independent Matrei reference",
        "sourceManifestSha256": digest(Path(folder) / "manifest.json"),
        "projection": "EPSG:3857",
        "sourceImagePixels": list(SIZE),
        "sourcePanelsGeographicallyContiguous": original["sourcePanelsGeographicallyContiguous"],
        "southwestUnsurveyedAndTransparent": True,
        "allRetainedPixelsBitIdenticalToDecodedSource": True,
        "maskedRGBAndAlphaZero": True,
        "modernFeaturesMayRemainOutsideReviewedExclusions": True,
        "provider": "basemap.at",
        "license": "CC BY 4.0",
        "requiredAttribution": "Datenquelle: basemap.at",
        "nativePanels": placements,
        "nativeSourceSeamDiagnostics": seams,
        "sourceAtlasFile": "v215-native-source-seam-atlas.png",
        "reviewContactFile": "v215-native-source-seam-contact.png",
        **{flag: False for flag in FALSE_FLAGS},
    }


def build(folder, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    atlas, _, _ = compose(folder)
    manifest = expected(folder)
    atlas.save(output / manifest["sourceAtlasFile"])
    contact(atlas).save(output / manifest["reviewContactFile"])
    manifest["sourceAtlasSha256"] = digest(output / manifest["sourceAtlasFile"])
    manifest["reviewContactSha256"] = digest(output / manifest["reviewContactFile"])
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify(folder, output)
    return manifest


def verify(folder, output):
    output = Path(output)
    manifest = json.loads((output / "manifest.json").read_text())
    control = expected(folder)
    require(set(manifest) == set(control) | {"sourceAtlasSha256", "reviewContactSha256"},
            "unexpected native atlas metadata")
    for key, value in control.items():
        require(manifest.get(key) == value, "native geography/approval metadata changed: " + key)
    image_path = output / control["sourceAtlasFile"]
    contact_path = output / control["reviewContactFile"]
    require(image_path.is_file() and digest(image_path) == manifest["sourceAtlasSha256"],
            "native atlas image missing or altered")
    require(contact_path.is_file() and digest(contact_path) == manifest["reviewContactSha256"],
            "native atlas visual evidence missing or altered")
    original, _, _ = compose(folder)
    with Image.open(image_path) as im:
        require(im.mode == "RGBA" and im.size == SIZE and im.tobytes() == original.tobytes(),
                "native atlas differs from exact masked source RGB/alpha")
    with Image.open(contact_path) as im:
        require(im.convert("RGB").tobytes() == contact(original).tobytes(),
                "source seam contact image differs from independently rendered review")
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
    print("V215 native source atlas verified; playable West/South game art remains UNAPPROVED")


if __name__ == "__main__":
    main()
