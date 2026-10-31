#!/usr/bin/env python3
"""Ingest genuinely new original V267-style art, not photo/heightmesh candidates.

The source image is authored separately. This script performs only UNIFORM
rescaling, exact V123 cut-corner clipping and conservative provenance/quality
checks. It cannot infer historic roads, confirm visual approval or promote art
into the production atlas. Source material remains the creator's original.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[1]
REF = "456107f28c8db1f87522bbc7511809b2a215f6fb"
W, H, CORNER = 1536, 1024, 256
BATCH = ROOT / "terrain-grid/v267-original-art-batch-01/batch.json"
TARGET_ID = "matrei-east-ridge"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_mask() -> Image.Image:
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.polygon([(CORNER, 0), (W-CORNER, 0), (W-1, CORNER),
               (W-1, H-CORNER-1), (W-CORNER, H-1),
               (CORNER, H-1), (0, H-CORNER-1), (0, CORNER)], fill=255)
    return mask


def ingest(source: Path, output: Path, left: int = 240, right: int = 240):
    """Uniform enlargement only; no tree deformation or new roads."""
    with Image.open(source) as original:
        im = original.convert("RGB")
    if im.size != (W, H) or left < 0 or right < 0 or left + right >= W:
        raise ValueError("Expected 1536x1024 original image and valid side margins")
    usable = W - left - right
    height = round(H * W / usable)
    scaled = im.crop((left, 0, W-right, H)).resize(
        (W, height), Image.Resampling.LANCZOS)
    top = (height-H)//2
    scene = scaled.crop((0, top, W, top+H))
    result = Image.new("RGB", (W, H), (10, 13, 11))
    result.paste(scene, (0, 0), exact_mask())
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output, "WEBP", quality=68, method=6)
    return {"sha256": sha(output), "dimensions": [W, H],
            "sourceDimensions": list(im.size), "sourceMargins": [left, right],
            "uniformScale": round(W/usable, 6), "treeGeometryWarped": False,
            "exactV123OctagonMask": True}


def verify(manifest_path: Path = BATCH):
    batch = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert batch["schema"] == "coe-v267-original-art-batch/v1"
    assert batch["referenceCommit"] == REF
    assert len(batch["cells"]) == 8
    cells = batch["cells"]
    assert len({c["id"] for c in cells}) == 8
    assert len({tuple(c["origin"]) for c in cells}) == 8
    art = [c for c in cells if c.get("originalArtComposed") is True]
    assert len(art) == 1 and art[0]["id"] == TARGET_ID
    c = art[0]
    assert c["origin"] == [3072, 0]
    assert c["visualGrammar"] == "v267-original-layered-landscape"
    assert not c["roadPorts"] and not c["strategicNodes"] and not c["provinceIds"]
    assert c["visuallyReviewed"] is True and c["visualQualityApproved"] is False
    for key in ("roadSeamsVerified", "historicalVerified",
                "nativePlayable", "userApproved"):
        assert c[key] is False, f"Premature promotion: {key}"
    p = ROOT / c["art"]
    assert p.is_file() and sha(p) == c["assetSha256"]
    with Image.open(p) as source:
        assert source.size == (W, H)
        rgb = source.convert("RGB")
        # Masked corners must be dark and interior must contain real terrain.
        for xy in ((0, 0), (W-1, 0), (0, H-1), (W-1, H-1)):
            assert max(rgb.getpixel(xy)) < 30, f"Unmasked corner {xy}"
        assert sum(rgb.getpixel((W//2, H//2))) > 90
        assert max(ImageStat.Stat(rgb.crop((512, 256, 1024, 768))).stddev) > 25
    for other in cells:
        if other["id"] != TARGET_ID:
            assert not other.get("art") and other["originalArtComposed"] is False
    if c["mobileWebkitRendered"]:
        assert (ROOT / "terrain-grid/v267-original-art-batch-01/actual-webkit-iphone-new-ridge.png").is_file()
    assert batch["netFinishedToday"] == 0
    return {"candidateMetadata": len(cells), "originalArtComposed": len(art),
            "visuallyReviewed": 1, "roadConnected": 0, "mobileWebkitRendered": int(c["mobileWebkitRendered"]),
            "historicallyVerified": 0, "nativePlayable": 0,
            "userApproved": 0, "netFinishedToday": 0,
            "assetSha256": c["assetSha256"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, help="original authored 1536x1024 image")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--left", type=int, default=240)
    ap.add_argument("--right", type=int, default=240)
    ap.add_argument("--manifest", type=Path, default=BATCH)
    args = ap.parse_args()
    if args.source:
        if not args.output or not args.output.resolve().is_relative_to(
                (ROOT / "terrain-grid/v267-original-art-batch-01").resolve()):
            raise ValueError("Only the isolated V267 candidate output folder may be written")
        print(json.dumps(ingest(args.source, args.output, args.left, args.right)))
    else:
        print(json.dumps(verify(args.manifest), sort_keys=True))


if __name__ == "__main__":
    main()