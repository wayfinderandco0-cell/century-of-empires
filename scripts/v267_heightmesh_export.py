#!/usr/bin/env python3
"""Export eight contiguous *real height-mesh* terrain candidates as glTF 2.0.

Uses the same V94 DEM and world-space cartway equations as the existing V267
relief study. The mesh is an additional technical 3D asset, NOT visual approval,
historical road verification, or integration into the playable V123 graph.
Octagon texture artwork is the native, original (non-photo) pilot PNG.
"""
from __future__ import annotations
import argparse, json, math, struct, hashlib
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter

TW, TH, COLS, ROWS, STEP = 1536, 1024, 4, 2, 16
C0, R0 = 7, 12
REF = "456107f28c8db1f87522bbc7511809b2a215f6fb"

def build_heightfield(root, out):
    """Read the SAME continuous ground heightfield used for the painted art.

    A separately generated DEM + sine field was a false geometry/art match.
    The renderer must run first at native scale and export this shared source.
    """
    source=out/"heightfield-step16.npy"
    if not source.exists():
        raise FileNotFoundError("Native original relief raster must export "+str(source))
    z=np.load(source,allow_pickle=False)
    expected=(TH*ROWS//STEP+1,TW*COLS//STEP+1)
    if z.shape!=expected or z.dtype!=np.float32 or not np.isfinite(z).all():
        raise ValueError(f"Invalid ground-art heightfield: {z.shape} {z.dtype}")
    x=np.arange(0,TW*COLS+1,STEP,dtype=np.float32)
    y=np.arange(0,TH*ROWS+1,STEP,dtype=np.float32)
    return x,y,z,None

def pack_gltf(tile, z, out, col, row, inlay=False):
    """Write indexed textured glTF with actual 3D vertices and shared edges."""
    if inlay:
        w = h = 512//STEP+1
        sx, sy = (col+1)*(TW//STEP)-256//STEP, TH//STEP-256//STEP
        world_x, world_y = (col+1)*TW-256, TH-256
    else:
        w, h = TW//STEP+1, TH//STEP+1
        sx, sy = col*(w-1), row*(h-1)
        world_x, world_y = col*TW, row*TH
    zz = z[sy:sy+h, sx:sx+w]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # glTF is Y-up; south on the map is negative Z.
    pos = np.stack((xx*STEP, zz, -yy*STEP), axis=-1)
    # Normals are computed from the GLOBAL field, not independently per tile.
    gy, gx = np.gradient(z, STEP)
    n = np.stack((-gx[sy:sy+h, sx:sx+w],
                  np.ones_like(zz),
                  gy[sy:sy+h, sx:sx+w]), axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    uv = np.stack((xx/(w-1), 1-yy/(h-1)), axis=-1)
    a = np.arange(h-1, dtype=np.uint32)[:, None]*w + np.arange(w-1, dtype=np.uint32)[None, :]
    tris = np.stack((a, a+w, a+1, a+1, a+w, a+w+1), axis=-1).reshape(-1)
    arrays = (pos.reshape(-1, 3).astype("<f4"),
              n.reshape(-1, 3).astype("<f4"),
              uv.reshape(-1, 2).astype("<f4"),
              tris.astype("<u4"))
    buf, views, accessors = bytearray(), [], []
    for i, arr in enumerate(arrays):
        offset = len(buf)
        data = arr.tobytes()
        buf.extend(data)
        while len(buf)%4: buf.append(0)
        views.append({"buffer":0,"byteOffset":offset,"byteLength":len(data),
                      "target":34963 if i==3 else 34962})
        ac = {"bufferView":i,"byteOffset":0,
              "componentType":5125 if i==3 else 5126,
              "count":int(arr.shape[0]),
              "type":"SCALAR" if i==3 else ("VEC2" if i==2 else "VEC3")}
        if i==0:
            ac["min"] = [float(t) for t in arr.min(axis=0)]
            ac["max"] = [float(t) for t in arr.max(axis=0)]
        accessors.append(ac)
    name = ("infill-%d-0"%col) if inlay else ("pilot-%d-%d"%(col,row))
    bin_name = name+".bin"
    (out/bin_name).write_bytes(buf)
    gltf = {
      "asset":{"version":"2.0","generator":"COE V267 world-locked height mesh; NOT approved art"},
      "buffers":[{"uri":bin_name,"byteLength":len(buf)}],
      "bufferViews":views,"accessors":accessors,
      "images":[{"uri":tile}],"samplers":[{"magFilter":9729,"minFilter":9987,"wrapS":33071,"wrapT":33071}],
      "textures":[{"sampler":0,"source":0}],
      "materials":[{"name":"Original procedural relief, alpha-cut octagon",
                    "pbrMetallicRoughness":{"baseColorTexture":{"index":0},
                    "metallicFactor":0,"roughnessFactor":1},
                    "alphaMode":"BLEND","doubleSided":True}],
      "meshes":[{"name":name,"primitives":[{"attributes":{"POSITION":0,"NORMAL":1,"TEXCOORD_0":2},
                                               "indices":3,"material":0,"mode":4}]}],
      "nodes":[{"mesh":0,"translation":[world_x,0,-world_y]}],
      "scenes":[{"nodes":[0]}],"scene":0
    }
    gltf_name = name+".gltf"
    (out/gltf_name).write_text(json.dumps(gltf,separators=(",",":")))
    return {"id":name,"gltf":gltf_name,"binary":bin_name,"vertexCount":int(w*h),
            "triangleCount":int(2*(w-1)*(h-1)),
            "sha256":hashlib.sha256(buf).hexdigest(),
            "nativeGamePlayable":False,"visuallyApproved":False,"playable":False if inlay else False}

def main(root, out):
    manifest_path = out/"manifest.json"
    assert manifest_path.exists(), "Run original native relief renderer before mesh export"
    original = json.loads(manifest_path.read_text())
    assert len(original["cells"])==8 and original["visuallyApprovedV267"] is False
    x, y, z, distance = build_heightfield(root, out)
    source=out/"heightfield-step16.npy"
    assert original["meshGroundArtAligned"]
    assert hashlib.sha256(source.read_bytes()).hexdigest()==original["meshSourceHeightfieldSha256"]
    out.mkdir(parents=True, exist_ok=True)
    cells = []
    for row in range(ROWS):
        for col in range(COLS):
            tile = "pilot-%d-%d-ground.png"%(col,row)
            assert (out/tile).exists()
            cells.append(pack_gltf(tile,z,out,col,row))
    inlays = []
    for col in range(COLS-1):
        tile = "infill-%d-0-ground.png"%col
        assert (out/tile).exists(), "Original continuous-raster infill missing"
        inlays.append(pack_gltf(tile,z,out,col,0,inlay=True))
    # Shared border heights and normals MUST be identical in world space.
    checks = []
    for row in range(ROWS):
        for col in range(COLS-1):
            a=z[row*(TH//STEP):(row+1)*(TH//STEP)+1,(col+1)*(TW//STEP)]
            b=z[row*(TH//STEP):(row+1)*(TH//STEP)+1,(col+1)*(TW//STEP)]
            assert np.array_equal(a,b)
            checks.append({"a":f"pilot-{col}-{row}","b":f"pilot-{col+1}-{row}",
                           "maxHeightDifference":0,"sameWorldGrid":True})
    for col in range(COLS):
        a=z[TH//STEP,col*(TW//STEP):(col+1)*(TW//STEP)+1]
        b=z[TH//STEP,col*(TW//STEP):(col+1)*(TW//STEP)+1]
        assert np.array_equal(a,b)
        checks.append({"a":f"pilot-{col}-0","b":f"pilot-{col}-1",
                       "maxHeightDifference":0,"sameWorldGrid":True})
    m = {"schema":"coe-v267-real-heightmesh-candidates/v1",
         "referenceCommit":REF,"source":"V94 DEM plus explicitly synthetic microrelief",
         "true3DMesh":True,"sourcePhotosUsed":False,
         "geometryUsesExactPaintedHeightfield":True,
         "paintedHeightfieldSha256":hashlib.sha256(source.read_bytes()).hexdigest(),
         "meshStepPixels":STEP,"cells":cells,"inlays":inlays,"geometricSeamChecks":checks,
         "roadContracts":len(original["seams"]),
         "historicalRoadsVerified":0,"nativeGamePlayable":0,
         "visuallyApprovedV267":0,"finishedToday":0,
         "note":"Actual 3D terrain geometry with procedural texture, NOT photoreal V267 parity or playable integration."}
    (out/"heightmesh-manifest.json").write_text(json.dumps(m,indent=2))
    print(json.dumps({"heightmeshCandidates":len(cells),"threeDGapInlays":len(inlays),
                      "triangles":sum(c["triangleCount"] for c in cells),
                      "vertices":sum(c["vertexCount"] for c in cells),
                      "seamsVerified":len(checks),
                      "nativeGamePlayable":0,"finishedToday":0}))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--out",type=Path,default=Path("generated/v267-relief-pilot"))
    a=p.parse_args();main(a.root,a.out)
