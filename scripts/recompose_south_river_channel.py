#!/usr/bin/env python3
"""Recompose the northern SOUTH river throat as a narrow photographed gorge.

Source-level art only, using the existing 1536x1024 original SOUTH river and
stone banks. No tree or road warps, synthetic blue river pool, copied Matrei
forest, mirrored landscape, extra settlements or V123 graph modifications.
This overwrites only the already opt-in ?southArt=basin candidate. It does NOT
change production or the default V267 art selection. Fictional Alpine game art.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"art-reviews/v267-original-source/south-bridge-contact-unapproved.webp"
OUT=ROOT/"art-reviews/v267-original-source/south-new-northern-basin-unapproved.webp"
REPORT=ROOT/"art-reviews/v267-northern-basin-review.md"
HTML=ROOT/"v267-three-octagon-original-art-prototype.html"
W,H=1536,1024

def smooth(a):
    a=np.clip(a,0,1)
    return a*a*(3-2*a)

def river_mask(rgb):
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    water=((hsv[:,:,0]>=79)&(hsv[:,:,0]<=125)&
           (hsv[:,:,1]>=37)&(hsv[:,:,2]>=48)).astype(np.uint8)
    water=cv2.morphologyEx(water,cv2.MORPH_CLOSE,
                           cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
    return water

def centerline(water):
    """Track the actual photographed SOUTH water, not a guessed x shift."""
    centers=[]
    previous=1100.
    for y in range(100,651):
        row=water[y,820:1470]
        coords=np.flatnonzero(row)+820
        coords=coords[np.abs(coords-previous)<210]
        if len(coords)>=9:
            bins=np.histogram(coords,bins=np.arange(820,1471,22))[0]
            k=int(np.argmax(bins))
            window=820+22*k+11
            near=coords[np.abs(coords-window)<70]
            if len(near)>=8: previous=.78*previous+.22*float(np.median(near))
        centers.append(previous)
    centers=np.array(centers,np.float32)
    centers=cv2.GaussianBlur(centers.reshape(-1,1),(1,41),0).ravel()
    return centers

def build(native):
    assert native.shape==(H,W,3)
    water=river_mask(native)
    actual=centerline(water)
    ys=np.arange(370,dtype=np.float32)
    xx=np.arange(W,dtype=np.float32)[None,:]
    yy=ys[:,None]
    # Matrei water exits ~949; converge to unchanged SOUTH gorge by y340.
    # The photographed throat is 55-70px radius, NOT a 150px turquoise basin.
    native_exit=float(actual[340-100])
    target=np.interp(ys,[0,80,170,250,340,369],
                     [949,966,1005,1050,native_exit,native_exit]).astype(np.float32)
    # Read actual SOUTH river water/stone downstream. Resample only water and
    # immediately adjoining bank material; native trees and road are immutable.
    donor_y=np.minimum(ys+145,649).astype(np.float32)
    donor_x=np.interp(donor_y,np.arange(100,651),actual)
    map_x=np.broadcast_to(xx+(donor_x-target)[:,None],(370,W)).copy()
    map_y=np.broadcast_to(donor_y[:,None],(370,W)).copy()
    donor=cv2.remap(native,map_x,map_y,cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_REFLECT_101)
    donor_water=cv2.remap(water,map_x,map_y,cv2.INTER_NEAREST,
                          borderMode=cv2.BORDER_CONSTANT)
    # Riverbank is an actual photographed bank, not randomly quilted water.
    bank=cv2.dilate(donor_water,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(39,39)))
    bank=cv2.GaussianBlur(bank.astype(np.float32),(0,0),6)
    dist=np.abs(xx-target[:,None])
    widths=np.interp(ys,[0,170,340],[78,72,104])[:,None]
    corridor=smooth((widths+15-dist)/23)
    depth=smooth((370-yy)/85)
    transplant=np.clip(bank*corridor*depth,0,1)
    # Reject donor trees; only native photographic water and limestone banks.
    dhsv=cv2.cvtColor(donor,cv2.COLOR_RGB2HSV)
    forest=((dhsv[:,:,0]>=31)&(dhsv[:,:,0]<=77)&
            (dhsv[:,:,1]>=53)&(dhsv[:,:,2]<195))
    transplant[forest & (donor_water==0)]*=.12
    transplant[:,:720]=0
    transplant[:,1450:]=0

    # Eliminate displaced northern river mouth, avoiding parallel rivers.
    # Inpaint water well outside NEW gorge using surrounding native ground.
    old=np.zeros((H,W),np.uint8)
    old[:255]=water[:255]*255
    old[:255,:770]=0
    old[:255,1450:]=0
    protect=(np.abs(xx-target[:,None])<widths+23)
    old[:255][protect[:255]]=0
    old=cv2.dilate(old,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    old[255:]=0
    old[:,:720]=0
    old[:,1450:]=0
    background=cv2.inpaint(native,old,9,cv2.INPAINT_TELEA)
    # Preserve native river once the replacement corridor rejoins it.
    base=background[:370].astype(np.float32)
    join=smooth((ys-215)/125)[:,None,None]
    base=base*(1-join)+native[:370].astype(np.float32)*join
    result=native.copy()
    alpha=transplant[:,:,None]
    result[:370]=np.uint8(np.clip(base*(1-alpha)+donor.astype(np.float32)*alpha,0,255))
    assert np.array_equal(result[370:],native[370:])
    assert np.array_equal(result[:370,:720],native[:370,:720])
    assert np.array_equal(result[:370,1450:],native[:370,1450:])
    delta=np.max(abs(result.astype(np.int16)-native.astype(np.int16)),axis=2)
    changed=int(np.count_nonzero(delta>8))
    assert changed>18000,("No substantial river reconstruction",changed)
    return result,changed,int(np.count_nonzero(old)),float(native_exit)

def main():
    html=HTML.read_text(encoding="utf-8")
    assert "SOUTH_BASIN_PREVIEW" in html
    assert "south-new-northern-basin-unapproved.webp" in html
    assert "[1536,478]" in html and "[466,0]" in html
    with Image.open(SOURCE) as f:
        native=np.asarray(f.convert("RGB"))
    result,changed,removed,exit_x=build(native)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(result).save(OUT,"WEBP",quality=94,method=6)
    REPORT.write_text(
      "# Narrow photographed SOUTH river throat - UNAPPROVED\n\n"
      "Replaces the previously rejected oversized turquoise basin in the SAME "
      "opt-in ?southArt=basin review mode. This is original fictional Alpine "
      "game artwork, not verified historical topography. The northern water "
      "throat is 55-70px radius rather than the previous 150px basin. Its "
      "water and adjoining limestone bank come from one contiguous photographed "
      "SOUTH river reach, not randomized material quilts or Matrei scenery. "
      "The old displaced northern water is locally inpainted with native "
      "terrain; the new throat converges to the untouched downstream river. "
      "All native trees, the x466 cartway, bridge, and everything below y370 "
      "are preserved without a global terrain warp.\n\n"
      f"Changed source pixels: {changed}; old water inpaint mask: {removed}; "
      f"native downstream water x near y340: {exit_x:.1f}.\n\n"
      "Still requires actual phone-size screenshot inspection. Inpainting may "
      "look artificial in rocky terrain; passing browser or movement checks "
      "cannot approve the art. Matrei V121, V123 100-node road graph, V94 "
      "campaign, sprites, saves, default preview and production unchanged. "
      "Production RED.\n\n"
      f"Original SOUTH SHA256: {hashlib.sha256(SOURCE.read_bytes()).hexdigest()}\n"
      f"Candidate SHA256: {hashlib.sha256(OUT.read_bytes()).hexdigest()}\n",
      encoding="utf-8")
    print("Narrow photographed SOUTH river built:",OUT,OUT.stat().st_size,
          "changed",changed,"old water mask",removed,"downstream x",exit_x)

if __name__=="__main__":
    main()
