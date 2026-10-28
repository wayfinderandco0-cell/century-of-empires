"""V251 isolated whole-scene road registration controls. No art approval."""
import unittest
import numpy as np
from v251_fictional_cartway_pair import arc_sample, warp, SOURCE, TARGET

class SceneWarpTests(unittest.TestCase):
    def setUp(self):
        self.image=np.zeros((1024,1536,3),dtype=np.uint8)
        self.image[:,:,1]=100

    def test_road_geometry_finite(self):
        for tile in ("west","south"):
            a,la=arc_sample(SOURCE[tile])
            b,lb=arc_sample(TARGET[tile])
            self.assertEqual(a.shape,(1024,2))
            self.assertGreater(la,800)
            self.assertGreater(lb,1000)

    def test_identity_preserves_source_pixels(self):
        path=[[300,300],[600,450],[900,500]]
        out,qa=warp(self.image,path,path)
        self.assertTrue(np.array_equal(out,self.image))
        self.assertTrue(qa["v245StrictGeometryPass"])

    def test_large_displacement_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"max displacement"):
            warp(self.image,[[500,0],[1000,600]],[[0,0],[1000,600]])

    def test_degenerate_road_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"degenerate"):
            arc_sample([[1,1],[1,1]])

    def test_west_fails_existing_155px_gate(self):
        _,qa=warp(self.image,SOURCE["west"],TARGET["west"],top_fade=True)
        self.assertFalse(qa["v245StrictGeometryPass"])
        self.assertFalse(qa["productionApproved"])
        self.assertEqual(qa["foldedSampleFraction"],0)

    def test_south_is_geometry_only_not_art_approval(self):
        _,qa=warp(self.image,SOURCE["south"],TARGET["south"])
        self.assertTrue(qa["v245StrictGeometryPass"])
        self.assertFalse(qa["originalPixelAnnotationIndependentlyVerified"])
        self.assertFalse(qa["humanArtApproved"])
        self.assertFalse(qa["productionApproved"])

if __name__=="__main__":
    unittest.main()
