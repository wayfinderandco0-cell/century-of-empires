#!/usr/bin/env node
/* No external dependencies. Guarantees off-road shortcuts are never auto-stitched. */
'use strict';
const assert=require('node:assert/strict');
const {buildNetwork,validateSeam,octagon,boundaryDistance}=require('../terrain-grid/v122-seam-engine.js');
const existing=require('../terrain-grid/octagon-1-v121.manifest.json');
const planned=require('../terrain-grid/octagon-network-v122.json');
const W=1536,H=1024;
assert.equal(octagon(W,H).length,8);
assert.equal(boundaryDistance([0,478],octagon(W,H)),0);
assert.equal(boundaryDistance([466,1024],octagon(W,H)),0);
function fixture(){
 return {
  tiles:[
   {id:'matrei',origin:[1536,0],width:W,height:H,artReviewed:true,roads:{
    west:[[0,450],[300,450],[500,450]],
    south:[[500,450],[500,700],[500,1024]]
   }},
   {id:'western_neighbor',origin:[0,0],width:W,height:H,artReviewed:true,roads:{
    east:[[1536,450],[1400,450]]
   }},
   {id:'southern_neighbor',origin:[1536,1024],width:W,height:H,artReviewed:true,roads:{
    north:[[500,0],[500,220]]
   }}
  ],
  links:[
   {id:'matrei-west',from:{tile:'matrei',road:'west',end:'start'},
    to:{tile:'western_neighbor',road:'east',end:'start'},bothRoadsVisuallyVerified:true,enabled:true},
   {id:'matrei-south',from:{tile:'matrei',road:'south',end:'end'},
    to:{tile:'southern_neighbor',road:'north',end:'start'},bothRoadsVisuallyVerified:true,enabled:true}
  ]
 };
}
const ok=fixture(),network=buildNetwork(ok);
assert(network.seams.every(s=>s.pass),JSON.stringify(network.seams));
const route=network.planRoute(network.key('western_neighbor',[1400,450]),network.key('southern_neighbor',[500,220]));
assert(route,'Three-cell test path must exist');
assert.equal(route.seams,2,'Cross exactly the two approved shared borders');
assert(route.positions.some(p=>p[0]===1536&&p[1]===450));
assert(route.positions.some(p=>p[0]===2036&&p[1]===1024));
assert(route.positions.every(p=>p.every(Number.isFinite)));
const short=fixture();short.tiles[0].roads.west[0]=[99,450];
assert(buildNetwork(short).seams[0].errors.includes('from_road_ends_inside_tile'));
assert.equal(buildNetwork(short).planRoute(
 buildNetwork(short).key('western_neighbor',[1400,450]),
 buildNetwork(short).key('southern_neighbor',[500,220])
),null,'Never route across a painted-road gap');
const shifted=fixture();shifted.tiles[1].origin=[0,20];
assert(buildNetwork(shifted).seams[0].errors.includes('world_seam_gap'));
const unreviewed=fixture();unreviewed.tiles[0].artReviewed=false;
assert(buildNetwork(unreviewed).seams[0].errors.includes('source_art_not_approved'));
const notEnabled=fixture();notEnabled.links[0].enabled=false;
assert(buildNetwork(notEnabled).seams[0].errors.includes('join_not_enabled'));
const missing=fixture();delete missing.tiles[1].roads.east;
assert(buildNetwork(missing).seams[0].errors.includes('missing_road_or_endpoint'));
// The actual currently published art is NOT ready for connecting neighboring
// tiles: check real V121 data rather than a generic toy model.
const actual=fixture();
actual.tiles[0].roads=existing.movement.roads;
actual.tiles[0].artReviewed=false;
actual.tiles[1].artReviewed=false;
actual.tiles[2].artReviewed=false;
actual.links=planned.links;
const actualCheck=buildNetwork(actual);
assert(actualCheck.seams.every(s=>!s.pass));
assert(actualCheck.seams[0].errors.includes('from_road_ends_inside_tile'));
assert(actualCheck.seams[1].errors.includes('from_road_ends_inside_tile'));
assert(actualCheck.seams[0].sourceInsetPx>90);
assert(actualCheck.seams[1].sourceInsetPx>60);
assert.equal(actualCheck.planRoute(
 actualCheck.key('western_neighbor',[1400,450]),
 actualCheck.key('matrei',existing.movement.roads.bridge.at(-1))
),null,'Current draft never pretends neighbor tiles are passable');
const summary={success:true,syntheticThreeTileCrossings:route.seams,
 v121RealRoadsReachBorder:false,liveCrossingsEnabled:actualCheck.seams.filter(s=>s.pass).length,
 currentSeamStatus:actualCheck.seams.map(s=>({
  name:s.id,insetPx:Number(s.sourceInsetPx.toFixed(1)),issues:s.errors
 }))};
console.log(JSON.stringify(summary,null,2));
