#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const {enhance}=require('../terrain-grid/v164-source-detail.js');
const pix=(w,h,fn)=>{const a=new Uint8ClampedArray(w*h*4);for(let y=0;y<h;y++)for(let x=0;x<w;x++){const k=(y*w+x)*4,v=fn(x,y);a.set([v,v,v,255],k)}return a;};
let count=0;const test=(name,fn)=>{fn();count++;console.log('PASS',name)};
test('uniform image unchanged',()=>{
 const a=pix(16,16,()=>97),b=enhance(a,16,16);
 assert.deepEqual(b.pixels,a);assert.equal(b.report.changedPixels,0);
});
test('source immutable and alpha unchanged',()=>{
 const a=pix(32,32,(x,y)=>x<16?42:181),before=new Uint8ClampedArray(a);
 const b=enhance(a,32,32);
 assert.deepEqual(a,before);assert(b.report.changedPixels>0);
 for(let k=3;k<b.pixels.length;k+=4)assert.equal(b.pixels[k],255);
});
test('bounded enhancement only near source edges',()=>{
 const a=pix(32,32,(x)=>x<16?42:181),b=enhance(a,32,32);
 for(let y=0;y<32;y++)for(let x=0;x<32;x++){
  const k=(y*32+x)*4;
  assert(Math.abs(b.pixels[k]-a[k])<=19);
  if(x<11||x>20)assert.equal(b.pixels[k],a[k]);
 }
 assert(b.pixels[(16*32+15)*4]<a[(16*32+15)*4]);
 assert(b.pixels[(16*32+16)*4]>a[(16*32+16)*4]);
});
test('deterministic, no invented features on smooth input',()=>{
 const a=pix(32,32,(x,y)=>Math.round(100+x*.5+y*.5));
 assert.deepEqual(enhance(a,32,32).pixels,enhance(a,32,32).pixels);
});
test('invalid parameters rejected',()=>{
 const a=pix(16,16,()=>70);
 for(const opt of [{radius:0},{radius:5},{strength:-1},{strength:2},{maxDelta:40}])
  assert.throws(()=>enhance(a,16,16,opt));
 assert.throws(()=>enhance(a,16,15));
 assert.throws(()=>enhance(new Uint8Array(a),16,16));
});
test('V164 study cannot alter V161 route/movement/painted photo',()=>{
 const old=fs.readFileSync('v161-native-material-study.html','utf8');
 const now=fs.readFileSync('v164-source-detail-study.html','utf8');
 const block=(s,a,b)=>{const i=s.indexOf(a),j=s.indexOf(b,i+a.length);assert(i>=0&&j>i);return s.slice(i,j)};
 for(const [a,b] of [
  ['function paintTrack(', 'function paintNaturalTrailFinish('],
  ['function render(){','function polygonAt('],
  ['function issue(to){','function nearestRoadNode('],
  ['function march(dt){','function halt(){'],
  ['function halt(){','C.addEventListener('],
  ['async function boot(){','function frame(t){']
 ])assert.equal(block(now,a,b),block(old,a,b));
 assert(now.includes('V164SourceDetail.enhance('));
 assert(now.includes('v123ToMaterialGeoregistered:false'));
 assert(now.includes('productionApproved:false'));
 assert(now.includes('get productionApproved(){return false}'));
 const hash=s=>crypto.createHash('sha1').update(s).digest('hex');
 assert.equal(hash(block(now,'function render(){','function polygonAt(')),
              hash(block(old,'function render(){','function polygonAt(')));
});
console.log('V164',count,'source-only and route-integrity tests passed; ART APPROVAL REMAINS RED');
