#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const {harmonize}=require('../terrain-grid/v160-seam-tone.js');
const w=160,h=160,pw=128,ph=128;
const bg=new Uint8ClampedArray(w*h*4),photo=new Uint8ClampedArray(pw*ph*4);
for(let i=0;i<bg.length;i+=4){bg[i]=65;bg[i+1]=85;bg[i+2]=58;bg[i+3]=255;}
for(let i=0;i<photo.length;i+=4){photo[i]=106;photo[i+1]=123;photo[i+2]=84;photo[i+3]=255;}
const before=photo.slice(),poly=[[30,8],[98,8],[120,30],[120,98],[98,120],[30,120],[8,98],[8,30]];
const input={background:bg,bgWidth:w,bgHeight:h,photo,photoWidth:pw,photoHeight:ph,
  bounds:[-16,-16,160,160],photoOrigin:[0,0],polygon:poly,inset:24,fadeRadius:35};
const report=harmonize(input);
assert.equal(report.version,160);assert.equal(report.productionApproved,false);
assert.equal(report.sourceGeoregistered,false);assert.equal(report.roadsModified,false);
assert.equal(report.photoModified,false);assert.equal(report.edgesWithEvidence,8);
assert.ok(report.anchors>=30);assert.ok(report.changedBackgroundPixels>1000);
assert.deepEqual(photo,before,'Matrei source painting is immutable');
function at(x,y){const ix=(y*w+x)*4;return [bg[ix],bg[ix+1],bg[ix+2]];}
const near=at(80,20),far=at(0,0);
assert.ok(near[0]>65&&near[1]>85,'Tonal mismatch at Matrei boundary reduced');
assert.deepEqual(far,[65,85,58],'Outside the feather region stays untouched');
assert.throws(()=>harmonize({...input,polygon:poly.slice(0,2)}),/polygon/);
assert.throws(()=>harmonize({...input,maxShift:100}),/reviewed RGBA/);
assert.throws(()=>harmonize({...input,photo:new Uint8ClampedArray(10)}),/reviewed RGBA/);
const red=photo.slice();for(let i=0;i<red.length;i+=4){red[i]=235;red[i+1]=60;red[i+2]=30;}
assert.throws(()=>harmonize({...input,photo:red}),/insufficient natural-source/);
console.log('V160 PASS: 8-edge source-anchored tonal correction; immutable painting; untouched far field; 4 negative tests');
