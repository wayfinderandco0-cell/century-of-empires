"""Evidence-gate regression checks."""
import copy
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
        self.assertIn("unverified_status",reasons)
        self.assertIn("missing_neighbor",reasons)
        self.assertIn("unverified_neighborArt",reasons)

    def test_reviewed_connection(self):
        edge={"status":"verified","fromCell":"a","toCell":"b","exit":[1100,704],"entry":[0,704],
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


    def test_explicit_status_required(self):
        for status in (None, "candidate", "unverified_candidate_not_playable", "approved", True):
            edge={"status":"verified","fromCell":"a","toCell":"b",
                  "exit":[1100,704],"entry":[0,704],"crossesRiver":True,
                  "routeArt":proof(),"terrainAccess":proof(),"neighborArt":proof(),
                  "bridgeOrFord":proof()}
            if status is None:
                del edge["status"]
            else:
                edge["status"]=status
            self.assertIn("unverified_status",connection_status(edge)[1])

    def test_malformed_edges_fail_closed(self):
        for obj in (None, [], "candidate", 42, False):
            self.assertEqual(connection_status(obj),(False,["invalid_edge"]))

    def test_invalid_neighbor_and_crossing_types(self):
        for field,value,reason in (("fromCell",1,"missing_neighbor"),
                                   ("toCell"," ","missing_neighbor"),
                                   ("crossesRiver",1,"unknown_crossing"),
                                   ("crossesRiver","false","unknown_crossing")):
            edge={"status":"verified","fromCell":"a","toCell":"b",
                  "exit":[1100,704],"entry":[0,704],"crossesRiver":True,
                  "routeArt":proof(),"terrainAccess":proof(),"neighborArt":proof(),
                  "bridgeOrFord":proof()}
            edge[field]=value
            self.assertIn(reason,connection_status(edge)[1])

    def test_missing_review_or_bridge(self):
        for field in ("routeArt","terrainAccess","neighborArt","bridgeOrFord"):
            edge={"status":"verified","fromCell":"a","toCell":"b",
                  "exit":[1100,704],"entry":[0,704],"crossesRiver":True,
                  "routeArt":proof(),"terrainAccess":proof(),"neighborArt":proof(),
                  "bridgeOrFord":proof()}
            edge[field]={"review":"verified","source":"","reviewer":"x"}
            self.assertFalse(connection_status(edge)[0])

    def test_no_mutation(self):
        edge={"status":"verified","fromCell":"a","toCell":"b",
              "exit":[1100,704],"entry":[0,704],"crossesRiver":True,
              "routeArt":proof(),"terrainAccess":proof(),"neighborArt":proof(),
              "bridgeOrFord":proof()}
        before=copy.deepcopy(edge)
        connection_status(edge)
        self.assertEqual(edge,before)

    def test_malformed_cell_is_never_playable(self):
        for obj in (None,5,"route",[],True):
            self.assertFalse(deep_zoom(obj))
            self.assertFalse(conquerable(obj))

if __name__=="__main__":
    unittest.main()
