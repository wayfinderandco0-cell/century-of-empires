#!/usr/bin/env python3
"""V158 source-frame material/colour study; NOT playable historical game art.

This is a *pixelwise* tonal reinterpretation of the verified V157 modern
source. It adds NO generated terrain, roads, structures, vegetation, or
repeated texture stamps. Unknown/modern-excluded pixels remain transparent.
The 3 sectors are modern Navis geographic SOURCE areas, not the three V123
game octagons. The 1780 landscape and game route transform remain unverified.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from PIL import Image

SIZE = (2304, 768)
SECTORS = ("source-west", "source-center", "source-east")
ATTRIBUTION = "Datenquelle: basemap.at"
NOT_APPROVED = {
    "gameOctagonsMapped": False,
    "gameRouteGeoregistered": False,
    "historic1780Certified": False,
    "historicalRoadEvidence": False,
    "bridgeBanksVerified": False,
    "modernInfrastructureCleared": False,
    "allModernFeaturesDetected": False,
    "periodArtComplete": False,
    "productionApproved": False,
    "manualArtReviewRequired": True,
}
# Per-channel monotonic LUT only: no geometry, blur, synthesized texture,
# spatial copying or fabricated historical feature. Entire 2304px source
# frame is transformed at once, so the sector boundaries cannot change it.
TONAL_LUT = ((94, 100, 10), (90, 100, 11), (78, 100, 13))

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_png(path, mode):
    with Image.open(path) as image:
        if image.format != "PNG" or image.mode != mode or image.size != SIZE:
            raise ValueError("Untrusted source/study PNG: " + str(path))
        return image.copy()

def retained_fractions(mask):
    if mask.mode != "L" or mask.size != SIZE or set(mask.getdata()) - {0, 255}:
        raise ValueError("Source mask must be binary and geographic-frame aligned")
    result = {}
    for i, name in enumerate(SECTORS):
        section = mask.crop((i * 768, 0, (i + 1) * 768, 768))
        ratio = round(section.histogram()[255] / (768 * 768), 6)
        if not 0.05 < ratio < 0.9:
            raise ValueError("Source sector coverage implausible: " + name)
        result[name] = ratio
    return result

def validate_source(source_dir):
    source_dir = Path(source_dir)
    m = json.loads((source_dir / "manifest.json").read_text())
    required = {
        "version": 157, "sourceVersion": 156, "pixelDimensions": list(SIZE),
        "sourceCrs": "EPSG:3857", "requiredAttribution": ATTRIBUTION,
        "license": "CC BY 4.0", "maskFile": "residual-modern-mask.png",
        "referenceFile": "residual-modern-reference.png",
        "exclusionAlphaMeaning": "0=excluded/unknown; 255=unreviewed modern source",
        **NOT_APPROVED,
    }
    for key, expected in required.items():
        if m.get(key) != expected:
            raise ValueError("Untrusted V157 source or forged approval: " + key)
    for key in ("maskSha256", "referenceSha256", "sourceMosaicSha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(m.get(key, ""))):
            raise ValueError("Missing source provenance: " + key)
    if set(m.get("sourceSectorRetainedFractions", {})) != set(SECTORS):
        raise ValueError("Untrusted source-sector inventory")
    for key, filename in (("maskSha256", m["maskFile"]),
                          ("referenceSha256", m["referenceFile"])):
        if digest(source_dir / filename) != m[key]:
            raise ValueError("V157 source file hash mismatch: " + filename)
    mask = read_png(source_dir / m["maskFile"], "L")
    rgba = read_png(source_dir / m["referenceFile"], "RGBA")
    if rgba.getchannel("A").tobytes() != mask.tobytes():
        raise ValueError("V157 source alpha does not match exclusions")
    if retained_fractions(mask) != m["sourceSectorRetainedFractions"]:
        raise ValueError("V157 source coverage does not match pixels")
    return m, rgba, mask

def period_palette_study(rgba, mask):
    if rgba.mode != "RGBA" or rgba.size != SIZE:
        raise ValueError("Invalid source RGBA")
    if rgba.getchannel("A").tobytes() != mask.tobytes():
        raise ValueError("Source mask mismatch")
    rgb = rgba.convert("RGB")
    channels = rgb.split()
    out = []
    for channel, (numerator, denominator, offset) in zip(channels, TONAL_LUT):
        lut = [max(0, min(255, (value * numerator + denominator // 2) // denominator + offset))
               for value in range(256)]
        out.append(channel.point(lut))
    styled = Image.merge("RGB", tuple(out)).convert("RGBA")
    styled.putalpha(mask)
    # Transparent RGB must also be zero: some PNG viewers ignore alpha, and
    # concealed modern roads/roofs must never leak into an art-study export.
    return Image.composite(styled, Image.new("RGBA", SIZE, (0, 0, 0, 0)), mask)

def expected_manifest(source):
    return {
        "version": 158,
        "purpose": "Nonrepeating pixelwise muted period-palette SOURCE study; not 1780 game art",
        "sourceVersion": 157,
        "sourceMosaicSha256": source["sourceMosaicSha256"],
        "sourceMaskSha256": source["maskSha256"],
        "sourceReferenceSha256": source["referenceSha256"],
        "pixelDimensions": list(SIZE),
        "sourceCrs": "EPSG:3857",
        "requiredAttribution": ATTRIBUTION,
        "license": "CC BY 4.0",
        "paletteLut": [list(x) for x in TONAL_LUT],
        "noSpatialCopyOrGeneratedFeatures": True,
        "unknownAlphaMeaning": "0=excluded/unknown, never automatically filled",
        "sourceSectorRetainedFractions": source["sourceSectorRetainedFractions"],
        "studyFile": "source-period-palette-study.png",
        "sectorFiles": {name: name + "-palette-study.png" for name in SECTORS},
        "gameOctagonsMapped": False,
        "gameRouteGeoregistered": False,
        "historic1780Certified": False,
        "historicalRoadEvidence": False,
        "bridgeBanksVerified": False,
        "modernInfrastructureCleared": False,
        "allModernFeaturesDetected": False,
        "periodArtComplete": False,
        "productionApproved": False,
        "manualArtReviewRequired": True,
        "sourceMayContainModernFeatures": True,
        "sourceSectorsAreNotGameOctagons": True,
    }

def verify_study(source_dir, out_dir):
    source, rgba, mask = validate_source(source_dir)
    out_dir = Path(out_dir)
    expected = expected_manifest(source)
    got = json.loads((out_dir / "manifest.json").read_text())
    if set(got) != set(expected) | {"studySha256", "sectorSha256"}:
        raise ValueError("Unexpected study metadata or forged game claim")
    for key, value in expected.items():
        if got.get(key) != value:
            raise ValueError("V158 source geometry/palette/approval changed: " + key)
    if set(got.get("sectorSha256", {})) != set(SECTORS):
        raise ValueError("Missing or extra study sectors")
    actual_study = period_palette_study(rgba, mask)
    if digest(out_dir / got["studyFile"]) != got["studySha256"]:
        raise ValueError("V158 full study hash mismatch")
    study = read_png(out_dir / got["studyFile"], "RGBA")
    if study.tobytes() != actual_study.tobytes():
        raise ValueError("V158 study pixels or alpha modified")
    for i, name in enumerate(SECTORS):
        file = out_dir / got["sectorFiles"][name]
        if digest(file) != got["sectorSha256"][name]:
            raise ValueError("V158 sector hash mismatch: " + name)
        with Image.open(file) as image:
            if image.format != "PNG" or image.mode != "RGBA" or image.size != (768, 768):
                raise ValueError("V158 sector dimensions/mode mismatch: " + name)
            if image.tobytes() != study.crop((i*768, 0, (i+1)*768, 768)).tobytes():
                raise ValueError("V158 sector not a continuous source-frame crop: " + name)
    return True

def produce(source_dir, out_dir):
    source, rgba, mask = validate_source(source_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    study = period_palette_study(rgba, mask)
    report = expected_manifest(source)
    study.save(out_dir / report["studyFile"], optimize=True)
    report["studySha256"] = digest(out_dir / report["studyFile"])
    report["sectorSha256"] = {}
    for i, name in enumerate(SECTORS):
        study.crop((i*768, 0, (i+1)*768, 768)).save(
            out_dir / report["sectorFiles"][name], optimize=True)
        report["sectorSha256"][name] = digest(out_dir / report["sectorFiles"][name])
    (out_dir / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    verify_study(source_dir, out_dir)
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v156", default="qa/v156-modern-exclusion")
    parser.add_argument("--v157", default="qa/v157-residual-modern")
    parser.add_argument("--output", default="qa/v158-period-material-study")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    # The real-source CI checks the entire V153 -> V156 -> V157 chain first.
    from v157_residual_modern_audit import verify_artifact as verify_v157
    verify_v157(Path(args.v156), Path(args.v157))
    if args.verify:
        verify_study(Path(args.v157), Path(args.output))
    else:
        produce(Path(args.v157), Path(args.output))
    print("V158 PASS: 3 source-frame palette sectors, unknown alpha preserved; no game or historical approval")

if __name__ == "__main__":
    main()
