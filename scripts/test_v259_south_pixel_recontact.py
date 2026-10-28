#!/usr/bin/env python3
"""Necessary geometry regression only. Not historical or visual acceptance."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v259_south_pixel_recontact import remap,verify_atlas,ROOT,TARGET,SOURCE
class TestV259(unittest.TestCase):
    def test_atlas(self):verify_atlas(ROOT/"terrain-grid/v123-atlas.js")
    def test_native_geometry(self):
        image=np.zeros((1024,1536,3),dtype=np.uint8)
        output,qa=remap(image)
        self.assertEqual(output.shape,image.shape)
        self.assertTrue(qa["necessaryGeometryPass"])
        self.assertEqual(qa["foldedFraction"],0)
        self.assertGreaterEqual(qa["sourcePixelCoverage"],.998)
        self.assertLessEqual(qa["maxAdditionalDisplacementPx"],40)
    def test_false_approval_flags(self):
        self.assertEqual(TARGET.shape,SOURCE.shape)
        _,qa=remap(np.zeros((1024,1536,3),dtype=np.uint8))
        for k in ("historicalRoadVerified","independentGeographicTiepointsVerified","bridgeBanksVerified","strictV203Passed","fourBrowserArtPassed","userVisualApproval","productionApproved"):
            self.assertIs(qa[k],False)
    def test_wrong_size(self):
        with self.assertRaisesRegex(ValueError,"1536x1024"):remap(np.zeros((10,10,3),dtype=np.uint8))
if __name__=="__main__":unittest.main()
