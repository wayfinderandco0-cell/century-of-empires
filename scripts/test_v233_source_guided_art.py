#!/usr/bin/env python3
"""V233 synthetic-only controls; no production or historical approval."""
import hashlib, tempfile
from pathlib import Path
from PIL import Image
import numpy as np
from v233_source_guided_art import warp, verified_roads, evaluate, FALSE_FLAGS, SIZE

def rejects(fn, expected):
    try:fn()
    except ValueError as e:assert expected in str(e),(expected,e)
    else:raise AssertionError("Invalid source accepted: "+expected)

def main():
    roads=verified_roads()
    assert len(roads["west"])==13 and len(roads["south"])==12
    image=Image.new("RGB",SIZE,(126,158,74)) # synthetic fixture only
    for tile in ("west","south"):
        result,metrics=warp(image,roads[tile],roads[tile])
        assert np.array_equal(np.asarray(result),np.asarray(image))
        assert metrics["maximumGuideShiftPx"]==0
    west=roads["west"]
    moved=[[x,y+10] for x,y in west]
    result,m=warp(image,west,moved)
    assert result.size==SIZE and m["foldoverFraction"]==m["invalidSourceFraction"]==0
    rejects(lambda:warp(image,west,[[x,y+120] for x,y in west]),"deformation")
    rejects(lambda:warp(image,west,moved[:-1]),"one source point")
    rejects(lambda:warp(image,west,[[float("nan"),y] for x,y in west]),"invalid")
    rejects(lambda:warp(Image.new("RGB",(100,100)),west,west),"1536x1024")
    assert all(v is False for v in FALSE_FLAGS.values())
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        for tile in ("west","south"):image.save(root/(tile+".png"))
        paths={tile:root/(tile+".png") for tile in ("west","south")}
        manifest={tile:{"sha256":hashlib.sha256(paths[tile].read_bytes()).hexdigest(),
                        "guide":roads[tile]} for tile in ("west","south")}
        report=evaluate(paths,manifest,root/"out")
        assert report["bothNecessaryArtGatesPass"]
        assert report["productionApproved"] is False
        assert all(x["status"]=="ART_STUDY_ONLY" for x in report["tiles"].values())
        manifest["south"]["sha256"]="0"*64
        rejects(lambda:evaluate(paths,manifest,root/"bad"),"SHA-256")
    print("V233 synthetic whole-scene warp, V123 pin, ground, tamper and false-approval controls PASS")
if __name__=="__main__":main()
