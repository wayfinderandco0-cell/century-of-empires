#!/usr/bin/env python3
"""V220 opt-in TWO WHOLE native orthophoto cell alternatives (NOT historical/game registration).
48 distinct modern basemap.at 256px JPEGs form two internally contiguous 1536x1024
native-pixel mosaics. Only the V218 visually reviewed 512px origin masks are
quarantined. Other modern features remain UNREVIEWED and therefore unapproved.
No pixel resampling, procedural noise, inpainting, false cartways or Matrei edits.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageChops
import v217_matrei_nearby_native_scout as scout
import v218_reviewed_modern_quarantine as quarantine

W,H,TILE=1536,1024,256
SITES=(('west',5),('south',8))
FLAGS=('sourceRegisteredToV123','historicRoadsVerified','allModernFeaturesExcluded',
       'periodSafe','gameArtApproved','physicalIPhoneApproved','productionApproved')
ROOT=Path(__file__).resolve().parents[1]

def require(ok, why):
    if not ok: raise ValueError('V220 fail-closed: '+why)

def sha(data): return hashlib.sha256(data).hexdigest()

def plan():
    base=scout.plan()['sites']
    cells=[]
    all_xyz=set()
    for cell,idx in SITES:
        x0,y0,z=base[idx]['nativeOriginXYZ']
        tiles=[]
        for row in range(4):
            for col in range(6):
                x,y=x0+col,y0+row
                require((x,y,z) not in all_xyz,'repeated source tile')
                all_xyz.add((x,y,z))
                tiles.append({'xyz':[x,y,z],'row':row,'col':col,
                    'name':f'{cell}-r{row}c{col}.jpeg',
                    'url':f'{scout.v204.BASE}/{z}/{y}/{x}.jpeg'})
        cells.append({'cell':cell,'reviewedV218Site':idx,'originXYZ':[x0,y0,z],
            'footprintLonLat':[scout.v204.footprint(x0,y0)[0],
                scout.v204.footprint(x0+5,y0+3)[1],
                scout.v204.footprint(x0+5,y0+3)[2],
                scout.v204.footprint(x0,y0)[3]],
            'file':f'{cell}-full-native-2023.webp','tiles':tiles,
            'nativePixels':[W,H],'reviewedMaskOnlyAtOrigin512':True,
            'artisticPlacementNotGeoregistration':True})
    return {'version':220,'kind':'OPT_IN_CONTIGUOUS_MODERN_ORTHOPHOTO_ART_STUDY',
        'attribution':'Datenquelle: basemap.at | CC BY 4.0',
        'sourceUrl':'https://basemap.at/orthofoto/',
        'sourceYear':2023,'projection':'EPSG:3857',
        'nativeTilePixels':TILE,'nativeCellPixels':[W,H],
        'contiguousWithinEachSourceCell':True,'contiguousBetweenGameCells':False,
        'sourceAreasNotGameGeography':True,'sourceModernRoadsMayRemain':True,
        'unreviewedModernFeaturesMayRemain':True,'sourceQuarantineStillUnknown':True,
        'noUpscaling':True,'noDuplicatedSourceTiles':True,
        'centerMatreiArtworkUnchanged':True,'roadGraphUnchanged':True,
        'cells':cells,**{f:False for f in FLAGS}}

def assert_plan(m):
    expected=plan()
    require(set(m)==set(expected),'unexpected manifest keys')
    for k in expected:
        if k!='cells': require(m[k]==expected[k], 'manifest flag/identity changed '+k)
    require(len(m['cells'])==2,'two cells required')
    for actual,pinned in zip(m['cells'],expected['cells']):
        require(set(actual) in (set(pinned),set(pinned)|{'sha256','maskZeroPixels'}),'cell fields changed')
        for k in pinned:
            if k!='tiles': require(actual[k]==pinned[k],'source cell changed '+k)
        require(len(actual['tiles'])==24,'24 native JPEGs per cell')
        for got,ref in zip(actual['tiles'],pinned['tiles']):
            require(set(got) in (set(ref),set(ref)|{'sha256','byteCount'}),'tile fields changed')
            for k in ref: require(got[k]==ref[k],'XYZ tile identity changed')
    return True

def source_image(cell,folder):
    rgb=Image.new('RGB',(W,H))
    for tile in cell['tiles']:
        data=(folder/tile['name']).read_bytes()
        require(sha(data)==tile['sha256'] and len(data)==tile['byteCount'],
                'source JPEG checksum changed')
        scout.native_jpeg(data)
        with Image.open(io.BytesIO(data)) as im:
            rgb.paste(im.convert('RGB'),(tile['col']*TILE,tile['row']*TILE))
    return rgb

def expected_alpha(cell,quarantine_folder):
    m=json.loads((quarantine_folder/'manifest.json').read_text())
    quarantine.verify_plan(m)
    reviewed=next(s for s in m['sites'] if s['siteIndex']==cell['reviewedV218Site'])
    # Exact first four 256px JPEGs must be identical to audited V218 source.
    source={(t['xyz'][0],t['xyz'][1],t['xyz'][2]):t for t in reviewed['sourceTiles']}
    for t in cell['tiles']:
        key=tuple(t['xyz'])
        if key in source:
            require(t['sha256']==source[key]['sha256'],
                    'V218 reviewed source tile has changed')
    with Image.open(quarantine_folder/reviewed['maskFile']) as im:
        mask=im.convert('L')
    require(mask.size==(512,512),'reviewed mask dimensions')
    alpha=Image.new('L',(W,H),255)
    alpha.paste(mask,(0,0))
    return alpha

def assemble(cell,folder,quarantine_folder):
    rgb=source_image(cell,folder)
    alpha=expected_alpha(cell,quarantine_folder)
    rgba=rgb.convert('RGBA')
    rgba.putalpha(alpha)
    return rgba

def acquire_native_tiles(cell,folder):
    """Reuse exact native JPEGs from the pinned prior Actions artifact if valid.
    This is a resumable SOURCE cache, not permission to fabricate missing pixels.
    Every JPEG is decoded/size-checked and its byte SHA pinned in the manifest.
    """
    for tile in cell['tiles']:
        path=folder/tile['name']
        if path.is_file():
            raw=path.read_bytes()
            try:
                scout.native_jpeg(raw)
            except (ValueError, OSError, SyntaxError):
                path.unlink()
            else:
                tile['sha256']=sha(raw)
                tile['byteCount']=len(raw)
                continue
        print('V220 missing original native tile: '+tile['name']+
              ' XYZ='+str(tile['xyz']),flush=True)
        scout.download(folder,{'sites':[{'tiles':[tile]}]})

def build(folder,quarantine_folder):
    scout.v204.verify_source_invariants('matrei')
    quarantine.verify(quarantine_folder)
    folder.mkdir(parents=True,exist_ok=True)
    m=plan()
    for cell in m['cells']:
        acquire_native_tiles(cell,folder)
        image=assemble(cell,folder,quarantine_folder)
        cell['maskZeroPixels']=sum(1 for a in image.getchannel('A').getdata() if a==0)
        require(cell['maskZeroPixels']>0,'reviewed exclusions missing')
        image.save(folder/cell['file'],format='WEBP',lossless=True,method=6)
        cell['sha256']=sha((folder/cell['file']).read_bytes())
    (folder/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    verify(folder,quarantine_folder)
    return m

def verify(folder,quarantine_folder):
    m=json.loads((folder/'manifest.json').read_text())
    assert_plan(m)
    quarantine.verify(quarantine_folder)
    for cell in m['cells']:
        expected=assemble(cell,folder,quarantine_folder)
        path=folder/cell['file']
        require(sha(path.read_bytes())==cell['sha256'],'mosaic bytes changed')
        with Image.open(path) as im:
            require(im.size==(W,H),'mosaic not native 1536x1024')
            actual=im.convert('RGBA')
        require(ImageChops.difference(actual.convert('RGB'),expected.convert('RGB')).getbbox() is None and
                ImageChops.difference(actual.getchannel('A'),expected.getchannel('A')).getbbox() is None,
                'mosaic RGB/alpha changed, source tampered or resampled')
        require(cell['maskZeroPixels']==sum(1 for a in expected.getchannel('A').getdata() if a==0),
                'quarantine mask coverage changed')
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,default=ROOT/'qa/v218-modern-quarantine')
    p.add_argument('--output',type=Path,default=ROOT/'terrain-v220/assets')
    p.add_argument('--verify',action='store_true')
    a=p.parse_args()
    result=verify(a.output,a.source) if a.verify else build(a.output,a.source)
    print(json.dumps({'verified':bool(result),'modernSourceOnly':True,
        'georegistration':False,'productionApproved':False}))

if __name__=='__main__': main()
