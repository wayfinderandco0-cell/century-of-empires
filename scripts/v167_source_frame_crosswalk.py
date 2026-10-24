#!/usr/bin/env python3
"""V167: source-pixel coordinate review sheets. NO V121-to-geography fit.

The V102 *alpine* material uses BROAD V97 bounds (1536 square), while
V102 *navis* material uses NARROW Navis bounds (2048 square). Confusing
those rasters would put future landmarks kilometres from their true
source coordinates. Render original images with labelled pixel/geographic
grids so independent matches can be reviewed without inventing them.
"""
import argparse
import base64
import hashlib
import io
import json
import math
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

V121_GIT_BLOB = "4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382"
SOURCES = {
    "v97-relief": ("terrain-v97/brenner-relief.webp", (1552, 1782), "broad"),
    "v102-alpine": ("terrain-v102/alpine-material.webp", (1536, 1536), "broad"),
    "v102-navis": ("terrain-v102/navis-material.webp", (2048, 2048), "narrow"),
}
MATREI_ORIGIN = (1536, 0)
GRID_STEP = 256

def require(ok, message):
    if not ok:
        raise ValueError(message)

def bounds(value):
    require(isinstance(value, list) and len(value) == 4 and
            all(type(v) in (int, float) and math.isfinite(v) for v in value),
            "invalid lon/lat bounds")
    west, south, east, north = value
    require(-180 <= west < east <= 180 and -90 <= south < north <= 90,
            "invalid geographic extent")
    return tuple(value)

def source_specs(v97, v102):
    broad = bounds(v97["boundsLonLat"])
    require(broad == bounds(v102["broadBoundsLonLat"]),
            "V97 and V102 BROAD bounds disagree")
    narrow = bounds(v102["boundsLonLat"])
    require(broad[0] < narrow[0] < narrow[2] < broad[2] and
            broad[1] < narrow[1] < narrow[3] < broad[3],
            "V102 Navis bounds are not contained within broad relief")
    require(v97["imageSize"] == [1552, 1782],
            "V97 relief dimensions changed")
    require(v102["version"] == 102, "wrong V102 source manifest")
    return {"broad": broad, "narrow": narrow}

def pixel_to_lonlat(x, y, size, extent):
    w, h = size
    require(w > 1 and h > 1 and 0 <= x <= w - 1 and 0 <= y <= h - 1,
            "pixel outside source raster")
    west, south, east, north = extent
    return (west + x / (w - 1) * (east - west),
            north - y / (h - 1) * (north - south))

def lonlat_to_pixel(lon, lat, size, extent):
    west, south, east, north = extent
    require(west <= lon <= east and south <= lat <= north,
            "coordinate outside source geography")
    return ((lon - west) / (east - west) * (size[0] - 1),
            (north - lat) / (north - south) * (size[1] - 1))

def original_matrei(html):
    raw = html.encode("utf-8")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()
    require(blob == V121_GIT_BLOB, "original V121 HTML git blob changed")
    found = re.findall(r"""src\\s*=\\s*["']data:image/webp;base64,([A-Za-z0-9+/=]+)["']""", html)
    require(len(found) == 1, "expected exactly one V121 embedded painting")
    binary = base64.b64decode(found[0], validate=True)
    with Image.open(io.BytesIO(binary)) as im:
        require(im.format == "WEBP" and im.size == (1536, 1024),
                "original Matrei painting format/dimensions changed")
        return im.convert("RGB")

def make_sheet(image, label, extent=None, origin=None, max_width=1050):
    require(image.mode == "RGB", "expected RGB source")
    w, h = image.size
    scale = min(1.0, max_width / w)
    sheet = image.resize((round(w * scale), round(h * scale)),
                         Image.Resampling.LANCZOS)
    footer = 76
    result = Image.new("RGB", (sheet.width, sheet.height + footer), "#16211d")
    result.paste(sheet, (0, 0))
    d = ImageDraw.Draw(result)
    font = ImageFont.load_default()
    for x in range(0, w, GRID_STEP):
        xx = round(x * scale)
        d.line((xx, 0, xx, sheet.height - 1), fill="#fff2a8", width=1)
        text = str(x + (origin[0] if origin else 0))
        d.text((xx + 3, 4), text, font=font, fill="#ffffff",
               stroke_width=1, stroke_fill="#000000")
    for y in range(0, h, GRID_STEP):
        yy = round(y * scale)
        d.line((0, yy, sheet.width - 1, yy), fill="#fff2a8", width=1)
        text = str(y + (origin[1] if origin else 0))
        d.text((4, yy + 12), text, font=font, fill="#ffffff",
               stroke_width=1, stroke_fill="#000000")
    d.text((8, sheet.height + 7), label, font=font, fill="#f5e2a6")
    if extent:
        nw = pixel_to_lonlat(0, 0, (w, h), extent)
        se = pixel_to_lonlat(w - 1, h - 1, (w, h), extent)
        d.text((8, sheet.height + 26),
               f"NW {nw[0]:.5f} E, {nw[1]:.5f} N  |  SE {se[0]:.5f} E, {se[1]:.5f} N",
               font=font, fill="#eeeeee")
    else:
        d.text((8, sheet.height + 26),
               "World pixels only; no geographic tie points verified",
               font=font, fill="#eeeeee")
    d.text((8, sheet.height + 48),
           "REVIEW AID ONLY: no matched landmarks, roads, bridge or art approved",
           font=font, fill="#ffb0a0")
    return result

def produce(root, out):
    root, out = Path(root), Path(out)
    v97 = json.loads((root / "terrain-v97/manifest.json").read_text())
    v102 = json.loads((root / "terrain-v102/manifest.json").read_text())
    extents = source_specs(v97, v102)
    art = original_matrei((root / "v121-octagon-1-painted-road.html").read_text())
    out.mkdir(parents=True, exist_ok=True)
    name = "v121-matrei-GAME-UNREGISTERED.png"
    make_sheet(art, "V121 MATREI illustrative game painting",
               origin=MATREI_ORIGIN).save(out / name)
    reports = {}
    for source_id, (path, expected, scope) in SOURCES.items():
        with Image.open(root / path) as src:
            require(src.format == "WEBP" and src.size == expected,
                    f"{source_id}: image format/dimensions changed")
            rgb = src.convert("RGB")
        extent = extents[scope]
        filename = source_id + "-SOURCE-geographic.png"
        make_sheet(rgb, source_id + " MODERN geographic source",
                   extent=extent).save(out / filename)
        # Verify the actual corner and centre pixel mapping in both directions.
        for xy in ((0, 0), (expected[0] - 1, expected[1] - 1),
                   ((expected[0] - 1) / 2, (expected[1] - 1) / 2)):
            lonlat = pixel_to_lonlat(*xy, expected, extent)
            roundtrip = lonlat_to_pixel(*lonlat, expected, extent)
            require(math.dist(xy, roundtrip) < 1e-7,
                    f"{source_id}: pixel-geography roundtrip failed")
        reports[source_id] = {
            "image": path, "size": list(expected), "boundsLonLat": list(extent),
            "boundsType": scope, "reviewSheet": filename,
            "imageGitBlobSha1": hashlib.sha1(
                b"blob " + str((root / path).stat().st_size).encode() + b"\\0" +
                (root / path).read_bytes()).hexdigest(),
            "sourcePixelsGeographicallyLocated": True,
            "matchedGameLandmarks": 0,
        }
    report = {
        "version": 167, "purpose": "Source-coordinate review only",
        "gamePaintingReviewSheet": name,
        "gamePaintingWorldOrigin": list(MATREI_ORIGIN),
        "gamePaintingGeographicallyRegistered": False,
        "gameSourceTiePoints": [],
        "sourceFrames": reports,
        "historicalRoadsVerified": False, "bridgeBanksVerified": False,
        "westSouthGameArtComplete": False, "physicalIPhoneApproved": False,
        "productionApproved": False,
        "warning": "V102 alpine uses BROAD V97 extent; V102 navis uses NARROW Navis extent. Never conflate their pixels or treat modern geography as 1780 game art."
    }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\\n")
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--output", default="qa/v167-source-crosswalk")
    args = p.parse_args()
    result = produce(args.root, args.output)
    print("V167 source review sheets:", len(result["sourceFrames"]),
          "modern sources; 0 game/geography landmarks; NOT APPROVED")

if __name__ == "__main__":
    main()
