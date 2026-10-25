'use strict';
const assert=require('node:assert/strict');
const {fitCandidate,validateEvidence,mapPoint}=require('../terrain-grid/v172-registration');
const kinds=['ridge','summit','valley-fork','bedrock-feature','saddle','river-confluence'];
function landmark(id,game,kind='ridge',offset=[0,0]){
 return {id,kind,game,source:[game[0]/2+offset[0],game[1]/2+offset[1]],
   independentlyReviewed:true,gameEvidence:'v121-painting-review-'+id,
   sourceEvidence:'v168-source-photo-review-'+id};
}
function fixture(){return {version:172,sourceVersion:169,sourceCrs:'EPSG:3857',
 sourceImageSize:[1536,1024],gameImageSize:[3072,2048],
 sourceMosaicSha256:'a'.repeat(64),gameArtSha256:'b'.repeat(64),
 productionApproved:false,v123RoadsGeoregistered:false,historicalRoadsVerified:false,
 bridgeBanksVerified:false,physicalIPhoneApproved:false,historic1780Certified:false,
 controls:[landmark('one',[100,100],kinds[0]),landmark('two',[1800,100],kinds[1]),
 landmark('three',[2900,900],kinds[2]),landmark('four',[2000,1400],kinds[3])],
 holdouts:[landmark('five',[600,400],kinds[4]),landmark('six',[2400,1300],kinds[5])]};}
let n=0;function check(name,fn){fn();n++;console.log('PASS',name);}
check('six independently reviewed synthetic controls produce a candidate, not approval',()=>{
 const r=fitCandidate(fixture());assert.equal(r.candidatePass,true);
 assert.deepEqual(r.matrix,[[0.5,0,0],[0,0.5,0]]);
 assert.equal(r.productionApproved,false);assert.equal(r.gameRouteGeoregistered,false);
 assert.deepEqual(mapPoint(r.matrix,[2400,1300]),[1200,650]);});
check('unknown geographic southwest is rejected',()=>{const m=fixture();m.holdouts[0].source=[200,800];assert.throws(()=>fitCandidate(m),/outside observed/);});
check('a real landmark needs two independent reviews',()=>{const m=fixture();m.controls[0].sourceEvidence='';assert.throws(()=>fitCandidate(m),/independent evidence/);});
check('no modern road or fictional bridge may act as a landmark',()=>{const m=fixture();m.controls[0].kind='bridge';assert.throws(()=>fitCandidate(m),/unsupported landmark/);});
check('duplicate controls are rejected',()=>{const m=fixture();m.holdouts[0].source=m.controls[0].source.slice();assert.throws(()=>fitCandidate(m),/duplicate geographic/);});
check('collinear control points are rejected',()=>{const m=fixture();m.controls=[landmark('aaa',[100,100],'ridge'),landmark('bbb',[200,200],'summit'),landmark('ccc',[300,300],'saddle'),landmark('ddd',[400,400],'valley-fork')];assert.throws(()=>fitCandidate(m),/collinear|singular/);});
check('independent holdout catches fabricated tie point',()=>{const m=fixture();m.holdouts[0].source[0]+=30;const r=fitCandidate(m);assert.equal(r.candidatePass,false);assert(r.maxHoldoutErrorPx>8);});
check('unreviewed manifest cannot silently become an approved route',()=>{const m=fixture();m.productionApproved=true;assert.throws(()=>fitCandidate(m),/forged/);});
check('source identity cannot be missing',()=>{const m=fixture();m.gameArtSha256='unknown';assert.throws(()=>fitCandidate(m),/SHA256/);});
check('control set cannot consist of one feature class',()=>{const m=fixture();for(const p of [...m.controls,...m.holdouts])p.kind='ridge';assert.throws(()=>fitCandidate(m),/three feature types/);});
check('unreviewed source-first template fails closed',()=>{const m=fixture();m.controls=[];m.holdouts=[];assert.throws(()=>validateEvidence(m),/four reviewed controls/);});
console.log(`${n} V172 candidate registration tests passed (synthetic geometry only; NO real tie points).`);
