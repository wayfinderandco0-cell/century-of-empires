#!/usr/bin/env python3
"""V174 synthetic/negative source-coverage tests. Real 18-JPEG test runs in CI."""
import copy
import unittest
from PIL import Image, ImageDraw
import v174_source_l_lod as v

def mask_fixture():
    mask = Image.new("L", v.SIZE, 255)
    ImageDraw.Draw(mask).rectangle((0,512,767,1023), fill=0)
    ImageDraw.Draw(mask).rectangle((100,100,108,108), fill=0)
    ImageDraw.Draw(mask).rectangle((1000,600,1040,640), fill=0)
    return mask

def meta_fixture(mask):
    _, sectors = v.build_coverage(mask)
    return {
        "version": 169, "sourceVersion": 168,
        "sourceCrs": "EPSG:3857",
        "sourceMosaicSha256": "a"*64,
        "maskSha256": "b"*64,
        "referenceSha256": "c"*64,
        "sourceExtentLonLat": [11.5,47.1,11.6,47.2],
        "requiredAttribution": "Datenquelle: basemap.at",
        "sourceLicense": "CC BY 4.0",
        "sourceSectorCoverage": {
            k: {"retainedPixels": s["retainedPixels"]} for k,s in sectors.items()
        },
        **v.FLAGS,
    }

class V174CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mask = mask_fixture()
        cls.meta = meta_fixture(cls.mask)
        cls.report = v.make_manifest(cls.meta,cls.mask,"b"*64,"c"*64)

    def test_three_sectors_and_unobserved_southwest(self):
        self.assertEqual(v.sector_for_block(0,0),"source-west")
        self.assertEqual(v.sector_for_block(24,0),"source-center")
        self.assertEqual(v.sector_for_block(24,16),"source-south")
        self.assertIsNone(v.sector_for_block(0,16))
        self.assertEqual(len(self.report["retainedPixelsByBlockRowMajor"]),1536)
        self.assertEqual(self.report["retainedPixelsByBlockRowMajor"][16*48],0)

    def test_32px_blocks_exact_retained_count(self):
        grid=self.report["retainedPixelsByBlockRowMajor"]
        self.assertEqual(grid[0],1024)
        self.assertEqual(grid[3+3*48],1024-81)  # 9x9 observed exclusion
        self.assertEqual(grid[24+16*48],1024)
        self.assertEqual(sum(grid),sum(x["retainedPixels"] for x in
                                     self.report["sectorCoverage"].values()))

    def test_partial_block_cannot_claim_complete_material(self):
        self.assertEqual(v.block_class(0),"excluded-or-unknown")
        self.assertEqual(v.block_class(1024),"unreviewed-modern-source")
        self.assertEqual(v.block_class(1),"mixed-source-and-exclusion")
        self.assertEqual(v.block_class(1023),"mixed-source-and-exclusion")
        for bad in (-1,1025,2.5,True):
            with self.assertRaises(ValueError):v.block_class(bad)

    def test_all_four_game_tiers_remain_ineligible(self):
        self.assertEqual([t["name"] for t in self.report["tiers"]],list(v.TIERS))
        for tier in self.report["tiers"]:
            self.assertTrue(tier["modernSourceInspectionOnly"])
            self.assertFalse(tier["gameArtEligible"])
            self.assertFalse(tier["playableRoadsEligible"])
            self.assertFalse(tier["deepZoomEligible"])
        self.assertFalse(self.report["productionApproved"])
        self.assertFalse(self.report["gameTerrainEligible"])
        self.assertFalse(self.report["sourceToV123TransformVerified"])

    def test_preview_shows_unknown_partial_retained(self):
        preview=v.block_preview(self.report["retainedPixelsByBlockRowMajor"])
        self.assertEqual(preview.size,(48,32))
        self.assertEqual(preview.getpixel((0,20)),0)
        self.assertEqual(preview.getpixel((3,3)),128)
        self.assertEqual(preview.getpixel((1,1)),255)

    def test_forged_approval_and_mismatched_source_rejected(self):
        forged=copy.deepcopy(self.meta);forged["productionApproved"]=True
        with self.assertRaisesRegex(ValueError,"forged source approval"):
            v.make_manifest(forged,self.mask,"b"*64,"c"*64)
        forged=copy.deepcopy(self.meta);forged["sourceSectorCoverage"]["source-west"]["retainedPixels"]+=1
        with self.assertRaisesRegex(ValueError,"coverage not bound"):
            v.make_manifest(forged,self.mask,"b"*64,"c"*64)
        with self.assertRaisesRegex(ValueError,"identity"):
            v.make_manifest(self.meta,self.mask,"x"*64,"c"*64)

    def test_missing_unknown_quadrant_and_nonbinary_alpha_rejected(self):
        changed=self.mask.copy();changed.putpixel((5,700),255)
        with self.assertRaisesRegex(ValueError,"unobserved southwest"):
            v.build_coverage(changed)
        changed=self.mask.copy();changed.putpixel((5,5),128)
        with self.assertRaisesRegex(ValueError,"nonbinary"):
            v.build_coverage(changed)

    def test_block_bounds_and_preview_tampering_rejected(self):
        for col,row in ((-1,0),(48,0),(0,32),(1.5,1)):
            with self.assertRaisesRegex(ValueError,"invalid block"):
                v.sector_for_block(col,row)
        with self.assertRaisesRegex(ValueError,"incomplete"):
            v.block_preview([1024]*10)

if __name__=="__main__":
    unittest.main()
