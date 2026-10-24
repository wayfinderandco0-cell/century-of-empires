#!/usr/bin/env python3
"""V157 synthetic regression: real-source claims require separate CI download."""
import copy
import json
import tempfile
from pathlib import Path
from PIL import Image
from v156_modern_exclusion import SIZE,make_mask
from v157_residual_modern_audit import (
    ROOF_REGIONS,DATE_MARKS,NOT_APPROVED,validate_observations,
    extend_mask,coverage,produce_verified,verify_artifact,sha)

negative=0
def reject(fn,label):
    global negative
    try: fn()
    except (ValueError,TypeError,KeyError,FileNotFoundError,OSError): negative+=1
    else: raise AssertionError("Fail-closed check accepted: "+label)

with tempfile.TemporaryDirectory() as temp:
    root=Path(temp);base_dir=root/"v156";out=root/"v157";base_dir.mkdir()
    base_mask=make_mask()
    original=Image.new("RGBA",SIZE,(80,117,65,255))
    original.putalpha(base_mask)
    base_mask.save(base_dir/"modern-exclusion-mask.png")
    original.save(base_dir/"modern-exclusion-reference.png")
    manifest={
        "sourceMosaicSha256":"synthetic-source-not-real",
        "maskFile":"modern-exclusion-mask.png",
        "referenceFile":"modern-exclusion-reference.png",
        "maskSha256":sha(base_dir/"modern-exclusion-mask.png"),
        "referenceSha256":sha(base_dir/"modern-exclusion-reference.png"),
        **NOT_APPROVED,
    }
    (base_dir/"manifest.json").write_text(json.dumps(manifest))
    assert validate_observations()
    new_mask=extend_mask(base_mask)
    assert all(new_mask.getpixel(((box[0]+box[2])//2,(box[1]+box[3])//2))==0 for _,box in ROOF_REGIONS)
    assert all(new_mask.getpixel(p)==0 for p in DATE_MARKS)
    assert all(new_mask.getpixel((x,y))<=base_mask.getpixel((x,y))
               for x in (0,180,550,780,1100,1400,1700,2100,2303)
               for y in (0,125,350,500,690,767))
    old_coverage=coverage(base_mask)
    new_coverage=coverage(new_mask)
    assert all(new_coverage[k] < old_coverage[k] for k in old_coverage)
    report=produce_verified(base_dir,out)
    assert verify_artifact(base_dir,out)
    assert report["productionApproved"] is False
    assert report["periodArtComplete"] is False
    assert report["gameRouteGeoregistered"] is False
    assert report["modernInfrastructureCleared"] is False
    assert report["manualArtReviewRequired"] is True

    reject(lambda:validate_observations(ROOF_REGIONS[:-1]),"removed modern roof")
    reject(lambda:validate_observations(ROOF_REGIONS+ROOF_REGIONS[-1:]),"duplicated roof")
    shifted=list(ROOF_REGIONS);shifted[0]=(shifted[0][0],(166,636,432,767))
    reject(lambda:validate_observations(tuple(shifted)),"shifted roof")
    reject(lambda:validate_observations(ROOF_REGIONS,DATE_MARKS[:-1]),"removed date")
    reject(lambda:validate_observations(ROOF_REGIONS,DATE_MARKS+((500,500),)),"invented date")
    reject(lambda:validate_observations(ROOF_REGIONS,((315,416),)+DATE_MARKS[1:]),"moved date")
    reject(lambda:extend_mask(Image.new("RGB",SIZE)),"wrong base format")
    reject(lambda:extend_mask(Image.new("L",(100,100))),"wrong base size")
    reject(lambda:extend_mask(Image.new("L",SIZE,128)),"nonbinary source")
    for key in ("productionApproved","periodArtComplete","gameRouteGeoregistered",
                "modernInfrastructureCleared","historicalRoadEvidence"):
        bad=copy.deepcopy(report);bad[key]=True
        (out/"manifest.json").write_text(json.dumps(bad))
        reject(lambda:verify_artifact(base_dir,out),"forged approval "+key)
    bad=copy.deepcopy(report);bad["sourceSectorRetainedFractions"]["source-west"]=0.9
    (out/"manifest.json").write_text(json.dumps(bad))
    reject(lambda:verify_artifact(base_dir,out),"forged source coverage")
    bad=copy.deepcopy(report);bad["inventedRoad"]=[100,200]
    (out/"manifest.json").write_text(json.dumps(bad))
    reject(lambda:verify_artifact(base_dir,out),"unexpected road field")
    (out/"manifest.json").write_text(json.dumps(report))
    for name in ("residual-modern-mask.png","residual-modern-reference.png"):
        path=out/name;original_bytes=path.read_bytes()
        path.write_bytes(b"bad-image")
        reject(lambda:verify_artifact(base_dir,out),"corrupted output "+name)
        path.write_bytes(original_bytes)
    assert verify_artifact(base_dir,out)
print(f"V157 PASS: 3 source sectors, 7 observed modern roof exclusions, 11 observed date marks, {negative} fail-closed negative tests; synthetic source ONLY")
