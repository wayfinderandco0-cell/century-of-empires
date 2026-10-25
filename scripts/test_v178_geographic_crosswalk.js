'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const geo = require('../terrain-grid/v178-source-geographic-crosswalk.js');
const root = path.resolve(__dirname, '..');
const json = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
let passed = 0;
function test(name, fn) { fn(); passed++; console.log('PASS', name); }
function rejects(fn, label) { assert.throws(fn, /invalid|outside|unknown|mismatch/ig, label); }
test('source tile origin agrees with V168 XYZ 17 planning', () => {
  assert.deepEqual(geo.ORIGIN, [69726, 46030]);
  assert.deepEqual(geo.crosswalk().tileOriginXYZ, [69726, 46030, 17]);
});
test('V94, V97 and V102 geographic manifests retain their distinct projections', () => {
  assert.equal(geo.verifyManifests(json('terrain-v94/manifest.json'),
    json('terrain-v97/manifest.json'), json('terrain-v102/manifest.json')), true);
});
test('tampered geographic bounds are rejected, never silently aligned', () => {
  const a = json('terrain-v94/manifest.json');
  const b = json('terrain-v97/manifest.json');
  const c = json('terrain-v102/manifest.json');
  rejects(() => geo.verifyManifests({...a, extent:[-15,26,49,75]}, b, c), 'V94 tamper');
  rejects(() => geo.verifyManifests(a, {...b, imageSize:[1600,1782]}, c), 'V97 tamper');
  rejects(() => geo.verifyManifests(a, b, {...c, grid:[256,257]}), 'V102 tamper');
});
test('three real SOURCE sector centers map to distinct locations', () => {
  const pts = [[384,256,'source-west'],[1152,256,'source-center'],[1152,768,'source-south']];
  const outputs = pts.map(([x,y,expected]) => {
    const r = geo.sourceToAtlases(x,y);
    assert.equal(r.sourceSector, expected);
    assert.ok(r.v97ReliefPixel.every(Number.isFinite));
    assert.ok(r.v102GridPixel.every(Number.isFinite));
    assert.ok(r.v94GamePixel.every(Number.isFinite));
    assert.ok(r.v94AtlasPixel.every(Number.isFinite));
    assert.equal(r.v123GameRegistered, false);
    assert.equal(r.playableRoad, false);
    return r.lonLat.join(',');
  });
  assert.equal(new Set(outputs).size, 3);
});
test('Mercator source pixels round-trip to lon/lat with sub-micro-pixel error', () => {
  for (let y=0; y<1024; y+=37) for (let x=0; x<1536; x+=43) {
    if (!geo.sectorAt(x,y)) continue;
    const p = geo.lonLatToSource(...geo.sourceToLonLat(x,y));
    assert.ok(Math.hypot(p[0]-x,p[1]-y)<1e-6, 'roundtrip drift at '+x+','+y);
  }
});
test('west/center seam is geographically continuous in all atlases', () => {
  for (const y of [0,111,255,511]) {
    const a = geo.sourceToAtlases(768-1e-6,y), b = geo.sourceToAtlases(768,y);
    for (const key of ['lonLat','v97ReliefPixel','v102GridPixel','v94GamePixel','v94AtlasPixel'])
      assert.ok(Math.hypot(...a[key].map((v,i)=>v-b[key][i]))<1e-4,key+' seam');
  }
});
test('center/south seam is geographically continuous in all atlases', () => {
  for (const x of [768,899,1152,1535]) {
    const a = geo.sourceToAtlases(x,512-1e-6), b = geo.sourceToAtlases(x,512);
    for (const key of ['lonLat','v97ReliefPixel','v102GridPixel','v94GamePixel','v94AtlasPixel'])
      assert.ok(Math.hypot(...a[key].map((v,i)=>v-b[key][i]))<1e-4,key+' seam');
  }
});
test('unacquired southwest source is unknown, not playable', () => {
  assert.equal(geo.sectorAt(384,768),null);
  rejects(()=>geo.sourceToAtlases(384,768),'SW unknown');
  rejects(()=>geo.sourceToAtlases(-1,100),'outside');
  rejects(()=>geo.sourceToAtlases(1536,100),'outside');
});
test('outside geographic footprint cannot be converted into sourced pixels', () => {
  rejects(()=>geo.lonLatToSource(12,47.13),'outside');
  rejects(()=>geo.sourceToLonLat(1537,0),'outside');
  rejects(()=>geo.sourceToLonLat(100,1025),'outside');
  rejects(()=>geo.lonLatToSource(11.5,90),'invalid');
});
test('source L geography is small, not a fictitious three-valley regional atlas', () => {
  const m=geo.crosswalk(), west=m.sectors['source-west'], south=m.sectors['source-south'];
  assert.ok(west.geographicBoundsLonLat[0]>=11.50);
  assert.ok(south.geographicBoundsLonLat[1]>=47.12);
  assert.ok(m.sectors['source-center'].geographicBoundsLonLat[2]<=11.53);
  assert.ok(m.sectors['source-center'].geographicBoundsLonLat[3]<=47.14);
});
test('crosswalk metadata never certifies painted Matrei or historic roads', () => {
  const m=geo.crosswalk();
  for (const key of ['sourceSectorsAreGameOctagons','v121ToGeographyRegistered',
    'v123RoadsGeoregistered','bridgeBanksVerified','historicalRoadsVerified',
    'periodArtComplete','physicalIPhoneApproved','productionApproved'])
    assert.equal(m[key],false,key);
  assert.equal(m.sourceReferenceOnly,true);
  assert.deepEqual(m.unobservedSouthwest,[0,512,768,1024]);
});
test('shared source boundaries have identical geographic coordinates', () => {
  const m=geo.crosswalk(), w=m.sectors['source-west'].geographicBoundsLonLat,
    c=m.sectors['source-center'].geographicBoundsLonLat,
    s=m.sectors['source-south'].geographicBoundsLonLat;
  assert.equal(w[2],c[0]);assert.equal(w[1],c[1]);assert.equal(w[3],c[3]);
  assert.equal(c[1],s[3]);assert.equal(c[0],s[0]);assert.equal(c[2],s[2]);
});
console.log('V178 geographic source crosswalk:',passed,'tests passed; GAME/road approval remains false.');
