#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const base=require('../terrain-grid/v122-seam-engine.js');
const safe=require('../terrain-grid/v123-safe-seam-engine.js');
const W=1536,H=1024;
const tile=(id,origin,roads)=>({id,origin,width:W,height:H,corner:256,artReviewed:true,roads});
const link=(fromRoad,toRoad)=>({id:'test',from:{tile:'a',road:fromRoad,end:'start'},to:{tile:'b',road:toRoad,end:'start'},bothRoadsVisuallyVerified:true,enabled:true});
function pair(a,b,l){return {tiles:[a,b],links:[l]};}
const neighbor=pair(tile('a',[0,0],{east:[[W,450],[1300,450]]}),
 tile('b',[W,0],{west:[[0,450],[200,450]]}),link('east','west'));
assert.equal(safe.octagonInteriorsOverlap(...neighbor.tiles),false);
assert.equal(safe.buildNetwork(neighbor).seams[0].pass,true,'Actual shared side remains passable');
const stacked=pair(tile('a',[0,0],{east:[[W,450],[1300,450]]}),
 tile('b',[0,0],{west:[[W,450],[1300,450]]}),link('east','west'));
assert.equal(base.buildNetwork(stacked).seams[0].pass,true,'Fixture must expose original false seam');
assert.equal(safe.octagonInteriorsOverlap(...stacked.tiles),true);
const blocked=safe.buildNetwork(stacked);
assert.equal(blocked.seams[0].pass,false);
assert(blocked.seams[0].errors.includes('tile_interiors_overlap'));
assert.equal(blocked.planRoute(blocked.key('a',[1300,450]),blocked.key('b',[1300,450])),null);
const diagonal=pair(tile('a',[0,0],{southeast:[[1408,896],[1320,835]]}),
 tile('b',[W-256,H-256],{northwest:[[128,128],[210,210]]}),link('southeast','northwest'));
assert.equal(safe.octagonInteriorsOverlap(...diagonal.tiles),false,'Valid angled border is not overlap');
assert(safe.buildNetwork(diagonal).seams[0].pass,'Angled shared border still works');
console.log(JSON.stringify({pass:true,stackedRejected:true,sideAdjacentAccepted:true,diagonalAdjacentAccepted:true}));
