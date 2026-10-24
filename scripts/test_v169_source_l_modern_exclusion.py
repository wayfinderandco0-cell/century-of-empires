#!/usr/bin/env python3
"""V169 fail-closed synthetic tests; CI additionally audits all 18 real JPEGs."""
import copy
import unittest
from PIL import Image
import v169_source_l_modern_exclusion as v

def synthetic_source():
    im=Image.new("RGBA",v.SIZE,(52,110,76,255))
    # Unknown southwest quadrant must remain genuinely unobserved.
    im.paste((0,0,0,0),(0,512,768,1024))
    return im

class V169ModernExclusionTests(unittest.TestCase):
    def setUp(self):
        self.source=synthetic_source()
        self.mask=v.make_mask(self.source)

    def test_manual_observations_pinned(self):
        self.assertTrue(v.validate_observations())
        bad=list(v.MODERN_ROADS)
        bad[1]=(bad[1][0],bad[1][1],((768,559),(1400,900),(1535,387)))
        with self.assertRaisesRegex(ValueError,"changed without source review"):
            v.validate_observations(tuple(bad),v.DEVELOPED,v.DATE_STAMPS)

    def test_source_footprint_and_unknown_quadrant(self):
        self.assertEqual(self.mask.getpixel((100,700)),0)
        self.assertEqual(self.mask.getpixel((760,900)),0)
        self.assertEqual(self.mask.getpixel((770,700)),255)
        self.assertEqual(self.mask.getpixel((700,400)),255)
        self.assertEqual(self.mask.size,(1536,1024))

    def test_observed_paved_road_is_excluded(self):
        for pt in ((1065,483),(1298,299),(1495,393),
                   (1129,931),(1296,867),(88,18)):
            self.assertEqual(self.mask.getpixel(pt),0,pt)

    def test_visible_modern_roofs_excluded(self):
        for pt in ((1000,550),(1400,386),(1110,925),
                   (1450,862),(210,26),(410,35)):
            self.assertEqual(self.mask.getpixel(pt),0,pt)

    def test_observed_2023_labels_excluded(self):
        for pt in v.DATE_STAMPS:
            self.assertEqual(self.mask.getpixel(pt),0,pt)

    def test_no_unmasking_or_fabricated_pixels(self):
        before=self.source.tobytes()
        clean=v.clean_rgba(self.source,self.mask)
        self.assertEqual(self.source.tobytes(),before)
        self.assertEqual(clean.getpixel((100,700)),(0,0,0,0))
        self.assertEqual(clean.getpixel((1065,483)),(0,0,0,0))
        self.assertEqual(clean.getpixel((700,400)),(52,110,76,255))
        self.assertEqual(clean.getpixel((850,100)),(52,110,76,255))
        with self.assertRaisesRegex(ValueError,"unmasked"):
            v.clean_rgba(self.source,Image.new("L",v.SIZE,255))

    def test_period_study_only_changes_retained_color(self):
        study=v.muted_study(self.source,self.mask)
        self.assertEqual(study.getpixel((100,700)),(0,0,0,0))
        self.assertEqual(study.getpixel((1065,483)),(0,0,0,0))
        self.assertEqual(study.getpixel((700,400))[3],255)
        self.assertNotEqual(study.getpixel((700,400))[:3],
                            self.source.getpixel((700,400))[:3])
        self.assertEqual(study.getchannel("A").tobytes(),self.mask.tobytes())

    def test_all_three_source_sectors_have_real_exclusions(self):
        result=v.coverage(self.source,self.mask)
        self.assertEqual(set(result),set(v.SECTORS))
        for sector in result.values():
            self.assertEqual(sector["sourcePixels"],768*512)
            self.assertGreater(sector["excludedPixels"],0)
            self.assertGreater(sector["retainedPixels"],0)

    def test_reject_nonbinary_and_wrong_source(self):
        with self.assertRaisesRegex(ValueError,"invalid V168"):
            v.make_mask(Image.new("RGB",v.SIZE))
        wrong=Image.new("RGBA",v.SIZE,(0,0,0,255))
        with self.assertRaisesRegex(ValueError,"unknown/source"):
            v.make_mask(wrong)
        with self.assertRaisesRegex(ValueError,"nonbinary"):
            v.make_mask(Image.new("RGBA",v.SIZE,(0,0,0,128)))

    def test_report_flags_stay_unapproved(self):
        source_meta={"version":168,"provider":"basemap.at",
                     "mosaicSha256":"a"*64,
                     "mosaicBoundsLonLat":[11.5,47.12,11.53,47.14],
                     **v.NO_APPROVAL}
        report=v.expected_manifest(source_meta,self.source,self.mask)
        self.assertEqual(report["dateStampObservationCount"],12)
        self.assertEqual(report["sourceVersion"],168)
        self.assertTrue(all(report[k] is False for k in v.NO_APPROVAL))
        self.assertFalse(report["modernInfrastructureCleared"])
        self.assertFalse(report["allModernFeaturesDetected"])
        self.assertTrue(report["manualArtReviewRequired"])
        forged=copy.deepcopy(source_meta);forged["productionApproved"]=True
        with self.assertRaisesRegex(ValueError,"approval changed"):
            v.expected_manifest(forged,self.source,self.mask)

if __name__=="__main__":unittest.main()
