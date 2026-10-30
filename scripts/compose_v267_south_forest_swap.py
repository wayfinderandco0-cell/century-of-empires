#!/usr/bin/env python3
"""Source-level relocation of native SOUTH forested shoulder and meadow, no tree warp.
Experimental fictional landscape, opt-in only; V123 and V121 untouched.
"""
from pathlib import Path
import numpy as np, cv2
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'art-reviews/v267-original-source/south-river-throat-recomposed-unapproved.webp'
OUT=ROOT/'art-reviews/v267-original-source/south-forest-shoulder-recomposed-unapproved.webp'
a=np.array(Image.open(SRC).convert('RGB'))
h,w=a.shape[:2]
yy,xx=np.mgrid[:h,:w].astype(np.float32)
# Only the meadow/forest slope LEFT of the x466 immutable cartway.
# Forest donor from lower native SOUTH, meadow donor from upper native SOUTH.
# No repeated trees: swap two nonoverlapping source regions.
top_source_y=np.clip(yy+430,0,h-1)
bottom_source_y=np.clip(yy-430,0,h-1)
mx=np.broadcast_to(xx,(h,w))
top=cv2.remap(a,mx,top_source_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
bottom=cv2.remap(a,mx,bottom_source_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def sm(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
# The original forest hillside naturally narrows toward the V123 cartway.
xedge=340+22*np.sin(yy/89)+13*np.sin(yy/39)
side=1-sm((xx-xedge+90)/130)
topmask=side*(1-sm((yy-295-15*np.sin(xx/78))/115))
bottommask=side*sm((yy-450-22*np.sin(xx/95))/105)*(1-sm((yy-760)/90))
# Protect every pixel in and near the road-bearing corridor and everything > x405.
topmask[:,405:]=0;bottommask[:,405:]=0
mask=np.maximum(topmask,bottommask)
donor=top*topmask[:,:,None]+bottom*bottommask[:,:,None]
result=a.astype(np.float32)*(1-mask[:,:,None])+donor
out=np.uint8(np.clip(result,0,255))
# original river and stone bridge, cartway and all forest to the east are byte-identical
assert np.array_equal(out[:,405:],a[:,405:])
changed=np.count_nonzero(np.max(abs(out.astype(np.int16)-a.astype(np.int16)),axis=2)>8)
Image.fromarray(out).save(OUT,'WEBP',quality=95,method=6)
print('forest swap',OUT,'changed',changed,'bytes',OUT.stat().st_size)
b=Image.new('RGB',(1536,900),'#19231c')
b.paste(Image.fromarray(a).crop((0,0,1536,450)),(0,0))
b.paste(Image.fromarray(out).crop((0,0,1536,450)),(0,450))
b.save('/tmp/south_forest_swap.jpg',quality=82)

# One isolated opt-in review mode; default WEST/MATREI/SOUTH remains unchanged.
HTML=ROOT/'v267-three-octagon-original-art-prototype.html'
html=HTML.read_text()
flag='const SOUTH_FOREST_SHOULDER_PREVIEW=SOUTH_ART_MODE==="forest"; /* V267_ORIGINAL_SOUTH_FOREST_SHOULDER */'
if flag not in html:
 marker='const SOUTH_THROAT_PREVIEW=SOUTH_ART_MODE==="throat";'
 assert marker in html
 html=html.replace(marker,flag+'\n'+marker,1)
needle='const southArtSource=SOUTH_THROAT_PREVIEW'
if 'const southArtSource=SOUTH_FOREST_SHOULDER_PREVIEW' not in html:
 assert needle in html
 html=html.replace(needle,'''const southArtSource=SOUTH_FOREST_SHOULDER_PREVIEW
   ? "art-reviews/v267-original-source/south-forest-shoulder-recomposed-unapproved.webp"
   : SOUTH_THROAT_PREVIEW''',1)
assert '[1536,478]' in html and '[466,0]' in html
HTML.write_text(html)
report=ROOT/'art-reviews/v267-south-forest-shoulder-review.md'
report.write_text(f'''# V267 native SOUTH forest-shoulder re-layout — UNAPPROVED

A fictional 1780–1880 Alpine game-art candidate, not verified historic topography.
The upper LEFT forested slope is moved as a coherent photographic source region
from lower native SOUTH (rigid x-preserving y displacement). Its former position
receives the upper native meadow source, avoiding duplicated trees or mirrored
landscape. The two regions are exchanged using an irregular terrain boundary,
not a global warp, random procedural tree sprites, or a digital road stripe.

The entire x>=405 corridor is byte-identical to the previous opt-in SOUTH
river-throat candidate. This includes the fixed x466 northern cartway, bridge,
river and all forest on the eastern slope. The original Matrei V121 image,
V123 100-node graph, V94 campaign, sprites, saves, and production remain unchanged.

Changed pixels (>8 RGB values): {changed}. Source asset: {OUT.name}.
Review only using ?southArt=forest; default remains unchanged. This is NOT
visual approval. Inspect actual phone-size WEST/MATREI/SOUTH screenshots for
photographic vertical transitions at x~330 and any road/river mismatch.
Production RED.
''')
print('opt-in preview patched; report',report)
