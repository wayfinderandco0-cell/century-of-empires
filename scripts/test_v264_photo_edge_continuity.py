#!/usr/bin/env python3
"""V264 fail-closed source-pixel seam study tests. NOT geographic or art approval."""
import importlib.util,hashlib,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v264',ROOT/'scripts/v264_photo_edge_continuity.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class EdgeTests(unittest.TestCase):
 def test_reflected_source_contact_and_fade(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);w=p/'west.png';s=p/'south.png'
   Image.new('RGB',(1536,1024),(31,79,123)).save(w)
   Image.new('RGB',(1536,1024),(151,98,36)).save(s)
   patch=mod.make_patch(w,s)
   self.assertEqual(patch.size,(1536,1024))
   self.assertEqual(patch.getpixel((0,478)),(31,79,123,255))
   self.assertEqual(patch.getpixel((466,1023)),(151,98,36,255))
   self.assertEqual(patch.getpixel((500,400))[3],0)
   self.assertEqual(patch.getpixel((375,400))[3],0)
   self.assertEqual(patch.getpixel((500,648))[3],0)
   self.assertTrue(0<patch.getpixel((240,400))[3]<255)
   self.assertTrue(0<patch.getpixel((500,800))[3]<255)

 def test_original_renderer_and_graph_preserved(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);w=p/'west.png';s=p/'south.png';base=p/'v263.html';out=p/'v264.html'
   Image.new('RGB',(1536,1024),(31,79,123)).save(w)
   Image.new('RGB',(1536,1024),(151,98,36)).save(s)
   src=("<script>const westRoad=[[1536,478]];const southRoad=[[466,0]];\n"
    "let staticFrame=null,staticDirty=true,staticBuilds=0,cacheHits=0,dynamicFrames=0;\n"
    "if(showPainted)V227ArtIngest.paint(cx);\n"
    "if(centerPhoto)cx.drawImage(centerPhoto,1536,0,W,H);\n"
    "get productionApproved(){return false};async function V263ImportPair(){};"
    "V263 OFFLINE EXACT-ART</script>")
   base.write_text(src)
   original=mod.EXPECTED
   try:
    mod.EXPECTED={k:hashlib.sha256(f.read_bytes()).hexdigest() for k,f in [('west',w),('south',s)]}
    report=mod.build(base,w,s,out)
    html=out.read_text()
    self.assertIn('V264_SEAM_UNDERLAY',html)
    self.assertIn('const westRoad=[[1536,478]];const southRoad=[[466,0]];',html)
    self.assertEqual(html.count('if(centerPhoto)cx.drawImage(centerPhoto,1536,0,W,H);'),1)
    self.assertIn('get productionApproved(){return false}',html)
    self.assertIn('V263_PINS[c.id]===c.sha256',html)
    self.assertGreater(report['patch_bytes'],1000)
    self.assertFalse(report['productionApproved'])
    with self.assertRaises(ValueError):mod.build(base,s,w,p/'wrong.html')
    with self.assertRaises(ValueError):mod.build(out,w,s,p/'twice.html')
   finally:mod.EXPECTED=original

 def test_original_images_if_available(self):
  import os
  w=os.environ.get('COE_V264_WEST');s=os.environ.get('COE_V264_SOUTH')
  if not w or not s:self.skipTest('original fictional PNGs are intentionally not hosted in CI')
  self.assertEqual(mod.sha(w),mod.EXPECTED['west'])
  self.assertEqual(mod.sha(s),mod.EXPECTED['south'])

if __name__=='__main__':unittest.main()
