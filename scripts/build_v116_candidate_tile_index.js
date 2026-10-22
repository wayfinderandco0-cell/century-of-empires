/* Deterministic coverage of repaired candidate graph across V115 image tiles.
 * Run: node scripts/build_v116_candidate_tile_index.js
 * Never grants production terrain or conquest permissions.
 */
"use strict";
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const old=require("../terrain-grid/v115-local-tiles-v116.json");
const source=require("../terrain-grid/v115-route-provenance.json");
const correction=require("../terrain-grid/v116-bridge-painted-candidate.json");
const road=require("./v116_road_graph.js");
const {buildSafe}=require("./v116_candidate_graph_guard.js");
const trace=require("./v116_route_tile_trace.js");
function hit(a,b,r){
 const dx=b[0]-a[0],dy=b[1]-a[1];let lo=0,hi=1;
 for(const [p,q] of [[-dx,a[0]-r[0]],[dx,r[2]-a[0]],[-dy,a[1]-r[1]],[dy,r[3]-a[1]]]){
   if(p===0){if(q<0)return false;continue;}
   const t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);
   if(lo>hi)return false;
 }
 return true;
}
// Match army/tile seam tracing's half-open ownership. A corner touch
// or a line exactly on a boundary must not create phantom corridor tiles.
function coveredTiles(points,tiles,index=old){
 if(!index||index.tiles!==tiles)throw Error("Candidate coverage requires the same validated tile index");
 return trace.traceRoute(index,points).visitedTileIds;
}
function makeIndex({localTiles=old,routeSource=source,bridgeCandidate=correction}={}){
 const g=buildSafe(routeSource,bridgeCandidate,road);
 const coverage={south:coveredTiles(g.paths.south,localTiles.tiles,localTiles),
                 bridge:coveredTiles(g.paths.bridge,localTiles.tiles,localTiles)};
 const result={...localTiles,
    routeCandidateTileIds:coverage,
    routeSourceVersion:{
      kind:"visually_traced_candidate_not_geographic_authority",
      input:"terrain-grid/v116-bridge-painted-candidate.json",
      originalIndex:"terrain-grid/v115-local-tiles-v116.json",
      bridgeTerminal:"visible-far-bank-only",
      routeGraph:"scripts/v116_road_graph.js",
      productionAccess:false
    },
    verification:{...localTiles.verification,roadPixelsAligned:false,bridgeCrossing:false,
                  farBankContinuation:false,playableRouteTiles:0,conquerableTiles:0},
    tiles:localTiles.tiles.map(t=>({...t,
      prototypeRouteCandidates:["south","bridge"].filter(name=>coverage[name].includes(t.id)),
      paintedRoadVerified:false,traversable:false,conquerable:false,deepZoomEligible:false}))
 };
 return result;
}
if(require.main===module){
 const output=path.join(root,"terrain-grid/v116-candidate-route-tiles.json");
 fs.writeFileSync(output,JSON.stringify(makeIndex(),null,2)+"\n");
 console.log("Wrote",output);
}
module.exports={makeIndex,hit,coveredTiles};
