#!/usr/bin/env python3
"""Validate REAL exported glTF border buffers and raster-to-mesh agreement.

Unlike the old check, this reads BOTH independent tile binaries, not two
slices of the same original global array. Zero approvals are implied.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

TW, TH, STEP, COLS, ROWS = 1536, 1024, 16, 4, 2

def tile_buffers(out, cell):
    gltf=json.loads((out/cell["gltf"]).read_text())
    raw=(out/cell["binary"]).read_bytes()
    arrays=[]
    for index in (0,1):
        accessor=gltf["accessors"][index]
        view=gltf["bufferViews"][accessor["bufferView"]]
        offset=view.get("byteOffset",0)+accessor.get("byteOffset",0)
        count=accessor["count"]
        arrays.append(np.frombuffer(raw,dtype="<f4",count=count*3,offset=offset)
                      .reshape(TH//STEP+1,TW//STEP+1,3).copy())
    origin=np.array(gltf["nodes"][0]["translation"],dtype=np.float32)
    return arrays[0]+origin,arrays[1]

def verify(out):
    mesh=json.loads((out/"heightmesh-manifest.json").read_text())
    art=json.loads((out/"manifest.json").read_text())
    field_file=out/"heightfield-step16.npy"
    z=np.load(field_file,allow_pickle=False)
    assert z.shape==(ROWS*TH//STEP+1,COLS*TW//STEP+1)
    sha=hashlib.sha256(field_file.read_bytes()).hexdigest()
    assert sha==mesh["paintedHeightfieldSha256"]==art["meshSourceHeightfieldSha256"]
    assert mesh["geometryUsesExactPaintedHeightfield"] and art["meshGroundArtAligned"]
    tiles={}
    for c in mesh["cells"]:
        col,row=map(int,c["id"].split("-")[1:])
        p,n=tile_buffers(out,c)
        expected=z[row*TH//STEP:(row+1)*TH//STEP+1,
                   col*TW//STEP:(col+1)*TW//STEP+1]
        assert np.max(np.abs(p[:,:,1]-expected))<.00001,c["id"]
        assert np.isfinite(n).all()
        assert np.max(np.abs(np.linalg.norm(n,axis=2)-1))<.00001
        tiles[(col,row)]=(p,n)
    assert len(tiles)==8
    checks=[]
    for row in range(ROWS):
        for col in range(COLS-1):
            pa,na=tiles[(col,row)]
            pb,nb=tiles[(col+1,row)]
            posdiff=float(np.max(np.abs(pa[:,-1,:]-pb[:,0,:])))
            normdiff=float(np.max(np.abs(na[:,-1,:]-nb[:,0,:])))
            assert posdiff<.00001 and normdiff<.00001,(col,row,posdiff,normdiff)
            checks.append({"a":f"pilot-{col}-{row}","b":f"pilot-{col+1}-{row}",
                           "positionError":posdiff,"normalError":normdiff})
    for col in range(COLS):
        pa,na=tiles[(col,0)]
        pb,nb=tiles[(col,1)]
        posdiff=float(np.max(np.abs(pa[-1,:,:]-pb[0,:,:])))
        normdiff=float(np.max(np.abs(na[-1,:,:]-nb[0,:,:])))
        assert posdiff<.00001 and normdiff<.00001,(col,posdiff,normdiff)
        checks.append({"a":f"pilot-{col}-0","b":f"pilot-{col}-1",
                       "positionError":posdiff,"normalError":normdiff})
    assert len(checks)==10
    # Road ports are only geometry-aligned provisional art, not historical
    # roads or enabled graph edges. Every port must sit on a verified seam.
    assert len(art["seams"])==8
    names={(c["a"],c["b"]) for c in checks}
    for seam in art["seams"]:
        assert (seam["a"],seam["b"]) in names
        v=seam.get("roadCrossingLocalY",seam.get("roadCrossingLocalX"))
        assert v and len(v)<16
        assert all((256<=n<=768) if seam["side"]=="east-west"
                   else (256<=n<=1280) for n in v)
    assert mesh["finishedToday"]==mesh["nativeGamePlayable"]==mesh["visuallyApprovedV267"]==0
    report={"independentBinaryPositionAndNormalSeams":len(checks),
            "artAndMeshGroundHeightAligned":len(tiles),
            "provisionalArtRoadSeams":len(art["seams"]),
            "historicallyVerified":0,"newlyPlayable":0,"finishedToday":0,
            "checks":checks}
    (out/"verified-binary-seams.json").write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!="checks"}))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("generated/v267-relief-pilot"))
    verify(p.parse_args().out)
