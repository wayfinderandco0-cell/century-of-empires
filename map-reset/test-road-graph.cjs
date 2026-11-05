/* node map-reset/test-road-graph.cjs — no external dependencies */
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path");
const doc=JSON.parse(fs.readFileSync(path.join(__dirname,"approved-three.json"),"utf8"));
const roads=require("./road-engine.js");
const g=roads.build(doc);
assert.equal(doc.tileArt.length,3);
assert.equal(g.verify.roadCount,8);
assert.equal(g.verify.nodeCount,98);
assert.equal(g.verify.connected,true);
assert.equal(g.verify.deadEnds,5);
const west=[275,550],south=[2806,1629],bridge=[1536+813,486],village=[1536+1137,112];
for(const [a,b] of [[west,south],[west,bridge],[west,village],[bridge,south]]){
 const route=g.route(a,b,1);assert(route&&route.length>0, "expected movement to use connected roads");
 assert.deepEqual(route.points[0],a);assert.deepEqual(route.points.at(-1),b);
}
for(const segment of g.segments){
 const p=[(segment.pa[0]+segment.pb[0])/2,(segment.pa[1]+segment.pb[1])/2];
 const trip=g.route(west,p,1);
 assert(trip&&trip.length>=0,"Every visible road segment must be reachable: "+segment.id);
 const nearest=g.nearest(p);assert(nearest.distance<.0001);
}
assert.equal(g.route(west,[10000,10000],25),null);
const extended=structuredClone(doc);
extended.tileArt.push({id:"new-sector",origin:[0,0],roads:{continuation:[[275,550],[175,552],[-100,600]]}});
const expanded=roads.build(extended);
assert(expanded.route(south,[-100,600],1),"New section must join original roads at exact exit");
const isolated=structuredClone(doc);
isolated.tileArt.push({id:"isolated",origin:[0,0],roads:{phantom:[[9999,9999],[10099,9999]]}});
assert.throws(()=>roads.build(isolated),/Disconnected visible roads/);
console.log("PASS: exact 3 approved sources; "+g.verify.roadCount+" roads, "+g.verify.nodeCount+" connected vertices, "+g.verify.segmentCount+" marchable segments; all mid-road destinations, border crossings, and expansion guard.");
