/* V179: independent geographic landmark coverage, NOT GAME registration.
   Never infer V121/V123 painted-road coordinates from real-world place names. */
'use strict';
const geo = require('./v178-source-geographic-crosswalk.js');
const V97 = Object.freeze([11.26,46.80,11.80,47.42]);
const V102 = Object.freeze([11.43,47.075,11.625,47.19]);
const ANCHORS = Object.freeze([
  Object.freeze({
    id:'matrei-am-brenner', name:'Matrei am Brenner (town reference)',
    lon:11.45306, lat:47.13083,
    source:'https://en.wikipedia.org/wiki/Matrei_am_Brenner',
    evidenceType:'modern-location-reference', gameCellAssigned:false
  }),
  Object.freeze({
    id:'brenner-pass', name:'Brenner Pass (geographic saddle reference)',
    lon:11.50750, lat:47.00333,
    source:'https://en.wikipedia.org/wiki/Brenner_Pass',
    evidenceType:'modern-location-reference', gameCellAssigned:false
  })
]);
function assert(ok,msg){if(!ok)throw Error(msg);}
function inside(lon,lat,b){return lon>=b[0]&&lon<=b[2]&&lat>=b[1]&&lat<=b[3];}
function km(a,b){
  const r=Math.PI/180, dlat=(b[1]-a[1])*r, dlon=(b[0]-a[0])*r;
  const q=Math.sin(dlat/2)**2+Math.cos(a[1]*r)*Math.cos(b[1]*r)*Math.sin(dlon/2)**2;
  return 6371.0088*2*Math.atan2(Math.sqrt(q),Math.sqrt(Math.max(0,1-q)));
}
function sourceBounds(){
  const m=geo.crosswalk();
  return Object.entries(m.sectors).map(([id,v])=>({id,bounds:v.geographicBoundsLonLat}));
}
function distanceToObservedSourceKm(lon,lat){
  const p=[lon,lat];
  return Math.min(...sourceBounds().map(({bounds:b})=>
    km(p,[Math.min(b[2],Math.max(b[0],lon)),Math.min(b[3],Math.max(b[1],lat))])));
}
function auditAnchor(a){
  assert(a&&typeof a.id==='string'&&a.id.length>0,'missing anchor ID');
  assert(Number.isFinite(a.lon)&&a.lon>=-180&&a.lon<=180&&
    Number.isFinite(a.lat)&&Math.abs(a.lat)<85,'invalid anchor lon/lat');
  assert(a.evidenceType==='modern-location-reference'&&
    typeof a.source==='string'&&a.source.startsWith('https://')&&
    a.gameCellAssigned===false,'unverified geographic anchor provenance or game assignment');
  let sourcePixel=null, observedSector=null;
  try{
    const [x,y]=geo.lonLatToSource(a.lon,a.lat);
    observedSector=geo.sectorAt(x,y);
    if(observedSector!==null)sourcePixel=[x,y];
  }catch(_e){ /* Geographic anchor outside the acquired SOURCE image. */ }
  return {
    id:a.id, lonLat:[a.lon,a.lat], evidenceURL:a.source,
    inV97Relief:inside(a.lon,a.lat,V97),
    inV102Relief:inside(a.lon,a.lat,V102),
    observedV168Source:observedSector!==null,
    observedSourceSector:observedSector,
    observedSourcePixel:sourcePixel,
    nearestObservedSourceKm:+distanceToObservedSourceKm(a.lon,a.lat).toFixed(3),
    sourceCoverageDoesNotCertifyHistoricArt:true,
    v121PaintedArtRegistered:false,
    v123RoadsGeoregistered:false,
    historicRoadVerified:false,
    bridgeBanksVerified:false,
    deepZoomGameArtEligible:false,
    physicalIPhoneApproved:false,
    productionApproved:false
  };
}
function coveragePlan(){
  const anchors=ANCHORS.map(auditAnchor);
  assert(anchors.every(a=>a.inV97Relief),'reference anchors unexpectedly outside V97 geographic coverage');
  return {
    version:179, status:'GEOGRAPHIC_REFERENCE_ONLY',
    anchors, existingSourceFrame:geo.crosswalk().tileOriginXYZ,
    matreiGameArtRegistered:false,
    westernPassGameLocationResolved:false,
    southernValleyGameLocationResolved:false,
    proposedThreeGameCellFootprintApproved:false,
    allThreeGameCellsCoveredByHighResSource:false,
    nextAction:'Identify independently evidenced GAME-cell footprints and acquire permitted source imagery at matching ground resolution; verify period roads and bridge banks separately.',
    v123RoadsGeoregistered:false, bridgeBanksVerified:false,
    periodArtComplete:false, physicalIPhoneApproved:false, productionApproved:false
  };
}
module.exports={ANCHORS,V97,V102,inside,km,sourceBounds,distanceToObservedSourceKm,auditAnchor,coveragePlan};
