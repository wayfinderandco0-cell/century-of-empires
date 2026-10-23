#!/usr/bin/env node
'use strict';
// V131: mobile tap selection must not route to an arbitrary nearby open node
// when the user tapped a reviewed, physically unsupported village segment.
const assert=require('node:assert/strict');
const {hitTest}=require('../terrain-grid/v131-road-hit-test.js');
const {buildNetwork}=require('../terrain-grid/v122-seam-engine.js');
const atlas=require('../terrain-grid/v123-atlas.js');
const source=require('../terrain-grid/octagon-1-v121.manifest.json');
let passed=0;
function check(name,fn){fn();passed++;console.log('PASS '+name);}
const tile={id:'pilot',origin:[100,200],width:1536,height:1024,corner:256,
 roads:{village:[[400,400],[500,400],[600,400],[700,400]]},
 blockedRoadSegments:{village:[1]}};
const network=buildNetwork({tiles:[tile],links:[]});
check('Tapping an open edge chooses a real traversable graph node',()=>{
 const h=hitTest(network,[550,600],20);
 assert.equal(h.kind,'open');assert(network.graph.has(h.key));
});
check('A closed segment takes priority even beside an open edge',()=>{
 const h=hitTest(network,[605,600],20);
 assert.equal(h.kind,'blocked');assert.equal(h.segment,1);
});
check('Tapping empty terrain or invalid coordinates never chooses a road',()=>{
 for(const [p,r] of [[[1200,1200],20],[[NaN,2],20],[[500,600],-1],[[500],20]])
  assert.equal(hitTest(network,p,r).kind,'none');
});
check('Raw village suspect area is blocked in the actual V123 atlas',()=>{
 const scene=atlas.create(source.movement.roads,{experimentalSeams:true});
 const h=hitTest(scene.network,[1536+1049,208.5],22);
 assert.equal(h.kind,'blocked');assert.equal(h.tile,'matrei');
 assert.equal(h.road,'village');assert.equal(h.segment,12);
 const far=hitTest(scene.network,[1536+1073.5,151],22);
 assert.equal(far.kind,'blocked');
 assert([14,15].includes(far.segment));
});
check('Bridge and reviewed lower road remain selectable',()=>{
 const scene=atlas.create(source.movement.roads,{experimentalSeams:true});
 for(const p of [[1536+813,486],[1536+1150,568]]){
  const h=hitTest(scene.network,p,18);
  assert.equal(h.kind,'open');assert(scene.network.graph.has(h.key));
 }
});
check('Closures do not rewrite coordinates or enable production seams',()=>{
 assert.deepEqual(tile.roads.village,[[400,400],[500,400],[600,400],[700,400]]);
 const scene=atlas.create(source.movement.roads);
 assert.equal(scene.productionApproved,false);
 assert(scene.network.seams.every(s=>!s.pass));
 assert.equal(hitTest(scene.network,[1536+1049,208.5],22).kind,'blocked');
});
console.log(JSON.stringify({version:131,passed,failed:0,roadSurfaceRepaired:false,productionApproved:false}));
