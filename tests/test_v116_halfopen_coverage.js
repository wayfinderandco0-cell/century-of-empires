"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const {coveredTiles}=require("../scripts/build_v116_candidate_tile_index.js");
function grid(){
 const tiles=[];
 for(let row=0;row<2;row++)for(let col=0;col<2;col++){
   const crop=[col*50,row*50,(col+1)*50,(row+1)*50];
   tiles.push({id:"t"+row+col,row,col,imageCropPx:crop,worldRectPx:crop,
     traversable:false,conquerable:false,deepZoomEligible:false});
 }
 return {kind:"unverified_local_art_tile_index",artBoxWorldPx:[0,0,100,100],
   artSizePx:[100,100],grid:{columns:2,rows:2},tiles};
}
test("corner contact excludes unentered cells",()=>{
 const index=grid();
 assert.deepEqual(coveredTiles([[10,10],[90,90]],index.tiles,index),["t00","t11"]);
});
test("vertical seam uses right-hand tile ownership",()=>{
 const index=grid();
 assert.deepEqual(coveredTiles([[50,0],[50,100]],index.tiles,index),["t01","t11"]);
});
test("reverse path does not include unrelated tiles",()=>{
 const index=grid();
 assert.deepEqual(coveredTiles([[10,20],[90,20],[10,20]],index.tiles,index),["t00","t01"]);
});
test("coverage uses a matching tile index",()=>{
 const index=grid();
 assert.throws(()=>coveredTiles([[10,10],[90,90]],index.tiles,{...index,tiles:[...index.tiles]}),
   /same validated tile index/);
});
