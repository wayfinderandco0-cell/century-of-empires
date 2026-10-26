#!/usr/bin/env python3
"""V207: conservative visible-modern-feature exclusions on native V205 aerial sources.

These masks are manually traced from the actual V205 512px source panels.
They are deliberately NOT a historical reconstruction, game registration,
period-safe forest survey, road survey, or image inpainting.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
import v204_contiguous_matrei_sources as source
import v206_audited_natural_cover as v206

SIZE = 512
# Coordinates are native pixels in the source panels, NOT V123 game pixels.
# Each polyline is a visibly modern track with a deliberately wide buffer.
# Each rectangle covers a visible year imprint or a conservatively uncertain
# modern clearing. A mask of 0 means "quarantined", never "empty terrain".
ANNOTATIONS = {
    "west_reference": {
        "paths": [
            {"width": 28, "xy": [[0, 397], [50, 402], [105, 391], [165, 354],
                                   [222, 314], [280, 273], [345, 250],
                                   [416, 216], [512, 160]]},
            {"width": 18, "xy": [[0, 52], [50, 87], [110, 128], [155, 176],
                                   [199, 228], [255, 254], [305, 263]]},
        ],
        "rects": [[42, 342, 77, 368], [361, 341, 401, 367],
                  [13, 17, 43, 44]],
        "knownExcluded": [[20, 397], [310, 263], [100, 120], [55, 354]],
        "knownRetained": [[400, 450], [350, 100]],
    },
    "matrei_reference": {
        # Open clearing contains possible modern forestry traces. Quarantine
        # rather than asserting that a meadow represents vegetation in 1780.
        "paths": [],
        "rects": [[0, 0, 512, 184], [169, 339, 209, 365],
                  [489, 339, 512, 365]],
        "knownExcluded": [[90, 90], [185, 351], [500, 351]],
        "knownRetained": [[100, 400], [300, 420]],
    },
    "south_reference": {
        "paths": [
            {"width": 31, "xy": [[0, 264], [42, 233], [92, 195], [150, 152],
                                   [210, 137], [265, 121], [299, 105],
                                   [316, 128], [297, 156], [252, 167],
                                   [211, 200], [161, 261], [157, 302],
                                   [173, 340]]},
            {"width": 30, "xy": [[47, 512], [50, 478], [82, 451], [137, 425],
                                   [194, 397], [241, 358], [273, 337],
                                   [333, 323]]},
        ],
        "rects": [[174, 469, 213, 495], [489, 147, 512, 173]],
        "knownExcluded": [[285, 125], [160, 310], [50, 480],
                          [188, 480], [500, 160]],
        "knownRetained": [[390, 410], [400, 40]],
    },
}
FALSE_FLAGS = (
    "sourceRegisteredToV123", "periodSafe", "historicalVegetationVerified",
    "allModernFeaturesExcluded", "historicalRoadsVerified",
    "bridgeBanksVerified", "roadsAlignedToGame", "gameArtApproved",
    "physicalIPhoneApproved", "productionApproved",
)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def mask_for(name):
    require(name in ANNOTATIONS, "unknown native panel")
    mask = Image.new("L", (SIZE, SIZE), 255)
    d = ImageDraw.Draw(mask)
    a = ANNOTATIONS[name]
    for path in a["paths"]:
        d.line([tuple(xy) for xy in path["xy"]], fill=0,
               width=path["width"], joint="curve")
        r = path["width"] // 2
        for x, y in path["xy"]:
            d.ellipse((x-r, y-r, x+r, y+r), fill=0)
    for rect in a["rects"]:
        d.rectangle(tuple(rect), fill=0)
    for x, y in a["knownExcluded"]:
        require(mask.getpixel((x, y)) == 0,
                "visible modern feature not excluded: " + name)
    for x, y in a["knownRetained"]:
        require(mask.getpixel((x, y)) == 255,
                "native forest control unexpectedly masked: " + name)
    return mask

def plan(source_folder):
    original, panels = v206.inspect_source(source_folder)
    require(set(ANNOTATIONS) == set(panels), "native panel set changed")
    return {
        "version": 207,
        "purpose": "Audited source-native exclusions only; NOT historical or playable artwork",
        "sourceManifestSha256": sha(Path(source_folder) / "manifest.json"),
        "sourceSite": original["site"],
        "provider": "basemap.at",
        "license": "CC BY 4.0",
        "requiredAttribution": "Datenquelle: basemap.at",
        "annotationBasis": "Manual tracing of visible roads, year marks and uncertain clearing in inspected V205 contact",
        "maskSemantics": "0=quarantined modern/uncertain pixels; 255=retained modern source pixels; retained does NOT mean 1780-valid",
        "noInpaintingOrSynthesizedPixels": True,
        "nativeMasksNotGameOctagons": True,
        "panels": [{
            "name": name,
            "nativeOriginXYZ": panels[name]["nativeOriginXYZ"],
            "sourcePanelSha256": v206.SOURCE_SHA256[name],
            "annotations": ANNOTATIONS[name],
            "maskImage": name + "-excluded-mask.png",
            "candidateImage": name + "-source-alpha.png",
        } for name in ANNOTATIONS],
        **{k: False for k in FALSE_FLAGS},
    }

def render_panel(source_folder, panel, out):
    name = panel["name"]
    mask = mask_for(name)
    mask_path = out / panel["maskImage"]
    mask.save(mask_path)
    with Image.open(Path(source_folder) / (name + ".png")) as image:
        original = image.convert("RGB")
    require(original.size == (SIZE, SIZE), "source size changed")
    rgba = original.convert("RGBA")
    rgba.putalpha(mask)
    candidate_path = out / panel["candidateImage"]
    rgba.save(candidate_path)
    kept = sum(1 for v in mask.getdata() if v == 255)
    ratio = kept / (SIZE * SIZE)
    require(0.30 < ratio < 0.95, "suspicious excluded area ratio: " + name)
    panel["retainedFraction"] = round(ratio, 6)
    panel["maskSha256"] = sha(mask_path)
    panel["candidateSha256"] = sha(candidate_path)
    return original, mask

def make_contact(images, out):
    # Red shows quarantined source features; no new terrain is painted.
    sheet = Image.new("RGB", (1024, 1090), (16, 30, 26))
    positions = {"west_reference": (0, 0),
                 "matrei_reference": (512, 0),
                 "south_reference": (512, 512)}
    for name, (original, mask) in images.items():
        overlay = original.convert("RGBA")
        red = Image.new("RGBA", (SIZE, SIZE), (255, 30, 65, 120))
        excluded = mask.point(lambda x: 255 - x)
        red.putalpha(excluded.point(lambda x: 120 if x else 0))
        overlay.alpha_composite(red)
        sheet.paste(overlay.convert("RGB"), positions[name])
    d = ImageDraw.Draw(sheet)
    d.text((8, 1029), "RED = EXCLUDED MODERN / UNCERTAIN SOURCE. NO INPAINTING.", fill="#fff0ce")
    d.text((8, 1050), "Modern basemap.at / CC BY 4.0. NOT V123 GAME GEOGRAPHY OR 1780 FOREST.", fill="#fff0ce")
    target = out / "v207-exclusion-contact.png"
    sheet.save(target)
    return target

def build(source_folder, output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    manifest = plan(source_folder)
    images = {}
    for panel in manifest["panels"]:
        images[panel["name"]] = render_panel(source_folder, panel, output_folder)
    contact = make_contact(images, output_folder)
    manifest["contactImage"] = contact.name
    manifest["contactSha256"] = sha(contact)
    (output_folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify(source_folder, output_folder)
    return manifest

def verify(source_folder, output_folder):
    output_folder = Path(output_folder)
    actual = json.loads((output_folder / "manifest.json").read_text())
    expected = plan(source_folder)
    require(set(actual) == set(expected) | {"contactImage", "contactSha256"},
            "unexpected output metadata")
    for k, v in expected.items():
        if k != "panels":
            require(actual.get(k) == v, "changed source/approval flag: " + k)
    require(len(actual["panels"]) == len(expected["panels"]) == 3,
            "three original native panels required")
    images = {}
    for got, exp in zip(actual["panels"], expected["panels"]):
        require(set(got) == set(exp) | {"retainedFraction", "maskSha256", "candidateSha256"},
                "unexpected panel metadata")
        for k, v in exp.items():
            require(got.get(k) == v, "altered annotations or source: " + k)
        name = exp["name"]
        expected_mask = mask_for(name)
        mask_path = output_folder / exp["maskImage"]
        candidate_path = output_folder / exp["candidateImage"]
        require(mask_path.is_file() and candidate_path.is_file(),
                "missing native mask or candidate")
        require(got["maskSha256"] == sha(mask_path)
                and got["candidateSha256"] == sha(candidate_path),
                "changed native mask/candidate checksum")
        with Image.open(mask_path) as saved:
            require(saved.mode == "L" and saved.size == (SIZE, SIZE)
                    and saved.tobytes() == expected_mask.tobytes(),
                    "excluded mask geometry changed")
        with Image.open(Path(source_folder) / (name + ".png")) as src:
            rgb = src.convert("RGB")
        with Image.open(candidate_path) as candidate:
            rgba = candidate.convert("RGBA")
            require(candidate.mode == "RGBA" and candidate.size == (SIZE, SIZE)
                    and rgba.convert("RGB").tobytes() == rgb.tobytes()
                    and rgba.getchannel("A").tobytes() == expected_mask.tobytes(),
                    "candidate changed native source RGB or excluded alpha")
        retained = sum(1 for v in expected_mask.getdata() if v == 255) / (SIZE * SIZE)
        require(got["retainedFraction"] == round(retained, 6),
                "retained area metric changed")
        images[name] = (rgb, expected_mask)
    contact_path = output_folder / "v207-exclusion-contact.png"
    require(contact_path.is_file() and actual.get("contactSha256") == sha(contact_path),
            "review contact altered before regeneration")
    expected_contact = make_contact(images, output_folder)
    require(actual.get("contactImage") == expected_contact.name
            and actual.get("contactSha256") == sha(expected_contact),
            "review contact does not match native masks")
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
    print("V207 modern-source exclusion masks verified; GAME ART/1780 registration remains FALSE")

if __name__ == "__main__":
    main()
