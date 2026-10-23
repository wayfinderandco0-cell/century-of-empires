#!/usr/bin/env node
'use strict';
// V124: movement roads must stay within the octagon polygon, not merely its
// rectangular image. No historical routes or new gameplay nodes are added.
const assert=require('node:assert/strict');
const {octagon,insideOctagon,buildNetwork}=require('../terrain-grid/v122-seam-engine.js');
const atlas=require('../terrain-grid/v123-atlas.js');
const manifest=require('../terrain-grid/octagon-1-v121.manifest.json');
const polygon=octagon(1536,1024,256);
let checks=0;
function check(label,fn){fn();checks++;console.log('PASS '+label);}
function tile(roads,origin=[0,0]){
 return {id:'sample',origin,width:1536,height:1024,corner:256,roads};
}
function shouldReject(roads,pattern,origin=[0,0]){
 assert.throws(()=>buildNetwork({tiles:[tile(roads,origin)],links:[]}),pattern);
}
check('Interior and actual border points remain legal',()=>{
 assert(insideOctagon([500,500],polygon));
 assert(insideOctagon([0,478],polygon));
 assert(insideOctagon([466,1024],polygon));
 const net=buildNetwork({tiles:[tile({r:[[500,500],[0,478]]})],links:[]});
 assert(net.planRoute(net.key('sample',[500,500]),net.key('sample',[0,478])));
});
check('Outside rectangular edge is not traversable',()=>{
 shouldReject({r:[[500,500],[1550,500]]},/Road leaves octagon/);
});
check('Rectangular cut-corner is not traversable',()=>{
 assert(!insideOctagon([20,20],polygon));
 shouldReject({r:[[500,500],[20,20]]},/Road leaves octagon/);
});
check('Off-map intermediate waypoint is rejected',()=>{
 shouldReject({r:[[500,500],[20,20],[500,600]]},/Road leaves octagon/);
});
check('Malformed/nonfinite road coordinates are rejected',()=>{
 shouldReject({r:[[500,500],[NaN,500]]},/Road leaves octagon/);
 shouldReject({r:[[500,500],[null,500]]},/Road leaves octagon/);
 shouldReject({r:[[500,500],[Infinity,500]]},/Road leaves octagon/);
});
check('Malformed origins and corner cuts are rejected',()=>{
 shouldReject({r:[[500,500],[600,500]]},/Bad tile/,[NaN,0]);
 shouldReject({r:[[500,500],[600,500]]},/Bad tile/,[0]);
 assert.throws(()=>buildNetwork({tiles:[{...tile({r:[[500,500],[600,500]]}),corner:700}],links:[]}),/Invalid octagon geometry/);
});
check('Existing V123 prototype routes stay connected only in engineering mode',()=>{
 const draft=atlas.create(manifest.movement.roads);
 assert(draft.network.seams.every(s=>!s.pass));
 const a=atlas.create(manifest.movement.roads,{experimentalSeams:true});
 const endpoints=atlas.endpoints(a);
 const route=a.network.planRoute(endpoints.west,endpoints.south);
 assert(route&&route.seams===2);
 assert.equal(a.productionApproved,false);
 assert.equal(a.physicalIPhoneApproved,false);
});
console.log(JSON.stringify({passed:checks,failed:0,productionApproved:false}));
