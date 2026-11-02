#!/usr/bin/env node
/* Synthetic passability tests are NOT certification of the real SOUTH/C03 art. */
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
for(const reason of ["uncertified_cross_tile_seam","missing_surface_mask:south","missing_surface_mask:countryside-03"])
 assert(real.reasons.includes(reason),JSON.stringify(real.reasons));
assert.deepEqual(real.points,[]);
assert.equal(real.cost,null);
const from=manifest.cells.find(c=>c.id==="south"),to=manifest.artCandidates.find(c=>c.id==="countryside-03");
const shas=Object.fromEntries(link.sourceImages.map(s=>[s.cell,s.gitBlobSha]));
const evidence={sourcePixelReview:true,evidencePath:"SYNTHETIC-TEST-NOT-REAL-REVIEW",reviewer:"automated-test",reviewedOn:"2026-11-01"};
function mask(c){
 return {sourceArt:c.art,sourceBlobSha:shas[c.id],reviewed:true,evidence,
  cellSize:32,columns:48,rows:32,classes:Array(48*32).fill("meadow")};
}
const masks={south:mask(from),"countryside-03":mask(to)};
const synthetic={...link,seamVerified:true,seamEvidence:{
 ...evidence,sourceBlobShas:shas,edgeY:1629,groundContinuity:true,noUnverifiedCrossing:true
}};
const inspect=(l=synthetic,m=masks)=>planner.inspect(l,manifest,m);
const pass=inspect();
assert.equal(pass.passable,true,JSON.stringify(pass));
assert(pass.cost>1000&&pass.cost<1100,pass.cost);
assert.equal(pass.clearanceRadiusPx,16);
assert.deepEqual(pass.points,link.waypoints);
assert.equal(pass.strategicRoad,false);
// Water exactly on the seam, even though the other tile is marked meadow.
masks["countryside-03"].classes[18*48+0]="river";
assert(inspect().reasons.some(r=>r.includes("impassable_or_unknown_terrain:countryside-03:river")));
masks["countryside-03"].classes[18*48+0]="meadow";
// Cliff off the centerline but inside the army's 16px clearance corridor.
masks["countryside-03"].classes[19*48+3]="cliff";
assert(inspect().reasons.some(r=>r.includes("impassable_or_unknown_terrain:countryside-03:cliff")));
masks["countryside-03"].classes[19*48+3]="meadow";
masks["countryside-03"].classes[18*48+0]="unknown";
assert.equal(inspect().passable,false);
masks["countryside-03"].classes[18*48+0]="meadow";
// Invalid/stale source evidence cannot certify a changed artwork.
masks["countryside-03"].sourceBlobSha="f".repeat(40);
assert(inspect().reasons.includes("uncertified_surface_mask:countryside-03"));
masks["countryside-03"].sourceBlobSha=shas["countryside-03"];
assert(inspect({...synthetic,seamEvidence:{...synthetic.seamEvidence,sourceBlobShas:{...shas,south:"f".repeat(40)}}})
 .reasons.includes("uncertified_cross_tile_seam"));
assert(inspect({...synthetic,sourceImages:[]}).reasons.includes("source_art_identity_mismatch"));
// A text string is not physical seam review evidence.
assert(inspect({...synthetic,seamEvidence:"synthetic review"}).reasons.includes("uncertified_cross_tile_seam"));
masks["countryside-03"].reviewed=false;
assert(inspect().reasons.includes("uncertified_surface_mask:countryside-03"));
masks["countryside-03"].reviewed=true;
masks["countryside-03"].cellSize=64;
assert(inspect().reasons.includes("uncertified_surface_mask:countryside-03"));
masks["countryside-03"].cellSize=32;
masks["countryside-03"].classes[0]="bog";
assert(inspect().reasons.includes("uncertified_surface_mask:countryside-03"));
masks["countryside-03"].classes[0]="meadow";
assert(inspect({...synthetic,waypoints:[[2806,1629],[3073,1629],[3840,1536]]})
 .reasons.includes("invalid_shared_edge_geometry"));
assert(inspect({...synthetic,strategicRoad:true}).reasons.includes("not_a_wilderness_link"));
assert(inspect({...synthetic,clearanceRadiusPx:0}).reasons.includes("invalid_clearance_radius"));
assert.equal(manifest.artCandidates.filter(c=>c.userApproval===true).length,0);
assert.equal(inspect().passable,true);
// Every cardinal neighbor must share a genuine octagon edge, never a diamond gap.
// These are synthetic meadow fixtures; they do NOT certify any real candidate.
for(const [direction,neighborOrigin,points] of [
 ["east",[3072,1024],[[2806,1629],[3072,1629],[3840,1536]]],
 ["west",[0,1024],[[1700,1629],[1536,1629],[768,1536]]],
 ["north",[1536,0],[[2200,1350],[2200,1024],[2200,500]]],
 ["south",[1536,2048],[[2200,1700],[2200,2048],[2200,2600]]]
]){
 const fixture=JSON.parse(JSON.stringify(manifest));
 fixture.cells=[{...from,id:"source",origin:[1536,1024],art:"fixture-source.webp"}];
 fixture.artCandidates=[{...to,id:"neighbor",nativeWorldOrigin:neighborOrigin,art:"fixture-neighbor.webp"}];
 const hashes={source:"a".repeat(40),neighbor:"b".repeat(40)};
 const src=[{cell:"source",path:"fixture-source.webp",gitBlobSha:hashes.source},
            {cell:"neighbor",path:"fixture-neighbor.webp",gitBlobSha:hashes.neighbor}];
 const mk=(art,sha)=>({sourceArt:art,sourceBlobSha:sha,reviewed:true,evidence,
   cellSize:32,columns:48,rows:32,classes:Array(48*32).fill("meadow")});
 const terrain={source:mk("fixture-source.webp",hashes.source),
                neighbor:mk("fixture-neighbor.webp",hashes.neighbor)};
 const testLink={...synthetic,from:"source",to:"neighbor",waypoints:points,sourceImages:src,
   seamEvidence:{...evidence,sourceBlobShas:hashes,edgeY:points[1][1],
                 groundContinuity:true,noUnverifiedCrossing:true}};
 const result=planner.inspect(testLink,fixture,terrain);
 assert.equal(result.passable,true,direction+":"+JSON.stringify(result));
 assert.equal(result.edgeDirection,direction);
 assert(result.cost>0);
 // An unpaired diagonal tile must never be traversable even with fake meadow masks.
 fixture.artCandidates[0].nativeWorldOrigin=[3072,2048];
 assert(planner.inspect(testLink,fixture,terrain).reasons.includes("invalid_shared_edge_geometry"));
}
console.log("PASS: real SOUTH/C03 blocked; source-bound masks, seam evidence, 16px army corridor, cliff/water, terrain cost and protected baseline tested");
