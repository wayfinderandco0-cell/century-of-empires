#!/usr/bin/env python3
"""V266 isolated Matrei native-photo edge reveal, never production approval.

Only two alpha expressions and an explicit title change in an exact SHA-pinned
V265 local HTML. Original V121/WEST/SOUTH pixels, V123 roads and gameplay stay intact.
"""
import argparse
import hashlib
import json
from pathlib import Path

BASE_SHA256 = '1d267eb96ba5b1e60f3dcb0b83fa898afc41c580d3c141fcf18f8ecdcf9dfe9a'
OLD_MASK = 'smooth((d-12-featherOffset)/280)'
NEW_MASK = 'smooth((d-22-featherOffset)/145)'
OLD_FOCUS = 'smooth((1.20-radius-irregular)/.59)'
NEW_FOCUS = 'smooth((1.17-radius-irregular)/.33)'
OLD_TITLE = 'V265 SOUTH SHADOW DETAIL RECOVERY - UNAPPROVED'
NEW_TITLE = 'V266 MATREI NATIVE EDGE REVEAL - UNAPPROVED'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def transform(html, *, require_exact_base=False):
    if require_exact_base and digest(html.encode()) != BASE_SHA256:
        raise ValueError('V265 exact offline HTML SHA256 mismatch')
    if 'V264_SEAM_UNDERLAY' in html:
        raise ValueError('V264 reflected seam must not be inherited')
    for marker in (OLD_MASK, OLD_FOCUS, OLD_TITLE,
                   'const V263_PINS=', 'const V263_IMAGES='):
        if html.count(marker) != 1:
            raise ValueError('missing or duplicated fail-closed marker: '+marker)
    for marker in ('get productionApproved(){return false}', 'V263ImportPair'):
        if marker not in html:
            raise ValueError('missing fail-closed marker: '+marker)
    result = html.replace(OLD_MASK, NEW_MASK).replace(OLD_FOCUS, NEW_FOCUS)
    result = result.replace(OLD_TITLE, NEW_TITLE)
    assert result.count(NEW_MASK) == result.count(NEW_FOCUS) == 1
    assert result.count('get productionApproved(){return false}') == html.count('get productionApproved(){return false}')
    return result

def build(source, destination):
    raw = Path(source).read_bytes()
    if digest(raw) != BASE_SHA256:
        raise ValueError('V265 exact HTML SHA256 mismatch')
    original = raw.decode('utf-8')
    result = transform(original)
    restored = (result.replace(NEW_MASK, OLD_MASK)
                      .replace(NEW_FOCUS, OLD_FOCUS)
                      .replace(NEW_TITLE, OLD_TITLE))
    if restored != original:
        raise ValueError('unexpected non-art change')
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    Path(destination).write_bytes(result.encode('utf-8'))
    return {'version':266,'inputSHA256':digest(raw),
            'outputSHA256':digest(Path(destination).read_bytes()),
            'matreiOriginalPixelsPreserved':True,
            'westAndSouthImagesUnchanged':True,
            'v123RoutesAndArmyUnchanged':True,
            'newTerrainFeaturesCreated':False,
            'independentGeographicRegistration':False,
            'historicalRoadsVerified':False,
            'bridgeBanksVerified':False,
            'exactWebKitArtTestPassed':False,
            'userVisualApproval':False,'productionApproved':False}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('v265_offline_html', type=Path)
    parser.add_argument('v266_offline_html', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.v265_offline_html, args.v266_offline_html), indent=2))
