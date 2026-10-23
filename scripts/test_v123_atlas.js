#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const api=require('../terrain-grid/v123-atlas.js');
const {buildNetwork}=require('../terrain-grid/v122-seam-engine.js');
const base=fs.readFileSync(require('node:path').join(__dirname,'../v121-octagon-1-painted-road.html'),'utf8');
const found=base.match(/const ROADS=(\{[^\r\n]+\});/);
assert(found,'Unable to recover exact V121 source-defined route graph');
const roads=JSON.parse(found[1]);
const draft=api.create(roads);
assert.equal(draft.productionApproved,false);
assert(draft.network.seams.every(s=>!s.pass),'Unapproved art must fail closed');
assert.equal(draft.network.planRoute(api.endpoints(draft).west,api.endpoints(draft).south),null,'Cannot travel while art is unapproved');
const atlas=api.create(roads,{experimentalSeams:true});
const ends=api.endpoints(atlas);
assert.equal(atlas.network.seams.length,2);
assert(atlas.network.seams.every(s=>s.pass),JSON.stringify(atlas.network.seams));
const route=atlas.network.planRoute(ends.west,ends.south);
assert(route,'Expect west-to-south route through Matrei');
assert.equal(route.seams,2);
const route2=atlas.network.planRoute(ends.south,ends.bridge);
assert(route2&&route2.seams===1);
assert(route.positions.some(p=>p[0]===1536&&p[1]===478),'No west cut-through');
assert(route.positions.some(p=>p[0]===2002&&p[1]===1024),'No south cut-through');
assert(route.positions.every(p=>Number.isFinite(p[0])&&Number.isFinite(p[1])));
const p=atlas.network.graph;
for(let i=1;i<route.keys.length;i++){
 const a=p.get(route.keys[i-1]),b=p.get(route.keys[i]);
 assert(a.edges.some(e=>e.to===route.keys[i]),'Non-graph route step');
 assert(Math.hypot(a.world[0]-b.world[0],a.world[1]-b.world[1])<200,'Unpainted large jump');
}
let bad=api.create(roads,{experimentalSeams:true});
bad.tiles[1].roads.west.shift();
assert(buildNetwork(bad).seams.some(s=>s.errors.includes('from_road_ends_inside_tile')),'Off-edge road must be rejected');
bad=api.create(roads,{experimentalSeams:true});bad.tiles[2].origin[0]+=12;
assert(buildNetwork(bad).seams.some(s=>s.errors.includes('world_seam_gap')),'Drifted neighbor rejected');
bad=api.create(roads,{experimentalSeams:true});bad.links[1].bothRoadsVisuallyVerified=false;
assert(buildNetwork(bad).seams.some(s=>s.errors.includes('source_art_not_approved')),'Uninspected painting rejected');
const summary={version:123,connectedEngineeringLinks:2,westToSouthSeams:route.seams,
 roadGraphSteps:route.keys.length,productionApproved:atlas.productionApproved,
 photoApproval:atlas.physicalIPhoneApproved,safeDraftLinks:draft.network.seams.filter(x=>x.pass).length};
console.log(JSON.stringify(summary,null,2));