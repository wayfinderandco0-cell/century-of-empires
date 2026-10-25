#!/usr/bin/env python3
"""V182: remove image-verified 2023 imprints from Matrei SOURCE, never GAME art."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
import v181_matrei_exclusions as prior

SIZE = prior.SIZE
STAMP_CENTERS = ((0,96),(320,96),(640,96),(1280,96),
                 (0,416),(320,416),(640,416))
HALF_WIDTH, HALF_HEIGHT = 23, 13
FALSE_FLAGS = prior.FALSE_FLAGS

def require(ok, why):
    if not ok:
        raise ValueError(why)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def stamp_mask():
    mask = Image.new('L', SIZE, 0)
    draw = ImageDraw.Draw(mask)
    for x,y in STAMP_CENTERS:
        require(0 <= x < SIZE[0] and 0 <= y < SIZE[1], 'invalid stamp point')
        draw.rectangle((max(0,x-HALF_WIDTH),y-HALF_HEIGHT,
                        min(SIZE[0]-1,x+HALF_WIDTH),y+HALF_HEIGHT),fill=255)
    return mask

def read_verified(source_dir, previous_dir):
    source_dir,previous_dir=Path(source_dir),Path(previous_dir)
    require(prior.verify(source_dir,previous_dir),'V181 source not verified')
    manifest=json.loads((previous_dir/'manifest.json').read_text())
    with Image.open(previous_dir/'matrei-modern-excluded-SOURCE.png') as im:
        require(im.mode=='RGBA' and im.size==SIZE,'invalid V181 output')
        image=im.copy()
    return manifest,image

def expected(image):
    mask=stamp_mask()
    pixels=image.load()
    marks=mask.load()
    result=Image.new('RGBA',SIZE,(0,0,0,0))
    out=result.load()
    newly_excluded=0
    for y in range(SIZE[1]):
        for x in range(SIZE[0]):
            p=pixels[x,y]
            if p[3] and marks[x,y]:
                newly_excluded+=1
            elif p[3]:
                out[x,y]=p
    return result,mask,newly_excluded

def build(source_dir,previous_dir,output_dir):
    old,image=read_verified(source_dir,previous_dir)
    result,mask,newly_excluded=expected(image)
    require(0<newly_excluded<10000,'date-stamp exclusion unexpectedly broad')
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    result.save(output_dir/'matrei-no-date-imprints-SOURCE.png',optimize=True)
    mask.save(output_dir/'matrei-date-imprint-mask.png',optimize=True)
    report={
        'version':182,
        'purpose':'Source-only exclusion of image-verified modern 2023 date stamps',
        'sourceV180Sha256':old['sourceMosaicSha256'],
        'parentV181ManifestSha256':sha(Path(previous_dir)/'manifest.json'),
        'parentV181ExcludedImageSha256':old['excludedOutputSha256'],
        'reviewedDateText':'2023',
        'reviewedStampCentersPixels':[list(x) for x in STAMP_CENTERS],
        'stampHalfWidthHeightPixels':[HALF_WIDTH,HALF_HEIGHT],
        'annotationMethod':'manual image review of real V180 source artifact 12593190495',
        'sourceAttribution':old['sourceAttribution'],
        'sourceLicense':old['sourceLicense'],
        'newlyExcludedObservedPixels':newly_excluded,
        'remainingBuiltEnvironmentUnreviewed':True,
        'transparencyHolesAreUnresolved':True,
        'doesNotReconstructHistoricalTerrain':True,
        'outputSha256':sha(output_dir/'matrei-no-date-imprints-SOURCE.png'),
        'maskSha256':sha(output_dir/'matrei-date-imprint-mask.png'),
        **{k:False for k in FALSE_FLAGS},
    }
    (output_dir/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    verify(source_dir,previous_dir,output_dir)
    return report

def verify(source_dir,previous_dir,output_dir):
    old,image=read_verified(source_dir,previous_dir)
    output_dir=Path(output_dir)
    report=json.loads((output_dir/'manifest.json').read_text())
    require(report.get('version')==182 and
            report.get('sourceV180Sha256')==old['sourceMosaicSha256'] and
            report.get('parentV181ManifestSha256')==sha(Path(previous_dir)/'manifest.json') and
            report.get('parentV181ExcludedImageSha256')==old['excludedOutputSha256'] and
            report.get('reviewedDateText')=='2023' and
            report.get('reviewedStampCentersPixels')==[list(x) for x in STAMP_CENTERS] and
            report.get('stampHalfWidthHeightPixels')==[HALF_WIDTH,HALF_HEIGHT] and
            report.get('sourceAttribution')==old['sourceAttribution'] and
            report.get('sourceLicense')==old['sourceLicense'] and
            report.get('remainingBuiltEnvironmentUnreviewed') is True and
            report.get('transparencyHolesAreUnresolved') is True and
            report.get('doesNotReconstructHistoricalTerrain') is True and
            all(report.get(k) is False for k in FALSE_FLAGS),
            'source/date provenance or GAME approval forged')
    result,mask,n=expected(image)
    require(n==report.get('newlyExcludedObservedPixels') and 0<n<10000,
            'incorrect exclusion count')
    require(sha(output_dir/'matrei-no-date-imprints-SOURCE.png')==report.get('outputSha256') and
            sha(output_dir/'matrei-date-imprint-mask.png')==report.get('maskSha256'),
            'image hashes changed')
    with Image.open(output_dir/'matrei-no-date-imprints-SOURCE.png') as actual:
        require(actual.mode=='RGBA' and actual.size==SIZE and
                actual.tobytes()==result.tobytes(),'SOURCE output pixels tampered')
    with Image.open(output_dir/'matrei-date-imprint-mask.png') as actual:
        require(actual.mode=='L' and actual.size==SIZE and
                actual.tobytes()==mask.tobytes(),'stamp mask pixels tampered')
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',default='qa/v180-matrei-source')
    p.add_argument('--previous',default='qa/v181-matrei-exclusions')
    p.add_argument('--output',default='qa/v182-matrei-imprints')
    p.add_argument('--verify',action='store_true')
    args=p.parse_args()
    if args.verify:
        verify(args.source,args.previous,args.output)
    else:
        build(args.source,args.previous,args.output)
    print('V182 verified SOURCE-only 2023 date imprint exclusion; GAME art unapproved')

if __name__=='__main__':
    main()
