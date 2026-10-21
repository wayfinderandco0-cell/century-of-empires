/* V116 two-branch painted-road audit. Analyst-selected image landmarks are
 * visual QA references, NOT independently surveyed historical road evidence.
 * Run: node tests/test_v116_road_network.js
 */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const read=p=>JSON.parse(fs.readFileSync(path.join(__dirname,"..",p),"utf8"));
const net=read("terrain-grid/v116-painted-road-network-candidate.json");
const old=read("terrain-grid/v115-route-provenance.json");
const index=read("terrain-grid/v115-local-tiles-v116.json");
const render=require("../scripts/v116_local_art_renderer.js");
let tests=0;function pass(name,f){f();tests++;console.log("PASS",name)}
function drift(p,path){
 let d=Infinity;for(let i=1;i<path.length;i++){
  const a=path[i-1],b=path[i],dx=b[0]-a[0],dy=b[1]-a[1];
  const t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy||1)));
  d=Math.min(d,Math.hypot(p[0]-a[0]-dx*t,p[1]-a[1]-dy*t));
 }return d;
}
pass("true V115 JPEG identity and shared V94 renderer",()=>{
 assert.equal(net.source.sourceBlobSha,old.source.githubBlobSha);
 assert.deepEqual(index.artSizePx,[1100,842]);render.validate(index);
});
pass("both paths share exactly the same original road prefix and new fork",()=>{
 assert.deepEqual(net.sharedApproachArtPx.slice(0,28),old.rawPath.slice(0,28));
 const join=net.forkIndex+1;
 assert.deepEqual(net.southPathArtPx.slice(0,join),net.sharedApproachArtPx);
 assert.deepEqual(net.bridgePathArtPx.slice(0,join),net.sharedApproachArtPx);
 assert.deepEqual(net.sharedApproachArtPx.at(-1),[503,760]);
 assert.deepEqual(net.forkArtPx,[503,760]);
});
pass("southern painted-cart-road route no longer cuts across original offroad line",()=>{
 for(const p of net.visualReferencePoints.south){
  assert(drift(p,old.rawPath)>20, "old path is not displaced "+p);
  assert(drift(p,net.southPathArtPx)<4, "new south path misses "+p);
 }
});
pass("new junction approach aligns with painted road reference markers",()=>{
 for(const p of net.visualReferencePoints.sharedApproach){
  assert(drift(p,old.rawPath)>20);
  assert(drift(p,net.sharedApproachArtPx)<4);
 }
});
pass("bridge route no longer doubles back and follows visible deck",()=>{
 const arr=net.bridgePathArtPx.slice(net.forkIndex),prev=old.bridgePath.slice(old.forkIndex);
 assert(prev.some((p,i)=>i>0&&p[0]<prev[i-1][0]));
 assert(arr.every((p,i)=>i===0||(p[0]>arr[i-1][0]&&p[1]>=arr[i-1][1])));
 for(const p of net.visualReferencePoints.bridge){
  assert(drift(p,old.bridgePath)>15);
  assert(drift(p,net.bridgePathArtPx)<4);
 }
});
pass("southern exit and far-bank crossing stop inside existing painted scene",()=>{
 assert.deepEqual(net.southPathArtPx.at(-1),[394,842]);
 assert.deepEqual(net.bridgePathArtPx.at(-1),[699,799]);
 assert(net.southPathArtPx.slice(net.forkIndex).every((p,i,a)=>
   i===0||(p[0]<a[i-1][0]&&p[1]>a[i-1][1])));
 for(const p of [...net.southPathArtPx,...net.bridgePathArtPx]){
  assert(p[0]>=0&&p[0]<=1100&&p[1]>=0&&p[1]<=842);
 }
 assert.equal(net.status.roadBeyondSourceArtVisible,false);
 assert.equal(net.status.productionTraversable,false);
 assert.equal(net.status.productionConquerable,false);
});
pass("candidate stays inside parent strategic cell r10-c09",()=>{
 for(const p of [...net.southPathArtPx,...net.bridgePathArtPx]){
  const [x,y]=render.artToWorld(index,p);
  assert.equal("r"+String(Math.floor(y/(1086/18))).padStart(2,"0")+"-c"+
               String(Math.floor(x/(1448/24))).padStart(2,"0"),"r10-c09");
 }
});
pass("interpolated moving army remains on same art/world path at 4 zoom levels",()=>{
 const bb=index.artBoxWorldPx;
 for(const [w,h] of [[390,844],[844,390]]){
  for(const factor of [1,2.1,3.3,4]){
   const vw={width:w,height:h},fit=Math.max(bb[2]-bb[0],(bb[3]-bb[1])*w/h)*1.045/factor,
         center=render.artToWorld(index,[550,421]),
         camera=[center[0]-fit/2,center[1]-fit*h/w/2,center[0]+fit/2,center[1]+fit*h/w/2];
   for(const route of [net.southPathArtPx,net.bridgePathArtPx]){
    for(let i=1;i<route.length;i++){
     for(const t of [0,.25,.5,.75,1]){
      const art=[route[i-1][0]*(1-t)+route[i][0]*t,route[i-1][1]*(1-t)+route[i][1]*t],
            world=render.artToWorld(index,art),
            sc=render.worldToScreen(world,camera,vw),
            back=render.screenToWorld(sc,camera,vw);
      assert(Math.hypot(world[0]-back[0],world[1]-back[1])<1e-10);
     }
    }
   }
  }
 }
});
console.log("PASS "+tests+" V116 road-network checks; physical iPhone / historical roads remain UNVERIFIED");