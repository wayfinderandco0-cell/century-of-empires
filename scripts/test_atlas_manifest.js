/* Reusable atlas/route manifest regression. No production gameplay modifications. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const root=path.resolve(__dirname,".."),m=JSON.parse(fs.readFileSync(path.join(root,"terrain-grid/atlas-cells.json"),"utf8"));
const V123=require("../terrain-grid/v123-atlas.js"),V122=require("../terrain-grid/v122-seam-engine.js");
assert.equal(m.cells.length,3);assert.equal(m.schema,"coe-atlas-cells/v1");
assert.deepEqual(m.cells.map(c=>c.origin),[[0,0],[1536,0],[1536,1024]]);
assert(m.cells.every(c=>c.strategicNodes.length===0&&c.provinceIds.length===0));
assert(m.decorativeInlays.every(i=>i.playable===false&&i.roads.length===0));
for(const c of m.cells){assert.equal(c.artMethodApproved,true);assert.equal(c.geoVerified,false);assert(fs.existsSync(path.join(root,c.art)),c.art);}
const atlas=V123.create(m.centerRoads,{experimentalSeams:true});
assert.equal(atlas.network.graph.size,100);
assert.equal(new Set([...atlas.network.graph.values()].map(n=>n.world.join(","))).size,98);
assert(atlas.network.seams.every(s=>s.pass&&s.endpointGapPx===0));
const ends=V123.endpoints(atlas);
const pathWestSouth=atlas.network.planRoute(ends.west,ends.south);
assert(pathWestSouth&&pathWestSouth.seams===2&&pathWestSouth.positions.length>35);
assert(pathWestSouth.positions.some(p=>p[0]===1536&&p[1]===478));
assert(pathWestSouth.positions.some(p=>p[0]===2002&&p[1]===1024));
assert.deepEqual(pathWestSouth.positions.at(-1),[2806,1629]);
assert.equal(V122.sharedSideLength(atlas.tiles[0],atlas.tiles[1])>0,true);
assert.equal(V122.sharedSideLength(atlas.tiles[1],atlas.tiles[2])>0,true);
console.log("PASS 3 art cells, 100 V123 nodes / 98 unique positions, 2 fixed zero-gap seams, WEST→SOUTH path, scenic/province separation");
