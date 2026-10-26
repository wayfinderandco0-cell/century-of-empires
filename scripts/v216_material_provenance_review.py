#!/usr/bin/env python3
"""V216: inspect actual native-resolution Alpine assets without passing them off as game art.

V94 = Europe overview; V97 = shaded Copernicus-derived relief;
V102 = PROCEDURAL/illustrative material; V215 = modern native aerial imagery.
This tool does not stretch, warp, fill masks, add roads, or change playable terrain.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

import v204_contiguous_matrei_sources as source
import v215_native_source_seam_atlas as native

ROOT = Path(__file__).resolve().parents[1]
CELL = 512
LABEL = 44
HEADER = 68
FOOTER = 86
FALSE_FLAGS = (
    "sourceRegisteredToV123", "historicalRoadsVerified", "bridgeBanksVerified",
    "gameArtApproved", "physicalIPhoneApproved", "productionApproved",
    "periodSafe", "v102IsPhotographic", "v94IsCloseupTerrain",
    "v97VerifiesBridgeBanks", "sourceAtlasIsGameGeography",
)

def require(ok, why):
    if not ok:
        raise ValueError(why)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def manifests(root, atlas):
    v94 = json.loads((root / "terrain-v94/manifest.json").read_text())
    v97 = json.loads((root / "terrain-v97/manifest.json").read_text())
    v102 = json.loads((root / "terrain-v102/manifest.json").read_text())
    v215 = json.loads((atlas / "manifest.json").read_text())
    require(v94["projection"] == "equirectangular" and v94["atlasSize"] == [8192, 6144],
            "V94 continent-wide source identity changed")
    require(v97["elevationSource"] == "Copernicus DEM GLO-30 Public 2021"
            and v97["imageSize"] == [1552, 1782], "V97 DEM/relief source changed")
    require(v102["broadBoundsLonLat"] == v97["boundsLonLat"]
            and v102["sources"]["art"].startswith("Original deterministic material")
            and "Illustrative" in v102["sources"]["path"],
            "V102 must be identified as illustrative, NOT photography or surveyed roads")
    require(v215["projection"] == "EPSG:3857"
            and v215["sourceImagePixels"] == [1024, 1024]
            and v215["sourcePanelsGeographicallyContiguous"] is True
            and v215["allRetainedPixelsBitIdenticalToDecodedSource"] is True,
            "V215 original modern source evidence changed")
    require(all(v215.get(k) is False for k in native.FALSE_FLAGS),
            "V215 must not claim geographic, historical or game-art approval")
    return v94, v97, v102, v215

def specs(root, atlas):
    v94, v97, v102, v215 = manifests(root, atlas)
    return [
        ("V94 EUROPE / MAP OVERVIEW", root / "terrain-v94/overview.webp",
         "continent overview / not close-up", False, None),
        ("V97 COPERNICUS / RELIEF", root / "terrain-v97/brenner-relief.webp",
         "shaded modern DEM / not a photo", False, None),
        ("V102 NAVIS / PROCEDURAL", root / "terrain-v102/navis-material.webp",
         "illustrative tree/ground art", False, None),
        ("V215 WEST / MODERN AERIAL", atlas / v215["sourceAtlasFile"],
         "native source / exclusions transparent", True, (0, 0, 512, 512)),
        ("V215 CENTER / MODERN AERIAL", atlas / v215["sourceAtlasFile"],
         "NOT original Matrei painting", True, (512, 0, 1024, 512)),
        ("V215 SOUTH / MODERN AERIAL", atlas / v215["sourceAtlasFile"],
         "NOT registered to V123 roads", True, (512, 512, 1024, 1024)),
    ]

def native_crop(image, rect=None):
    require(image.width >= CELL and image.height >= CELL,
            "asset too small for native 512px study; never upscale")
    if rect is None:
        x = (image.width - CELL) // 2
        y = (image.height - CELL) // 2
        rect = (x, y, x + CELL, y + CELL)
    x0, y0, x1, y1 = rect
    require(x1-x0 == CELL and y1-y0 == CELL
            and 0 <= x0 < x1 <= image.width and 0 <= y0 < y1 <= image.height,
            "invalid unresampled native crop")
    return image.crop(rect), list(rect)

def draw_contact(root, atlas):
    entries = []
    w, h = CELL * 3, HEADER + (CELL + LABEL) * 2 + FOOTER
    sheet = Image.new("RGB", (w, h), (19, 30, 27))
    d = ImageDraw.Draw(sheet)
    d.text((18, 14), "V216 / NATIVE-PIXEL SOURCE STUDY / NOT PLAYABLE GAME ART",
           fill=(255, 231, 187))
    d.text((18, 37), "Same 512-pixel crop size, DIFFERENT geographic scale and source truth",
           fill=(210, 217, 204))
    for idx, (name, path, note, photographic, rect) in enumerate(specs(root, atlas)):
        require(path.is_file(), "missing pinned terrain source: " + str(path))
        with Image.open(path) as im:
            original_size = list(im.size)
            if idx == 0:
                require(im.size == (1448, 1086), "V94 overview pixels changed")
            if idx == 1:
                require(im.size == (1552, 1782), "V97 relief pixels changed")
            if idx == 2:
                require(im.size == (2048, 2048), "V102 material pixels changed")
            if idx >= 3:
                require(im.size == (1024, 1024) and im.mode == "RGBA",
                        "V215 source atlas lost native RGBA masks")
            patch, crop = native_crop(im, rect)
            px, py = (idx % 3) * CELL, HEADER + (idx // 3) * (CELL + LABEL)
            if idx >= 3:
                require(patch.mode == "RGBA", "modern source mask lost")
                # Diagnostic background, not a pixel replacement in source.
                backdrop = Image.new("RGB", patch.size, (31, 25, 25))
                backdrop.paste(patch.convert("RGB"), (0, 0), patch.getchannel("A"))
                sheet.paste(backdrop, (px, py))
                transparent = sum(1 for a in patch.getchannel("A").getdata() if a == 0)
                require(transparent > 0, "modern exclusions unexpectedly missing")
            else:
                sheet.paste(patch.convert("RGB"), (px, py))
                transparent = 0
            d.rectangle((px, py, px + CELL - 1, py + CELL - 1),
                        outline=(216, 185, 125), width=2)
            d.text((px + 10, py + CELL + 5), name, fill=(255, 228, 179))
            d.text((px + 10, py + CELL + 23), note, fill=(203, 219, 202))
            entries.append({
                "label": name, "sourceFile": str(path.relative_to(root)) if path.is_relative_to(root)
                            else path.name,
                "sourceSha256": sha(path), "originalPixels": original_size,
                "cropXYXY": crop, "cropNeverResampled": True,
                "nativePhotographicModernSource": photographic,
                "verified1780Landscape": False, "registeredToV123": False,
                "transparentQuarantinedPixelsInCrop": transparent,
            })
    y = h - FOOTER + 9
    d.text((18, y), "V102 is algorithmically painted, NOT an aerial photograph. V97 is relief, NOT bridge-bank evidence.",
           fill=(255, 214, 162))
    d.text((18, y + 21), "V215 is genuine modern photography ~3.578 km from the Matrei reference; NOT the V123 game location.",
           fill=(255, 214, 162))
    d.text((18, y + 42), "No warp / no invented roads / no period claim. Modern imagery: Datenquelle: basemap.at / CC BY 4.0",
           fill=(211, 219, 205))
    return sheet, entries

def expected(root, atlas):
    source.verify_source_invariants("forest")
    _, _, _, v215 = manifests(root, atlas)
    sheet, entries = draw_contact(root, atlas)
    return sheet, {
        "version": 216,
        "purpose": "Native-resolution provenance study; not a playable game-art change",
        "sourceAtlasSha256": v215["sourceAtlasSha256"],
        "sourceAtlasManifestSha256": sha(atlas / "manifest.json"),
        "sources": entries,
        "unmodifiedOriginalV121PhotoAndV123RoadGraph": True,
        "noImageStretchOrSyntheticDetail": True,
        "differentSourceFramesNotClaimedEquivalent": True,
        "nativePhotoNotAutomaticallyHistorical": True,
        "contactFile": "v216-native-provenance-contact.png",
        "license": "V215 modern basemap.at CC BY 4.0",
        **{flag: False for flag in FALSE_FLAGS},
    }

def build(root, atlas, output):
    native.verify(root / "qa/v216-native-source", atlas)
    sheet, manifest = expected(root, atlas)
    output.mkdir(parents=True, exist_ok=True)
    sheet.save(output / manifest["contactFile"])
    manifest["contactSha256"] = sha(output / manifest["contactFile"])
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify(root, atlas, output)
    return manifest

def verify(root, atlas, output):
    native.verify(root / "qa/v216-native-source", atlas)
    sheet, control = expected(root, atlas)
    stored = json.loads((output / "manifest.json").read_text())
    require(set(stored) == set(control) | {"contactSha256"},
            "unexpected provenance or approval fields")
    for key, value in control.items():
        require(stored.get(key) == value, "source provenance/approval altered: " + key)
    path = output / control["contactFile"]
    require(path.is_file() and sha(path) == stored.get("contactSha256"),
            "contact hash changed")
    with Image.open(path) as actual:
        require(actual.mode == "RGB" and actual.size == sheet.size
                and actual.tobytes() == sheet.tobytes(),
                "visual source comparison changed")
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--atlas", type=Path, default=ROOT / "qa/v216-native-atlas")
    p.add_argument("--output", type=Path, default=ROOT / "qa/v216-provenance")
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    if a.verify:
        verify(a.root, a.atlas, a.output)
    else:
        build(a.root, a.atlas, a.output)
    print("V216 native source study verified; game artwork, geography, roads remain NOT APPROVED")

if __name__ == "__main__":
    main()
