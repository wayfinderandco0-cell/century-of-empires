#!/usr/bin/env python3
"""Fail-closed tests: V197 high-resolution geographic SOURCE materials."""
import copy
import json
import tempfile
from pathlib import Path
from PIL import Image
import v197_highres_material_samples as v

count = 0
def check(label, fn):
    global count
    fn()
    count += 1
    print("PASS", label)

def reject(fn):
    try:
        fn()
    except (ValueError, FileNotFoundError, KeyError):
        return
    raise AssertionError("forged provenance or approval was accepted")

def fixture(folder):
    m = v.plan()
    for i, sample in enumerate(m["samples"]):
        for j, tile in enumerate(sample["tiles"]):
            color = ((i*61+j*13+30)%255, (i*47+j*19+65)%255, (i*23+j*37+90)%255)
            path = folder/tile["name"]
            Image.new("RGB", (256,256), color).save(path, format="JPEG")
            tile["sha256"] = v.sha(path)
            tile["byteCount"] = path.stat().st_size
    return m

def geographic():
    m = v.plan()
    assert m["zoom"] == 18 and m["materialPatchPixels"] == [512,512]
    assert m["parentGridOriginXYZ"] == [8712,5752,14]
    assert len(m["samples"]) == 3
    xyz = [tuple(t["tileXYZ"]) for s in m["samples"] for t in s["tiles"]]
    assert len(set(xyz)) == 12
    assert all(s["nativeOriginXYZ"][2] == 18 for s in m["samples"])
    assert all(s["footprintLonLat"][0] < s["footprintLonLat"][2]
               and s["footprintLonLat"][1] < s["footprintLonLat"][3]
               for s in m["samples"])
    assert v.validate(m)

def not_historic():
    m = v.plan()
    assert all(m[k] is False for k in v.FALSE_FLAGS)
    assert m["notGameOctagonCenters"] and m["modernRoadRailRoofMaskNotCertified"]
    assert m["naturalCoverRequiresManualReview"]
    assert m["requiredAttribution"] == "Datenquelle: basemap.at"

def forbid_forgery():
    for mutate in (
        lambda m: m.update(productionApproved=True),
        lambda m: m.update(gameOctagonsGeoregistered=True),
        lambda m: m.update(modernInfrastructureExcluded=True),
        lambda m: m.update(physicalIPhoneApproved=True),
        lambda m: m.update(modernRoadRailRoofMaskNotCertified=False),
        lambda m: m.update(requiredAttribution=""),
        lambda m: m["samples"][0].update(overviewPixelXY=[700,900]),
        lambda m: m["samples"][0]["tiles"][0].update(tileXYZ=[1,2,18]),
        lambda m: m["samples"][0]["tiles"][0].update(url="https://example.invalid/x.jpeg"),
        lambda m: m["samples"].pop(),
        lambda m: m.update(historicalRoutes=[[0,0],[1,1]]),
    ):
        m = copy.deepcopy(v.plan())
        mutate(m)
        reject(lambda: v.validate(m))

def synthetic_roundtrip():
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        m = fixture(folder)
        v.produce(m,folder)
        assert v.verify(folder)
        assert len({s["imageSha256"] for s in m["samples"]}) == 3
        for s in m["samples"]:
            with Image.open(folder/s["image"]) as im:
                assert im.size == (512,512)
            assert s["reviewMetrics"]["periodSafe"] is False
            assert s["reviewMetrics"]["naturalCoverVerified"] is False
        with Image.open(folder/m["contactSheet"]) as im:
            assert im.size == (1536,554)

def corrupt_jpeg():
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        m = fixture(folder)
        v.produce(m,folder)
        (folder/m["samples"][1]["tiles"][2]["name"]).write_bytes(b"forged")
        reject(lambda: v.verify(folder))

def corrupt_image():
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        m = fixture(folder)
        v.produce(m,folder)
        p = folder/m["samples"][0]["image"]
        with Image.open(p) as im:
            changed = im.copy()
        changed.putpixel((20,20),(255,0,0))
        changed.save(p)
        reject(lambda: v.verify(folder))

def corrupt_manifest():
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        m = fixture(folder)
        v.produce(m,folder)
        p = folder/"manifest.json"
        manifest = json.loads(p.read_text())
        manifest["samples"][0]["reviewMetrics"]["periodSafe"] = True
        p.write_text(json.dumps(manifest))
        reject(lambda: v.verify(folder))

def missing_tile():
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        m = fixture(folder)
        (folder/m["samples"][0]["tiles"][0]["name"]).unlink()
        reject(lambda: v.assemble(m["samples"][0],folder))

for label, fn in (
    ("three unique zoom-18 geographic source footprints",geographic),
    ("license retained and every GAME/historical approval false",not_historic),
    ("forged coordinates, licensing and approvals rejected",forbid_forgery),
    ("12 native JPEGs produce 3 verified 512px materials",synthetic_roundtrip),
    ("source JPEG tampering rejected",corrupt_jpeg),
    ("material PNG tampering rejected",corrupt_image),
    ("period-safe approval forgery rejected",corrupt_manifest),
    ("missing native imagery rejected",missing_tile),
):
    check(label,fn)
print(f"V197 {count} tests PASS; real source acquisition separately required")
