"""Evidence-gate regression checks."""
import json
import unittest
from pathlib import Path
from v116_corridor_gate import connection_status, deep_zoom, conquerable

ROOT = Path(__file__).resolve().parents[1]
def proof():
    return {"review":"verified","source":"reviewed-source","reviewer":"reviewer"}

class Tests(unittest.TestCase):
    def test_candidate(self):
        data=json.loads((ROOT/"terrain-grid/octagon-1-east-candidate.json").read_text())
        ok, reasons=connection_status(data)
        self.assertFalse(ok)
        self.assertIn("missing_neighbor",reasons)
        self.assertIn("unverified_neighborArt",reasons)

    def test_reviewed_connection(self):
        edge={"fromCell":"a","toCell":"b","exit":[1100,704],"entry":[0,704],
              "crossesRiver":True,"routeArt":proof(),"terrainAccess":proof(),
              "neighborArt":proof(),"bridgeOrFord":proof()}
        self.assertEqual(connection_status(edge),(True,[]))
        edge["entry"]=[0,705]
        self.assertFalse(connection_status(edge)[0])

    def test_zoom_and_conquest(self):
        for kind in ("scenic","background"):
            self.assertFalse(deep_zoom({"kind":kind,"accessibleRoute":proof()}))
            self.assertFalse(conquerable({"kind":kind,"conquestObjective":proof()}))
        self.assertTrue(deep_zoom({"kind":"route","accessibleRoute":proof()}))
        self.assertFalse(conquerable({"kind":"route","accessibleRoute":proof()}))
        self.assertTrue(conquerable({"kind":"strategic","accessibleObjective":proof(),"conquestObjective":proof()}))

if __name__=="__main__":
    unittest.main()
