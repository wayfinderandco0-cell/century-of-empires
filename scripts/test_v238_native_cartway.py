#!/usr/bin/env python3
"""V238 native photographic cartway: synthetic positive/negative regression."""
import hashlib
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
import v238_bake_native_cartways as v238

class CartwayTests(unittest.TestCase):
    def setUp(self):
        self.road=v238.verify_graph()['west']
    def test_pinned_graph_and_distinct_sources(self):
        self.assertEqual(v238.verify_graph()['south'][0],[466,0])
        self.assertEqual(v238.verify_graph()['west'][-1],[275,550])
        self.assertNotEqual(v238.WEST_SHA256,v238.SOUTH_INFO['sha1'])
        self.assertEqual(v238.SOUTH_INFO['license'],'CC0 1.0')
        self.assertEqual(v238.commons_original_url(v238.SOUTH_INFO['filename']),
          'https://upload.wikimedia.org/wikipedia/commons/a/a8/Peaceful_Austrian_valley_%28Unsplash%29.jpg')
        self.assertEqual(v238.PIN,'09f04b4062e24fbacbb645307462cdddce2b2aa3')
    def test_meadow_bakes_only_on_immutable_corridor(self):
        # Deliberately uniform synthetic grass: verifies pixels and geometry,
        # NOT photographic quality or real-world terrain.
        src=Image.new('RGB',(1536,1024),(118,156,58))
        baked,review,metrics,open_fraction,passed=v238.bake_scene(src,self.road,'west')
        self.assertTrue(passed,metrics)
        self.assertGreater(open_fraction,.95)
        a=np.asarray(src);b=np.asarray(baked)
        self.assertTrue(np.array_equal(a[100:160,100:160],b[100:160,100:160]))
        self.assertFalse(np.array_equal(a[535:560,700:740],b[535:560,700:740]))
        self.assertEqual(baked.size,(1536,1024))
    def test_canopy_cannot_become_approved_cartway(self):
        src=Image.new('RGB',(1536,1024),(18,54,35))
        _,_,metrics,open_fraction,passed=v238.bake_scene(src,self.road,'west')
        self.assertFalse(passed)
        self.assertLess(open_fraction,.05)
        self.assertFalse(metrics['necessaryRoadGroundGate'])
    def test_wrong_dimensions_and_graph_tamper_rejected(self):
        with self.assertRaises(ValueError):
            v238.bake_cartway(Image.new('RGB',(1024,1024)),self.road)
        orig=v238.ROOT
        try:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);(root/'terrain-grid').mkdir()
                (root/'terrain-grid/v123-atlas.js').write_text('tampered')
                v238.ROOT=root
                with self.assertRaisesRegex(ValueError,'V123 immutable'):
                    v238.verify_graph()
        finally:v238.ROOT=orig
    def test_all_approval_flags_false(self):
        self.assertFalse(any(v238.FALSE.get(x) for x in (
            'sourceRegisteredToV123','historicalRoadsVerified','bridgeBanksVerified',
            'humanVisualApproval','physicalIPhoneApproved','productionApproved')))
if __name__=='__main__':unittest.main()
