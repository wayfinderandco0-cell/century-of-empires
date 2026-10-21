/* Run: node --test tests/test_v116_road_graph.js */
"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const graphLib=require("../scripts/v116_road_graph.js");
const candidate=require("../terrain-grid/v116-bridge-painted-candidate.json");
const source=require("../terrain-grid/v115-route-provenance.json");
const tiles=require("../terrain-grid/v115-local-tiles-v116.json");
const render=require("../scripts/v116_local_art_renderer.js");
const graph=()=>graphLib.build({south:source.rawPath,bridge:candidate.bridgeCenterlineArtPx,
  forkIndex:source.forkIndex,imageSize:[1100,842]});
test("fixture is exact V115 image and does not grant gameplay rights",()=>{
 assert.equal(candidate.sourceV115BlobSha,source.source.githubBlobSha);
 const g=graph();assert.equal(g.approvedForProduction,false);
 assert.equal(g.conquerable,false);assert.equal(g.bridgeTerminal,"visible-far-bank-only");
 assert.equal(tiles.verification.playableRouteTiles,0);
});
test("three connected road edges share precisely one fork",()=>{
 const g=graph();assert.deepEqual(g.edges.approach.at(-1),g.forkPoint);
 assert.deepEqual(g.edges.south[0],g.forkPoint);
 assert.deepEqual(g.edges.bridge[0],g.forkPoint);
 assert.notDeepEqual(g.endpoints.bridgeStop,g.endpoints.southExit);
});
test("road graph rejects discontinuity, duplicate nodes and off-art passage",()=>{
 const bad=candidate.bridgeCenterlineArtPx.map(p=>p.slice());bad[10][0]++;
 assert.throws(()=>graphLib.build({south:source.rawPath,bridge:bad,forkIndex:source.forkIndex}),/share exact/);
 const duplicate=source.rawPath.map(p=>p.slice());duplicate[10]=duplicate[9];
 assert.throws(()=>graphLib.build({south:duplicate,bridge:duplicate,forkIndex:source.forkIndex}),/Zero-length/);
 const outside=candidate.bridgeCenterlineArtPx.map(p=>p.slice());outside.at(-1)[0]=1101;
 assert.throws(()=>graphLib.build({south:source.rawPath,bridge:outside,forkIndex:source.forkIndex}),/Out-of-art/);
});
test("army uses arclength, not percent of different branch geometry",()=>{
 const g=graph();const d=g.forkDistance*.63;
 assert.deepEqual(g.sample("south",d),g.sample("bridge",d));
 const switched=g.choose("south",d,"bridge");assert.equal(switched.allowed,true);
 assert.equal(switched.distance,d);assert.deepEqual(g.sample(switched.route,d),g.sample("south",d));
});
test("army cannot teleport from branch onto the other after junction",()=>{
 const g=graph(),d=g.forkDistance+30;
 const blocked=g.choose("bridge",d,"south");
 assert.equal(blocked.allowed,false);assert.equal(blocked.route,"bridge");
 assert.deepEqual(g.sample("bridge",blocked.distance),g.sample("bridge",d));
});
test("exact fork is switchable and bridge has no fake continuation",()=>{
 const g=graph();assert.equal(g.choose("south",g.forkDistance,"bridge").allowed,true);
 const end=g.advance("bridge",g.length("bridge")-1,10000);
 assert.equal(end.arrived,true);assert.deepEqual(end.position,g.endpoints.bridgeStop);
 assert.equal(end.terminal,"visible-far-bank-stop");
 assert.deepEqual(g.advance("bridge",end.distance,400).position,end.position);
});
test("bridge branch does not reverse along painted crossing",()=>{
 const g=graph(),p=g.edges.bridge;
 for(let i=1;i<p.length;i++)assert(p[i][0]>p[i-1][0],"Reverse x after fork");
});
test("hand-selected bridge reference pixels show improvement, not historical proof",()=>{
 const g=graph(),m=g.landmarkAudit(candidate.visualReferencePointsArtPx,candidate.originalBrokenBridgePath);
 assert.equal(m.candidate.count,5);
 assert(m.candidate.max < candidate.regressionAcceptance.maxCandidatePointDriftPx);
 assert(m.baseline.mean > candidate.regressionAcceptance.minOriginalPointDriftPx);
 assert(m.candidate.mean < m.baseline.mean*.1);
});
test("unit path and painted image share exact pixel/world transform",()=>{
 const g=graph();
 const a=render.artToWorld(tiles,g.forkPoint),p=g.sample("south",g.forkDistance);
 assert.deepEqual(g.forkPoint,p);
 assert(Math.hypot(...a.map((v,i)=>v-render.artToWorld(tiles,p)[i]))<1e-10);
 const box=tiles.artBoxWorldPx,viewport={width:390,height:844};
 for(const name of ["south","bridge"])for(const ratio of [0,.22,.45,.69,1]){
   const pt=g.sample(name,g.length(name)*ratio);
   const wp=render.artToWorld(tiles,pt),q=render.screenToWorld(render.worldToScreen(wp,box,viewport),box,viewport);
   assert(Math.hypot(q[0]-wp[0],q[1]-wp[1])<1e-10);
 }
});
test("all 48 tiles still non-playable after road graph proof",()=>{
 assert.equal(tiles.tiles.length,48);
 assert(tiles.tiles.every(t=>!t.traversable&&!t.conquerable&&!t.deepZoomEligible));
});
