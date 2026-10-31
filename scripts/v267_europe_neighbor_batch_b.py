#!/usr/bin/env python3
"""Second 8-cell European Alpine original-layered scenic ART STUDY.

Uses eight additional individually CC0-verified oblique European landscape
sources; never samples protected WEST/MATREI/SOUTH or the first eight studies.
Natural perspective/trees are preserved. There are NO invented cartways,
settlements, river crossings, conquest nodes or historical route claims.
"""
from __future__ import annotations
import hashlib
import io
import json
import os
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw
import v267_original_neighbor_art as v267
import v267_native_ground_compositor as ground

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-grid/v267-europe-neighbor-b"
REF=v267.REF
# All locations are V123 *local scenic atlas coordinates*, NOT geodetic
# coordinates. Source landscapes are geographic analogues, not surveyed tiles.
# Titles have individually documented CC0 licenses on Wikimedia Commons.
SPEC=[
 ("southern-terraces","Tyrol, Austria (Unsplash).jpg",(0,3072),"tyrolean-wooded-valley",(.48,.60),"Tyrol, Austria","dM4ppxLsxbM"),
 ("southern-high-meadow","Lost in the mountains of South Tyrol (Unsplash).jpg",(1536,3072),"south-tyrol-high-meadow",(.51,.57),"South Tyrol, Italy","7oxd5HfTLiE"),
 ("dolomite-south-ridge","Snowy mountain in the Dolomites (Unsplash).jpg",(3072,3072),"dolomite-limestone-ridge",(.49,.56),"Dolomites, Italy","b3YPoXpvp4M"),
 ("dolomite-south-pass","Passo Sella, Dolomites (Unsplash).jpg",(4608,3072),"dolomite-open-pass",(.51,.60),"Passo Sella, Italy","OzhhqIQuoO0"),
 ("alpine-southwest-slope","Swiss Alps, Switzerland (Unsplash).jpg",(6144,3072),"swiss-alpine-green-slope",(.48,.57),"Troistorrents, Switzerland","HzaT5l4Fzqc"),
 ("alpine-east-summit","Dramatic Alpine scenery (Unsplash).jpg",(6144,0),"alpine-high-ridge",(.50,.53),"Kleine Scheidegg, Switzerland","h4_Dq9CYugM"),
 ("alpine-east-lakeside","Mountain peak in a lake (Unsplash).jpg",(6144,1024),"austrian-lakeside-forest",(.50,.55),"Kitzbühel, Austria","bWuy_tqJPOA"),
 ("alpine-east-snowfield","Alpine village landscape (Unsplash).jpg",(6144,2048),"snowy-alpine-settlement-reference",(.49,.58),"Livigno, Italy","WCm0wjn1y04"),
]
def licensed_source(spec):
    """Commons verifies CC0 first. Same-source Unsplash original is a fallback.

    Commons 429 on shared runners must not cause a replacement photograph.
    The immutable Unsplash ID is transcribed from that exact Commons file page.
    """
    title=spec[1]
    try:
        return v267.commons(title)
    except RuntimeError as first:
        # Only network delivery errors are eligible. A failed CC0 license
        # check must never be bypassed.
        if "429" not in str(first) and "404" not in str(first):
            raise
        unsplash_id=spec[6]
        url="https://unsplash.com/photos/"+unsplash_id+"/download?force=true&w=2400"
        try:
            raw=v267.get(url,fast_fail_429=True)
            photo=Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception as second:
            raise RuntimeError("Both CC0 source delivery paths failed for "+title+
                               "; Commons: "+str(first)+"; Unsplash: "+str(second))
        if photo.width<1600 or photo.height<1050:
            raise RuntimeError("Insufficient same-source Unsplash dimensions: "+title)
        return photo,{
            "title":title,
            "page":"https://commons.wikimedia.org/wiki/File:"+
                   urllib.parse.quote(title.replace(" ","_")),
            "license":"CC0 1.0",
            "licenseUrl":"https://creativecommons.org/publicdomain/zero/1.0/",
            "sourceSha256":hashlib.sha256(raw).hexdigest(),
            "download":url,
            "sourceDimensions":list(photo.size),
            "sameSourceUnsplashId":unsplash_id,
            "rightsVerifiedBy":"Commons CC0 page; immutable pre-2017 Unsplash photo ID"
        }

def prior_source(spec,old_by_id):
    """Offline re-authoring from a PREVIOUSLY licensed derivative, not raw source.

    Transparent fallback for Commons 429/Unsplash 401. Never claim this input
    is a fresh photograph or a new European geographic location.
    """
    cell=old_by_id[spec[0]]
    asset=ROOT/cell["art"]
    raw=asset.read_bytes()
    with Image.open(io.BytesIO(raw)) as im:
        previous=im.convert("RGB")
        if previous.size!=(1536,1024):
            raise RuntimeError("Prior scenic art has unexpected dimensions")
        # Uniform zoom permits a lower ground window without distorting trees.
        previous=previous.resize((1966,1311),Image.Resampling.LANCZOS)
    provenance=dict(cell["sourcePrimary"])
    provenance["intermediateArtSha256"]=hashlib.sha256(raw).hexdigest()
    provenance["inputType"]="previously-committed-unapproved-CC0-derivative"
    provenance["freshRawSourceDownloaded"]=False
    return previous,provenance

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # Reuse tested V267 photo provenance, crop, scene-composition and edge
    # color preflight; it records physical seams as UNVERIFIED.
    v267.OUT=OUT
    offline=os.environ.get("V267_OFFLINE_RECOMPOSE")=="1"
    if offline:
        prior=json.loads((OUT/"batch.json").read_text())
        old_by_id={c["id"]:c for c in prior["cells"]}
        if set(old_by_id)!={s[0] for s in SPEC}:
            raise RuntimeError("Offline source cache IDs do not match the eight existing cells")
        sources=[prior_source(s,old_by_id) for s in SPEC]
    else:
        sources=[licensed_source(s) for s in SPEC]
    if len({p["sourceSha256"] for _,p in sources})!=8:
        raise RuntimeError("Primary sources must be eight unique original photographs")
    cells=[]
    for i,(ident,title,origin,biome,focus,region,unsplash_id) in enumerate(SPEC):
        photo,provenance=sources[i]
        donor,donor_provenance=sources[(i+5)%8]
        primary,crop=ground.ground_window(photo,focus)
        foreground,foreground_crop=ground.ground_window(donor,(.43+.04*(i%3),.59))
        # A whole-scene layered perspective composition, NOT aerial tiles,
        # raster-distorted trees, clone imagery or a procedural heightmesh.
        composed,ground_report=ground.compose(primary,foreground)
        target=OUT/(ident+".webp")
        composed.save(target,"WEBP",quality=91,method=6)
        cells.append({
            "id":ident,"origin":list(origin),"biome":biome,
            "art":target.relative_to(ROOT).as_posix(),
            "assetSha256":hashlib.sha256(target.read_bytes()).hexdigest(),
            "visualGrammar":"v267-original-layered-landscape",
            "originalArtComposed":True,
            "sourcePrimary":dict(provenance,crop=crop),
            "sourceForeground":dict(donor_provenance,crop=foreground_crop),
            "sourceRegionReference":region,
            "sourceMethod":ground_report["method"]+(" (offline re-authoring of prior CC0 derivative; not a new raw photograph)" if offline else ""),
            "recomposedFromPreviousDerivative":offline,
            "groundRegistration":ground_report,
            "scenicSettlements":[],"strategicNodes":[],"provinceIds":[],
            "roadPorts":[],"roadSeamsVerified":False,
            "riverCrossingsVerified":False,"geoVerified":False,
            "historicalVerified":False,"historicallyVerified":False,
            "visuallyReviewed":False,"mobileWebkitRendered":False,
            "nativePlayable":False,"userApproved":False,
            "notes":"Unapproved terrain-aware photographic study, NOT approved V267-quality art; source location is not a historical survey or exact world-cell placement. No new roads. Sky, modern structures and material seams require manual visual review."
        })
    # Adjacent image-edge COLOR grading does not verify geometry or roads.
    edge=v267.harmonize_candidate_edge_light(cells)
    if len(edge["pairs"])!=7:
        raise RuntimeError("Expected seven adjacent pairs in second eight-cell chain")
    if len({c["assetSha256"] for c in cells})!=8:
        raise RuntimeError("Repeated art output")
    batch={
        "schema":"coe-v267-original-art-batch/v1","referenceCommit":REF,
        "status":"unapproved-native-ground-recomposition-from-prior-licensed-art" if offline else "unapproved-source-backed-European-scenic-art-study",
        "scenario":"geographic analogues from Europe; NOT 1780–1880 surveyed roads",
        "sourceDelivery":"prior committed licensed derivatives, no new downloads" if offline else "fresh source download",
        "cells":cells,"links":[],"decorativeInlays":[],
        "generatedCandidates":8,"originalArtComposed":8,
        "lightingEdgePairsGraded":7,"physicalTerrainSeamsVerified":0,
        "visuallyReviewed":0,"roadConnected":0,"mobileWebkitRendered":0,
        "historicallyVerified":0,"nativePlayable":0,"userApproved":0,
        "netFinishedToday":0
    }
    (OUT/"batch.json").write_text(json.dumps(batch,indent=2,ensure_ascii=False)+"\n")
    board=Image.new("RGB",(1536,4*550),(20,30,26))
    draw=ImageDraw.Draw(board)
    for i,c in enumerate(cells):
        x=(i%2)*768;y=(i//2)*550
        image=Image.open(ROOT/c["art"]).resize((768,512),Image.Resampling.LANCZOS)
        board.paste(image,(x,y+24))
        draw.text((x+8,y+5),c["id"]+" · "+c["biome"],fill="#f5e2bd")
        draw.text((x+8,y+538),"SCENIC CANDIDATE · ROADS / HISTORY / PLAYABILITY UNVERIFIED",fill="#f5e2bd")
    board.save(OUT/"eight-europe-scenes-contact.webp","WEBP",quality=87,method=6)
    print(json.dumps({"candidateMetadata":8,"originalArtComposed":8,
                      "edgeColorPairs":7,"roadConnected":0,"nativePlayable":0,
                      "historicallyVerified":0,"finished":0}))
if __name__=="__main__":
    main()
