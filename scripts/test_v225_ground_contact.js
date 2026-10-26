#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('terrain-grid/v225-cartway-ground-contact.js','utf8');
const sandbox={window:{}};
vm.runInNewContext(source,sandbox,{filename:'v225-cartway-ground-contact.js'});
const api=sandbox.window.V225GroundContact;
assert.ok(api&&typeof api.paint==='function');
function context(){
 const traces=[];let current=[];
 return {traces,save(){},restore(){},translate(){},beginPath(){current=[];},
 moveTo(x,y){current.push([x,y]);},lineTo(x,y){current.push([x,y]);},
 stroke(){traces.push(current.map(p=>p.slice()));},
 set filter(v){},set lineCap(v){},set lineJoin(v){},set lineWidth(v){},set strokeStyle(v){}};
}
const roads={
 west:[[110,478],[250,475],[550,485]],
 south:[[150,100],[340,240],[510,320]]
};
const atlas={tiles:[
 {id:'west',origin:[0,0],roads:{main:roads.west.map(p=>p.slice())}},
 {id:'matrei',origin:[1536,0],roads:{bridge:[[0,0],[500,500]]}},
 {id:'south',origin:[1536,1024],roads:{main:roads.south.map(p=>p.slice())}}
]};
const before=JSON.stringify(atlas);
const ctx=context();
const report=api.paint(ctx,atlas);
assert.equal(JSON.stringify(atlas),before,'never mutate original graph');
assert.equal(report.roads,2);assert.equal(report.segments,4);
assert.deepEqual(Array.from(report.cells.map(c=>c.tile)),['west','south']);
assert.equal(report.productionApproved,false);
assert.equal(report.sourceRegisteredToV123,false);
assert.equal(report.bridgeBanksVerified,false);
assert.equal(ctx.traces.length,8,'four ground grades per unchanged route');
for(let i=0;i<4;i++)assert.deepEqual(ctx.traces[i],roads.west);
for(let i=4;i<8;i++)assert.deepEqual(ctx.traces[i],roads.south);
const broken={tiles:[{id:'west',origin:[0,0],roads:{main:[[1,2],[3,4]]}},
 {id:'south',origin:[0,0],roads:{main:[[1,2],[3,4]]}}]};
assert.throws(()=>api.paint(context(),broken),/incomplete/);
const invalid={tiles:[{id:'west',origin:[0,0],roads:{main:[[1,2],[NaN,4],[5,6]]}},
 {id:'south',origin:[0,0],roads:{main:[[1,2],[3,4],[5,6]]}}]};
assert.throws(()=>api.paint(context(),invalid),/invalid original road/);
console.log('V225 graph-locked grading: immutable points, both cells, negative controls PASS');
