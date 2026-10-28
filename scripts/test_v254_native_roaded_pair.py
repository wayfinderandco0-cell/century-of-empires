#!/usr/bin/env python3
"""V254 regression: exact V123 graph and fail-closed fictional raster geometry."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from v251_fictional_cartway_pair import require_immutable_atlas, warp
from v254_native_roaded_pair import PINNED,SOURCE,TARGET,load_original

class NativePair(unittest.TestCase):
    def test_immutable_v123(self):
        require_immutable_atlas(ROOT/"terrain-grid/v123-atlas.js")
        self.assertEqual(TARGET["west"][0],[275,550])
        self.assertEqual(TARGET["west"][-1],[1536,478])
        self.assertEqual(TARGET["south"][0],[466,0])
        self.assertEqual(TARGET["south"][-1],[1270,605])
    def test_distinct_pinned_sources_and_endpoints(self):
        self.assertNotEqual(PINNED["west"],PINNED["south"])
        self.assertEqual(SOURCE["west"][0][0],275)
        self.assertEqual(SOURCE["west"][-1][0],1536)
        self.assertEqual(SOURCE["south"][0][1],0)
        self.assertLess(SOURCE["south"][-1][0],1536)
    def test_fail_closed_wrong_source_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"not-original.png"
            p.write_bytes(b"not the pinned source")
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                load_original(p,"south")
    def test_two_real_size_warp_geometry(self):
        # Synthetic pixels only: verifies transform mathematics, NOT image realism.
        image=np.zeros((1024,1536,3),dtype=np.uint8)
        for tile,sigma in (("west",160),("south",210)):
            out,m=warp(image,SOURCE[tile],TARGET[tile],sigma=sigma,
                       max_disp=155,top_fade=False)
            self.assertEqual(out.shape,image.shape)
            self.assertTrue(m["v245StrictGeometryPass"],(tile,m))
            self.assertEqual(m["foldedSampleFraction"],0)
            self.assertFalse(m["sourceRegisteredToV123"])
            self.assertFalse(m["humanArtApproved"])
            self.assertFalse(m["productionApproved"])
    def test_reject_excessive_displacement(self):
        image=np.zeros((1024,1536,3),dtype=np.uint8)
        with self.assertRaisesRegex(ValueError,"max displacement"):
            warp(image,[[0,0],[100,0]],[[500,0],[600,0]],max_disp=155)

if __name__=="__main__":unittest.main()
