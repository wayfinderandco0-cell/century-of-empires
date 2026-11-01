/* V267 EAST-01 additive route CONTRACT, not a certified route or game mutation.
 * Protects immutable V123 WEST/MATREI/SOUTH graph. This candidate may NOT be
 * used for army movement until cartway paint and physical border are approved.
 * The proposed Alpine route is fictional, not a surveyed 1780-1880 road.
 */
(function(root,factory){
  const isNode=typeof module!=="undefined"&&module.exports;
  const api=factory(isNode?require("./v122-seam-engine.js"):root.V122Seam);
  if(isNode)module.exports=api;else root.COEV267EastExtension=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(seams){
"use strict";
const clone=x=>JSON.parse(JSON.stringify(x));
const EAST_ID="east-01";
const MATREI_EXIT=[1536,749];
const EAST_ENTRY=[0,749];
function candidate(base){
 if(!base||base.version!==123||!Array.isArray(base.tiles)||!Array.isArray(base.links))
   throw Error("V123 base is required");
 const tiles=clone(base.tiles),links=clone(base.links);
 if(tiles.length!==3||links.length!==2||tiles.some(t=>!["west","matrei","south"].includes(t.id)))
   throw Error("Protected three-tile V123 baseline changed");
 const matrei=tiles.find(t=>t.id==="matrei");
 const end=matrei.roads.southeast?.at(-1);
 if(!end||end[0]!==1351||end[1]!==749)throw Error("V123 southeast road changed");
 // PREVIEW-ONLY: coordinates exactly follow V8 compositor ROUTE (scripts/v267_east01_cartway_v7.py).\n // Geometry alignment is necessary but NOT proof of physical art, history, or playability.
 matrei.roads.southeast.push([1425,750],MATREI_EXIT.slice());
 tiles.push({id:EAST_ID,name:"Unapproved east Alpine terrain study",
   origin:[3072,0],width:1536,height:1024,corner:256,
   biome:"alpine-forest-limestone-ridge",artReviewed:false,
   scenicSettlements:[],strategicNodes:[],provinceIds:[],
   roads:{west:[EAST_ENTRY.slice(),[79,747],[169,739],[249,723],[329,700],[412,667],[488,628],[569,592],[644,567],[714,559]]}});
 links.push({id:"matrei-east-01-candidate",
   from:{tile:"matrei",road:"southeast",end:"end"},
   to:{tile:EAST_ID,road:"west",end:"start"},
   bothRoadsVisuallyVerified:false,enabled:false});
 const network=seams.buildNetwork({tiles,links});
 const check=network.seams.find(s=>s.id==="matrei-east-01-candidate");
 if(!check||check.pass||check.endpointGapPx!==0)
   throw Error("Unapproved east seam must be geometrically paired but disabled");
 if(network.seams.filter(s=>s.pass).length!==2)
   throw Error("Protected V123 seams drifted");
 return {version:"v267-east-candidate/v1",tiles,links,network,
   roadPaintVerified:false,riverVerified:false,nativePlayable:false,
   historicallyVerified:false,finished:false};
}
return Object.freeze({candidate,EAST_ID,MATREI_EXIT,EAST_ENTRY});
});