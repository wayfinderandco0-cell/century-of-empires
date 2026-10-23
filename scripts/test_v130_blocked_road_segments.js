#!/usr/bin/env node
'use strict';
// V130: raw-source visual hazards close graph edges, not merely add a warning.
// No historical cartway or replacement coordinates are inferred.
const assert=require('node:assert/strict');
const {buildNetwork}=require('../terrain-grid/v122-seam-engine.js');
const atlas=require('../terrain-grid/v123-atlas.js');
const source=require('../terrain-grid/octagon-1-v121.manifest.json');
let passed=0;
function check(label,fn){fn();passed++;console.log('PASS '+label);}
const tile=(blocked)=>({id:'test',origin:[0,0],width:1536,height:1024,corner:256,
 roads:{road:[[400,400],[500,400],[600,400]]},blockedRoadSegments:blocked});
const graph=(blocked)=>buildNetwork({tiles:[tile(blocked)],links:[]});
check('Unblocked synthetic road remains traversable',()=>{
 const net=graph({});
 assert(net.planRoute(net.key('test',[400,400]),net.key('test',[600,400])));
});
check('Closing one segment stops travel in BOTH directions',()=>{
 const net=graph({road:[1]});
 const a=net.key('test',[400,400]),b=net.key('test',[600,400]);
 assert.equal(net.planRoute(a,b),null);
 assert.equal(net.planRoute(b,a),null);
 assert(net.planRoute(a,net.key('test',[500,400])));
});
check('Reject invalid or ambiguous closures rather than silently opening',()=>{
 for(const bad of [{unknown:[0]},{road:[-1]},{road:[2]},{road:[1,1]},
                   {road:[1.5]},{road:['1']},{road:[null]},{road:true}]){
  assert.throws(()=>graph(bad),/Bad blocked road segment/);
 }
});
check('Reviewed village mismatch is explicitly closed in the V123 engineering atlas',()=>{
 const demo=atlas.create(source.movement.roads,{experimentalSeams:true});
 const center=demo.tiles.find(t=>t.id==='matrei');
 assert.deepEqual(center.blockedRoadSegments.village,[12,13,14,15]);
 assert.deepEqual(center.roads.village,source.movement.roads.village,
   'Raw V121 source coordinates must remain immutable');
 const net=demo.network;
 const lower=net.key('matrei',[1150,568]);
 const upper=net.key('matrei',[1058,220]);
 const bridge=net.key('matrei',[813,486]);
 assert(net.planRoute(bridge,lower),'Safe bridge-to-village junction must remain accessible');
 assert.equal(net.planRoute(bridge,upper),null,'No army may traverse suspect road from below');
 assert.equal(net.planRoute(upper,bridge),null,'No army may traverse suspect road from above');
 for(let i=12;i<=15;i++){
  const a=net.graph.get(net.key('matrei',center.roads.village[i]));
  const b=net.key('matrei',center.roads.village[i+1]);
  assert(!a||!a.edges.some(e=>e.to===b),'Closed segment '+i+' must not exist in graph');
 }
 assert.equal(demo.productionApproved,false);
 assert.equal(demo.physicalIPhoneApproved,false);
});
check('Other experimental corridors and strict production seam gate remain intact',()=>{
 const demo=atlas.create(source.movement.roads,{experimentalSeams:true});
 const ends=atlas.endpoints(demo);
 assert(demo.network.planRoute(ends.west,ends.south));
 assert.equal(demo.network.seams.filter(s=>s.pass).length,2);
 const prod=atlas.create(source.movement.roads);
 assert(prod.network.seams.every(s=>!s.pass));
 assert.equal(prod.productionApproved,false);
});
console.log(JSON.stringify({version:130,passed,failed:0,roadSurfaceRepaired:false,
 historicalRoadAccuracyVerified:false,productionApproved:false}));
