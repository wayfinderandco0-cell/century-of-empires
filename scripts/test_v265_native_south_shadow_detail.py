#!/usr/bin/env python3
"""V265 fail-closed, additive artwork tests. Passing != production approval."""
import base64,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v265',ROOT/'scripts/v265_native_south_shadow_detail.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class NativeShadowDetail(unittest.TestCase):
    def test_dark_detail_recovery_not_synthetic_noise(self):
        y,x=np.mgrid[0:1024,0:1536]
        v=(18+18*(x/1535)+9*np.sin(x/17)+6*np.sin(y/23)).clip(0,255).astype('uint8')
        a=np.stack([v,v,v],axis=2)
        b=mod.recover(a)
        self.assertEqual(b.shape,a.shape)
        self.assertEqual(b.dtype,np.uint8)
        self.assertGreater(float(b.mean()),float(a.mean())+5)
        self.assertGreater(float(b.std()),float(a.std())*.85)
        self.assertTrue(np.array_equal(mod.recover(a),b),'deterministic, no random texture')
        with self.assertRaises(ValueError):mod.recover(a,clip=4)
    def test_js_embedded_hashes_fail_closed_and_no_production_approval(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);source=p/'south.png';out=p/'new.png';html=p/'base.html';result=p/'new.html'
            Image.new('RGB',(1536,1024),(30,42,24)).save(source)
            raw=source.read_bytes();sha=mod.digest(raw)
            oldpin=mod.ORIGINAL_WEST_SHA
            body=('const V263_PINS='+json.dumps({'west':oldpin,'south':sha})+';\n'
                  'const V263_IMAGES='+json.dumps({'west':'d2VzdA==','south':base64.b64encode(raw).decode()})+';\n'
                  'V263ImportPair;get productionApproved(){return false};V263 OFFLINE EXACT-ART PLAYABLE CANDIDATE')
            html.write_text(body)
            rep=mod.build(html,source,out,result,expected_south=sha)
            updated=result.read_text()
            self.assertIn(rep['southRecoveredSHA256'],updated)
            self.assertIn('get productionApproved(){return false}',updated)
            self.assertNotIn('V264_SEAM_UNDERLAY',updated)
            self.assertFalse(rep['productionApproved'])
            with self.assertRaises(ValueError):mod.build(html,source,out,result,expected_south='0'*64)
            html.write_text(body.replace('V263ImportPair','V264_SEAM_UNDERLAY;V263ImportPair'))
            with self.assertRaises(ValueError):mod.build(html,source,out,result,expected_south=sha)
    def test_exact_source_if_present(self):
        import os
        original=os.environ.get('COE_V265_ORIGINAL_SOUTH')
        if not original:self.skipTest('exact original fictional art is local-only; CI cannot approve it')
        self.assertEqual(mod.digest(Path(original).read_bytes()),mod.ORIGINAL_SOUTH_SHA)

if __name__=='__main__':unittest.main()
