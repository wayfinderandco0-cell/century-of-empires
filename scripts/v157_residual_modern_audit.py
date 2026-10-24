#!/usr/bin/env python3
"""V157: manually reviewed residual MODERN-source exclusions, NOT historical art.

Coordinates below are original V153 2304x768 source pixels, reviewed against
V156's actual CI PNG (artifact 12555208923). Rectangles are conservative
exclusions of visible remaining 2023 roofs/development/date labels. This
does NOT infer any 1780 road, structure, route, or vegetation. Transparent
means UNKNOWN: a human artist must author/review replacement terrain.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
from v156_modern_exclusion import SIZE, verify_output as verify_v156

# Observed in actual V156 west/center/east PNG, not generated road geometry.
# Box = (x0,y0,x1,y1), inclusive. Larger than a roof by design.
ROOF_REGIONS = (
    ("west-south-roof-cluster", (165, 636, 432, 767)),
    ("west-east-roof", (682, 563, 767, 658)),
    ("center-southwest-roofs", (898, 442, 1140, 616)),
    ("center-east-roofs", (1438, 396, 1535, 480)),
    ("east-mid-roofs", (1666, 315, 1874, 441)),
    ("east-northeast-roofs", (2145, 210, 2303, 326)),
    ("east-south-roof-cluster", (1536, 609, 2135, 767)),
)
# Individual still-visible '2023' stamps after V156's initial tile-center mask.
# These are observed source labels, NOT a claim of complete watermark removal.
DATE_MARKS = (
    (314, 416), (314, 735), (648, 735),
    (958, 99), (1278, 99), (958, 736), (1278, 736),
    (1919, 416), (2240, 416), (1919, 735), (2240, 735),
)
CANONICAL_ROOFS = ROOF_REGIONS
CANONICAL_DATES = DATE_MARKS
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

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_observations(roofs=ROOF_REGIONS, dates=DATE_MARKS):
    if roofs != CANONICAL_ROOFS or dates != CANONICAL_DATES:
        raise ValueError("V157 manually observed regions changed without review")
    for name, (x0,y0,x1,y1) in roofs:
        if not name or any(type(v) is not int for v in (x0,y0,x1,y1)):
            raise ValueError("Untrusted roof exclusion coordinates")
        if not (0 <= x0 < x1 < SIZE[0] and 0 <= y0 < y1 < SIZE[1]):
            raise ValueError("Roof observation outside source raster")
    for x,y in dates:
        if any(type(v) is not int for v in (x,y)):
            raise ValueError("Untrusted date label")
        if not (27 <= x < SIZE[0]-27 and 10 <= y < SIZE[1]-10):
            raise ValueError("Date label exclusion outside source")
    return True

def extend_mask(base_mask, roofs=ROOF_REGIONS, dates=DATE_MARKS):
    validate_observations(roofs, dates)
    if base_mask.mode != "L" or base_mask.size != SIZE:
        raise ValueError("V156 source mask format/size mismatch")
    if set(base_mask.getdata()) - {0,255}:
        raise ValueError("V156 source mask must be binary")
    result=base_mask.copy()
    d=ImageDraw.Draw(result)
    for _name,box in roofs:
        d.rectangle(box,fill=0)
    for x,y in dates:
        d.rectangle((x-27,y-10,x+27,y+10),fill=0)
    if any(new > old for old,new in zip(base_mask.tobytes(),result.tobytes())):
        raise ValueError("Previously excluded modern pixels became visible")
    return result

def coverage(mask):
    result={}
    for i,name in enumerate(("source-west","source-center","source-east")):
        section=mask.crop((i*768,0,(i+1)*768,768))
        ratio=section.histogram()[255]/(768*768)
        if not 0.05 < ratio < 0.9:
            raise ValueError("Implausible retained source fraction")
        result[name]=round(ratio,6)
    return result

def expected_report(base_manifest, mask):
    if any(base_manifest.get(k) != v for k,v in NOT_APPROVED.items()):
        raise ValueError("V156 source is not in required unapproved state")
    return {
        "version":157,
        "purpose":"Manually observed residual MODERN roofs/date labels; UNKNOWN holes, NOT game art",
        "sourceVersion":156,
        "sourceMosaicSha256":base_manifest["sourceMosaicSha256"],
        "previousMaskSha256":base_manifest["maskSha256"],
        "previousReferenceSha256":base_manifest["referenceSha256"],
        "pixelDimensions":list(SIZE),
        "sourceCrs":"EPSG:3857",
        "requiredAttribution":"Datenquelle: basemap.at",
        "license":"CC BY 4.0",
        "roofObservationNames":[name for name,_ in ROOF_REGIONS],
        "dateLabelObservationCount":len(DATE_MARKS),
        "sourceSectorRetainedFractions":coverage(mask),
        "exclusionAlphaMeaning":"0=excluded/unknown; 255=unreviewed modern source",
        "maskFile":"residual-modern-mask.png",
        "referenceFile":"residual-modern-reference.png",
        **NOT_APPROVED,
    }

def verify_images(base_mask, base_rgba, output_dir, report):
    if base_rgba.mode != "RGBA" or base_rgba.size != SIZE:
        raise ValueError("V156 RGBA source format mismatch")
    mask=extend_mask(base_mask)
    expected=base_rgba.copy()
    expected.putalpha(mask)
    for key in ("maskFile","referenceFile"):
        path=output_dir/report[key]
        with Image.open(path) as image:
            if image.format!="PNG" or image.size!=SIZE:
                raise ValueError("V157 PNG dimensions/format changed")
            required="L" if key=="maskFile" else "RGBA"
            if image.mode!=required or image.tobytes()!=(mask if key=="maskFile" else expected).tobytes():
                raise ValueError("V157 output pixel mismatch: "+key)
    return True

def verify_artifact(v156_dir, out_dir):
    base=json.loads((v156_dir/"manifest.json").read_text())
    with Image.open(v156_dir/base["maskFile"]) as im: base_mask=im.copy()
    with Image.open(v156_dir/base["referenceFile"]) as im: base_rgba=im.copy()
    expected=expected_report(base,extend_mask(base_mask))
    report=json.loads((out_dir/"manifest.json").read_text())
    if set(report)!=set(expected)|{"maskSha256","referenceSha256"}:
        raise ValueError("Unexpected V157 fields or false certification")
    if any(report.get(k)!=v for k,v in expected.items()):
        raise ValueError("V157 provenance/coverage/approval mismatch")
    for key,filekey in (("maskSha256","maskFile"),("referenceSha256","referenceFile")):
        if report.get(key)!=sha(out_dir/report[filekey]):
            raise ValueError("V157 source-image hash mismatch")
    return verify_images(base_mask,base_rgba,out_dir,report)

def produce_verified(v156_dir,out_dir):
    base=json.loads((v156_dir/"manifest.json").read_text())
    with Image.open(v156_dir/base["maskFile"]) as im: base_mask=im.copy()
    with Image.open(v156_dir/base["referenceFile"]) as im: base_rgba=im.copy()
    mask=extend_mask(base_mask)
    rgba=base_rgba.copy()
    rgba.putalpha(mask)
    out_dir.mkdir(parents=True,exist_ok=True)
    report=expected_report(base,mask)
    mask.save(out_dir/report["maskFile"],optimize=True)
    rgba.save(out_dir/report["referenceFile"],optimize=True)
    report["maskSha256"]=sha(out_dir/report["maskFile"])
    report["referenceSha256"]=sha(out_dir/report["referenceFile"])
    (out_dir/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    verify_artifact(v156_dir,out_dir)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",default="qa/v153-geographic-strip")
    p.add_argument("--v156",default="qa/v156-modern-exclusion")
    p.add_argument("--output",default="qa/v157-residual-modern")
    p.add_argument("--verify",action="store_true")
    a=p.parse_args()
    source,v156,out=Path(a.source),Path(a.v156),Path(a.output)
    verify_v156(source,v156)  # Rebuild/check the genuine source and all V156 pixels.
    if a.verify: verify_artifact(v156,out)
    else: produce_verified(v156,out)
    print("V157 PASS: 7 observed residual modern roof regions, 11 residual date marks; three source sectors; NO historical/game approval")

if __name__=="__main__":
    main()
