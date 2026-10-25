#!/usr/bin/env python3
"""V183: geographically native Brenner Pass SOURCE sample, not GAME terrain.

Nine independent XYZ orthophoto JPEGs cover a small real-world pass vicinity.
This does NOT locate any Western Pass/Southern Valley GAME octagon, V123 road,
bridge bank, 1780 route or historic building. No image pixels are invented.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image

ANCHOR = (11.50750, 47.00333)  # V179 independent modern reference
MATREI = (11.45306, 47.13083)  # V179 independent modern reference
ZOOM, TILE, SIDE = 17, 256, 3
SIZE = (TILE * SIDE, TILE * SIDE)
BASE = 'https://mapsneu.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857'
SOURCE = 'https://basemap.at/orthofoto/'
ATTRIBUTION = 'Datenquelle: basemap.at'
FALSE_FLAGS = ('sourceSectorsAreGameOctagons', 'v121ToGeographyRegistered',
               'v123RoadsGeoregistered', 'historicalRoadsVerified',
               'bridgeBanksVerified', 'historic1780Certified', 'periodArtComplete',
               'physicalIPhoneApproved', 'productionApproved')

def require(ok, msg):
    if not ok: raise ValueError(msg)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def tile_at(lon, lat):
    require(-180 <= lon <= 180 and -85 < lat < 85, 'invalid anchor')
    n = 1 << ZOOM
    return (int((lon + 180) / 360 * n),
            int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n))

def bounds(x, y):
    n = 1 << ZOOM
    def lat(row): return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * row / n))))
    return [(x / n) * 360 - 180, lat(y + 1), ((x + 1) / n) * 360 - 180, lat(y)]

def distance_km(a, b):
    r = math.pi / 180
    dlat, dlon = (b[1]-a[1])*r, (b[0]-a[0])*r
    q = math.sin(dlat/2)**2 + math.cos(a[1]*r)*math.cos(b[1]*r)*math.sin(dlon/2)**2
    return 6371.0088*2*math.atan2(math.sqrt(q),math.sqrt(1-q))

def plan():
    cx, cy = tile_at(*ANCHOR)
    x0, y0 = cx-1, cy-1
    samples = []
    for row in range(SIDE):
        for col in range(SIDE):
            x, y = x0+col, y0+row
            samples.append({'name':f'r{row}c{col}', 'row':row, 'col':col,
                'tileXYZ':[x,y,ZOOM], 'boundsLonLat':bounds(x,y),
                'url':f'{BASE}/{ZOOM}/{y}/{x}.jpeg'})
    west,_,_,north = bounds(x0,y0)
    _,south,east,_ = bounds(x0+2,y0+2)
    require(west < ANCHOR[0] < east and south < ANCHOR[1] < north,
            'pass anchor outside source mosaic')
    return {'version':183, 'purpose':'Modern Brenner Pass SOURCE study; NOT GAME octagons',
        'anchorId':'brenner-pass', 'anchorLonLat':list(ANCHOR),
        'anchorEvidence':'https://en.wikipedia.org/wiki/Brenner_Pass',
        'matreiAnchorLonLat':list(MATREI),
        'matreiToPassStraightLineKm':round(distance_km(MATREI,ANCHOR),3),
        'separateFromMatreiSource':True,
        'doesNotProveContinuousTerrainCoverage':True,
        'sourceHasUnreviewedModernInfrastructure':True,
        'sourceRoadsNotPeriodRoutes':True,
        'provider':'basemap.at', 'sourceUrl':SOURCE, 'license':'CC BY 4.0',
        'licenseUrl':'https://creativecommons.org/licenses/by/4.0/',
        'requiredAttribution':ATTRIBUTION, 'crs':'EPSG:3857',
        'zoom':ZOOM, 'pixelDimensions':list(SIZE),
        'tileOriginXYZ':[x0,y0,ZOOM],
        'mosaicBoundsLonLat':[west,south,east,north],
        'samples':samples, **{k:False for k in FALSE_FLAGS}}

def validate(m):
    expected = plan()
    require(set(m)-set(expected) <= {'mosaicFile','mosaicSha256','seamDiagnostics'},
            'unapproved source metadata')
    for key,value in expected.items():
        if key == 'samples': continue
        require(m.get(key)==value, 'source identity or false GAME approval: '+key)
    samples = m.get('samples')
    require(isinstance(samples,list) and len(samples)==9, 'missing/extra tiles')
    for got, correct in zip(samples,expected['samples']):
        require(isinstance(got,dict) and
                set(got)-set(correct) <= {'imageFile','sha256','byteCount'},
                'unexpected tile metadata')
        for key,value in correct.items():
            require(got.get(key)==value, 'source tile identity/geometry: '+key)
        if 'imageFile' in got:
            require(got['imageFile']==got['name']+'.jpeg', 'tile filename mismatch')
    return True

def download(m, folder):
    validate(m)
    folder = Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    for item in m['samples']:
        request=Request(item['url'],headers={'User-Agent':'CenturyOfEmpires-SourceAudit/1.0'})
        with urlopen(request,timeout=20) as response:
            data=response.read(1024*1024+1)
            mime=response.headers.get('Content-Type','')
        require(len(data)<=1024*1024 and data.startswith(b'\xff\xd8') and
                'image' in mime.lower(), 'invalid or oversized source response')
        with Image.open(io.BytesIO(data)) as im:
            require(im.format=='JPEG' and im.size==(256,256), 'not native JPEG')
            im.verify()
        name=item['name']+'.jpeg'
        (folder/name).write_bytes(data)
        item.update(imageFile=name,sha256=hashlib.sha256(data).hexdigest(),byteCount=len(data))

def compose(m,folder):
    validate(m)
    folder=Path(folder)
    image=Image.new('RGBA',SIZE,(0,0,0,0))
    hashes=[]
    for item in m['samples']:
        require(item.get('imageFile')==item['name']+'.jpeg' and
                isinstance(item.get('sha256'),str) and len(item['sha256'])==64,
                'missing native JPEG provenance')
        path=folder/item['imageFile']
        require(path.is_file() and sha(path)==item['sha256'], 'tampered source JPEG')
        with Image.open(path) as tile:
            require(tile.format=='JPEG' and tile.size==(256,256), 'wrong JPEG dimensions')
            image.paste(tile.convert('RGBA'),(item['col']*256,item['row']*256))
        hashes.append(item['sha256'])
    require(len(set(hashes))==9, 'duplicate geographic imagery tiles')
    return image

def seams(image):
    result=[]
    for label,x1,y1,x2,y2,dx,dy,n in (
        ('west/center',255,0,256,0,0,1,768),
        ('center/east',511,0,512,0,0,1,768),
        ('north/middle',0,255,0,256,1,0,768),
        ('middle/south',0,511,0,512,1,0,768)):
        differences=[]
        for i in range(n):
            a=image.getpixel((x1+dx*i,y1+dy*i))
            b=image.getpixel((x2+dx*i,y2+dy*i))
            require(a[3]==b[3]==255,'unobserved native source seam')
            differences.append(sum(abs(a[k]-b[k]) for k in range(3))/3)
        result.append({'edge':label,'samples':n,
                       'meanRGBDifference':round(sum(differences)/n,4),
                       'nativeSourcePixelAdjacencyVerified':True,
                       'gameArtSeamApproved':False})
    return result

def produce(m,folder):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    image=compose(m,folder)
    name='brenner-pass-modern-source.png'
    image.save(folder/name,optimize=True)
    m.update(mosaicFile=name,mosaicSha256=sha(folder/name),seamDiagnostics=seams(image))
    (folder/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    verify(folder)
    return m

def verify(folder):
    folder=Path(folder)
    m=json.loads((folder/'manifest.json').read_text())
    expected=compose(m,folder)
    require(m.get('mosaicFile')=='brenner-pass-modern-source.png' and
            sha(folder/m['mosaicFile'])==m.get('mosaicSha256'), 'mosaic hash mismatch')
    with Image.open(folder/m['mosaicFile']) as im:
        require(im.mode=='RGBA' and im.size==SIZE and
                im.tobytes()==expected.tobytes(), 'mosaic pixels altered')
    require(m.get('seamDiagnostics')==seams(expected),'seam diagnostics altered')
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',default='qa/v183-brenner-pass-source')
    p.add_argument('--download',action='store_true')
    p.add_argument('--verify',action='store_true')
    a=p.parse_args()
    folder=Path(a.output)
    if a.verify: verify(folder)
    elif a.download:
        m=plan()
        download(m,folder)
        produce(m,folder)
    else:
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'manifest.json').write_text(json.dumps(plan(),indent=2)+'\n')
    print('V183 native Brenner Pass SOURCE only; roads, bridge and GAME art unapproved')

if __name__=='__main__': main()
