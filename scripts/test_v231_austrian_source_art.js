/* V231 fail-closed source/approval tests; not a human art acceptance test. */
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const loader=require('../terrain-grid/v231-austrian-source-art.js');
const root=path.resolve(__dirname,'..');
const dir=path.join(root,'terrain-v231/assets');
const m=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8'));
assert.equal(loader.verify(m),true);
assert.equal(m.sourceRegisteredToV123,false);
assert.equal(m.productionApproved,false);
for(const id of ['west','south']){
 const src=m.sources[id],file=path.join(dir,src.file),data=fs.readFileSync(file);
 assert.equal(crypto.createHash('sha256').update(data).digest('hex'),src.outputSha256);
 assert.equal(data.subarray(0,4).toString('ascii'),'RIFF');
 assert.equal(data.subarray(8,12).toString('ascii'),'WEBP');
 assert.equal(src.nativePixels.join(','),'1536,1024');
 assert.equal(src.author,id==='west'?'Stijn te Strake':'Volker Schnäbele');
 assert.equal(src.license,'CC0 1.0');
}
const copy=()=>structuredClone(m);
function rejected(mutate){const bad=copy();mutate(bad);assert.throws(()=>loader.verify(bad));}
rejected(m=>m.productionApproved=true);
rejected(m=>m.sourceLandmarkTiepointsVerified=true);
rejected(m=>m.selectionIsSemanticVerification=true);
rejected(m=>m.sources.west.nonrepeatingGroundStrip=null);
rejected(m=>m.sourceRegisteredToV123=true);
rejected(m=>m.notHistorical1780Geography=false);
rejected(m=>m.cartwaysAndBridgeBanksNotSurveyed=false);
rejected(m=>m.sources.south.sourceSha256=m.sources.west.sourceSha256);
rejected(m=>m.sources.west.outputSha256='0'.repeat(64).slice(0,63));
rejected(m=>m.sources.south.nativePixels=[1024,1024]);
rejected(m=>m.sources.west.author='unknown');\nrejected(m=>m.sources.south.sourceSha1='x'.repeat(40));
rejected(m=>m.sources.west.license='unspecified');
rejected(m=>m.sources.south.humanVisualApproval=true);
console.log('V231 source-integrity, native assets, and false-approval negative controls PASS; human art still RED');
