#!/usr/bin/env python3
"""Native-pixel licensed PHOTO art for two distinct Sharr Mountains source cells.

This is a real 1536x1024 photographic composition stage, not an SVG/map
thumbnail. No new road, bridge, settlement, province or gameplay route is
implied. Historical geography and source-image modern-feature quarantine
remain separate approval gates. Sources and credit are in terrain-v224.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "terrain-grid" / "factory-photo"
W, H = 1536, 1024
# These two different photographs are from the Sharr Mountains, Kosovo.
# Their original files are 3072x2304. The rectangles below use native
# pixels, NOT repeated/mirrored terrain or global image stretching.
SOURCES = (
    dict(id="eu-09-16", source="terrain-v224/source/west-wikimedia-3072-ccby.jpg",
         sourceKey="west", rect=(1536, 740, 3072, 1764),
         motif="Sharr limestone ridges and alpine spring meadows"),
    dict(id="eu-10-16", source="terrain-v224/source/south-wikimedia-3072-ccby.jpg",
         sourceKey="south", rect=(1536, 890, 3072, 1914),
         motif="Sharr wooded highland slopes and rocky pasture"),
)
def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    provenance = json.loads((ROOT / "terrain-v224/assets/manifest.json").read_text())
    licenses = {row["tile"]: row for row in provenance["sources"]}
    batch = json.loads((ROOT / "generated/octagon-factory/batch-01/manifest.json").read_text())
    by_id = {cell["id"]: cell for cell in batch["cells"]}
    records = []
    contact = Image.new("RGB", (W, H + 70), "#14271f")
    for i, spec in enumerate(SOURCES):
        cell = by_id.get(spec["id"])
        if not cell:
            raise RuntimeError("Photo candidate absent from geographic batch 01: " + spec["id"])
        evidence = licenses[spec["sourceKey"]]
        if evidence["original"] != spec["source"] or evidence["license"] != "CC BY 4.0":
            raise RuntimeError("Missing exact source and CC BY provenance")
        if cell["usableForGameplay"] or cell["historicallyCertified"]:
            raise RuntimeError("Unverified candidate incorrectly enabled")
        original = Image.open(ROOT / spec["source"]).convert("RGB")
        if original.size != (3072, 2304):
            raise RuntimeError(f"Unexpected source resolution {original.size}")
        rect = spec["rect"]
        if rect[2]-rect[0] != W or rect[3]-rect[1] != H:
            raise RuntimeError("No native-pixel scaling permitted")
        image = original.crop(rect)
        # Warm photographic atlas grade; no procedural trees, mountains,
        # roads, or river geometry is synthesized. Preserve full detail.
        image = ImageEnhance.Color(image).enhance(.86)
        image = ImageEnhance.Contrast(image).enhance(1.04)
        image = ImageEnhance.Brightness(image).enhance(.91)
        output = OUT / (spec["id"] + ".webp")
        image.save(output, "WEBP", quality=93, method=6)
        if Image.open(output).size != (W, H):
            raise RuntimeError("Output size mismatch")
        if i == 0:
            contact.paste(image.resize((768, 512), Image.Resampling.LANCZOS), (0, 45))
        else:
            contact.paste(image.resize((768, 512), Image.Resampling.LANCZOS), (768, 45))
        records.append(dict(
            id=spec["id"], grid=cell["grid"], origin=cell["origin"],
            geography=cell["geography"], image="terrain-grid/factory-photo/"+output.name,
            imageSize=[W,H], originalSource=spec["source"],
            sourceCrop=list(rect), sourceSha256=sha((ROOT/spec["source"]).read_bytes()),
            outputSha256=sha(output.read_bytes()), motif=spec["motif"],
            sourceRegion="Sharr Mountains, Kosovo; reference imagery, not georegistration",
            sourcePage=evidence["sourcePage"], author=evidence["author"],
            license=evidence["license"], licenseUrl=evidence["licenseUrl"],
            modernFeaturesQuarantined=False, originalTerrainSource=True,
            sourceBackedPhotographicArtComposed=True, artMethodApproved=False,
            physicallyRoadSeamChecked=False, paintedRoads=[], gameplayEnabled=False,
            historicallyVerified=False, visuallyReviewedOnPhone=False,
            provinceIds=[], scenicSettlements=[], strategicTowns=[]
        ))
    if len({x["originalSource"] for x in records}) != len(records):
        raise RuntimeError("Repeated source in two-cell pilot")
    if len({x["outputSha256"] for x in records}) != len(records):
        raise RuntimeError("Duplicate photographic artwork")
    draw = ImageDraw.Draw(contact)
    draw.text((16, 16), "PHOTO SOURCE A: distinct native crop, Kosovo", fill="#fff1d4")
    draw.text((784, 16), "PHOTO SOURCE B: distinct native crop, Kosovo", fill="#fff1d4")
    draw.text((16, 578), "NOT road-connected / NOT historically certified / NOT final gameplay art", fill="#fff1d4")
    contact.save(OUT / "photo-contact.webp", "WEBP", quality=88)
    manifest = dict(schema="coe-photo-art/v1", status="source-backed-unapproved",
        fixedArtReference="456107f28c8db1f87522bbc7511809b2a215f6fb",
        batch=1, photographicArtComposed=len(records), visuallyChecked=0,
        physicallyRoadConnected=0, mobileRendered=0, nativeGamePlayable=0,
        historicallyVerified=0, finishedToday=0, cells=records)
    (OUT/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    cards = "".join(
        '<article><img src="'+r["id"]+'.webp" alt="'+r["motif"]+'"><h2>'+r["id"]+
        '</h2><p>'+r["motif"]+'</p><p>Photo: '+r["author"]+
        ' · CC BY 4.0. Not historically verified; no road or province enabled.</p></article>'
        for r in records)
    (OUT/"index.html").write_text(
        '<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Century of Empires: native photo art source candidates</title>'
        '<style>body{margin:12px;background:#152820;color:#f4e6c9;font:15px system-ui}'
        'main{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:12px}'
        'article{border:1px solid #a48b60;padding:8px;border-radius:8px;background:#22372e}'
        'img{width:100%;aspect-ratio:3/2;object-fit:contain}p{font-size:12px;line-height:1.5}'
        '</style><h1>Two original photographic terrain candidates</h1>'
        '<p>Full 1536×1024 source-native photographic art, NOT low-resolution geographic SVG. '
        'Distinct source photographs; no artificial road stripes, no duplicate Matrei scenery. '
        'Unverified modern features and missing physical route registration BLOCK gameplay.</p>'
        '<main>'+cards+'</main></html>')
    print(json.dumps(dict(photoArtComposed=len(records), outputImages=[r["image"] for r in records],
                          finished=0, outputBytes=sum((OUT/(r["id"]+".webp")).stat().st_size for r in records))))

if __name__ == "__main__":
    main()
