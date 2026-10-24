#!/usr/bin/env python3
"""V156 offline synthetic QA: excludes modern source candidates, never approves game art."""
import copy
import hashlib
import json
import tempfile
from pathlib import Path
from PIL import Image
from v156_modern_exclusion import (SIZE,CORRIDORS,UNAPPROVED,make_mask,
    validate_geometry,sector_coverage,produce,verify_output)

negative=0

def reject(fn,label):
    global negative
    try:fn()
    except (ValueError,TypeError,KeyError,FileNotFoundError,OSError):negative+=1
    else:raise AssertionError('Fail-closed case was accepted: '+label)

with tempfile.TemporaryDirectory() as temp:
    src=Path(temp)/'src';out=Path(temp)/'out';src.mkdir()
    # Deliberately synthetic; only real-source CI may establish genuine pixels.
    image=Image.new('RGB',SIZE,(85,123,76))
    image.save(src/'modern-source-strip.png')
    m={'version':153,'grid':[3,9],'pixelDimensions':list(SIZE),
       'crs':'EPSG:3857','provider':'basemap.at','license':'CC BY 4.0',
       'requiredAttribution':'Datenquelle: basemap.at',
       'mosaicFile':'modern-source-strip.png',
       'mosaicSha256':hashlib.sha256((src/'modern-source-strip.png').read_bytes()).hexdigest(),
       'sectors':[{'name':f'source-{name}','pixelBounds':[i*768,0,(i+1)*768,768]}
                  for i,name in enumerate(('west','center','east'))],
       'samples':[{'name':f'r{r}c{c}','gridRow':r,'gridCol':c,
                   'sha256':hashlib.sha256(f'synthetic-{r}-{c}'.encode()).hexdigest()}
                  for r in range(3) for c in range(9)]}
    for k in ('gameOctagonCentersCertified','gameRouteGeoregistered',
              'historic1780Certified','navigableRouteCertified',
              'bridgeBanksVerified','productionApproved'):m[k]=False
    (src/'manifest.json').write_text(json.dumps(m))
    assert validate_geometry()
    mask=make_mask();coverage=sector_coverage(mask)
    assert len(coverage)==3 and all(0.1<v<0.9 for v in coverage.values())
    for row in range(3):
        for col in range(9):
            assert mask.getpixel((col*256+128,row*256+128))==0
    for _name,_radius,points in CORRIDORS:
        assert all(mask.getpixel(point)==0 for point in points)
    report=produce(src,out)
    assert verify_output(src,out)
    assert report['productionApproved'] is False
    assert report['modernInfrastructureCleared'] is False
    assert report['manualArtReviewRequired'] is True
    assert all(report[k] is False for k in UNAPPROVED if k!='manualArtReviewRequired')

    reject(lambda:validate_geometry(CORRIDORS[:2]),'missing modern exclusion')
    bad=list(CORRIDORS);name,r,pts=bad[0];bad[0]=(name,r,((9999,400),)+pts[1:])
    reject(lambda:validate_geometry(tuple(bad)),'out of bounds observation')
    bad=list(CORRIDORS);name,r,pts=bad[0];bad[0]=(name,5,pts)
    reject(lambda:validate_geometry(tuple(bad)),'narrowed unreviewed mask')
    bad=list(CORRIDORS);name,r,pts=bad[0];bad[0]=(name,r,((900,400),(1000,400),(1100,400)))
    reject(lambda:validate_geometry(tuple(bad)),'modern source coverage truncated')
    bad=copy.deepcopy(report);bad['productionApproved']=True
    (out/'manifest.json').write_text(json.dumps(bad))
    reject(lambda:verify_output(src,out),'forged production approval')
    bad=copy.deepcopy(report);bad['historicalRoadEvidence']=True
    (out/'manifest.json').write_text(json.dumps(bad))
    reject(lambda:verify_output(src,out),'forged historic road evidence')
    bad=copy.deepcopy(report);bad['sourceSectorRetainedFractions']['source-east']=1.0
    (out/'manifest.json').write_text(json.dumps(bad))
    reject(lambda:verify_output(src,out),'forged modern-source coverage')
    bad=copy.deepcopy(report);bad['unexpectedPlayableRoute']=[1,2]
    (out/'manifest.json').write_text(json.dumps(bad))
    reject(lambda:verify_output(src,out),'extra navigability claim')
    (out/'manifest.json').write_text(json.dumps(report))
    p=out/'modern-exclusion-mask.png';original=p.read_bytes();p.write_bytes(b'broken')
    reject(lambda:verify_output(src,out),'corrupted alpha mask')
    p.write_bytes(original)
    p=out/'modern-exclusion-reference.png';original=p.read_bytes();p.write_bytes(b'broken')
    reject(lambda:verify_output(src,out),'corrupted source reference')
    p.write_bytes(original)
    assert verify_output(src,out)
print(f'V156 PASS: 3 source sectors, 27 candidate watermark exclusions, 3 modern corridor candidates, {negative} fail-closed negative cases; no historical/game approval')
