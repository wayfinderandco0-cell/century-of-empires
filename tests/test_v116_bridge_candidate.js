/* Century of Empires V116: local painted-bridge candidate regression checks.
 * These tests validate candidate GEOMETRY against analyst-selected visual
 * bridge reference points, NOT independent historical cartography or Safari.
 * Run: node tests/test_v116_bridge_candidate.js
 */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
const candidate=read("terrain-grid/v116-bridge-painted-candidate.json");
const v115=read("terrain-grid/v115-route-provenance.json");
const index=read("terrain-grid/v115-local-tiles-v116.json");
const renderer=require("../scripts/v116_local_art_renderer.js");
let passed=0;
function test(name,fn){fn();passed++;console.log("PASS",name)}
function segmentDistance(p,a,b) {
 const dx=b[0]-a[0],dy=b[1]-a[1],length=dx*dx+dy*dy;
 const t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(length||1)));
 return Math.hypot(p[0]-a[0]-dx*t,p[1]-a[1]-dy*t);
}
function drift(p,route) {
 return Math.min(...route.slice(1).map((q,i)=>segmentDistance(p,route[i],q)));
}
const fixed=candidate.bridgeCenterlineArtPx,original=v115.bridgePath;
test("uses the exact V115 source image identity",()=>{
 assert.equal(candidate.sourceV115BlobSha,v115.source.githubBlobSha);
 assert.equal(index.artSizePx.join("x"),"1100x842");
});
test("revised path preserves exact shared road to fork",()=>{
 assert.equal(candidate.sharedForkIndex,v115.forkIndex);
 assert.deepEqual(fixed.slice(0,v115.forkIndex+1),v115.rawPath.slice(0,v115.forkIndex+1));
});
test("bridge branch no longer doubles back from fork",()=>{
 const old=original.slice(v115.forkIndex);
 assert(old.some((p,i)=>i>0&&p[0]<old[i-1][0]));
 const newBranch=fixed.slice(v115.forkIndex);
 assert(newBranch.every((p,i)=>i===0||p[0]>newBranch[i-1][0]));
 assert(newBranch.every((p,i)=>i===0||p[1]>=newBranch[i-1][1]));
});
test("visual bridge landmarks improve versus old route",()=>{
 for(const p of candidate.visualReferencePointsArtPx){
  const old=drift(p,original),now=drift(p,fixed);
  assert(old>=candidate.regressionAcceptance.minOriginalPointDriftPx,
    "baseline was not displaced at "+p+"; drift="+old);
  assert(now<=candidate.regressionAcceptance.maxCandidatePointDriftPx,
    "repaired candidate misses landmark "+p+" by "+now);
 }
});
test("endpoints stay in artwork and stop at visible far bank",()=>{
 for(const p of fixed){assert(p[0]>=0&&p[0]<=1100);assert(p[1]>=0&&p[1]<=842);}
 assert.deepEqual(fixed.at(-1),[699,799]);
 assert.equal(candidate.verification.roadOnFarBankBeyondBridgeVerified,false);
 assert.equal(candidate.verification.traversableProductionBridge,false);
 assert.equal(candidate.verification.conquerableProductionTarget,false);
});
test("road candidate remains in one parent strategic cell",()=>{
 renderer.validate(index);
 const ids=new Set();
 for(const p of fixed){const world=renderer.artToWorld(index,p),x=Math.floor(world[0]/(1448/24)),y=Math.floor(world[1]/(1086/18));
  ids.add("r"+String(y).padStart(2,"0")+"-c"+String(x).padStart(2,"0"));
 }
 assert.deepEqual([...ids],["r10-c09"]);
});
test("army/world/screen positions agree at all zoom presets",()=>{
 const b=index.artBoxWorldPx;
 const points=[fixed[0],fixed[v115.forkIndex],fixed[43],fixed.at(-1)];
 for(const v of [{width:390,height:844},{width:844,height:390}]){
  for(const factor of [1,2.1,3.3,4.0]){
   const ww=Math.max(b[2]-b[0],(b[3]-b[1])*v.width/v.height)*1.045/factor;
   const cc=renderer.artToWorld(index,[550,421]),hh=ww*v.height/v.width,cam=[cc[0]-ww/2,cc[1]-hh/2,cc[0]+ww/2,cc[1]+hh/2];
   for(const p of points){
    const world=renderer.artToWorld(index,p),screen=renderer.worldToScreen(world,cam,v),back=renderer.screenToWorld(screen,cam,v);
    assert(Math.hypot(back[0]-world[0],back[1]-world[1])<1e-10);
   }
  }
 }
});
console.log("PASS "+passed+" candidate bridge checks (visual, NOT historic certification)");