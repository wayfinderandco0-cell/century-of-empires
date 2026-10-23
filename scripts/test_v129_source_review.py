#!/usr/bin/env python3
"""Synthetic tests for fail-closed raw source review exports."""
import io
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
import export_v129_source_review as subject


class SourceReviewTests(unittest.TestCase):
    def setUp(self):
        self.image=Image.new('RGB',(320,240),(55,125,60))
        ImageDraw.Draw(self.image).line([(40,120),(280,120)],fill=(175,155,110),width=11)
        out=io.BytesIO()
        self.image.save(out,format='PNG')
        self.content=out.getvalue()
        self.manifest={'dimensions':{'width':320,'height':240},
                       'art':{'path':'synthetic.png','gitBlobSha':subject.git_blob_sha(self.content)},
                       'movement':{'roads':{'west':[[40,120],[110,120]],
                                            'bridge':[[110,120],[140,120],[220,120],[280,120]]},
                                   'primaryStoneBridgeEnds':[[140,120],[220,120]]}}

    def test_source_pin_rejects_different_image_bytes(self):
        subject.verify_source(self.content,self.manifest)
        with self.assertRaisesRegex(ValueError,'differs'):
            subject.verify_source(self.content+b'changed',self.manifest)

    def test_crop_contains_review_point_at_edges(self):
        for point in ([0,0],[319,239],[150,100]):
            l,t,r,b=subject.crop_box(point,160,self.image.size)
            self.assertTrue(l<=point[0]<r and t<=point[1]<b)
            self.assertEqual((r-l,b-t),(160,160))

    def test_invalid_coordinates_fail_closed(self):
        for point in ([320,50],[-1,20],[float('nan'),10],[True,4],[5]):
            with self.assertRaises(ValueError):
                subject.crop_box(point,160,self.image.size)

    def test_raw_crop_identical_to_source(self):
        review={'point':[100,120]}
        raw,marked,box=subject.make_pair(self.image,review)
        self.assertEqual(list(raw.getdata()),list(self.image.crop(box).getdata()))
        self.assertNotEqual(list(raw.getdata()),list(marked.getdata()))
        self.assertEqual(self.image.getpixel((100,120)),(175,155,110))

    def test_export_deterministic_and_never_certifies(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            ra=subject.export(self.image,self.manifest,self.content,a)
            rb=subject.export(self.image,self.manifest,self.content,b)
            self.assertEqual(ra,rb)
            self.assertGreater(ra['totalReviewSamples'],0)
            for key in ('historicalAccuracyVerified','roadSurfaceClassified',
                        'pixelAlignmentVerified','bridgeCrossingVerified',
                        'neighborContinuationVerified','productionEnabled'):
                self.assertIs(ra[key],False)
            self.assertEqual((Path(a)/'v129-review-index.json').read_bytes(),
                             (Path(b)/'v129-review-index.json').read_bytes())
            for route in ra['routes'].values():
                if route['image']:
                    self.assertEqual((Path(a)/route['image']).read_bytes(),
                                     (Path(b)/route['image']).read_bytes())

    def test_manifest_dimension_mismatch_rejected(self):
        self.manifest['dimensions']['width']=321
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'dimensions'):
                subject.export(self.image,self.manifest,self.content,d)

    def test_unsafe_route_name_rejected(self):
        self.manifest['movement']['roads']['../escape']=[[40,120],[100,120]]
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'Unsafe'):
                subject.export(self.image,self.manifest,self.content,d)


if __name__=='__main__':
    unittest.main()
