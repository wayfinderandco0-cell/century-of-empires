#!/usr/bin/env python3
"""Synthetic tests: V128 review suggestions do not approve real roads."""
import unittest
from PIL import Image, ImageDraw
import audit_v128_road_profiles as subject


class CrossSectionReviewTests(unittest.TestCase):
    def setUp(self):
        self.img = Image.new('RGB', (240, 180), (40, 110, 40))
        self.roads = {'west': [[35, 90], [105, 90]],
                      'south': [[105, 90], [105, 150]],
                      'bridge': [[105, 90], [125, 90], [175, 90], [205, 90]]}
        self.manifest = {'dimensions': {'width': 240, 'height': 180},
                         'art': {'path': 'synthetic'},
                         'movement': {'roads': self.roads,
                                      'primaryStoneBridgeEnds': [[125, 90], [175, 90]]}}

    def test_cross_section_tracks_perpendicular_offsets(self):
        ImageDraw.Draw(self.img).line([(35, 90), (205, 90)], fill=(180, 165, 130), width=11)
        sample = next(subject.previous.sample_polyline([[60, 90], [120, 90]]))
        profile = subject.cross_section(self.img, sample)
        self.assertEqual([p['offsetPx'] for p in profile], list(subject.OFFSETS))
        self.assertEqual(profile[3]['rgbDeltaFromCenter'], 0)
        self.assertGreater(profile[0]['rgbDeltaFromCenter'], 70)

    def test_out_of_bounds_cross_section_rejected(self):
        sample = {'point': (10, 10), 'tangent': (1, 0), 'arc': 5}
        self.assertIsNone(subject.cross_section(self.img, sample))

    def test_bridge_approaches_ranked_without_weak_contrast(self):
        ImageDraw.Draw(self.img).line([(35, 90), (205, 90)], fill=(180, 165, 130), width=11)
        points = subject.rank_route(self.img, 'bridge', self.roads['bridge'], self.manifest['movement']['primaryStoneBridgeEnds'])
        self.assertTrue(any('bridge_approach_review' in p['reviewReasons'] for p in points))
        self.assertTrue(all(len(p['crossSection']) == 7 for p in points))

    def test_terminal_review_without_inventing_neighbor_roads(self):
        west = subject.rank_route(self.img, 'west', self.roads['west'], [])
        south = subject.rank_route(self.img, 'south', self.roads['south'], [])
        self.assertTrue(any('unverified_west_termination' in p['reviewReasons'] for p in west))
        self.assertTrue(any('unverified_south_termination' in p['reviewReasons'] for p in south))

    def test_weak_unpainted_segment_gets_review(self):
        points = subject.rank_route(self.img, 'bridge', self.roads['bridge'], [[125, 90], [175, 90]])
        self.assertTrue(any('weak_center_vs_flank_contrast' in p['reviewReasons'] for p in points))

    def test_ranked_points_spaced_and_deterministic(self):
        a = subject.rank_route(self.img, 'bridge', self.roads['bridge'], [[125, 90], [175, 90]])
        b = subject.rank_route(self.img, 'bridge', self.roads['bridge'], [[125, 90], [175, 90]])
        self.assertEqual(a, b)
        self.assertTrue(all(y['arcPx']-x['arcPx'] >= 24 for x,y in zip(a, a[1:])))
        self.assertLessEqual(len(a), 8)

    def test_production_flags_fail_closed(self):
        report = subject.audit(self.img, self.manifest)
        self.assertEqual(report['version'], 128)
        for key in ('roadSurfaceClassified', 'historicalAccuracyVerified',
                    'pixelAlignmentVerified', 'bridgeCrossingVerified',
                    'neighborContinuationVerified', 'productionEnabled'):
            self.assertIs(report[key], False)
        self.assertEqual(report['reviewPointCount'], sum(len(v) for v in report['reviewProfiles'].values()))

    def test_invalid_limit_rejected(self):
        for limit in (0, -1, True, 1.2):
            with self.assertRaises(ValueError):
                subject.rank_route(self.img, 'west', self.roads['west'], [], limit=limit)


if __name__ == '__main__':
    unittest.main()
