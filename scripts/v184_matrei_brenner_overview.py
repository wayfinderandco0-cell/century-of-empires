#!/usr/bin/env python3
"""V184: contiguous modern SOURCE overview between two verified Alpine anchors.

This native zoom-14 orthophoto rectangle is NOT a 1780 road, bridge, playable
corridor, game octagon, or a replacement for the original V121/V123 art.
"""
import argparse
import hashlib
import io
import json
import math
import time
from urllib.error import URLError
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image
from v180_matrei_source import ANCHOR as MATREI
from v183_brenner_pass_source import ANCHOR as BRENNER

ZOOM, TILE, PAD = 14, 256, 1
BASE = 'https://mapsneu.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857'
FALSE_FLAGS = ('sourceSectorsAreGameOctagons', 'v121ToGeographyRegistered',
               'v123RoadsGeoregistered', 'historicalRoadsVerified',
               'bridgeBanksVerified', 'historic1780Certified', 'periodArtComplete',
               'physicalIPhoneApproved', 'productionApproved')

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def tile_at(lon, lat):
    require(-180 <= lon <= 180 and -85 < lat < 85, 'invalid anchor')
    n = 1 << ZOOM
    return (int((lon+180)/360*n),
            int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n))

def bounds(x,y):
    n = 1 << ZOOM
    def lat(row):
        return math.degrees(math.atan(math.sinh(math.pi*(1-2*row/n))))
    return [(x/n)*360-180,lat(y+1),((x+1)/n)*360-180,lat(y)]

def plan():
    a,b = tile_at(*MATREI),tile_at(*BRENNER)
    x0,x1 = min(a[0],b[0])-PAD,max(a[0],b[0])+PAD
    y0,y1 = min(a[1],b[1])-PAD,max(a[1],b[1])+PAD
    width,height = x1-x0+1,y1-y0+1
    require(width*height <= 100 and width >= 3 and height >= 3,
            'unexpected anchor separation or source footprint')
    samples=[]
    for row in range(height):
        for col in range(width):
            x,y=x0+col,y0+row
            samples.append({'name':f'r{row:02d}c{col:02d}', 'row':row,'col':col,
                'tileXYZ':[x,y,ZOOM], 'boundsLonLat':bounds(x,y),
                'url':f'{BASE}/{ZOOM}/{y}/{x}.jpeg'})
    west,_,_,north=bounds(x0,y0)
    _,south,east,_=bounds(x1,y1)
    for lon,lat in (MATREI,BRENNER):
        require(west < lon < east and south < lat < north,
                'anchor outside source rectangle')
    return {'version':184,
        'purpose':'Modern geographic overview SOURCE; NOT historical GAME octagons',
        'anchorsLonLat':{'matrei':list(MATREI),'brenner':list(BRENNER)},
        'anchorSource':'V179 independently identified modern geographic anchors',
        'crs':'EPSG:3857','zoom':ZOOM,'tileSize':TILE,
        'paddingNativeTiles':PAD,'tileOriginXYZ':[x0,y0,ZOOM],
        'gridTiles':[width,height], 'pixelDimensions':[width*TILE,height*TILE],
        'mosaicBoundsLonLat':[west,south,east,north],
        'plannedGridFullyContiguous':True,
        'straightLineAnchorCoverageOnly':True,
        'doesNotProveHistoricalOrTraversableRoadCorridor':True,
        'doesNotReplaceHighResolutionGameTerrain':True,
        'modernInfrastructureRequiresExclusion':True,
        'provider':'basemap.at', 'sourceUrl':'https://basemap.at/orthofoto/',
        'license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/',
        'requiredAttribution':'Datenquelle: basemap.at',
        'samples':samples,**{key:False for key in FALSE_FLAGS}}

def validate(m):
    expected=plan()
    require(set(m)-set(expected) <= {'mosaicFile','mosaicSha256','seamDiagnostics'},
            'unexpected source or approval metadata')
    for key,value in expected.items():
        if key!='samples':
            require(m.get(key)==value,'altered geometry/source/approval: '+key)
    samples=m.get('samples')
    require(isinstance(samples,list) and len(samples)==len(expected['samples']),
            'missing/extra source tiles')
    for got,correct in zip(samples,expected['samples']):
        require(isinstance(got,dict) and
                set(got)-set(correct) <= {'imageFile','sha256','byteCount'},
                'unexpected tile metadata')
        for key,value in correct.items():
            require(got.get(key)==value,'source tile geometry/identity: '+key)
        if 'imageFile' in got:
            require(got['imageFile']==got['name']+'.jpeg','source filename mismatch')
    return True

def download(m,folder):
    validate(m)
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    for item in m['samples']:
        req=Request(item['url'],headers={'User-Agent':'CenturyOfEmpires-SourceAudit/1.0'})
        for attempt in range(4):
            try:
                with urlopen(req,timeout=20) as response:
                    data=response.read(1024*1024+1)
                    mime=response.headers.get('Content-Type','')
                break
            except (URLError, TimeoutError):
                if attempt==3:
                    raise
                time.sleep(1.5*(attempt+1))
        require(len(data)<=1024*1024 and data.startswith(b'\xff\xd8') and
                'image' in mime.lower(),'invalid source response')
        with Image.open(io.BytesIO(data)) as im:
            require(im.format=='JPEG' and im.size==(TILE,TILE),'not native JPEG')
            im.verify()
        path=folder/(item['name']+'.jpeg')
        path.write_bytes(data)
        item.update(imageFile=path.name,sha256=hashlib.sha256(data).hexdigest(),
                    byteCount=len(data))

def compose(m,folder):
    validate(m)
    folder=Path(folder)
    image=Image.new('RGBA',tuple(m['pixelDimensions']),(0,0,0,0))
    hashes=[]
    for item in m['samples']:
        require(item.get('imageFile')==item['name']+'.jpeg' and
                isinstance(item.get('sha256'),str) and len(item['sha256'])==64,
                'missing tile provenance')
        path=folder/item['imageFile']
        require(path.is_file() and sha(path)==item['sha256'] and
                path.stat().st_size==item.get('byteCount'),'tampered/missing JPEG')
        with Image.open(path) as original:
            require(original.format=='JPEG' and original.size==(TILE,TILE),
                    'wrong native tile dimensions')
            image.paste(original.convert('RGBA'),(item['col']*TILE,item['row']*TILE))
        hashes.append(item['sha256'])
    require(len(set(hashes))==len(hashes),'duplicate source imagery')
    return image

def seams(image,grid):
    width,height=grid
    horizontal=[];vertical=[]
    for row in range(height):
        for col in range(width-1):
            x=(col+1)*TILE;y=row*TILE
            for j in range(TILE):
                a=image.getpixel((x-1,y+j));b=image.getpixel((x,y+j))
                require(a[3]==b[3]==255,'unobserved horizontal source seam')
                horizontal.append(sum(abs(a[k]-b[k]) for k in range(3))/3)
    for row in range(height-1):
        for col in range(width):
            x=col*TILE;y=(row+1)*TILE
            for j in range(TILE):
                a=image.getpixel((x+j,y-1));b=image.getpixel((x+j,y))
                require(a[3]==b[3]==255,'unobserved vertical source seam')
                vertical.append(sum(abs(a[k]-b[k]) for k in range(3))/3)
    return {'horizontalTilePairs':height*(width-1),
            'verticalTilePairs':width*(height-1),
            'horizontalMeanRGBDifference':round(sum(horizontal)/len(horizontal),4),
            'verticalMeanRGBDifference':round(sum(vertical)/len(vertical),4),
            'nativeRasterFullyObserved':True,'gameArtSeamApproved':False}

def produce(m,folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    image=compose(m,folder)
    name='matrei-brenner-modern-overview.png'
    image.save(folder/name,optimize=True)
    m.update(mosaicFile=name,mosaicSha256=sha(folder/name),
             seamDiagnostics=seams(image,m['gridTiles']))
    (folder/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    verify(folder)
    return m

def verify(folder):
    folder=Path(folder)
    m=json.loads((folder/'manifest.json').read_text())
    image=compose(m,folder)
    require(m.get('mosaicFile')=='matrei-brenner-modern-overview.png' and
            m.get('mosaicSha256')==sha(folder/m['mosaicFile']),
            'mosaic SHA mismatch')
    with Image.open(folder/m['mosaicFile']) as saved:
        require(saved.mode=='RGBA' and saved.size==tuple(m['pixelDimensions']) and
                saved.tobytes()==image.tobytes(),'mosaic source pixels altered')
    require(m.get('seamDiagnostics')==seams(image,m['gridTiles']),
            'seam diagnostics altered')
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',default='qa/v184-matrei-brenner-overview')
    p.add_argument('--download',action='store_true')
    p.add_argument('--verify',action='store_true')
    a=p.parse_args();folder=Path(a.output)
    if a.verify:verify(folder)
    elif a.download:
        m=plan();download(m,folder);produce(m,folder)
    else:
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'manifest.json').write_text(json.dumps(plan(),indent=2)+'\n')
    print('V184 contiguous modern SOURCE overview only; historic roads and GAME art NOT approved')

if __name__=='__main__':main()
