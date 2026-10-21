"use strict";
const {test}=require("node:test"),a=require("node:assert/strict");
const trace=require("../scripts/v116_route_tile_trace.js");
const road=require("../scripts/v116_road_graph.js");
const render=require("../scripts/v116_local_art_renderer.js");
const source=require("../terrain-grid/v115-route-provenance.json");
const candidate=require("../terrain-grid/v116-bridge-painted-candidate.json");
const index=require("../terrain-grid/v116-candidate-route-tiles.json");
const graph=()=>road.build({south:source.rawPath,bridge:candidate.bridgeCenterlineArtPx,
 forkIndex:source.forkIndex,imageSize:index.artSizePx});
function toy(){
 const tiles=[];for(let row=0;row<2;row++)for(let col=0;col<2;col++){
 const r=[col*50,row*50,(col+1)*50,(row+1)*50];
 tiles.push({id:"t"+row+col,row,col,imageCropPx:r,worldRectPx:r,traversable:false,conquerable:false,deepZoomEligible:false});
 }
 return {kind:"unverified_local_art_tile_index",artBoxWorldPx:[0,0,100,100],
  artSizePx:[100,100],grid:{columns:2,rows:2},tiles};
}
test("corner does not invent adjacent traversed tiles",()=>{
 const t=trace.traceRoute(toy(),[[10,10],[90,90]]);
 a.deepEqual(t.visitedTileIds,["t00","t11"]);a.deepEqual(t.seams[0].atArtPx,[50,50]);
 a.equal(t.productionAccess,false);
});
test("tile edge shares exact coordinate and army distance",()=>{
 const t=trace.traceRoute(toy(),[[0,25],[100,25]]);
 a.deepEqual(t.seams,[{fromTile:"t00",toTile:"t01",atArtPx:[50,25],distancePx:50}]);
 a.equal(t.lengthPx,100);
});
test("route on border has deterministic single-tile ownership",()=>{
 a.deepEqual(trace.traceRoute(toy(),[[50,0],[50,100]]).visitedTileIds,["t01","t11"]);
});
test("out-of-art, NaN and duplicate points fail closed",()=>{
 a.throws(()=>trace.traceRoute(toy(),[[0,0],[101,1]]),/outside artwork/);
 a.throws(()=>trace.traceRoute(toy(),[[0,0],[0,0]]),/Zero-length/);
 a.throws(()=>trace.traceRoute(toy(),[[0,0],[NaN,2]]),/Invalid candidate/);
});
test("actual V115 tile crossings match coverage",()=>{
 const g=graph(),t=trace.traceGraph(index,g);
 for(const name of ["south","bridge"]){
  a.deepEqual(t[name].visitedTileIds,index.routeCandidateTileIds[name]);
  a(t[name].seams.length>0);
 }
 a(index.tiles.every(x=>!x.traversable&&!x.conquerable&&!x.deepZoomEligible));
});
test("far-bank continuation cannot be authorized",()=>{
 const g=graph();
 a.throws(()=>trace.traceGraph(index,{...g,bridgeTerminal:"invented-road"}),/nonproduction/);
 a.deepEqual(g.advance("bridge",g.length("bridge"),500).position,g.endpoints.bridgeStop);
});
test("army and tile seams coincide in 4 zooms, both phone orientations",()=>{
 const g=graph(),t=trace.traceGraph(index,g),[x0,y0,x1,y1]=index.artBoxWorldPx;
 const cx=(x0+x1)/2,cy=(y0+y1)/2,w=x1-x0,h=y1-y0;
 for(const f of [2,1,.65,.25])for(const viewport of [{width:390,height:844},{width:844,height:390}]){
  const cam=[cx-w*f/2,cy-h*f/2,cx+w*f/2,cy+h*f/2];
  for(const name of ["south","bridge"])for(const s of t[name].seams){
   const p=render.artToWorld(index,s.atArtPx),unit=render.artToWorld(index,g.sample(name,s.distancePx));
   const sp=render.worldToScreen(p,cam,viewport),su=render.worldToScreen(unit,cam,viewport);
   a(Math.hypot(sp[0]-su[0],sp[1]-su[1])<1e-6);
   const back=render.screenToWorld(sp,cam,viewport);
   a(Math.hypot(back[0]-p[0],back[1]-p[1])<1e-9);
  }
 }
});
