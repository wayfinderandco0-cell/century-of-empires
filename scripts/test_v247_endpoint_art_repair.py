#!/usr/bin/env python3
"""V247 synthetic regression only; cannot establish human visual acceptance."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).parent))
from v247_endpoint_art_repair import prepare,road_mask

class EndpointArtRepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.image=self.root/"source.png"
        canvas=Image.new("RGB",(1536,1024),(68,106,62))
        d=ImageDraw.Draw(canvas)
        for y in range(0,1024,8):
            d.line([(0,y),(1535,y)],fill=(67+(y%7),103+(y%13),63+(y%9)))
        d.line([(0,525),(275,540),(500,535),(1000,520),(1535,478)],fill=(144,107,64),width=30)
        canvas.save(self.image)
        self.points=[[0,525],[130,531],[275,540],[500,535],[1000,520],[1535,478]]
        self.manifest={
          "originalSha256":hashlib.sha256(self.image.read_bytes()).hexdigest(),
          "sourceKind":"fictional-generated-art-study",
          "sourceAttribution":"Synthetic test; not game art",
          "annotationMethod":"manual-original-pixel-visible-road-trace",
          "fullVisibleRoadPoints":self.points,
          "playableStartIndex":2,"playableEndIndex":5}
    def test_changes_only_unsupported_area_and_never_promotes(self):
        out=self.root/"out"
        result=prepare(self.image,self.manifest,out)
        self.assertGreater(result["erasedPixels"],1000)
        self.assertEqual(result["changedOutsideErase"],0)
        for key in ("productionApproved","promotionEligible","historicalRoadsVerified","retouchingIsOriginalSource"):
            self.assertFalse(result[key])
        self.assertTrue((out/"survey-endpoint-review.jpg").exists())
        self.assertTrue((out/"erased-road-mask.png").exists())
        original=np.asarray(Image.open(self.image))
        changed=np.asarray(Image.open(out/"endpoint-repaired-ART-STUDY.png"))
        self.assertTrue(np.array_equal(original[400:450,700:800],changed[400:450,700:800]))
        self.assertTrue(np.array_equal(original[500:550,500:800],changed[500:550,500:800]))
    def test_wrong_hash_rejected(self):
        with self.assertRaisesRegex(ValueError,"SHA256"):
            prepare(self.image,dict(self.manifest,originalSha256="0"*64),self.root/"bad")
    def test_requires_independent_annotation(self):
        with self.assertRaisesRegex(ValueError,"independent"):
            prepare(self.image,dict(self.manifest,annotationMethod="V123-generated"),self.root/"bad")
    def test_refuses_photography_pretending_to_be_generated(self):
        with self.assertRaisesRegex(ValueError,"licensed photography"):
            prepare(self.image,dict(self.manifest,sourceKind="licensed-photography"),self.root/"bad")
    def test_bad_indices_rejected(self):
        with self.assertRaisesRegex(ValueError,"surveyed road"):
            prepare(self.image,dict(self.manifest,playableStartIndex=4,playableEndIndex=2),self.root/"bad")
    def test_invalid_coordinates_rejected(self):
        with self.assertRaisesRegex(ValueError,"bad source"):
            road_mask((1536,1024),[[0,5],[9999,10]])

if __name__=="__main__":
    unittest.main()
