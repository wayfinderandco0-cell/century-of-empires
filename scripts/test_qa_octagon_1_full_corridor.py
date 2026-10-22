#!/usr/bin/env python3
"""Synthetic coverage and fail-closed tests; these do not certify road artwork."""
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_octagon_1_full_corridor import build_report, corridor_segments


def geometry():
    shared = [[616, 0]] + [[616, i * 20] for i in range(1, 36)] + [[437, 742]]
    approach = shared + [[600, 770], [699, 799]]
    south = shared + [[390, 780], [315, 842]]
    east = [[717, 794], [780, 769], [1100, 704]]
    return approach, east, south


def fake_editor(approach, east, south):
    import json
    return "\n".join(f"const {name}={json.dumps(value)};"
                     for name, value in zip(("APPROACH", "BASE_EAST", "SOUTH"),
                                            (approach, east, south)))


class FullCorridorTests(unittest.TestCase):
    def test_every_approach_and_south_edge_is_covered_once(self):
        approach, east, south = geometry()
        routes = corridor_segments(approach, east, south)
        self.assertEqual(len(routes), 4)
        self.assertEqual(routes["shared_north_to_fork"][-1], [437, 742])
        self.assertEqual(routes["fork_to_bridge_arrival"][0], [437, 742])
        self.assertEqual(routes["east_bank_candidate"][0], [699, 799])
        self.assertEqual(routes["south_branch_candidate"][-1], [315, 842])
        self.assertEqual(sum(len(routes[k]) - 1 for k in
                             ("shared_north_to_fork", "fork_to_bridge_arrival")),
                         len(approach) - 1)
        self.assertEqual(sum(len(routes[k]) - 1 for k in
                             ("shared_north_to_fork", "south_branch_candidate")),
                         len(south) - 1)

    def test_shared_approach_drift_is_rejected(self):
        a, e, s = geometry()
        s[17] = [615, 340]
        with self.assertRaisesRegex(ValueError, "shared approach"):
            corridor_segments(a, e, s)

    def test_changed_bridge_and_exit_are_rejected(self):
        a, e, s = geometry()
        a[-1] = [700, 799]
        with self.assertRaisesRegex(ValueError, "endpoints"):
            corridor_segments(a, e, s)
        a, e, s = geometry()
        e[-1] = [1099, 704]
        with self.assertRaisesRegex(ValueError, "endpoints"):
            corridor_segments(a, e, s)

    def test_zero_length_route_is_rejected(self):
        a, e, s = geometry()
        e.insert(1, e[0].copy())
        with self.assertRaisesRegex(ValueError, "zero-length"):
            corridor_segments(a, e, s)

    def test_report_covers_all_four_and_never_certifies(self):
        a, e, s = geometry()
        raw = io.BytesIO()
        Image.new("RGB", (1100, 842), (70, 100, 40)).save(raw, "JPEG")
        with patch("qa_octagon_1_full_corridor.verify_source_blob", return_value="synthetic-pin"):
            report = build_report(fake_editor(a, e, s), raw.getvalue())
        self.assertEqual(len(report["segments"]), 4)
        self.assertTrue(all(x["samples"] > 1 for x in report["segments"].values()))
        self.assertFalse(report["production_ready"])
        self.assertFalse(report["painted_road_verified"])
        self.assertFalse(report["bridge_far_bank_verified"])
        self.assertFalse(report["neighbor_connection_verified"])
        self.assertTrue(all("low_contrast_runs" in part for part in report["segments"].values()))
        self.assertTrue(any(part["low_contrast_runs"] for part in report["segments"].values()))
        self.assertGreater(report["unobservable_sample_total"], 0)
        self.assertFalse(report["all_cross_track_samples_observable"])
        self.assertTrue(any(part["unobservable_runs"] for part in report["segments"].values()))

    def test_wrong_source_fails_closed(self):
        a, e, s = geometry()
        with self.assertRaises(ValueError):
            build_report(fake_editor(a, e, s), b"not-the-pinned-jpeg")


if __name__ == "__main__":
    unittest.main()
