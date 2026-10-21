/* Run: node --test tests/test_v116_route_tile_coverage.js */
"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {makeIndex}=require("../scripts/build_v116_candidate_tile_index.js");
const renderer=require("../scripts/v116_local_art_renderer.js");
const old=require("../terrain-grid/v115-local-tiles-v116.json");
const j=JSON.parse(fs.readFileSync(path.join(__dirname,"../terrain-grid/v116-candidate-route-tiles.json"),"utf8"));
test("revised coverage generated deterministically from actual centerline",()=>{
 assert.deepEqual(j,makeIndex());
 assert.equal(j.tiles.length,48);
 assert.deepEqual(j.parentOctagonCandidates,["r10-c09"]);
});
test("graph re-route removes original false-positive bridge tile",()=>{
 assert(old.routeCandidateTileIds.bridge.includes("local-r05-c02"));
 assert(!j.routeCandidateTileIds.bridge.includes("local-r05-c02"));
 assert.equal(j.routeCandidateTileIds.bridge.length,9);
});
test("old geometry and image world transforms unchanged",()=>{
 assert.deepEqual(j.artBoxWorldPx,old.artBoxWorldPx);
 assert.deepEqual(j.artSizePx,old.artSizePx);
 for(let k=0;k<48;k++) {
   assert.deepEqual(j.tiles[k].worldRectPx,old.tiles[k].worldRectPx);
   assert.deepEqual(j.tiles[k].imageCropPx,old.tiles[k].imageCropPx);
 }
 renderer.validate(j);
});
test("no tile falsely declared road-verified, passable or conquerable",()=>{
 assert.equal(j.routeSourceVersion.productionAccess,false);
 assert(j.tiles.every(t=>!t.traversable&&!t.conquerable&&!t.deepZoomEligible&&!t.paintedRoadVerified));
 assert.equal(j.verification.playableRouteTiles,0);
});
