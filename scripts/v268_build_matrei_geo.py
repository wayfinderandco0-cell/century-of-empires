#!/usr/bin/env python3
"""V268 geographically pinned 2x2 continuous terrain. Demo only, not historic."""
import hashlib,io,json,math,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter
from PIL import Image,ImageDraw
P=Path('terrain-grid/v268-matrei');P.mkdir(parents=True,exist_ok=True)
W,H,TW,TH=3072,2048,1536,1024
WEST,EAST,SOUTH,NORTH=11.385,11.555,47.088,47.177
ZOOM=12
def pxlon(x):return (x+180)/360*2**ZOOM*256
def pxlat(y):return (1-math.asinh(math.tan(math.radians(y)))/math.pi)/2*2**ZOOM*256
def source():
 x0,x1=pxlon(WEST),pxlon(EAST);y0,y1=pxlat(NORTH),pxlat(SOUTH)
 ax,bx=math.floor(x0/256),math.floor(x1/256)
 ay,by=math.floor(y0/256),math.floor(y1/256)
 mosaic=np.empty(((by-ay+1)*256,(bx-ax+1)*256),np.float32);tiles=[]
 for iy in range(ay,by+1):
  for ix in range(ax,bx+1):
   url=f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{ZOOM}/{ix}/{iy}.png'
   for n in range(4):
    try:
     with urlopen(Request(url,headers={'User-Agent':'CenturyOfEmpires-V268/1.0'}),timeout=35) as r: raw=r.read()
     rgb=np.array(Image.open(io.BytesIO(raw)).convert('RGB'),dtype=np.float32)
     assert rgb.shape==(256,256,3)
     mosaic[(iy-ay)*256:(iy-ay+1)*256,(ix-ax)*256:(ix-ax+1)*256]=rgb[:,:,0]*256+rgb[:,:,1]+rgb[:,:,2]/256-32768
     tiles.append({'url':url,'sha256':hashlib.sha256(raw).hexdigest()});break
    except Exception:
     if n==3:raise
     time.sleep(2+n)
 xs=np.linspace(x0-ax*256,x1-ax*256,W//16+1);ys=np.linspace(y0-ay*256,y1-ay*256,H//16+1)
 yy,xx=np.meshgrid(ys,xs,indexing='ij')
 return map_coordinates(mosaic,[yy,xx],order=1,mode='nearest').astype(np.float32),tiles
def terrain(z):
 ry,rx=z.shape
 sx=(EAST-WEST)*111320*math.cos(math.radians((NORTH+SOUTH)/2))/(rx-1)
 sy=(NORTH-SOUTH)*111320/(ry-1)
 dz_y,dz_x=np.gradient(gaussian_filter(z,1.1),sy,sx)
 slope=np.hypot(dz_x,dz_y);norm=np.sqrt(1+dz_x*dz_x+dz_y*dz_y)
 sun=np.clip((.76+.48*dz_x+.44*dz_y)/norm,.22,1.25)
 rock=(slope>.5)|(z>2430);forest=(z<2090)&(slope<.40)
 rng=np.random.default_rng(2682026)
 noise=gaussian_filter(rng.normal(size=z.shape).astype('f4'),2.4)
 noise=(noise/max(.01,noise.std()))*4
 col=np.where(rock[:,:,None],np.array([142,137,124],dtype='f4'),np.where(forest[:,:,None],np.array([47,79,50],dtype='f4'),np.array([109,129,76],dtype='f4')))
 col=np.where((z>2820)[:,:,None],[190,193,188],col)
 col=np.clip(col*sun[:,:,None]+noise[:,:,None],0,255).astype('uint8')
 im=Image.fromarray(col,'RGB').resize((W,H),Image.Resampling.BICUBIC)
 d=ImageDraw.Draw(im,'RGBA')
 for i in range(12500):
  x=int(rng.integers(0,W));y=int(rng.integers(0,H))
  if not forest[min(ry-1,y//16),min(rx-1,x//16)]:continue
  h=int(rng.integers(10,22));w=int(h*.35)
  d.ellipse((x+3,y-1,x+w+7,y+h*.25),fill=(15,20,19,70))
  d.polygon([(x,y-h),(x-w,y+2),(x+w,y+2)],fill=(18,47,32,int(rng.integers(145,215))))
  d.line([(x-w//2,y-h//3),(x,y-h+3)],fill=(119,145,111,66),width=2)
 return im,slope
def mesh(z,c,r):
 rows,cols=65,97
 a=z[r*64:r*64+rows,c*96:c*96+cols]
 yy,xx=np.mgrid[0:rows,0:cols]
 v=np.stack([c*TW+xx*16,(a-600)*.8,-(r*TH+yy*16)],axis=-1).astype('<f4').reshape(-1,3)
 uv=np.stack([xx/96,yy/64],axis=-1).astype('<f4').reshape(-1,2)
 idx=np.arange(rows*cols,dtype='u4').reshape(rows,cols)
 tri=np.stack([idx[:-1,:-1],idx[1:,:-1],idx[:-1,1:],idx[:-1,1:],idx[1:,:-1],idx[1:,1:]],axis=-1).reshape(-1).astype('<u4')
 n=f'matrei-{c}-{r}';raw=v.tobytes()+uv.tobytes()+tri.tobytes()
 (P/(n+'.bin')).write_bytes(raw)
 views=[{'buffer':0,'byteOffset':0,'byteLength':v.nbytes,'target':34962},{'buffer':0,'byteOffset':v.nbytes,'byteLength':uv.nbytes,'target':34962},{'buffer':0,'byteOffset':v.nbytes+uv.nbytes,'byteLength':tri.nbytes,'target':34963}]
 acc=[{'bufferView':0,'componentType':5126,'count':len(v),'type':'VEC3','min':v.min(axis=0).tolist(),'max':v.max(axis=0).tolist()},{'bufferView':1,'componentType':5126,'count':len(uv),'type':'VEC2'},{'bufferView':2,'componentType':5125,'count':len(tri),'type':'SCALAR'}]
 g={'asset':{'version':'2.0','generator':'COE V268 DEM shared-world mesh'},'buffers':[{'uri':n+'.bin','byteLength':len(raw)}],'bufferViews':views,'accessors':acc,'images':[{'uri':n+'.webp'}],'textures':[{'source':0}],'materials':[{'pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':1},'doubleSided':True}],'meshes':[{'primitives':[{'attributes':{'POSITION':0,'TEXCOORD_0':1},'indices':2,'material':0}]}],'nodes':[{'mesh':0}],'scenes':[{'nodes':[0]}],'scene':0}
 (P/(n+'.gltf')).write_text(json.dumps(g,separators=(',',':')))
 return {'gltf':n+'.gltf','meshVertices':len(v),'meshTriangles':len(tri)//3,'meshSha256':hashlib.sha256(raw).hexdigest()}
def main():
 z,tiles=source()
 assert z.shape==(129,193) and np.isfinite(z).all() and float(np.ptp(z))>100,'Bad DEM'
 picture,slope=terrain(z);picture.save(P/'contact-sheet.webp','WEBP',quality=84)
 np.save(P/'heightfield-step16.npy',z)
 # Candidate only: no water/river certification, slope threshold is not gameplay passability.
 Image.fromarray(np.uint8(slope<.58)*255).save(P/'slope-candidate-mask.png')
 cells=[]
 for row in range(2):
  for col in range(2):
   n=f'matrei-{col}-{row}'
   picture.crop((col*TW,row*TH,(col+1)*TW,(row+1)*TH)).save(P/(n+'.webp'),'WEBP',quality=86)
   cells.append({'id':n,'originPixels':[col*TW,row*TH],'art':n+'.webp','sha256':hashlib.sha256((P/(n+'.webp')).read_bytes()).hexdigest(),'bboxWGS84':[WEST+(EAST-WEST)*col/2,SOUTH+(NORTH-SOUTH)*(1-(row+1)/2),WEST+(EAST-WEST)*(col+1)/2,SOUTH+(NORTH-SOUTH)*(1-row/2)],**mesh(z,col,row),'finished':False,'playableRouteCertified':False})
 checks=[]
 for row in range(2):checks.append({'cells':[f'matrei-0-{row}',f'matrei-1-{row}'],'heightSeamDiffMeters':float(np.max(np.abs(z[row*64:row*64+65,96]-z[row*64:row*64+65,96])))})
 for col in range(2):checks.append({'cells':[f'matrei-{col}-0',f'matrei-{col}-1'],'heightSeamDiffMeters':float(np.max(np.abs(z[64,col*96:col*96+97]-z[64,col*96:col*96+97])))})
 manifest={'schema':'coe-v268-matrei-continuous/v1','status':'REAL_GEOGRAPHIC_VISUAL_PILOT_NOT_APPROVED','place':'Matrei am Brenner, Austria','bboxWGS84':[WEST,SOUTH,EAST,NORTH],'dimensions':[W,H],'cellSize':[TW,TH],'source':'Mapzen Terrain Tiles (AWS Open Data Terrarium)','sourceURL':'https://registry.opendata.aws/terrain-tiles/','attributionURL':'https://github.com/tilezen/joerd/blob/master/docs/attribution.md','downloadedUTC':datetime.now(timezone.utc).isoformat(),'inputTiles':tiles,'heightSourceSHA256':hashlib.sha256(z.tobytes()).hexdigest(),'heightRangeMeters':[float(z.min()),float(z.max())],'modernDataNotHistoricalSurvey':True,'vegetationIsProceduralNotHistorical':True,'verifiedRivers':False,'historicalRoads':False,'certifiedNewPlayableTiles':0,'approvedOriginalThreePreserved':True,'cells':cells,'sharedSeams':checks}
 assert len(cells)==4 and all(v['heightSeamDiffMeters']==0 for v in checks)
 (P/'manifest.json').write_text(json.dumps(manifest,indent=2))
 print('V268 built REAL shared-source Matrei terrain, 4 raster tiles, 4 glTF meshes; DEM range',manifest['heightRangeMeters'])
if __name__=='__main__':main()
