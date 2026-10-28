#!/usr/bin/env python3
"""V261: exact fictional-art V249 browser screenshots -> unchanged strict V203. ART RED."""
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image
from qa_v203_canopy_structure import audit, ENGINES, ORIENTATIONS, REGIONS

EXPECTED = {
 'west':'36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7',
 'south':'d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb'
}

def verify_sources(west,south,expected=EXPECTED):
    hashes={}
    for tile,path in [('west',west),('south',south)]:
        if not path.is_file():raise FileNotFoundError(f'Missing exact {tile}: {path}')
        hashes[tile]=hashlib.sha256(path.read_bytes()).hexdigest()
        if hashes[tile]!=expected[tile]:raise ValueError(f'{tile} source SHA mismatch')
        with Image.open(path) as im:
            if im.size!=(1536,1024):raise ValueError(f'{tile} source size mismatch')
    if hashes['west']==hashes['south']:raise ValueError('Duplicate artwork')
    return hashes

def assess_captures(captures,out,hashes=None):
    staged=out/'v203-input';staged.mkdir(parents=True,exist_ok=True)
    missing=[]
    for engine in ENGINES:
        for orient in ORIENTATIONS:
            for tile in REGIONS:
                name=f'{engine}-{orient}-{tile}-RAW-UNAPPROVED.png'
                src=captures/name
                if not src.is_file():missing.append(name);continue
                with Image.open(src) as im:im.verify()
                shutil.copyfile(src,staged/f'{engine}-{orient}-{tile}-close.png')
    strict=audit(staged,out/'strict-v203',make_contact=True)
    assert not (missing and strict['passed']), 'Missing captures must fail V203'
    result={'version':261,'exactV260SourceSHA256':hashes,
       'allTwelveRawScreenshotsPresent':not missing,'missingRawScreenshots':missing,
       'strictV203':strict,'strictV203Passed':strict['passed'],
       'historicalRoadVerified':False,'independentGeographicTiepointsVerified':False,
       'bridgeBanksVerified':False,'physicalIPhoneApproved':False,
       'humanVisualApproval':False,'productionApproved':False}
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--west',type=Path);p.add_argument('--south',type=Path)
    p.add_argument('--screenshots',type=Path,help='Reaudit old captures; NO browser run')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--engines',default='chromium,webkit')
    p.add_argument('--chromium-executable')
    a=p.parse_args()
    if a.screenshots:
        if a.west or a.south:raise ValueError('Old screenshot mode cannot claim V260 hashes')
        result=assess_captures(a.screenshots,a.out)
        result['browserExecutionThisRun']=False
    else:
        if not a.west or not a.south:p.error('Both exact V260 sources required')
        hashes=verify_sources(a.west,a.south)
        from qa_v259_offline_real_renderer import run
        functional=run(a.root,a.west,a.south,a.out/'actual-renderer',
                       tuple(a.engines.split(',')),a.chromium_executable)
        result=assess_captures(a.out/'actual-renderer',a.out,hashes)
        result['browserExecutionThisRun']=True
        result['fourBrowserTechnicalPass']=bool(functional['fourBrowserTechnicalPass'])
        result['exactArtFourBrowserNecessaryPass']=bool(functional['fourBrowserTechnicalPass'] and result['strictV203Passed'])
    (a.out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'strictV203Passed':result['strictV203Passed'],
      'missingRawScreenshots':result['missingRawScreenshots'],
      'browserExecutionThisRun':result['browserExecutionThisRun'],
      'productionApproved':False},indent=2))
if __name__=='__main__':main()
