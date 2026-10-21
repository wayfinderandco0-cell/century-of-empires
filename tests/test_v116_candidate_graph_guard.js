/* Run: node --test tests/test_v116_candidate_graph_guard.js
 * Synthetic fixtures isolate the guard; existing road-graph tests exercise geometry.
 */
"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const {buildSafe}=require("../scripts/v116_candidate_graph_guard.js");
const copy=x=>JSON.parse(JSON.stringify(x));
const source=()=>({
  source:{repository:"wayfinderandco0-cell/century-of-empires",path:"v115-town-pan-controls.html",
    githubBlobSha:"9a8f44120c2f220abf434bed384f230cf6483296"},
  sourceArt:{widthPx:1100,heightPx:842},forkIndex:1,
  rawPath:[[616,0],[437,742],[325,834]],
  verification:{historicalRoadEvidence:false,roadCenterlineMatchesPaintedArt:false,
    bridgeCrossingMatchesPaintedArt:false,farBankContinuationVerified:false,
    accessibleStrategicObjectiveVerified:false}
});
const candidate=()=>({schemaVersion:1,kind:"candidate_painted_bridge_centerline_not_authoritative",
  sourceRouteFile:"terrain-grid/v115-route-provenance.json",
  sourceV115BlobSha:"9a8f44120c2f220abf434bed384f230cf6483296",
  sharedForkIndex:1,bridgeCenterlineArtPx:[[616,0],[437,742],[699,799]],
  verification:{historicalRoadVerified:false,roadOnFarBankBeyondBridgeVerified:false,
    traversableProductionBridge:false,conquerableProductionTarget:false}
});
const fakeRoad={build:({south,bridge,imageSize})=>({
  kind:"art-aligned-candidate",approvedForProduction:false,conquerable:false,
  bridgeTerminal:"visible-far-bank-only",imageSize,
  forkPoint:south[1].slice(),edges:{approach:south.slice(0,2),south:south.slice(1),bridge:bridge.slice(1)},
  paths:{south:copy(south),bridge:copy(bridge)},
  endpoints:{approachStart:south[0].slice(),southExit:south.at(-1).slice(),bridgeStop:bridge.at(-1).slice()}
})};
test("sourced candidate remains nonproduction and deeply immutable",()=>{
  const s=source(),c=candidate(),g=buildSafe(s,c,fakeRoad);
  assert.equal(g.approvedForProduction,false);
  assert.equal(g.conquerable,false);
  assert.equal(g.bridgeTerminal,"visible-far-bank-only");
  assert.deepEqual(g.endpoints.bridgeStop,[699,799]);
  for(const target of [g,g.paths,g.paths.south[0],g.edges.bridge[0],g.endpoints.bridgeStop,g.imageSize,g.forkPoint]){
    assert(Object.isFrozen(target));
  }
  assert.throws(()=>{g.paths.bridge[2][0]=999;},TypeError);
  c.bridgeCenterlineArtPx[2][0]=1000;
  assert.deepEqual(g.endpoints.bridgeStop,[699,799]);
});
test("matched forged source hashes do not bypass the pinned V115 identity",()=>{
  const s=source(),c=candidate();s.source.githubBlobSha="f".repeat(40);c.sourceV115BlobSha=s.source.githubBlobSha;
  assert.throws(()=>buildSafe(s,c,fakeRoad),/provenance/);
});
test("unknown source and dimensions fail closed",()=>{
  for(const edit of [s=>s.source.path="v114-town-camera-bridge-safety.html",
    s=>s.source.repository="elsewhere/repo",s=>s.sourceArt.widthPx=1200]){
    const s=source();edit(s);assert.throws(()=>buildSafe(s,candidate(),fakeRoad),/provenance/);
  }
});
test("altered terminal cannot imply an invented far-bank continuation",()=>{
  const c=candidate();c.bridgeCenterlineArtPx.push([730,810]);
  assert.throws(()=>buildSafe(source(),c,fakeRoad),/provenance/);
});
test("false production claims in either source fail closed",()=>{
  for(const key of Object.keys(source().verification)){
    const s=source();s.verification[key]=true;
    assert.throws(()=>buildSafe(s,candidate(),fakeRoad),/provenance/,key);
  }
  for(const key of ["historicalRoadVerified","roadOnFarBankBeyondBridgeVerified",
    "traversableProductionBridge","conquerableProductionTarget"]){
    const c=candidate();c.verification[key]=true;
    assert.throws(()=>buildSafe(source(),c,fakeRoad),/provenance/,key);
  }
});
test("incorrect candidate identity or fork fails closed",()=>{
  for(const edit of [c=>c.kind="production",c=>c.schemaVersion=2,
    c=>c.sourceRouteFile="different.json",c=>c.sharedForkIndex=2]){
    const c=candidate();edit(c);
    assert.throws(()=>buildSafe(source(),c,fakeRoad),/provenance/);
  }
});
test("road graph trying to override production flags or endpoint is rejected",()=>{
  for(const edit of [g=>g.approvedForProduction=true,g=>g.conquerable=true,
    g=>g.bridgeTerminal="far-bank-connected",g=>g.endpoints.bridgeStop=[800,810]]){
    const rogue={build:args=>{const g=fakeRoad.build(args);edit(g);return g;}};
    assert.throws(()=>buildSafe(source(),candidate(),rogue),/diverges/);
  }
});
