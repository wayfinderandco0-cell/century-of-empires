#!/usr/bin/env node
'use strict';
// This tests physical proportions, NOT exact V123 route geography or art quality.
const assert=require('node:assert/strict');
const fit=require('../terrain-grid/v144-geo-material.js').fit;
const v97=require('../terrain-v97/manifest.json');
const v102=require('../terrain-v102/manifest.json');
const ground=[-1500,-1800,6200,5800];
assert.deepEqual(v102.broadBoundsLonLat,v97.boundsLonLat,
  'V102 broad albedo and V97 relief must share the same geographic extent');
const b=v97.boundsLonLat;
for(const [w,h] of [[1536,1024],v97.imageSize]){
  const c=fit(b,ground,w,h);
  assert.ok(c.sy>0&&c.sh<h,'Broad geographic source should crop north/south, not stretch');
  assert.equal(c.sx,0);
  assert.ok(c.sw<=w&&c.sh<=h&&c.sy+c.sh<=h+1e-8);
  assert.ok(Math.abs(c.metresPerWorldX/c.metresPerWorldY-1)<1e-9,
    'No anisotropic mountain stretching');
  assert.deepEqual(c.sourceBoundsLonLat,b);
  assert.equal(c.routeGeoregistered,false);
  assert.equal(c.historicallyCertified,false);
  assert.ok(c.cropLonLat[1]<47.13&&c.cropLonLat[3]>47.13,
    'Crop must retain Matrei-region latitude without claiming route alignment');
}
const crop=fit(b,ground,1536,1024);
const cropFraction=crop.sh/1024;
assert.ok(cropFraction>.53&&cropFraction<.58,'Physical crop differs from full-frame V142 stretch');
const narrow=fit(b,[0,0,3000,9000],1536,1024);
assert.ok(narrow.sx>0&&narrow.sy===0,'Tall view crops east/west');
for(const invalid of [
  [[11,47,11,48],ground,100,100],
  [b,ground,0,100],
  [b,[0,0,-1,500],100,100]
])assert.throws(()=>fit(...invalid));
console.log('V144 source aspect checks passed: V97/V102 common extent, isotropic physical crop, no route certification; vertical fraction='+cropFraction.toFixed(4));
