/* Gate tests: synthetic metadata only. These are NOT eight generated artworks. */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const contract=require("../terrain-grid/v267-art-factory-contract.js");
const base=JSON.parse(fs.readFileSync(path.join(__dirname,"../terrain-grid/atlas-cells.json"),"utf8"));
assert.equal(contract.assertBase(base),true);
const fake=(n)=>({
  id:"new-cell-"+n,origin:[(n%4+4)*1536,(Math.floor(n/4)+4)*1024],
  biome:n%2?"alpine-foothill":"wooded-valley",
  scenicSettlements:[],strategicNodes:[],provinceIds:[],
  roadPorts:[],originalArtComposed:false,visuallyReviewed:false,
  roadSeamsVerified:false,mobileWebkitRendered:false,
  historicalVerified:false,nativePlayable:false,userApproved:false
});
const batch={schema:"coe-v267-original-art-batch/v1",
  referenceCommit:contract.REF,cells:Array.from({length:8},(_,n)=>fake(n)),
  links:[],decorativeInlays:[{id:"unplayable-gap",playable:false,roads:[]}]};
const summary=contract.validateBatch(batch,base);
assert.equal(summary.candidateMetadata,8);
for(const [k,v] of Object.entries(summary))if(k!=="candidateMetadata")assert.equal(v,0,k);
const rejects=(fn,pattern)=>assert.throws(fn,pattern);
const clone=x=>JSON.parse(JSON.stringify(x));
{
  const bad=clone(base);bad.cells[0].art="terrain-grid/factory-photo/flat.webp";
  rejects(()=>contract.assertBase(bad),/source\/placement drift/);
}
{
  const bad=clone(batch);bad.cells[0].art="terrain-grid/factory-photo/flat.webp";
  bad.cells[0].assetSha256="a".repeat(64);bad.cells[0].visualGrammar="v267-original-layered-landscape";
  rejects(()=>contract.validateBatch(bad,base),/prohibited flat/);
}
{
  const bad=clone(batch);bad.cells[0].historicalVerified=true;
  rejects(()=>contract.validateBatch(bad,base),/unsupported history/);
}
{
  const bad=clone(batch);bad.cells[0].scenicSettlements=[{name:"fictional hamlet",capturable:true}];
  rejects(()=>contract.validateBatch(bad,base),/scenic village/);
}
{
  const bad=clone(batch);bad.decorativeInlays[0].roads=[[1,2]];
  rejects(()=>contract.validateBatch(bad,base),/phantom road/);
}
{
  const bad=clone(batch);bad.cells[0].origin=base.cells[0].origin;
  rejects(()=>contract.validateBatch(bad,base),/overlapping protected/);
}
{
  const good=clone(batch);
  good.cells[0].roadPorts=[{id:"r0",side:"east",local:[1536,478],routeId:"graph-edge-001"}];
  good.cells[1].roadPorts=[{id:"r1",side:"west",local:[0,478],routeId:"graph-edge-001"}];
  // Synthetic geometry: place cell 1 immediately east of cell 0.
  good.cells[1].origin=[good.cells[0].origin[0]+1536,good.cells[0].origin[1]];
  good.links=[{id:"pair",from:{cell:good.cells[0].id,port:"r0"},to:{cell:good.cells[1].id,port:"r1"}}];
  assert.equal(contract.validateBatch(good,base).roadConnected,0,"A paired test seam is not visual proof");
  good.cells[1].roadPorts[0].local[1]=479;
  rejects(()=>contract.validateBatch(good,base),/world mismatch/);
}
{
  const bad=clone(batch);bad.cells[0].art="art-reviews/v267-new-cell.webp";
  bad.cells[0].assetSha256="b".repeat(64);
  bad.cells[0].visualGrammar="v267-original-layered-landscape";
  bad.cells[0].originalArtComposed=true;
  bad.cells[0].visuallyReviewed=true;
  bad.cells[0].mobileWebkitRendered=true;
  bad.cells[0].nativePlayable=true;
  bad.cells[0].userApproved=true;
  // No source-backed historical verification or road connection => NOT finished.
  assert.equal(contract.validateBatch(bad,base).netFinishedToday,0);
}
console.log("PASS: locked WEST/MATREI/SOUTH, exact paired seam geometry, false-history/photo/inlay rejection, zero fabricated finished art");
