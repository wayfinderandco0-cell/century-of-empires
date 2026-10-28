"""V252 strict low-strain SOUTH experiment; no production approval."""
import unittest
import numpy as np
from v251_fictional_cartway_pair import arc_sample, SOURCE as V251_SOURCE
from v252_low_strain_south_candidate import (SOURCE_ROAD, TARGET_ROAD,
    continuation_length, remap_native_road, require_source)

class LowStrainSouthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image=np.zeros((1024,1536,3),dtype=np.uint8)
        cls.image[:,:,1]=120
        cls.candidate,cls.qa=remap_native_road(cls.image)

    def test_source_is_less_displaced_than_v251(self):
        a,_=arc_sample(SOURCE_ROAD,2048)
        b,_=arc_sample(TARGET_ROAD,2048)
        old,_=arc_sample(V251_SOURCE['south'],2048)
        self.assertLess(np.linalg.norm(a-b,axis=1).max(),40)
        self.assertGreater(np.linalg.norm(old-b,axis=1).max(),140)

    def test_geometric_strain_reduced(self):
        self.assertTrue(self.qa['necessaryLowStrainGeometryPass'])
        self.assertGreaterEqual(self.qa['minSampledJacobian'],0.8)
        self.assertLess(self.qa['annotatedLineP95ResidualPx'],1)
        self.assertGreaterEqual(self.qa['observedPixelCoverage'],0.997)

    def test_identity_preserves_pixels(self):
        p=[[466,0],[540,310],[930,510],[1270,605]]
        result,qa=remap_native_road(self.image,p,p)
        self.assertTrue(np.array_equal(result,self.image))
        self.assertTrue(qa['necessaryLowStrainGeometryPass'])

    def test_unsupported_road_extension_blocks_art(self):
        self.assertGreater(continuation_length(),140)
        self.assertFalse(self.qa['productionApproved'])
        self.assertFalse(self.qa['humanArtApproved'])
        self.assertFalse(self.qa['historical1780CartwayVerified'])
        self.assertFalse(self.qa['sourceGameNaturalTiepointsVerified'])

    def test_wrong_image_fails_closed(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'wrong.png';f.write_bytes(b'not the pinned source')
            with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):
                require_source(f)

    def test_invalid_geometry_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'Low-strain limit'):
            remap_native_road(self.image,[[500,0],[1000,600]],[[0,0],[1000,600]])
        with self.assertRaisesRegex(ValueError,'Unsupported native size'):
            remap_native_road(np.zeros((512,768,3),dtype=np.uint8))

if __name__=='__main__':unittest.main()
