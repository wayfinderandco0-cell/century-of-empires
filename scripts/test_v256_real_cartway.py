#!/usr/bin/env python3
"""V256 regression: reject real-road misregistration instead of trusting guessed anchors."""
import hashlib,sys,unittest,tempfile
from pathlib import Path
import numpy as np,cv2
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v256_real_cartway import TRACE,TARGET,PINS,NATIVE,V123_SHA,arc_positions,target_at_source_progress,process
from v255_anchored_cartway import mapping,evaluate,paired_samples

class RealCartwayTests(unittest.TestCase):
 def test_immutable_v123_hash_and_endpoints(self):
  local=Path(__file__).resolve().parent
  atlas=local/'terrain-grid/v123-atlas.js'
  if not atlas.exists():atlas=local.parent/'terrain-grid/v123-atlas.js'
  data=atlas.read_bytes();sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  self.assertEqual(sha,V123_SHA)
  self.assertEqual(TARGET['west'][0],[275,550]);self.assertEqual(TARGET['south'][-1],[1270,605])
 def test_source_pins_distinct_and_more_dense_than_v255(self):
  self.assertNotEqual(PINS['west'],PINS['south'])
  self.assertGreaterEqual(len(TRACE['west']),18);self.assertGreaterEqual(len(TRACE['south']),20)
 def test_normalized_arclength_endpoints(self):
  for tile in ('west','south'):
   p=arc_positions(TRACE[tile]);self.assertAlmostEqual(p[0],0);self.assertAlmostEqual(p[-1],1)
   self.assertTrue(np.all(np.diff(p)>0))
   dst=target_at_source_progress(tile)
   self.assertEqual(dst[0],TARGET[tile][0]);self.assertEqual(dst[-1],TARGET[tile][-1])
 def test_reject_degenerate_trace(self):
  with self.assertRaisesRegex(ValueError,'degenerate'):arc_positions([[1,1],[1,1],[2,3]])
 def test_geometry_rejects_west_and_retains_south(self):
  # Corrected WEST source-road centerline needs >155px relocation.
  for tile in ('west','south'):
   dst=target_at_source_progress(tile)
   mx,my,*_=mapping(TRACE[tile],dst,sigma=170,spacing=1.25)
   qa=evaluate(mx,my,TRACE[tile],dst)
   self.assertEqual(mx.shape,NATIVE)
   self.assertEqual(qa['foldedFraction'],0)
   if tile=='west':
    self.assertGreater(qa['maxPairedAnchorDisplacementPx'],155)
    self.assertFalse(qa['necessaryGeometryPass'])
   else:
    self.assertLessEqual(qa['maxPairedAnchorDisplacementPx'],155)
    self.assertTrue(qa['necessaryGeometryPass'])
 def test_synthetic_road_transport_not_art_approval(self):
  for tile in ('west','south'):
   dst=target_at_source_progress(tile)
   mx,my,*_=mapping(TRACE[tile],dst,sigma=170,spacing=1.25)
   img=np.zeros((*NATIVE,3),np.uint8)
   cv2.polylines(img,[np.asarray(TRACE[tile],np.int32)],False,(255,255,255),20,cv2.LINE_AA)
   warp=cv2.remap(img,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
   _,q=paired_samples(TRACE[tile],dst,spacing=5)
   pixels=warp[np.clip(np.rint(q[:,1]).astype(int),0,1023),np.clip(np.rint(q[:,0]).astype(int),0,1535),0]
   self.assertGreater(float(np.mean(pixels>150)),.94)
 def test_sha_pin_rejects_unknown_source(self):
  with tempfile.TemporaryDirectory() as tmp:
   fake=Path(tmp)/'fake.png';fake.write_bytes(b'not a valid source')
   root=Path(__file__).resolve().parent
   atlas=root/'terrain-grid/v123-atlas.js'
   if not atlas.exists():atlas=root.parent/'terrain-grid/v123-atlas.js'
   with self.assertRaisesRegex(ValueError,'wrong original image SHA256'):
    process('south',fake,atlas,Path(tmp)/'out')

if __name__=='__main__':unittest.main()
