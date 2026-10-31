#!/usr/bin/env python3
"""Source-pixel road evidence survey across an eight-cell German photo block.

The photographed 2025 farm road is REAL, but this algorithmic candidate
centerline is NOT human verified, historically established, or a game route.
Never paint its path into the source artwork or activate V123/V94 movement.
"""
from __future__ import annotations
import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"terrain-grid/factory-photo/dulmen-road-8"
W,H=1536,1024
STEP=8
YMIN,YMAX=256//STEP,768//STEP

def candidate_path(image):
    """Locate neutral-colored native gravel bands; bridge tree occlusions.

    This is an observed-image segmentation HYPOTHESIS, not an approved road.
    The road is never repainted, only highlighted on a separate review sheet.
    """
    small=image.resize((image.width//STEP,H//STEP),Image.Resampling.BILINEAR)
    pix=small.load()
    sw=small.width
    anchors=[]
    for x in range(sw):
        good=[False]*(H//STEP)
        for y in range(32,124):
            r,g,b=pix[x,y]
            good[y]=r>105 and abs(r-g)<32 and abs(g-b)<45 and b>95
        # Gravel shadows and scattered vegetation interrupt the band; close
        # gaps shorter than 5 downsampled pixels without moving source art.
        y=33
        while y<124:
            if good[y] or not good[y-1]:
                y+=1
                continue
            stop=y
            while stop<124 and not good[stop] and stop-y<5:
                stop+=1
            if stop<124 and good[stop]:
                for j in range(y,stop):good[j]=True
            y=stop+1
        runs=[]
        begin=None
        for y in range(32,125):
            active=good[y] if y<124 else False
            if active and begin is None:begin=y
            if not active and begin is not None:
                if y-begin>=11:runs.append((begin,y,y-begin))
                begin=None
        best=max(runs,key=lambda r:r[2]) if runs else None
        anchors.append((best[0]+best[1])/2 if best and 14<=best[2]<54 else None)
    valid=[(x,y) for x,y in enumerate(anchors) if y is not None]
    if len(valid)<sw*.55:
        raise RuntimeError("Photographed neutral road band not sufficiently detected")
    # Fill temporary occlusions (especially trees) by interpolation, not by
    # hallucinating road pixels or adding a fake visual cartway.
    values=[0.0]*sw
    for x in range(sw):
        if anchors[x] is not None:
            values[x]=anchors[x]
            continue
        left=x-1
        while left>=0 and anchors[left] is None:left-=1
        right=x+1
        while right<sw and anchors[right] is None:right+=1
        if left<0:values[x]=anchors[right]
        elif right>=sw:values[x]=anchors[left]
        else:values[x]=anchors[left]+(anchors[right]-anchors[left])*(x-left)/(right-left)
    median=[sorted(values[max(0,x-6):min(sw,x+7)])[len(values[max(0,x-6):min(sw,x+7)])//2] for x in range(sw)]
    smooth=[sum(median[max(0,x-8):min(sw,x+9)])/len(median[max(0,x-8):min(sw,x+9)]) for x in range(sw)]
    return [(min(image.width-1,x*STEP+STEP//2),int(y*STEP+STEP//2)) for x,y in enumerate(smooth)]

def draw_route(d,points,color="#55e6e2",scale=1,ox=0,oy=0):
    coords=[(ox+x*scale,oy+y*scale) for x,y in points]
    # Dashed survey line, deliberately NOT a photographed/cartway paint layer.
    for i in range(0,len(coords)-1,2):
        d.line(coords[i:i+2],fill=color,width=max(1,round(3*scale)))
    return coords

def main():
    manifest=json.loads((OUT/"manifest.json").read_text())
    if len(manifest["cells"])!=8 or manifest["finishedToday"]!=0:
        raise RuntimeError("Expected unapproved eight-photo source block")
    cells={tuple(c["grid"]):c for c in manifest["cells"]}
    panorama=Image.new("RGB",(4*W,H))
    for col in range(4):
        c=cells[(7+col,8)]
        with Image.open(ROOT/c["image"]) as tile:
            if tile.size!=(W,H) or not c["modernRoadQuarantined"]:
                raise RuntimeError("Unsafe/missing modern source art")
            panorama.paste(tile.convert("RGB"),(col*W,0))
    points=candidate_path(panorama)
    # Source-native map-space coordinates, not guessed geographic longitude.
    def at_x(x):
        return min(points,key=lambda p:abs(p[0]-x))[1]
    seams=[]
    for col in (1,2,3):
        x=col*W
        y=at_x(x)
        seams.append({
            "a":f"eu-{6+col:02d}-08","b":f"eu-{7+col:02d}-08",
            "localA":[W,y],"localB":[0,y],"sourcePanorama":[x,y],
            "insideOctagonStraightSide":256<=y<=768,
            "sourceNativePixelsAdjacent":True,
            "algorithmicRoadHypothesis":True,
            "roadSurfaceHumanReviewed":False,
            "historicallyVerified":False,"routeEnabled":False
        })
    routes=[]
    for col in range(4):
        path=[[x-col*W,y] for x,y in points if col*W<=x<(col+1)*W]
        routes.append({"cellId":f"eu-{7+col:02d}-08","localCandidatePoints":path,
                       "surveyOnly":True,"gameplayEnabled":False})
    result={
        "schema":"coe-road-source-survey/v1",
        "sourceGroup":"dulmen-germany-drone-original-2025",
        "method":"PIL neutral-gravel band, occlusion interpolation and median smoothing; NOT an authenticated road segmentation",
        "imageSource":"2025 Dietmar Rabich Wikimedia Commons CC BY-SA 4.0",
        "sourceAttribution":"Dietmar Rabich / Wikimedia Commons / CC BY-SA 4.0; processed photographic crop and diagnostic overlays",
        "sourceManifest":"terrain-grid/factory-photo/dulmen-road-8/manifest.json",
        "imageSize":[4*W,H],
        "evidenceKind":"photographic source-road SURVEY CANDIDATE",
        "candidateSeams":seams,"routes":routes,
        "photoRoadVisibleInSource":True,
        "humanRoadContactApproved":False,
        "sourceExactlyV94Georeferenced":False,
        "historicallyVerified":False,
        "nativeGamePlayable":False,
        "roadConnectedFinishedCells":0,
        "finishedToday":0
    }
    (OUT/"road-source-survey.json").write_text(json.dumps(result,indent=2)+"\n")
    # Two different views: native photographic overview and seam contact crops.
    review=panorama.resize((3072,512),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(review)
    draw_route(d,points,scale=.5)
    for s in seams:
        x,y=s["sourcePanorama"]
        x=int(x*.5);y=int(y*.5)
        d.ellipse((x-9,y-9,x+9,y+9),outline="#f8d266",width=3)
        d.line((x,0,x,512),fill="#f8d266",width=2)
    canvas=Image.new("RGB",(3072,610),"#17271e")
    canvas.paste(review,(0,0))
    dd=ImageDraw.Draw(canvas)
    dd.text((20,525),"REAL 2025 SOURCE PHOTO / cyan = ALGORITHM ROAD HYPOTHESIS, NOT APPROVED ROAD",fill="#f6e6b7")
    dd.text((20,552),"3 exact source-pixel joins; crossings require human photo-contact review before ANY graph registration",fill="#f6e6b7")
    dd.text((20,579),"Dietmar Rabich / Wikimedia Commons / CC BY-SA 4.0. No source terrain or V123/V94 routes modified.",fill="#f6e6b7")
    canvas.save(OUT/"road-source-survey-review.webp","WEBP",quality=91,method=6)
    strip=Image.new("RGB",(3*1024,740),"#17271e")
    ds=ImageDraw.Draw(strip)
    for idx,s in enumerate(seams):
        x,y=s["sourcePanorama"]
        crop=panorama.crop((x-256,max(0,min(H-512,y-256)),x+256,max(0,min(H-512,y-256))+512))
        crop=crop.resize((1024,680),Image.Resampling.LANCZOS)
        strip.paste(crop,(idx*1024,0))
        ds.line((idx*1024+512,0,idx*1024+512,680),fill="#f8d266",width=2)
        ds.text((idx*1024+14,695),s["a"]+" > "+s["b"]+" | UNREVIEWED source road",fill="#f6e6b7")
    strip.save(OUT/"road-source-seam-contact.webp","WEBP",quality=91,method=6)
    (OUT/"road-source-survey.html").write_text("""<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dülmen road source survey</title><style>body{margin:0;background:#16271e;color:#f1e1bb;font:14px system-ui}main{max-width:1050px;margin:auto;padding:12px}img{display:block;width:100%;height:auto;margin:14px 0}small{color:#cbbd9e}</style><main><h2>Photographed road — unreviewed trace hypothesis</h2><p>Original 2025 source road is visible. Cyan path is a computer-generated survey suggestion, NOT a confirmed road centerline, 1780 route, or playable graph.</p><img src="road-source-survey-review.webp"><h3>Three real photo seam contacts</h3><img src="road-source-seam-contact.webp"><small>Dietmar Rabich / Wikimedia Commons / CC BY-SA 4.0; source-native terrain preserved; no gameplay enabled.</small></main></html>""")
    print(json.dumps({"sourceNativePhotoCells":8,"algorithmicCandidateSeams":len(seams),
                      "straightSideCandidates":sum(s["insideOctagonStraightSide"] for s in seams),
                      "reviewedRoads":0,"playable":0,"finishedToday":0}))
if __name__=="__main__":
    main()
