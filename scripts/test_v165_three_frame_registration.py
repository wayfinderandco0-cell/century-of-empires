#!/usr/bin/env python3
"""Synthetic V165 tests; NO synthetic point represents an Alpine landmark."""
import copy
import json
import unittest
from pathlib import Path
import v165_three_frame_registration as v165

FRAME = {
    "id": "synthetic-shared-frame-not-real-geography",
    "width": 7000, "height": 5000,
    "referenceUrl": "https://www.openstreetmap.org/",
    "modernReferenceOnly": True,
}
LOCAL = ((400, 300), (700, 300), (500, 600))


def sample():
    data = {"schemaVersion": 1, "sourceFrame": copy.deepcopy(FRAME),
            "corridors": {}}
    for corridor, (ox, oy) in v165.ORIGINS.items():
        rows = []
        for i, (x, y) in enumerate(LOCAL):
            gx, gy = x+ox, y+oy
            rows.append({
                "id": f"{corridor}-landmark-{i}",
                "role": "holdout" if i == 2 else "control",
                "game": [gx, gy],
                "source": [gx+400, gy+500],
                "gameEvidenceUrl": f"https://www.openstreetmap.org/node/{100+i}",
                "sourceEvidenceUrl": f"https://www.openstreetmap.org/node/{200+i}",
                "reviewedBy": "synthetic-test-only",
            })
        data["corridors"][corridor] = rows
    return data


class FrameTests(unittest.TestCase):
    def test_three_synthetic_corridors_share_one_world_frame(self):
        report = v165.audit(sample())
        self.assertTrue(report["allThreeCandidateFitsValidated"])
        self.assertTrue(report["sharedSourceFrameCoherent"])
        self.assertEqual(len(report["seamDiagnostics"]), 2)
        for x in report["seamDiagnostics"].values():
            self.assertEqual(x["sourceSeamDeltaPx"], 0)
        for key in ("gameRouteGeoregistered", "historicalRoadsVerified",
                    "bridgeBanksVerified", "periodArtComplete",
                    "threeOctagonsVisuallyApproved", "physicalIPhoneApproved",
                    "productionApproved"):
            self.assertIs(report[key], False, key)

    def test_real_repository_evidence_remains_blocked(self):
        p = Path(__file__).resolve().parents[1] / "terrain-grid/v163-unverified-landmark-evidence.json"
        r = v165.audit(json.loads(p.read_text()))
        self.assertFalse(r["allThreeCandidateFitsValidated"])
        self.assertFalse(r["sharedSourceFrameCoherent"])
        self.assertFalse(r["productionApproved"])
        self.assertEqual(set(r["corridors"]), set(v165.ORIGINS))

    def test_south_below_matre_i_not_to_right(self):
        d = sample()
        self.assertGreater(d["corridors"]["southern_valley"][0]["game"][1], 1024)
        self.assertTrue(v165.audit(d)["sharedSourceFrameCoherent"])
        d["corridors"]["southern_valley"][0]["game"] = [3400, 400]
        with self.assertRaisesRegex(ValueError, "outside its V123 octagon"):
            v165.audit(d)

    def test_matrei_landmarks_cannot_count_as_west(self):
        d = sample()
        d["corridors"]["western_pass"] = copy.deepcopy(d["corridors"]["matrei"])
        with self.assertRaisesRegex(ValueError, "outside its V123 octagon"):
            v165.audit(d)

    def test_cut_off_octagon_corners_are_not_playable_controls(self):
        d = sample()
        d["corridors"]["western_pass"][0]["game"] = [5, 5]
        with self.assertRaisesRegex(ValueError, "octagon footprint"):
            v165.audit(d)

    def test_reused_landmark_id_across_tiles_rejected(self):
        d = sample()
        d["corridors"]["southern_valley"][1]["id"] = d["corridors"]["matrei"][1]["id"]
        with self.assertRaisesRegex(ValueError, "reused landmark ID"):
            v165.audit(d)

    def test_reused_source_pixel_across_tiles_rejected(self):
        d = sample()
        d["corridors"]["southern_valley"][1]["source"] = d["corridors"]["matrei"][1]["source"]
        with self.assertRaisesRegex(ValueError, "reused source pixel"):
            v165.audit(d)

    def test_three_separately_perfect_but_shifted_fits_rejected(self):
        d = sample()
        for row in d["corridors"]["southern_valley"]:
            row["source"][0] += 50
        with self.assertRaisesRegex(ValueError, "source coordinate seam discontinuity"):
            v165.audit(d)

    def test_three_separately_perfect_but_scaled_fits_rejected(self):
        d = sample()
        for row in d["corridors"]["southern_valley"]:
            row["source"] = [round(row["source"][0]*1.1),
                             round(row["source"][1]*1.1)]
        with self.assertRaisesRegex(ValueError, "source scale discontinuity"):
            v165.audit(d)

    def test_three_separately_perfect_but_rotated_fits_rejected(self):
        d = sample()
        for row in d["corridors"]["southern_valley"]:
            x, y = row["source"]
            row["source"] = [y+1200, 4000-x]
        with self.assertRaisesRegex(ValueError, "source rotation discontinuity"):
            v165.audit(d)

    def test_partial_evidence_does_not_approve(self):
        d = sample()
        d["corridors"]["western_pass"] = []
        r = v165.audit(d)
        self.assertFalse(r["allThreeCandidateFitsValidated"])
        self.assertFalse(r["sharedSourceFrameCoherent"])
        self.assertFalse(r["productionApproved"])

    def test_bad_independent_holdout_still_fails(self):
        d = sample()
        d["corridors"]["matrei"][2]["source"][1] += 40
        with self.assertRaisesRegex(ValueError, "holdout residual"):
            v165.audit(d)

    def test_no_unrecognized_tile_or_historical_source_claim(self):
        d = sample()
        d["corridors"]["fictional_valley"] = []
        with self.assertRaises(ValueError):
            v165.audit(d)
        d = sample()
        d["sourceFrame"]["modernReferenceOnly"] = False
        with self.assertRaises(ValueError):
            v165.audit(d)


if __name__ == "__main__":
    unittest.main()
