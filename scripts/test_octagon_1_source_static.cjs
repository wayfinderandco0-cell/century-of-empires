#!/usr/bin/env node
"use strict";
// Fast source/geometry safety gate. NOT an artwork or historical-road approval.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const crypto=require("node:crypto");
const root=require("node:path").resolve(__dirname,"..");
const read=p=>fs.readFileSync(require("node:path").join(root,p));
const html=read("octagon-1-road-authoring.html").toString("utf8");
const jpg=read("terrain-grid/octagon-1-v119-source.jpg");
assert.equal(jpg.length,591185,"Original source must be byte-for-byte preserved");
assert.equal(jpg[0],0xff);assert.equal(jpg[1],0xd8);
assert.equal(jpg.at(-2),0xff);assert.equal(jpg.at(-1),0xd9);
const gitBlob=crypto.createHash("sha1").update(Buffer.from("blob "+jpg.length+"\\0")).update(jpg).digest("hex");
assert.equal(gitBlob,"96c5eeee5afafa20c5442da42c9a1caedd4b00ad","Source identity changed");
assert.ok(html.includes('const IMAGE="./terrain-grid/octagon-1-v119-source.jpg"'),"Image must load externally");
assert.ok(!html.includes("data:image/jpeg;base64,"),"No duplicated inline source image");
assert.ok(html.includes('id="raw"') && html.includes("if(showInk){"),"Raw-source comparison view missing");
assert.ok(html.includes('get sourceLabelStillBaked(){return true}'),"Baked-label issue must remain disclosed");
function points(name){
 const match=html.match(new RegExp("const\\s+"+name+"=(\\\\[\\\\[.*?\\\\]\\\\])\\s*;"));
 if(!match)throw Error("Missing "+name+" route geometry");
 return JSON.parse(match[1]);
}
const approach=points("APPROACH"),east=points("BASE_EAST"),south=points("SOUTH");
assert.deepEqual(approach.at(-1),[699,799],"Bridge end must not move");
assert.deepEqual(east.at(-1),[1100,704],"Unapproved east exit must stay fixed");
assert.deepEqual(south.at(-1),[315,842],"South route must remain separate");
assert.deepEqual(south.slice(0,37),approach.slice(0,37),"Shared village fork changed");
assert.ok(east.every((p,i)=>i===0||p[0]>east[i-1][0]),"East route backtracks");
assert.ok(html.includes("data.connectionGate=gate?gate.authoringExportStatus(data,null)"),"Safety gate not attached");
assert.ok(html.includes("approvedForProduction:false"),"Candidate must never be marked approved");
const gate=require("./octagon_1_corridor_gate.js");
const candidate={
 kind:"octagon-1-art-authored-candidate",schemaVersion:1,
 eastEdge:[1100,704],neighborEntry:[0,704],approvedForProduction:false
};
const proof=gate.authoringExportStatus(candidate,null);
assert.equal(proof.traversable,false);
assert.ok(proof.reasons.includes("authoring_export_requires_independent_approval"));
console.log("PASS: original source JPEG, bridge/fork geometry, raw-art view, and blocked candidate exports");
