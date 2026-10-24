#!/usr/bin/env python3
"""V168: real-source FIRST L-shaped three-octagon terrain reference.

This is an independent geographic SOURCE study, NOT a V121/V123 game-frame
registration, not a historical route survey, and not finished period game art.
Uses 18 distinct native-resolution basemap.at orthophoto tiles in a 6x4
source-pixel rectangle, with the southwest 3x2 quadrant explicitly UNKNOWN.
Unlike the earlier 3x9 source strip, the footprint matches the L topology of
West -> Center -> South, at half-scale of the immutable V123 pixel layout.
No photo is repeated, stretched or copied into another octagon.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image

ZOOM=17
CENTER=(11.520,47.130)
SOURCE='https://basemap.at/orthofoto/'
BASE='https://mapsneu.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857'
ATTRIBUTION='Datenquelle: basemap.at'
SIZE=(1536,1024)
CELL=(768,512)
CUT=128
SECTORS={
    'source-west':(0,0,768,512),
    'source-center':(768,0,1536,512),
    'source-south':(768,512,1536,1024),
}
NO_APPROVAL={
    'sourceSectorsAreGameOctagons':False,
    'v121ToGeographyRegistered':False,
    'v123RoadsGeoregistered':False,
    'historic1780Certified':False,
    'historicalRoadsVerified':False,
    'bridgeBanksVerified':False,
    'periodArtComplete':False,
    'physicalIPhoneApproved':False,
    'productionApproved':False,
}

def require(condition,message):
    if not condition:raise ValueError(message)

def xyz(lon,lat,z):
    require(-180<=lon<=180 and -85.05112878<lat<85.05112878 and 0<=z<=20,
            'invalid EPSG:3857 coordinate')
    n=1<<z
    return (min(n-1,max(0,math.floor((lon+180)/360*n))),
            min(n-1,max(0,math.floor((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n))))

def xyz_bounds(x,y,z):
    n=1<<z
    require(0<=x<n and 0<=y<n,'invalid XYZ tile')
    lat=lambda row:math.degrees(math.atan(math.sinh(math.pi*(1-2*row/n))))
    return [x/n*360-180,lat(y+1),(x+1)/n*360-180,lat(y)]

def octagon(origin):
    x,y=origin;w,h=CELL;c=CUT
    return [[x+c,y],[x+w-c,y],[x+w,y+c],[x+w,y+h-c],
            [x+w-c,y+h],[x+c,y+h],[x,y+h-c],[x,y+c]]

def plan(v102):
    require(v102.get('version')==102,'expected V102 geographic manifest')
    bounds=v102.get('boundsLonLat')
    require(isinstance(bounds,list) and len(bounds)==4 and
            all(type(t) in (int,float) and math.isfinite(t) for t in bounds) and
            bounds[0]<bounds[2] and bounds[1]<bounds[3],
            'invalid Navis source extent')
    cx,cy=xyz(*CENTER,ZOOM)
    # Keep CENTER inside source-center; 6 cols, 4 rows, lower-left quadrant
    # unknown. 3x2 source tiles form each game-proportioned 768x512 footprint.
    x0,y0=cx-4,cy-1
    records=[]
    for row in range(4):
        for col in range(6):
            if row>=2 and col<3:continue
            x,y=x0+col,y0+row
            geo=xyz_bounds(x,y,ZOOM)
            require(bounds[0]<=geo[0]<geo[2]<=bounds[2] and
                    bounds[1]<=geo[1]<geo[3]<=bounds[3],
                    'source L footprint exceeds V102 Navis bounds')
            sector='source-west' if col<3 else ('source-center' if row<2 else 'source-south')
            records.append({'name':f'r{row}c{col}','row':row,'col':col,
                            'sourceSector':sector,'tileXYZ':[x,y,ZOOM],
                            'boundsLonLat':geo,'url':f'{BASE}/{ZOOM}/{y}/{x}.jpeg'})
    require(len(records)==18 and len({tuple(r['tileXYZ']) for r in records})==18,
            'expected 18 unique original-pixel geographic tiles')
    outer=xyz_bounds(x0,y0,ZOOM)
    far=xyz_bounds(x0+5,y0+3,ZOOM)
    return {'version':168,'purpose':'Modern geographic L-layout reference only; NOT game art',
            'provider':'basemap.at','sourceUrl':SOURCE,'license':'CC BY 4.0',
            'licenseUrl':'https://creativecommons.org/licenses/by/4.0/',
            'requiredAttribution':ATTRIBUTION,'crs':'EPSG:3857',
            'sourceManifest':'terrain-v102/manifest.json','zoom':ZOOM,
            'pixelDimensions':list(SIZE),'cellPixelDimensions':list(CELL),
            'centerLonLat':list(CENTER),
            'mosaicBoundsLonLat':[outer[0],far[1],far[2],outer[3]],
            'unobservedSouthwestBoundsPixels':[0,512,768,1024],
            'unobservedSouthwestMeaning':'No image acquired; NEVER invent terrain or a route',
            'sourceSectors':[{'id':k,'pixelBounds':list(v),'octagonPolygon':octagon(v[:2])}
                             for k,v in SECTORS.items()],
            'samples':records,'mosaicFile':'modern-source-L.png',
            'sourceImageSeamDiagnostics':[],**NO_APPROVAL}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_manifest(m):
    require(m.get('version')==168 and m.get('provider')=='basemap.at' and
            m.get('crs')=='EPSG:3857' and m.get('requiredAttribution')==ATTRIBUTION,
            'untrusted source metadata')
    require(m.get('pixelDimensions')==list(SIZE) and
            m.get('cellPixelDimensions')==list(CELL), 'source pixel dimensions changed')
    require(m.get('unobservedSouthwestBoundsPixels')==[0,512,768,1024],
            'unknown quadrant silently filled')
    for k,v in NO_APPROVAL.items():require(m.get(k) is v,'forged approval: '+k)
    require([(s.get('id'),s.get('pixelBounds'),s.get('octagonPolygon'))
             for s in m.get('sourceSectors',[])]==
            [(k,list(v),octagon(v[:2])) for k,v in SECTORS.items()],
            'L sector geometry changed')
    records=m.get('samples',[])
    require(len(records)==18,'missing or duplicated source tile')
    cx,cy=xyz(*CENTER,ZOOM);x0,y0=cx-4,cy-1
    for record,(row,col) in zip(records,((r,c) for r in range(4) for c in range(6)
                                          if r<2 or c>=3)):
        tile=[x0+col,y0+row,ZOOM]
        sector='source-west' if col<3 else ('source-center' if row<2 else 'source-south')
        require(record.get('name')==f'r{row}c{col}' and record.get('row')==row and
                record.get('col')==col and record.get('tileXYZ')==tile and
                record.get('sourceSector')==sector and
                record.get('boundsLonLat')==xyz_bounds(*tile) and
                record.get('url')==f'{BASE}/{ZOOM}/{tile[1]}/{tile[0]}.jpeg',
                'geographic tile order/coordinates changed')
    return True

def compose(m,directory):
    validate_manifest(m)
    mosaic=Image.new('RGBA',SIZE,(0,0,0,0))
    for record in m['samples']:
        path=directory/(record['name']+'.jpeg')
        require(path.is_file() and record.get('imageFile')==path.name and
                record.get('sha256')==sha(path),'missing/tampered source tile: '+record['name'])
        with Image.open(path) as im:
            require(im.format=='JPEG' and im.size==(256,256),'invalid native source tile')
            tile=im.convert('RGBA')
        mosaic.paste(tile,(record['col']*256,record['row']*256))
    require(mosaic.getpixel((0,700))[3]==0 and
            mosaic.getpixel((768,700))[3]==255 and
            mosaic.getpixel((700,500))[3]==255,
            'unobserved quadrant must remain transparent')
    return mosaic

def seam_diagnostics(mosaic):
    require(mosaic.mode=='RGBA' and mosaic.size==SIZE,'wrong L source raster')
    edges=(('source-west/source-center',(767,128),(768,128),(0,1),256),
           ('source-center/source-south',(896,511),(896,512),(1,0),512))
    result=[]
    for label,left,right,step,count in edges:
        differences=[]
        for i in range(count):
            x,y=left[0]+step[0]*i,left[1]+step[1]*i
            u,v=right[0]+step[0]*i,right[1]+step[1]*i
            a,b=mosaic.getpixel((x,y)),mosaic.getpixel((u,v))
            require(a[3]==b[3]==255,'source image gap at shared octagon border')
            differences.append(sum(abs(a[j]-b[j]) for j in range(3))/3)
        result.append({'sharedEdge':label,'sampleCount':count,
                       'meanAdjacentPixelRGBDifference':round(sum(differences)/count,4),
                       'maxAdjacentPixelRGBDifference':round(max(differences),4),
                       'sourceImagePixelsPresent':True,
                       'visualSeamAccepted':False})
    return result

def produce(m,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    image=compose(m,directory)
    m['sourceImageSeamDiagnostics']=seam_diagnostics(image)
    image.save(directory/m['mosaicFile'],optimize=True)
    m['mosaicSha256']=sha(directory/m['mosaicFile'])
    m['sectorSha256']={}
    for k,box in SECTORS.items():
        name=k+'.png';image.crop(box).save(directory/name,optimize=True)
        m['sectorSha256'][k]=sha(directory/name)
    (directory/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    verify(directory)
    return m

def verify(directory):
    directory=Path(directory);m=json.loads((directory/'manifest.json').read_text())
    source=compose(m,directory)
    require(sha(directory/m['mosaicFile'])==m.get('mosaicSha256'),
            'source L mosaic SHA256 mismatch')
    with Image.open(directory/m['mosaicFile']) as im:
        require(im.mode=='RGBA' and im.size==SIZE and im.tobytes()==source.tobytes(),
                'source mosaic pixels differ from original geographic tiles')
    require(m.get('sourceImageSeamDiagnostics')==seam_diagnostics(source),
            'seam diagnostics changed')
    require(set(m.get('sectorSha256',{}))==set(SECTORS),'missing sector')
    for k,box in SECTORS.items():
        path=directory/(k+'.png')
        require(sha(path)==m['sectorSha256'][k],'sector SHA256 mismatch: '+k)
        with Image.open(path) as im:
            require(im.mode=='RGBA' and im.size==CELL and
                    im.tobytes()==source.crop(box).tobytes(),
                    'sector pixels not native source: '+k)
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest',default='terrain-v102/manifest.json')
    parser.add_argument('--output',default='qa/v168-source-L')
    parser.add_argument('--download',action='store_true')
    parser.add_argument('--verify',action='store_true')
    a=parser.parse_args()
    if a.verify:
        verify(a.output)
    else:
        m=plan(json.loads(Path(a.manifest).read_text()))
        if a.download:
            from v146_orthophoto_sample import fetch_images
            fetch_images(m,Path(a.output))
            produce(m,Path(a.output))
        else:
            Path(a.output).mkdir(parents=True,exist_ok=True)
            (Path(a.output)/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print('V168 source-first L: 18 native orthophoto tiles; no historical/game/visual approval')

if __name__=='__main__':main()
