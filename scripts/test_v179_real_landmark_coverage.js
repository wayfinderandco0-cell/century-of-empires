'use strict';
const assert=require('node:assert/strict');
const audit=require('../terrain-grid/v179-real-landmark-coverage.js');
const geo=require('../terrain-grid/v178-source-geographic-crosswalk.js');
let passed=0;
function test(name,fn){fn();passed++;console.log('PASS',name);}
const anchors=audit.ANCHORS;
test('Matrei and Brenner are separately sourced modern geographic anchors, not game control points',()=>{
  assert.equal(anchors.length,2);
  assert.equal(new Set(anchors.map(a=>a.id)).size,2);
  assert.ok(anchors.every(a=>a.gameCellAssigned===false&&a.source.startsWith('https://')));
});
test('both geographic anchors are within the V97 relief footprint',()=>{
  assert.ok(anchors.every(a=>audit.auditAnchor(a).inV97Relief));
});
test('Matrei lies in V102 relief but OUTSIDE the small V168 SOURCE L',()=>{
  const a=audit.auditAnchor(anchors[0]);
  assert.equal(a.inV102Relief,true);
  assert.equal(a.observedV168Source,false);
  assert.equal(a.observedSourcePixel,null);
  assert.ok(a.nearestObservedSourceKm>3);
});
test('Brenner Pass lies outside V102 and outside V168 SOURCE L',()=>{
  const a=audit.auditAnchor(anchors[1]);
  assert.equal(a.inV102Relief,false);
  assert.equal(a.observedV168Source,false);
  assert.ok(a.nearestObservedSourceKm>10);
});
test('Navis SOURCE center is observed but does NOT gain historic road or GAME eligibility',()=>{
  const a=audit.auditAnchor({id:'navis-source-study',lon:11.520,lat:47.130,
    source:'https://github.com/wayfinderandco0-cell/century-of-empires/issues/9',
    evidenceType:'modern-location-reference',gameCellAssigned:false});
  assert.equal(a.observedV168Source,true);
  assert.equal(a.observedSourceSector,'source-center');
  assert.ok(a.observedSourcePixel.every(Number.isFinite));
  assert.equal(a.deepZoomGameArtEligible,false);
  assert.equal(a.v123RoadsGeoregistered,false);
  assert.equal(a.bridgeBanksVerified,false);
});
test('unknown southwest of L is not promoted to observed imagery',()=>{
  const [lon,lat]=geo.sourceToLonLat(384,768);
  const a=audit.auditAnchor({id:'unknown',lon,lat,
    source:'https://github.com/wayfinderandco0-cell/century-of-empires/issues/9',
    evidenceType:'modern-location-reference',gameCellAssigned:false});
  assert.equal(a.observedV168Source,false);
  assert.equal(a.observedSourcePixel,null);
  assert.ok(a.nearestObservedSourceKm>0);
});
test('geographic distance is symmetric, zero at same point, and sane between anchors',()=>{
  const a=[anchors[0].lon,anchors[0].lat],b=[anchors[1].lon,anchors[1].lat];
  assert.equal(audit.km(a,a),0);
  assert.ok(Math.abs(audit.km(a,b)-audit.km(b,a))<1e-9);
  assert.ok(audit.km(a,b)>14&&audit.km(a,b)<16);
});
test('source geographic sector bounds are exactly the existing V178 crosswalk',()=>{
  const bounds=audit.sourceBounds(),m=geo.crosswalk();
  assert.equal(bounds.length,3);
  for(const s of bounds)assert.deepEqual(s.bounds,m.sectors[s.id].geographicBoundsLonLat);
});
test('invalid or forged anchor provenance and game assignments fail closed',()=>{
  const a=anchors[0];
  for(const bad of [{...a,lon:Infinity},{...a,lat:90},{...a,source:'http://unverified.example'},
    {...a,evidenceType:'historic-road-confirmed'},{...a,gameCellAssigned:true},
    {...a,id:''}]){
    assert.throws(()=>audit.auditAnchor(bad),/invalid|unverified|missing/);
  }
});
test('coverage plan does not falsely locate West/South or certify V121/V123 art',()=>{
  const p=audit.coveragePlan();
  assert.equal(p.version,179);
  assert.deepEqual(p.existingSourceFrame,[69726,46030,17]);
  assert.equal(p.anchors.length,2);
  for(const key of ['matreiGameArtRegistered','westernPassGameLocationResolved',
    'southernValleyGameLocationResolved','proposedThreeGameCellFootprintApproved',
    'allThreeGameCellsCoveredByHighResSource','v123RoadsGeoregistered',
    'bridgeBanksVerified','periodArtComplete','physicalIPhoneApproved','productionApproved'])
    assert.equal(p[key],false,key);
  assert.ok(p.anchors.every(a=>!a.observedV168Source));
});
console.log('V179 independently sourced geographic anchor/coverage checks:',passed,'passed; no GAME approval.');
