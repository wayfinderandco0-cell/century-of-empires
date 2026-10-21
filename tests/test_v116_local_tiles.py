"""Child LOD tile tests. Run: python -m unittest discover -s tests -p test_v116_local_tiles.py -v"""
import importlib.util
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('local_tiles',ROOT/'scripts/build_v116_local_tiles.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
MANIFEST=json.loads((ROOT/'terrain-v94/manifest.json').read_text())
SOURCE=json.loads((ROOT/'terrain-grid/v115-route-provenance.json').read_text())


class LocalTileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=m.make_local_index(MANIFEST,SOURCE)

    def tile(self,r,c):
        return self.index['tiles'][r*8+c]

    def test_48_tiles_with_unique_ids(self):
        i=self.index
        self.assertEqual(i['grid'],{'columns':8,'rows':6,'tileCount':48})
        self.assertEqual(len({t['id'] for t in i['tiles']}),48)

    def test_shared_image_edges_no_seams(self):
        for r in range(6):
            for c in range(8):
                a=self.tile(r,c)['imageCropPx']
                if c<7: self.assertEqual(a[2],self.tile(r,c+1)['imageCropPx'][0])
                if r<5: self.assertEqual(a[3],self.tile(r+1,c)['imageCropPx'][1])
        self.assertEqual(self.tile(0,0)['imageCropPx'][:2],[0,0])
        self.assertEqual(self.tile(5,7)['imageCropPx'][2:],[1100,842])
        self.assertTrue(all(type(edge) is int for t in self.index['tiles']
                            for edge in t['imageCropPx']))

    def test_shared_world_edges_no_seams(self):
        for r in range(6):
            for c in range(8):
                a=self.tile(r,c)['worldRectPx']
                if c<7: self.assertAlmostEqual(a[2],self.tile(r,c+1)['worldRectPx'][0],places=12)
                if r<5: self.assertAlmostEqual(a[3],self.tile(r+1,c)['worldRectPx'][1],places=12)

    def test_all_tiles_contained_in_single_parent(self):
        self.assertEqual(self.index['parentOctagonCandidates'],['r10-c09'])
        self.assertTrue(all(t['parentOctagonCandidates']==['r10-c09'] for t in self.index['tiles']))

    def test_art_anchor_matches_v94_world_and_lonlat(self):
        lon,lat=SOURCE['matreiLonLat']
        west,south,east,north=MANIFEST['extent']
        width,height=MANIFEST['gameSize']
        expected=[(lon-west)*width/(east-west),(north-lat)*height/(north-south)]
        for a,b in zip(self.index['anchorWorldPx'],expected):
            self.assertAlmostEqual(a,b,places=12)
        artx,arty=SOURCE['artAnchorPx']
        x0,y0,x1,y1=self.index['artBoxWorldPx']
        self.assertAlmostEqual(x0+artx/1100*(x1-x0),expected[0],places=12)
        self.assertAlmostEqual(y0+arty/842*(y1-y0),expected[1],places=12)

    def test_lonlat_world_projection_same_as_overview(self):
        west,south,east,north=MANIFEST['extent']
        width,height=MANIFEST['gameSize']
        for t in self.index['tiles']:
            for pos,ll in [(t['worldRectPx'][:2],t['lonLatNW']),
                           (t['worldRectPx'][2:],t['lonLatSE'])]:
                self.assertAlmostEqual(ll[0],west+pos[0]*(east-west)/width,places=11)
                self.assertAlmostEqual(ll[1],north-pos[1]*(north-south)/height,places=11)

    def test_prototype_route_candidates_never_grant_access(self):
        i=self.index
        self.assertGreater(len(i['routeCandidateTileIds']['south']),0)
        self.assertGreater(len(i['routeCandidateTileIds']['bridge']),0)
        self.assertTrue(all(not t['traversable'] and not t['deepZoomEligible']
                            and not t['conquerable'] and not t['paintedRoadVerified']
                            for t in i['tiles']))
        self.assertEqual(i['verification']['playableRouteTiles'],0)

    def test_route_segments_have_tile_coverage(self):
        for name,key in [('south','rawPath'),('bridge','bridgePath')]:
            ids=set(self.index['routeCandidateTileIds'][name])
            for a,b in zip(SOURCE[key],SOURCE[key][1:]):
                self.assertTrue(any(t['id'] in ids and
                                    m.intersects_segment_rect(a,b,t['imageCropPx'])
                                    for t in self.index['tiles']))

    def test_clipping_handles_crossing_touch_and_outside(self):
        rect=[0,0,10,10]
        self.assertTrue(m.intersects_segment_rect([-2,5],[12,5],rect))
        self.assertTrue(m.intersects_segment_rect([-1,-1],[0,0],rect))
        self.assertTrue(m.intersects_segment_rect([5,5],[5,5],rect))
        self.assertFalse(m.intersects_segment_rect([-1,11],[11,11],rect))
        self.assertFalse(m.intersects_segment_rect([-1,-1],[-1,-1],rect))

    def test_rejects_false_verification_and_bad_geometry(self):
        s=json.loads(json.dumps(SOURCE))
        s['verification']['farBankContinuationVerified']=True
        with self.assertRaisesRegex(ValueError,'unverified'):
            m.make_local_index(MANIFEST,s)
        s=json.loads(json.dumps(SOURCE))
        s['rawPath'][0]=[float('nan'),0]
        with self.assertRaisesRegex(ValueError,'Invalid south'):
            m.make_local_index(MANIFEST,s)
        with self.assertRaisesRegex(ValueError,'grid dimensions'):
            m.make_local_index(MANIFEST,SOURCE,cols=0)

    def test_deterministic_output(self):
        self.assertEqual(m.make_local_index(MANIFEST,SOURCE),m.make_local_index(MANIFEST,SOURCE))


if __name__=='__main__':unittest.main()
