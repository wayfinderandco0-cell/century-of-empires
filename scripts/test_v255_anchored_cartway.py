#!/usr/bin/env python3
"""V255 synthetic existing-road contact and immutable V123 regression checks.

These tests prove transform mechanics, NOT photographic road realism,
geographic registration, bridge-bank continuity, or user art approval.
"""
import sys
import hashlib
import tempfile
import unittest
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from v255_anchored_cartway import (
 SOURCE,TARGET,PINS,NATIVE,V123_SHA,paired_samples,mapping,evaluate,process
)

class AnchoredRoadTests(unittest.TestCase):
 def test_v123_immutable(self):
  raw=(ROOT/"terrain-grid/v123-atlas.js").read_bytes()
  sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
  self.assertEqual(sha,V123_SHA)
  self.assertEqual(TARGET["west"][0],[275,550])
  self.assertEqual(TARGET["south"][-1],[1270,605])
 def test_distinct_pins_and_native_anchor_pairs(self):
  self.assertNotEqual(PINS["west"],PINS["south"])
  for tile in ("west","south"):
   self.assertEqual(len(SOURCE[tile]),len(TARGET[tile]))
   self.assertGreaterEqual(len(SOURCE[tile]),12)
 def test_reject_unpaired_anchor(self):
  with self.assertRaisesRegex(ValueError,"correspond"):
   paired_samples([[1,1],[2,2]],[[1,1],[2,2],[3,3]])
 def test_geometry_both_native_cells(self):
  for tile in ("west","south"):
   mx,my=mapping(SOURCE[tile],TARGET[tile])
   self.assertEqual(mx.shape,NATIVE)
   q=evaluate(mx,my,SOURCE[tile],TARGET[tile])
   self.assertTrue(q["necessaryGeometryPass"],(tile,q))
   self.assertLessEqual(q["maxAnchorRemapErrorPx"],2.0)
   self.assertEqual(q["foldedFraction"],0)
 def test_synthetic_existing_road_pixels_reach_v123(self):
  for tile in ("west","south"):
   # Bright road is drawn on SOURCE only, never on V123 target.
   img=np.zeros((*NATIVE,3),np.uint8)
   cv2.polylines(img,[np.asarray(SOURCE[tile],np.int32)],False,(245,245,245),18,cv2.LINE_AA)
   mx,my=mapping(SOURCE[tile],TARGET[tile])
   warped=cv2.remap(img,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
   _,target=paired_samples(SOURCE[tile],TARGET[tile],spacing=4)
   x=np.clip(np.rint(target[:,0]).astype(int),0,1535)
   y=np.clip(np.rint(target[:,1]).astype(int),0,1023)
   samples=warped[y,x,0]
   self.assertGreater(float(np.mean(samples>160)),.95,(tile,float(np.mean(samples>160))))
 def test_reject_wrong_source_sha(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"fake.png";p.write_bytes(b"not a pinned image")
   with self.assertRaisesRegex(ValueError,"wrong original source SHA256"):
    process("south",p,Path(d)/"out",ROOT/"terrain-grid/v123-atlas.js")

if __name__=="__main__":unittest.main()
