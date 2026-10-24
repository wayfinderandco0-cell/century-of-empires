#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const {audit,tileCoverage,signedEdge,shaBlob}=require('./v159_game_art_coverage.js');
const poly=[[386,6],[1150,6],[1444,283],[1444,675],[1150,968],[386,968],[91,675],[91,283]];
const preview=`const W=1536,H=1024; const poly=${JSON.stringify(poly)};
center.putImageData(im,0,0); p[k+3]=Math.round(p[k+3]*smooth((d-14)/230));
if(centerPhoto)cx.drawImage(centerPhoto,1536,0,W,H);
get productionApproved(){return false}`;
const atlas=`{id:'west',name:'Western pass',origin:[0,0]}
{id:'matrei',name:'Matrei',origin:[1536,0]}
{id:'south',name:'Southern valley',origin:[1536,1024]}
productionApproved:false`;
const result=audit(preview,atlas,{pinned:false});
assert.equal(result.version,159);
assert.equal(result.productionApproved,false);
assert.equal(result.threeGameOctagonsVisuallyApproved,false);
assert.equal(result.modernSourceSectorsAreNotGameOctagons,true);
assert.equal(result.tiles.west.meanOriginalPhotoAlpha,0);
assert.equal(result.tiles.south.meanOriginalPhotoAlpha,0);
assert.ok(result.tiles.matrei.meanOriginalPhotoAlpha>.2);
assert.ok(result.tiles.matrei.meanOriginalPhotoAlpha<1);
assert.equal(signedEdge(poly,800,500)>200,true);
assert.ok(signedEdge(poly,0,0)<0);
assert.equal(tileCoverage(poly,'matrei',32,24).meanOriginalPhotoAlpha>.2,true);
assert.match(shaBlob(preview),/^[a-f0-9]{40}$/);
let rejects=0;
function reject(p,a,pattern){assert.throws(()=>audit(p,a,{pinned:false}),pattern);rejects++;}
reject(preview.replace('1536,0,W,H','0,0,W,H'),atlas,/origin/);
reject(preview.replace('if(centerPhoto)cx.drawImage(centerPhoto,1536,0,W,H);',
  'if(centerPhoto)cx.drawImage(centerPhoto,1536,0,W,H); cx.drawImage(centerPhoto,0,0,W,H);'),atlas,/once/);
reject(preview.replace('smooth((d-14)/230)','smooth((d-14)/10)'),atlas,/feather/);
reject(preview.replace('const W=1536,H=1024','const W=1536,H=2048'),atlas,/dimensions/);
reject(preview.replace('center.putImageData(im,0,0)','center.drawImage(im,0,0)'),atlas,/alpha source/);
reject(preview.replace('get productionApproved(){return false}','get productionApproved(){return true}'),atlas,/release flag/);
reject(preview,atlas.replace('origin:[1536,1024]','origin:[1536,0]'),/origin changed/);
reject(preview,atlas.replace('productionApproved:false','productionApproved:true'),/release flag/);
reject(preview.replace('const poly='+JSON.stringify(poly),'const poly=[]'),atlas,/boundary/);
reject(preview.replace('const poly='+JSON.stringify(poly),'const poly=[[0,0]]'),atlas,/polygon/);
assert.throws(()=>audit(preview,atlas),/identity drift/);rejects++;
assert.throws(()=>tileCoverage(poly,'invented'),/Unknown game/);rejects++;
console.log(`V159 PASS: actual-photo-only three-game-octagon coverage; ${rejects} fail-closed negative cases; no art/historical/release claims`);
