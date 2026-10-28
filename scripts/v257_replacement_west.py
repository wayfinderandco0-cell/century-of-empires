#!/usr/bin/env python3
"""V257: new original WEST physical-cartway source, not verified historic geography.

Native road traces are manually observed fictional-image pixels, NOT independent
V209 geodesy. This study never changes immutable V123 or promotes production.
"""
from pathlib import Path
import argparse, hashlib, json
import cv2, numpy as np
from v255_anchored_cartway import NATIVE,V123_SHA,TARGET,mapping,evaluate
from v256_real_cartway import TRACE as OLD_TRACE,target_at_source_progress

WEST_SOURCE_SHA='2f7b6171c8fa479a61d372a7027e98aa0296ece92e38fc8908bbf65c4d7300fa'
SOUTH_SOURCE_SHA='034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3'
# WEST has an existing small stone bridge over a tributary near x1190.
# This does not independently validate V123 bridge topology or both bank routes.
TRACE={
 'west':[[275,432],[320,412],[370,399],[430,395],[500,405],[570,424],
         [640,433],[700,431],[784,422],[850,416],[920,401],[980,388],
         [1050,378],[1120,367],[1210,355],[1320,353],[1450,354],[1535,356]],
 'south':OLD_TRACE['south'],
}
PINS={'west':WEST_SOURCE_SHA,'south':SOUTH_SOURCE_SHA}

def verify_source(tile,path):
 data=Path(path).read_bytes()
 if hashlib.sha256(data).hexdigest()!=PINS[tile]:raise ValueError('source SHA256 mismatch')
 im=cv2.imread(str(path),cv2.IMREAD_COLOR)
 if im is None or im.shape[:2]!=NATIVE:raise ValueError('source dimensions mismatch')
 return im

def check_atlas(path):
 data=Path(path).read_bytes()
 sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if sha!=V123_SHA:raise ValueError('immutable V123 atlas SHA changed')

def build(tile,source,atlas,out):
 check_atlas(atlas);im=verify_source(tile,source)
 dst=target_at_source_progress(tile,TRACE[tile])
 mx,my,_,_=mapping(TRACE[tile],dst,sigma=170,spacing=1.25)
 qa=evaluate(mx,my,TRACE[tile],dst)
 result=cv2.remap(im,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 cv2.imwrite(str(out/(tile+'-v257-UNAPPROVED.webp')),result,[cv2.IMWRITE_WEBP_QUALITY,92])
 review=result.copy()
 cv2.polylines(review,[np.rint(np.asarray(dst)).astype(np.int32)],False,(0,0,255),3,cv2.LINE_AA)
 cv2.imwrite(str(out/(tile+'-v257-road-review.jpg')),review,[cv2.IMWRITE_JPEG_QUALITY,94])
 qa.update({'sourceSha256':PINS[tile],'sourceNativeSize':list(NATIVE[::-1]),
            'independentGeographicTiepointsVerified':False,'historicalRoadVerified':False,
            'bridgeBanksVerified':False,'strictV203Passed':False,'fourBrowserArtPassed':False,
            'userVisualApproval':False,'productionApproved':False})
 return qa

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--west',required=True);p.add_argument('--south',required=True)
 p.add_argument('--atlas',default='terrain-grid/v123-atlas.js');p.add_argument('--out',required=True)
 a=p.parse_args();r={'version':257,'tiles':{}}
 for tile in ('west','south'):r['tiles'][tile]=build(tile,getattr(a,tile),a.atlas,a.out)
 r['allNecessaryGeometryPass']=all(x['necessaryGeometryPass'] for x in r['tiles'].values())
 r['productionApproved']=False
 Path(a.out,'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
