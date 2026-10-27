#!/usr/bin/env python3
"""V240 tests: actual road pixels and independent geometry both required."""
import hashlib
import io
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from PIL import Image,ImageDraw
import v240_cartway_trace_registration as m

ROAD=[[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],[980,515],
      [890,535],[784,551],[680,560],[570,540],[470,520],[370,522],[275,550]]

def pack(img):
    f=io.BytesIO();img.save(f,"PNG");return f.getvalue()
def manifest(raw,trace=ROAD):
    return {"sourceSha256":hashlib.sha256(raw).hexdigest(),
            "annotationMethod":"human-visible-road-trace","visibleRoadPoints":trace}

def test():
    im=Image.new("RGB",m.SIZE,(80,140,60))
    ImageDraw.Draw(im).line([tuple(p) for p in ROAD],fill=(145,104,68),width=18)
    raw=pack(im);r=m.verify(im,raw,manifest(raw),ROAD)
    assert r["necessaryVisibleCartwayGate"],r
    assert not r["annotationIndependentVerified"] and not r["productionApproved"]
    assert r["p95MisalignmentPx"]==0 and r["longestNoEarthRunPx"]==0
    # Grass alone is NOT a physical road, even with identical trace points.
    blank=Image.new("RGB",m.SIZE,(80,140,60));b=pack(blank)
    assert not m.verify(blank,b,manifest(b),ROAD)["necessaryVisibleCartwayGate"]
    # Physically visible road is unusable if it is 70px away from gameplay route.
    moved=[[x,y-70] for x,y in ROAD]
    im2=Image.new("RGB",m.SIZE,(80,140,60))
    ImageDraw.Draw(im2).line([tuple(p) for p in moved],fill=(145,104,68),width=18)
    raw2=pack(im2)
    assert not m.verify(im2,raw2,manifest(raw2,moved),ROAD)["necessaryVisibleCartwayGate"]
    assert m.geometry(ROAD,moved)["p95MisalignmentPx"]>40
    # Missing far-bank continuation/endpoints cannot be silently inferred.
    assert not m.geometry(ROAD,ROAD[2:-2])["geometryPass"]
    for bad in [dict(manifest(raw),sourceSha256="0"*64),
                dict(manifest(raw),annotationMethod="auto-generated-from-V123")]:
        try:m.verify(im,raw,bad,ROAD)
        except ValueError:pass
        else:raise AssertionError("Tampering accepted")
    print("PASS V240 6 road/source/endpoint/negative controls; production RED")
if __name__=="__main__":test()
