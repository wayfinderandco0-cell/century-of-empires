#!/usr/bin/env python3
"""Synthetic compositor tests; not artwork approval or mobile proof."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
import v267_native_ground_compositor as g
src=np.zeros((1450,2100,3),dtype=np.uint8)
src[:,:,0]=np.arange(2100,dtype=np.uint16)[None,:]%256
src[:,:,1]=np.arange(1450,dtype=np.uint16)[:,None]%256
src[:,:,2]=130
window,rect=g.ground_window(Image.fromarray(src),(.48,.56))
assert window.size==(1536,1024)
assert 1400<=rect[3]<=1450 and rect[2]-rect[0]==1536 and rect[3]-rect[1]==1024
assert np.array_equal(np.asarray(window)[0,0],src[rect[1],rect[0]])
a=np.asarray(window);b=np.roll(a,18,axis=1)
path=g.seam_path(a,b)
assert path.shape==(1536,) and 640<=path.min()<=path.max()<=905
out,report=g.compose(Image.fromarray(a),Image.fromarray(b))
assert out.size==(1536,1024)
assert report["roadsAdded"]==0 and not report["physicalTileEdgesVerified"]
assert np.array_equal(np.asarray(out)[:500],a[:500])
print("PASS V267 native ground compositor: no warping, bounded seam, no invented roads")
