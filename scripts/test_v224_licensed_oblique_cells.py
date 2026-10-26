#!/usr/bin/env python3
"""V224 fail-closed source provenance and visual approval negative controls."""
import copy,json,tempfile
from pathlib import Path
import v224_licensed_oblique_cells as art

def must_reject(mutator):
 with tempfile.TemporaryDirectory(prefix='v224-negative-') as temp:
  old=art.DIR
  try:
   art.DIR=Path(temp)
   (art.DIR/'assets').mkdir()
   m=json.loads((old/'assets'/'manifest.json').read_text())
   mutator(m)
   (art.DIR/'assets'/'manifest.json').write_text(json.dumps(m))
   try:art.verify()
   except (ValueError,KeyError,AssertionError):return
   raise AssertionError('V224 negative control falsely accepted')
  finally:art.DIR=old

def main():
 m=art.verify()
 assert m['humanVisualApproval'] is False
 assert m['knownModernRoadVisibleInSouth'] is True
 assert m['actualSourceRegion'].startswith('Sharr Mountains, Kosovo')
 assert all(s['license']=='CC BY 4.0' for s in m['sources'])
 assert len({s['sourceSha256'] for s in m['sources']})==2
 for flag in art.FALSE:
  must_reject(lambda x,k=flag:x.__setitem__(k,True))
 must_reject(lambda x:x.__setitem__('humanVisualApproval',True))
 must_reject(lambda x:x.__setitem__('modernFeaturesFullyExcluded',True))
 must_reject(lambda x:x.__setitem__('knownModernRoadVisibleInSouth',False))
 must_reject(lambda x:x.__setitem__('actualSourceRegion','Matrei Austria 1780'))
 must_reject(lambda x:x['sources'][1].__setitem__('sourceSha256',x['sources'][0]['sourceSha256']))
 must_reject(lambda x:x['sources'][0].__setitem__('sourceRect',[0,0,1536,1024]))
 must_reject(lambda x:x['sources'][0].__setitem__('license','unknown'))
 must_reject(lambda x:x['sources'][1].__setitem__('outputSha256','0'*64))
 print('V224 source, modern-feature and approval negative controls PASS; ART STILL NOT APPROVED')
if __name__=='__main__':main()
