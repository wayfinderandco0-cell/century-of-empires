#!/usr/bin/env python3
"""V208: source/game frame audit negative controls; no synthetic art approval."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import v204_contiguous_matrei_sources as source
import v208_source_game_frame_audit as audit


class FrameAuditTests(unittest.TestCase):
    def test_three_real_source_panels_are_not_game_octagons(self):
        r = audit.audit()
        self.assertEqual(r["version"], 208)
        self.assertEqual([c["gameCell"] for c in r["gameCells"]], ["west", "matrei", "south"])
        self.assertGreater(r["anchorSeparationKilometres"], 3.0)
        self.assertLess(r["anchorSeparationKilometres"], 5.0)
        self.assertTrue(all(c["directStretchAnisotropy"] > 1.4 for c in r["gameCells"]))
        self.assertTrue(all(c["independentlyReviewedMatchingLandmarks"] == 0 for c in r["gameCells"]))
        self.assertTrue(all(c["candidateGameToSourceTransform"] is None for c in r["gameCells"]))
        self.assertTrue(all(r[k] is False for k in audit.FALSE_FLAGS))
        self.assertEqual(r["gameGeometryPinnedTo"], source.PINNED)
        self.assertTrue(r["originalV121PhotoAndV123GraphUnmodified"])
        self.assertEqual(r["sourceProjection"], "EPSG:3857")
        self.assertEqual(r["requiredAttribution"], "Datenquelle: basemap.at (CC BY 4.0)")

    def test_exact_source_footprints_and_world_octagons(self):
        r = audit.audit()
        game = r["gameCells"]
        self.assertEqual(game[0]["gameOrigin"], [0, 0])
        self.assertEqual(game[1]["gameOrigin"], [1536, 0])
        self.assertEqual(game[2]["gameOrigin"], [1536, 1024])
        for c in game:
            self.assertEqual(len(c["gameOctagonPolygonWorldXY"]), 8)
            self.assertEqual(c["gameSizePixels"], [1536, 1024])
            self.assertEqual(c["requiredIndependentLandmarksPerCell"], 3)
            self.assertTrue(c["sourcePixelsMayNotBePastedAsGameGeography"])
        self.assertEqual(len(r["sourcePanels"]), 3)
        self.assertTrue(all(195 < p["approxGroundWidthMetres"] < 225
                            for p in r["sourcePanels"]))
        self.assertTrue(all(195 < p["approxGroundHeightMetres"] < 225
                            for p in r["sourcePanels"]))

    def test_output_exact_rebuild_and_tampering_fail(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            r = audit.build(out)
            self.assertTrue(audit.verify(out))
            svg = (out / "frame-comparison.svg").read_text()
            self.assertIn("NOT GEOGRAPHICALLY REGISTERED", svg)
            self.assertIn("NO INVENTED ROAD CONNECTIONS", svg)
            m = json.loads((out / "manifest.json").read_text())
            m["sourceRegisteredToV123"] = True
            (out / "manifest.json").write_text(json.dumps(m))
            with self.assertRaises(ValueError):
                audit.verify(out)
            audit.build(out)
            with (out / "frame-comparison.svg").open("a") as f:
                f.write("fabricated")
            with self.assertRaises(ValueError):
                audit.verify(out)
            audit.build(out)
            self.assertEqual(r["sourceRegisteredToV123"], False)

    def test_missing_report_and_fake_source_frame_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                audit.verify(Path(td) / "absent")
        real_plan = source.plan
        def substituted(site):
            m = copy.deepcopy(real_plan(site))
            if site == "forest":
                m["panels"][0]["footprintLonLat"] = [0, 0, 1, 1]
            return m
        with patch.object(source, "plan", side_effect=substituted):
            with self.assertRaises(ValueError):
                audit.audit()

    def test_require_registered_cli_stays_red(self):
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run(
                [sys.executable, str(Path(audit.__file__)),
                 "--output", td, "--require-registered"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('"sourceRegisteredToV123": false', result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
