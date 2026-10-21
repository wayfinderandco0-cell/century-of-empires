"use strict";
/* node --test tests/test_v117_road_art_contract.js */
const {test}=require("node:test");
const assert=require("node:assert/strict");
const Road=require("../scripts/v116_road_graph.js");
const Art=require("../scripts/v117_road_art_contract.js");
const source=require("../terrain-grid/v115-route-provenance.json");
const bridge=require("../terrain-grid/v116-bridge-painted-candidate.json");
const make=()=>{
 const graph=Road.build({south:source.rawPath,bridge:bridge.bridgeCenterlineArtPx,
  forkIndex:source.forkIndex,imageSize:[1100,842]});
 return {graph,art:Art.build(graph)};
};
function canvas(){
 const calls=[],ctx={globalAlpha:1,
  save(){calls.push(["save"])},restore(){calls.push(["restore"])},
  beginPath(){calls.push(["begin"])},
  moveTo(x,y){calls.push(["move",x,y])},
  lineTo(x,y){calls.push(["line",x,y])},
  stroke(){calls.push(["stroke",this.strokeStyle,this.lineWidth])}};
 return {ctx,calls};
}
test("road ink follows exactly the moving army over both entire branches",()=>{
 const {graph,art}=make();
 for(const name of ["south","bridge"])for(let i=0;i<=256;i++){
  const pos=art.sampledArmy(name,graph.length(name)*i/256);
  assert(art.distanceToCenterline(pos,name)<1e-6,
    "Road painted centerline must exactly contain every army location");
 }
});
test("shared fork is continuous; bridge ends at the actual artwork candidate far bank",()=>{
 const {graph,art}=make();
 assert.deepEqual(art.bridgeStop,[699,799]);
 assert.deepEqual(graph.endpoints.bridgeStop,art.bridgeStop);
 assert.deepEqual(graph.edges.approach.at(-1),graph.edges.bridge[0]);
 assert.deepEqual(graph.edges.approach.at(-1),graph.edges.south[0]);
 assert.deepEqual(art.sampledArmy("bridge",graph.length("bridge")),art.bridgeStop);
 assert.equal(art.approvedForProduction,false);
});
test("earth track uses identical source coordinates across four zoom levels and both phone orientations",()=>{
 const {art}=make();
 for(const factor of [.4,.9,2.1,5.0])for(const dimensions of [[390,844],[844,390]]){
  const {ctx,calls}=canvas();
  const projection=p=>[(p[0]-510)*factor+dimensions[0]/2,(p[1]-490)*factor+dimensions[1]/2];
  const result=art.paint(ctx,projection,{route:"bridge"});
  assert.equal(result.farBankContinuationVerified,false);
  assert.equal(result.approvedForProduction,false);
  assert.equal(calls.filter(x=>x[0]==="stroke").length,8);
  assert(calls.every(x=>x[0]!=="stroke"||x[2]>0));
  assert(art.assertSynced());
 }
});
test("road painter draws both exits without duplicating the shared approach",()=>{
 const {art}=make();const {ctx,calls}=canvas();
 art.paint(ctx,p=>p,{route:"both"});
 assert.equal(calls.filter(x=>x[0]==="stroke").length,13);
});
test("changing a route without changing the corresponding road fails closed",()=>{
 const {graph,art}=make();graph.paths.bridge[40][0]+=8;
 assert.throws(()=>art.paint(canvas().ctx,p=>p),/changed independently/);
 assert.throws(()=>art.sampledArmy("bridge",100),/changed independently/);
});
test("rejects a fake production-approved bridge and a distorted transform",()=>{
 const {graph,art}=make();
 assert.throws(()=>Art.build({...graph,approvedForProduction:true}),/refuses/);
 assert.throws(()=>Art.build({...graph,bridgeTerminal:"invented-road"}),/refuses/);
 assert.throws(()=>art.paint(canvas().ctx,p=>[p[0]*3,p[1]]),/near-isotropic/);
});
test("road offsets never change the input graph geometry",()=>{
 const {graph,art}=make(),before=JSON.stringify(graph.paths);
 art.paint(canvas().ctx,p=>p);
 assert.equal(JSON.stringify(graph.paths),before);
 assert(art.assertSynced());
});
