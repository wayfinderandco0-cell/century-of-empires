#!/usr/bin/env python3
"""V218: quarantine visually identified modern features in four V217 source panels.

Research-only modern basemap.at material. 0 alpha means UNKNOWN/UNUSABLE, never
inpainted. Nothing is registered to V121/V123 or accepted as 1780 terrain.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw
import v217_matrei_nearby_native_scout as scout

ROOT = Path(__file__).resolve().parents[1]
SIZE = 512
# Reviewed against the ACTUAL V217 1600x1935 source contact, not synthetic tiles.
# Rectangles are half-open [left,top,right,bottom]; polygons use native pixels.
# The masks are deliberately overinclusive, NOT a claim that everything else
# is free of modern structures, forestry, dates or altered land use.
REGIONS = {
    3: {
        "dates": [[0, 143, 34, 181], [291, 143, 350, 181],
                  [0, 461, 34, 503], [291, 461, 351, 504]],
        "modernStructures": [[388, 321, 436, 373]],
        "modernClearings": [],
    },
    5: {
        "dates": [[37, 143, 96, 180], [358, 143, 417, 181],
                  [37, 460, 96, 505], [358, 460, 417, 505]],
        "modernStructures": [],
        "modernClearings": [
            [[0, 0], [116, 0], [176, 52], [216, 73], [293, 73],
             [314, 192], [244, 251], [166, 247], [76, 199], [0, 208]],
        ],
    },
    6: {
        "dates": [[0, 13, 35, 53], [293, 13, 351, 53],
                  [0, 330, 35, 374], [293, 330, 351, 375]],
        "modernStructures": [],
        "modernClearings": [
            [[20, 171], [83, 143], [179, 167], [249, 218],
             [200, 282], [86, 303], [17, 252]],
        ],
    },
    8: {
        "dates": [[37, 13, 97, 53], [358, 13, 418, 53],
                  [37, 331, 97, 375], [358, 331, 418, 375]],
        "modernStructures": [[451, 323, 500, 378]],
        "modernClearings": [
            [[316, 512], [341, 469], [391, 438], [434, 426],
             [467, 404], [512, 398], [512, 512]],
        ],
    },
}
FLAGS = ("registeredToV121", "registeredToV123", "historicalRoadsVerified",
         "allModernFeaturesExcluded", "periodSafe", "gameArtApproved",
         "physicalIPhoneApproved", "productionApproved")
FIELDS = ("siteId", "siteIndex", "originXYZ", "sourceFootprintLonLat",
          "sourceTiles", "reviewedMasks", "originalFile", "maskFile", "quarantineFile")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(ok, why):
    if not ok:
        raise ValueError(why)

def plan():
    source = scout.plan()
    sites = []
    for i in REGIONS:
        s = source["sites"][i]
        sites.append({
            "siteId": s["id"], "siteIndex": i,
            "originXYZ": s["nativeOriginXYZ"],
            "sourceFootprintLonLat": s["footprintLonLat"],
            "sourceTiles": [{"xyz": t["xyz"], "url": t["url"], "name": t["name"]}
                            for t in s["tiles"]],
            "reviewedMasks": REGIONS[i],
            "originalFile": f"site-{i:02d}-original.png",
            "maskFile": f"site-{i:02d}-quarantine-mask.png",
            "quarantineFile": f"site-{i:02d}-quarantined.png",
        })
    return {
        "version": 218,
        "purpose": "Conservative visible-modern-feature quarantine, research ONLY",
        "source": "basemap.at modern 2023 aerial; CC BY 4.0; Datenquelle: basemap.at",
        "projection": "EPSG:3857", "nativeSize": [SIZE, SIZE],
        "sourceGapsRemainUnknown": True,
        "maskMeaning": "alpha=0 is excluded/unknown, NOT inpainted",
        "remainingModernFeaturesMayExist": True,
        "siteIndices": list(REGIONS),
        "sites": sites, **{f: False for f in FLAGS},
    }

def mask_for(site):
    mask = Image.new("L", (SIZE, SIZE), 255)
    d = ImageDraw.Draw(mask)
    for label in ("dates", "modernStructures"):
        for x0, y0, x1, y1 in site["reviewedMasks"][label]:
            require(0 <= x0 < x1 <= SIZE and 0 <= y0 < y1 <= SIZE,
                    "invalid quarantine rectangle")
            d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=0)
    for points in site["reviewedMasks"]["modernClearings"]:
        require(len(points) >= 3 and all(0 <= x <= SIZE and 0 <= y <= SIZE
                                         for x, y in points), "invalid polygon")
        d.polygon(points, fill=0)
    return mask

def quarantined(rgb, mask):
    require(rgb.mode == "RGB" and rgb.size == (SIZE, SIZE), "native RGB required")
    require(mask.mode == "L" and mask.size == (SIZE, SIZE), "native mask required")
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.paste(rgb.convert("RGBA"), (0, 0), mask)
    return out

def contact(sites, folder):
    # Original left, quarantined right. Black is unavailable, not restored art.
    out = Image.new("RGB", (SIZE * 2, 76 + (SIZE + 46) * len(sites) + 55),
                    (17, 27, 25))
    d = ImageDraw.Draw(out)
    d.text((10, 9), "V218 REAL 2023 SOURCE: ORIGINAL / QUARANTINED", fill=(255, 225, 176))
    d.text((10, 31), "BLACK = EXCLUDED / UNKNOWN. NOT 1780. NOT GAME ART. NOT V123 REGISTERED.",
           fill=(235, 216, 182))
    for j, site in enumerate(sites):
        y = 76 + j * (SIZE + 46)
        with Image.open(folder / site["originalFile"]) as src:
            out.paste(src.convert("RGB"), (0, y))
        with Image.open(folder / site["quarantineFile"]) as src:
            # Transparent pixels must show as black, not invented foliage.
            out.paste(src.convert("RGB"), (SIZE, y))
        d.text((10, y + SIZE + 9),
               f"{site['siteId']} | LEFT original / RIGHT visible-feature quarantine; modern source only",
               fill=(225, 221, 185))
    d.text((10, out.height - 36),
           "Datenquelle: basemap.at | CC BY 4.0 | unresolved modern features remain",
           fill=(245, 220, 177))
    return out

def source_site(site, folder):
    reference = scout.plan()["sites"][site["siteIndex"]]
    for got, expected in zip(site["sourceTiles"], reference["tiles"]):
        require(all(got[k] == expected[k] for k in ("xyz", "url", "name")),
                "source tile identity changed")
        original = (folder / got["name"]).read_bytes()
        require(sha(original) == got["sha256"] and len(original) == got["byteCount"],
                "source JPEG bytes changed")
        scout.native_jpeg(original)
    # v217.assemble checks the native JPEG identity and copies pixels unresized.
    for got, expected in zip(site["sourceTiles"], reference["tiles"]):
        expected["sha256"], expected["byteCount"] = got["sha256"], got["byteCount"]
    return scout.assemble(reference, folder)

def verify_plan(manifest):
    expected = plan()
    require(set(manifest) == set(expected) | {"contactFile", "contactSha256"},
            "manifest fields changed")
    for k in expected:
        if k != "sites":
            require(manifest[k] == expected[k], "unverified approval/geography: " + k)
    require(len(manifest["sites"]) == len(expected["sites"]), "site count changed")
    dynamic = {"sourceSha256", "maskSha256", "quarantineSha256",
               "sourcePixelsSha256", "retainedPixels", "excludedPixels"}
    for got, pinned in zip(manifest["sites"], expected["sites"]):
        require(set(got) == set(pinned) | dynamic, "site metadata fields changed")
        for k in FIELDS:
            if k == "sourceTiles":
                continue
            require(got[k] == pinned[k], "site geometry/masks changed: " + k)
        require(len(got["sourceTiles"]) == 4, "four native JPEGs required")
        for a, b in zip(got["sourceTiles"], pinned["sourceTiles"]):
            require(set(a) == set(b) | {"sha256", "byteCount"},
                    "unexpected source tile metadata")
            for k in b:
                require(a[k] == b[k], "source tile identity changed")
    return True

def verify(folder):
    manifest = json.loads((folder / "manifest.json").read_text())
    verify_plan(manifest)
    for site in manifest["sites"]:
        source = source_site(site, folder)
        require(sha(source.tobytes()) == site["sourcePixelsSha256"],
                "source decoded RGB changed")
        mask = mask_for(site)
        out = quarantined(source, mask)
        excluded = SIZE * SIZE - sum(1 for value in mask.getdata() if value)
        require(excluded == site["excludedPixels"] and
                SIZE * SIZE - excluded == site["retainedPixels"] and
                0 < excluded < SIZE * SIZE, "quarantine coverage changed")
        for path_key, expected, hash_key in (
            ("originalFile", source, "sourceSha256"),
            ("maskFile", mask, "maskSha256"),
            ("quarantineFile", out, "quarantineSha256"),
        ):
            p = folder / site[path_key]
            require(sha(p.read_bytes()) == site[hash_key], "image hash changed: " + path_key)
            with Image.open(p) as actual:
                require(actual.mode == expected.mode and actual.size == expected.size
                        and actual.tobytes() == expected.tobytes(),
                        "image pixels changed: " + path_key)
    preview = contact(manifest["sites"], folder)
    path = folder / manifest["contactFile"]
    require(sha(path.read_bytes()) == manifest["contactSha256"],
            "contact bytes changed")
    with Image.open(path) as im:
        require(im.mode == "RGB" and im.size == preview.size and
                im.tobytes() == preview.tobytes(), "contact pixels changed")
    return True

def build(folder):
    scout.v204.verify_source_invariants("matrei")
    folder.mkdir(parents=True, exist_ok=True)
    manifest = plan()
    for site in manifest["sites"]:
        reference = scout.plan()["sites"][site["siteIndex"]]
        scout.download(folder, {"sites": [reference]})
        for a, b in zip(site["sourceTiles"], reference["tiles"]):
            a["sha256"], a["byteCount"] = b["sha256"], b["byteCount"]
        rgb = source_site(site, folder)
        mask = mask_for(site)
        out = quarantined(rgb, mask)
        for key, im, digest in (
            ("originalFile", rgb, "sourceSha256"),
            ("maskFile", mask, "maskSha256"),
            ("quarantineFile", out, "quarantineSha256"),
        ):
            im.save(folder / site[key])
            site[digest] = sha((folder / site[key]).read_bytes())
        site["sourcePixelsSha256"] = sha(rgb.tobytes())
        site["retainedPixels"] = sum(1 for v in mask.getdata() if v)
        site["excludedPixels"] = SIZE * SIZE - site["retainedPixels"]
    manifest["contactFile"] = "v218-original-versus-quarantine.png"
    preview = contact(manifest["sites"], folder)
    preview.save(folder / manifest["contactFile"])
    manifest["contactSha256"] = sha((folder / manifest["contactFile"]).read_bytes())
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify(folder)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=ROOT / "qa/v218-modern-quarantine")
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    verify(args.output) if args.verify else build(args.output)
    print("V218 native modern-feature quarantine verified; game/1780 approval FALSE")

if __name__ == "__main__":
    main()
