#!/usr/bin/env node
'use strict';
// V125 regression: a nearby octagon boundary is not necessarily a SHARED side.
// Synthetic roads here are geometry fixtures, never sourced playable corridors.
const assert=require('node:assert/strict');
const {buildNetwork,sharedSideLength,sharedBorderSegments}=require('../terrain-grid/v122-seam-engine.js');
const atlas=require('../terrain-grid/v123-atlas.js');
const source=require('../terrain-grid/octagon-1-v121.manifest.json');
let passed=0;
function check(name,fn){fn();passed++;console.log('PASS '+name);}
function fixture(){
 return {
  tiles:[
   {id:'matrei',origin:[1536,0],width:1536,height:1024,corner:256,artReviewed:true,
    roads:{west:[[0,478],[300,450]]}},
   {id:'west',origin:[0,0],width:1536,height:1024,corner:256,artReviewed:true,
    roads:{east:[[1536,478],[1400,450]]}}
  ],
  links:[{id:'west-matrei',from:{tile:'matrei',road:'west',end:'start'},
   to:{tile:'west',road:'east',end:'start'},bothRoadsVisuallyVerified:true,enabled:true}]
 };
}
function route(plan){
 const network=buildNetwork(plan);
 return network.planRoute(network.key('west',plan.tiles[1].roads.east.at(-1)),
                          network.key('matrei',plan.tiles[0].roads.west.at(-1)));
}
check('Real shared west border and coincident endpoints pass',()=>{
 const f=fixture(),network=buildNetwork(f);
 assert.equal(sharedBorderSegments(...f.tiles).length,1);
 assert(sharedSideLength(...f.tiles)>400);
 assert.equal(network.seams[0].pass,true);
 assert.equal(route(f).seams,1);
});
check('Endpoints on adjacent diagonal edges near a common corner do NOT join',()=>{
 const f=fixture();
 f.tiles[0].roads.west[0]=[0.5,255.5];
 f.tiles[1].roads.east[0]=[1535.5,255.5];
 const seam=buildNetwork(f).seams[0];
 assert(seam.endpointGapPx<=1.5);
 assert.equal(seam.sourceInsetPx,0);
 assert.equal(seam.targetInsetPx,0);
 assert(seam.errors.includes('endpoint_not_on_shared_border'),JSON.stringify(seam));
 assert.equal(route(f),null);
});
check('One-pixel overlapping tile origins are not a shared border',()=>{
 const f=fixture();f.tiles[1].origin=[1,0];
 const seam=buildNetwork(f).seams[0];
 assert(seam.endpointGapPx<=1.5);
 assert.equal(sharedSideLength(...f.tiles),0);
 assert(seam.errors.includes('no_shared_octagon_side'),JSON.stringify(seam));
 assert.equal(route(f),null);
});
check('One-pixel gap between neighboring tile footprints fails closed',()=>{
 const f=fixture();f.tiles[1].origin=[-1,0];
 const seam=buildNetwork(f).seams[0];
 assert(seam.endpointGapPx<=1.5);
 assert(seam.errors.includes('no_shared_octagon_side'),JSON.stringify(seam));
 assert.equal(route(f),null);
});
check('Diagonal corner contact alone does not create a side',()=>{
 const f=fixture();f.tiles[1].origin=[0,1024];
 assert.equal(sharedBorderSegments(...f.tiles).length,0);
 assert.equal(sharedSideLength(...f.tiles),0);
 assert(buildNetwork(f).seams[0].errors.includes('no_shared_octagon_side'));
});
check('Disabled or unreviewed artwork still blocks otherwise valid seam',()=>{
 const f=fixture();f.links[0].enabled=false;
 assert(buildNetwork(f).seams[0].errors.includes('join_not_enabled'));
 f.links[0].enabled=true;f.tiles[1].artReviewed=false;
 assert(buildNetwork(f).seams[0].errors.includes('source_art_not_approved'));
});
check('V123 production mode remains closed; engineering preview still connects',()=>{
 const draft=atlas.create(source.movement.roads);
 assert(draft.network.seams.every(s=>!s.pass));
 const experiment=atlas.create(source.movement.roads,{experimentalSeams:true});
 assert(experiment.network.seams.every(s=>s.pass));
 assert.equal(experiment.productionApproved,false);
 assert.equal(experiment.physicalIPhoneApproved,false);
});
console.log(JSON.stringify({version:125,passed,failed:0,productionApproved:false}));
