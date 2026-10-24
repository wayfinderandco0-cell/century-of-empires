#!/usr/bin/env python3
"""Synthetic positive/negative tests for V171 screenshot detail gate."""
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_v171_neighbor_detail as gate

class DetailGateTests(unittest.TestCase):
    def test_thresholds_are_unchanged_from_v140(self):
        self.assertEqual(gate.MIN_RELATIVE_GRADIENT, .35)
        self.assertEqual(gate.MIN_RELATIVE_STRONG_EDGES, .25)
    def test_flat_neighbor_is_rejected(self):
        scores={'matrei':{'mean_luma_gradient':10.,'strong_edge_fraction':.2},
                'west':{'mean_luma_gradient':2.,'strong_edge_fraction':.01},
                'south':{'mean_luma_gradient':5.,'strong_edge_fraction':.1}}
        self.assertFalse(gate.assess(scores)['west']['passes_minimum_detail'])
        self.assertTrue(gate.assess(scores)['south']['passes_minimum_detail'])
    def test_exact_boundary_passes(self):
        scores={'matrei':{'mean_luma_gradient':10.,'strong_edge_fraction':.2},
                'west':{'mean_luma_gradient':3.5,'strong_edge_fraction':.05},
                'south':{'mean_luma_gradient':10.,'strong_edge_fraction':.2}}
        self.assertTrue(all(v['passes_minimum_detail'] for v in gate.assess(scores).values()))
    def test_missing_capture_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            result=gate.audit(Path(d))
            self.assertFalse(result['passed'])
            self.assertEqual(len(result['screenshots_missing']), 12)
            self.assertFalse(result['productionApproved'])
    def test_all_four_configurations_required(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for e in gate.ENGINES:
                for o in gate.ORIENTATIONS:
                    for name in ('opening','west-terrain','south-terrain'):
                        im=Image.new('RGB',(80,80))
                        px=im.load()
                        for y in range(80):
                            for x in range(80):
                                v=255 if (x+y)%2 else 0
                                px[x,y]=(v,v,v)
                        im.save(p/f'{e}-{o}-{name}.png')
            self.assertTrue(gate.audit(p)['passed'])
            (p/'webkit-landscape-west-terrain.png').unlink()
            self.assertFalse(gate.audit(p)['passed'])
    def test_small_image_rejected(self):
        with self.assertRaises(ValueError):gate.detail_score(Image.new('RGB',(8,8)))

if __name__ == '__main__':unittest.main()
