#!/usr/bin/env node
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const baseDir=path.resolve(__dirname,"..");
const V123=require("../terrain-grid/v123-atlas.js");
const seam=require("../terrain-grid/v122-seam-engine.js");
const east=require("../terrain-grid/v267-east-extension.js");
const manifest=JSON.parse(fs.readFileSync(path.join(baseDir,"terrain-grid/atlas-cells.json"),"utf8"));
const base=V123.create(manifest.centerRoads,{experimentalSeams:true});
const snapshot=JSON.stringify({tiles:base.tiles,links:base.links});
assert.equal(base.network.graph.size,100);
assert.equal(base.network.seams.filter(s=>s.pass).length,2);
const proposal=east.candidate(base);
assert.equal(JSON.stringify({tiles:base.tiles,links:base.links}),snapshot,"V123 source mutated");
assert.equal(proposal.tiles.length,4);
assert.equal(proposal.links.length,3);
const eastCheck=proposal.network.seams.find(s=>s.id==="matrei-east-01-candidate");
assert.equal(eastCheck.pass,false);
assert.equal(eastCheck.endpointGapPx,0);
assert(eastCheck.errors.includes("source_art_not_approved"));
assert(eastCheck.errors.includes("join_not_enabled"));
const origin=proposal.network.key("matrei",[518,519]);
// The additive graph must follow exactly the road centerline painted by V8.
const evidence=JSON.parse(fs.readFileSync(path.join(baseDir,"terrain-grid/v267-original-art-batch-01/matrei-east-v8-narrow-dirt-evidence.json"),"utf8"));
const painted=evidence.roadWorldPoints;
const matreiRoad=proposal.tiles.find(t=>t.id==="matrei").roads.southeast;
const eastRoad=proposal.tiles.find(t=>t.id==="east-01").roads.west;
assert.deepEqual(matreiRoad.slice(-3),painted.slice(0,3));
assert.deepEqual(eastRoad.map(p=>[p[0]+1536,p[1]]),painted.slice(2));
assert.deepEqual(painted[2],[1536,749]);
const target=proposal.network.key("east-01",[714,559]);
assert.equal(proposal.network.planRoute(origin,target),null,"unapproved east route traversable");
// Synthetic validator fixture only: tests that the proposed endpoints can join
// IF future original art, physical seam, and both cartways are approved.
// This must NEVER set the real manifest's status to approved.
const tiles=JSON.parse(JSON.stringify(proposal.tiles));
const links=JSON.parse(JSON.stringify(proposal.links));
tiles.find(t=>t.id==="east-01").artReviewed=true;
const link=links.find(l=>l.id==="matrei-east-01-candidate");
link.bothRoadsVisuallyVerified=true;link.enabled=true;
const simulated=seam.buildNetwork({tiles,links});
assert.equal(simulated.seams.filter(s=>s.pass).length,3);
const route=simulated.planRoute(simulated.key("matrei",[518,519]),simulated.key("east-01",[714,559]));
assert(route&&route.seams===1&&route.distance>0);
assert.equal(proposal.nativePlayable,false);
console.log(JSON.stringify({result:"PASS",baseNodes:100,baseSeams:2,
  candidateEndpointGap:0,candidateEnabled:false,
  candidateTraversable:false,artRouteCenterlineExact:true,syntheticValidatorRoute:"PASS",
  physicalSeamVerified:false,newPlayable:0}));
