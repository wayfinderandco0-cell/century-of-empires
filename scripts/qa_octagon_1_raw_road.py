#!/usr/bin/env python3
"""Raw JPEG route sampling diagnostic. Contrast is not evidence of a real road."""
import argparse
import csv
import json
import math
import re
from pathlib import Path
from statistics import median
from PIL import Image, ImageDraw

SW, SH = 1100, 842

def extract(text, name):
    m = re.search(r'const\s+' + re.escape(name) + r'\s*=\s*(\[\[.*?\]\])\s*;', text, re.S)
    if not m:
        raise ValueError('Missing candidate geometry: ' + name)
    points = json.loads(m.group(1))
    if len(points) < 2 or any(len(p) != 2 or any(type(v) not in (int, float) or not math.isfinite(v) for v in p) or not (0 <= p[0] <= SW and 0 <= p[1] <= SH) for p in points):
        raise ValueError('Invalid candidate geometry: ' + name)
    return points

def samples(path, spacing=16):
    segments = [(a, b, math.dist(a, b)) for a, b in zip(path, path[1:])]
    total = sum(s[2] for s in segments)
    if total <= 0:
        raise ValueError('Zero-length route')
    count = math.ceil(total / spacing)
    for index in range(count + 1):
        remaining = total * index / count
        for a, b, length in segments:
            if length == 0:
                continue
            if remaining <= length + 1e-8:
                t = max(0, min(1, remaining / length))
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                nx, ny = -(b[1] - a[1]) / length, (b[0] - a[0]) / length
                yield index, x, y, nx, ny
                break
            remaining -= length

def pixel(im, x, y):
    if not (2 <= x < SW - 2 and 2 <= y < SH - 2):
        return None
    x, y = round(x), round(y)
    neighborhood = [im.getpixel((x + dx, y + dy)) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    return tuple(median(rgb[c] for rgb in neighborhood) for c in range(3))

def contrast(a, b):
    return math.sqrt(sum((v - w) ** 2 for v, w in zip(a, b)))

def inspect(im, route):
    rows = []
    for index, x, y, nx, ny in samples(route):
        mid = pixel(im, x, y)
        left = pixel(im, x + 14 * nx, y + 14 * ny)
        right = pixel(im, x - 14 * nx, y - 14 * ny)
        score = round((contrast(mid, left) + contrast(mid, right)) / 2, 2) if mid and left and right else None
        rows.append(dict(sample=index, x=round(x, 2), y=round(y, 2), raw_center_rgb=mid,
                         raw_left_rgb=left, raw_right_rgb=right, raw_cross_track_contrast=score))
    return rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--image', type=Path, default=Path('terrain-grid/octagon-1-v119-source.jpg'))
    p.add_argument('--editor', type=Path, default=Path('octagon-1-road-authoring.html'))
    p.add_argument('--output', type=Path, default=Path('qa/octagon-1/raw-road'))
    a = p.parse_args()
    text = a.editor.read_text()
    approach, east, south = (extract(text, name) for name in ('APPROACH', 'BASE_EAST', 'SOUTH'))
    if approach[-1] != [699, 799] or east[-1] != [1100, 704] or south[-1] != [315, 842]:
        raise ValueError('Candidate endpoint changed: independent review required')
    with Image.open(a.image) as source:
        if source.size != (SW, SH):
            raise ValueError('Unexpected original JPEG dimensions')
        im = source.convert('RGB')
    routes = {'east_candidate': [approach[-1]] + east, 'south_candidate': south[36:]}
    data = {name: inspect(im, path) for name, path in routes.items()}
    a.output.mkdir(parents=True, exist_ok=True)
    with (a.output / 'raw-road-samples.csv').open('w', newline='') as f:
        fields = ['route', 'sample', 'x', 'y', 'raw_center_rgb', 'raw_left_rgb', 'raw_right_rgb', 'raw_cross_track_contrast']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for name, rows in data.items():
            for row in rows:
                writer.writerow({'route': name, **row})
    report = {'source': str(a.image), 'source_dimensions': [SW, SH],
              'method': 'unaltered JPEG 3x3 median pixels, 14px cross-track offsets, 16px arc samples',
              'painted_road_verified': False, 'historical_road_verified': False,
              'bridge_far_bank_verified': False, 'production_ready': False, 'routes': {}}
    patches = []
    for name, rows in data.items():
        values = [r['raw_cross_track_contrast'] for r in rows if r['raw_cross_track_contrast'] is not None]
        report['routes'][name] = {
            'samples': len(rows), 'valid_samples': len(values),
            'median_cross_track_contrast': round(median(values), 2) if values else None,
            'low_contrast_under_18': sum(v < 18 for v in values),
            'warning': 'Color contrast is diagnostic only: neither high nor low contrast certifies a road.'}
        for row in rows[::max(1, len(rows) // 16)]:
            x, y = round(row['x']), round(row['y'])
            patches.append((name, row['sample'], im.crop((x - 32, y - 32, x + 32, y + 32))))
    columns = 8
    sheet = Image.new('RGB', (columns * 92, math.ceil(len(patches) / columns) * 88), (235, 231, 218))
    draw = ImageDraw.Draw(sheet)
    for i, (name, index, crop) in enumerate(patches):
        x, y = i % columns * 92, i // columns * 88
        sheet.paste(crop, (x + 14, y + 2))
        draw.text((x + 2, y + 68), f'{name[:5]} #{index}', fill=(0, 0, 0))
    sheet.save(a.output / 'raw-road-contact-sheet.png')
    (a.output / 'raw-road-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
