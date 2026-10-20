#!/usr/bin/env python3
"""Century of Empires V94: one geographically registered theater-wide terrain build.
Mapzen AWS Terrarium DEM z8, Natural Earth II idealized pre-modern landcover,
Natural Earth 10m land and river vectors. Current topography; indicative vegetation.
Generates overview, 12 independently loadable 2048px tiles, measured DEM and
landcover grid, aligned coastline and real mapped river centerlines.
"""
import concurrent.futures, io, json, math, os, time, zipfile, warnings
from pathlib import Path
import numpy as np, requests, shapefile
from PIL import Image, ImageDraw
from shapely.geometry import shape, box, Polygon, MultiPolygon, LineString, MultiLineString, GeometryCollection
from shapely.ops import unary_union

Image.MAX_IMAGE_PIXELS=None
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'terrain-v94';TILES=OUT/'tiles'
OUT.mkdir(exist_ok=True);TILES.mkdir(exist_ok=True)
WEST,EAST,SOUTH,NORTH=-14.,49.,26.,75.
GAME_W,GAME_H=1448,1086
W,H=8192,6144
ZOOM=8;N=1<<ZOOM;SZ=256
BBOX=box(WEST,SOUTH,EAST,NORTH)
session=requests.Session()
def get(url,timeout=75):
    for attempt in range(4):
        try:
            r=session.get(url,timeout=timeout);r.raise_for_status();return r.content
        except Exception:
            if attempt==3:raise
            time.sleep(2*(attempt+1))
def zip_files(url):
    archive=zipfile.ZipFile(io.BytesIO(get(url,150)))
    names=archive.namelist()
    base=[p for p in names if p.lower().endswith('.shp')]
    if not base:raise RuntimeError('No shp in '+url)
    prefix=base[0][:-4]
    out={}
    for ext in ('shp','shx','dbf'):
        match=next((x for x in names if x.lower()==(prefix+'.'+ext).lower()),None)
        if not match:raise RuntimeError('Missing '+ext+' in '+url)
        out[ext]=io.BytesIO(archive.read(match))
    return shapefile.Reader(shp=out['shp'],shx=out['shx'],dbf=out['dbf'])
def game_point(lon,lat):
    return [(lon-WEST)/(EAST-WEST)*GAME_W,(NORTH-lat)/(NORTH-SOUTH)*GAME_H]
def point_list(coords):
    return [[round(t,2) for t in game_point(*xy)] for xy in coords]
def merc_y(lat):
    return (1-math.asinh(math.tan(math.radians(lat)))/math.pi)*N/2
def merc_x(lon):return (lon+180)/360*N
x0,x1=int(merc_x(WEST)),int(merc_x(EAST))
y0,y1=int(merc_y(NORTH)),int(merc_y(SOUTH))
coords=[(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1)]
print('DOWNLOAD elevation tiles',len(coords),'zoom',ZOOM,flush=True)
mosaic=np.zeros(((y1-y0+1)*SZ,(x1-x0+1)*SZ),dtype=np.float32)
failed=[]
def get_dem(t):
    x,y=t
    url=f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{ZOOM}/{x}/{y}.png'
    for attempt in range(3):
        try:
            res=requests.get(url,timeout=24)
            if res.status_code==404:return x,y,None,'ocean'
            res.raise_for_status()
            a=np.asarray(Image.open(io.BytesIO(res.content)).convert('RGB'),dtype=np.float32)
            return x,y,a[:,:,0]*256+a[:,:,1]+a[:,:,2]/256-32768,None
        except Exception as exc:
            if attempt==2:return x,y,None,str(exc)
            time.sleep(.8*(attempt+1))
with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
    for k,(x,y,tile,err) in enumerate(pool.map(get_dem,coords),1):
        if tile is not None:
            row=(y-y0)*SZ;col=(x-x0)*SZ
            mosaic[row:row+SZ,col:col+SZ]=tile
        elif err!='ocean':failed.append((x,y,err))
        if k%180==0:print('DEM progress',k,'/',len(coords),flush=True)
if len(failed)>5:raise RuntimeError('Too many failed DEM fetches: '+repr(failed[:6]))
print('Elevation download complete',flush=True)
xs=np.linspace(WEST,EAST,W,dtype=np.float32)
ys=np.linspace(NORTH,SOUTH,H,dtype=np.float32)
px=np.clip((xs+180)/360*N*SZ-x0*SZ,0,mosaic.shape[1]-1.001)
py=np.clip(np.asarray([merc_y(float(y))*SZ-y0*SZ for y in ys]),0,mosaic.shape[0]-1.001)
ix=px.astype('int32');iy=py.astype('int32')
fx=px-ix;fy=py-iy
dem=np.empty((H,W),dtype=np.float32)
for row in range(H):
    aa=mosaic[iy[row],ix]*(1-fx)+mosaic[iy[row],ix+1]*fx
    bb=mosaic[iy[row]+1,ix]*(1-fx)+mosaic[iy[row]+1,ix+1]*fx
    dem[row]=aa*(1-fy[row])+bb*fy[row]
del mosaic,px,py,ix,iy,fx,fy

# Natural Earth II raster reconstructs broad natural/pre-industrial landscape,
# not a surveyed forest boundary for 1780.
print('DOWNLOAD Natural Earth II vegetation',flush=True)
z=zipfile.ZipFile(io.BytesIO(get('https://naturalearth.s3.amazonaws.com/10m_raster/NE2_LR_LC.zip',150)))
tiffs=[p for p in z.namelist() if p.lower().endswith(('.tif','.tiff'))]
if not tiffs:raise RuntimeError('Natural Earth II ZIP lacks TIFF')
with z.open(tiffs[0]) as fd:
    nat=Image.open(io.BytesIO(fd.read())).convert('RGB')
    nx,ny=nat.size
    crop=(round((WEST+180)/360*nx),round((90-NORTH)/180*ny),
          round((EAST+180)/360*nx),round((90-SOUTH)/180*ny))
    cover=nat.crop(crop).resize((W,H),Image.Resampling.BICUBIC)
    nat.close()
print('Natural Earth II geographic crop',crop,'render',cover.size,flush=True)

print('DOWNLOAD Natural Earth 10m mapped land',flush=True)
land_reader=zip_files('https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip')
land=Image.new('L',(W,H),0);draw=ImageDraw.Draw(land)
polys=[];all_land=[]
for shp in land_reader.shapes():
    try:
        g=shape(shp.__geo_interface__)
        if not g.intersects(BBOX):continue
        clip=g.intersection(BBOX)
        if clip.is_empty:continue
        all_land.extend(list(clip.geoms) if isinstance(clip,MultiPolygon) else [clip])
    except Exception:continue
# Render coast at native 8k. Vector geometry simplified only for browser SVG mask.
for poly in all_land:
    if not isinstance(poly,Polygon):continue
    xy=[((lon-WEST)/(EAST-WEST)*(W-1),(NORTH-lat)/(NORTH-SOUTH)*(H-1)) for lon,lat in poly.exterior.coords]
    if len(xy)>=3:draw.polygon(xy,fill=255)
    for hole in poly.interiors:
        hole_xy=[((lon-WEST)/(EAST-WEST)*(W-1),(NORTH-lat)/(NORTH-SOUTH)*(H-1)) for lon,lat in hole.coords]
        if len(hole_xy)>=3:draw.polygon(hole_xy,fill=0)
    simple=poly.simplify(.010,preserve_topology=True)
    if simple.is_empty:continue
    if isinstance(simple,Polygon):
        pts=point_list(simple.exterior.coords)
        if len(pts)>=4:polys.append(pts)
land_reader.close()
if len(polys)<25:raise RuntimeError('Insufficient coastline polygons '+str(len(polys)))
(OUT/'land.json').write_text(json.dumps({'source':'Natural Earth 10m land','polygons':polys,'width':GAME_W,'height':GAME_H},separators=(',',':')))
print('LAND polygons',len(polys),flush=True)

# Terrain quality: measured slope shading + Natural Earth II real-world shaped
# environmental palette. Color treatment is period-cartographic, not modern sat.
cover_np=np.asarray(cover,dtype=np.uint8)
land_mask=np.asarray(land,dtype=np.uint8)
rgb=np.empty((H,W,3),dtype=np.uint8)
earth=111320.
for top in range(0,H,240):
    bottom=min(H,top+240)
    a=max(0,top-1);b=min(H,bottom+1)
    slice_dem=dem[a:b]
    gx=np.gradient(slice_dem,axis=1)
    gy=np.gradient(slice_dem,axis=0)
    lat_slice=ys[a:b]
    dx=(EAST-WEST)/(W-1)*earth*np.maximum(.25,np.cos(np.radians(lat_slice)))
    dy=(NORTH-SOUTH)/(H-1)*earth
    east=gx/dx[:,None];north=-gy/dy
    shift=np.clip(-east*.69-north*.73,-.25,.25)
    lit=np.clip(.90+shift*1.35,.65,1.11)
    for ch in range(3):
        natural=cover_np[a:b,:,ch].astype(np.float32)
        # Period atlas: desaturate slightly without losing geographic cover.
        grayscale=cover_np[a:b,:,:].mean(axis=2)
        adapted=natural*.82+grayscale*.18
        if ch==2:adapted*=.94
        if ch==0:adapted*=1.015
        data=(adapted*lit).clip(0,255).astype('uint8')
        rgb[top:bottom,:,ch]=data[top-a:bottom-a]
    if top%960==0:print('Terrain shade',top,'/',H,flush=True)
# Ocean geometry comes from 10m shoreline, not guessing the color blue.
sea=land_mask<128
rgb[sea]=np.array([25,75,100],dtype=np.uint8)
img=Image.fromarray(rgb,'RGB')
overview=img.resize((4096,3072),Image.Resampling.LANCZOS)
overview.save(OUT/'overview.webp','WEBP',quality=89,method=5)
for ty in range(3):
    for tx in range(4):
        crop=img.crop((tx*2048,ty*2048,(tx+1)*2048,(ty+1)*2048))
        crop.save(TILES/f'{tx}-{ty}.webp','WEBP',quality=88,method=5)
print('Saved overview and 12 theater zoom tiles',flush=True)
# All gameplay terrain samples use the same measured topography, not image shade.
grid=Image.fromarray(dem,mode='F').resize((512,384),Image.Resampling.BILINEAR)
hvals=np.round(np.asarray(grid)).astype(np.int16)
(OUT/'heights.json').write_text(json.dumps({'source':'Mapzen AWS Terrarium z8','width':512,'height':384,
 'heights':hvals.ravel().tolist()},separators=(',',':')))
# Natural Earth II colors imply broad woodland, not exact year-1780 vegetation.
low=np.asarray(cover.resize((512,384),Image.Resampling.BILINEAR)).astype(np.int16)
h=np.asarray(grid)
green=(low[:,:,1].astype(float)-low[:,:,0].astype(float)*.94)
saturation=low[:,:,1]-low[:,:,2]
forest=(green>5)&(saturation>3)&(h<1800)
forest_pixels=forest.astype(np.uint8)
(OUT/'woods.json').write_text(json.dumps({'source':'Natural Earth II idealized land cover, approximate woodland proxy',
 'width':512,'height':384,'forest':forest_pixels.ravel().tolist()},separators=(',',':')))
print('Woodland proxy cover',round(float(forest.mean())*100,1),'%',flush=True)

print('DOWNLOAD Natural Earth 10m rivers',flush=True)
rivers=[]
for kind in ('ne_10m_rivers_lake_centerlines_scale_rank','ne_10m_rivers_europe'):
    reader=zip_files('https://naturalearth.s3.amazonaws.com/10m_physical/'+kind+'.zip')
    for rec in reader.iterShapeRecords():
        try:
            attrs={k.lower():v for k,v in rec.record.as_dict().items()}
            geo=shape(rec.shape.__geo_interface__)
            if not geo.intersects(BBOX):continue
            geo=geo.intersection(BBOX)
            rank=attrs.get('scalerank',attrs.get('scale_rank',attrs.get('min_zoom',7)))
            try:rank=int(rank)
            except:rank=7
            name=str(attrs.get('name') or attrs.get('name_en') or '')
            if geo.is_empty:continue
            lines=list(geo.geoms) if isinstance(geo,(MultiLineString,GeometryCollection)) else [geo]
            for piece in lines:
                if not isinstance(piece,LineString):continue
                sim=piece.simplify(.009,preserve_topology=True)
                points=point_list(sim.coords)
                if len(points)<2:continue
                path='M'+'L'.join(f'{x:g} {y:g}' for x,y in points)
                rivers.append({'name':name[:48],'major':rank<=4,'rank':rank,'d':path})
        except Exception:continue
    reader.close()
if len(rivers)<120:raise RuntimeError('River layer too small: '+str(len(rivers)))
(OUT/'rivers.json').write_text(json.dumps({'source':'Natural Earth 10m river and lake centerlines, Europe supplement','rivers':rivers},separators=(',',':')))
print('RIVERS centerlines',len(rivers),flush=True)
manifest={'version':'94','projection':'equirectangular','extent':[WEST,SOUTH,EAST,NORTH],
          'gameSize':[GAME_W,GAME_H],'atlasSize':[W,H],'tiles':[4,3],
          'overview':'terrain-v94/overview.webp','tileTemplate':'terrain-v94/tiles/{x}-{y}.webp',
          'heights':'terrain-v94/heights.json','woods':'terrain-v94/woods.json',
          'land':'terrain-v94/land.json','rivers':'terrain-v94/rivers.json',
          'elevationSource':'Mapzen/AWS Terrarium z8','physicalSource':'Natural Earth 10m',
          'vegetationSource':'Natural Earth II idealized pre-modern landcover; NOT verified 1780 forest survey'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert Image.open(OUT/'overview.webp').size==(4096,3072)
assert all(Image.open(TILES/f'{x}-{y}.webp').size==(2048,2048) for x in range(4) for y in range(3))
assert int(hvals.max())>1800
assert (forest_pixels.sum()>10000 and forest_pixels.sum()<forest_pixels.size*.92)
print('V94 COMPLETE: real elevation, idealized premodern cover, detailed coasts and mapped rivers',flush=True)
