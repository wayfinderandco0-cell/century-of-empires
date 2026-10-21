/* Candidate V115 art-pixel route to ordered V116 child-tile crossings; never gameplay authorization. */
(function(root){
"use strict";
const render=typeof require==="function"?require("./v116_local_art_renderer.js"):root.CenturyV116Tiles;
const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const point=(a,b,t)=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];
function traceRoute(index,path){
 render.validate(index);
 if(!Array.isArray(path)||path.length<2||path.some(p=>!Array.isArray(p)||p.length!==2||p.some(v=>typeof v!=="number"||!Number.isFinite(v))))throw Error("Invalid candidate route");
 const {rows,columns:cols}=index.grid;
 const tiles=new Map(index.tiles.map(t=>[t.row+":"+t.col,t]));
 const xs=[0],ys=[0];
 for(let c=0;c<cols;c++)xs.push(tiles.get("0:"+c).imageCropPx[2]);
 for(let r=0;r<rows;r++)ys.push(tiles.get(r+":0").imageCropPx[3]);
 const locate=(v,edges)=>{
   if(v<0||v>edges.at(-1))throw Error("Route point outside artwork");
   return v===edges.at(-1)?edges.length-2:edges.findIndex((e,i)=>i<edges.length-1&&v>=e&&v<edges[i+1]);
 };
 const tile=p=>tiles.get(locate(p[1],ys)+":"+locate(p[0],xs)).id;
 path.forEach(tile);
 const spans=[];let length=0;
 for(let i=1;i<path.length;i++){
   const a=path[i-1],b=path[i],len=dist(a,b);
   if(len<1e-9)throw Error("Zero-length route edge");
   const ts=[0,1];
   for(const [axis,edges] of [[0,xs],[1,ys]]){
     const d=b[axis]-a[axis];if(Math.abs(d)<1e-9)continue;
     for(const edge of edges.slice(1,-1)){
       const t=(edge-a[axis])/d;if(t>1e-9&&t<1-1e-9)ts.push(t);
     }
   }
   ts.sort((a,b)=>a-b);
   for(let j=1;j<ts.length;j++){
     const t0=ts[j-1],t1=ts[j];if(t1-t0<1e-9)continue;
     const fromPx=point(a,b,t0),toPx=point(a,b,t1);
     spans.push({tileId:tile(point(a,b,(t0+t1)/2)),segmentIndex:i-1,
       fromPx,toPx,startDistancePx:length+len*t0,endDistancePx:length+len*t1});
   }
   length+=len;
 }
 if(!spans.length||Math.abs(spans.at(-1).endDistancePx-length)>1e-6)throw Error("Incomplete trace");
 const seams=[];
 for(let i=1;i<spans.length;i++){
   const a=spans[i-1],b=spans[i];
   if(dist(a.toPx,b.fromPx)>1e-6||Math.abs(a.endDistancePx-b.startDistancePx)>1e-6)throw Error("Discontinuous tile seam");
   if(a.tileId!==b.tileId)seams.push({fromTile:a.tileId,toTile:b.tileId,atArtPx:b.fromPx.slice(),distancePx:b.startDistancePx});
 }
 return {kind:"candidate_art_tile_trace_not_playable",productionAccess:false,lengthPx:length,
   spans,seams,visitedTileIds:[...new Set(spans.map(s=>s.tileId))].sort()};
}
function traceGraph(index,g){
 if(!g||g.approvedForProduction!==false||g.conquerable!==false||g.bridgeTerminal!=="visible-far-bank-only")throw Error("Expected nonproduction visible-bank-only graph");
 const out={kind:"candidate_only",productionAccess:false};
 for(const name of ["south","bridge"]){
   const t=traceRoute(index,g.paths[name]);out[name]=t;
   if(Math.abs(t.lengthPx-g.length(name))>1e-6)throw Error("Arclength mismatch");
   for(const s of t.seams)if(dist(s.atArtPx,g.sample(name,s.distancePx))>1e-6)throw Error("Army/seam mismatch");
 }
 return out;
}
const api={traceRoute,traceGraph};
if(typeof module==="object"&&module.exports)module.exports=api;
else root.CenturyV116RouteTileTrace=api;
})(typeof globalThis!=="undefined"?globalThis:this);
