#!/usr/bin/env python3
"""Produce inspectable browser screenshots of the ACTUAL V267 embedded landscape.
The screenshots remove navigation overlays; they are never simulations or mockups.
"""
import json
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"v267-three-octagon-original-art-prototype.html").read_text()
OUT=ROOT/"art-reviews"
OUT.mkdir(exist_ok=True)
VIEWS=[("SOUTH JOIN","south"),("WEST JOIN","west"),("WHOLE MAP","whole")]
images=[]
errors=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    context=browser.new_context(viewport={"width":390,"height":844},
         device_scale_factor=2,is_mobile=True,has_touch=True)
    page=context.new_page()
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.set_content(HTML,wait_until="load")
    page.wait_for_function("window.COE && COE.originalMatreiLoaded && COE.sourceRegistered && COE.decorativeGapPatches.length===3",timeout=90000)
    # Remove fixed HUD overlays and labels solely for clean visualization.
    page.evaluate("""() => {
       document.querySelector('header').style.display='none';
       document.querySelector('footer').style.display='none';
    }""")
    for label,place in VIEWS:
        if place=="whole":
            page.evaluate("document.querySelector('#whole').click()")
        else:
            page.evaluate("(join) => COE.focusJoin(join)",place)
        page.wait_for_timeout(250)
        raw=page.screenshot()
        frame=Image.open(BytesIO(raw)).convert("RGB")
        images.append((label,frame))
    assert not errors, errors
    assert page.evaluate("COE.nodes") == 100
    assert page.evaluate("COE.westSouthConnected")
    context.close();browser.close()
padding=24;title=52
width=max(im.width for _,im in images);height=max(im.height for _,im in images)
board=Image.new("RGB",(len(images)*(width+padding)+padding,height+title+2*padding),(21,35,29))
draw=ImageDraw.Draw(board)
for i,(label,im) in enumerate(images):
    x=padding+i*(width+padding)
    draw.text((x,padding+12),label,fill=(241,231,199))
    board.paste(im,(x,title+padding))
board.save(OUT/"v267-road-scene-current.jpg",quality=87,optimize=True)
(OUT/"v267-road-scene-current.json").write_text(json.dumps({
  "description":"Chromium actual V267 candidate art, HUD hidden for inspection",
  "orientation":"390x844, DPR2",
  "panels":[x for x,_ in images],
  "production_approved":False,
  "native_iphone_safari_verified":False,
  "errors":errors
},indent=2))
print("Saved clean browser image at",OUT/"v267-road-scene-current.jpg")
