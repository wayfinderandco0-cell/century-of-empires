#!/usr/bin/env node
/* Terrain movement must not be inferred from image adjacency or V123 road nodes. */
"use strict";
const fs=require("node:fs"),assert=require("node:assert/strict");
const planner=require("../terrain-grid/atlas-overland.js");
const manifest=JSON.parse(fs.readFileSync("terrain-grid/atlas-cells.json","utf8"));
const contract=JSON.parse(fs.readFileSync("terrain-grid/atlas-overland-links.json","utf8"));
const link=contract.links.find(x=>x.id==="south-c03-overland");
assert(link&&link.mode==="overland"&&link.strategicRoad===false&&link.historicallyVerified===false);
assert.deepEqual(link.waypoints,[[2806,1629],[3072,1629],[3840,1536]]);
assert.equal(contract.surfaceMasks.south,undefined);
const real=planner.inspect(link,manifest,contract.surfaceMasks);
assert.equal(real.passable,false);
assert(real.reasons.includes("uncertified_cross_tile_seam"));
assert(real.reasons.includes("missing_surface_mask:south"));
assert(real.reasons.includes("missing_surface_mask:countryside-03"));
assert.deepEqual(real.points,[]);
assert.equal(real.cost,null);
const source=manifest.cells.find(c=>c.id==="south");
const dest=manifest.artCandidates.find(c=>c.id==="countryside-03");
function syntheticMask(art){
 return {sourceArt:art,reviewed:true,evidence:"SYNTHETIC UNIT TEST ONLY",
  cellSize:64,columns:24,rows:16,classes:Array(384).fill("meadow")};
}
const masks={south:syntheticMask(source.art),"countryside-03":syntheticMask(dest.art)};
const synthetic={...link,seamVerified:true,seamEvidence:"SYNTHETIC UNIT TEST ONLY"};
const pass=planner.inspect(synthetic,manifest,masks);
assert.equal(pass.passable,true,JSON.stringify(pass));
assert(pass.cost>1000&&pass.cost<1100,pass.cost);
assert.deepEqual(pass.points,link.waypoints);
assert.equal(pass.strategicRoad,false);
masks["countryside-03"].classes[9*24+0]="river";
const water=planner.inspect(synthetic,manifest,masks);
assert.equal(water.passable,false);
assert(water.reasons.some(r=>r.includes("impassable_or_unknown_terrain:countryside-03:river")));
assert.deepEqual(water.points,[]);
masks["countryside-03"].classes[9*24+0]="unknown";
assert.equal(planner.inspect(synthetic,manifest,masks).passable,false);
masks["countryside-03"].classes[9*24+0]="meadow";
masks["countryside-03"].reviewed=false;
assert(planner.inspect(synthetic,manifest,masks).reasons.includes("uncertified_surface_mask:countryside-03"));
masks["countryside-03"].reviewed=true;
assert(planner.inspect({...synthetic,waypoints:[[2806,1629],[3073,1629],[3840,1536]]},manifest,masks)
 .reasons.includes("invalid_shared_edge_geometry"));
assert.equal(manifest.artCandidates.filter(c=>c.userApproval===true).length,0);
console.log("PASS: actual SOUTH/C03 overland blocked; synthetic land cost, water, unknown, evidence and edge gates tested");
