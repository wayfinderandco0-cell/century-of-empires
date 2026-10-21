"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const Road=require("../scripts/v116_road_graph.js");
const Exit=require("../scripts/v118_east_connector.js");
const source=require("../terrain-grid/v115-route-provenance.json");
const painted=require("../terrain-grid/v116-bridge-painted-candidate.json");
function graph(){
 return Road.build({south:source.rawPath,bridge:Exit.extend(painted.bridgeCenterlineArtPx),
 forkIndex:source.forkIndex,imageSize:[1100,842]});
}
function ctx(){
 const calls=[];
 const c={save(){},restore(){},beginPath(){calls.push("begin")},
 moveTo(x,y){calls.push(["M",x,y])},lineTo(x,y){calls.push(["L",x,y])},
 stroke(){calls.push(["stroke",this.lineWidth,this.strokeStyle])}};
 return {c,calls};
}
test("far bank through eastern cell boundary is continuous",()=>{
 const g=graph();
 assert.deepEqual(g.endpoints.bridgeStop,[1100,781]);
 assert.deepEqual(g.paths.bridge.at(-1),[1100,781]);
 assert.deepEqual(Exit.nextCellEntry,[0,781]);
 assert.deepEqual(g.paths.bridge.slice(-Exit.points.length),Exit.points);
});
test("army stays on the same painted exit geometry at every sample",()=>{
 const g=graph(),{c,calls}=ctx();
 assert.equal(Exit.draw(c,p=>p,g).sameRoute,true);
 assert.equal(calls.filter(x=>Array.isArray(x)&&x[0]==="stroke").length,5);
 for(let i=0;i<=1000;i++){
  const p=g.sample("bridge",g.length("bridge")*i/1000);
  assert(Road.closestPointDistance(p,g.paths.bridge)<1e-7);
 }
});
test("moving army reaches far bank and then the cart track exit",()=>{
 const g=graph(),at=g.paths.bridge.findIndex(p=>p[0]===699&&p[1]===799);
 const bankDist=g.paths.bridge.slice(1,at+1).reduce((d,p,i)=>d+Math.hypot(p[0]-g.paths.bridge[i][0],p[1]-g.paths.bridge[i][1]),0);
 const across=g.advance("bridge",bankDist,40);
 assert(across.position[0]>699&&across.arrived===false);
 const edge=g.advance("bridge",bankDist,2000);
 assert.equal(edge.arrived,true);
 assert.deepEqual(edge.position,[1100,781]);
});
test("invalid crossings and paint/army divergence fail closed",()=>{
 assert.throws(()=>Exit.extend([[699,798]]),/requires/);
 const g=graph();
 g.paths.bridge.at(-1)[1]=780;
 assert.throws(()=>Exit.draw(ctx().c,p=>p,g),/differs/);
});
test("road ink projects correctly at four scales",()=>{
 const g=graph();
 for(const scale of [.4,.9,2.1,5]){
  const {c,calls}=ctx();
  Exit.draw(c,p=>[p[0]*scale,p[1]*scale],g);
  assert.equal(calls.filter(x=>Array.isArray(x)&&x[0]==="stroke").length,5);
 }
});
