#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const geo=require('../terrain-grid/v148-orthophoto-pixels.js');
if(process.argv.length!==3) throw Error('Usage: node scripts/test_v148_orthophoto_pixels.js <V147 planned manifest.json>');
const m=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const v=geo.verify(m);
assert.equal(v.dimension,768);
assert.equal(m.samples.length,9);
assert.equal(m.productionApproved,false);
const copy=()=>JSON.parse(JSON.stringify(m));
let checks=0;
for(const sample of m.samples){
  const b=sample.tileBoundsLonLat;
  const lon=(b[0]+b[2])/2,lat=(b[1]+b[3])/2;
  const p=geo.geoToPixel(m,lon,lat);
  assert.equal(p.gridRow,sample.gridRow);
  assert.equal(p.gridCol,sample.gridCol);
  assert.equal(p.source,sample.name);
  assert.ok(Math.abs(p.tilePixel[0]-128)<1e-6);
  assert.ok(Math.abs(p.tilePixel[1]-128)<.002); // midpoint latitude is not exact Mercator midpoint
  const ll=geo.pixelToGeo(m,p.x,p.y);
  assert.ok(Math.abs(ll[0]-lon)<1e-10 && Math.abs(ll[1]-lat)<1e-10);
  assert.equal(p.gameRouteGeoregistered,false);
  checks++;
}
// Geographic source bounds and all four pixel corners are independent of the
// fantasy road/canvas world. Preserve half-open east/south pixel semantics.
const [west,south,east,north]=m.mosaicBoundsLonLat;
const upperLeft=geo.pixelToGeo(m,0,0);
assert.ok(Math.abs(upperLeft[0]-west)<1e-10 && Math.abs(upperLeft[1]-north)<1e-10);
const bottomRight=geo.pixelToGeo(m,768,768,true);
assert.ok(Math.abs(bottomRight[0]-east)<1e-10 && Math.abs(bottomRight[1]-south)<1e-10);
assert.throws(()=>geo.pixelToGeo(m,768,768),/outside/);
assert.throws(()=>geo.geoToPixel(m,east,north),/outside/);
assert.throws(()=>geo.geoToPixel(m,west,south),/outside/);
checks+=5;
const mid=m.samples[4].tileBoundsLonLat;
const crop=geo.cropForBounds(m,mid);
assert.deepEqual(crop.pixelRect,[256,256,512,512]);
assert.equal(crop.noResampling,true);
assert.equal(crop.productionApproved,false);
const full=geo.cropForBounds(m,m.mosaicBoundsLonLat);
assert.deepEqual(full.pixelRect,[0,0,768,768]);
checks+=5;
const bad=copy();bad.samples[4].tileXYZ[0]++;
assert.throws(()=>geo.verify(bad),/adjacency/);checks++;
const badUrl=copy();badUrl.samples[8].url='https://example.org/fake.jpg';
assert.throws(()=>geo.verify(badUrl),/URL/);checks++;
const badBounds=copy();badBounds.mosaicBoundsLonLat[0]+=.01;
assert.throws(()=>geo.verify(badBounds),/bounds mismatch/);checks++;
const badFlag=copy();badFlag.gameRouteGeoregistered=true;
assert.throws(()=>geo.verify(badFlag),/cannot assert/);checks++;
const badProvider=copy();badProvider.provider='unknown';
assert.throws(()=>geo.verify(badProvider),/Unsupported/);checks++;
assert.throws(()=>geo.geoToPixel(m,NaN,47.13),/Non-finite/);checks++;
assert.throws(()=>geo.geoToPixel(m,west-.01,47.13),/outside/);checks++;
assert.throws(()=>geo.cropForBounds(m,[west-.01,south,east,north]),/beyond/);checks++;
assert.throws(()=>geo.cropForBounds(m,[east,south,west,north]),/Invalid/);checks++;
console.log(`V148 modern source geographic-to-pixel mapping: ${checks} assertions PASS; 9/9 exact tile lookups; no V123 route or historical certification.`);
