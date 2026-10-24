#!/usr/bin/env python3
"""V156: visible-source-only MODERN exclusion study; never game art.

Conservatively suppresses *candidate* 2023 watermarks, paved-road corridors,
and buildings in the modern V153 Navis aerial mosaic. The observed polylines
are deliberately broad visual-review masks, NOT historical routes or geometry
for the V121/V123 game. Transparent pixels mean 'unknown/needs authored art',
not a road, bridge, pasture, or permission to fill from a repeated patch.

This does NOT claim every modern feature has been found. Source is still
modern, and no historical land-cover, bridge or game-road mapping is approved.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
from v155_material_candidates import verify_source, ATTRIBUTION

SIZE=(2304,768)
# Approximate visible 2023 paved-road and adjacent developed-area corridors,
# traced from the original 2304x768 modern-source mosaic. These are exclusion
# candidates only, NOT playable or historic routes. Radius in source pixels.
CORRIDORS=(
    ('visible-modern-central-road',88,(
        (0,692),(100,655),(190,628),(270,595),(350,552),
        (440,521),(550,511),(680,499),(800,475),(940,417),
        (1040,363),(1120,317),(1160,260),(1198,320),
        (1270,354),(1380,356),(1490,341),(1600,343),
        (1710,328),(1810,268),(1900,241),(1990,226),
        (2090,218),(2190,178),(2303,139))),
    ('visible-modern-south-road',77,(
        (1410,767),(1490,707),(1590,661),(1700,632),
        (1810,609),(1930,565),(2040,545),(2180,532),(2303,515))),
    ('visible-modern-northwest-track',35,(
        (0,29),(95,18),(165,11),(238,28))),
)
# A few detached visible roofs not guaranteed to fall inside the broad road
# corridors. This is intentionally NOT a complete building detector.
DETACHED_OBSERVATIONS=((216,15,28),(370,52,26),(1258,79,27),
                       (1430,472,22),(1411,449,22))
UNAPPROVED={
    'gameOctagonsMapped':False,
    'gameRouteGeoregistered':False,
    'historic1780Certified':False,
    'historicalRoadEvidence':False,
    'bridgeBanksVerified':False,
    'modernInfrastructureCleared':False,
    'allModernFeaturesDetected':False,
    'periodArtComplete':False,
    'productionApproved':False,
    'manualArtReviewRequired':True,
}

def digest(data):return hashlib.sha256(data).hexdigest()

def validate_geometry(corridors=CORRIDORS,detached=DETACHED_OBSERVATIONS):
    if len(corridors)!=3 or len({c[0] for c in corridors})!=3:
        raise ValueError('Missing/duplicated source exclusion corridors')
    for name,radius,points in corridors:
        if not name.startswith('visible-modern-') or type(radius) is not int or not 12<=radius<=100:
            raise ValueError('Untrusted exclusion corridor or radius')
        if len(points)<3:
            raise ValueError('Incomplete observed modern corridor')
        for x,y in points:
            if type(x) is not int or type(y) is not int or not(0<=x<SIZE[0] and 0<=y<SIZE[1]):
                raise ValueError('Exclusion coordinates outside source image')
    if len(detached)!=5:
        raise ValueError('Detached source observations changed')
    for x,y,r in detached:
        if any(type(v) is not int for v in (x,y,r)) or not(0<=x<SIZE[0] and 0<=y<SIZE[1] and 8<=r<=40):
            raise ValueError('Invalid detached source observation')
    # Ensure the main exclusion passes all three *source* sectors; this is
    # not evidence that it is a historical game road.
    xs=[p[0] for p in corridors[0][2]]
    if min(xs)>100 or max(xs)<2200 or not any(768<=x<1536 for x in xs):
        raise ValueError('Main modern exclusion does not span all source sectors')
    return True

def make_mask(corridors=CORRIDORS,detached=DETACHED_OBSERVATIONS):
    validate_geometry(corridors,detached)
    mask=Image.new('L',SIZE,255)  # 255=retained source; 0=excluded/unknown
    d=ImageDraw.Draw(mask)
    for _name,radius,points in corridors:
        d.line(points,fill=0,width=radius*2,joint='curve')
        for x,y in points:
            d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=0)
    for x,y,r in detached:
        d.ellipse((x-r,y-r,x+r,y+r),fill=0)
    # V155 already identified a conservative date-label exclusion around
    # the centers of each 256px original JPEG tile. Widen the vertical
    # allowance; never claim machine-certified complete watermark removal.
    for row in range(3):
        for col in range(9):
            x,y=col*256+128,row*256+128
            d.rectangle((x-55,y-58,x+55,y+25),fill=0)
    return mask

def sector_coverage(mask):
    result={}
    for i,name in enumerate(('source-west','source-center','source-east')):
        region=mask.crop((i*768,0,(i+1)*768,768))
        retained=sum(region.histogram()[1:])
        total=768*768
        ratio=retained/total
        # Both unmasked material AND real exclusions must exist in each.
        if not 0.10<ratio<0.90:
            raise ValueError('Modern exclusion leaves implausible source coverage: '+name)
        result[name]=round(ratio,6)
    return result

def expected_manifest(source,coverage):
    return {'version':156,'purpose':'Candidate modern-infrastructure exclusions on source imagery; NOT game art',
            'sourceVersion':153,'sourceMosaicSha256':source['mosaicSha256'],
            'sourceCrs':'EPSG:3857','pixelDimensions':list(SIZE),
            'requiredAttribution':ATTRIBUTION,'license':'CC BY 4.0',
            'exclusionAlphaMeaning':'0=excluded/unknown; 255=unreviewed modern source',
            'excludedSourceOnly':True,'exclusionCorridorNames':[c[0] for c in CORRIDORS],
            'watermarkCandidateCount':27,'detachedObservationCount':len(DETACHED_OBSERVATIONS),
            'sourceSectorRetainedFractions':coverage,
            'maskFile':'modern-exclusion-mask.png',
            'referenceFile':'modern-exclusion-reference.png',
            **UNAPPROVED}

def produce(source_dir,out_dir):
    source=json.loads((source_dir/'manifest.json').read_text())
    raster=verify_source(source,source_dir)
    mask=make_mask()
    coverage=sector_coverage(mask)
    out_dir.mkdir(parents=True,exist_ok=True)
    mask.save(out_dir/'modern-exclusion-mask.png',optimize=True)
    rgba=raster.convert('RGBA');rgba.putalpha(mask)
    rgba.save(out_dir/'modern-exclusion-reference.png',optimize=True)
    report=expected_manifest(source,coverage)
    report['maskSha256']=digest((out_dir/report['maskFile']).read_bytes())
    report['referenceSha256']=digest((out_dir/report['referenceFile']).read_bytes())
    (out_dir/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    verify_output(source_dir,out_dir)
    return report

def verify_output(source_dir,out_dir):
    source=json.loads((source_dir/'manifest.json').read_text())
    raster=verify_source(source,source_dir)
    mask=make_mask()
    expected=expected_manifest(source,sector_coverage(mask))
    got=json.loads((out_dir/'manifest.json').read_text())
    if set(got)!=set(expected)|{'maskSha256','referenceSha256'}:
        raise ValueError('Unexpected exclusion metadata/approval claims')
    for k,v in expected.items():
        if got.get(k)!=v:
            raise ValueError('Source, exclusion geometry, or approval status changed: '+k)
    for key,filekey in [('maskSha256','maskFile'),('referenceSha256','referenceFile')]:
        if got.get(key)!=digest((out_dir/got[filekey]).read_bytes()):
            raise ValueError('Excluded source PNG SHA256 mismatch: '+key)
    with Image.open(out_dir/got['maskFile']) as im:
        if im.format!='PNG' or im.mode!='L' or im.size!=SIZE or im.tobytes()!=mask.tobytes():
            raise ValueError('Source exclusion mask pixel mismatch')
    with Image.open(out_dir/got['referenceFile']) as im:
        if im.format!='PNG' or im.mode!='RGBA' or im.size!=SIZE:
            raise ValueError('Excluded reference format mismatch')
        actual=im.tobytes()
    expected_rgba=raster.convert('RGBA');expected_rgba.putalpha(mask)
    if actual!=expected_rgba.tobytes():
        raise ValueError('Modern source exclusion pixel mismatch')
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',default='qa/v153-geographic-strip')
    p.add_argument('--output',default='qa/v156-modern-exclusion')
    p.add_argument('--verify',action='store_true')
    a=p.parse_args()
    if a.verify:verify_output(Path(a.source),Path(a.output))
    else:produce(Path(a.source),Path(a.output))
    print('V156 PASS: three modern-source exclusion corridors, 27 candidate watermarks, 3 sector alpha checks; NOT game art')

if __name__=='__main__':main()
