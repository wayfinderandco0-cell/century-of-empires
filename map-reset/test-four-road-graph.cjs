/* node map-reset/test-four-road-graph.cjs
 * Independent QA for the draft fourth-section extension.
 * Does NOT approve its artwork or alter the three-section baseline.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path");
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,"approved-four-review.json"),"utf8"));
const original=JSON.parse(fs.readFileSync(path.join(__dirname,"approved-three.json"),"utf8"));
const roads=require("./road-engine.js");
assert.equal(original.tileArt.length,3);
assert.equal(manifest.tileArt.length,4);
for(let i=0;i<3;i++){
  assert.equal(manifest.tileArt[i].id,original.tileArt[i].id);
  assert.deepEqual(manifest.tileArt[i].origin,original.tileArt[i].origin);
  assert.equal(manifest.tileArt[i].image,original.tileArt[i].image);
  const baseline=original.tileArt[i].roads;
  for(const [name,poly] of Object.entries(baseline))
    assert.deepEqual(manifest.tileArt[i].roads[name],poly,"Original geometry modified: "+name);
}
const g=roads.build(manifest);
assert.equal(g.verify.connected,true);
assert.equal(g.verify.roadCount,10);
assert.equal(g.verify.nodeCount,112);
assert.equal(g.verify.segmentCount,111);
const west=[275,550], south=[2806,1629], east=[4502,1526], border=[3072,1629];
for(const [a,b] of [[west,south],[west,east],[south,east],[border,east]]){
  const trip=g.route(a,b,1);
  assert(trip && trip.points.length>=2, "Missing movement route: "+JSON.stringify([a,b]));
  assert.deepEqual(trip.points[0],a);
  assert.deepEqual(trip.points.at(-1),b);
}
for(const s of g.segments){
  const midpoint=[(s.pa[0]+s.pb[0])/2,(s.pa[1]+s.pb[1])/2];
  assert(g.route(west,midpoint,1),"Segment not available to army: "+s.id);
}
assert(g.route(west,[3072+810,1024+556],110),"Off-node click on east cartway must route");
const broken=structuredClone(manifest);
broken.tileArt[3].roads.west[0][1]+=1;
assert.throws(()=>roads.build(broken),/Disconnected visible roads/);
console.log("PASS: four sections, "+g.verify.roadCount+" roads, "+g.verify.nodeCount+
            " graph vertices, "+g.verify.segmentCount+" reachable road segments;"+
            " original three unchanged; east border and march validated.");
