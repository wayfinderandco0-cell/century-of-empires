#!/usr/bin/env python3
"""Export raw/annotated V121 road-review crops from pinned original art.

This creates inspection evidence only. Contrast, crop markers, and apparent
painted roads are NOT approval of historical routes, bridge safety or gameplay.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw
import audit_v128_road_profiles as previous

ROOT = Path(__file__).resolve().parent.parent
CROP_SIZE = 160
LABEL_HEIGHT = 22


def git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(content)).encode('ascii') + b'\0' + content).hexdigest()


def verify_source(content: bytes, manifest: dict) -> None:
    expected = manifest['art']['gitBlobSha']
    if not isinstance(expected, str) or len(expected) != 40 or git_blob_sha(content) != expected:
        raise ValueError('Original source painting differs from pinned V121 Git blob')


def crop_box(point, size, dimensions):
    if not isinstance(size, int) or isinstance(size, bool) or size < 1:
        raise ValueError('Invalid crop size')
    if any(d < size for d in dimensions):
        raise ValueError('Source image is smaller than the requested crop')
    if not previous.previous.valid_point(point):
        raise ValueError('Invalid review point')
    x, y = point
    width, height = dimensions
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError('Review point is outside the source painting')
    left = max(0, min(width-size, round(x)-size//2))
    top = max(0, min(height-size, round(y)-size//2))
    return left, top, left+size, top+size


def make_pair(image, review, size=CROP_SIZE):
    box = crop_box(review['point'], size, image.size)
    raw = image.crop(box).convert('RGB')
    marked = raw.copy()
    x = round(review['point'][0])-box[0]
    y = round(review['point'][1])-box[1]
    draw = ImageDraw.Draw(marked)
    # Mark only the candidate coordinate; never draw a replacement road.
    draw.line([(x-9,y),(x+9,y)], fill=(255,0,0), width=2)
    draw.line([(x,y-9),(x,y+9)], fill=(255,0,0), width=2)
    return raw, marked, list(box)


def export(image, manifest, source_bytes, output_dir, size=CROP_SIZE):
    verify_source(source_bytes, manifest)
    if image.size != (manifest['dimensions']['width'], manifest['dimensions']['height']):
        raise ValueError('Painting dimensions differ from pinned V121 manifest')
    review_report = previous.audit(image.convert('RGB'), manifest)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    routes = {}
    for name, reviews in review_report['reviewProfiles'].items():
        if not name.isascii() or not name.replace('_', '').isalnum():
            raise ValueError('Unsafe route name in manifest')
        entries = []
        if not reviews:
            routes[name] = {'image': None, 'samples': []}
            continue
        sheet = Image.new('RGB', (2*size, len(reviews)*(size+LABEL_HEIGHT)), (255,255,255))
        pen = ImageDraw.Draw(sheet)
        for i, review in enumerate(reviews):
            raw, marked, box = make_pair(image, review, size)
            y = i*(size+LABEL_HEIGHT)
            sheet.paste(raw, (0,y))
            sheet.paste(marked, (size,y))
            pen.text((3,y+size+3), f"{i+1}: {review['point']} arc={review['arcPx']}", fill=(0,0,0))
            entries.append({'point': review['point'], 'arcPx': review['arcPx'],
                            'reviewReasons': review['reviewReasons'], 'cropBox': box,
                            'rawPanelUnmodified': True})
        filename = f'v129-{name}-raw-vs-marked.png'
        sheet.save(output_dir/filename, format='PNG', optimize=False)
        routes[name] = {'image': filename, 'samples': entries,
                        'sha256': hashlib.sha256((output_dir/filename).read_bytes()).hexdigest()}
    report = {'version':129, 'sourceArt':manifest['art']['path'],
              'sourceGitBlobSha':git_blob_sha(source_bytes),
              'sourceSha256':hashlib.sha256(source_bytes).hexdigest(),
              'cropSizePx':size, 'leftPanel':'unaltered source image crop',
              'rightPanel':'same crop with candidate center point marker only',
              'routes':routes, 'totalReviewSamples':sum(len(x['samples']) for x in routes.values()),
              'historicalAccuracyVerified':False, 'roadSurfaceClassified':False,
              'pixelAlignmentVerified':False, 'bridgeCrossingVerified':False,
              'neighborContinuationVerified':False, 'productionEnabled':False,
              'interpretation':'Review evidence only; visually inspect raw painting before changing geometry or enabling roads.'}
    (output_dir/'v129-review-index.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=ROOT/'terrain-grid/octagon-1-v121.manifest.json')
    parser.add_argument('--image',type=Path)
    parser.add_argument('--out',type=Path,default=Path('v129-road-source-review'))
    args=parser.parse_args()
    manifest=json.loads(args.manifest.read_text(encoding='utf-8'))
    image_path=args.image or ROOT/manifest['art']['path']
    source_bytes=image_path.read_bytes()
    with Image.open(io.BytesIO(source_bytes)) as original:
        report=export(original.convert('RGB'),manifest,source_bytes,args.out)
    print(json.dumps({'samples':report['totalReviewSamples'], 'output':str(args.out),
                      'sourceGitBlobSha':report['sourceGitBlobSha'], 'productionEnabled':False}))


if __name__=='__main__':
    main()
