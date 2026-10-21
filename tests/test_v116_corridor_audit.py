"""Regression tests for source-derived V115 geometry; not art verification."""
import importlib.util
import json
import math
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("corridor",ROOT/"scripts/audit_v116_corridor.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
MANIFEST=json.loads((ROOT/"terrain-v94/manifest.json").read_text())
SOURCE=json.loads((ROOT/"terrain-grid/v115-route-provenance.json").read_text())

class CorridorTests(unittest.TestCase):
    def test_source_provenance_is_explicit(self):
        self.assertEqual(SOURCE["source"]["githubBlobSha"],"9a8f44120c2f220abf434bed384f230cf6483296")
        self.assertEqual(SOURCE["forkIndex"],36)
        self.assertEqual(SOURCE["rawPath"][36],SOURCE["bridgePath"][36])
        self.assertEqual(SOURCE["bridgePath"][-1],[704,824])

    def test_audit_maps_to_one_parent_octagon_without_playable_claim(self):
        result=mod.audit(MANIFEST,SOURCE)
        self.assertEqual(result["candidateParentCells"],["r10-c09"])
        self.assertEqual(result["verifiedDeepZoomEligibleCells"],[])
        self.assertEqual(result["generatedV116PlayableAnnotations"],{})
        self.assertTrue(result["needsHierarchicalChildTiles"])
        self.assertLess(result["sourceArtFractionOfOneParentCell"],0.00005)
        self.assertEqual(result["routes"]["south"]["artPointCount"],43)
        self.assertEqual(result["routes"]["bridge"]["artPointCount"],56)

    def test_projection_matches_v115_art_anchor(self):
        result=mod.audit(MANIFEST,SOURCE)
        box=result["artBoxWorldPx"]
        x=box[0]+SOURCE["artAnchorPx"][0]/1100*box[2]
        y=box[1]+SOURCE["artAnchorPx"][1]/842*box[3]
        self.assertAlmostEqual(x,(11.451+14)*1448/63,places=7)
        self.assertAlmostEqual(y,(75-47.127)*1086/49,places=7)

    def test_intermediate_grid_cells_are_not_skipped(self):
        cells=mod.cells_for_segment([1,1],[1430,1000],1448,1086)
        self.assertIn((0,0),cells)
        self.assertIn((23,16),cells)
        self.assertGreater(len(cells),25)

    def test_out_of_atlas_segment_rejected(self):
        with self.assertRaises(ValueError):
            mod.cells_for_segment([-1,0],[10,10],1448,1086)

    def test_invalid_fork_is_rejected(self):
        altered=json.loads(json.dumps(SOURCE))
        altered["bridgePath"][36]=[1,1]
        with self.assertRaisesRegex(ValueError,"junction"):
            mod.audit(MANIFEST,altered)

    def test_fake_verified_route_is_rejected(self):
        altered=json.loads(json.dumps(SOURCE))
        altered["verification"]["farBankContinuationVerified"]=True
        with self.assertRaisesRegex(ValueError,"verification"):
            mod.audit(MANIFEST,altered)

    def test_out_of_image_point_rejected(self):
        altered=json.loads(json.dumps(SOURCE))
        altered["rawPath"][-1]=[1101,842]
        with self.assertRaisesRegex(ValueError,"bounds"):
            mod.audit(MANIFEST,altered)

if __name__=='__main__':
    unittest.main()
