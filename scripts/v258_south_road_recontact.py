#!/usr/bin/env python3
"""V258: fix SOUTH fictional source-cartway mid-bend registration (ART RED).

All coordinates below are manually sighted on an original fictional 1536x1024
image. Neither they nor V123 imply historical roads or natural geodetic ties.
No V123 graph, Matrei art, sprite, save, or campaign code is modified.
"""
import argparse, json
from pathlib import Path
import cv2
import numpy as np
from scipy.spatial import cKDTree
from v257_replacement_west import (TRACE as V257_TRACE, PINS, check_atlas,
    verify_source, target_at_source_progress, mapping, evaluate, TARGET)

# V256's SOUTH points x~570..700 were 15..35px below the actual ruts.
# Corrected by observing the ORIGINAL source pixels, not the target overlay.
SOUTH_ROAD_CENTER=[
 [449,0],[449,50],[455,100],[463,150],[478,200],[500,250],
 [535,300],[590,337],[632,353],[674,378],[705,414],[730,460],
 [775,498],[840,530],[905,558],[980,581],[1060,597],
 [1140,607],[1200,614],[1244,624]
]
TRACE={'west':V257_TRACE['west'],'south':SOUTH_ROAD_CENTER}
# Eight original-source mid-segment road centers excluded from fitting. These
# are manually sighted image-pixel holdouts, NOT independent V209 tiepoints.
SOUTH_HOLDOUT=np.asarray([
 [555,317],[610,344],[653,367],[690,392],
 [745,474],[800,515],[875,548],[950,575]],dtype=np.float64)

def _distance_to_route(pt,route):
    a=route[:-1];v=route[1:]-a
    t=np.clip(np.sum((pt-a)*v,axis=1)/np.sum(v*v,axis=1),0,1)
    return float(np.min(np.linalg.norm(pt-(a+t[:,None]*v),axis=1)))

def south_holdout_report(trace):
    """Inverse-map manually observed native pixels; compare to V123 polyline.

    This is a more independent diagnostic than training-anchor residuals, but
    still only source-pixel observations, NOT historical/geodetic verification.
    """
    dst=target_at_source_progress('south',trace)
    mx,my,_,_=mapping(trace,dst,sigma=170,spacing=1.25)
    yy,xx=np.indices(mx[::2,::2].shape)
    tree=cKDTree(np.column_stack((mx[::2,::2].ravel(),my[::2,::2].ravel())))
    source_inverse_error,indices=tree.query(SOUTH_HOLDOUT)
    mapped=np.column_stack((xx.ravel()[indices]*2,yy.ravel()[indices]*2))
    target=np.asarray(TARGET['south'],dtype=np.float64)
    distances=np.asarray([_distance_to_route(p,target) for p in mapped])
    return {'sourceHoldoutsManuallyObserved':True,
      'independentGeographicTiepointsVerified':False,
      'holdoutSourcePoints':SOUTH_HOLDOUT.astype(int).tolist(),
      'perHoldoutDistanceToV123Px':np.round(distances,2).tolist(),
      'medianPx':round(float(np.median(distances)),2),
      'p90Px':round(float(np.percentile(distances,90)),2),
      'maxPx':round(float(np.max(distances)),2),
      'maxInverseSamplingErrorPx':round(float(np.max(source_inverse_error)),2)}

def process(tile,source,atlas,out):
    check_atlas(atlas)
    im=verify_source(tile,source)
    dst=target_at_source_progress(tile,TRACE[tile])
    mx,my,_,_=mapping(TRACE[tile],dst,sigma=170,spacing=1.25)
    qa=evaluate(mx,my,TRACE[tile],dst)
    result=cv2.remap(im,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    cv2.imwrite(str(out/(tile+'-v258-UNAPPROVED.webp')),result,[cv2.IMWRITE_WEBP_QUALITY,92])
    review=result.copy()
    cv2.polylines(review,[np.rint(np.asarray(dst)).astype(np.int32)],False,(0,0,255),2,cv2.LINE_AA)
    cv2.imwrite(str(out/(tile+'-v258-road-review.jpg')),review,[cv2.IMWRITE_JPEG_QUALITY,94])
    qa.update({'sourceSha256':PINS[tile],'sourceNativeSize':[1536,1024],
      'sourceRoadTraceManuallyObserved':True,
      'independentGeographicTiepointsVerified':False,'historicalRoadVerified':False,
      'bridgeBanksVerified':False,'strictV203Passed':False,'fourBrowserArtPassed':False,
      'userVisualApproval':False,'productionApproved':False})
    if tile=='south':qa['sourcePixelHoldout']=south_holdout_report(TRACE['south'])
    return qa

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--west',required=True);p.add_argument('--south',required=True)
    p.add_argument('--atlas',default='terrain-grid/v123-atlas.js')
    p.add_argument('--out',required=True)
    a=p.parse_args();result={'version':258,'tiles':{}}
    for tile in ('west','south'):
        result['tiles'][tile]=process(tile,getattr(a,tile),a.atlas,a.out)
    result['necessaryGeometryPass']=all(
      x.get('necessaryGeometryPass',x.get('geometryPass',False)) for x in result['tiles'].values())
    result['productionApproved']=False
    Path(a.out,'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
