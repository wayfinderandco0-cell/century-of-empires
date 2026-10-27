#!/usr/bin/env python3
"""V234 synthetic fixtures: native-crop geometry, source integrity, RED gates."""
import hashlib,tempfile
from pathlib import Path
import numpy as np
from PIL import Image
from v234_native_corridor_crop import native_candidates,evaluate_sources
from v233_source_guided_art import verified_roads

def rejects(fn,expected):
    try:fn()
    except ValueError as e:assert expected in str(e),(expected,str(e))
    else:raise AssertionError("invalid input accepted: "+expected)

def main():
    roads=verified_roads()
    assert len(roads["west"])==13 and len(roads["south"])==12
    array=np.full((1400,2000,3),(146,146,146),dtype=np.uint8)
    array[180:1280,280:1920]=(126,158,74)
    image=Image.fromarray(array)
    for tile in ("west","south"):
        ranked=native_candidates(image,roads[tile],stride=64)
        assert ranked[0]["ground"]["necessaryRoadGroundGate"],(tile,ranked[0])
        assert ranked[0]["crop"][2]-ranked[0]["crop"][0]==1536
        assert ranked[0]["crop"][3]-ranked[0]["crop"][1]==1024
    rejects(lambda:native_candidates(Image.new("RGB",(800,800)),roads["west"]),
            "native 1536x1024")
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);sources={};manifest={}
        for tile in ("west","south"):
            path=root/(tile+".png")
            arr=array.copy()
            arr[1200:1220,100:120]=(255,0,0) if tile=="west" else (0,0,255)
            Image.fromarray(arr).save(path)
            sources[tile]=path
            manifest[tile]={"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                            "author":"synthetic test fixture","sourcePage":"local-only",
                            "license":"TEST_FIXTURE_NOT_REAL_SOURCE"}
        report=evaluate_sources(sources,root/"out",manifest)
        assert report["bothNecessaryGroundGatesPass"]
        assert report["productionApproved"] is False
        for tile in ("west","south"):
            t=report["tiles"][tile]
            with Image.open(root/"out"/t["candidateFile"]) as actual:
                with Image.open(sources[tile]) as original:
                    expected=original.crop(tuple(t["nativeCrop"]))
                    assert actual.size==expected.size==(1536,1024)
        manifest["south"]["sha256"]="0"*64
        rejects(lambda:evaluate_sources(sources,root/"bad",manifest),"SHA256 mismatch")
        manifest["south"]["sha256"]=hashlib.sha256(sources["south"].read_bytes()).hexdigest()
        manifest["west"]["author"]=""
        rejects(lambda:evaluate_sources(sources,root/"bad2",manifest),"source attribution")
    print("V234 native crop, 2-cell clearance, provenance, tamper and RED controls PASS")
if __name__=="__main__":main()
