#!/usr/bin/env python3
"""V256: denser visually traced fictional source road, arc-registered to immutable V123.

Visual source coordinates are hand-annotated from *original* image pixels. They
are not verified historical road coordinates or geographic tiepoints. This tool
never modifies the V123 graph and never promotes artwork to production.
"""
from pathlib import Path
import sys, hashlib, json
import numpy as np, cv2
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v255_anchored_cartway import NATIVE,PINS,V123_SHA,TARGET,mapping,evaluate

TRACE={
'west':[[275,427],[320,419],[370,414],[430,417],[500,417],[570,412],[640,406],[700,402],[784,391],[850,386],[920,382],[980,379],[1050,376],[1120,370],[1210,365],[1320,359],[1450,350],[1535,341]],
'south':[[449,0],[448,50],[452,100],[462,150],[479,200],[495,250],[521,300],[571,350],[626,384],[672,410],[692,427],[727,457],[776,499],[838,535],[905,559],[980,580],[1060,598],[1140,611],[1200,618],[1244,624]],
}

def arc_positions(points):
    p=np.asarray(points,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=2 or len(p)<3 or not np.isfinite(p).all():raise ValueError('invalid trace')
    step=np.linalg.norm(np.diff(p,axis=0),axis=1)
    if np.any(step<2):raise ValueError('degenerate trace')
    arc=np.r_[0,np.cumsum(step)]
    return arc/arc[-1]

def target_at_source_progress(tile,src=None):
    """Reparameterize fixed V123 geometry at measured source trace arc fractions."""
    src=TRACE[tile] if src is None else src
    trg=np.asarray(TARGET[tile],dtype=np.float64)
    trgt=arc_positions(trg)
    src_t=arc_positions(src)
    dst=np.column_stack([np.interp(src_t,trgt,trg[:,axis]) for axis in (0,1)])
    dst[0]=trg[0];dst[-1]=trg[-1]
    return dst.tolist()

def contact_score(src_image,warped,source_trace,target_trace,halfwidth=8):
    """Diagnostic only: grass/stone can share dirt colors; not a road accuracy test."""
    def scores(im,trace):
        hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        pts=np.asarray(trace,dtype=np.float32)
        d=np.linalg.norm(np.diff(pts,axis=0),axis=1)
        arc=np.r_[0,np.cumsum(d)];ss=np.linspace(0,arc[-1],300)
        xx=np.interp(ss,arc,pts[:,0]);yy=np.interp(ss,arc,pts[:,1])
        good=[]
        for x,y in zip(xx,yy):
            i=int(round(x));j=int(round(y))
            if i<12 or i>=im.shape[1]-12 or j<12 or j>=im.shape[0]-12:continue
            patch=hsv[j-5:j+6,i-5:i+6]
            good.append(float(np.mean((patch[:,:,2]>65)&(patch[:,:,1]<185))))
        return float(np.mean(good)) if good else 0.
    return {'sourceDirtLikeFraction':round(scores(src_image,source_trace),3),'warpedDirtLikeFraction':round(scores(warped,target_trace),3)}

def process(tile,source,atlas,out):
    raw=Path(atlas).read_bytes();sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if sha!=V123_SHA:raise ValueError('immutable V123 changed')
    data=Path(source).read_bytes()
    if hashlib.sha256(data).hexdigest()!=PINS[tile]:raise ValueError('wrong original image SHA256')
    image=cv2.imread(str(source));assert image is not None and image.shape[:2]==NATIVE
    dst=target_at_source_progress(tile)
    mx,my,_,_=mapping(TRACE[tile],dst,sigma=170,spacing=1.25)
    qa=evaluate(mx,my,TRACE[tile],dst)
    warped=cv2.remap(image,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    qa.update(contact_score(image,warped,TRACE[tile],dst))
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    cv2.imwrite(str(out/(tile+'-v256-fictional-UNAPPROVED.webp')),warped,[cv2.IMWRITE_WEBP_QUALITY,92])
    review=warped.copy()
    cv2.polylines(review,[np.rint(np.asarray(dst)).astype(np.int32)],False,(0,220,0),2,cv2.LINE_AA)
    cv2.polylines(review,[np.asarray(TARGET[tile],np.int32)],False,(0,0,255),2,cv2.LINE_AA)
    cv2.imwrite(str(out/(tile+'-v256-road-contact-UNAPPROVED.jpg')),review,[cv2.IMWRITE_JPEG_QUALITY,94])
    qa.update({'tile':tile,'sourceSha256':PINS[tile],'nativeRoadTraceManuallyObserved':True,'sourceTrace':TRACE[tile],'dirtLikeProxyIsAcceptanceEvidence':False,'naturalTiepointsVerified':False,'historicRoadVerified':False,'bridgeBanksVerified':False,'strictV203Passed':False,'fourBrowserArtPassed':False,'humanArtApproved':False,'productionApproved':False})
    return qa

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--west',required=True);p.add_argument('--south',required=True);p.add_argument('--atlas',default='terrain-grid/v123-atlas.js');p.add_argument('--out',required=True);args=p.parse_args()
 result={'version':256,'tiles':{}}
 for tile in ('west','south'):result['tiles'][tile]=process(tile,getattr(args,tile),args.atlas,args.out)
 result['allNecessaryGeometryPass']=all(q['necessaryGeometryPass'] for q in result['tiles'].values())
 result['productionApproved']=False
 Path(args.out,'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
