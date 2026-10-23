#!/usr/bin/env node
'use strict';
// Guard against invisible army movement outside the rendered octagon polygon.
// This audits geometry only; it does not certify historical roads or artwork.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {octagon}=require('../terrain-grid/v122-seam-engine.js');
const atlas=require('../terrain-grid/v123-atlas.js');
const source=fs.readFileSync(path.join(__dirname,'../v121-octagon-1-painted-road.html'),'utf8');
const match=source.match(/const ROADS=(\{[^\r\n]+\});/);
assert(match,'V121 road graph missing');
const roads=JSON.parse(match[1]);
const scene=atlas.create(roads,{experimentalSeams:true});
function inside(p,poly,epsilon=.001){
 if(!Array.isArray(p)||p.length!==2||!p.every(Number.isFinite))return false;
 return poly.every((a,i)=>{
  const b=poly[(i+1)%poly.length],dx=b[0]-a[0],dy=b[1]-a[1];
  return dx*(p[1]-a[1])-dy*(p[0]-a[0]) >= -epsilon*Math.hypot(dx,dy);
 });
}
const shape=octagon(1536,1024,256);
for(const [point,expected] of [
 [[0,478],true],[[1536,256],true],[[1280,0],true],
 [[100,100],false],[[1536,200],false],[[1281,0],false],
 [[-4,478],false],[[NaN,10],false]
])assert.equal(inside(point,shape),expected,'Polygon clip: '+point);
let points=0;
for(const tile of scene.tiles){
 const poly=octagon(tile.width,tile.height,tile.corner);
 for(const [name,line] of Object.entries(tile.roads)){
  for(const [i,p] of line.entries()){
   assert(inside(p,poly),'Road outside painted octagon: '+tile.id+'/'+name+'['+i+']');
   points++;
  }
 }
}
assert(scene.network.seams.every(s=>s.pass),'Existing engineering seam regression');
console.log(JSON.stringify({pass:true,tiles:scene.tiles.length,roadPointsChecked:points,
 boundaryCases:8,engineeringSeams:scene.network.seams.length,
 historicallyVerified:false,physicalIphoneApproved:false},null,2));
