#!/usr/bin/env python3
"""World-anchored original faceted 3D bedrock for isolated V267 terrain pilot.

Uses the exact DEM-derived painted heightfield and existing provisional
cartway centerlines. No photo crops, historic claims, or gameplay changes.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.spatial import cKDTree
from v267_native_relief_pilot import TW, TH, COLS, ROWS, road_centerlines

STEP=16
W,H=TW*COLS,TH*ROWS
SEED=2671032

def build(out:Path):
    src=out/'heightfield-step16.npy'
    field=np.load(src,allow_pickle=False)
    assert field.shape==(H//STEP+1,W//STEP+1) and field.dtype==np.float32
    assert np.isfinite(field).all()
    source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
    terrain=json.loads((out/'heightmesh-manifest.json').read_text())
    assert source_sha==terrain['paintedHeightfieldSha256']
    assert terrain['visuallyApprovedV267']==terrain['nativeGamePlayable']==terrain['finishedToday']==0
    rng=np.random.default_rng(SEED)
    gy,gx=np.gradient(field,STEP)
    slope=np.hypot(gx,gy)
    cut=float(np.quantile(slope,.56))
    yy,xx=np.meshgrid(np.arange(23,H-22,33),np.arange(23,W-22,33),indexing='ij')
    x=np.clip(xx.ravel()+rng.uniform(-8,8,xx.size),22,W-23).astype(np.float32)
    y=np.clip(yy.ravel()+rng.uniform(-8,8,yy.size),22,H-23).astype(np.float32)
    s=map_coordinates(slope,[y/STEP,x/STEP],order=1,mode='nearest')
    alt=map_coordinates(field,[y/STEP,x/STEP],order=1,mode='nearest')
    roads=np.concatenate(road_centerlines(W,H,1),axis=0)
    clearance=cKDTree(roads).query(np.column_stack((x,y)),workers=1)[0]
    probability=np.clip((s-cut)/(max(cut,.001)*2),.08,.57)
    keep=(s>cut)&(clearance>30)&(rng.random(len(x))<probability)
    x,y,s,alt,clearance=(a[keep] for a in (x,y,s,alt,clearance))
    assert len(x)>40, 'No rocky slopes: review terrain threshold'
    pos=[];nor=[];col=[];indices=[]
    shades=np.array([[.42,.41,.36],[.55,.53,.46],[.36,.39,.36],
                     [.61,.59,.51],[.45,.43,.39]],dtype=np.float32)
    def ground(px,py):
        return float(map_coordinates(field,[[py/STEP],[px/STEP]],order=1,mode='nearest')[0])
    for i,(cx,cy,steep,base) in enumerate(zip(x,y,s,alt)):
        radius=float(rng.uniform(4.0,11.0))
        height=float(rng.uniform(2.0,5.5)+min(5.0,steep*9))
        rotation=float(rng.uniform(0,2*np.pi))
        angles=rotation+np.arange(8)*2*np.pi/8
        jitter=rng.uniform(.74,1.19,8)
        outer=[];shoulder=[]
        for j,a in enumerate(angles):
            px=float(cx+radius*jitter[j]*np.cos(a))
            py=float(cy+radius*jitter[j]*np.sin(a))
            outer.append((px,ground(px,py)-.18,-py))
            mx=float(cx+(px-cx)*.62)
            my=float(cy+(py-cy)*.62)
            shoulder.append((mx,ground(mx,my)+height*rng.uniform(.37,.68),-my))
        peak=(float(cx+rng.uniform(-.15,.15)*radius),float(base+height),
              -float(cy+rng.uniform(-.15,.15)*radius))
        tint=shades[i%len(shades)]*float(rng.uniform(.84,1.12))
        def tri(a,b,c,face):
            u=np.subtract(b,a);v=np.subtract(c,a)
            n=np.cross(u,v);n=n/(np.linalg.norm(n)+1e-9)
            if n[1]<0:n=-n
            face_color=np.clip(tint*(.83+.05*(face%6)),0,.95)
            k=len(pos)
            pos.extend((a,b,c));nor.extend((n,n,n));col.extend((face_color,)*3)
            indices.extend((k,k+1,k+2))
        for j in range(8):
            k=(j+1)%8
            tri(outer[j],outer[k],shoulder[j],j)
            tri(outer[k],shoulder[k],shoulder[j],j+2)
            tri(shoulder[j],shoulder[k],peak,j+4)
    position=np.asarray(pos,dtype='<f4')
    normal=np.asarray(nor,dtype='<f4')
    color=np.asarray(col,dtype='<f4')
    idx=np.asarray(indices,dtype='<u4')
    assert len(position)==len(normal)==len(color)==len(idx)==len(x)*72
    assert np.isfinite(position).all() and np.isfinite(normal).all()
    binary=bytearray();views=[];accessors=[]
    for k,a in enumerate((position,normal,color,idx)):
        offset=len(binary);data=a.tobytes();binary.extend(data)
        while len(binary)%4:binary.append(0)
        views.append({'buffer':0,'byteOffset':offset,'byteLength':len(data),
                      'target':34963 if k==3 else 34962})
        ac={'bufferView':k,'componentType':5125 if k==3 else 5126,
            'count':len(a),'type':'SCALAR' if k==3 else 'VEC3'}
        if k==0:
            ac['min']=position.min(axis=0).astype(float).tolist()
            ac['max']=position.max(axis=0).astype(float).tolist()
        accessors.append(ac)
    out.mkdir(parents=True,exist_ok=True)
    binname='bedrock-outcrops.bin'
    gltf='bedrock-outcrops.gltf'
    (out/binname).write_bytes(binary)
    model={'asset':{'version':'2.0','generator':'COE V267 original world-locked bedrock study'},
           'buffers':[{'uri':binname,'byteLength':len(binary)}],
           'bufferViews':views,'accessors':accessors,
           'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1,'COLOR_0':2},
                                    'indices':3,'mode':4}]}],
           'nodes':[{'mesh':0}],'scenes':[{'nodes':[0]}],'scene':0}
    (out/gltf).write_text(json.dumps(model,separators=(',',':')))
    counts=[int(np.count_nonzero((x>=c*TW)&(x<(c+1)*TW)&
             (y>=r*TH)&(y<(r+1)*TH))) for r in range(ROWS) for c in range(COLS)]
    manifest={'schema':'coe-v267-original-3d-bedrock/v1',
              'referenceCommit':'456107f28c8db1f87522bbc7511809b2a215f6fb',
              'heightfieldSha256':source_sha,'source':'V94 modern DEM plus synthetic facets',
              'gltf':gltf,'binary':binname,'sha256':hashlib.sha256(binary).hexdigest(),
              'outcrops':len(x),'byCell':counts,'vertexCount':len(position),
              'triangleCount':len(idx)//3,'minimumCartwayClearance':float(clearance.min()),
              'photographicCropsUsed':False,'historicalGeologyVerified':False,
              'visuallyApprovedV267':0,'nativeGamePlayable':0,'finishedToday':0,
              'status':'UNAPPROVED_3D_BEDROCK_STUDY'}
    (out/'bedrock-manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({'3DBedrockOutcrops':len(x),'byCell':counts,
                      'triangles':len(idx)//3,'roadClearance':round(float(clearance.min()),1),
                      'approved':0,'playable':0,'finishedToday':0}))
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=Path('generated/v267-relief-pilot'))
    args=p.parse_args()
    build(args.out)
