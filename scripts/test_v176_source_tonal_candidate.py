#!/usr/bin/env python3
"""Synthetic tests. CI also regenerates and verifies real 18-JPEG source L."""
import copy
import unittest
from PIL import Image,ImageDraw
import v176_source_tonal_candidate as v

class V176Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=Image.new('RGBA',v.SIZE,(70,90,80,255))
        cls.mask=Image.new('L',v.SIZE,255)
        d=ImageDraw.Draw(cls.mask)
        d.rectangle((0,512,767,1023),fill=0)
        d.rectangle((1000,350,1030,380),fill=0)
        cls.study.putalpha(cls.mask)
        cls.study=Image.composite(cls.study,Image.new('RGBA',v.SIZE,(0,0,0,0)),cls.mask)
        cls.counts={k:cls.mask.crop(box).histogram()[255] for k,box in v.SECTORS.items()}
        cls.meta={"version":169,"sourceCrs":"EPSG:3857",
          "sourceLicense":"CC BY 4.0","requiredAttribution":"Datenquelle: basemap.at",
          "sourceSectorsAreNotGameOctagons":True,"modernInfrastructureCleared":False,
          "sourceMosaicSha256":"a"*64,"maskSha256":"b"*64,
          "referenceSha256":"c"*64,"studySha256":"d"*64,
          "sourceSectorCoverage":{k:{"retainedPixels":n} for k,n in cls.counts.items()},
          **{k:False for k in v.FALSE_FLAGS}}
        cls.lod={"version":174,"sourceMosaicSha256":"a"*64,
          "sourceMaskSha256":"b"*64,"sourceReferenceSha256":"c"*64,
          "blockGrid":[48,32],"tiers":[{"gameArtEligible":False,
          "playableRoadsEligible":False,"deepZoomEligible":False} for _ in range(4)],
          "sectorCoverage":{k:{"retainedPixels":n} for k,n in cls.counts.items()},
          "retainedPixelsByBlockRowMajor":[cls.mask.crop((x*32,y*32,x*32+32,y*32+32)).histogram()[255]
            for y in range(32) for x in range(48)]}
    def test_real_pixel_mask_is_preserved(self):
        v.validate_source(self.meta,self.lod,self.study,self.mask)
        out=v.tone(self.study)
        self.assertEqual(out.getchannel('A').tobytes(),self.mask.tobytes())
        self.assertEqual(out.getpixel((10,700)),(0,0,0,0))
        self.assertEqual(out.getpixel((1010,365)),(0,0,0,0))
        self.assertEqual(out.getpixel((100,200))[3],255)
        self.assertNotEqual(out.getpixel((100,200))[:3],self.study.getpixel((100,200))[:3])
    def test_metadata_never_approves_game_art(self):
        m=v.expected_manifest(self.meta,self.lod)
        self.assertFalse(m['gameArtEligible'])
        self.assertFalse(m['canTraverseSourceRoads'])
        self.assertFalse(m['productionApproved'])
        self.assertFalse(m['periodArtComplete'])
        self.assertFalse(m['v123RoadsGeoregistered'])
        self.assertTrue(m['noSpatialCopiesOrSynthesizedFeatures'])
    def test_reject_forged_approvals(self):
        for k in v.FALSE_FLAGS:
            m=copy.deepcopy(self.meta);m[k]=True
            with self.assertRaisesRegex(ValueError,'forged source approval'):
                v.validate_source(m,self.lod,self.study,self.mask)
    def test_reject_lod_game_eligibility(self):
        l=copy.deepcopy(self.lod);l['tiers'][2]['deepZoomEligible']=True
        with self.assertRaisesRegex(ValueError,'untrusted LOD'):
            v.validate_source(self.meta,l,self.study,self.mask)
    def test_reject_mask_fill(self):
        study=self.study.copy();study.putpixel((10,700),(1,2,3,255))
        with self.assertRaisesRegex(ValueError,'filled'):
            v.validate_source(self.meta,self.lod,study,self.mask)
    def test_reject_wrong_block_count(self):
        l=copy.deepcopy(self.lod);l['retainedPixelsByBlockRowMajor'][0]-=1
        with self.assertRaisesRegex(ValueError,'LOD pixel count'):
            v.validate_source(self.meta,l,self.study,self.mask)
    def test_reject_modern_infrastructure_claim(self):
        m=copy.deepcopy(self.meta);m['modernInfrastructureCleared']=True
        with self.assertRaisesRegex(ValueError,'false historic claim'):
            v.validate_source(m,self.lod,self.study,self.mask)
    def test_reject_nonbinary_alpha(self):
        mask=self.mask.copy();mask.putpixel((5,5),128)
        study=self.study.copy();study.putalpha(mask)
        with self.assertRaisesRegex(ValueError,'nonbinary'):
            v.validate_source(self.meta,self.lod,study,mask)
if __name__=='__main__':unittest.main()
