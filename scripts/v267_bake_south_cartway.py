#!/usr/bin/env python3
"""Bake a visually aligned SOUTH cartway and shared terrain edge in V267.

Original SOUTH ground art is moved as a coherent landscape, not replaced by
a digital road stripe. This fictional art prototype is not verified historic
topography. Matrei source bytes, V123 topology, V94 engine, sprites and saves
remain untouched; the review is never promoted to main by this script.
"""
from __future__ import annotations
import argparse
import base64
from pathlib import Path
import re
import cv2
import numpy as np

SOURCE = 'art-reviews/v267-original-source/south-no-horizon-overhead-unapproved.jpg'
OUTPUT = 'art-reviews/v267-original-source/south-cartway-local-registered-unapproved.jpg'
HTML = 'v267-three-octagon-original-art-prototype.html'
# Fixed V123 road nodes plus an off-graph continuation at the right edge.
TARGET = np.array([
 [466,0],[466,74],[470,160],[488,235],[540,310],[620,350],
 [700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605],
 [1536,670]], dtype=np.float64)
# Original photograph road centerline; image-control points, not geography.
PHOTO = np.array([
 [515,0],[515,74],[520,100],[530,140],[540,175],[620,230],
 [700,285],[805,345],[930,412],[1050,450],[1140,472],[1270,486],
 [1536,510]], dtype=np.float64)
# Stabilize the forests, river and exterior. Never reflect or repeat tiles.
ANCHORS = np.array([
 [0,0],[0,200],[0,450],[0,800],[0,1023],
 [1535,0],[1535,150],[1535,850],[1535,1023],
 [250,0],[850,0],[1150,0],[1400,0],
 [250,1023],[550,1023],[850,1023],[1150,1023],[1400,1023],
 [300,700],[650,900],[950,980]], dtype=np.float64)

def kernel(p, q):
    d = p[:,None,:] - q[None,:,:]
    r2 = np.sum(d*d, axis=2)
    return 0.5*r2*np.log(np.maximum(r2,1e-10))

def bake(source):
    h,w = source.shape[:2]
    if (w,h) != (1536,1024):
        raise ValueError(f'Expected 1536x1024 SOUTH art, got {w}x{h}')
    points = np.vstack((TARGET, ANCHORS))
    offsets = np.vstack((PHOTO-TARGET, np.zeros_like(ANCHORS)))
    n = len(points)
    p = np.column_stack((np.ones(n), points))
    a = np.block([[kernel(points,points)+np.eye(n)*1000,p],
                  [p.T,np.zeros((3,3))]])
    weights = np.linalg.solve(a,np.vstack((offsets,np.zeros((3,2)))))
    yy,xx = np.mgrid[0:h:16,0:w:16].astype(np.float32)
    q = np.column_stack((xx.ravel(),yy.ravel()))
    basis = np.column_stack((kernel(q,points),np.ones(len(q)),q))
    field = (basis@weights).reshape(*xx.shape,2).astype(np.float32)
    dx = cv2.resize(field[:,:,0],(w,h),interpolation=cv2.INTER_CUBIC)
    dy = cv2.resize(field[:,:,1],(w,h),interpolation=cv2.INTER_CUBIC)
    gy,gx = np.mgrid[0:h,0:w].astype(np.float32)
    return cv2.remap(source,np.clip(gx+dx,0,w-1),np.clip(gy+dy,0,h-1),
                     cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)

MATREI_BEFORE = "canvas.getContext('2d').putImageData(out,0,0);return canvas;\n}\nfunction loadImage"
MATREI_AFTER = """canvas.getContext('2d').putImageData(out,0,0);
 // Only in the isolated review: the bottom eight GOLD-frame pixels at
 // the SOUTH join become adjacent native V121 terrain pixels.
 // The original V121 image asset remains byte-for-byte unchanged.
 const edgeCtx=canvas.getContext('2d');
 edgeCtx.putImageData(edgeCtx.getImageData(0,1008,W,8),0,1016);
 return canvas;
}
function loadImage"""
FRAME_BEFORE = 'ctx.save();ctx.translate(...tile.o);poly();ctx.strokeStyle="#e1cda087";ctx.lineWidth=7;ctx.stroke();ctx.restore();'
FRAME_AFTER = """ctx.save();ctx.translate(...tile.o);ctx.strokeStyle="#e1cda087";ctx.lineWidth=7;
  // Shared road-bearing sides are not gold fake cartways.
  // All outer octagon sides keep the original frame/zoom treatment.
  ctx.beginPath();
  if(tile.id==="matrei"){
    ctx.moveTo(CUT,0);ctx.lineTo(W-CUT,0);ctx.lineTo(W,CUT);ctx.lineTo(W,H-CUT);ctx.lineTo(W-CUT,H);
    ctx.moveTo(CUT,H);ctx.lineTo(0,H-CUT);ctx.lineTo(0,CUT);ctx.lineTo(CUT,0);
  }else if(tile.id==="west"){
    ctx.moveTo(CUT,0);ctx.lineTo(W-CUT,0);ctx.lineTo(W,CUT);
    ctx.moveTo(W,H-CUT);ctx.lineTo(W-CUT,H);ctx.lineTo(CUT,H);ctx.lineTo(0,H-CUT);ctx.lineTo(0,CUT);ctx.lineTo(CUT,0);
  }else{
    ctx.moveTo(W,CUT);ctx.lineTo(W,H-CUT);ctx.lineTo(W-CUT,H);ctx.lineTo(CUT,H);ctx.lineTo(0,H-CUT);ctx.lineTo(0,CUT);ctx.lineTo(CUT,0);
  }
  ctx.stroke();ctx.restore();"""

def update_html(html, jpeg):
    graph = re.search(r'const atlas=\[.*?\];\nconst ART_MATREI_CANONICAL=',html,re.S)
    matrei = re.search(r'ART_MATREI_CANONICAL="data:image/webp;base64,[^"]+"',html)
    if not graph or not matrei:
        raise RuntimeError('Cannot verify protected V121/V123 content')
    encoded = base64.b64encode(jpeg).decode('ascii')
    replacement = 'ART_SOUTH="data:image/jpeg;base64,'+encoded+'"'
    changed,n = re.subn(r'ART_SOUTH="data:image/jpeg;base64,[^"]+"',
                        lambda _:replacement,html,count=1)
    if n!=1:
        raise RuntimeError('Missing single embedded SOUTH image')
    if MATREI_BEFORE in changed:
        changed=changed.replace(MATREI_BEFORE,MATREI_AFTER,1)
    elif MATREI_AFTER not in changed:
        raise RuntimeError('Unexpected Matrei renderer; refusing modification')
    if FRAME_BEFORE in changed:
        changed=changed.replace(FRAME_BEFORE,FRAME_AFTER,1)
    elif FRAME_AFTER not in changed:
        raise RuntimeError('Unexpected frame renderer; refusing modification')
    changed=changed.replace('SOUTH cartway photo registration • no global x warp • UNAPPROVED',
                            'SOUTH terrain-aligned road + natural forest • UNAPPROVED')
    if graph.group(0) not in changed or matrei.group(0) not in changed:
        raise RuntimeError('Protected V121 image or V123 graph changed')
    return changed

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    root=args.repo
    source=cv2.imread(str(root/SOURCE),cv2.IMREAD_COLOR)
    if source is None:
        raise FileNotFoundError(root/SOURCE)
    art=bake(source)
    ok,encoded=cv2.imencode('.jpg',art,[cv2.IMWRITE_JPEG_QUALITY,94])
    if not ok:
        raise RuntimeError('Cannot encode original SOUTH terrain')
    data=encoded.tobytes()
    changed=update_html((root/HTML).read_text(encoding='utf-8'),data)
    if not args.dry_run:
        out=root/OUTPUT
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_bytes(data)
        (root/HTML).write_text(changed,encoding='utf-8')
    print('Baked',len(data),'bytes of terrain-aligned SOUTH art; embedded:',not args.dry_run,
          '| original V121, 100-node V123, V94/saves/sprites untouched | UNAPPROVED')

if __name__=='__main__':
    main()
