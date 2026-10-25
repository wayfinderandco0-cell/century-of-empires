#!/usr/bin/env python3
"""V199 fail-closed synthetic regression tests; CI also verifies real V197/V198."""
import copy
import json
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
import v199_clean_native_crops as v

count = 0

def check(label, fn):
    global count
    fn()
    count += 1
    print('PASS', label)

def reject(fn):
    try:
        fn()
    except (ValueError, KeyError, FileNotFoundError):
        return
    raise AssertionError('tampered or unsafe source was accepted')

def fixture(root):
    src, quarantine, out = root/'v197', root/'v198', root/'v199'
    src.mkdir(); quarantine.mkdir()
    samples197, samples198 = [], []
    for i, name in enumerate(v.CROPS):
        image = Image.new('RGB', (512,512))
        px = image.load()
        for y in range(512):
            for x in range(512):
                px[x,y] = ((x+11*i)%256, (y+17*i)%256, (x//3+y//4+41*i)%256)
        src_name = name+'.png'
        image.save(src/src_name)
        mask = Image.new('L', (512,512), 0)
        d = ImageDraw.Draw(mask)
        # All outside candidate crops. Each source must still contain exclusions.
        d.rectangle((2,2,9,9), fill=255)
        alpha = mask.point(lambda p: 255-p)
        rgba = image.convert('RGBA'); rgba.putalpha(alpha)
        mask_name = name+'-excluded-mask.png'
        qname = name+'-quarantined.png'
        mask.save(quarantine/mask_name)
        rgba.save(quarantine/qname)
        origin = [130000+i*30, 91000+i*30, 18]
        samples197.append({
            'name': name, 'image': src_name, 'imageSha256': v.sha(src/src_name),
            'nativeOriginXYZ': origin,
            'footprintLonLat': v.lonlat_bounds(origin, (0,0,512,512)),
        })
        samples198.append({
            'name': name, 'sourceImageSha256': v.sha(src/src_name),
            'quarantinedImage': qname, 'quarantinedImageSha256': v.sha(quarantine/qname),
            'maskImage': mask_name, 'maskImageSha256': v.sha(quarantine/mask_name),
            'excludedPixelCount': mask.tobytes().count(255),
            'retainedPixelCount': mask.tobytes().count(0),
        })
    m197 = {
        'version':197, 'requiredAttribution':'Datenquelle: basemap.at',
        'license':'CC BY 4.0', 'notGameOctagonCenters':True, 'samples':samples197,
    }
    (src/'manifest.json').write_text(json.dumps(m197))
    m198 = {
        'version':198, 'requiredAttribution':'Datenquelle: basemap.at',
        'license':'CC BY 4.0', 'sourceManifestSha256':v.sha(src/'manifest.json'),
        'geographicRegistrationToV123':False,
        'unreviewedModernFeaturesRemain':True,
        'samples':samples198,
        **{k:False for k in v.FORBIDDEN_TRUE},
    }
    (quarantine/'manifest.json').write_text(json.dumps(m198))
    return src, quarantine, out

def roundtrip():
    with tempfile.TemporaryDirectory() as t:
        a,b,c=fixture(Path(t))
        m=v.produce(a,b,c)
        assert v.verify(a,b,c)
        assert len(m['crops'])==9
        assert m['gameWorldRegistrationKnown'] is False
        assert m['onlyAnnotatedFeaturesExcluded'] is True
        assert all(item['eligibleForGameArt'] is False for item in m['crops'])
        assert all(item['annotatedFeaturePixelsInside']==0 for item in m['crops'])
        with Image.open(c/m['contactSheet']) as im:
            assert im.size == (480, 564)

def registration():
    b=v.lonlat_bounds([139000,91000,18],(20,35,180,195))
    assert b[0]<b[2] and b[1]<b[3]
    assert b==v.lonlat_bounds([139000,91000,18],(20,35,180,195))
    reject(lambda:v.lonlat_bounds([139000,91000,17],(20,35,180,195)))

def corrupted_crop():
    with tempfile.TemporaryDirectory() as t:
        a,b,c=fixture(Path(t));m=v.produce(a,b,c)
        p=c/m['crops'][0]['name']
        with Image.open(p) as im: x=im.copy()
        x.putpixel((0,0),(255,0,0));x.save(p)
        reject(lambda:v.verify(a,b,c))

def forged_geography():
    with tempfile.TemporaryDirectory() as t:
        a,b,c=fixture(Path(t));m=v.produce(a,b,c)
        p=c/'manifest.json';data=json.loads(p.read_text())
        data['crops'][0]['footprintLonLat'][0]+=0.01
        p.write_text(json.dumps(data))
        reject(lambda:v.verify(a,b,c))

def forged_approval():
    with tempfile.TemporaryDirectory() as t:
        a,b,c=fixture(Path(t));v.produce(a,b,c)
        p=c/'manifest.json';data=json.loads(p.read_text())
        data['gameArtApproved']=True
        p.write_text(json.dumps(data))
        reject(lambda:v.verify(a,b,c))

def mask_intrusion():
    with tempfile.TemporaryDirectory() as t:
        a,b,c=fixture(Path(t));v.produce(a,b,c)
        name=list(v.CROPS)[0]
        path=b/(name+'-excluded-mask.png')
        with Image.open(path) as im: mask=im.copy()
        mask.putpixel((42,70),255);mask.save(path)
        meta=b/'manifest.json';m=json.loads(meta.read_text())
        m['samples'][0]['maskImageSha256']=v.sha(path)
        m['samples'][0]['excludedPixelCount']=mask.tobytes().count(255)
        m['samples'][0]['retainedPixelCount']=mask.tobytes().count(0)
        meta.write_text(json.dumps(m))
        reject(lambda:v.plan(a,b))

def source_tamper():
    with tempfile.TemporaryDirectory() as t:
        a,b,c=fixture(Path(t));v.produce(a,b,c)
        name=list(v.CROPS)[0]
        p=a/(name+'.png')
        with Image.open(p) as im: image=im.copy()
        image.putpixel((30,30),(255,0,0));image.save(p)
        reject(lambda:v.plan(a,b))

def bad_parent_manifest():
    with tempfile.TemporaryDirectory() as t:
        a,b,c=fixture(Path(t));v.produce(a,b,c)
        p=a/'manifest.json';data=json.loads(p.read_text())
        data['samples'][0]['nativeOriginXYZ']=[0,0,18]
        p.write_text(json.dumps(data))
        reject(lambda:v.plan(a,b))

def alpha_tamper():
    with tempfile.TemporaryDirectory() as t:
        a,b,c=fixture(Path(t));v.produce(a,b,c)
        name=list(v.CROPS)[0]
        p=b/(name+'-quarantined.png')
        with Image.open(p) as im: rgba=im.copy()
        rgba.putpixel((5,5),(*rgba.getpixel((5,5))[:3],255));rgba.save(p)
        meta=b/'manifest.json';data=json.loads(meta.read_text())
        data['samples'][0]['quarantinedImageSha256']=v.sha(p)
        meta.write_text(json.dumps(data))
        reject(lambda:v.plan(a,b))

def overlapping_crops():
    original=copy.deepcopy(v.CROPS)
    try:
        name=list(v.CROPS)[0]
        v.CROPS[name]=(original[name][0],original[name][0],original[name][2])
        with tempfile.TemporaryDirectory() as t:
            a,b,_=fixture(Path(t))
            reject(lambda:v.plan(a,b))
    finally:
        v.CROPS.clear();v.CROPS.update(original)

for label, fn in (
    ('nine clean native source crops and contact',roundtrip),
    ('EPSG:3857 native geographic pixel conversion',registration),
    ('corrupted crop rejected',corrupted_crop),
    ('forged crop geography rejected',forged_geography),
    ('game approval forgery rejected',forged_approval),
    ('mask intrusion rejected even with updated SHA',mask_intrusion),
    ('altered source image rejected',source_tamper),
    ('tampered parent registration rejected',bad_parent_manifest),
    ('quarantine alpha forgery rejected',alpha_tamper),
    ('overlapping native crops rejected',overlapping_crops),
):
    check(label,fn)
print(f'V199 {count} synthetic fail-closed tests PASS; game visual approval not tested')
