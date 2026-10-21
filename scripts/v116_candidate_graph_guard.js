/* V116: fail-closed, immutable public view of a sourced road-graph candidate.
 * This is not historical verification or permission to cross the far bank.
 */
(function(root){
"use strict";
const freezeCopy=v=>Array.isArray(v)?Object.freeze(v.map(freezeCopy)):
  v&&typeof v==="object"?Object.freeze(Object.fromEntries(
    Object.entries(v).map(([k,x])=>[k,freezeCopy(x)]))):v;
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function buildSafe(source,candidate,roadApi){
  const api=roadApi||(typeof require==="function"?require("./v116_road_graph.js"):root.CenturyV116RoadGraph);
  if(!api||typeof api.build!=="function"||!source||!source.source||!source.sourceArt||
     !candidate||candidate.sourceV115BlobSha!==source.source.githubBlobSha||
     candidate.sharedForkIndex!==source.forkIndex||
     !candidate.verification||
     candidate.verification.roadOnFarBankBeyondBridgeVerified!==false||
     candidate.verification.traversableProductionBridge!==false)
    throw Error("Unverified V116 source or bridge provenance");
  const g=api.build({south:source.rawPath,bridge:candidate.bridgeCenterlineArtPx,
    forkIndex:source.forkIndex,imageSize:[source.sourceArt.widthPx,source.sourceArt.heightPx]});
  if(g.kind!=="art-aligned-candidate"||g.approvedForProduction!==false||
     g.conquerable!==false||g.bridgeTerminal!=="visible-far-bank-only"||
     !equal(g.paths.south,source.rawPath)||
     !equal(g.paths.bridge,candidate.bridgeCenterlineArtPx)||
     !equal(g.endpoints.bridgeStop,candidate.bridgeCenterlineArtPx.at(-1)))
    throw Error("Candidate graph diverges from sourced artwork or terminal");
  return Object.freeze({...g,imageSize:freezeCopy(g.imageSize),
    forkPoint:freezeCopy(g.forkPoint),edges:freezeCopy(g.edges),
    paths:freezeCopy(g.paths),endpoints:freezeCopy(g.endpoints)});
}
const api={buildSafe};
if(typeof module==="object"&&module.exports)module.exports=api;
else root.CenturyV116SafeRoadGraph=api;
})(typeof globalThis!=="undefined"?globalThis:this);
