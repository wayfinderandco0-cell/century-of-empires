/* Century of Empires V117 — paint road from the SAME candidate graph as unit motion.
 * Strictly a visual prototype. Does NOT verify historical roads, the south path,
 * a beyond-bank bridge exit, traversal, conquest, or the production octagon.
 * No manually maintained second "visual" centerline is permitted.
 */
(function(root){
"use strict";
const point=p=>Array.isArray(p)&&p.length===2&&p.every(v=>typeof v==="number"&&Number.isFinite(v));
const eq=(a,b)=>a[0]===b[0]&&a[1]===b[1];
const clone=arr=>arr.map(p=>p.slice());
function length(a,b){return Math.hypot(b[0]-a[0],b[1]-a[1]);}
function offsets(points,amount){
 if(!Array.isArray(points)||points.length<2||points.some(p=>!point(p)))throw Error("Bad cart track geometry");
 return points.map((p,i)=>{
  const lo=points[Math.max(0,i-1)],hi=points[Math.min(points.length-1,i+1)];
  const dx=hi[0]-lo[0],dy=hi[1]-lo[1],n=Math.hypot(dx,dy);
  if(n<=1e-9)throw Error("Degenerate cart track tangent");
  return [p[0]-dy*amount/n,p[1]+dx*amount/n];
 });
}
function segmentDistance(p,a,b){
 const vx=b[0]-a[0],vy=b[1]-a[1],den=vx*vx+vy*vy;
 const t=den?Math.max(0,Math.min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/den)):0;
 return Math.hypot(p[0]-a[0]-t*vx,p[1]-a[1]-t*vy);
}
function distanceToCenterline(p,route){
 if(!point(p)||!Array.isArray(route)||route.length<2)throw Error("Invalid art path");
 let best=Infinity;
 for(let i=1;i<route.length;i++)best=Math.min(best,segmentDistance(p,route[i-1],route[i]));
 return best;
}
function build(graph){
 if(!graph||graph.kind!=="art-aligned-candidate"||graph.approvedForProduction!==false||
    graph.conquerable!==false||graph.bridgeTerminal!=="visible-far-bank-only"||
    typeof graph.sample!=="function"||typeof graph.length!=="function"||
    !graph.edges||!graph.paths||!graph.endpoints||!Array.isArray(graph.imageSize))
    throw Error("V117 refuses unverified or production bridge graph");
 const all=Object.fromEntries(["south","bridge"].map(n=>[n,clone(graph.paths[n])]));
 const approach=clone(graph.edges.approach),south=clone(graph.edges.south),bridge=clone(graph.edges.bridge);
 const fork=approach.at(-1),stop=graph.endpoints.bridgeStop;
 if(!point(stop)||!point(fork)||!eq(stop,bridge.at(-1))||
    !eq(fork,south[0])||!eq(fork,bridge[0])||
    !eq(stop,all.bridge.at(-1))||!eq(graph.endpoints.southExit,all.south.at(-1)))
   throw Error("Graph branch artwork disconnected");
 for(const [n,path] of Object.entries(all)){
  if(path.length<2||path.some(p=>!point(p)||p[0]<0||p[1]<0||
       p[0]>graph.imageSize[0]||p[1]>graph.imageSize[1]))
    throw Error("Road art exceeds source painting");
  for(let i=1;i<path.length;i++)if(length(path[i-1],path[i])<=1e-9)
    throw Error("Road art has zero-length segment");
  if(distanceToCenterline(graph.sample(n,graph.length(n)),path)>1e-6)
    throw Error("Endpoint of moving army differs from painted track");
 }
 // Keep an immutable geometry snapshot: production may never mutate the art
 // independently of its movement graph, even when a caller passes mutable data.
 const saved=JSON.stringify(all),edges={approach,south,bridge};
 function assertSynced(){
  if(JSON.stringify({south:graph.paths.south,bridge:graph.paths.bridge})!==saved)
    throw Error("Road artwork/army source geometry changed independently");
  for(const n of ["south","bridge"]){
   for(let i=0;i<=32;i++){
    const p=graph.sample(n,graph.length(n)*i/32);
    if(distanceToCenterline(p,all[n])>1e-6)
      throw Error("Army has left painted road centerline");
   }
  }
  return true;
 }
 assertSynced();
 function trace(ctx,project,path,color,width){
  ctx.beginPath();
  path.forEach((p,i)=>{const q=project(p);if(!point(q))throw Error("Invalid road projection");
    if(i)ctx.lineTo(q[0],q[1]);else ctx.moveTo(q[0],q[1]);});
  ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();
 }
 function paint(ctx,project,opts={}){
  assertSynced();
  if(!ctx||typeof ctx.beginPath!=="function"||typeof ctx.stroke!=="function"||
     typeof ctx.save!=="function"||typeof ctx.restore!=="function"||
     typeof project!=="function")throw Error("Invalid road art canvas");
  const route=opts.route||"bridge";
  if(!["bridge","south","both"].includes(route))throw Error("Unknown road drawing branch");
  const origin=project([100,100]),dx=project([101,100]),dy=project([100,101]);
  if(!point(origin)||!point(dx)||!point(dy))throw Error("Invalid art coordinate projection");
  const sx=length(origin,dx),sy=length(origin,dy);
  if(sx<=0||sy<=0||Math.max(sx,sy)/Math.min(sx,sy)>1.1)
    throw Error("Road art requires near-isotropic art-pixel projection");
  const scale=(sx+sy)/2;
  // Two earth shoulders and paired wheel ruts share one source-pixel centerline.
  // This overlay is visibly different from the original painting; it is a
  // diagnostic authoring layer, NOT independent proof the source road matches.
  const chosen=[edges.approach];
  if(route==="bridge"||route==="both")chosen.push(edges.bridge);
  if(route==="south"||route==="both")chosen.push(edges.south);
  ctx.save();
  try{
   ctx.lineCap="round";ctx.lineJoin="round";
   ctx.globalAlpha=opts.alpha===undefined?.82:opts.alpha;
   if(!Number.isFinite(ctx.globalAlpha)||ctx.globalAlpha<0||ctx.globalAlpha>1)
     throw Error("Invalid road opacity");
   for(const path of chosen){
    trace(ctx,project,path,"#443f30",18*scale);
    trace(ctx,project,path,"#9b845c",14*scale);
    trace(ctx,project,path,"#b8a077",11*scale);
    trace(ctx,project,offsets(path,-3.6),"#66583f",1.3*scale);
    trace(ctx,project,offsets(path,3.6),"#66583f",1.3*scale);
   }
  }finally{ctx.restore();}
  return Object.freeze({kind:"prototype-cart-track",route,
    drawnCenterline:"the same candidate graph the army follows",
    bridgeStop:stop.slice(),farBankContinuationVerified:false,
    approvedForProduction:false});
 }
 return Object.freeze({kind:"prototype-coupled-road-art",approvedForProduction:false,
  bridgeStop:stop.slice(),assertSynced,paint,distanceToCenterline:(p,n)=>{
   if(!Object.hasOwn(all,n))throw Error("Unknown candidate route");return distanceToCenterline(p,all[n]);},
  sampledArmy:(n,d)=>{assertSynced();return graph.sample(n,d);}});
}
const api={build,offsets,distanceToCenterline};
if(typeof module==="object"&&module.exports)module.exports=api;
else root.CenturyV117RoadArt=api;
})(typeof globalThis!=="undefined"?globalThis:this);
