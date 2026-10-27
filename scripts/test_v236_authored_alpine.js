#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const V123=require('../terrain-grid/v123-atlas.js');
const V236=require('../terrain-grid/v236-authored-alpine.js');
const V226=require('../terrain-grid/v226-artwork-contract.js');
const html=fs.readFileSync(path.join(__dirname,'../v121-octagon-1-painted-road.html'),'utf8');
const roads=JSON.parse(html.match(/const ROADS=(\\{[^\\r\\n]+\\});/)[1]);
const atlas=V123.create(roads,{experimentalSeams:true});
const before=JSON.stringify(atlas.tiles);
V226.build(atlas);V236.assertAtlas(atlas);
assert.deepEqual(V236.approvals,{sourceRegisteredToV123:false,historicalRoadsVerified:false,
 bridgeBanksVerified:false,onwardRoadVerified:false,licenseVerified:false,
 roadClearanceVerified:false,gameArtApproved:false,humanVisualApproval:false,
 physicalIPhoneApproved:false,productionApproved:false});
let calls=0,trees=0,clipCount=0,drawImages=0;
const ctx=new Proxy({}, {get(t,k){
 if(k==='createLinearGradient')return ()=>({addColorStop(){}});
 if(k==='ellipse')return ()=>{trees++};
 if(k==='clip')return ()=>{clipCount++};
 if(k==='drawImage')return ()=>{drawImages++};
 if(['save','restore','translate','beginPath','moveTo','lineTo','closePath','fill','stroke','fillRect'].includes(k))return ()=>{calls++};
 return t[k];
},set(t,k,v){t[k]=v;return true}});
const report=V236.paint(ctx,atlas);
assert.equal(report.cells,2);assert.equal(report.productionApproved,false);
assert.ok(calls>3000,'real authored terrain features must render');
assert.ok(trees>100,'scene should have individual trees');
assert.equal(clipCount,2,'exactly two neighbor octagon clips');
assert.equal(drawImages,0,'do not copy Matrei or unrelated photographs');
assert.equal(JSON.stringify(atlas.tiles),before,'art cannot mutate route geometry');
for(const id of ['west','south']){
 const tampered=V123.create(roads,{experimentalSeams:true});
 const tile=tampered.tiles.find(t=>t.id===id);
 tile.roads[id==='west'?'east':'north'][4][0]+=1;
 assert.throws(()=>V236.assertAtlas(tampered),/drift/);
}
assert.throws(()=>V236.paint(ctx,{...atlas,productionApproved:true}),/rejected/);
const preview=fs.readFileSync(path.join(__dirname,'../v236-authored-alpine-playtest.html'),'utf8');
assert.match(preview,/V236AuthoredAlpine\.paint\(cx,atlas\)/);
assert.match(preview,/centerPhoto\)cx\.drawImage\(centerPhoto,1536,0,W,H\)/);
assert.match(preview,/V192\.orderTo|orderTo\(/);
console.log('V236 PASS: '+calls+' drawn features; '+trees+' crowns; 2 exact clips; 0 image copies; immutable roads, false approvals and tamper controls');
