#!/usr/bin/env python3
"""V239 original-photo source contract, graph preservation and fail-closed gates."""
import hashlib
import io
import unittest
from unittest.mock import patch
from PIL import Image
import v239_hinteregger_south as v239
import v238_bake_native_cartways as v238

class HintereggerTests(unittest.TestCase):
    def test_source_provenance_and_canonical_original(self):
        self.assertEqual(v239.SOURCE['author'],'Carsten Steger')
        self.assertEqual(v239.SOURCE['license'],'CC BY-SA 4.0')
        self.assertIsNone(v239.SOURCE['sha1']) # no false SHA approval
        self.assertEqual(v239.source_url(),
            'https://upload.wikimedia.org/wikipedia/commons/6/6c/Aerial_image_of_Hinteregger_Alm_%28view_from_the_southeast%29.jpg')
        self.assertFalse(v239.FLAGS['sourceRegisteredToV123'])
        self.assertFalse(v239.FLAGS['historicalRoadsVerified'])
        self.assertFalse(v239.FLAGS['bridgeBanksVerified'])
        self.assertFalse(v239.FLAGS['productionApproved'])

    def test_original_photo_dimensions_and_sha_mismatch_rejected(self):
        wrong=io.BytesIO()
        Image.new('RGB',(64,64),(120,155,80)).save(wrong,'JPEG')
        with self.assertRaisesRegex(ValueError,'dimensions mismatch'):
            v239.inspect_bytes(wrong.getvalue())
        with patch.dict(v239.SOURCE,{'dimensions':[64,64]}):
            image,sha=v239.inspect_bytes(wrong.getvalue())
            self.assertEqual(image.size,(64,64))
            self.assertEqual(sha,hashlib.sha1(wrong.getvalue()).hexdigest())
            with self.assertRaisesRegex(ValueError,'SHA1 changed'):
                v239.inspect_bytes(wrong.getvalue(),'0'*40)

    def test_v123_south_geometry_is_immutable(self):
        roads=v238.verify_graph()
        self.assertEqual(roads['south'][0],[466,0])
        self.assertEqual(roads['south'][-1],[1270,605])
        self.assertEqual(roads['west'][-1],[275,550])

    def test_no_forest_bake_can_be_promoted(self):
        roads=v238.verify_graph()
        image=Image.new('RGB',(1536,1024),(18,54,35))
        _,_,metrics,_,ok=v238.bake_scene(image,roads['south'],'south')
        self.assertFalse(ok)
        self.assertFalse(metrics['necessaryRoadGroundGate'])

if __name__=='__main__':
    unittest.main()
