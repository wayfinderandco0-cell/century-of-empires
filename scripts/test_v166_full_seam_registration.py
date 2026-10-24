#!/usr/bin/env python3
"""Synthetic negative cases only. None are evidence of Alpine geography."""
import copy
import json
import math
import unittest
from pathlib import Path

import v165_three_frame_registration as v165
import v166_full_seam_registration as v166
from test_v165_three_frame_registration import sample


def change_south_about_crossing(data, scale=1.0, degrees=0.0):
    anchor = (2002, 1024)
    source_anchor = (2402, 1524)
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    for row in data["corridors"]["southern_valley"]:
        dx = row["game"][0] - anchor[0]
        dy = row["game"][1] - anchor[1]
        row["source"] = [
            source_anchor[0] + scale * (c * dx - s * dy),
            source_anchor[1] + scale * (s * dx + c * dy),
        ]


class WholeBorderTests(unittest.TestCase):
    def test_perfect_shared_frame_passes_but_never_approves_game(self):
        result = v166.audit(sample())
        self.assertTrue(result["fullSharedBordersValidated"])
        self.assertEqual(len(result["fullBorderDiagnostics"]), 2)
        for item in result["fullBorderDiagnostics"].values():
            self.assertEqual(item["maxSourceBorderDriftPx"], 0)
            self.assertEqual(item["sampleCount"], 4)
        for key in ("gameRouteGeoregistered", "historicalRoadsVerified",
                    "bridgeBanksVerified", "periodArtComplete",
                    "threeOctagonsVisuallyApproved", "physicalIPhoneApproved",
                    "productionApproved"):
            self.assertIs(result[key], False)

    def test_real_unmatched_source_evidence_stays_blocked(self):
        p = Path(__file__).resolve().parents[1] / "terrain-grid/v163-unverified-landmark-evidence.json"
        result = v166.audit(json.loads(p.read_text()))
        self.assertFalse(result["fullSharedBordersValidated"])
        self.assertEqual(result["fullBorderDiagnostics"], {})
        self.assertFalse(result["productionApproved"])

    def test_actual_octagon_border_endpoints_and_road_anchors(self):
        self.assertEqual(v166.SHARED_EDGES, (
            ("western_pass", "matrei", (1536, 256), (1536, 768), (1536, 478)),
            ("matrei", "southern_valley", (1792, 1024), (2816, 1024), (2002, 1024)),
        ))
        for left, right, first, last, crossing in v166.SHARED_EDGES:
            for xy in (first, last, crossing):
                for tile in (left, right):
                    ox, oy = v165.ORIGINS[tile]
                    self.assertTrue(v165.inside_octagon((xy[0]-ox, xy[1]-oy)))

    def test_road_anchor_only_can_hide_1point5_degree_rotation(self):
        d = sample()
        change_south_about_crossing(d, degrees=1.5)
        self.assertTrue(v165.audit(d)["sharedSourceFrameCoherent"])
        with self.assertRaisesRegex(ValueError, "full-border source discontinuity"):
            v166.audit(d)

    def test_road_anchor_only_can_hide_one_percent_scale_drift(self):
        d = sample()
        change_south_about_crossing(d, scale=1.01)
        self.assertTrue(v165.audit(d)["sharedSourceFrameCoherent"])
        with self.assertRaisesRegex(ValueError, "full-border source discontinuity"):
            v166.audit(d)

    def test_source_raster_must_contain_full_projected_edge(self):
        d = sample()
        d["sourceFrame"]["width"] = 2800
        # Every synthetic landmark still lies within this raster.
        self.assertTrue(v165.audit(d)["sharedSourceFrameCoherent"])
        with self.assertRaisesRegex(ValueError, "projected border exits declared source frame"):
            v166.audit(d)

    def test_small_uniform_registration_difference_is_bounded(self):
        d = sample()
        for row in d["corridors"]["southern_valley"]:
            row["source"][0] += 1
        result = v166.audit(d)
        self.assertTrue(result["fullSharedBordersValidated"])
        self.assertLessEqual(
            result["fullBorderDiagnostics"]["matrei_to_southern_valley"]["maxSourceBorderDriftPx"], 1.0001)

    def test_missing_corridor_stays_blocked_not_implicitly_valid(self):
        d = sample()
        d["corridors"]["western_pass"] = []
        result = v166.audit(d)
        self.assertFalse(result["fullSharedBordersValidated"])

    def test_large_unmatched_holdout_still_rejected_upstream(self):
        d = sample()
        d["corridors"]["matrei"][2]["source"][1] += 60
        with self.assertRaisesRegex(ValueError, "holdout residual"):
            v166.audit(d)


if __name__ == "__main__":
    unittest.main()
