#!/usr/bin/env python3
"""V258 non-production regressions; never confuse geometry with art approval."""
import unittest,tempfile
from pathlib import Path
import numpy as np
from v258_south_road_recontact import (TRACE,SOUTH_ROAD_CENTER,SOUTH_HOLDOUT,
    south_holdout_report,process,PINS,check_atlas,verify_source,mapping,
    evaluate,target_at_source_progress)
from v257_replacement_west import TRACE as V257_TRACE,TARGET

class SouthRecontactTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=south_holdout_report(V257_TRACE['south'])
  cls.after=south_holdout_report(TRACE['south'])
 def test_real_midbend_regression_improves_unfitted_source_holdouts(self):
  self.assertGreater(self.before['p90Px'],25)
  self.assertLess(self.after['p90Px'],5)
  self.assertLess(self.after['medianPx'],3)
  self.assertGreater(self.before['p90Px']-self.after['p90Px'],20)
 def test_holdouts_not_used_as_fit_vertices(self):
  self.assertEqual(len(SOUTH_HOLDOUT),8)
  self.assertFalse(any(p in SOUTH_ROAD_CENTER for p in SOUTH_HOLDOUT.astype(int).tolist()))
  self.assertFalse(self.after['independentGeographicTiepointsVerified'])
 def test_south_native_geometry_gates_unchanged(self):
  dst=target_at_source_progress('south',TRACE['south'])
  mx,my,_,_=mapping(TRACE['south'],dst,sigma=170,spacing=1.25)
  q=evaluate(mx,my,TRACE['south'],dst)
  self.assertLess(q['maxPairedAnchorDisplacementPx'],155)
  self.assertGreater(q['minSampledJacobian'],.24)
  self.assertGreater(q['sourcePixelCoverage'],.997)
  self.assertEqual(q['foldedFraction'],0)
  self.assertTrue(q.get('necessaryGeometryPass',q.get('geometryPass',False)))
 def test_west_original_source_and_trace_preserved(self):
  self.assertEqual(TRACE['west'],V257_TRACE['west'])
  self.assertEqual(PINS['west'],'2f7b6171c8fa479a61d372a7027e98aa0296ece92e38fc8908bbf65c4d7300fa')
  self.assertNotEqual(PINS['west'],PINS['south'])
 def test_immutable_v123_hash_and_endpoints(self):
  check_atlas(Path(__file__).resolve().parent.parent/'terrain-grid/v123-atlas.js')
  self.assertEqual(TARGET['south'][0],[466,0])
  self.assertEqual(TARGET['south'][-1],[1270,605])
 def test_wrong_image_source_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'bad.png';f.write_bytes(b'wrong')
   with self.assertRaisesRegex(ValueError,'source SHA256 mismatch'):
    verify_source('south',f)
 def test_actual_pngs_optional_fail_closed(self):
  import os
  west=os.environ.get('V258_WEST_PNG');south=os.environ.get('V258_SOUTH_PNG')
  if not (west and south):self.skipTest('Original fictional PNGs not hosted in CI; real-art browser QA unverified')
  atlas=Path(__file__).resolve().parent.parent/'terrain-grid/v123-atlas.js'
  with tempfile.TemporaryDirectory() as d:
   for tile,src in [('west',west),('south',south)]:
    q=process(tile,src,atlas,d)
    self.assertTrue(q.get('necessaryGeometryPass',q.get('geometryPass',False)))
    self.assertFalse(q['productionApproved'])
    self.assertTrue((Path(d)/(tile+'-v258-road-review.jpg')).exists())

if __name__=='__main__':unittest.main()
