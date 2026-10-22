/* V116 candidate-index provenance regression. Run: node --test tests/test_v116_index_provenance_gate.js */
"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const {makeIndex}=require("../scripts/build_v116_candidate_tile_index.js");
const source=require("../terrain-grid/v115-route-provenance.json");
const candidate=require("../terrain-grid/v116-bridge-painted-candidate.json");
const baseline=require("../terrain-grid/v116-candidate-route-tiles.json");
const copy=x=>JSON.parse(JSON.stringify(x));

test("pinned source reproduces the checked-in 48-tile candidate index",()=>{
  assert.deepStrictEqual(makeIndex(),baseline);
  assert.equal(baseline.tiles.length,48);
  assert(baseline.tiles.every(t=>!t.traversable&&!t.conquerable&&!t.deepZoomEligible));
});

test("candidate index refuses altered provenance, unpainted far-bank roads and permissions",()=>{
  const mutations=[
    (s,c)=>{s.source.githubBlobSha="f".repeat(40);c.sourceV115BlobSha=s.source.githubBlobSha;},
    (s,c)=>c.bridgeCenterlineArtPx.push([710,800]),
    (s,c)=>c.verification.traversableProductionBridge=true,
    (s,c)=>c.verification.conquerableProductionTarget=true,
    (s,c)=>s.verification.historicalRoadEvidence=true,
    (s,c)=>s.sourceArt.widthPx=999,
    (s,c)=>c.sharedForkIndex+=1,
    (s,c)=>c.verification.roadOnFarBankBeyondBridgeVerified=true
  ];
  for(const mutate of mutations){
    const s=copy(source),c=copy(candidate);
    mutate(s,c);
    assert.throws(()=>makeIndex({routeSource:s,bridgeCandidate:c}),/provenance/);
  }
});

test("provenance checks do not modify their input records",()=>{
  const s=copy(source),c=copy(candidate);
  const index=makeIndex({routeSource:s,bridgeCandidate:c});
  assert.deepStrictEqual(s,source);
  assert.deepStrictEqual(c,candidate);
  assert.deepStrictEqual(index.routeCandidateTileIds,baseline.routeCandidateTileIds);
});
