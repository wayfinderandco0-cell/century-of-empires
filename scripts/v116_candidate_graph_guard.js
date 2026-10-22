/* V116: fail-closed, immutable public view of a sourced road-graph candidate.
 * This is not historical verification or permission to cross the far bank.
 */
(function(root){
"use strict";
// Pin the known V115 art version and provisional terminal; a candidate JSON edit
// must not silently authorize a different source image or a new far-bank route.
const V115_BLOB="9a8f44120c2f220abf434bed384f230cf6483296";
const BRIDGE_TERMINAL=[699,799];
const PINNED_FORK_INDEX=36;
// Exact route snapshots are integrity gates, not geographic or historical proof.
// Deliberate geometry changes require explicit review and re-pinning.
const PINNED_SOUTH_PATH_JSON="[[616,0],[615,22],[613,45],[614,51],[610,77],[609,103],[597,129],[585,156],[581,182],[574,208],[570,234],[563,253],[554,274],[538,300],[519,326],[504,352],[494,379],[502,402],[511,421],[512,435],[504,447],[493,463],[485,477],[483,493],[485,507],[496,525],[508,541],[514,557],[513,565],[507,582],[495,600],[480,625],[467,650],[453,688],[447,706],[446,724],[437,742],[423,761],[403,780],[379,797],[352,815],[325,834],[315,842]]";
const PINNED_BRIDGE_PATH_JSON="[[616,0],[615,22],[613,45],[614,51],[610,77],[609,103],[597,129],[585,156],[581,182],[574,208],[570,234],[563,253],[554,274],[538,300],[519,326],[504,352],[494,379],[502,402],[511,421],[512,435],[504,447],[493,463],[485,477],[483,493],[485,507],[496,525],[508,541],[514,557],[513,565],[507,582],[495,600],[480,625],[467,650],[453,688],[447,706],[446,724],[437,742],[450,746],[466,749],[483,752],[500,757],[516,762],[531,766],[549,771],[570,775],[591,779],[613,783],[634,786],[656,789],[679,794],[699,799]]";

const freezeCopy=v=>Array.isArray(v)?Object.freeze(v.map(freezeCopy)):
  v&&typeof v==="object"?Object.freeze(Object.fromEntries(
    Object.entries(v).map(([k,x])=>[k,freezeCopy(x)]))):v;
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function buildSafe(source,candidate,roadApi){
  const api=roadApi||(typeof require==="function"?require("./v116_road_graph.js"):root.CenturyV116RoadGraph);
  if(!api||typeof api.build!=="function"||!source||!source.source||!source.sourceArt||
     source.source.repository!=="wayfinderandco0-cell/century-of-empires"||
     source.source.path!=="v115-town-pan-controls.html"||
     source.source.githubBlobSha!==V115_BLOB||
     source.sourceArt.widthPx!==1100||source.sourceArt.heightPx!==842||
     source.forkIndex!==PINNED_FORK_INDEX||
     JSON.stringify(source.rawPath)!==PINNED_SOUTH_PATH_JSON||
     !source.verification||source.verification.historicalRoadEvidence!==false||
     source.verification.roadCenterlineMatchesPaintedArt!==false||
     source.verification.bridgeCrossingMatchesPaintedArt!==false||
     source.verification.farBankContinuationVerified!==false||
     source.verification.accessibleStrategicObjectiveVerified!==false||
     !candidate||candidate.schemaVersion!==1||
     candidate.kind!=="candidate_painted_bridge_centerline_not_authoritative"||
     candidate.sourceRouteFile!=="terrain-grid/v115-route-provenance.json"||
     candidate.sourceV115BlobSha!==V115_BLOB||
     candidate.sharedForkIndex!==source.forkIndex||
     !Array.isArray(candidate.bridgeCenterlineArtPx)||
     !equal(candidate.bridgeCenterlineArtPx.at(-1),BRIDGE_TERMINAL)||
     JSON.stringify(candidate.bridgeCenterlineArtPx)!==PINNED_BRIDGE_PATH_JSON||
     !candidate.verification||
     candidate.verification.historicalRoadVerified!==false||
     candidate.verification.roadOnFarBankBeyondBridgeVerified!==false||
     candidate.verification.traversableProductionBridge!==false||
     candidate.verification.conquerableProductionTarget!==false)
    throw Error("Unverified V116 source or bridge provenance");
  const g=api.build({south:source.rawPath,bridge:candidate.bridgeCenterlineArtPx,
    forkIndex:source.forkIndex,imageSize:[source.sourceArt.widthPx,source.sourceArt.heightPx]});
  if(g.kind!=="art-aligned-candidate"||g.approvedForProduction!==false||
     g.conquerable!==false||g.bridgeTerminal!=="visible-far-bank-only"||
     !equal(g.paths.south,source.rawPath)||
     !equal(g.paths.bridge,candidate.bridgeCenterlineArtPx)||
     !equal(g.endpoints.bridgeStop,BRIDGE_TERMINAL))
    throw Error("Candidate graph diverges from sourced artwork or terminal");
  return Object.freeze({...g,imageSize:freezeCopy(g.imageSize),
    forkPoint:freezeCopy(g.forkPoint),edges:freezeCopy(g.edges),
    paths:freezeCopy(g.paths),endpoints:freezeCopy(g.endpoints)});
}
const api={buildSafe};
if(typeof module==="object"&&module.exports)module.exports=api;
else root.CenturyV116SafeRoadGraph=api;
})(typeof globalThis!=="undefined"?globalThis:this);
