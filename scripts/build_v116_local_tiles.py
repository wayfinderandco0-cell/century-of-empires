#!/usr/bin/env python3
"""Build a *non-playable* child-tile index for the V115 painted local scene.

The V116 24x18 octagons are a strategic index, not local image tiles. This
module subdivides the tiny V115 scene footprint while keeping its original
artwork, V94 world pixels, and longitude/latitude tied to one affine transform.

The V115 painting is oblique and its single anchor is approximate; this is a
coordinate/provenance scaffold, NOT a validated historical road map. No tile
is marked playable, traversable, conquerable, or verified for deep zoom.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def finite_pair(value):
    return (isinstance(value, (list, tuple)) and len(value) == 2 and
            all(type(v) in (int, float) and math.isfinite(v) for v in value))


def intersects_segment_rect(a, b, rect):
    """Liang-Barsky inclusive segment/rectangle intersection (touches included)."""
    if not finite_pair(a) or not finite_pair(b):
        raise ValueError('Segment coordinates must be finite pairs')
    x0, y0, x1, y1 = rect
    if not (x0 < x1 and y0 < y1):
        raise ValueError('Invalid tile rectangle')
    dx, dy = b[0] - a[0], b[1] - a[1]
    lo, hi = 0.0, 1.0
    for p, q in ((-dx, a[0]-x0), (dx, x1-a[0]),
                 (-dy, a[1]-y0), (dy, y1-a[1])):
        if p == 0:
            if q < 0:
                return False
            continue
        t = q/p
        if p < 0:
            lo = max(lo, t)
        else:
            hi = min(hi, t)
        if lo > hi:
            return False
    return True


def make_local_index(manifest, source, cols=8, rows=6, parent_cols=24, parent_rows=18):
    if manifest.get('projection') != 'equirectangular':
        raise ValueError('Requires V94 equirectangular projection')
    extent, size = manifest.get('extent'), manifest.get('gameSize')
    if (not isinstance(extent, list) or len(extent) != 4 or
            any(type(v) not in (int, float) or not math.isfinite(v) for v in extent)):
        raise ValueError('Invalid atlas extent')
    if not finite_pair(size) or min(size) <= 0:
        raise ValueError('Invalid atlas gameSize')
    west, south, east, north = extent
    width, height = size
    if west >= east or south >= north:
        raise ValueError('Invalid atlas geographic extent')
    if any(type(v) is not int or v < 1 or v > 128 for v in (cols, rows, parent_cols, parent_rows)):
        raise ValueError('Invalid grid dimensions')
    art = source.get('sourceArt', {})
    aw, ah = art.get('widthPx'), art.get('heightPx')
    art_width = source.get('artWidthAtlasPx')
    anchor, anchor_ll = source.get('artAnchorPx'), source.get('matreiLonLat')
    if (not finite_pair([aw, ah]) or min(aw, ah) <= 0 or
            type(art_width) not in (int, float) or not math.isfinite(art_width) or art_width <= 0 or
            not finite_pair(anchor) or not finite_pair(anchor_ll)):
        raise ValueError('Invalid V115 art transform')
    if not (0 <= anchor[0] <= aw and 0 <= anchor[1] <= ah):
        raise ValueError('Art anchor outside source image')
    lon, lat = anchor_ll
    if not (west <= lon <= east and south <= lat <= north):
        raise ValueError('Geographic anchor outside atlas')
    world_anchor = ((lon-west)*width/(east-west), (north-lat)*height/(north-south))
    art_height = art_width * ah / aw
    x0 = world_anchor[0] - anchor[0]/aw*art_width
    y0 = world_anchor[1] - anchor[1]/ah*art_height
    if not (0 <= x0 < x0+art_width <= width and 0 <= y0 < y0+art_height <= height):
        raise ValueError('Local artwork lies outside atlas')
    def world(px, py):
        return [x0 + px*art_width/aw, y0 + py*art_height/ah]
    def lonlat(px, py):
        x, y = world(px, py)
        return [west + x*(east-west)/width, north - y*(north-south)/height]
    def parent_candidates(rect):
        out = []
        for r in range(parent_rows):
            for c in range(parent_cols):
                bx0, by0 = c*width/parent_cols, r*height/parent_rows
                bx1, by1 = (c+1)*width/parent_cols, (r+1)*height/parent_rows
                # Positive area overlap only, not a shared boundary touch.
                if rect[0] < bx1 and rect[2] > bx0 and rect[1] < by1 and rect[3] > by0:
                    out.append(f'r{r:02d}-c{c:02d}')
        return out
    routes = {}
    for name, key in (('south','rawPath'),('bridge','bridgePath')):
        pts = source.get(key)
        if not isinstance(pts, list) or len(pts) < 2 or any(not finite_pair(p) for p in pts):
            raise ValueError(f'Invalid {name} prototype path')
        if any(not (0 <= p[0] <= aw and 0 <= p[1] <= ah) for p in pts):
            raise ValueError(f'{name} path leaves source art')
        routes[name] = pts
    fork = source.get('forkIndex')
    if type(fork) is not int or not (0 <= fork < min(len(p) for p in routes.values())):
        raise ValueError('Invalid fork index')
    if routes['south'][:fork+1] != routes['bridge'][:fork+1]:
        raise ValueError('Route branches do not share the source fork')
    if any(source.get('verification', {}).values()):
        raise ValueError('Prototype cannot assert unverified road/bridge access')
    # Calculate each edge from the *global* art transform; do not add
    # rounded tile widths, which would accumulate seams.
    # Use integer source-pixel crop boundaries to avoid subpixel raster seams.
    # Unequal one-pixel tile widths are intentional when dimensions do not divide.
    xedges = [round(aw*i/cols) for i in range(cols+1)]
    yedges = [round(ah*i/rows) for i in range(rows+1)]
    if any(b <= a for edges in (xedges,yedges) for a,b in zip(edges,edges[1:])):
        raise ValueError('Too many tiles for source image resolution')
    tiles = []
    route_ids = {name: set() for name in routes}
    for r in range(rows):
        for c in range(cols):
            rect = [xedges[c], yedges[r], xedges[c+1], yedges[r+1]]
            a, b = world(rect[0], rect[1]), world(rect[2], rect[3])
            wr = [a[0], a[1], b[0], b[1]]
            tile_id = f'local-r{r:02d}-c{c:02d}'
            candidate_routes = []
            for name, pts in routes.items():
                if any(intersects_segment_rect(p, q, rect) for p, q in zip(pts, pts[1:])):
                    candidate_routes.append(name)
                    route_ids[name].add(tile_id)
            tiles.append({
                'id':tile_id, 'row':r, 'col':c,
                'imageCropPx':rect, 'worldRectPx':wr,
                'lonLatNW':lonlat(rect[0], rect[1]),
                'lonLatSE':lonlat(rect[2], rect[3]),
                'parentOctagonCandidates':parent_candidates(wr),
                'prototypeRouteCandidates':candidate_routes,
                'paintedRoadVerified':False,
                'traversable':False, 'conquerable':False, 'deepZoomEligible':False,
                'renderableExistingArtwork':True
            })
    return {
        'version':116, 'kind':'unverified_local_art_tile_index',
        'source':source.get('source', {}),
        'artSource':'V115 embedded V109-style oblique scene (no independent tiles generated)',
        'georegistration':'approximate single-anchor affine placement; NOT survey-grade',
        'atlasProjection':'equirectangular',
        'atlasGameSize':size, 'atlasExtentLonLat':extent,
        'artSizePx':[aw, ah], 'artBoxWorldPx':[x0,y0,x0+art_width,y0+art_height],
        'anchorArtPx':anchor, 'anchorLonLat':anchor_ll,
        'anchorWorldPx':list(world_anchor),
        'parentOctagonCandidates':parent_candidates([x0,y0,x0+art_width,y0+art_height]),
        'grid':{'columns':cols,'rows':rows,'tileCount':len(tiles)},
        'routeCandidateTileIds':{name:sorted(ids) for name,ids in routes.items() for ids in [route_ids[name]]},
        'verification':{'historicalRoad':False,'roadPixelsAligned':False,
                        'bridgeCrossing':False,'farBankContinuation':False,
                        'playableRouteTiles':0,'conquerableTiles':0},
        'tiles':tiles
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'terrain-v94/manifest.json')
    parser.add_argument('--source', type=Path, default=ROOT/'terrain-grid/v115-route-provenance.json')
    parser.add_argument('--output', type=Path, default=ROOT/'terrain-grid/v115-local-tiles-v116.json')
    parser.add_argument('--columns', type=int, default=8)
    parser.add_argument('--rows', type=int, default=6)
    args = parser.parse_args()
    data = make_local_index(json.loads(args.manifest.read_text()),
                            json.loads(args.source.read_text()),args.columns,args.rows)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,separators=(',',':'))+'\n')
    print('local artwork child tiles:',data['grid']['tileCount'],
          '| parent cells:',data['parentOctagonCandidates'],
          '| verified playable:',data['verification']['playableRouteTiles'])


if __name__ == '__main__':
    main()
