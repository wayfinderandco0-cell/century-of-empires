#!/usr/bin/env python3
"""Offline V155 source-pixel and fail-closed regression; synthetic fixture."""
import copy
import hashlib
import json
import tempfile
from pathlib import Path
from PIL import Image
from v155_material_candidates import (CROPS,UNAPPROVED,verify_geometry,
                                      verify_source,produce,verify_output)

positive=0
negative=0
def reject(fn,label):
    global negative
    try: fn()
    except (ValueError,KeyError,TypeError,FileNotFoundError): negative+=1
    else: raise AssertionError('Accepted invalid input: '+label)

with tempfile.TemporaryDirectory() as tmp:
    src=Path(tmp)/'src';out=Path(tmp)/'out';src.mkdir()
    # Synthetic RGB image for deterministic OFFLINE tests; never game art.
    im=Image.new('RGB',(2304,768))
    for y in range(768):
        for x in range(2304):
            im.putpixel((x,y),((x//11)%256,(y//7)%256,((x+y)//13)%256))
    im.save(src/'modern-source-strip.png')
    m={'version':153,'grid':[3,9],'pixelDimensions':[2304,768],
       'crs':'EPSG:3857','provider':'basemap.at','license':'CC BY 4.0',
       'requiredAttribution':'Datenquelle: basemap.at',
       'mosaicFile':'modern-source-strip.png',
       'mosaicSha256':hashlib.sha256((src/'modern-source-strip.png').read_bytes()).hexdigest(),
       'sectors':[{'name':f'source-{n}','pixelBounds':[i*768,0,(i+1)*768,768]}
                  for i,n in enumerate(('west','center','east'))],
       'samples':[{'name':f'r{r}c{c}','gridRow':r,'gridCol':c,
                   'sha256':hashlib.sha256(f'synthetic-r{r}c{c}'.encode()).hexdigest()}
                  for r in range(3) for c in range(9)]}
    for k in ('gameOctagonCentersCertified','gameRouteGeoregistered',
              'historic1780Certified','navigableRouteCertified',
              'bridgeBanksVerified','productionApproved'):m[k]=False
    (src/'manifest.json').write_text(json.dumps(m))
    assert verify_geometry()
    report=produce(src,out)
    assert verify_output(src,out)
    assert len(report['candidates'])==6
    assert all(v is False for k,v in UNAPPROVED.items() if k!='manualArtReviewRequired')
    assert report['manualArtReviewRequired'] is True
    assert len({c['sha256'] for c in report['candidates']})==6
    positive+=6

    bad=copy.deepcopy(m);bad['productionApproved']=True
    reject(lambda:verify_source(bad,src),'forged production approval')
    bad=copy.deepcopy(m);bad['samples'][0]['sha256']='not-a-sha'
    reject(lambda:verify_source(bad,src),'bad JPEG provenance')
    bad=copy.deepcopy(m);bad['sectors'][1]['pixelBounds'][0]=770
    reject(lambda:verify_source(bad,src),'shifted sector')
    bad=copy.deepcopy(m);bad['mosaicSha256']='0'*64
    reject(lambda:verify_source(bad,src),'source SHA256 mismatch')
    bad=copy.deepcopy(m);bad['requiredAttribution']=''
    reject(lambda:verify_source(bad,src),'missing attribution')
    reject(lambda:verify_geometry(CROPS[:5]),'missing source sample')
    bad_crops=list(CROPS);bad_crops[0]=(*bad_crops[0][:3],(100,100,228,228))
    reject(lambda:verify_geometry(tuple(bad_crops)),'watermark zone')
    bad_crops=list(CROPS);bad_crops[2]=(*bad_crops[2][:3],(740,160,868,288))
    reject(lambda:verify_geometry(tuple(bad_crops)),'cross-sector crop')
    good=json.loads((out/'manifest.json').read_text())
    bad=copy.deepcopy(good);bad['gameRouteGeoregistered']=True
    (out/'manifest.json').write_text(json.dumps(bad))
    reject(lambda:verify_output(src,out),'forged road registration')
    bad=copy.deepcopy(good);bad['candidates'][1]['pixelBounds'][0]+=1
    (out/'manifest.json').write_text(json.dumps(bad))
    reject(lambda:verify_output(src,out),'changed crop bounds')
    bad=copy.deepcopy(good);bad['candidates'][3]['sourceTileRefs'][0]['sourceJpegSha256']='f'*64
    (out/'manifest.json').write_text(json.dumps(bad))
    reject(lambda:verify_output(src,out),'changed source tile')
    (out/'manifest.json').write_text(json.dumps(good))
    path=out/good['candidates'][0]['file'];original=path.read_bytes()
    path.write_bytes(b'corrupt')
    reject(lambda:verify_output(src,out),'changed PNG bytes')
    path.write_bytes(original)
    assert verify_output(src,out)
    positive+=1
print(f'V155 PASS: {positive} positive checks, {negative} fail-closed negatives; modern material references only')
