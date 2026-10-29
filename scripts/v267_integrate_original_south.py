#!/usr/bin/env python3
"""Stage one ORIGINAL SOUTH terrain source into the isolated V267 art preview.

This is a source-art integration command, not a renderer/graph rewrite. It never
touches Matrei V121, V123, the V94 campaign, sprites, saves or production main.
The candidate is fictional Alpine game art, NOT verified historic topography.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "v267-three-octagon-original-art-prototype.html"
ART_DIR = ROOT / "art-reviews" / "v267-original-source"
ART_FILE = ART_DIR / "south-overhead-ground-unapproved.jpg"
MANIFEST = ART_DIR / "south-overhead-ground-unapproved.json"
REVIEW = ROOT / "art-reviews" / "v267-south-overhead-review-unapproved.html"

def replace_source(html: str, source: bytes) -> str:
    # Replace exactly one source-art string. Do not alter V121/V123 JavaScript.
    marker = r'ART_SOUTH="data:image/jpeg;base64,[^"]+"'
    new = 'ART_SOUTH="data:image/jpeg;base64,' + base64.b64encode(source).decode("ascii") + '"'
    changed, count = re.subn(marker, lambda _m: new, html, count=1)
    if count != 1:
        raise ValueError("Could not locate the single embedded SOUTH JPEG")
    # No changes outside the embedded SOUTH source are permitted.
    old_rest = re.sub(marker, "ART_SOUTH=SOURCE", html, count=1)
    new_rest = re.sub(marker, "ART_SOUTH=SOURCE", changed, count=1)
    if old_rest != new_rest:
        raise AssertionError("Unexpected changes to the V267 preview")
    return changed

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path, help="new original 1536x1024 SOUTH image")
    ap.add_argument("--write-review", action="store_true", help="write source, manifest and isolated review HTML")
    args = ap.parse_args()
    source = args.source.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    with Image.open(source) as raw:
        if raw.size != (1536, 1024):
            raise ValueError(f"Expected 1536x1024, got {raw.size}")
        image = raw.convert("RGB")
    import io
    out = io.BytesIO()
    image.save(out, "JPEG", quality=93, subsampling=0, optimize=True)
    data = out.getvalue()
    html = PREVIEW.read_text(encoding="utf-8")
    changed = replace_source(html, data)
    digest = hashlib.sha256(data).hexdigest()
    info = {
        "status": "UNAPPROVED",
        "source_file": str(source),
        "image_dimensions": [1536, 1024],
        "jpeg_sha256": digest,
        "bytes": len(data),
        "road_graph": "V123 unchanged; west (1536,478)/(0,478), south (466,1024)/(466,0)",
        "source_provenance": "fictional original Alpine game art, not verified historic topography",
        "required_review": "actual iPhone Safari road/forest/seam visual approval",
    }
    if args.write_review:
        ART_DIR.mkdir(parents=True, exist_ok=True)
        ART_FILE.write_bytes(data)
        MANIFEST.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
        REVIEW.write_text(changed, encoding="utf-8")
        print(f"STAGED {ART_FILE.relative_to(ROOT)} and {REVIEW.relative_to(ROOT)}")
    else:
        print("DRY RUN; use --write-review to stage the separate unapproved review.")
    print(json.dumps(info, indent=2))

if __name__ == "__main__":
    main()
