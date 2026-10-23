#!/usr/bin/env python3
"""Reject undeclared road intersections; does not certify painted or historical roads."""
import json
import unittest
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "terrain-grid/octagon-1-v121.manifest.json"

def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def on_segment(a, b, p):
    return cross(a,b,p)==0 and all(min(a[i],b[i])<=p[i]<=max(a[i],b[i]) for i in (0,1))

def intersects(a,b,c,d):
    x,y,z,w=cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
    return (on_segment(a,b,c) or on_segment(a,b,d) or on_segment(c,d,a)
            or on_segment(c,d,b) or (x*y<0 and z*w<0))

def shared_endpoint_only(a,b,c,d,approved):
    common={tuple(a),tuple(b)} & {tuple(c),tuple(d)} & approved
    if len(common)!=1:
        return False
    p=next(iter(common))
    u=b if tuple(a)==p else a
    v=d if tuple(c)==p else c
    # Different rays can meet at a fork but cannot overlap in the same direction.
    return cross(p,u,v)!=0 or (u[0]-p[0])*(v[0]-p[0])+(u[1]-p[1])*(v[1]-p[1])<0

def errors(roads):
    approved={tuple(roads["bridge"][0]),tuple(roads["bridge"][-1])}
    segments=[(name,i,a,b) for name,pts in roads.items()
              for i,(a,b) in enumerate(zip(pts,pts[1:]))]
    violations=[]
    for i,(name,j,a,b) in enumerate(segments):
        if a==b:
            violations.append(f"{name}[{j}] has zero length")
        for other,k,c,d in segments[i+1:]:
            if not intersects(a,b,c,d):
                continue
            if name==other and abs(j-k)==1:
                p=b if tuple(b) in (tuple(c),tuple(d)) else a
                u=a if tuple(b)==tuple(p) else b
                v=d if tuple(c)==tuple(p) else c
                if cross(p,u,v)!=0 or (u[0]-p[0])*(v[0]-p[0])+(u[1]-p[1])*(v[1]-p[1])<0:
                    continue
            if name!=other and shared_endpoint_only(a,b,c,d,approved):
                continue
            violations.append(f"{name}[{j}] crosses {other}[{k}] without an approved junction")
    return violations

class V121RouteIntersections(unittest.TestCase):
    def test_checked_in_roads(self):
        roads=json.loads(MANIFEST.read_text())["movement"]["roads"]
        self.assertEqual(errors(roads),[])
    def test_unapproved_crossing_rejected(self):
        roads={"west":[[0,0],[10,10]],"north":[[0,10],[10,0]],
               "bridge":[[20,20],[30,20]]}
        self.assertTrue(errors(roads))
    def test_declared_fork_accepted(self):
        roads={"west":[[0,0],[10,10]],"north":[[10,10],[10,0]],
               "bridge":[[10,10],[20,20]],"south":[[10,10],[0,20]]}
        self.assertEqual(errors(roads),[])
    def test_overlap_rejected(self):
        roads={"west":[[0,0],[10,0]],"north":[[5,0],[15,0]],
               "bridge":[[20,20],[30,20]]}
        self.assertTrue(errors(roads))

if __name__=="__main__":
    unittest.main()
