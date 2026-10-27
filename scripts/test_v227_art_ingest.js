#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const cp=require('node:child_process');
const crypto=require('node:crypto');
const V123=require('../terrain-grid/v123-atlas.js');
const V226=require('../terrain-grid/v226-artwork-contract.js');
const V227=require('../terrain-grid/v227-art-ingest.js');
(async()=>{
 const protectedFiles={
  'v121-octagon-1-painted-road.html':'4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382',
  'terrain-grid/v123-atlas.js':'09f04b4062e24fbacbb645307462cdddce2b2aa3'
 };
 for(const [path,sha] of Object.entries(protectedFiles))
  assert.equal(cp.execFileSync('git',['hash-object',path],{encoding:'utf8'}).trim(),sha);
 const html=fs.readFileSync('v121-octagon-1-painted-road.html','utf8');
 const roads=JSON.parse(html.match(/const ROADS=(\{[^\r\n]+\});/)[1]);
 const atlas=V123.create(roads,{experimentalSeams:true});
 const contract=V226.build(atlas);
 assert.equal(V227.validateContract(contract),true);
 assert.throws(()=>V227.validateContract({...contract,version:227}),/contract/);
 assert.throws(()=>V227.validateContract({...contract,productionApproved:true}),/contract/);
 assert.throws(()=>V227.validateContract({...contract,cells:contract.cells.slice(0,1)}),/two neighbor/);
 assert.throws(()=>V227.validateContract({...contract,cells:contract.cells.map(c=>({...c,origin:[9,9]}))}),/origin/);
 const sample=Buffer.alloc(256,42);
 const file=new Blob([sample],{type:'image/png'});
 file.name='synthetic-test-only.png';
 const sha=crypto.createHash('sha256').update(sample).digest('hex');
 assert.throws(()=>V227.validateFile('matrei',file),/unknown cell/);
 assert.throws(()=>V227.validateFile('west',new Blob([sample],{type:'text/plain'})),/PNG/);
 assert.throws(()=>V227.validateFile('south',new Blob([Buffer.alloc(10)],{type:'image/png'})),/size/);
 global.createImageBitmap=async()=>({width:1536,height:1024,close(){}});
 await assert.rejects(()=>V227.importFile('west',file,contract,{productionApproved:true}),/false approval/);
 await assert.rejects(()=>V227.importFile('west',file,contract,{expectedSha256:'0'.repeat(64)}),/mismatch/);
 const west=await V227.importFile('west',file,contract,{expectedSha256:sha});
 assert.equal(west.sha256,sha);
 assert.equal(west.sourceRegisteredToV123,false);
 assert.equal(west.licenseVerified,false);
 assert.equal(west.productionApproved,false);
 assert.equal(west.roadClearanceVerified,false);
 const south=await V227.importFile('south',file,contract);
 assert.equal(south.origin.join(','),'1536,1024');
 assert.equal(V227.snapshot().cells.filter(Boolean).length,2);
 const calls=[];
 const ctx={save(){calls.push('save')},restore(){calls.push('restore')},
  translate(...p){calls.push(['translate',...p])},
  beginPath(){},moveTo(){},lineTo(){},closePath(){},clip(){calls.push('clip')},
  drawImage(...p){calls.push(['draw',p[1],p[2],p[3],p[4]])}};
 assert.equal(V227.paint(ctx),2);
 assert.equal(calls.filter(c=>Array.isArray(c)&&c[0]==='draw').length,2);
 assert.equal(calls.filter(c=>c==='clip').length,2);
 assert.equal(calls.filter(c=>Array.isArray(c)&&c[0]==='translate')[1].slice(1).join(','),'1536,1024');
 V227.reset('west');assert.equal(V227.paint(ctx),1);
 V227.reset();assert.equal(V227.paint(ctx),0);
 assert.equal(V227.snapshot().productionApproved,false);
 console.log('V227 PASS: protected blobs, exact V226 topology, image-size/SHA/format/tamper negative controls, two-cell canvas paint, no false approval');
})().catch(e=>{console.error(e);process.exit(1)});
