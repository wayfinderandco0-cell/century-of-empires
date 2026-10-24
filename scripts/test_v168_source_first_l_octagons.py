#!/usr/bin/env python3
"""V168 real-geographic L topology and fail-closed source-pixel tests."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import v168_source_first_l_octagons as v

class SourceFirstLTests(unittest.TestCase):
    def setUp(self):
        self.manifest=v.plan({'version':102,'boundsLonLat':[11.43,47.075,11.625,47.19]})
    def test_exactly_eighteen_unique_xyz_sources(self):
        self.assertEqual(len(self.manifest['samples']),18)
        self.assertEqual(len({tuple(r['tileXYZ']) for r in self.manifest['samples']}),18)
        self.assertTrue(v.validate_manifest(self.manifest))
    def test_correct_L_source_sectors(self):
        self.assertEqual({r['sourceSector'] for r in self.manifest['samples']},set(v.SECTORS))
        self.assertEqual([sum(r['sourceSector']==name for r in self.manifest['samples'])
                          for name in v.SECTORS],[6,6,6])
        self.assertEqual(self.manifest['unobservedSouthwestBoundsPixels'],[0,512,768,1024])
    def test_geo_tile_bounds_roundtrip(self):
        for r in self.manifest['samples']:
            west,south,east,north=r['boundsLonLat']
            self.assertEqual(v.xyz((west+east)/2,(south+north)/2,v.ZOOM),tuple(r['tileXYZ'][:2]))
    def test_shared_clipped_octagon_edges(self):
        west,center,south=[x['octagonPolygon'] for x in self.manifest['sourceSectors']]
        self.assertEqual([p for p in west if p[0]==768],[[768,128],[768,384]])
        self.assertEqual([p for p in center if p[0]==768],[[768,384],[768,128]])
        self.assertEqual([p for p in center if p[1]==512],[[1408,512],[896,512]])
        self.assertEqual([p for p in south if p[1]==512],[[896,512],[1408,512]])
    def test_outside_navis_bounds_fails(self):
        with self.assertRaisesRegex(ValueError,'exceeds'):
            v.plan({'version':102,'boundsLonLat':[11.519,47.129,11.521,47.131]})
    def test_reject_missing_or_duplicated_source(self):
        bad=copy.deepcopy(self.manifest);bad['samples'].pop()
        with self.assertRaisesRegex(ValueError,'missing or duplicated'):
            v.validate_manifest(bad)
        bad=copy.deepcopy(self.manifest);bad['samples'][3]['tileXYZ']=bad['samples'][2]['tileXYZ']
        with self.assertRaisesRegex(ValueError,'coordinates changed'):
            v.validate_manifest(bad)
    def test_reject_wrong_sector_and_approval(self):
        bad=copy.deepcopy(self.manifest);bad['samples'][0]['sourceSector']='source-south'
        with self.assertRaisesRegex(ValueError,'coordinates changed'):
            v.validate_manifest(bad)
        bad=copy.deepcopy(self.manifest);bad['productionApproved']=True
        with self.assertRaisesRegex(ValueError,'forged approval'):
            v.validate_manifest(bad)
    def test_source_pixels_are_exact_and_unknown_is_transparent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);m=copy.deepcopy(self.manifest)
            # Synthetic image gradients cross all original tile boundaries.
            for r in m['samples']:
                im=Image.new('RGB',(256,256));pix=im.load()
                for y in range(256):
                    for x in range(256):
                        xx=r['col']*256+x;yy=r['row']*256+y
                        pix[x,y]=(xx//8%256,yy//8%256,(xx+yy)//16%256)
                name=r['name']+'.jpeg';im.save(p/name,quality=95)
                r['imageFile']=name;r['sha256']=v.sha(p/name)
            result=v.produce(m,p)
            self.assertTrue(v.verify(p))
            self.assertEqual(len(result['sourceImageSeamDiagnostics']),2)
            with Image.open(p/'modern-source-L.png') as im:
                self.assertEqual(im.getpixel((100,700))[3],0)
                self.assertEqual(im.getpixel((900,700))[3],255)
                self.assertEqual(im.size,v.SIZE)
            # Missing/tampered original source cannot be replaced by filled terrain.
            (p/'r0c0.jpeg').write_bytes(b'forged')
            with self.assertRaisesRegex(ValueError,'tampered'):
                v.verify(p)
    def test_no_unapproved_game_claims(self):
        for k in v.NO_APPROVAL:self.assertIs(self.manifest[k],False)
        self.assertIn('NOT game art',self.manifest['purpose'])

if __name__=='__main__':unittest.main()
