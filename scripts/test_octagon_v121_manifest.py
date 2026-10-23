#!/usr/bin/env python3
"""Fail-closed V121 source-art/route manifest contract; not historical or visual approval."""
import base64
import hashlib
import json
import math
import re
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'terrain-grid/octagon-1-v121.manifest.json'
HTML = ROOT / 'v121-octagon-1-painted-road.html'
ART = ROOT / 'terrain-grid/octagon-1-v121.webp'


def embedded_json(html, name):
    match = re.search(r'const\s+' + re.escape(name) + r'\s*=\s*([^;\n]+);', html)
    if not match:
        raise ValueError(f'Missing {name} constant in playable prototype')
    return json.loads(match.group(1))


def node(point):
    return tuple(point)


def validate(data, html, art):
    """Return all independently testable contract violations; do not certify road pixels."""
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)

    roads = data['movement']['roads']
    width = data['dimensions']['width']
    height = data['dimensions']['height']
    require((width, height) == (1536, 1024), 'unexpected source-art dimensions')
    require(set(roads) == {'west', 'north', 'south', 'bridge', 'village', 'southeast'}, 'route inventory drift')
    points = set()
    adjacency = {}
    for name, route in roads.items():
        require(len(route) >= 2, f'{name}: missing route segments')
        for point in route:
            require(len(point) == 2 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in point), f'{name}: invalid coordinate')
            require(0 <= point[0] < width and 0 <= point[1] < height, f'{name}: outside artwork')
            points.add(node(point))
        for a, b in zip(route, route[1:]):
            a, b = node(a), node(b)
            require(a != b, f'{name}: zero-length road segment')
            adjacency.setdefault(a, set()).add(b)
            adjacency.setdefault(b, set()).add(a)
    require(len(points) == data['movement']['graphNodeCount'], 'graph node count differs from authored data')
    if points:
        visited = set()
        queue = deque([next(iter(points))])
        while queue:
            p = queue.popleft()
            if p in visited:
                continue
            visited.add(p)
            queue.extend(adjacency.get(p, ()) - visited)
        require(visited == points, 'road network has disconnected segments')

    require(roads['west'][-1] == roads['north'][0] == roads['south'][0] == roads['bridge'][0], 'west/north/south/bridge fork disconnected')
    require(roads['bridge'][-1] == roads['village'][0] == roads['southeast'][0], 'east village/southeast fork disconnected')
    ends = data['movement']['primaryStoneBridgeEnds']
    require(len(ends) == 2 and all(p in roads['bridge'] for p in ends), 'bridge endpoints not on the authored bridge route')
    if len(ends) == 2 and all(p in roads['bridge'] for p in ends):
        require(roads['bridge'].index(ends[0]) < roads['bridge'].index(ends[1]), 'bridge endpoints reversed')

    try:
        require(embedded_json(html, 'ROADS') == roads, 'prototype roads differ from exported manifest')
        require(embedded_json(html, 'BRIDGE_ENDS') == ends, 'prototype bridge differs from exported manifest')
    except (ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    image_match = re.search(r"source\.src='data:image/webp;base64,([^']+)'", html)
    require(bool(image_match), 'missing embedded WebP source artwork')
    if image_match:
        try:
            require(base64.b64decode(image_match.group(1), validate=True) == art, 'embedded artwork differs from reusable WebP')
        except ValueError as exc:
            errors.append(f'invalid embedded image: {exc}')
    require(art[:4] == b'RIFF' and art[8:12] == b'WEBP', 'reusable artwork is not WebP')
    sha = hashlib.sha1(f'blob {len(art)}\0'.encode() + art).hexdigest()
    require(sha == data['art']['gitBlobSha'], 'artwork git blob SHA differs from pinned manifest')
    require(data['art']['path'] == 'terrain-grid/octagon-1-v121.webp', 'artwork path changed')
    require(data['source']['prototype'] == 'v121-octagon-1-painted-road.html', 'prototype identity changed')

    exits = {'west': roads['west'][0], 'south': roads['south'][-1], 'southeast': roads['southeast'][-1]}
    require(len(data['edgeConnections']) == len(exits), 'edge connection count differs from unbuilt exits')
    for edge in data['edgeConnections']:
        road = edge['road']
        require(road in exits and edge['point'] == exits.get(road), f'{road}: exit endpoint drift')
        require(edge['neighborStatus'] == 'not authored', f'{road}: neighbor claimed without sourced evidence')
    require(set(e['road'] for e in data['edgeConnections']) == set(exits), 'edge exit inventory drift')
    for key in ('physicalIphoneVisualApproval', 'historicalRoadAccuracyVerified', 'neighborSeamVerified', 'productionGameplayIntegrated'):
        require(data['acceptance'].get(key) is False, f'{key}: unverified approval claimed')
    require('get productionApproved(){return false}' in html, 'prototype production gate changed')
    require('get historicalRouteVerified(){return false}' in html, 'prototype historical gate changed')
    return errors


class V121ManifestIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text())
        cls.html = HTML.read_text()
        cls.art = ART.read_bytes()

    def test_source_contract(self):
        self.assertEqual(validate(self.data, self.html, self.art), [])

    def test_modified_art_rejected(self):
        changed = bytearray(self.art)
        changed[-1] ^= 1
        self.assertTrue(validate(self.data, self.html, bytes(changed)))

    def test_fake_neighbor_rejected(self):
        altered = json.loads(json.dumps(self.data))
        altered['edgeConnections'][0]['neighborStatus'] = 'connected'
        self.assertIn('west: neighbor claimed without sourced evidence', validate(altered, self.html, self.art))

    def test_unapproved_production_gate_rejected(self):
        altered = json.loads(json.dumps(self.data))
        altered['acceptance']['productionGameplayIntegrated'] = True
        self.assertTrue(any('productionGameplayIntegrated' in e for e in validate(altered, self.html, self.art)))

    def test_road_drift_rejected(self):
        altered = json.loads(json.dumps(self.data))
        altered['movement']['roads']['bridge'][6][0] += 3
        self.assertIn('prototype roads differ from exported manifest', validate(altered, self.html, self.art))

    def test_bridge_drift_rejected(self):
        altered = json.loads(json.dumps(self.data))
        altered['movement']['primaryStoneBridgeEnds'][0] = [0, 0]
        self.assertIn('bridge endpoints not on the authored bridge route', validate(altered, self.html, self.art))


if __name__ == '__main__':
    unittest.main()
