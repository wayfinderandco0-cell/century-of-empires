#!/usr/bin/env python3
"""V234: search untouched native photographs for a full V123 road corridor.
No road painting, image warp, repeated source patches, or historic-road claims.
"""
import argparse,hashlib,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from v232_route_ground_preflight import SIZE,sample_polyline,ground_mask,inspect
from v233_source_guided_art import verified_roads,FALSE_FLAGS

def native_candidates(image,road,stride=48,max_review=24):
    rgb=np.asarray(image.convert("RGB"))
    h,w=rgb.shape[:2];cw,ch=SIZE
    if w<cw or h<ch:raise ValueError("Source cannot supply native 1536x1024 pixels")
    mask,_=ground_mask(image)
    clear=cv2.boxFilter(mask.astype(np.float32),-1,(25,25),
                        normalize=True,borderType=cv2.BORDER_CONSTANT)
    xy=np.rint(np.asarray(sample_polyline(road))).astype(np.int32)
    xy[:,0]=np.clip(xy[:,0],0,cw-1)
    xy[:,1]=np.clip(xy[:,1],0,ch-1)
    xs=list(range(0,w-cw+1,stride));ys=list(range(0,h-ch+1,stride))
    if xs[-1]!=w-cw:xs.append(w-cw)
    if ys[-1]!=h-ch:ys.append(h-ch)
    ox,oy=np.meshgrid(xs,ys)
    offsets=np.stack([ox.ravel(),oy.ravel()],axis=1)
    scores=np.zeros(len(offsets),np.float32)
    for start in range(0,len(offsets),1024):
        batch=offsets[start:start+1024]
        sx=batch[:,0,None]+xy[None,:,0]
        sy=batch[:,1,None]+xy[None,:,1]
        fractions=clear[sy,sx]
        passable=fractions>=.67
        openness=passable.mean(axis=1)
        run=np.zeros(len(batch),np.int32)
        longest=np.zeros(len(batch),np.int32)
        for j in range(passable.shape[1]):
            run=np.where(passable[:,j],0,run+1)
            longest=np.maximum(longest,run)
        scores[start:start+len(batch)]=(openness-.0009*longest*4+
                                          .1*fractions.mean(axis=1))
    ranked=[]
    for index in np.argsort(-scores,kind="stable")[:max_review]:
        x,y=map(int,offsets[index])
        crop=Image.fromarray(rgb[y:y+ch,x:x+cw])
        metrics,_=inspect(crop,road,"candidate")
        ranked.append({"crop":[x,y,x+cw,y+ch],
                       "selectionScore":round(float(scores[index]),5),
                       "ground":metrics})
    return ranked

def evaluate_sources(sources,output,source_manifest=None):
    roads=verified_roads()
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    result={"version":234,"method":"unmodified native full-scene photo crop",
            "sourceRegisteredToV123":False,"historicalRoadsVerified":False,
            "bridgeBanksVerified":False,"humanVisualApproval":False,
            "productionApproved":False,"tiles":{}}
    hashes=[]
    for tile in ("west","south"):
        path=Path(sources[tile]);raw=path.read_bytes()
        sha=hashlib.sha256(raw).hexdigest()
        if source_manifest:
            info=source_manifest[tile]
            if sha!=info["sha256"]:raise ValueError("STOP: "+tile+" source SHA256 mismatch")
            if not all(info.get(k) for k in ("author","sourcePage","license")):
                raise ValueError("STOP: missing source attribution for "+tile)
        if sha in hashes:raise ValueError("STOP: duplicate original source across cells")
        hashes.append(sha)
        with Image.open(path) as image:
            ranked=native_candidates(image,roads[tile])
            selected=next((r for r in ranked if r["ground"]["necessaryRoadGroundGate"]),None)
            best=selected or ranked[0];crop=best["crop"]
            scene=image.convert("RGB").crop(tuple(crop))
            _,review=inspect(scene,roads[tile],tile)
            review.save(output/(tile+"-native-road-review.jpg"),quality=91)
            if selected:
                scene.save(output/(tile+"-native-photo-candidate.webp"),
                           "WEBP",quality=93,method=6)
            result["tiles"][tile]={"status":"GROUND_PREFLIGHT_ONLY" if selected else "REJECTED",
                                   "originalSha256":sha,
                                   "provenance":source_manifest[tile] if source_manifest else "UNVERIFIED_LOCAL_FIXTURE",
                                   "nativeCrop":crop,
                                   "review":tile+"-native-road-review.jpg",
                                   "candidateFile":tile+"-native-photo-candidate.webp" if selected else None,
                                   "topCandidates":ranked[:3],**FALSE_FLAGS}
    result["bothNecessaryGroundGatesPass"]=all(t["status"]=="GROUND_PREFLIGHT_ONLY"
                                               for t in result["tiles"].values())
    (output/"v234-report.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--west",type=Path,required=True)
    p.add_argument("--south",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--manifest",type=Path)
    p.add_argument("--enforce",action="store_true")
    a=p.parse_args()
    if a.enforce and not a.manifest:
        raise SystemExit("STOP: enforced production preflight requires source provenance")
    manifest=json.loads(a.manifest.read_text()) if a.manifest else None
    r=evaluate_sources({"west":a.west,"south":a.south},a.output,manifest)
    print(json.dumps(r,indent=2))
    if a.enforce and not r["bothNecessaryGroundGatesPass"]:
        raise SystemExit("RED: neither scene may be promoted without BOTH full-source ground gates")
if __name__=="__main__":main()
