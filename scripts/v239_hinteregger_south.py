#!/usr/bin/env python3
"""V239: inspect a NEW, license-attributed oblique SOUTH photo; no art promotion.

The photographed 2025 Hinteregger Alm is NOT registered to V123, and modern
tracks, structures, trees and landforms cannot verify 1780 cartways. Never
replace a failed source with painted strips or modify immutable road geometry.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import time
import requests
from PIL import Image
import v237_build_photo_grounded as v237
import v238_bake_native_cartways as v238

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v239-hinteregger-south'
SOURCE={
 'filename':'Aerial image of Hinteregger Alm (view from the southeast).jpg',
 'author':'Carsten Steger',
 'date':'2025-09-21',
 'page':'https://commons.wikimedia.org/wiki/File:Aerial_image_of_Hinteregger_Alm_(view_from_the_southeast).jpg',
 'license':'CC BY-SA 4.0',
 'licenseUrl':'https://creativecommons.org/licenses/by-sa/4.0/',
 'dimensions':[5700,3700],
 'sha1':None, # MUST be pinned after first original-source inspection.
 'place':'Hinteregger Alm, Styria, Austria; NOT Matrei or Brenner registration',
}
FLAGS={**v238.FALSE,'licenseVerified':False,'sourceRegisteredToV123':False,
       'historicalRoadsVerified':False,'bridgeBanksVerified':False,
       'humanVisualApproval':False,'productionApproved':False}

def source_url():
    return v238.commons_original_url(SOURCE['filename'])

def inspect_bytes(raw, expected_sha1=None):
    sha1=hashlib.sha1(raw).hexdigest()
    with Image.open(io.BytesIO(raw)) as im:
        if list(im.size)!=SOURCE['dimensions']:
            raise ValueError('STOP: original SOUTH dimensions mismatch')
        photo=im.convert('RGB')
    if expected_sha1 is not None and sha1!=expected_sha1:
        raise ValueError('STOP: original SOUTH SHA1 changed')
    return photo,sha1

def fetch_original():
    last=None
    for pause in (0,8):
        if pause:time.sleep(pause)
        response=requests.get(source_url(),timeout=120,headers={
          'User-Agent':'CenturyOfEmpires/0.3 (CC BY-SA 4.0 research; issue 9)'})
        last=response
        if response.status_code not in (429,503):break
    last.raise_for_status()
    return inspect_bytes(last.content,SOURCE['sha1'])

def evaluate(photo):
    roads=v238.verify_graph()
    crop,box,ranking=v237.candidate_crop(photo,roads['south'])
    baked,ground,metrics,open_fraction,ground_ok=v238.bake_scene(
        crop,roads['south'],'south')
    # Ground-color heuristics are NECESSARY ONLY. Never auto-promote an image.
    return {'crop':crop,'baked':baked,'ground':ground,
            'nativeCrop':box,'rank':list(ranking),
            'metrics':metrics,'openFraction':open_fraction,
            'necessaryGround':bool(ground_ok)}

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    roads=v238.verify_graph()
    assert roads['south'][0]==[466,0] and roads['south'][-1]==[1270,605]
    photo,sha1=fetch_original()
    e=evaluate(photo)
    e['crop'].save(OUT/'south-original-native-crop.jpg',quality=91)
    e['ground'].save(OUT/'south-original-ground-review.jpg',quality=91)
    e['baked'].save(OUT/'south-cartway-DIAGNOSTIC-ONLY.jpg',quality=91)
    report={'version':239,'source':{**SOURCE,'sha1Observed':sha1,
             'sha1PinnedAndVerified':SOURCE['sha1'] is not None,
             'originalUrl':source_url()},
       'nativeCrop':e['nativeCrop'],'rank':e['rank'],
       'ground':e['metrics'],'bakedCorridorOpenColor':e['openFraction'],
       'necessaryGroundOnly':e['necessaryGround'],
       'historicalSourceTiepoints':'UNVERIFIED',
       'noPreviewPromoted':True,'reason':'Human physical-cartway and 2025-modern-feature review required',
       **FLAGS}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\\n')
    print(json.dumps({'sha1':sha1,'nativeCrop':e['nativeCrop'],
          'necessaryGroundOnly':e['necessaryGround'],
          'ground':e['metrics'],'approval':'RED'},indent=2))
    return report

if __name__=='__main__':
    build()
