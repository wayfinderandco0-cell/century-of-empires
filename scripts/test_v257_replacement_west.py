#!/usr/bin/env python3
"""V257 regressions: replace the blocked WEST source without relaxing V123 gates."""
import sys,unittest,tempfile
from pathlib import Path
import numpy as np,cv2
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v257_replacement_west import TRACE,PINS,NATIVE,TARGET,check_atlas,verify_source,build
from v256_real_cartway import TRACE as OLD_TRACE,target_at_source_progress
from v255_anchored_cartway import mapping,evaluate,paired_samples

class ReplacementWestTests(unittest.TestCase):
 def test_original_source_pins_distinct_and_replaced(self):
  self.assertNotEqual(PINS['west'],'7326e88c778ed4a0018c241156e701690e95deb1feeb8fa13a298c0f0c74505e')
  self.assertNotEqual(PINS['west'],PINS['south'])
  self.assertEqual(len(TRACE['west']),18)
 def test_immutable_v123_and_fixed_endpoints(self):
  check_atlas(Path(__file__).resolve().parent.parent/'terrain-grid/v123-atlas.js')
  self.assertEqual(TARGET['west'][0],[275,550]);self.assertEqual(TARGET['west'][-1],[1536,478])
  self.assertEqual(TARGET['south'][-1],[1270,605])
 def test_new_west_below_original_displacement_limit(self):
  dst=target_at_source_progress('west',TRACE['west'])
  mx,my,*_=mapping(TRACE['west'],dst,sigma=170,spacing=1.25)
  qa=evaluate(mx,my,TRACE['west'],dst)
  self.assertEqual(mx.shape,NATIVE)
  self.assertLess(qa['maxPairedAnchorDisplacementPx'],155)
  self.assertLess(qa['maxPairedAnchorDisplacementPx'],160.15)
  self.assertGreater(qa['minSampledJacobian'],.24)
  self.assertEqual(qa['foldedFraction'],0)
  self.assertTrue(qa['necessaryGeometryPass'])
 def test_old_west_still_rejected_without_relaxing_limit(self):
  dst=target_at_source_progress('west',OLD_TRACE['west'])
  mx,my,*_=mapping(OLD_TRACE['west'],dst,sigma=170,spacing=1.25)
  qa=evaluate(mx,my,OLD_TRACE['west'],dst)
  self.assertGreater(qa['maxPairedAnchorDisplacementPx'],155)
  self.assertFalse(qa['necessaryGeometryPass'])
 def test_south_geometry_unchanged(self):
  self.assertEqual(TRACE['south'],OLD_TRACE['south'])
  dst=target_at_source_progress('south',TRACE['south'])
  mx,my,*_=mapping(TRACE['south'],dst,sigma=170,spacing=1.25)
  qa=evaluate(mx,my,TRACE['south'],dst)
  self.assertTrue(qa['necessaryGeometryPass'])
 def test_synthetic_cartway_pixel_transport(self):
  dst=target_at_source_progress('west',TRACE['west'])
  mx,my,*_=mapping(TRACE['west'],dst,sigma=170,spacing=1.25)
  img=np.zeros((*NATIVE,3),np.uint8)
  cv2.polylines(img,[np.asarray(TRACE['west'],np.int32)],False,(255,255,255),20,cv2.LINE_AA)
  warp=cv2.remap(img,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  _,pts=paired_samples(TRACE['west'],dst,spacing=5)
  pixels=warp[np.clip(np.rint(pts[:,1]).astype(int),0,1023),np.clip(np.rint(pts[:,0]).astype(int),0,1535),0]
  self.assertGreater(float(np.mean(pixels>150)),.94)
 def test_reject_wrong_source_hash(self):
  with tempfile.TemporaryDirectory() as tmp:
   fake=Path(tmp)/'fake.png';fake.write_bytes(b'not pinned image')
   with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):verify_source('west',fake)
 def test_real_art_optional_fail_closed(self):
  import os
  west=os.environ.get('V257_WEST_PNG');south=os.environ.get('V257_SOUTH_PNG')
  if not (west and south):self.skipTest('Original PNGs absent in CI: real-image gameplay unverified')
  atlas=Path(__file__).resolve().parent.parent/'terrain-grid/v123-atlas.js'
  with tempfile.TemporaryDirectory() as tmp:
   for tile,src in [('west',west),('south',south)]:
    qa=build(tile,src,atlas,tmp)
    self.assertTrue(qa['necessaryGeometryPass'])
    self.assertFalse(qa['productionApproved'])
    self.assertTrue((Path(tmp)/(tile+'-v257-road-review.jpg')).exists())

if __name__=='__main__':unittest.main()
