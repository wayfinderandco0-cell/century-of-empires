/* V267 SOUTH→SOUTHEAST candidate: route geometry PRE-FLIGHT ONLY.
 * The approved SOUTH source art appears to show a cartway exiting its
 * eastern border. The exact exit is NOT surveyed/visually certified.
 * This module never enables movement or paints a road; do not promote it
 * until source-art road contact, edge registration and a NEW roaded
 * neighbor image have been independently reviewed on real WebKit.
 */
(function(root,factory){
 const api=factory(typeof module!=="undefined"&&module.exports?require("./v122-seam-engine.js"):root.V122Seam);
 if(typeof module!=="undefined"&&module.exports)module.exports=api;
 else root.COEV267SouthEastGate=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(seams){
 "use strict";
 const copy=o=>JSON.parse(JSON.stringify(o));
 const ID="south-east-road-pilot";
 const EXIT=[1536,578],ENTRY=[0,578];
 function candidate(base){
  if(!base||base.version!==123||base.tiles?.length!==3||base.links?.length!==2)
   throw Error("Immutable V123 three-cell network required");
  const tiles=copy(base.tiles),links=copy(base.links);
  const south=tiles.find(t=>t.id==="south");
  if(!south||south.origin.join(",")!=="1536,1024"||
    south.roads.north?.at(-1)?.join(",")!=="1270,605")
   throw Error("SOUTH V123 source route changed; stop");
  // Provisional extension along the apparent SOUTH eastbound cartway.
  // These intermediate points require painted-road control-point QA.
  south.roads.eastCandidate=[[1270,605],[1355,597],[1440,586],EXIT.slice()];
  tiles.push({id:ID,name:"Southeast Alpine road candidate — NOT PLAYABLE",
   origin:[3072,1024],width:1536,height:1024,corner:256,
   artReviewed:false,roads:{westCandidate:[ENTRY.slice(),[140,602],[260,636],[390,668],[530,672],[690,647],[835,610]]},
   scenicSettlements:[],strategicNodes:[],provinceIds:[]});
  links.push({id:"south-southeast-provisional",
   from:{tile:"south",road:"eastCandidate",end:"end"},
   to:{tile:ID,road:"westCandidate",end:"start"},
   bothRoadsVisuallyVerified:false,enabled:false});
  const network=seams.buildNetwork({tiles,links});
  const seam=network.seams.find(s=>s.id==="south-southeast-provisional");
  if(!seam||seam.pass||seam.endpointGapPx!==0||
     !seam.errors.includes("source_art_not_approved")||
     !seam.errors.includes("join_not_enabled"))
   throw Error("Unsafe: provisional route became traversable");
  if(network.seams.filter(s=>s.pass).length!==2)
   throw Error("Approved WEST/MATREI/SOUTH graph changed");
  return {version:"v267-south-east-preflight/v1",tiles,links,network,
   paintedRoadReviewed:false,neighborRoadArtAvailable:false,
   riverCrossingsVerified:false,nativePlayable:false,userApproved:false};
 }
 return Object.freeze({candidate,ID,EXIT,ENTRY});
});
