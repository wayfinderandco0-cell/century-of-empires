#!/usr/bin/env python3
"""V209 fail-closed tests. All populated matches below are SYNTHETIC, not real Alpine landmarks."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import v209_landmark_tiepoint_intake as reg

EMPTY = {
    "schemaVersion": 209, "sourceSite": "forest", "humanVisualApproval": False,
    "matches": {"west": [], "matrei": [], "south": []},
}
POINTS = {
    "west": [(600, 400), (820, 400), (700, 560), (760, 600)],
    "matrei": [(2100, 400), (2320, 400), (2200, 560), (2260, 600)],
    "south": [(2100, 1400), (2320, 1400), (2200, 1560), (2260, 1600)],
}


def synthetic():
    data = copy.deepcopy(EMPTY)
    for cell, points in POINTS.items():
        for i, (x, y) in enumerate(points):
            data["matches"][cell].append({
                "id": f"synthetic-{cell}-{i}",
                "role": "control" if i < 2 else "holdout",
                "feature": "bedrock_outcrop",
                "gameWorldXY": [x, y],
                "sourceContactXY": [round(0.35 * x - 12.8, 6), round(0.35 * y + 32, 6)],
                "gameEvidenceUrl": f"https://github.com/wayfinderandco0-cell/century-of-empires/issues/9#synthetic-game-{cell}-{i}",
                "sourceEvidenceUrl": f"https://github.com/wayfinderandco0-cell/century-of-empires/issues/9#synthetic-source-{cell}-{i}",
                "reviewedBy": "synthetic-test-only",
            })
    return data


class LandmarkIntakeTests(unittest.TestCase):
    def test_real_manifest_has_no_claimed_landmarks(self):
        manifest = json.loads((reg.ROOT / "terrain-grid/v209-unverified-tiepoints.json").read_text())
        self.assertEqual(manifest, EMPTY)
        result = reg.audit(manifest)
        self.assertFalse(result["allThreeCandidateFits"])
        self.assertEqual(result["registrationStatus"], "BLOCKED_MISSING_REAL_TIEPOINTS")
        self.assertEqual(set(result["findings"]), set(reg.CELLS))
        self.assertTrue(all(not v["candidateFit"] for v in result["findings"].values()))
        self.assertTrue(all(result[k] is False for k in reg.FALSE_FLAGS))

    def test_actual_v123_south_octagon_not_truncated_at_y1024(self):
        self.assertTrue(reg.inside_polygon((2300, 1500), reg.frames.polygon((1536, 1024))))
        self.assertFalse(reg.inside_polygon((1537, 1025), reg.frames.polygon((1536, 1024))))
        self.assertTrue(reg.inside_polygon((1536 + 256, 1024), reg.frames.polygon((1536, 1024))))

    def test_synthetic_four_point_fit_all_three_never_approves(self):
        report = reg.audit(synthetic())
        self.assertTrue(report["allThreeCandidateFits"])
        self.assertEqual(report["registrationStatus"], "MATHEMATICAL_CANDIDATE_ONLY_NOT_APPROVED")
        self.assertEqual(report["gameGeometryPinnedTo"], reg.source.PINNED)
        self.assertTrue(all(v["maxHoldoutResidualSourcePixels"] == 0
                            for v in report["findings"].values()))
        self.assertTrue(all(v["gameToModernSourceSimilarity"][:2] == [0.35, 0]
                            for v in report["findings"].values()))
        self.assertTrue(all(report[k] is False for k in reg.FALSE_FLAGS))

    def test_missing_one_corridor_blocks_all(self):
        data = synthetic()
        data["matches"]["south"] = []
        self.assertFalse(reg.audit(data)["allThreeCandidateFits"])

    def test_clipped_octagon_corner_is_not_landmark(self):
        data = synthetic()
        data["matches"]["west"][0]["gameWorldXY"] = [1, 1]
        with self.assertRaisesRegex(ValueError, "outside clipped"):
            reg.audit(data)

    def test_source_landmark_must_be_in_matching_native_panel(self):
        data = synthetic()
        data["matches"]["west"][0]["sourceContactXY"] = [900, 100]
        with self.assertRaisesRegex(ValueError, "outside native panel"):
            reg.audit(data)

    def test_holdout_residual_and_collinearity_fail(self):
        data = synthetic()
        data["matches"]["matrei"][2]["sourceContactXY"][0] += 20
        with self.assertRaisesRegex(ValueError, "holdout residual"):
            reg.audit(data)
        data = synthetic()
        data["matches"]["matrei"][2]["gameWorldXY"] = [2210, 400]
        with self.assertRaisesRegex(ValueError, "collinear"):
            reg.audit(data)

    def test_bad_evidence_duplicate_and_non_natural_feature_fail(self):
        for key, val in (
            ("gameEvidenceUrl", "https://example.com/not-real"),
            ("reviewedBy", ""),
            ("feature", "modern_highway"),
        ):
            data = synthetic()
            data["matches"]["west"][0][key] = val
            with self.assertRaises(ValueError, key):
                reg.audit(data)
        data = synthetic()
        data["matches"]["south"][0]["sourceEvidenceUrl"] = data["matches"]["west"][0]["sourceEvidenceUrl"]
        with self.assertRaisesRegex(ValueError, "reused evidence"):
            reg.audit(data)

    def test_cross_cell_geography_must_agree(self):
        data = synthetic()
        for row in data["matches"]["south"]:
            row["sourceContactXY"][0] += 30
        with self.assertRaisesRegex(ValueError, "disagree"):
            reg.audit(data)

    def test_never_accept_fake_approval_or_extra_cell(self):
        data = synthetic()
        data["humanVisualApproval"] = True
        with self.assertRaisesRegex(ValueError, "visual approval"):
            reg.audit(data)
        data = synthetic()
        data["matches"]["fantasy_east"] = []
        with self.assertRaisesRegex(ValueError, "exactly three"):
            reg.audit(data)

    def test_require_registered_cli_stays_red(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.json"
            cmd = [sys.executable, str(reg.__file__), "--report", str(out)]
            p = subprocess.run(cmd + ["--require-registered"], capture_output=True, text=True)
            self.assertEqual(p.returncode, 2, p.stderr)
            self.assertTrue(out.exists())
            self.assertFalse(json.loads(out.read_text())["sourceRegisteredToV123"])
            p = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
