#!/usr/bin/env python3
"""Audit V115 prototype path coordinates against V94/V116 geography.

This does not validate a road against the painted image or historical sources.
It deliberately never emits playable/verified V116 annotations.

Run from repo root:
  python scripts/audit_v116_corridor.py \
    --source terrain-grid/v115-route-provenance.json \
    --manifest terrain-v94/manifest.json \
    --output terrain-grid/v115-route-audit-v116.json
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _finite_pair(p):
    return (isinstance(p, list) and len(p) == 2 and
            all(type(v) in (int, float) and math.isfinite(v) for v in p))


def cells_for_segment(a, b, width, height, cols=24, rows=18):
    """Cells touched by a segment, including intermediate cells across grid lines.

    Segment must lie within the atlas. Boundary-only contacts are conservatively
    included by checking each interval midpoint and both endpoints.
    """
    if not (_finite_pair(a) and _finite_pair(b)):
        raise ValueError("Segment endpoints must be finite coordinate pairs")
    for p in (a, b):
        if not (0 <= p[0] <= width and 0 <= p[1] <= height):
            raise ValueError("Segment lies outside atlas")
    ts = {0.0, 1.0}
    dx, dy = b[0]-a[0], b[1]-a[1]
    for dim, step, count, length in ((0, dx, cols, width), (1, dy, rows, height)):
        if step:
            for k in range(1, count):
                t = (k*length/count - a[dim]) / step
                if 0 < t < 1:
                    ts.add(t)
    ordered = sorted(ts)
    def cell(t):
        x, y = a[0]+dx*t, a[1]+dy*t
        return (min(cols-1, max(0, int(x/(width/cols)))),
                min(rows-1, max(0, int(y/(height/rows)))))
    out = {cell(t) for t in ordered}
    out.update(cell((u+v)/2) for u, v in zip(ordered, ordered[1:]))
    return out


def audit(manifest, source, cols=24, rows=18):
    if manifest.get("projection") != "equirectangular":
        raise ValueError("Expected V94 equirectangular atlas")
    west, south, east, north = manifest["extent"]
    width, height = manifest["gameSize"]
    if not all(math.isfinite(v) for v in [west,south,east,north,width,height]):
        raise ValueError("Nonfinite map bounds")
    if west >= east or south >= north or width <= 0 or height <= 0:
        raise ValueError("Invalid map bounds")
    if not (isinstance(cols,int) and isinstance(rows,int) and cols>0 and rows>0):
        raise ValueError("Invalid grid dimensions")
    if not _finite_pair(source.get("matreiLonLat")) or not _finite_pair(source.get("artAnchorPx")):
        raise ValueError("Missing or malformed anchor")
    aw, ah = source["sourceArt"]["widthPx"], source["sourceArt"]["heightPx"]
    artw = source["artWidthAtlasPx"]
    if min(aw, ah, artw) <= 0:
        raise ValueError("Invalid art dimensions")
    anchor_lon, anchor_lat = source["matreiLonLat"]
    ax = (anchor_lon-west)*width/(east-west)
    ay = (north-anchor_lat)*height/(north-south)
    arth = artw*ah/aw
    artbox = [ax-source["artAnchorPx"][0]/aw*artw,
              ay-source["artAnchorPx"][1]/ah*arth, artw, arth]

    def to_world(p):
        return [artbox[0]+p[0]/aw*artw, artbox[1]+p[1]/ah*arth]
    routes = {"south":source["rawPath"], "bridge":source["bridgePath"]}
    fork = source["forkIndex"]
    if type(fork) is not int or not (0 <= fork < min(map(len, routes.values()))):
        raise ValueError("Invalid fork index")
    if routes["south"][:fork+1] != routes["bridge"][:fork+1]:
        raise ValueError("Bridge branch does not share the same junction geometry")
    out_routes = {}
    candidate = set()
    for name, path in routes.items():
        if len(path) < 2 or any(not _finite_pair(p) for p in path):
            raise ValueError("Invalid route points")
        if any(not (0 <= p[0] <= aw and 0 <= p[1] <= ah) for p in path):
            raise ValueError("Prototype route leaves painted image bounds")
        world = [to_world(p) for p in path]
        cells = set()
        for a,b in zip(world,world[1:]):
            cells.update(cells_for_segment(a,b,width,height,cols,rows))
        candidate.update(cells)
        length = sum(math.dist(a,b) for a,b in zip(path,path[1:]))
        out_routes[name] = {
            "artPointCount":len(path),
            "artLengthPx":round(length,5),
            "startWorldPx":[round(v,9) for v in world[0]],
            "endWorldPx":[round(v,9) for v in world[-1]],
            "candidateParentCells":[f"r{r:02d}-c{c:02d}" for c,r in sorted(cells)],
            "verifiedForArmyTravel":False,
            "verifiedAgainstArtwork":False
        }
    verification = source.get("verification", {})
    # A source flag is not proof; the audit cannot independently certify artwork.
    if any(verification.values()):
        raise ValueError("Unverified prototype snapshot cannot assert verification flags")
    result = {
        "version":116,
        "status":"prototype_geometry_audit_only",
        "source":source["source"],
        "mapProjection":"equirectangular",
        "artBoxWorldPx":[round(v,9) for v in artbox],
        "forkArtPx":routes["south"][fork],
        "forkWorldPx":[round(v,9) for v in to_world(routes["south"][fork])],
        "routes":out_routes,
        "candidateParentCells":[f"r{r:02d}-c{c:02d}" for c,r in sorted(candidate)],
        "sourceArtFractionOfOneParentCell":round((artw*arth)/((width/cols)*(height/rows)),10),
        "needsHierarchicalChildTiles":True,
        "verifiedDeepZoomEligibleCells":[],
        "generatedV116PlayableAnnotations":{},
        "bridgeFarBankContinuation":"unverified; no inferred road",
        "warning":"Candidate cells indicate where V115 artwork lies, NOT verified historical roads or accessible strategic objectives."
    }
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,default=ROOT/"terrain-v94/manifest.json")
    parser.add_argument("--source",type=Path,default=ROOT/"terrain-grid/v115-route-provenance.json")
    parser.add_argument("--output",type=Path,default=ROOT/"terrain-grid/v115-route-audit-v116.json")
    args=parser.parse_args()
    result=audit(json.loads(args.manifest.read_text()),json.loads(args.source.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print("candidate parent cells:", ", ".join(result["candidateParentCells"]))
    print("verified playable cells:",len(result["verifiedDeepZoomEligibleCells"]))
    print("hierarchical child tiles needed:",result["needsHierarchicalChildTiles"])


if __name__ == "__main__":
    main()
