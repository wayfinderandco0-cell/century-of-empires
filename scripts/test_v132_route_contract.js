#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const {validateRoute}=require('../terrain-grid/v132-route-contract.js');
let passed=0;
const check=(name,fn)=>{fn();passed++;console.log('PASS '+name);};
const a='a',b='b',c='c',d='d';
const graph=new Map([
 [a,{id:'matrei',world:[0,0],edges:[{to:b,length:10,kind:'painted-road'}]}],
 [b,{id:'matrei',world:[10,0],edges:[{to:a,length:10,kind:'painted-road'},{to:c,length:0,kind:'approved-seam'}]}],
 [c,{id:'west',world:[10,0],edges:[{to:b,length:0,kind:'approved-seam'},{to:d,length:10,kind:'painted-road'}]}],
 [d,{id:'west',world:[20,0],edges:[{to:c,length:10,kind:'painted-road'}]}]
]);
const net={graph};
const route={keys:[a,b,c,d],positions:[[0,0],[10,0],[10,0],[20,0]],distance:20,seams:1};
const verify=r=>validateRoute(net,r);
const copy=r=>JSON.parse(JSON.stringify(r));
check('Existing painted road and approved bridge seam pass',()=>assert.equal(verify(route).pass,true));
check('Reverse route remains valid',()=>assert.equal(verify({keys:[d,c,b,a],positions:route.positions.slice().reverse(),distance:20,seams:1}).pass,true));
check('Missing graph edge cannot shortcut a closed segment',()=>{
 const r=copy(route);r.keys=[a,d];r.positions=[[0,0],[20,0]];assert.equal(verify(r).reason,'missing_approved_edge');
});
check('Untrusted image-space army point rejected',()=>{
 const r=copy(route);r.positions[1]=[10,2];assert.equal(verify(r).reason,'untrusted_waypoint');
});
check('False length and seam claims rejected',()=>{
 const r=copy(route);r.distance=0;assert.equal(verify(r).reason,'distance_mismatch');
 r.distance=20;r.seams=0;assert.equal(verify(r).reason,'seam_count_mismatch');
});
check('No implicit crossing if seam edge loses approval',()=>{
 const edge=graph.get(b).edges[1];edge.kind='painted-road';
 assert.equal(verify(route).reason,'unapproved_tile_crossing');edge.kind='approved-seam';
});
check('Reject malformed routes and nonfinite points',()=>{
 for(const r of [null,{keys:[],positions:[]},{keys:[a],positions:[[Infinity,0]]},
   {keys:[a,b],positions:[[0,0]]}])assert.equal(verify(r).pass,false);
});
check('Single-node stationary route is permitted',()=>{
 assert.equal(verify({keys:[a],positions:[[0,0]],distance:0,seams:0}).pass,true);
});
check('Real V123 graph obeys route contract and known village closure',()=>{
 const atlas=require('../terrain-grid/v123-atlas.js');
 const source=require('../terrain-grid/octagon-1-v121.manifest.json');
 const scene=atlas.create(source.movement.roads,{experimentalSeams:true});
 const ends=atlas.endpoints(scene);
 const allowed=scene.network.planRoute(ends.bridge,ends.south);
 assert(allowed);assert.equal(validateRoute(scene.network,allowed).pass,true);
 const suspect=scene.network.key('matrei',[1137,112]);
 assert.equal(scene.network.planRoute(ends.bridge,suspect),null);
 const prod=atlas.create(source.movement.roads);
 assert.equal(prod.network.planRoute(atlas.endpoints(prod).west,atlas.endpoints(prod).south),null);
});
console.log(JSON.stringify({version:132,passed,failed:0,roadSurfaceRepaired:false,productionApproved:false}));
