/* Run: node --test tests/test_v116_candidate_graph_guard.js
 * Synthetic fixtures isolate the guard; existing road-graph tests exercise geometry.
 */
"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const {buildSafe}=require("../scripts/v116_candidate_graph_guard.js");
const copy=x=>JSON.parse(JSON.stringify(x));
const source=()=>copy(require("../terrain-grid/v115-route-provenance.json"));
const candidate=()=>copy(require("../terrain-grid/v116-bridge-painted-candidate.json"));
const fakeRoad=require("../scripts/v116_road_graph.js");
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

test("all interior geometry and shared fork remain pinned despite matching endpoints",()=>{
  for(const mutate of [
    (s,c)=>{c.bridgeCenterlineArtPx[44][1]+=1;},
    (s,c)=>{s.rawPath[5][0]+=1;},
    (s,c)=>{s.rawPath[5][0]+=1;c.bridgeCenterlineArtPx[5][0]+=1;},
    (s,c)=>{s.forkIndex=35;c.sharedForkIndex=35;}
  ]){
    const s=source(),c=candidate();mutate(s,c);
    assert.throws(()=>buildSafe(s,c,fakeRoad),/provenance/);
  }
});
test("unmodified source fixtures are never mutated by the guard",()=>{
  const s=source(),c=candidate(),beforeS=copy(s),beforeC=copy(c);
  buildSafe(s,c,fakeRoad);
  assert.deepEqual(s,beforeS);
  assert.deepEqual(c,beforeC);
});
