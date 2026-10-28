#!/usr/bin/env python3
"""V260 fail-closed synthetic and optional exact-original image regressions."""
import os, unittest
import cv2
import numpy as np
from v260_single_pass_native_south import (
    compose_maps, correction_maps, render, PINS, quality_report
)

class TestV260(unittest.TestCase):
    def test_source_hash_pinned(self):
        self.assertEqual(PINS['south'],
          '034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3')

    def test_composition_identity(self):
        y,x=np.indices((1024,1536),dtype=np.float32)
        mx,my=compose_maps(x,y,x,y)
        self.assertLess(np.max(np.abs(mx-x)),1e-3)
        self.assertLess(np.max(np.abs(my-y)),1e-3)

    def test_bad_source_fails_closed(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png') as f:
            f.write(b'not the pinned image');f.flush()
            with self.assertRaises(ValueError):render(f.name)

    def test_no_production_approval(self):
        y,x=np.indices((1024,1536),dtype=np.float32)
        r=quality_report(x,y)
        for key in ('historicalRoadVerified','independentGeographicTiepointsVerified',
                    'bridgeBanksVerified','strictV203Passed',
                    'exactArtFourBrowserPassed','userApproved','productionApproved'):
            self.assertIs(r[key],False)

    def test_correction_map_no_fold(self):
        x,y=correction_maps()
        r=quality_report(x,y)
        self.assertGreater(r['minSampledJacobian'],.5)
        self.assertEqual(r['sampledFoldedFraction'],0)

    @unittest.skipUnless(os.environ.get('V260_ORIGINAL_SOUTH'),
      'Exact original PNG is local-only, not hosted in CI')
    def test_actual_original_one_pass_detail(self):
        out,qa,_=render(os.environ['V260_ORIGINAL_SOUTH'])
        self.assertEqual(out.shape,(1024,1536,3))
        self.assertEqual(qa['sampledFoldedFraction'],0)
        self.assertGreater(qa['minSampledJacobian'],.5)
        self.assertGreater(qa['nativeSourceCoverage'],.998)
        reference=os.environ.get('V259_REFERENCE_SOUTH')
        if reference:
            prior=cv2.imread(reference)
            self.assertEqual(prior.shape,out.shape)
            x1,y1,x2,y2=(460,280,1100,600)
            def hf(im):
                g=cv2.cvtColor(im[y1:y2,x1:x2],cv2.COLOR_BGR2GRAY).astype(np.float32)
                return float(np.mean(np.abs(cv2.Laplacian(g,cv2.CV_32F))))
            self.assertGreater(hf(out),hf(prior)*1.03)
            self.assertLess(float(np.mean(np.abs(out.astype(np.float32)-prior.astype(np.float32)))),4)

if __name__=='__main__':unittest.main()
