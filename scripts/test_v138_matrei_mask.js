'use strict';
// Verify the V138 fast convex-octagon mask preserves every visible V137 alpha
// against the original exact point-to-segment distance calculation.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'..','v137-coherent-alpine-preview.html'),'utf8');
const match=html.match(/const poly=(\\[[^\\n]+\\]);/);
assert(match,'V137 Matrei polygon must exist');
const poly=JSON.parse(match[1]);
assert.equal(poly.length,8);
const start=html.indexOf('const inwardEdges=');
const end=html.indexOf('async function loadGroundImage',start);
assert(start>0&&end>start,'optimized mask code must be present');
const optimized=html.slice(start,end);
assert(!/Math\\.hypot/.test(optimized.slice(optimized.indexOf('function signedEdge'))),
  'signedEdge must not call hypot for every pixel');
const fast=vm.runInNewContext(optimized+'; signedEdge;', {poly,Math});
function reference(x,y){
  let inside=false,best=Infinity;
  for(let i=0,j=poly.length-1;i<poly.length;j=i++){
    const a=poly[j],b=poly[i],dx=b[0]-a[0],dy=b[1]-a[1];
    const t=Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));
    best=Math.min(best,Math.hypot(x-a[0]-t*dx,y-a[1]-t*dy));
    if(((a[1]>y)!==(b[1]>y))&&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]))inside=!inside;
  }
  return inside?best:-best;
}
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
let checks=0;
for(let y=-110;y<=1130;y+=11)for(let x=-110;x<=1650;x+=11){
  const a=reference(x,y),b=fast(x,y);
  // Only interior distance affects the feather: exterior alpha is zero.
  if(a>1e-7)assert(Math.abs(a-b)<1e-7,'inside mask mismatch at '+x+','+y);
  else assert(b<1e-7,'outside mask incorrectly inside at '+x+','+y);
  const alpha0=smooth((a-14)/230),alpha1=smooth((b-14)/230);
  assert(Math.abs(alpha0-alpha1)<1e-9,'visible feather changed at '+x+','+y);
  checks++;
}
for(const [x,y] of poly){
  assert(Math.abs(fast(x,y))<1e-7,'vertex mask mismatch');
}
console.log('V138 Matrei alpha equivalence: '+checks+' grid points and 8 vertices PASS');
