#!/usr/bin/env node
'use strict';
// Independent z18 reference values, computed from native XYZ (not game geometry).
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const geo=require('../terrain-grid/v213-source-geodesy.js');
const cases=[
  ['west',[256,256],11.435394287109375,47.1000446940252,[139399,92096,18]],
  ['matrei',[768,256],11.438140869140625,47.1000446940252,[139401,92096,18]],
  ['south',[768,768],11.438140869140625,47.09817500706038,[139401,92098,18]]
];
for(const [cell,xy,lon,lat,xyz] of cases){
  const got=geo.toGeo(cell,xy);
  assert.ok(Math.abs(got.lon-lon)<1e-10,{cell,lon:got.lon});
  assert.ok(Math.abs(got.lat-lat)<1e-10,{cell,lat:got.lat});
  assert.deepEqual(got.nativeXYZ,xyz);
  assert.deepEqual(got.nativePixelXY,[0,0]);
  assert.equal(got.gameGeographyVerified,false);
  assert.equal(got.historicalGeographyVerified,false);
  assert.equal(got.sourceStatus,'MODERN_NATIVE_XYZ_NOT_REGISTERED_TO_GAME');
}
const westEnd=geo.toGeo('west',[511.999,256]);
const matreiStart=geo.toGeo('matrei',[512,256]);
assert.ok(westEnd.lon<matreiStart.lon && matreiStart.lon-westEnd.lon<1e-7);
assert.ok(Math.abs(westEnd.lat-matreiStart.lat)<1e-10);
const matreiEnd=geo.toGeo('matrei',[768,511.999]);
const southStart=geo.toGeo('south',[768,512]);
assert.ok(matreiEnd.lat>southStart.lat && matreiEnd.lat-southStart.lat<1e-7);
assert.ok(Math.abs(matreiEnd.lon-southStart.lon)<1e-10);
for(const [cell,xy] of [
 ['unknown',[1,1]],['west',[512,10]],['west',[-.01,100]],['west',[0,512]],
 ['matrei',[511.99,50]],['matrei',[1024,50]],['south',[768,511.99]],
 ['south',[768,1024]],['south',[NaN,600]],['south',[Infinity,600]],
 ['west',['100',100]],['west',null],['west',[1]],['west',[1,2,3]]
])assert.throws(()=>geo.toGeo(cell,xy),RangeError,JSON.stringify({cell,xy}));
const ui=fs.readFileSync(path.join(__dirname,'../v213-landmark-geographic-review.html'),'utf8');
assert.match(ui,/terrain-grid\/v213-source-geodesy\.js/);
assert.match(ui,/window\.V213/);
assert.match(ui,/sourceGeo:/);
assert.match(ui,/UNVERIFIED_VISUAL_OBSERVATION_NOT_INDEPENDENTLY_MATCHED/);
assert.match(ui,/sourceRegisteredToV123:false/);
assert.match(ui,/gameArtApproved:false/);
assert.match(ui,/physicalIPhoneApproved:false/);
console.log('V213: native geographic centers, 2 seams, 14 invalid cases, provenance and approval barriers PASS');
