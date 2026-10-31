#!/usr/bin/env python3
"""Second 8-cell European Alpine original-layered scenic ART STUDY.

Uses eight additional individually CC0-verified oblique European landscape
sources; never samples protected WEST/MATREI/SOUTH or the first eight studies.
Natural perspective/trees are preserved. There are NO invented cartways,
settlements, river crossings, conquest nodes or historical route claims.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
import v267_original_neighbor_art as v267

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-grid/v267-europe-neighbor-b"
REF=v267.REF
# All locations are V123 *local scenic atlas coordinates*, NOT geodetic
# coordinates. Source landscapes are geographic analogues, not surveyed tiles.
# Titles have individually documented CC0 licenses on Wikimedia Commons.
SPEC=[
 ("southern-terraces","Tyrol, Austria (Unsplash).jpg",(0,3072),"tyrolean-wooded-valley",(.48,.60),"Tyrol, Austria"),
 ("southern-high-meadow","Lost in the mountains of South Tyrol (Unsplash).jpg",(1536,3072),"south-tyrol-high-meadow",(.51,.57),"South Tyrol, Italy"),
 ("dolomite-south-ridge","Snowy mountain in the Dolomites (Unsplash).jpg",(3072,3072),"dolomite-limestone-ridge",(.49,.56),"Dolomites, Italy"),
 ("dolomite-south-pass","Passo Sella, Dolomites (Unsplash).jpg",(4608,3072),"dolomite-open-pass",(.51,.60),"Passo Sella, Italy"),
 ("alpine-southwest-slope","Swiss Alps, Switzerland (Unsplash).jpg",(6144,3072),"swiss-alpine-green-slope",(.48,.57),"Troistorrents, Switzerland"),
 ("alpine-east-summit","Dramatic Alpine scenery (Unsplash).jpg",(6144,0),"alpine-high-ridge",(.50,.53),"Kleine Scheidegg, Switzerland"),
 ("alpine-east-lakeside","Mountain peak in a lake (Unsplash).jpg",(6144,1024),"austrian-lakeside-forest",(.50,.55),"Kitzbühel, Austria"),
 ("alpine-east-snowfield","Alpine village landscape (Unsplash).jpg",(6144,2048),"snowy-alpine-settlement-reference",(.49,.58),"Livigno, Italy"),
]
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # Reuse tested V267 photo provenance, crop, scene-composition and edge
    # color preflight; it records physical seams as UNVERIFIED.
    v267.OUT=OUT
    sources=[v267.commons(s[1]) for s in SPEC]
    if len({p["sourceSha256"] for _,p in sources})!=8:
        raise RuntimeError("Primary sources must be eight unique original photographs")
    cells=[]
    for i,(ident,title,origin,biome,focus,region) in enumerate(SPEC):
        photo,provenance=sources[i]
        donor,donor_provenance=sources[(i+5)%8]
        primary,crop=v267.window(photo,focus)
        foreground,foreground_crop=v267.window(donor,(.43+.04*(i%3),.59))
        # A whole-scene layered perspective composition, NOT aerial tiles,
        # raster-distorted trees, clone imagery or a procedural heightmesh.
        composed=v267.compose(primary,foreground,i+23)
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
            "sourceMethod":"Unique CC0 oblique European landscape source, secondary photographic foreground layer, graded illumination, preserved natural perspective",
            "scenicSettlements":[],"strategicNodes":[],"provinceIds":[],
            "roadPorts":[],"roadSeamsVerified":False,
            "riverCrossingsVerified":False,"geoVerified":False,
            "historicalVerified":False,"historicallyVerified":False,
            "visuallyReviewed":False,"mobileWebkitRendered":False,
            "nativePlayable":False,"userApproved":False,
            "notes":"Unapproved scenic source-composition study; photograph location is not a historical survey or exact world-cell placement. No new roads. Modern structures or seasonality require visual review."
        })
    # Adjacent image-edge COLOR grading does not verify geometry or roads.
    edge=v267.harmonize_candidate_edge_light(cells)
    if len(edge["pairs"])!=7:
        raise RuntimeError("Expected seven adjacent pairs in second eight-cell chain")
    if len({c["assetSha256"] for c in cells})!=8:
        raise RuntimeError("Repeated art output")
    batch={
        "schema":"coe-v267-original-art-batch/v1","referenceCommit":REF,
        "status":"unapproved-source-backed-European-scenic-art-study",
        "scenario":"geographic analogues from Europe; NOT 1780–1880 surveyed roads",
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
