#!/usr/bin/env python3
"""V252: lower-strain SOUTH physical-road source study, NEVER approved game art.

The road is an EXISTING image feature, not a painted route. The manually estimated
source trace and its extra visible continuation are not independent evidence of
historic roads or V123 geographic tiepoints. WEST and production remain blocked.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial import cKDTree

from v251_fictional_cartway_pair import SOUTH, PINNED_V123_BLOB, require_immutable_atlas, arc_sample

SOURCE_SHA256 = '3f2be77f71c05923b10bea8e8dd9c5f9ea7de51aa55842cedc2d6872b4ebceb2'
# Visual estimates on an ORIGINAL fictional source, not independent road evidence.
SOURCE_ROAD = [[452,0],[451,75],[452,160],[475,230],[528,300],[600,360],
               [700,420],[805,480],[920,540],[1040,580],[1160,602],[1270,613]]
# Physical source road continues beyond the immutable V123 endpoint: REJECT.
SOURCE_UNSUPPORTED_CONTINUATION = [[1270,613],[1350,619],[1420,625]]
TARGET_ROAD = SOUTH


def require_source(path):
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError('Original fictional SOUTH source SHA256 mismatch; reject')
    image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if image is None or image.shape[:2] != (1024,1536):
        raise ValueError('SOUTH source dimensions/decode mismatch; reject')
    return image


def continuation_length():
    p = np.asarray(SOURCE_UNSUPPORTED_CONTINUATION, dtype=float)
    return float(np.linalg.norm(np.diff(p,axis=0),axis=1).sum())


def remap_native_road(image, source=SOURCE_ROAD, target=TARGET_ROAD, sigma=180):
    if image.shape[:2] != (1024,1536) or not (100 <= sigma <= 250):
        raise ValueError('Unsupported native size or deformation radius')
    a, la = arc_sample(source, 2048)
    b, lb = arc_sample(target, 2048)
    shift = a - b
    maximum = float(np.linalg.norm(shift, axis=1).max())
    if maximum > 40:
        raise ValueError(f'Low-strain limit 40px exceeded: {maximum:.2f}px')
    h,w = image.shape[:2]
    yy,xx = np.indices((h,w),dtype=np.float32)
    pixels = np.column_stack((xx.ravel(),yy.ravel()))
    distance,nearest = cKDTree(b).query(pixels,k=1,workers=-1)
    weight = np.exp(-0.5*(distance/sigma)**2).astype(np.float32)
    # Preserve the inverse correspondence at the centerline: do NOT blur the
    # 2D displacement field as V251 did; it shifts road pixels off the route.
    mapx = xx + (shift[nearest,0]*weight).reshape(h,w).astype(np.float32)
    mapy = yy + (shift[nearest,1]*weight).reshape(h,w).astype(np.float32)
    result = cv2.remap(image,mapx,mapy,cv2.INTER_CUBIC,
                       borderMode=cv2.BORDER_REFLECT_101)
    step=8
    gx=np.gradient(mapx[::step,::step],step)
    gy=np.gradient(mapy[::step,::step],step)
    jac=gx[1]*gy[0]-gx[0]*gy[1]
    coverage=float(np.mean((mapx>=0)&(mapx<w)&(mapy>=0)&(mapy<h)))
    # Mathematically measured mapping of the MANUALLY ANNOTATED line only;
    # this is not proof the source's actual road pixels were traced correctly.
    samplex=cv2.remap(mapx,b[:,0].astype(np.float32).reshape(1,-1),
                      b[:,1].astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0]
    sampley=cv2.remap(mapy,b[:,0].astype(np.float32).reshape(1,-1),
                      b[:,1].astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0]
    residual=np.hypot(samplex-a[:,0],sampley-a[:,1])
    qa={
        'maxSourceToTargetDisplacementPx':round(maximum,3),
        'minSampledJacobian':round(float(jac.min()),4),
        'foldedSampleFraction':round(float(np.mean(jac<=0)),6),
        'observedPixelCoverage':round(coverage,6),
        'arcLengthStretchFraction':round(abs(lb/la-1),5),
        'annotatedLineMedianResidualPx':round(float(np.median(residual)),3),
        'annotatedLineP95ResidualPx':round(float(np.percentile(residual,95)),3),
        'unsupportedVisibleRoadContinuationPx':round(continuation_length(),2),
        'necessaryLowStrainGeometryPass':bool(maximum<=40 and jac.min()>=0.80
            and coverage>=0.997 and abs(lb/la-1)<=0.03 and np.percentile(residual,95)<=1),
        'independentSourceTraceVerified':False,
        'sourceGameNaturalTiepointsVerified':False,
        'historical1780CartwayVerified':False,
        'bridgeBanksVerified':False,
        'strictV203FourBrowserArtPass':False,
        'humanArtApproved':False,
        'productionApproved':False,
    }
    return result,qa


def run(source_path,output_dir,atlas_path):
    require_immutable_atlas(atlas_path)
    original=require_source(source_path)
    candidate,qa=remap_native_road(original)
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    cv2.imwrite(str(out/'south-v252-UNAPPROVED.jpg'),candidate,
                [cv2.IMWRITE_JPEG_QUALITY,94])
    overlay=candidate.copy()
    cv2.polylines(overlay,[np.asarray(TARGET_ROAD,dtype=np.int32)],False,
                  (25,35,245),2,cv2.LINE_AA)
    cv2.imwrite(str(out/'south-v252-route-overlay-UNAPPROVED.jpg'),overlay,
                [cv2.IMWRITE_JPEG_QUALITY,94])
    report={
      'version':252,'kind':'FICTIONAL_SOUTH_SOURCE_ART_STUDY_UNAPPROVED',
      'sourceSha256':SOURCE_SHA256,'immutableV123Blob':PINNED_V123_BLOB,
      'sourceAttribution':'Original AI-generated fictional Alpine image; NOT geographic evidence',
      'sourceRoadTraceMethod':'VISUAL_ESTIMATE_UNVERIFIED',
      'westStatus':'REJECTED_V251_161_98PX_WARP_AND_NO_SOURCE_PROOF',
      'southStatus':'REJECTED_UNSUPPORTED_VISIBLE_ROAD_CONTINUATION_AND_NO_PROVENANCE',
      'south':qa,'productionApproved':False,
    }
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--south',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--atlas',default='terrain-grid/v123-atlas.js')
    a=ap.parse_args()
    print(json.dumps(run(a.south,a.out,a.atlas),indent=2))
