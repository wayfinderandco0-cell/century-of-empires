#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const audit=require('../terrain-grid/v151-frame-provenance.js');
if(process.argv.length!==6) throw Error('Usage: node scripts/test_v151_frame_provenance.js <V121 html> <V147 downloaded manifest> <V150 observations> <report output>');
const html=fs.readFileSync(process.argv[2],'utf8');
const manifest=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const observations=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
const result=audit.audit(html,manifest,observations);
assert.equal(audit.assertNoUnreviewedPromotion(result),true);
assert.equal(result.originalArt.gitBlobSha1,audit.V121_HTML_GIT_BLOB);
assert.deepEqual(result.originalArt.dimensions,[1536,1024]);
assert.match(result.originalArt.imageSha256,/^[a-f0-9]{64}$/);
assert.equal(result.modernSource.mosaicSha256,audit.V150_SOURCE_MOSAIC_SHA256);
assert.equal(result.modernSource.candidateCount,3);
assert.equal(result.geographicFramesMatched,false);
assert.equal(result.sourceImageryIsGameArt,false);
assert.equal(result.productionApproved,false);
const copy=x=>JSON.parse(JSON.stringify(x));
let negative=0;
function reject(mutator,pattern){
  const m=copy(manifest),o=copy(observations);
  const h=mutator(m,o)??html;
  assert.throws(()=>audit.audit(h,m,o),pattern);negative++;
}
reject((m)=>{m.mosaicSha256='a'.repeat(64)},/hash differs/);
reject((m)=>{delete m.mosaicSha256},/hash differs/);
reject((m)=>{m.samples[0].sha256='not-a-hash'},/hashes required/);
reject((m)=>{m.samples[1].tileXYZ[0]++},/adjacency/);
reject((m)=>{m.gameRouteGeoregistered=true},/cannot assert/);
reject((m,o)=>{o[0].matchedV123RoadVertex='matrei:west:0'},/game-linked/);
reject((m,o)=>{o[0].historicalRoadVerified=true},/game-linked/);
reject((m,o)=>{o[0].status='approved'},/status/);
reject((m,o)=>{o[0].pixel=[769,10]},/outside/);
reject((m,o)=>{o[1].id=o[0].id},/duplicate/);
reject(()=>html.replace('Century of Empires · Octagon 1','Century of Empires · altered'),/identity changed/);
for(const field of ['geographicFramesMatched','sourceImageryIsGameArt','bridgeBanksVerified','navigableRouteCertified','historic1780Certified','physicalIPhoneApproved','productionApproved']){
  const r=copy(result);r[field]=true;
  assert.throws(()=>audit.assertNoUnreviewedPromotion(r),/must not enable/);negative++;
}
for(const tile of ['west','matrei','south']){
  const r=copy(result);r.gameOctagons[tile].independentMatchedControls=3;
  assert.throws(()=>audit.assertNoUnreviewedPromotion(r),/must not enable/);negative++;
}
fs.writeFileSync(process.argv[5],JSON.stringify(result,null,2)+'\n');
console.log('V151: original V121 WebP identity verified, 9 modern source images provenance-locked, 3 source-only candidates NOT promoted; '+negative+' fail-closed negative cases PASS. NO matched geographic frames or game art approval.');
