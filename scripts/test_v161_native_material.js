#!/usr/bin/env node
/* V161 isolated material-study guard: source identities and unchanged routes.
 * No browser or numeric detail score grants visual/historical approval.
 */
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const shaBlob=data=>crypto.createHash('sha1').update(Buffer.concat([
 Buffer.from('blob '+data.length+'\\0'),data])).digest('hex');
const pins=Object.freeze({
 'terrain-v102/alpine-material.webp':'a6f9ef315d2a34766d1ed4e3be2cabb47c23473a',
 'terrain-v97/brenner-relief.webp':'fb8301549db4735db321150929d32b6e7f3d5344',
 'v121-octagon-1-painted-road.html':'4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382',
 'terrain-grid/v123-atlas.js':'09f04b4062e24fbacbb645307462cdddce2b2aa3'
});
function checkSources(read=path=>fs.readFileSync(path)){
 for(const [path,pin] of Object.entries(pins))
   assert.equal(shaBlob(read(path)),pin,'Unreviewed source change: '+path);
}
function sliceBetween(source,a,b){
 const start=source.indexOf(a),end=source.indexOf(b,start+a.length);
 assert(start>=0&&end>start,'Missing reviewed source section: '+a);
 return source.slice(start,end);
}
function checkPreview(v160,v161){
 for(const [start,end] of [
  ['function paintTrack(', 'function paintNaturalTrailFinish('],
  ['function render(){','function polygonAt('],
  ['function issue(to){','function nearestRoadNode('],
  ['function march(dt){','function halt(){'],
  ['function halt(){','C.addEventListener('],
  ['async function boot(){','function frame(t){']
 ])assert.equal(sliceBetween(v161,start,end),sliceBetween(v160,start,end),
     'V161 altered original road/army/render/boot behavior: '+start);
 for(const marker of [
  "const groundBounds=[-1500,-1800,6200,5800]",
  "const poly=[[386,6],[1150,6],[1444,283],[1444,675],[1150,968],[386,968],[91,675],[91,283]]",
  "atlas=V123Atlas.create(v121Roads,{experimentalSeams:true})",
  "surveyLimits=V152Survey.inspect(atlas)",
  "g.drawImage(material,0,0,2048,2048)",
  "groundDetails=null",
  "syntheticTreeMarks:0,materialTilesDrawn:1",
  "v123ToMaterialGeoregistered:false",
  "bridgeBanksVerified:false",
  "historicalLandcoverVerified:false",
  "physicalIPhoneApproved:false,productionApproved:false",
  "get productionApproved(){return false}"
 ])assert(v161.includes(marker),'Missing material/provenance guard: '+marker);
 assert(!v161.includes('for(let i=0;i<122000;i++'),'Cartoon tree stamps reintroduced');
 assert(!v161.includes('for(let i=0;i<32000;i++'),'Fake rock decals reintroduced');
 assert(!v161.includes('photoStamp(source'),'Repeated photo stamps reintroduced');
 assert(!v161.includes('sourceGeoMaterial=new URLSearchParams'),'Unreviewed source-mode switching');
 assert(!v161.includes('sourceGeoregistered:true'),'Unverified geographic claim');
 assert(!v161.includes('productionApproved:true'),'Unapproved production flag');
}
checkSources();
const old=fs.readFileSync('v160-matrei-seam-study.html','utf8');
const study=fs.readFileSync('v161-native-material-study.html','utf8');
checkPreview(old,study);
let negatives=0;
function rejects(fn){assert.throws(fn);negatives++;}
rejects(()=>checkPreview(old,study.replace('bridgeBanksVerified:false','bridgeBanksVerified:true')));
rejects(()=>checkPreview(old,study.replace('g.drawImage(material,0,0,2048,2048)','g.drawImage(material,0,0,1024,1024)')));
rejects(()=>checkPreview(old,study.replace('atlas=V123Atlas.create(v121Roads,{experimentalSeams:true})','atlas=V123Atlas.create({}, {experimentalSeams:true})')));
rejects(()=>checkPreview(old,study.replace('get productionApproved(){return false}','get productionApproved(){return true}')));
rejects(()=>checkSources(path=>path==='terrain-v97/brenner-relief.webp'?Buffer.from('fake'):fs.readFileSync(path)));
console.log('V161 PASS: 4 original source identities, unchanged route/render/army code; '+negatives+' tamper cases rejected. Artwork approval remains RED.');
