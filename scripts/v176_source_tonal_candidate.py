#!/usr/bin/env python3
"""Source-first Alpine tonal art *candidate*. No inferred historical geography.

Only per-pixel color transforms on independently masked modern reference imagery.
No spatial resampling, alpha fill, feature cloning, roads or game-coordinate claims.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

SIZE = (1536, 1024)
SECTORS = {"source-west": (0,0,768,512),
           "source-center": (768,0,1536,512),
           "source-south": (768,512,1536,1024)}
FILENAME = "source-L-period-tonal-CANDIDATE.png"
# Monotonic LUTs preserve original local image structure and edges.
# These are interpretive colors, not a reconstruction of 1780 vegetation.
LUT = ((110,100,1),(107,100,0),(105,100,-5))
FALSE_FLAGS = ("productionApproved", "periodArtComplete", "historic1780Certified",
               "v123RoadsGeoregistered", "bridgeBanksVerified", "physicalIPhoneApproved",
               "historicalRoadsVerified", "v121ToGeographyRegistered")

def require(ok, reason):
    if not ok: raise ValueError(reason)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_source(meta, lod, study, mask):
    require(meta.get("version") == 169 and meta.get("sourceCrs") == "EPSG:3857" and
            meta.get("sourceLicense") == "CC BY 4.0" and
            meta.get("requiredAttribution") == "Datenquelle: basemap.at" and
            meta.get("sourceSectorsAreNotGameOctagons") is True and
            meta.get("modernInfrastructureCleared") is False,
            "wrong geographic source or false historic claim")
    require(all(meta.get(k) is False for k in FALSE_FLAGS), "forged source approval")
    require(lod.get("version") == 174 and
            lod.get("sourceMosaicSha256") == meta.get("sourceMosaicSha256") and
            lod.get("sourceMaskSha256") == meta.get("maskSha256") and
            lod.get("sourceReferenceSha256") == meta.get("referenceSha256") and
            lod.get("blockGrid") == [48,32] and
            len(lod.get("retainedPixelsByBlockRowMajor", [])) == 1536 and
            len(lod.get("tiers", [])) == 4 and
            all(lod.get(k) is False for k in FALSE_FLAGS) and
            lod.get("sourceToV123TransformVerified") is False and
            all(not t.get("gameArtEligible", True) and
                    not t.get("playableRoadsEligible", True) and
                    not t.get("deepZoomEligible", True) for t in lod["tiers"]),
            "untrusted LOD or forged game eligibility")
    require(study.mode == "RGBA" and study.size == SIZE and
            mask.mode == "L" and mask.size == SIZE,
            "invalid source/mask dimensions")
    require(study.getchannel("A").tobytes() == mask.tobytes(),
            "modern or unknown pixels filled")
    require(set(mask.getdata()) <= {0,255}, "nonbinary modern exclusions")
    require(mask.crop((0,512,768,1024)).getbbox() is None,
            "unobserved southwest pixels became visible")
    for name,box in SECTORS.items():
        require(mask.crop(box).histogram()[255] ==
                meta["sourceSectorCoverage"][name]["retainedPixels"] ==
                lod["sectorCoverage"][name]["retainedPixels"],
                "sector coverage mismatch: " + name)
    for row in range(32):
        for col in range(48):
            n = mask.crop((col*32,row*32,col*32+32,row*32+32)).histogram()[255]
            require(n == lod["retainedPixelsByBlockRowMajor"][row*48+col],
                    "LOD pixel count differs from source mask")

def tone(study):
    require(study.mode == "RGBA" and study.size == SIZE, "wrong source study")
    rgb = study.convert("RGB")
    channels=[]
    for channel,(n,d,offset) in zip(rgb.split(),LUT):
        table=[max(0,min(255,(v*n+d//2)//d+offset)) for v in range(256)]
        channels.append(channel.point(table))
    out=Image.merge("RGB",tuple(channels)).convert("RGBA")
    out.putalpha(study.getchannel("A"))
    # Original excluded RGB was zero; keep excluded output RGB zero too.
    return Image.composite(out,Image.new("RGBA",SIZE,(0,0,0,0)),study.getchannel("A"))

def expected_manifest(meta,lod):
    return {"version":176,"purpose":"SOURCE-ONLY interpretive tonal candidate, NOT historical game art",
            "sourceStudySha256":meta["studySha256"],
            "sourceMaskSha256":meta["maskSha256"],
            "sourceMosaicSha256":lod["sourceMosaicSha256"],
            "sourceCrs":"EPSG:3857","pixelDimensions":list(SIZE),
            "sourceSectors":{k:list(v) for k,v in SECTORS.items()},
            "tonalLut":[list(x) for x in LUT],
            "noSpatialCopiesOrSynthesizedFeatures":True,
            "modernExclusionsRemainTransparent":True,
            "sourceSectorsAreNotGameOctagons":True,
            "allModernFeaturesDetected":False,
            "modernInfrastructureCleared":False,
            "humanHistoricalArtReviewRequired":True,
            "gameArtEligible":False,"gameDeepZoomEligible":False,
            "canTraverseSourceRoads":False,
            "requiredAttribution":meta["requiredAttribution"],
            "sourceLicense":meta["sourceLicense"],
            "imageFile":FILENAME,
            **{k:False for k in FALSE_FLAGS}}

def load(modern,lod_dir):
    modern=Path(modern);lod_dir=Path(lod_dir)
    meta=json.loads((modern/"manifest.json").read_text())
    lod=json.loads((lod_dir/"manifest.json").read_text())
    require(sha(modern/meta["studyFile"]) == meta["studySha256"] and
            sha(modern/meta["maskFile"]) == meta["maskSha256"],
            "source file SHA mismatch")
    with Image.open(modern/meta["studyFile"]) as im: study=im.copy()
    with Image.open(modern/meta["maskFile"]) as im: mask=im.copy()
    validate_source(meta,lod,study,mask)
    return meta,lod,study

def build(modern,lod_dir,output):
    meta,lod,study=load(modern,lod_dir)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    tone(study).save(output/FILENAME,optimize=True)
    report=expected_manifest(meta,lod)
    report["imageSha256"]=sha(output/FILENAME)
    (output/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    verify(modern,lod_dir,output)
    return report

def verify(modern,lod_dir,output):
    meta,lod,study=load(modern,lod_dir)
    output=Path(output);got=json.loads((output/"manifest.json").read_text())
    expected=expected_manifest(meta,lod)
    require(set(got)==set(expected)|{"imageSha256"} and
            all(got.get(k)==v for k,v in expected.items()),
            "forged candidate provenance or game approval")
    require(sha(output/FILENAME)==got["imageSha256"], "candidate SHA mismatch")
    with Image.open(output/FILENAME) as im:
        require(im.format=="PNG" and im.mode=="RGBA" and im.size==SIZE and
                im.tobytes()==tone(study).tobytes(),
                "candidate pixels differ from source-only LUT")
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--modern",default="qa/v169-modern-source-L")
    p.add_argument("--lod",default="qa/v174-source-lod")
    p.add_argument("--output",default="qa/v176-tonal-candidate")
    p.add_argument("--verify",action="store_true")
    a=p.parse_args()
    if a.verify:verify(a.modern,a.lod,a.output)
    else:build(a.modern,a.lod,a.output)
    print("V176 SOURCE-only tonal material candidate; NOT 1780–1880 game art")
if __name__=="__main__":main()
