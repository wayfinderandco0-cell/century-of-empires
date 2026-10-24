#!/usr/bin/env python3
"""Fail-closed V123 game-frame -> modern geographic-source candidate registration.

Two independent landmark controls determine a similarity transform; a THIRD,
unused holdout must agree. Never edits game routes, paints roads, or grants
historical/visual/production approval. Real matching evidence is still missing.
"""
import argparse
import json
import math
from pathlib import Path
from urllib.parse import urlsplit

CORRIDORS = ('western_pass', 'matrei', 'southern_valley')
MAX_RELATIVE_HOLDOUT_ERROR = 0.02
MIN_HOLDOUT_OFFSET = 0.20
MIN_TRIANGLE_AREA = 0.025


def require(condition, message):
    if not condition:
        raise ValueError(message)


def point(value, label):
    require(isinstance(value, list) and len(value) == 2 and
            all(type(v) in (float, int) and math.isfinite(v) for v in value),
            f'{label}: expected two finite numeric coordinates')
    return tuple(value)


def evidence_url(value, label):
    require(isinstance(value, str), f'{label}: missing evidence URL')
    u = urlsplit(value)
    require(u.scheme == 'https' and bool(u.hostname) and u.hostname not in
            ('localhost', 'example.com', 'example.org', 'example.net'),
            f'{label}: require actual HTTPS evidence URL')


def fit_two_controls(a, b):
    g0, g1 = a['game'], b['game']
    s0, s1 = a['source'], b['source']
    dx, dy = g1[0]-g0[0], g1[1]-g0[1]
    ux, uy = s1[0]-s0[0], s1[1]-s0[1]
    denom = dx*dx + dy*dy
    require(denom >= 2500, 'control points must be separated by >=50 game pixels')
    require(ux*ux + uy*uy >= 2500, 'source controls must be separated by >=50 pixels')
    aa = (dx*ux + dy*uy)/denom
    bb = (dx*uy - dy*ux)/denom
    tx = s0[0]-aa*g0[0]+bb*g0[1]
    ty = s0[1]-bb*g0[0]-aa*g0[1]
    return aa, bb, tx, ty


def project(transform, xy):
    a, b, tx, ty = transform
    return (a*xy[0]-b*xy[1]+tx, b*xy[0]+a*xy[1]+ty)


def validate_corridor(name, records, frame):
    require(isinstance(records, list), f'{name}: matches must be a list')
    if not records:
        return {'status': 'BLOCKED_MISSING_REAL_LANDMARK_MATCHES', 'candidateTransformValidated': False}
    require(len(records) == 3, f'{name}: require exactly 2 controls and 1 independent holdout')
    ids, gpoints, spoints = set(), set(), set()
    controls, holdouts = [], []
    for row in records:
        require(isinstance(row, dict), f'{name}: malformed landmark')
        require(set(row) == {'id', 'role', 'game', 'source', 'gameEvidenceUrl',
                             'sourceEvidenceUrl', 'reviewedBy'}, f'{name}: unknown/missing evidence fields')
        ident = row['id']
        require(isinstance(ident, str) and len(ident.strip()) >= 4 and ident not in ids,
                f'{name}: duplicate/invalid landmark ID')
        ids.add(ident)
        require(row['role'] in ('control', 'holdout'), f'{name}: unknown landmark role')
        g, s = point(row['game'], f'{name} game'), point(row['source'], f'{name} source')
        require(g not in gpoints and s not in spoints, f'{name}: duplicated landmark coordinates')
        gpoints.add(g); spoints.add(s)
        require(0 <= g[0] <= 4608 and 0 <= g[1] <= 1024,
                f'{name}: outside three-cell V123 study game frame')
        require(0 <= s[0] < frame['width'] and 0 <= s[1] < frame['height'],
                f'{name}: source point outside declared raster')
        evidence_url(row['gameEvidenceUrl'], f'{name} game')
        evidence_url(row['sourceEvidenceUrl'], f'{name} source')
        require(isinstance(row['reviewedBy'], str) and len(row['reviewedBy'].strip()) >= 3,
                f'{name}: reviewer attribution required')
        item = {'id': ident, 'game': g, 'source': s}
        (controls if row['role'] == 'control' else holdouts).append(item)
    require(len(controls) == 2 and len(holdouts) == 1,
            f'{name}: require 2 controls and 1 withheld holdout')
    a, b, h = *controls, holdouts[0]
    baseline = math.dist(a['game'], b['game'])
    require(min(math.dist(h['game'], a['game']), math.dist(h['game'], b['game'])) >=
            MIN_HOLDOUT_OFFSET*baseline,
            f'{name}: holdout too close to control')
    triangle = abs((b['game'][0]-a['game'][0])*(h['game'][1]-a['game'][1]) -
                   (b['game'][1]-a['game'][1])*(h['game'][0]-a['game'][0]))/2
    require(triangle >= MIN_TRIANGLE_AREA*baseline**2,
            f'{name}: nearly collinear holdout cannot test 2D fit')
    transform = fit_two_controls(a, b)
    predicted = project(transform, h['game'])
    error = math.dist(predicted, h['source'])
    source_baseline = math.dist(a['source'], b['source'])
    relative = error/source_baseline
    require(relative <= MAX_RELATIVE_HOLDOUT_ERROR,
            f'{name}: holdout residual {relative:.4%} exceeds 2% control baseline')
    return {'status': 'CANDIDATE_FIT_ONLY_NOT_GEOGRAPHICALLY_APPROVED',
            'candidateTransformValidated': True,
            'controlLandmarks': [a['id'], b['id']], 'holdoutLandmark': h['id'],
            'gameToSourceSimilarity': [round(v, 9) for v in transform],
            'holdoutErrorSourcePixels': round(error, 5),
            'holdoutErrorFractionOfControlBaseline': round(relative, 7)}


def audit(data):
    require(isinstance(data, dict) and set(data) == {'schemaVersion', 'sourceFrame', 'corridors'},
            'unexpected registration manifest schema')
    require(data['schemaVersion'] == 1, 'unsupported manifest version')
    frame = data['sourceFrame']
    require(isinstance(frame, dict) and set(frame) ==
            {'id', 'width', 'height', 'referenceUrl', 'modernReferenceOnly'},
            'source frame must be explicitly identified')
    require(isinstance(frame['id'], str) and len(frame['id']) >= 4, 'missing source ID')
    require(type(frame['width']) is int and type(frame['height']) is int and
            frame['width'] > 100 and frame['height'] > 100, 'invalid source dimensions')
    evidence_url(frame['referenceUrl'], 'source frame')
    require(frame['modernReferenceOnly'] is True, 'source cannot be claimed historical')
    corridors = data['corridors']
    require(isinstance(corridors, dict) and set(corridors) == set(CORRIDORS),
            'all three real GAME corridors required; no unknown corridors')
    findings = {name: validate_corridor(name, corridors[name], frame) for name in CORRIDORS}
    all_valid = all(v['candidateTransformValidated'] for v in findings.values())
    return {'version': 163, 'sourceFrameId': frame['id'], 'corridors': findings,
            'allThreeCandidateFitsValidated': all_valid,
            'gameRouteGeoregistered': False, 'historicalRoadsVerified': False,
            'bridgeBanksVerified': False, 'periodArtComplete': False,
            'threeOctagonsVisuallyApproved': False, 'productionApproved': False,
            'note': 'Candidate similarity fits cannot establish historical roads, bridge banks, art quality or approval.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--allow-blocked', action='store_true',
                        help='CI may report an intentionally empty evidence manifest without approving it')
    args = parser.parse_args()
    report = audit(json.loads(args.evidence.read_text()))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'allThreeCandidateFitsValidated': report['allThreeCandidateFitsValidated'],
                      'statuses': {k: v['status'] for k, v in report['corridors'].items()}}, indent=2))
    if not report['allThreeCandidateFitsValidated'] and not args.allow_blocked:
        raise SystemExit(2)

if __name__ == '__main__':
    main()
