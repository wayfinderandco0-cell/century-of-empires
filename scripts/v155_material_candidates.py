#!/usr/bin/env python3
"""V155: exact modern Alpine material REFERENCES; never certified game terrain.

Six 128px boxes were visually inspected in the genuine V153 source strip.
They avoid conspicuous roads, roofs and date labels at inspection resolution,
but this is not a certified modern-infrastructure clearance. Never tile them
as 1780–1880 artwork or map them onto V121/V123 without independent controls.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from PIL import Image

SIZE=(2304,768)
SOURCE='modern-source-strip.png'
ATTRIBUTION='Datenquelle: basemap.at'
CROPS=(
    ('west-canopy','source-west','canopy',(130,150,258,278)),
    ('west-meadow','source-west','meadow',(0,480,128,608)),
    ('center-canopy','source-center','canopy',(780,160,908,288)),
    ('center-meadow','source-center','meadow',(960,580,1088,708)),
    ('east-canopy','source-east','canopy',(1716,20,1844,148)),
    ('east-meadow','source-east','meadow',(2000,450,2128,578)),
)
UNAPPROVED=dict(gameOctagonsMapped=False,gameRouteGeoregistered=False,
                historicalRoadEvidence=False,historic1780Certified=False,
                modernInfrastructureCleared=False,bridgeBanksVerified=False,
                productionApproved=False,manualArtReviewRequired=True)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify_geometry(crops=CROPS):
    if len(crops)!=6 or len({c[0] for c in crops})!=6:
        raise ValueError('Expected six unique source candidates')
    for name,sector,kind,box in crops:
        if not re.fullmatch(r'(west|center|east)-(canopy|meadow)',name) or kind not in ('canopy','meadow'):
            raise ValueError('Invalid candidate name or material class')
        if name!=sector.removeprefix('source-')+'-'+kind:
            raise ValueError('Candidate sector/class mismatch')
        if not isinstance(box,(tuple,list)) or len(box)!=4 or any(type(v) is not int for v in box):
            raise ValueError('Invalid source-pixel coordinates')
        x0,y0,x1,y1=box
        if x1-x0!=128 or y1-y0!=128 or not(0<=x0<x1<=SIZE[0] and 0<=y0<y1<=SIZE[1]):
            raise ValueError('Expected 128x128 original-pixel crop')
        if not(x0//768==(x1-1)//768=={'source-west':0,'source-center':1,'source-east':2}[sector]):
            raise ValueError('Crop crosses source-sector boundary')
        for row in range(3):
            for col in range(9):
                # Known 2023 source labels appear around each 256px tile center.
                # Conservative exclusion is not a guarantee of no other labels.
                wx,wy=col*256+128,row*256+128
                if x0<wx+48 and x1>wx-48 and y0<wy+20 and y1>wy-20:
                    raise ValueError('Crop overlaps known modern date watermark')
    return True

def verify_source(m,source_dir):
    verify_geometry()
    if m.get('version')!=153 or m.get('grid')!=[3,9] or m.get('pixelDimensions')!=list(SIZE):
        raise ValueError('Unexpected V153 geographic source dimensions')
    if m.get('crs')!='EPSG:3857' or m.get('provider')!='basemap.at' or m.get('license')!='CC BY 4.0' or m.get('requiredAttribution')!=ATTRIBUTION:
        raise ValueError('Source CRS, provider or attribution changed')
    if m.get('mosaicFile')!=SOURCE or not re.fullmatch(r'[0-9a-f]{64}',m.get('mosaicSha256','')):
        raise ValueError('Missing source mosaic SHA256')
    if [(s.get('name'),s.get('pixelBounds')) for s in m.get('sectors',[])]!=[
        ('source-west',[0,0,768,768]),('source-center',[768,0,1536,768]),
        ('source-east',[1536,0,2304,768])]:
        raise ValueError('Source sector bounds changed')
    samples=m.get('samples',[])
    if len(samples)!=27:
        raise ValueError('Missing original source tiles')
    for row in range(3):
        for col in range(9):
            t=samples[row*9+col]
            if t.get('name')!=f'r{row}c{col}' or t.get('gridRow')!=row or t.get('gridCol')!=col or not re.fullmatch(r'[0-9a-f]{64}',t.get('sha256','')):
                raise ValueError('Source tile provenance missing or reordered')
    for key in ('gameOctagonCentersCertified','gameRouteGeoregistered',
                'historic1780Certified','navigableRouteCertified',
                'bridgeBanksVerified','productionApproved'):
        if m.get(key) is not False:
            raise ValueError('Unverified historical/game source claim')
    data=(source_dir/SOURCE).read_bytes()
    if digest(data)!=m['mosaicSha256']:
        raise ValueError('Source mosaic SHA256 mismatch')
    with Image.open(source_dir/SOURCE) as im:
        if im.format!='PNG' or im.size!=SIZE:
            raise ValueError('Unexpected source image dimensions or encoding')
        return im.convert('RGB')

def expected_manifest(m):
    candidates=[]
    for name,sector,kind,box in CROPS:
        x0,y0,x1,y1=box
        refs=[]
        for row in range(y0//256,(y1-1)//256+1):
            for col in range(x0//256,(x1-1)//256+1):
                t=m['samples'][row*9+col]
                refs.append({'tileName':t['name'],'sourceJpegSha256':t['sha256']})
        candidates.append({'name':name,'sourceSector':sector,
                           'modernMaterialClass':kind,'pixelBounds':list(box),
                           'sourceTileRefs':refs,'file':name+'.png'})
    return {'version':155,'purpose':'Modern Alpine photographic material references only',
            'sourceVersion':153,'sourceMosaicSha256':m['mosaicSha256'],
            'sourceCrs':'EPSG:3857','requiredAttribution':ATTRIBUTION,
            'license':'CC BY 4.0','pixelExact':True,
            'candidateCount':len(candidates),**UNAPPROVED,
            'candidates':candidates}

def produce(source_dir,out_dir):
    m=json.loads((source_dir/'manifest.json').read_text())
    raster=verify_source(m,source_dir)
    out_dir.mkdir(parents=True,exist_ok=True)
    report=expected_manifest(m)
    for candidate in report['candidates']:
        crop=raster.crop(tuple(candidate['pixelBounds']))
        path=out_dir/candidate['file']
        crop.save(path,optimize=True)
        candidate['sha256']=digest(path.read_bytes())
    (out_dir/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    verify_output(source_dir,out_dir)
    return report

def verify_output(source_dir,out_dir):
    m=json.loads((source_dir/'manifest.json').read_text())
    raster=verify_source(m,source_dir)
    report=json.loads((out_dir/'manifest.json').read_text())
    expected=expected_manifest(m)
    if set(report)!=set(expected) or any(report[k]!=v for k,v in expected.items() if k!='candidates'):
        raise ValueError('Candidate manifest metadata or approval flags changed')
    if len(report.get('candidates',[]))!=len(expected['candidates']):
        raise ValueError('Candidate list incomplete')
    for got,want in zip(report['candidates'],expected['candidates']):
        if set(got)!=set(want)|{'sha256'} or any(got[k]!=v for k,v in want.items()):
            raise ValueError('Candidate coordinates or source identity changed')
        if not re.fullmatch(r'[0-9a-f]{64}',got.get('sha256','')):
            raise ValueError('Missing candidate image SHA256')
        path=out_dir/got['file']
        if digest(path.read_bytes())!=got['sha256']:
            raise ValueError('Candidate image SHA256 mismatch')
        with Image.open(path) as im:
            if im.format!='PNG' or im.size!=(128,128) or im.convert('RGB').tobytes()!=raster.crop(tuple(got['pixelBounds'])).tobytes():
                raise ValueError('Candidate image is not an exact source-pixel crop')
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',default='qa/v153-geographic-strip')
    p.add_argument('--output',default='qa/v155-material-candidates')
    p.add_argument('--verify',action='store_true')
    a=p.parse_args()
    if a.verify:
        verify_output(Path(a.source),Path(a.output))
    else:
        produce(Path(a.source),Path(a.output))
    print('V155 PASS: 6 exact modern source material references, provenance and pixel integrity; game and historical art UNAPPROVED')

if __name__=='__main__':
    main()
