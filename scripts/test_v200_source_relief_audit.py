#!/usr/bin/env python3
"""V200 synthetic negative and positive regression checks (not visual acceptance)."""
import copy
import json
import tempfile
from pathlib import Path
from PIL import Image
import v200_source_relief_audit as v

CASES = {
 "western_forest_reference": ([139402,92095,18], [(40,65),(335,65),(40,290)]),
 "eastern_ridge_reference": ([139456,92082,18], [(20,35),(150,230),(335,300)]),
 "southern_forest_reference": ([139415,92178,18], [(20,30),(255,30),(15,250)])
}
count = 0


def fixture(root):
    src = root/"manifest.json"
    crops = []
    for group,(xyz,locations) in CASES.items():
        for i,(x,y) in enumerate(locations,1):
            rect = [x,y,x+160,y+160]
            crops.append({
                "name":f"{group}-clean-reference-{i:02d}.png",
                "sourceSample":group,"nativeOriginXYZ":xyz,
                "sourcePixelRect":rect,
                "footprintLonLat":v.native_bounds(xyz,rect),
                "annotatedFeaturePixelsInside":0,"maskClearancePixels":12,
                "eligibleForGameArt":False,
                "historicalNaturalCoverVerified":False,
                "modernFeaturesFullyExcluded":False
            })
    src.write_text(json.dumps({
        "version":199,"crs":"EPSG:3857","nativeZoom":18,
        "nativeCropPixels":[160,160],"requiredAttribution":"Datenquelle: basemap.at",
        "license":"CC BY 4.0","onlyAnnotatedFeaturesExcluded":True,
        **{k:False for k in v.REQUIRED_FALSE},"crops":crops
    }))
    data = {
        "boundsLonLat":v.BOUNDS,"heightGrid":v.GRID,"imageSize":v.SIZE,
        "elevationSource":"Copernicus DEM GLO-30 Public 2021",
        "landCoverSource":"ESA WorldCover 2021 v200",
        "elevationM":[1100+i%100 for i in range(260*300)],
        "treeGrid":[i%2 for i in range(260*300)]
    }
    vm = {k:data[k] for k in ("boundsLonLat","heightGrid","imageSize",
                               "elevationSource","landCoverSource")}
    v102 = {"version":102,"boundsLonLat":[11.43,47.075,11.625,47.19],
            "grid":[257,257]}
    v94 = {"version":"94","projection":"equirectangular",
           "extent":[-14,26,49,75],"atlasSize":[8192,6144]}
    return src,data,vm,v102,v94


def run(args):
    return v.audit(*args, expected_manifest_sha=None)


def test(label, fn):
    global count
    with tempfile.TemporaryDirectory() as tmp:
        fn(Path(tmp))
    count += 1
    print("PASS",label)


def reject(fn):
    try:fn()
    except (ValueError,KeyError,TypeError):
        return
    raise AssertionError("unsafe/tampered geography accepted")


def positive(tmp):
    a=fixture(tmp);r=run(a)
    assert len(r["sites"])==9 and len(r["siteGroups"])==3
    assert all(x["eligibleForGameArtwork"] is False for x in r["sites"])
    assert all(x["gameRoadOrBridgeVerified"] is False for x in r["sites"])
    assert all(x["v97ApproxElevationM"]>=1100 for x in r["sites"])
    assert 100<r["v97GridApproxCellMeters"][0]<200
    assert 200<r["v97GridApproxCellMeters"][1]<250
    assert all(r[k] is False for k in ("gameArtApproved","productionApproved"))
    im=tmp/"relief.webp";Image.new("RGB",tuple(v.SIZE),(90,105,90)).save(im)
    out=tmp/"review.png";v.render_map(r,im,out)
    with Image.open(out) as picture:
        assert picture.size==(1552,1897)


def false_approval(tmp):
    a=list(fixture(tmp));m=json.loads(a[0].read_text())
    m["gameArtApproved"]=True;a[0].write_text(json.dumps(m))
    reject(lambda:run(a))


def wrong_native_projection(tmp):
    a=list(fixture(tmp));m=json.loads(a[0].read_text())
    m["crops"][0]["nativeOriginXYZ"][2]=17
    a[0].write_text(json.dumps(m));reject(lambda:run(a))


def forged_geographic_footprint(tmp):
    a=list(fixture(tmp));m=json.loads(a[0].read_text())
    m["crops"][0]["footprintLonLat"][0]+=0.0001
    a[0].write_text(json.dumps(m));reject(lambda:run(a))


def source_site_outside_v97(tmp):
    a=list(fixture(tmp));m=json.loads(a[0].read_text())
    m["crops"][0]["nativeOriginXYZ"][0]=0
    m["crops"][0]["footprintLonLat"]=v.native_bounds(
        m["crops"][0]["nativeOriginXYZ"],m["crops"][0]["sourcePixelRect"])
    a[0].write_text(json.dumps(m));reject(lambda:run(a))


def v97_grid_tamper(tmp):
    a=list(fixture(tmp));a[1]["heightGrid"]=[261,300]
    reject(lambda:run(a))


def v102_frame_tamper(tmp):
    a=list(fixture(tmp));a[3]["boundsLonLat"][0]=11.2
    reject(lambda:run(a))


def v94_frame_tamper(tmp):
    a=list(fixture(tmp));a[4]["projection"]="WebMercator"
    reject(lambda:run(a))


def group_collapse(tmp):
    a=list(fixture(tmp));m=json.loads(a[0].read_text())
    first=m["crops"][0]["nativeOriginXYZ"]
    for row in m["crops"][3:6]:
        row["nativeOriginXYZ"]=first
        row["footprintLonLat"]=v.native_bounds(first,row["sourcePixelRect"])
    a[0].write_text(json.dumps(m));reject(lambda:run(a))


def coarse_resolution_not_bridge_survey(tmp):
    a=fixture(tmp);r=run(a)
    assert r["v97DataResolutionInsufficientForRoadOrBridgeSurvey"]
    assert r["v97ForestIsModern2021ProxyNot1780Evidence"]
    assert r["v102MaterialIsIllustrativeNotRegisteredV123GameArt"]
    assert r["v121PhotoRegistered"] is False and r["v123RoadsRegistered"] is False


for label,fn in [
 ("9 modern source sites on real geographic coordinate frames",positive),
 ("forged game art approval rejected",false_approval),
 ("wrong XYZ zoom rejected",wrong_native_projection),
 ("fabricated crop geolocation rejected",forged_geographic_footprint),
 ("source outside V97 atlas rejected",source_site_outside_v97),
 ("changed V97 grid rejected",v97_grid_tamper),
 ("changed V102 Navis footprint rejected",v102_frame_tamper),
 ("changed V94 atlas projection rejected",v94_frame_tamper),
 ("collapsed supposedly independent study regions rejected",group_collapse),
 ("coarse relief cannot prove historical road/bridge/forest",coarse_resolution_not_bridge_survey)
]:
    test(label,fn)
print("V200:",count,"synthetic fail-closed checks PASS; no GAME art approval")
