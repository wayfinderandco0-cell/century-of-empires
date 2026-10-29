#!/usr/bin/env python3
"""Bake SOUTH's existing photographic cartway near the immutable V123 guide.

Fictional 1780–1880 game art only, not verified historical topography.
Unlike the rejected full-cell x-warp, this source-art registration adjusts
only the near-road vertical photo coordinate, never the road graph or Matrei.
The final JPEG is baked into the standalone candidate, not warped on iPhone.
"""
from __future__ import annotations
import argparse
import base64
from pathlib import Path
import re
import cv2
import numpy as np

SOURCE = 'art-reviews/v267-original-source/south-valley-recomposed-unapproved.jpg'
OUTPUT = 'art-reviews/v267-original-source/south-cartway-local-registered-unapproved.jpg'
HTML = 'v267-three-octagon-original-art-prototype.html'
# Original source-photo cartway control points (art observations, NOT roads).
PHOTO_XY = np.array([
    [540,310],[620,350],[700,380],[805,420],[930,455],
    [1050,485],[1140,515],[1270,540],[1390,565],[1480,585],[1536,595]
], dtype=np.float64)
# Unmodified V123 points and plausible continuation past its last road node.
V123_XY = np.array([
    [540,310],[620,350],[700,400],[805,442],[930,510],
    [1050,550],[1140,585],[1270,605],[1390,635],[1480,660],[1536,670]
], dtype=np.float64)

def bake(source: np.ndarray) -> np.ndarray:
    h,w = source.shape[:2]
    if (w,h) != (1536,1024):
        raise ValueError(f'Expected 1536x1024 SOUTH art, got {w}x{h}')
    xx = np.arange(w, dtype=np.float32)
    native_y = np.interp(xx, PHOTO_XY[:,0], PHOTO_XY[:,1]).astype(np.float32)
    graph_y = np.interp(xx, V123_XY[:,0], V123_XY[:,1]).astype(np.float32)
    delta = np.clip(graph_y-native_y, -95, 95)
    delta = cv2.GaussianBlur(delta[None,:], (0,0), 10)[0]
    ramp = np.clip((xx-540)/125,0,1)
    ramp = ramp*ramp*(3-2*ramp)
    delta *= ramp
    delta[xx<540] = 0
    xgrid,ygrid = np.meshgrid(xx,np.arange(h,dtype=np.float32))
    sample_y=ygrid.copy()
    for _ in range(6):
        weight=np.exp(-.5*((sample_y-graph_y[None,:])/190.0)**2)
        sample_y=ygrid-delta[None,:]*weight
    sample_y=np.clip(sample_y,0,h-1).astype(np.float32)
    return cv2.remap(source,xgrid,sample_y,cv2.INTER_CUBIC,
                     borderMode=cv2.BORDER_REPLICATE)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    root=args.repo
    src=cv2.imread(str(root/SOURCE),cv2.IMREAD_COLOR)
    if src is None:raise FileNotFoundError(root/SOURCE)
    art=bake(src)
    out=root/OUTPUT
    out.parent.mkdir(parents=True,exist_ok=True)
    if not cv2.imwrite(str(out),art,[cv2.IMWRITE_JPEG_QUALITY,94]):
        raise RuntimeError('Failed to write SOUTH artwork')
    html_path=root/HTML
    html=html_path.read_text(encoding='utf-8')
    encoded=base64.b64encode(out.read_bytes()).decode('ascii')
    replacement='ART_SOUTH="data:image/jpeg;base64,'+encoded+'"'
    new,n=re.subn(r'ART_SOUTH="data:image/jpeg;base64,[^"]+"',
                  lambda _:replacement,html,count=1)
    if n!=1:raise RuntimeError('Missing embedded ART_SOUTH; refusing write')
    new=new.replace('Native SOUTH forest • NEW original terrain source • no global warp • UNAPPROVED',
                    'SOUTH cartway photo registration • no global x warp • UNAPPROVED')
    if not args.dry_run:html_path.write_text(new,encoding='utf-8')
    print(f'SOUTH art baked: {out}, {out.stat().st_size} bytes; '
          f'embedded={not args.dry_run}; V121/V123/game/saves unchanged')

if __name__=='__main__':main()
