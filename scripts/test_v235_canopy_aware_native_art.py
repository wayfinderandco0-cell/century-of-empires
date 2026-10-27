#!/usr/bin/env python3
"""V235 regression: actual V234 screenshot crop and independent native-source tests."""
import hashlib
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image
import v232_route_ground_preflight as v232
import v234_native_corridor_crop as v234
from v235_canopy_aware_native_art import canopy_aware_ground_mask,evaluate

def rejects(fn,needle):
    try:fn()
    except ValueError as e:assert needle in str(e),str(e)
    else:raise AssertionError("Invalid input accepted: "+needle)

def main():
    roads=v232.source_roads()
    old=v232.ground_mask
    grass=Image.new("RGB",(1536,1024),(126,158,74))
    forest=Image.new("RGB",(1536,1024),(94,132,112))
    for tile in ("west","south"):
        v232.ground_mask=old
        assert v232.inspect(forest,roads[tile],tile)[0]["necessaryRoadGroundGate"], "V234 bug regression fixture"
        v232.ground_mask=canopy_aware_ground_mask
        assert not v232.inspect(forest,roads[tile],tile)[0]["necessaryRoadGroundGate"]
        assert v232.inspect(grass,roads[tile],tile)[0]["necessaryRoadGroundGate"]
    evidence=Path("terrain-v235/previous-v234-review")
    if evidence.exists():
        for tile in ("west","south"):
            with Image.open(evidence/(tile+"-native-photo-candidate.webp")) as image:
                v232.ground_mask=old
                prior=v232.inspect(image,roads[tile],tile)[0]
                v232.ground_mask=canopy_aware_ground_mask
                revised=v232.inspect(image,roads[tile],tile)[0]
                assert prior["necessaryRoadGroundGate"],(tile,prior)
                assert revised["necessaryRoadGroundGate"] is (tile=="west"),(tile,revised)
                print("Actual V234",tile,"previous",prior["openRoadbedArea"],
                      "corrected",revised["openRoadbedArea"],
                      "blocked",revised["longestBlockedRunPx"])
    v232.ground_mask=canopy_aware_ground_mask
    v234.ground_mask=canopy_aware_ground_mask
    arr=np.full((1400,2000,3),(146,146,146),dtype=np.uint8)
    arr[180:1280,280:1920]=(126,158,74)
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);sources={};manifest={}
        for tile in ("west","south"):
            copy=arr.copy()
            copy[1200:1220,100:120]=(255,0,0) if tile=="west" else (0,0,255)
            path=root/(tile+".png");Image.fromarray(copy).save(path)
            sources[tile]=path
            manifest[tile]={"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                            "author":"synthetic test fixture","sourcePage":"local",
                            "license":"TEST_ONLY"}
        result=evaluate(sources,root/"review",manifest)
        assert result["bothNecessaryLandcoverGatesPass"]
        assert result["productionApproved"] is False
        assert result["sourceRegisteredToV123"] is False
        manifest["south"]["sha256"]="0"*64
        rejects(lambda:evaluate(sources,root/"tampered",manifest),"SHA256 mismatch")
        manifest["south"]["sha256"]=hashlib.sha256(sources["south"].read_bytes()).hexdigest()
        manifest["west"]["author"]=""
        rejects(lambda:evaluate(sources,root/"unattributed",manifest),"attribution")
    print("V235 actual-crop regression, source-native search, tamper, RED tests PASS")

if __name__=="__main__":main()
