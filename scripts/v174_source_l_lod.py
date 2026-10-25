#!/usr/bin/env python3
"""V174: fail-closed, alpha-aware LOD coverage for the REAL V168/V173 SOURCE L.

Retained pixels are unreviewed *modern* geographic reference, NOT 1780 game art.
Excluded modern structures and the unacquired SW quadrant remain unknown.
No V121/V123 route, bridge, province or historical feature is inferred.
"""
import argparse
import json
from pathlib import Path
from PIL import Image
from v168_source_first_l_octagons import SIZE, CELL, SECTORS, NO_APPROVAL, sha
from v169_source_l_modern_exclusion import FLAGS, verify_output

BLOCK = 32
COLUMNS, ROWS = SIZE[0] // BLOCK, SIZE[1] // BLOCK
PIXELS_PER_BLOCK = BLOCK * BLOCK
TIERS = ("europe-overview", "regional", "alpine-pass", "ground")
SOURCE_ONLY_FLAGS = {
    **NO_APPROVAL, **FLAGS,
    "sourceReferenceOnly": True,
    "gameTerrainEligible": False,
    "gameDeepZoomEligible": False,
    "sourceToV123TransformVerified": False,
    "canTraverseSourceRoads": False,
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sector_for_block(col, row):
    require(type(col) is int and type(row) is int and
            0 <= col < COLUMNS and 0 <= row < ROWS, "invalid block address")
    if row >= 16 and col < 24:
        return None
    return "source-west" if col < 24 else ("source-center" if row < 16 else "source-south")

def block_class(retained):
    require(type(retained) is int and 0 <= retained <= PIXELS_PER_BLOCK,
            "invalid retained pixel count")
    return "excluded-or-unknown" if retained == 0 else (
        "unreviewed-modern-source" if retained == PIXELS_PER_BLOCK else
        "mixed-source-and-exclusion"
    )

def build_coverage(mask):
    require(mask.mode == "L" and mask.size == SIZE, "wrong source exclusion mask")
    require(set(mask.getdata()) <= {0, 255}, "nonbinary source alpha")
    blocks = []
    summary = {name: {"retainedPixels": 0, "fullyRetainedBlocks": 0,
                      "mixedBlocks": 0, "excludedBlocks": 0}
               for name in SECTORS}
    for row in range(ROWS):
        for col in range(COLUMNS):
            n = mask.crop((col*BLOCK, row*BLOCK,
                           (col+1)*BLOCK, (row+1)*BLOCK)).histogram()[255]
            sector = sector_for_block(col, row)
            if sector is None:
                require(n == 0, "unobserved southwest quadrant became visible")
            else:
                item = summary[sector]
                item["retainedPixels"] += n
                if n == 0: item["excludedBlocks"] += 1
                elif n == PIXELS_PER_BLOCK: item["fullyRetainedBlocks"] += 1
                else: item["mixedBlocks"] += 1
            blocks.append(n)
    require(len(blocks) == COLUMNS * ROWS, "incomplete source block grid")
    for name, box in SECTORS.items():
        expected = mask.crop(box).histogram()[255]
        require(summary[name]["retainedPixels"] == expected,
                "source sector coverage mismatch: " + name)
        require(sum(summary[name][k] for k in
                    ("fullyRetainedBlocks", "mixedBlocks", "excludedBlocks")) == 24*16,
                "source sector block count mismatch: " + name)
    return blocks, summary

def make_manifest(source_meta, mask, mask_sha, reference_sha):
    require(source_meta.get("version") == 169 and
            source_meta.get("sourceVersion") == 168 and
            source_meta.get("sourceCrs") == "EPSG:3857" and
            source_meta.get("sourceMosaicSha256") and
            source_meta.get("maskSha256") == mask_sha and
            source_meta.get("referenceSha256") == reference_sha,
            "wrong modern geographic source identity")
    for key, value in SOURCE_ONLY_FLAGS.items():
        if key in source_meta:
            require(source_meta[key] is value, "forged source approval: " + key)
    require(all(source_meta.get(k) is v for k, v in FLAGS.items()),
            "V173 modern exclusions/approval flags missing")
    blocks, summary = build_coverage(mask)
    for name in SECTORS:
        require(summary[name]["retainedPixels"] ==
                source_meta["sourceSectorCoverage"][name]["retainedPixels"],
                "source mask coverage not bound to manifest: " + name)
    return {
        "version": 174,
        "purpose": "Modern geographic SOURCE L coverage; no game-art or movement approval",
        "sourceVersion": 169,
        "sourceMosaicSha256": source_meta["sourceMosaicSha256"],
        "sourceMaskSha256": mask_sha,
        "sourceReferenceSha256": reference_sha,
        "sourceCrs": "EPSG:3857",
        "sourceExtentLonLat": source_meta["sourceExtentLonLat"],
        "pixelDimensions": list(SIZE),
        "blockSize": BLOCK,
        "blockGrid": [COLUMNS, ROWS],
        "sourceSectors": {k: list(v) for k, v in SECTORS.items()},
        "unobservedSouthwestBoundsPixels": [0,512,768,1024],
        "retainedPixelsByBlockRowMajor": blocks,
        "blockValueMeaning": "0=unknown/excluded; 1..1023=mixed; 1024=unreviewed modern SOURCE",
        "sectorCoverage": summary,
        "tiers": [{"name": tier, "modernSourceInspectionOnly": True,
                   "gameArtEligible": False, "playableRoadsEligible": False,
                   "deepZoomEligible": False} for tier in TIERS],
        "requiredAttribution": source_meta["requiredAttribution"],
        "sourceLicense": source_meta["sourceLicense"],
        "humanPeriodArtReviewRequired": True,
        **SOURCE_ONLY_FLAGS,
    }

def block_preview(blocks):
    require(len(blocks) == COLUMNS*ROWS, "incomplete block preview")
    image = Image.new("L", (COLUMNS, ROWS))
    image.putdata([0 if n == 0 else (255 if n == PIXELS_PER_BLOCK else 128)
                   for n in blocks])
    return image

def load_verified(source_dir, modern_dir):
    verify_output(source_dir, modern_dir)  # checks all 18 real JPEGs, alpha, SHA
    modern_dir = Path(modern_dir)
    source_meta = json.loads((modern_dir / "manifest.json").read_text())
    with Image.open(modern_dir / source_meta["maskFile"]) as im:
        require(im.format == "PNG" and im.mode == "L" and im.size == SIZE,
                "wrong modern mask image")
        mask = im.copy()
    return source_meta, mask

def build(source_dir, modern_dir, output):
    meta, mask = load_verified(source_dir, modern_dir)
    manifest = make_manifest(meta, mask, meta["maskSha256"], meta["referenceSha256"])
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    preview = block_preview(manifest["retainedPixelsByBlockRowMajor"])
    preview.save(output / "source-L-block-coverage.png", optimize=True)
    manifest["coveragePreviewSha256"] = sha(output / "source-L-block-coverage.png")
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify(source_dir, modern_dir, output)
    return manifest

def verify(source_dir, modern_dir, output):
    meta, mask = load_verified(source_dir, modern_dir)
    output = Path(output)
    got = json.loads((output / "manifest.json").read_text())
    expected = make_manifest(meta, mask, meta["maskSha256"], meta["referenceSha256"])
    require(set(got) == set(expected) | {"coveragePreviewSha256"},
            "untrusted V174 fields")
    require(all(got.get(k) == value for k, value in expected.items()),
            "V174 source coverage, tiers or approvals changed")
    path = output / "source-L-block-coverage.png"
    require(sha(path) == got["coveragePreviewSha256"],
            "V174 coverage preview checksum mismatch")
    with Image.open(path) as im:
        require(im.format == "PNG" and im.mode == "L" and
                im.size == (COLUMNS, ROWS) and
                im.tobytes() == block_preview(expected["retainedPixelsByBlockRowMajor"]).tobytes(),
                "V174 coverage preview pixels changed")
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="qa/v168-source-L")
    p.add_argument("--modern", default="qa/v169-modern-source-L")
    p.add_argument("--output", default="qa/v174-source-lod")
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    if a.verify: verify(a.source, a.modern, a.output)
    else: build(a.source, a.modern, a.output)
    print("V174: 3 modern SOURCE sectors, 4 inspection tiers; all game/route eligibility FALSE")

if __name__ == "__main__":
    main()
