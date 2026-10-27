#!/usr/bin/env python3
"""Immutable V123 road-conditioned art briefs for WEST and SOUTH.

These are precise image-composition constraints, NOT game art, proof of a
historical route, source-to-world registration, or permission to change V123.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = (1536, 1024)
PINNED_V123_GIT_BLOB = '09f04b4062e24fbacbb645307462cdddce2b2aa3'
ROUTES = {'west': ('westRoad', 13, (1536, 478), (275, 550)),
          'south': ('southRoad', 12, (466, 0), (1270, 605))}
CLEARANCE_RADIUS = 48
ROADBED_RADIUS = 13
OCTAGON = ((256, 0), (1280, 0), (1536, 256), (1536, 768),
           (1280, 1024), (256, 1024), (0, 768), (0, 256))


def git_blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def load_routes(source, require_pin=True):
    raw = Path(source).read_bytes()
    sha = git_blob_sha(raw)
    if require_pin and sha != PINNED_V123_GIT_BLOB:
        raise ValueError('V123 blob changed: STOP; no conditioning from altered graph')
    text = raw.decode('utf-8')
    result = {}
    for tile, (name, count, start, end) in ROUTES.items():
        match = re.search(r'const\s+' + name + r'\s*=\s*(\[\[[^;]+?\]\])\s*;', text)
        if not match:
            raise ValueError('Missing immutable V123 ' + name)
        points = json.loads(match.group(1))
        if (len(points) != count or tuple(points[0]) != start or
                tuple(points[-1]) != end or any(len(p) != 2 or
                not all(isinstance(v, int) for v in p) for p in points)):
            raise ValueError('V123 route structure/portal drift: ' + tile)
        if any(not (0 <= x <= SIZE[0] and 0 <= y <= SIZE[1]) for x, y in points):
            raise ValueError('Route point outside native cell: ' + tile)
        result[tile] = points
    return sha, result


def draw_masks(points):
    """Return clearance, roadbed and octagon masks, all in native pixel space.

    255 in clearance means an artist must reserve unobstructed continuous
    ground; it does NOT mean there is already a road.
    """
    clearance = Image.new('L', SIZE)
    roadbed = Image.new('L', SIZE)
    polygon = Image.new('L', SIZE)
    ImageDraw.Draw(polygon).polygon(OCTAGON, fill=255)
    for canvas, radius in ((clearance, CLEARANCE_RADIUS),
                           (roadbed, ROADBED_RADIUS)):
        d = ImageDraw.Draw(canvas)
        d.line([tuple(p) for p in points], fill=255, width=radius * 2 + 1, joint='curve')
        for p in points:
            x, y = p
            d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=255)
    return clearance, roadbed, polygon


def make_review(points, tile, clearance, roadbed, polygon):
    image = Image.new('RGB', SIZE, (33, 47, 49))
    image.paste((75, 115, 86), mask=polygon)
    image.paste((157, 177, 106), mask=clearance)
    image.paste((129, 89, 60), mask=roadbed)
    d = ImageDraw.Draw(image)
    d.line([tuple(p) for p in points], fill=(255, 242, 197), width=3, joint='curve')
    for label, p in (('PORTAL', points[0]), ('SURVEY LIMIT', points[-1])):
        x, y = p
        d.ellipse((x-8, y-8, x+8, y+8), outline=(255, 255, 255), width=3)
        dx = -170 if x > SIZE[0] - 200 else 15
        dy = 18 if y < 30 else -26
        d.text((max(10, x+dx), min(SIZE[1]-25, y+dy)), label, fill=(255, 255, 255))
    d.text((36, 36), tile.upper() + ' / V123 ART-CONDITIONING ONLY', fill='white')
    d.text((36, 58), 'Green: keep terrain open | Brown: physical cartway needed | White: immutable centerline', fill='white')
    d.text((36, 80), 'Not historical evidence, not playable imagery, not approved', fill='white')
    return image


def generate(atlas_path, output, require_pin=True):
    sha, routes = load_routes(atlas_path, require_pin=require_pin)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    report = {'version': 243, 'v123GitBlob': sha, 'nativePixels': list(SIZE),
              'artworkKind': 'ORIGINAL_FICTIONAL_CONDITIONING_GUIDES_ONLY',
              'sourceRegisteredToV123': False, 'historicRoadsVerified': False,
              'bridgeBanksVerified': False, 'sourceLicenseVerified': False,
              'humanArtApproved': False, 'physicalIPhoneApproved': False,
              'productionApproved': False, 'cells': {}}
    for tile, points in routes.items():
        clear, road, octagon = draw_masks(points)
        clear.save(out / f'{tile}-keep-clear-48px.png')
        road.save(out / f'{tile}-roadbed-13px.png')
        make_review(points, tile, clear, road, octagon).save(out / f'{tile}-composition-guide.png')
        report['cells'][tile] = {
            'routePoints': points, 'source': 'immutable V123 authored gameplay geometry',
            'firstPoint': points[0], 'lastPoint': points[-1],
            'clearanceRadiusPx': CLEARANCE_RADIUS, 'roadbedRadiusPx': ROADBED_RADIUS,
            'imageReadyForGameplay': False,
            'requiredArt': 'Unique photo-grade terrain authored around centerline; no cloned imagery or flat road stripe',
        }
    (out / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--atlas', default='terrain-grid/v123-atlas.js')
    parser.add_argument('--out', default='qa/v243-road-conditioning')
    args = parser.parse_args()
    print(json.dumps(generate(args.atlas, args.out), indent=2))
