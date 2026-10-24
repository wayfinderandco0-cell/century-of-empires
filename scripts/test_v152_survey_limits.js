#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const V123=require('../terrain-grid/v123-atlas.js');
const V152=require('../terrain-grid/v152-survey-limits.js');
const html=fs.readFileSync('v121-octagon-1-painted-road.html','utf8');
const match=html.match(/const ROADS=(\{[^\r\n]+\});/);
assert.ok(match,'Original V121 immutable road declaration missing');
const originalRoads=JSON.parse(match[1]);
const fresh=()=>V123.create(originalRoads,{experimentalSeams:true});
const atlas=fresh(),before=JSON.stringify(atlas.tiles);
const report=V152.inspect(atlas);
assert.equal(report.version,152);
assert.equal(report.markers.length,2);
assert.deepEqual(report.markers.map(m=>m.world),[[275,550],[2806,1629]]);
assert.deepEqual(report.markers.map(m=>m.tile),['west','south']);
assert.equal(JSON.stringify(atlas.tiles),before,'Inspector must not edit roads');
assert.equal(report.gameGraphChanged,false);
assert.equal(report.unverifiedContinuationsDrawn,false);
assert.equal(report.onwardNavigationApproved,false);
assert.equal(report.productionApproved,false);
const start=V123.endpoints(atlas).matrei;
for(const m of report.markers){
  const route=atlas.network.planRoute(start,m.nodeKey);
  assert.ok(route&&route.positions.length>1,'Graph must reach its genuine endpoint');
  assert.deepEqual(route.positions.at(-1),m.world);
  assert.equal(atlas.network.graph.get(m.nodeKey).edges.length,1);
  assert.equal(m.onwardRoadVerified,false);
  assert.equal(m.physicalBarrierClaimed,false);
  assert.equal(m.historic1780Certified,false);
}
const calls=[];
const ctx=new Proxy({}, {get(_obj,key){
  if(key==='save'||key==='restore'||key==='beginPath'||key==='fill'||key==='stroke')
    return ()=>calls.push([key]);
  if(['translate','scale','arc','fillText','fillRect'].includes(key))
    return (...args)=>calls.push([key,...args]);
  return undefined;
},set(){return true;}});
V152.paint(ctx,.18,report,true);
assert.deepEqual(calls.filter(c=>c[0]==='translate').map(c=>c.slice(1)),[[275,550],[2806,1629]]);
assert.equal(calls.filter(c=>c[0]==='fillText'&&c[1]==='?').length,2);
assert.equal(calls.filter(c=>c[0]==='fillText'&&c[1]==='UNSURVEYED EXIT').length,2);
assert.equal(calls.filter(c=>c[0]==='save').length,2);
assert.equal(calls.filter(c=>c[0]==='restore').length,2);
let negatives=0;
function reject(mutate,pattern){
  const a=fresh();mutate(a);
  assert.throws(()=>V152.inspect(a),pattern);negatives++;
}
reject(a=>a.tiles.find(t=>t.id==='west').roads.east.push([300,560]),/geometry changed/);
reject(a=>a.tiles.find(t=>t.id==='south').roads.north.at(-1)[0]++,/geometry changed/);
reject(a=>a.tiles.find(t=>t.id==='west').origin[0]++,/geometry changed/);
reject(a=>a.tiles.find(t=>t.id==='south').roads.north=[],/geometry changed/);
reject(a=>a.network.graph.delete(a.network.key('west',[275,550])),/terminal road vertex/);
reject(a=>a.network.graph.get(a.network.key('south',[1270,605])).edges.push({to:'invented',kind:'painted-road'}),/terminal road vertex/);
reject(a=>a.tiles.splice(a.tiles.findIndex(t=>t.id==='west'),1),/Missing pinned/);
for(const bad of [0,NaN,-1,Infinity]){
  assert.throws(()=>V152.paint(ctx,bad,report),/validated report/);negatives++;
}
assert.throws(()=>V152.paint(ctx,1,{...report,productionApproved:true}),/validated report/);negatives++;
console.log('V152: both pinned V123 survey termini exact, degree-one, reachable, visibly marked, no invented continuation; '+negatives+' negative cases PASS. No art/historical/iPhone approval.');
