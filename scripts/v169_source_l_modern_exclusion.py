#!/usr/bin/env python3
"""V169: visually observed MODERN exclusions on the exact V168 geographic L.

All coordinates refer to original 1536x1024 V168 basemap.at SOURCE pixels,
reviewed against the actual 18-tile CI mosaic (artifact 12576057255).
These are conservative candidate exclusions, NOT 1780 routes or game art.
Excluded/unsurveyed pixels remain transparent with zero hidden RGB; no
inpainting, copy/paste, fictitious river, building, road or bridge is added.
The muted-palette output is a source-material study, NOT historical evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
from v168_source_first_l_octagons import (
    SIZE, CELL, SECTORS, NO_APPROVAL, ATTRIBUTION, sha, verify as verify_v168,
)

# Centerlines visually traced from the ACTUAL V168 source-L PNG. These are
# 2023 asphalt/driveway exclusion candidates, never playable route geometry.
# Radius includes visible road shoulders; unmasked modern features may remain.
MODERN_ROADS=(
    ("northwest-visible-drive", 13, ((0,29),(48,25),(88,18),(126,31))),
    ("center-modern-paved-road", 24, (
        (768,559),(816,568),(874,555),(928,550),(965,532),
        (1017,508),(1065,483),(1115,450),(1163,420),
        (1213,394),(1252,373),(1284,337),(1298,299),
        (1311,287),(1341,317),(1390,354),(1442,380),
        (1495,393),(1535,387))),
    ("south-modern-paved-road", 24, (
        (951,1023),(1001,986),(1056,950),(1129,931),
        (1168,899),(1203,856),(1232,840),(1259,844),
        (1296,867),(1362,889),(1425,866),(1492,840),(1535,833))),
)
# Broad visual-review exclusions for visible contemporary roofs and paved
# yards, with original source coordinates (inclusive bounds).
DEVELOPED=(
    ("center-road-farm-buildings", (880,457,1134,637)),
    ("center-east-roof-cluster", (1318,337,1535,440)),
    ("south-road-houses-west", (1030,854,1207,1023)),
    ("south-road-houses-east", (1292,795,1535,949)),
    ("west-north-rooflets", (126,0,259,54)),
    ("west-north-small-roof", (392,15,432,57)),
)
# Visible 2023 source date stamps, including partial stamps at the west edge.
# These are individual observed labels, not an OCR-based completeness claim.
DATE_STAMPS=(
    (0,96),(315,96),(638,96),(958,96),(1278,96),
    (0,415),(315,415),(638,415),(958,415),(1278,415),
    (958,735),(1278,735),
)
# The V158 LUT is applied only to retained original pixels; no spatial edits.
TONAL_LUT=((94,100,10),(90,100,11),(78,100,13))
FLAGS={
    **NO_APPROVAL,
    "allModernFeaturesDetected":False,
    "modernInfrastructureCleared":False,
    "manualArtReviewRequired":True,
    "sourceMayContainModernFeatures":True,
    "sourceSectorsAreNotGameOctagons":True,
}
FILES={
    "maskFile":"source-L-modern-exclusion-mask.png",
    "referenceFile":"source-L-modern-exclusion-reference.png",
    "studyFile":"source-L-muted-material-study.png",
}
def require(ok,message):
    if not ok:raise ValueError(message)

def in_source(x,y):
    return 0<=x<SIZE[0] and 0<=y<SIZE[1] and (y<512 or x>=768)

def validate_observations(roads=MODERN_ROADS,developed=DEVELOPED,dates=DATE_STAMPS):
    require(roads==MODERN_ROADS and developed==DEVELOPED and dates==DATE_STAMPS,
            "observed modern-feature geometry changed without source review")
    names=[v[0] for v in roads]+[v[0] for v in developed]
    require(len(names)==len(set(names)) and len(names)>=8,"duplicated/missing observations")
    for name,radius,points in roads:
        require(type(radius) is int and 5<=radius<=35 and len(points)>=3,
                "untrusted modern road observation")
        require(all(type(x) is int and type(y) is int and in_source(x,y)
                    for x,y in points),"road outside acquired source")
    for name,(x0,y0,x1,y1) in developed:
        require(all(type(v) is int for v in (x0,y0,x1,y1)) and
                x0<x1 and y0<y1 and in_source(x0,y0) and in_source(x1,y1),
                "development exclusion outside acquired source")
    for x,y in dates:
        require(type(x) is int and type(y) is int and in_source(x,y),
                "date label outside acquired source")
    return True

def source_mask(source):
    require(source.mode=="RGBA" and source.size==SIZE,"invalid V168 RGBA source")
    # Preserve the entire unobserved southwest quadrant as alpha zero.
    alpha=source.getchannel("A")
    require(set(alpha.getdata())<={0,255},"nonbinary V168 source alpha")
    require(alpha.getpixel((0,700))==0 and alpha.getpixel((800,700))==255,
            "V168 unknown/source alpha altered")
    return alpha

def make_mask(source):
    validate_observations()
    mask=source_mask(source)
    d=ImageDraw.Draw(mask)
    for _name,radius,points in MODERN_ROADS:
        d.line(points,fill=0,width=radius*2,joint="curve")
        for x,y in points:
            d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=0)
    for _name,box in DEVELOPED:d.rectangle(box,fill=0)
    for x,y in DATE_STAMPS:
        d.rectangle((x-25,y-11,x+25,y+11),fill=0)
    require(mask.getpixel((0,700))==0,"unknown quadrant was filled")
    require(not any(new>old for old,new in zip(source.getchannel("A").tobytes(),mask.tobytes())),
            "excluded/unknown source pixels became visible")
    return mask

def clean_rgba(source,mask):
    require(mask.mode=="L" and mask.size==SIZE and set(mask.getdata())<={0,255},
            "invalid binary source exclusion mask")
    require(source_mask(source).size==mask.size,"invalid original source")
    require(not any(new>old for old,new in zip(source.getchannel("A").tobytes(),mask.tobytes())),
            "modern/unknown pixels were unmasked")
    return Image.composite(source,Image.new("RGBA",SIZE,(0,0,0,0)),mask)

def muted_study(source,mask):
    channels=source.convert("RGB").split()
    out=[]
    for ch,(numerator,denominator,offset) in zip(channels,TONAL_LUT):
        table=[max(0,min(255,(v*numerator+denominator//2)//denominator+offset))
               for v in range(256)]
        out.append(ch.point(table))
    styled=Image.merge("RGB",tuple(out)).convert("RGBA")
    return clean_rgba(styled,mask) if False else Image.composite(
        styled,Image.new("RGBA",SIZE,(0,0,0,0)),mask)

def coverage(source,mask):
    original=source_mask(source)
    result={}
    for name,box in SECTORS.items():
        old=original.crop(box).histogram()[255]
        new=mask.crop(box).histogram()[255]
        total=CELL[0]*CELL[1]
        require(old==total and 0<new<old,"source exclusion missing or entire sector removed: "+name)
        result[name]={
            "sourcePixels":old,
            "retainedPixels":new,
            "excludedPixels":old-new,
            "retainedFraction":round(new/total,6),
        }
    return result

def expected_manifest(original,source,mask):
    require(original.get("version")==168 and original.get("provider")=="basemap.at",
            "wrong V168 source provenance")
    for key,value in NO_APPROVAL.items():
        require(original.get(key) is value,"V168 approval changed: "+key)
    return {
        "version":169,
        "purpose":"Observed modern exclusions and source-pixel muted material; NOT GAME ART",
        "sourceVersion":168,
        "sourceMosaicSha256":original["mosaicSha256"],
        "sourceCrs":"EPSG:3857",
        "sourceExtentLonLat":original["mosaicBoundsLonLat"],
        "pixelDimensions":list(SIZE),
        "sourceSectorPixelBounds":{k:list(v) for k,v in SECTORS.items()},
        "unobservedSouthwestBoundsPixels":[0,512,768,1024],
        "sourceLicense":"CC BY 4.0",
        "requiredAttribution":ATTRIBUTION,
        "modernRoadObservations":[name for name,*_ in MODERN_ROADS],
        "developedObservations":[name for name,*_ in DEVELOPED],
        "dateStampObservationCount":len(DATE_STAMPS),
        "exclusionAlphaMeaning":"0=modern-excluded or unknown, never auto-filled; 255=unreviewed modern source",
        "paletteLut":[list(v) for v in TONAL_LUT],
        "noSpatialCopiesOrSynthesizedFeatures":True,
        "sourceSectorCoverage":coverage(source,mask),
        **FILES,**FLAGS,
    }

def validate_input(directory):
    directory=Path(directory)
    verify_v168(directory)  # Original 18 JPEG SHA256s, exact L pixels and sectors.
    original=json.loads((directory/"manifest.json").read_text())
    with Image.open(directory/original["mosaicFile"]) as im:
        require(im.format=="PNG" and im.mode=="RGBA" and im.size==SIZE,
                "untrusted original L PNG")
        source=im.copy()
    return original,source

def build(source_dir,out_dir):
    original,source=validate_input(source_dir)
    mask=make_mask(source)
    report=expected_manifest(original,source,mask)
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    outputs={
        "maskSha256":(report["maskFile"],mask),
        "referenceSha256":(report["referenceFile"],clean_rgba(source,mask)),
        "studySha256":(report["studyFile"],muted_study(source,mask)),
    }
    for key,(filename,image) in outputs.items():
        image.save(out_dir/filename,optimize=True)
        report[key]=sha(out_dir/filename)
    (out_dir/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    verify_output(source_dir,out_dir)
    return report

def verify_output(source_dir,out_dir):
    original,source=validate_input(source_dir)
    mask=make_mask(source)
    expected=expected_manifest(original,source,mask)
    out_dir=Path(out_dir)
    got=json.loads((out_dir/"manifest.json").read_text())
    require(set(got)==set(expected)|{"maskSha256","referenceSha256","studySha256"},
            "unexpected V169 metadata or false approval")
    require(all(got.get(k)==v for k,v in expected.items()),
            "source, exclusions, coverage, or approval metadata changed")
    for key,filename,expected_image in (
        ("maskSha256",FILES["maskFile"],mask),
        ("referenceSha256",FILES["referenceFile"],clean_rgba(source,mask)),
        ("studySha256",FILES["studyFile"],muted_study(source,mask)),
    ):
        path=out_dir/filename
        require(sha(path)==got[key],"V169 output SHA256 mismatch: "+filename)
        with Image.open(path) as im:
            require(im.format=="PNG" and im.mode==expected_image.mode and
                    im.size==SIZE and im.tobytes()==expected_image.tobytes(),
                    "V169 output pixels mismatch: "+filename)
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",default="qa/v168-source-L")
    p.add_argument("--output",default="qa/v169-modern-source-L")
    p.add_argument("--verify",action="store_true")
    a=p.parse_args()
    if a.verify:verify_output(a.source,a.output)
    else:build(a.source,a.output)
    print("V169 modern exclusions: real source pixels, unknown transparent; NOT game art")

if __name__=="__main__":main()
