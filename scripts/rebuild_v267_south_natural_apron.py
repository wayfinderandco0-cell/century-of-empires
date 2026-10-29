#!/usr/bin/env python3
"""Photographic SOUTH terrain join for isolated V267 only. Never edits V121/V123/V94."""
from __future__ import annotations
import base64,hashlib,io,re
from pathlib import Path
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"v267-three-octagon-original-art-prototype.html"
ART=ROOT/"art-reviews/v267-original-source/south-northern-apron-unapproved.jpg"
REVIEW=ROOT/"art-reviews/v267-south-northern-apron-review.md"
W,H=1536,1024

def decode(html,name):
 m=re.search(r'(?<!\w)'+name+r'="data:image/[^;]+;base64,([^"]+)"',html)
 if not m: raise RuntimeError("Missing embedded image "+name)
 im=Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert("RGB")
 if im.size!=(W,H): raise RuntimeError("Wrong art dimensions "+name)
 return np.asarray(im),m

def matrei_ground(src):
 y,x=np.mgrid[0:H,0:W].astype("float32")
 t=np.clip((y-845)/179,0,1);t=t*t*(3-2*t)
 sy=10+y*(953/H)-26*t
 sl=np.where(sy<286,385-(sy-10)*(295/276),np.where(sy>674,90+(sy-674)*(295/289),90))
 tl=np.where(y<256,256-y,np.where(y>768,y-768,0));tr=W-tl
 b=np.clip((y-700)/324,0,1);b=b*b*(3-2*b)
 sx=np.clip(sl+(x-tl)*(W-2*sl)/(tr-tl)-55*b*np.exp(-.5*((x-466)/105)**2),0,W-1.001)
 west=26*np.exp(-.5*((x-240)/400)**2)*np.exp(-.5*((y-505)/110)**2)
 mat=cv2.remap(src,sx.astype("float32"),np.clip(sy+west,0,H-1.001).astype("float32"),cv2.INTER_LINEAR)
 mat[(x<tl)|(x>tr)]=0
 return mat

def main():
 html=HTML.read_text(encoding="utf-8")
 if "SOUTH_NATURAL_APRON_20261029" in html:
  print("Already applied; no second resampling");return
 south,m=decode(html,"ART_SOUTH")
 source,_=decode(html,"ART_MATREI_CANONICAL")
 mat=matrei_ground(source)
 y,x=np.mgrid[0:H,0:W].astype("float32")
 dr=np.interp(y,[0,74,160,235,340],[41,39,28,16,0])
 rv=np.interp(y,[0,160,340],[108,75,0])
 displacement=np.where(x<466,dr*np.clip(x/466,0,1),
  np.where(x<900,dr+(rv-dr)*np.clip((x-466)/434,0,1),
  rv*(1-np.clip((x-900)/500,0,1))))
 south=cv2.remap(south,np.clip(x+displacement,0,W-1.001).astype("float32"),
                 y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
 # Low-frequency photographic color adjustment without inventing a road stripe.
 ml=cv2.cvtColor(mat,cv2.COLOR_RGB2LAB).astype("float32")
 sl=cv2.cvtColor(south,cv2.COLOR_RGB2LAB).astype("float32")
 ref=cv2.GaussianBlur(ml[982:1015].mean(axis=0),(0,0),48)
 own=cv2.GaussianBlur(sl[:35].mean(axis=0),(0,0),48)
 correction=cv2.GaussianBlur(ref-own,(0,0),64)
 correction=np.clip(correction,[-22,-9,-9],[22,9,9])
 edge=np.clip((x-256)/90,0,1)*np.clip((1280-x)/90,0,1)
 edge=edge*edge*(3-2*edge)
 fade=np.clip((190-y)/190,0,1);fade=fade*fade*(3-2*fade)
 sl+=.48*fade[:,:,None]*edge[:,:,None]*correction[None,:,:]
 south=cv2.cvtColor(np.uint8(np.clip(sl,0,255)),cv2.COLOR_LAB2RGB)
 for j in range(12):
  a=.72*(1-j/12)**2
  south[j,256:1280]=np.uint8((1-a)*south[j,256:1280]+a*mat[1011+j,256:1280])
 output=io.BytesIO()
 Image.fromarray(south).save(output,"JPEG",quality=92,subsampling=0,optimize=True)
 jpg=output.getvalue()
 uri='ART_SOUTH="data:image/jpeg;base64,'+base64.b64encode(jpg).decode("ascii")+'"'
 html=html[:m.start()]+uri+html[m.end():]
 # V121 image is unchanged; only the display copy's bottom 26px gold is omitted.
 old_sy="const sy=10+y*(953/H);"
 new_sy="const edgeT=Math.max(0,Math.min(1,(y-845)/179)); const edgeSmooth=edgeT*edgeT*(3-2*edgeT); const sy=10+y*(953/H)-26*edgeSmooth; /* SOUTH_NATURAL_APRON_20261029 */"
 if html.count(old_sy)!=1: raise RuntimeError("Matrei render mapping changed")
 html=html.replace(old_sy,new_sy,1)
 # Preserve exterior octagon frame, remove only four shared-side strokes.
 old_frame='ctx.save();ctx.translate(...tile.o);poly();ctx.strokeStyle="#e1cda087";ctx.lineWidth=7;ctx.stroke();ctx.restore();'
 new_frame='''ctx.save();ctx.translate(...tile.o);
   const sides=[[CUT,0],[W-CUT,0],[W,CUT],[W,H-CUT],[W-CUT,H],[CUT,H],[0,H-CUT],[0,CUT]];
   ctx.strokeStyle="#e1cda087";ctx.lineWidth=7;
   for(let i=0;i<8;i++){
    if((tile.id==="matrei"&&(i===4||i===6))||(tile.id==="south"&&i===0)||(tile.id==="west"&&i===2))continue;
    ctx.beginPath();ctx.moveTo(...sides[i]);ctx.lineTo(...sides[(i+1)%8]);ctx.stroke();
   }ctx.restore();'''
 if html.count(old_frame)==1:
  html=html.replace(old_frame,new_frame,1)
 else:
  # The current V267 renderer already has custom shared-edge framing.
  # Preserve it rather than overwriting the existing design system.
  print("Preserving existing V267 shared-side frame treatment")
 assert html.count("const southRoad=")==1 and html.count("const westRoad=")==1
 ART.parent.mkdir(parents=True,exist_ok=True)
 ART.write_bytes(jpg)
 HTML.write_text(html,encoding="utf-8")
 REVIEW.write_text(
  "# SOUTH natural photographic apron — UNAPPROVED\n\n"
  "Fictional original Alpine prototype art; not historically verified.\n\n"
  "Changes: locally register the first 340px of SOUTH terrain, retain native trees, "
  "join the photographed cartway at x466, adjust natural stream material, remove "
  "V121 render-copy gold from the shared SOUTH boundary, and suppress only "
  "the two pairs of shared-edge frame strokes. The V121 source image and "
  "100-node V123 graph are unchanged. No production renderer, V94, sprites or saves edited.\n\n"
  "Still requires physical iPhone Safari inspection, WEST and SOUTH visual approval, "
  "and road alignment farther east. Production RED.\n\n"
  "SOUTH JPEG SHA256: "+hashlib.sha256(jpg).hexdigest()+"\n",encoding="utf-8")
 print("SOUTH terrain rebuilt",len(jpg),"bytes; SHA256",hashlib.sha256(jpg).hexdigest())
if __name__=="__main__": main()
