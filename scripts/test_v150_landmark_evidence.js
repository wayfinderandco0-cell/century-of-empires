#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const evidence=require('../terrain-grid/v150-landmark-evidence.js');
if(process.argv.length!==5) throw Error('Usage: node scripts/test_v150_landmark_evidence.js <downloaded manifest> <observations.json> <output.json>');
const manifest=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const observations=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const report=evidence.packet(manifest,observations);
assert.equal(report.observations.length,3);
assert.equal(report.provider,'basemap.at');
assert.equal(report.productionApproved,false);
assert.equal(report.v123RoadsMapped,false);
assert.equal(report.bridgeBanksVerified,false);
assert.equal(report.historic1780Certified,false);
assert.equal(report.v123RouteTiePoints.length,0);
for(const f of report.observations){
  assert.equal(f.matchedV123RoadVertex,null);
  assert.equal(f.matchedGameOctagon,null);
  assert.equal(f.visualLandmarkAuthenticated,false);
  assert.match(f.sourceTileSha256,/^[a-f0-9]{64}$/);
  assert.ok(f.lonLat[0]>11.516&&f.lonLat[0]<11.525);
  assert.ok(f.lonLat[1]>47.128&&f.lonLat[1]<47.134);
}
const clone=x=>JSON.parse(JSON.stringify(x));
let n=0;
function reject(mutator,pattern){
  const m=clone(manifest),o=clone(observations);
  mutator(m,o);
  assert.throws(()=>evidence.packet(m,o),pattern);
  n++;
}
reject((m)=>{delete m.mosaicSha256},/hashes/);
reject((m)=>{m.samples[4].sha256='unverified'},/hashes/);
reject((m)=>{m.samples[4].tileXYZ[0]++},/adjacency/);
reject((m)=>{m.productionApproved=true},/cannot assert/);
reject((m,o)=>{o[0].matchedV123RoadVertex='west:0'},/game-linked/);
reject((m,o)=>{o[0].historicalRoadVerified=true},/game-linked/);
reject((m,o)=>{o[0].pixel=[768,50]},/outside/);
reject((m,o)=>{o[0].pixel=[NaN,20]},/constrained/);
reject((m,o)=>{o[0].status='approved'},/status/);
reject((m,o)=>{o[1].id=o[0].id},/duplicate/);
reject((m,o)=>{o[0].type='1780-certified-road'},/type/);
reject((m,o)=>{o[0].description='short'},/status/);
reject((m,o)=>{o.length=0},/At least one/);
fs.writeFileSync(process.argv[4],JSON.stringify(report,null,2)+'\n');
console.log('V150: 3 modern source observations have exact GPS/pixel/hashed-tile provenance; '+n+' fail-closed tests passed. Zero V123 matches or historical/production claims.');
