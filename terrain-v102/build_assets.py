#!/usr/bin/env python3
"""Deterministic art bake. Reuses V97 geography; never downloads new terrain.
All vegetation, material microtexture and the pack trail are illustrative.
"""
import json, math, hashlib
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter, zoom
from scipy.spatial import cKDTree
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'terrain-v102'
rng=np.random.default_rng(102)
source=ROOT/'terrain-v97/brenner-data.json'
d=json.loads(source.read_text()); streams=json.loads((ROOT/'terrain-v99/brenner-streams.json').read_text())
west,south,east,north=d['boundsLonLat']; gw,gh=d['heightGrid']
dem=np.array(d['elevationM'],np.float32).reshape(gh,gw)
woods=np.array(d['treeGrid'],np.float32).reshape(gh,gw)
origin=[11.52,47.13]; MX=111320*math.cos(math.radians(origin[1])); MY=111320
bounds=[11.43,47.075,11.625,47.19]

def sample(a,lon,lat,order=3):
    return map_coordinates(a,[(north-lat)/(north-south)*(gh-1),(lon-west)/(east-west)*(gw-1)],order=order,mode='nearest')
def noise(n,size):
    a=rng.random((n,n),dtype=np.float32)
    return zoom(a,size/n,order=3)[:size,:size]
def coords(bounds,size):
    w,s,e,n=bounds
    return np.meshgrid(np.linspace(w,e,size,dtype=np.float32),np.linspace(n,s,size,dtype=np.float32))
def bake(bounds,size,detail):
    lon,lat=coords(bounds,size); h=sample(dem,lon,lat)
    w,s,e,n=bounds; px=(e-w)*MX/(size-1); py=(n-s)*MY/(size-1)
    sy,sx=np.gradient(h,py,px); slope=np.hypot(sx,sy)
    n1=noise(18,size); n2=noise(91,size); n3=noise(370,size)
    forest=sample(gaussian_filter(woods,.8),lon,lat,1)
    forest=np.clip((forest*.70+n1*.32+n2*.22-.32)*2.2,0,1)
    forest*=np.clip((2180-h)/260,0,1)*np.clip((1.1-slope)/.35,0,1)
    rock=np.clip((slope-.38)*2.5+(h-2100)/720+(n2-.5)*.45,0,1)
    rock=np.maximum(rock,np.clip((h-2400)/280,0,1))
    rgb=np.zeros((size,size,3),np.float32)
    grass=np.array([124,132,87])+((n1-.5)*17+(n2-.5)*8)[...,None]*np.array([1,.9,.55])
    dry=np.array([149,141,108])
    grass=grass*(1-n1[...,None]*.3)+dry*n1[...,None]*.3
    stone=np.array([153,150,137])+((n2-.5)*25+(n3-.5)*14)[...,None]
    rgb=grass*(1-rock[...,None])+stone*rock[...,None]
    forest*=1-rock*.84
    rgb=rgb*(1-forest[...,None]*.65)+np.array([62,80,54])*forest[...,None]*.65
    # Native retained V97 relief brings back measured ridgeline shading beyond the reduced mesh.
    im=np.asarray(Image.open(ROOT/'terrain-v97/brenner-relief.webp').convert('RGB'),np.float32)
    yy=(north-lat)/(north-south)*(im.shape[0]-1); xx=(lon-west)/(east-west)*(im.shape[1]-1)
    lum=map_coordinates(im.mean(2),[yy,xx],order=1,mode='nearest')
    relief=lum-gaussian_filter(lum, max(1,size/210))
    rgb*=np.clip(1+relief[...,None]*.009,.68,1.28)
    # Anisotropic, subdued rock striation; world based, not a repeated bitmap tile.
    grain=(n3-.5)*4
    striation=np.sin(lon*17800+lat*12600+(n2-.5)*14)*rock*1.6
    rgb+=grain[...,None]+striation[...,None]
    return lon,lat,h,slope,forest,rock,rgb,px,py

print('Baking geographic material',flush=True)
lon,lat,h,slope,forest,rock,rgb,px,py=bake(bounds,2048,True)

# Retain natural streams only; artificial drainage ditches are excluded.
water=[]
for line in streams['waterways']:
    if line['type'] not in ('stream','river'): continue
    cc=np.array(line['coords'],float)
    if ((cc[:,0]>=bounds[0])&(cc[:,0]<=bounds[2])&(cc[:,1]>=bounds[1])&(cc[:,1]<=bounds[3])).any():
        water.append({'name':line['name'] or 'Mountain stream','type':line['type'],'coords':line['coords']})
# One illustrative pack trail on a bank of the surveyed Navisbach, not a historic-road claim.
navis=next(x for x in water if x['name']=='Navisbach' and x['type']=='river')
trail=[]
for i,p in enumerate(navis['coords'][::-1]):
    if i%4==0 or i==len(navis['coords'])-1:
        trail.append([p[0],p[1]+.00062+math.sin(i*.09)*.00015])

def local(cc):
    a=np.asarray(cc);return np.column_stack(((a[:,0]-origin[0])*MX,(origin[1]-a[:,1])*MY))
def dense(cc,spacing=8):
    a=local(cc);out=[]
    for p,q in zip(a[:-1],a[1:]):
        nn=max(2,math.ceil(np.linalg.norm(q-p)/spacing))
        out.extend(p+(q-p)*np.arange(nn)[:,None]/nn)
    return np.asarray(out)
riverpts=np.concatenate([dense(x['coords']) for x in water]); rt=cKDTree(riverpts)
tp=dense(trail);tt=cKDTree(tp)
pixelpos=np.column_stack(((lon.ravel()-origin[0])*MX,(origin[1]-lat.ravel())*MY))
rd=rt.query(pixelpos,workers=2)[0].reshape(h.shape);td=tt.query(pixelpos,workers=2)[0].reshape(h.shape)
forest*=np.clip((rd-13)/28,0,1)*np.clip((td-9)/17,0,1)
# Canopy shadow is irregular and geographically stable. Tree crowns are real render geometry.
candidate=rng.uniform([bounds[0],bounds[1]],[bounds[2],bounds[3]],(175000,2))
cx=(candidate[:,0]-bounds[0])/(bounds[2]-bounds[0])*2047
cy=(bounds[3]-candidate[:,1])/(bounds[3]-bounds[1])*2047
ff=map_coordinates(forest,[cy,cx],order=1)
keep=rng.random(len(candidate))<ff*.72
candidate=candidate[keep];cx=cx[keep];cy=cy[keep]
size=rng.uniform(12,27,len(candidate));seed=rng.random(len(candidate))
heights=sample(dem,candidate[:,0],candidate[:,1])
trees=np.column_stack((candidate[:,0],candidate[:,1],heights,size,seed))
shadow=np.zeros(h.shape,np.float32)
np.add.at(shadow,(np.clip(cy.astype(int)+2,0,2047),np.clip(cx.astype(int)+2,0,2047)),.28)
shadow=gaussian_filter(shadow,1.4)
rgb*=1-np.clip(shadow[...,None]*1.8,0,.25)
# Broad forest floor corrects the excluded riparian/trail clearings.
rgb=rgb*.93+np.array([149,148,112])*.07
Image.fromarray(np.clip(rgb,0,255).astype('uint8')).save(OUT/'navis-material.webp',quality=91,method=6)
trees.astype('<f4').tofile(OUT/'trees.f32')
print('Trees',len(trees),flush=True)

_,_,_,_,_,_,base,_,_=bake(d['boundsLonLat'],1536,False)
Image.fromarray(np.clip(base,0,255).astype('uint8')).save(OUT/'alpine-material.webp',quality=88,method=6)

# Height mesh samples are interpolation of V97, explicitly not newly measured detail.
mlon,mlat=coords(bounds,257)
mh=sample(dem,mlon,mlat).astype('<f4');mh.tofile(OUT/'navis-height.f32')
dem.astype('<f4').tofile(OUT/'alpine-height.f32')
(OUT/'features.json').write_text(json.dumps({'waterways':water,'trail':{'name':'Pack trail','illustrative':True,'coords':trail}},separators=(',',':')))
manifest={
 'version':102,'originLonLat':origin,'metersPerDegree':[MX,MY],
 'boundsLonLat':bounds,'grid':[257,257],'broadBoundsLonLat':d['boundsLonLat'],'broadGrid':[gw,gh],
 'treeCount':len(trees),'treeStride':5,'seed':102,
 'sources':{'elevation':'Reused V97 Copernicus GLO-30-derived 260×300 numeric grid; retained spacing about 160×230 m',
 'relief':'Reused V97 shaded relief (1552×1782), not aerial photography',
 'waterways':'Reused V99 OpenStreetMap natural streams; modern geographic guides, not certified historical courses',
 'woodland':'V97 ESA WorldCover 2021 proxy, smoothed and artistically reconstructed; not a historical survey',
 'path':'Illustrative unpaved pack trail offset from Navisbach; no assertion of an authenticated 1780 alignment',
 'art':'Original deterministic material, tree crowns and shading; no external image tiles'},
 'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'rendering':'EPSG:4326 inputs; local east/north metric frame at 11.52 E, 47.13 N; elevation metres; no vertical exaggeration',
 'locationNote':'Navis valley, northern Brenner region. The actual Brenner Pass summit is about 14 km south and is not this close-up scene.'
}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Assets ready',flush=True)
