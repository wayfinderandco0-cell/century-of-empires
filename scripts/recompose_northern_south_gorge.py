from PIL import Image, ImageDraw, ImageFont
import re, base64, io
import numpy as np, math, hashlib
from scipy.ndimage import gaussian_filter
from pathlib import Path
root=Path('/tmp/coe')
html_path=root/'v267-three-octagon-original-art-prototype.html'
html=html_path.read_text(encoding='utf-8')
m=re.search(r'ART_SOUTH\s*=\s*"data:image/[^;]+;base64,([^"]+)',html)
assert m, 'Missing durable original SOUTH data URL'
base=np.asarray(Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB'),dtype=np.float32)
donor=np.asarray(Image.open(root/'art-reviews/v267-original-source/south-bridge-contact-unapproved.webp').convert('RGB'),dtype=np.float32)
H,W=base.shape[:2]
assert (W,H)==(1536,1024)
yy,xx=np.mgrid[:H,:W].astype(np.float32)
# Reconstruct a whole, photographic northern river gorge. Keep native cartway
# corridor and the original bridge downstream; no displacement of any trees.
# Donor is an independent SOUTH gorge source, not V121 Matrei.
# A rigid 25px source offset aligns the natural river throat at the northern edge.
donor=np.pad(donor,((0,0),(0,35),(0,0)),mode='edge')[:,25:25+W]
def sm(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
# The boundary follows meadow/forest/rock irregularity, not a straight rectangle.
edge_x=720+37*np.sin(yy/87)+21*np.sin(yy/31)
edge_y=345+46*np.sin(xx/149)+23*np.sin(xx/57)
alpha=sm((xx-edge_x)/115)*(1-sm((yy-edge_y)/140))
alpha[:,:670]=0
alpha[545:]=0
# Source-faithful full photographic scene composition with broad natural boundary.
# No per-pixel displacement of trees or rocks, no fabricated road stroke.
from PIL import ImageFilter
mask=Image.fromarray(np.uint8(np.clip(alpha*255,0,255)),mode='L').filter(ImageFilter.GaussianBlur(radius=15))
photoA=Image.fromarray(np.uint8(base));photoB=Image.fromarray(np.uint8(donor))
out=np.asarray(Image.composite(photoB,photoA,mask),dtype=np.uint8).copy()
out[:,:670]=base[:,:670].astype(np.uint8)
out[545:]=base[545:].astype(np.uint8)
p=root/'art-reviews/v267-original-source/south-northern-photographic-gorge-review.webp'
Image.fromarray(out).save(p,'WEBP',quality=92,method=6)
changed=int(np.count_nonzero(np.max(np.abs(out.astype(np.int16)-base.astype(np.int16)),axis=2)>8))
print('changed',changed,'size',p.stat().st_size,'sha256',hashlib.sha256(p.read_bytes()).hexdigest())
# Review two full sources plus tight 900x500 top junction at equal scale.
im=Image.open(p).convert('RGB')
before=Image.fromarray(base.astype(np.uint8))
can=Image.new('RGB',(1500,850),'#191d1a');d=ImageDraw.Draw(can)
for i,(photo,name) in enumerate([(before,'CURRENT SOUTH'),(im,'NEW GORGE')]):
 crop=photo.crop((0,0,1536,760)).resize((750,750))
 can.paste(crop,(750*i,38));d.text((750*i+15,12),name,fill='white')
can.save('/tmp/south-before-after.jpg',quality=70,optimize=True)
print('comparison bytes',Path('/tmp/south-before-after.jpg').stat().st_size)


# Add one isolated source-art switch; the default source remains unchanged.
marker='const SOUTH_BASIN_PREVIEW=SOUTH_ART_MODE==="basin";'
flag='const SOUTH_CONTINUITY_PREVIEW=SOUTH_ART_MODE==="continuity"; /* NORTH_SOUTH_ORIGINAL_GORGE_RECOMPOSITION */'
if flag not in html:
 assert marker in html
 html=html.replace(marker,flag+'\n'+marker,1)
needle='const southArtSource=SOUTH_BASIN_PREVIEW'
replacement=('const southArtSource=SOUTH_CONTINUITY_PREVIEW\n'
 '   ? "art-reviews/v267-original-source/south-northern-photographic-gorge-review.webp"\n'
 '   : SOUTH_BASIN_PREVIEW')
if 'const southArtSource=SOUTH_CONTINUITY_PREVIEW' not in html:
 assert needle in html
 html=html.replace(needle,replacement,1)
html_path.write_text(html,encoding='utf-8')
report=root/'art-reviews/v267-northern-gorge-recomposition-review.md'
report.write_text(
 '# NORTH SOUTH photographic gorge reconstruction — isolated, UNAPPROVED\n\n'
 'A newly composed 1536×1024 fictional Alpine SOUTH scene, not verified historic topography. '
 'The original WEST, Matrei V121, V123 100-node route graph, V94 campaign, sprites, saves, '
 'default preview, and production remain unchanged.\n\n'
 'The new northern gorge replaces the large waterfall with a natural narrow rapids-and-limestone '
 'corridor using an independent existing SOUTH photographic source. A geographically irregular '
 'transition extends across the northern 545px and the eastern forest and river; '
 'the native cartway corridor x<670 and entire landscape below y545 are byte-preserved '
 'from the existing SOUTH art. Trees and cliffs are transferred rigidly, not warped. '
 'No new settlements or digital road strokes were added. '
 'The existing stone bridge is preserved.\n\n'
 f'Image pixels changed (>8 RGB levels): {changed}; source SHA256: {hashlib.sha256(p.read_bytes()).hexdigest()}.\n\n'
 'Review only with southArt=continuity; the candidate may still have a visible Matrei–SOUTH '
 'transition and may not have perfect photographic road alignment. Do not merge or call it '
 'approved based solely on browser/pathfinding checks. Compare actual iPhone-sized '
 'screenshots and request physical iPhone visual acceptance first. Production RED.\n',
 encoding='utf-8')
print('patched opt-in HTML; report',report)
