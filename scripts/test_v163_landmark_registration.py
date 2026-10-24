#!/usr/bin/env python3
"""Synthetic control/holdout tests. No fixtures are claimed as real Alpine landmarks."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import v163_landmark_registration as reg

BASE = {
    'schemaVersion': 1,
    'sourceFrame': {'id': 'synthetic-test-raster', 'width': 4000, 'height': 3000,
                    'referenceUrl': 'https://www.openstreetmap.org/', 'modernReferenceOnly': True},
    'corridors': {k: [] for k in reg.CORRIDORS}
}


def matches():
    # Artificial 90-degree rotation with scale 2, translation (1500,600).
    return [{'id': name, 'role': role, 'game': [x,y], 'source': [1500-2*y, 600+2*x],
             'gameEvidenceUrl': f'https://www.openstreetmap.org/node/{i+100}',
             'sourceEvidenceUrl': f'https://www.openstreetmap.org/node/{i+200}',
             'reviewedBy': 'synthetic-test-only'}
            for i,(name,role,x,y) in enumerate([
                ('control-north', 'control', 300, 300),
                ('control-east', 'control', 500, 300),
                ('holdout-south', 'holdout', 410, 440)])]


class RegistrationTests(unittest.TestCase):
    def filled(self):
        d = copy.deepcopy(BASE)
        for k in reg.CORRIDORS:
            d['corridors'][k] = matches()
        return d

    def test_empty_real_evidence_blocks_every_corridor(self):
        result = reg.audit(copy.deepcopy(BASE))
        self.assertFalse(result['allThreeCandidateFitsValidated'])
        self.assertEqual(len(result['corridors']), 3)
        self.assertTrue(all(not v['candidateTransformValidated'] for v in result['corridors'].values()))
        self.assertFalse(result['productionApproved'])

    def test_exact_synthetic_similarity_with_independent_holdout(self):
        report = reg.audit(self.filled())
        self.assertTrue(report['allThreeCandidateFitsValidated'])
        for v in report['corridors'].values():
            self.assertEqual(v['holdoutErrorSourcePixels'], 0)
            self.assertEqual(v['gameToSourceSimilarity'], [0, 2, 1500, 600])
        for field in ('gameRouteGeoregistered', 'historicalRoadsVerified',
                      'bridgeBanksVerified', 'periodArtComplete',
                      'threeOctagonsVisuallyApproved', 'productionApproved'):
            self.assertFalse(report[field], field)

    def test_partial_coverage_remains_blocked(self):
        d = self.filled(); d['corridors']['southern_valley'] = []
        self.assertFalse(reg.audit(d)['allThreeCandidateFitsValidated'])

    def test_holdout_mismatch_fails(self):
        d = self.filled(); d['corridors']['matrei'][2]['source'][0] += 35
        with self.assertRaisesRegex(ValueError, 'holdout residual'):
            reg.audit(d)

    def test_collinear_holdout_fails(self):
        d = self.filled(); r = d['corridors']['matrei'][2]
        r['game'] = [410, 300]; r['source'] = [900, 1420]
        with self.assertRaisesRegex(ValueError, 'collinear'):
            reg.audit(d)

    def test_near_duplicate_controls_fail(self):
        d = self.filled(); r = d['corridors']['matrei'][1]
        r['game'] = [301, 300]; r['source'] = [900, 1202]
        with self.assertRaisesRegex(ValueError, 'separated'):
            reg.audit(d)

    def test_duplicate_landmark_ids_fail(self):
        d = self.filled(); d['corridors']['matrei'][1]['id'] = 'control-north'
        with self.assertRaisesRegex(ValueError, 'duplicate/invalid'):
            reg.audit(d)

    def test_out_of_bounds_game_or_source_fails(self):
        for key, xy in [('game', [4700, 300]), ('source', [4001, 1200])]:
            d = self.filled(); d['corridors']['matrei'][1][key] = xy
            with self.assertRaises(ValueError):
                reg.audit(d)

    def test_unreviewed_or_non_https_evidence_fails(self):
        for key, val in [('reviewedBy', ''), ('gameEvidenceUrl', 'http://example.com'),
                         ('sourceEvidenceUrl', 'https://example.org/fake')]:
            d = self.filled(); d['corridors']['matrei'][1][key] = val
            with self.assertRaises(ValueError):
                reg.audit(d)

    def test_extra_unverified_role_fails(self):
        d = self.filled(); d['corridors']['matrei'][2]['role'] = 'control'
        with self.assertRaisesRegex(ValueError, '2 controls'):
            reg.audit(d)

    def test_historical_claim_and_extra_corridor_fail(self):
        d = self.filled(); d['sourceFrame']['modernReferenceOnly'] = False
        with self.assertRaisesRegex(ValueError, 'historical'):
            reg.audit(d)
        d = self.filled(); d['corridors']['fictional_pass'] = []
        with self.assertRaisesRegex(ValueError, 'three real GAME corridors'):
            reg.audit(d)

    def test_missing_evidence_file_not_implicitly_approved(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                (Path(td)/'missing.json').read_text()

if __name__ == '__main__':
    unittest.main()
