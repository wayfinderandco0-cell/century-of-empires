/* V116 candidate-only route regression: reversals, exact edges and multi-tile seams.
 * Run: node --test tests/test_v116_trace_backtracking.js
 */
"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const {traceRoute}=require("../scripts/v116_route_tile_trace.js");
function grid(){
 const tiles=[];
 for(let row=0;row<2;row++)for(let col=0;col<3;col++){
   const r=[col*30,row*40,(col+1)*30,(row+1)*40];
   tiles.push({id:`r${row}c${col}`,row,col,imageCropPx:r,worldRectPx:r,
     traversable:false,conquerable:false,deepZoomEligible:false});
 }
 return {kind:"unverified_local_art_tile_index",artBoxWorldPx:[0,0,90,80],
   artSizePx:[90,80],grid:{columns:3,rows:2},tiles};
}
test("reversal reports both seam directions at cumulative distances, without granting access",()=>{
 const t=traceRoute(grid(),[[10,20],[80,20],[10,20]]);
 assert.equal(t.lengthPx,140);
 assert.deepEqual(t.visitedTileIds,["r0c0","r0c1","r0c2"]);
 assert.deepEqual(t.seams,[
   {fromTile:"r0c0",toTile:"r0c1",atArtPx:[30,20],distancePx:20},
   {fromTile:"r0c1",toTile:"r0c2",atArtPx:[60,20],distancePx:50},
   {fromTile:"r0c2",toTile:"r0c1",atArtPx:[60,20],distancePx:90},
   {fromTile:"r0c1",toTile:"r0c0",atArtPx:[30,20],distancePx:120}
 ]);
 assert.equal(t.productionAccess,false);
});
test("route on exact internal vertical edge belongs only to right-side tiles",()=>{
 const t=traceRoute(grid(),[[30,0],[30,80]]);
 assert.deepEqual(t.visitedTileIds,["r0c1","r1c1"]);
 assert.deepEqual(t.seams,[
   {fromTile:"r0c1",toTile:"r1c1",atArtPx:[30,40],distancePx:40}
 ]);
});
test("full-width edge-to-edge crossing yields two seams, no outside phantom tile",()=>{
 const t=traceRoute(grid(),[[0,20],[90,20]]);
 assert.equal(t.lengthPx,90);
 assert.deepEqual(t.seams.map(s=>[s.atArtPx,s.distancePx]),[
   [[30,20],30],[[60,20],60]
 ]);
 assert.deepEqual(t.visitedTileIds,["r0c0","r0c1","r0c2"]);
});
test("right and bottom artwork boundaries stay inside final tile",()=>{
 const t=traceRoute(grid(),[[90,0],[90,80]]);
 assert.deepEqual(t.visitedTileIds,["r0c2","r1c2"]);
 assert.deepEqual(t.seams.map(s=>s.atArtPx),[[90,40]]);
});
test("candidate-only trace fails closed when a tile is made traversable",()=>{
 const index=grid();index.tiles[0].traversable=true;
 assert.throws(()=>traceRoute(index,[[0,20],[90,20]]),/prematurely playable|Invalid/);
});
