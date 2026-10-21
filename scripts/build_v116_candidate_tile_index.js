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
function hit(a,b,r){
 const dx=b[0]-a[0],dy=b[1]-a[1];let lo=0,hi=1;
 for(const [p,q] of [[-dx,a[0]-r[0]],[dx,r[2]-a[0]],[-dy,a[1]-r[1]],[dy,r[3]-a[1]]]){
   if(p===0){if(q<0)return false;continue;}
   const t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);
   if(lo>hi)return false;
 }
 return true;
}
function coveredTiles(points,tiles){
 const ids=[];
 for(const tile of tiles){
   const b=tile.imageCropPx;
   if(points.slice(1).some((p,i)=>hit(points[i],p,b)))ids.push(tile.id);
 }
 return ids.sort();
}
function makeIndex(){
 if(correction.sourceV115BlobSha!==source.source.githubBlobSha)
    throw Error("Source artwork does not match original V115");
 const g=road.build({south:source.rawPath,bridge:correction.bridgeCenterlineArtPx,
    forkIndex:source.forkIndex,imageSize:old.artSizePx});
 const coverage={south:coveredTiles(g.paths.south,old.tiles),
                 bridge:coveredTiles(g.paths.bridge,old.tiles)};
 const result={...old,
    routeCandidateTileIds:coverage,
    routeSourceVersion:{
      kind:"visually_traced_candidate_not_geographic_authority",
      input:"terrain-grid/v116-bridge-painted-candidate.json",
      originalIndex:"terrain-grid/v115-local-tiles-v116.json",
      bridgeTerminal:"visible-far-bank-only",
      routeGraph:"scripts/v116_road_graph.js",
      productionAccess:false
    },
    verification:{...old.verification,roadPixelsAligned:false,bridgeCrossing:false,
                  farBankContinuation:false,playableRouteTiles:0,conquerableTiles:0},
    tiles:old.tiles.map(t=>({...t,
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
