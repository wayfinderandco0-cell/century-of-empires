/* Node preflight: no gallery artwork may be counted as playable.
 * Also verifies the proposed SOUTH-east road is geometrically paired
 * but blocked until real painted-road and mobile QA approval.
 */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const V123=require("../terrain-grid/v123-atlas.js");
const ledger=require("../terrain-grid/atlas-playability.js");
const gate=require("../terrain-grid/v267-southeast-route-gate.js");
const manifest=JSON.parse(fs.readFileSync("terrain-grid/atlas-cells.json","utf8"));
const base=V123.create(manifest.centerRoads,{experimentalSeams:true});
const status=ledger.audit(base,manifest);
assert.deepEqual(status.playableIds,["matrei","south","west"]);
assert.equal(status.baselinePlayable,3);
assert.equal(status.connectedNew.length,0);
assert.deepEqual(status.displayOnlyCandidateIds,[
 "countryside-03","countryside-04","countryside-05","countryside-06"
]);
assert.equal(status.finishedIds.length,0);
assert.equal(status.label,"3 PLAYABLE · 4 ART-ONLY · 0 NEW FINISHED");
const proposed=gate.candidate(base);
assert.equal(proposed.nativePlayable,false);
assert.equal(proposed.network.seams.length,3);
const seam=proposed.network.seams.find(s=>s.id==="south-southeast-provisional");
assert.equal(seam.endpointGapPx,0);
assert.equal(seam.pass,false);
assert.deepEqual(seam.errors.sort(),["join_not_enabled","source_art_not_approved"]);
assert.equal(ledger.audit(proposed,manifest).connectedNew.length,0);
assert.equal(ledger.audit(proposed,manifest).blockedSeams.length,1);
const originalSouth=base.tiles.find(t=>t.id==="south");
assert.deepEqual(originalSouth.roads.north.at(-1),[1270,605]);
assert.equal(Object.hasOwn(originalSouth.roads,"eastCandidate"),false);
assert.equal(base.tiles.length,3);
assert.equal(base.network.graph.size,100);
console.log("PASS: exactly 3 playable; 4 display-only; SOUTH east geometry paired but NOT traversable");
