/* V122 seam geometry gate.
 * Routes from painted cartways may cross tile borders ONLY through inspected,
 * coincident, visibly painted endpoints. Never infer a seam from nearest nodes.
 * Pure CommonJS for the stand-alone renderer, Node tests and future campaign.
 */
'use strict';
const EPS=1.5;
const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const translate=(p,o)=>[p[0]+o[0],p[1]+o[1]];
function octagon(w,h,cut=256){
 if(!(w>2*cut&&h>2*cut))throw Error('Invalid octagon geometry');
 return [[cut,0],[w-cut,0],[w,cut],[w,h-cut],
         [w-cut,h],[cut,h],[0,h-cut],[0,cut]];
}
function segmentDistance(p,a,b){
 const dx=b[0]-a[0],dy=b[1]-a[1],den=dx*dx+dy*dy;
 const t=den?Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)):0;
 return dist(p,[a[0]+t*dx,a[1]+t*dy]);
}
function boundaryDistance(p,polygon){
 return Math.min(...polygon.map((a,i)=>segmentDistance(p,a,polygon[(i+1)%polygon.length])));
}
// A road is navigable only inside its actual convex octagon footprint.
// A tile's rectangular image bounds are NOT sufficient near cut corners.
function insideOctagon(point,polygon,epsilon=1e-7){
 if(!Array.isArray(point)||point.length!==2||!point.every(Number.isFinite))return false;
 let direction=0;
 for(let i=0;i<polygon.length;i++){
  const a=polygon[i],b=polygon[(i+1)%polygon.length];
  const cross=(b[0]-a[0])*(point[1]-a[1])-(b[1]-a[1])*(point[0]-a[0]);
  if(Math.abs(cross)<=epsilon)continue;
  const sign=Math.sign(cross);
  if(direction&&sign!==direction)return false;
  direction=sign;
 }
 return true;
}
// Only opposite-facing, exactly collinear octagon edges form a shared border.
// Overlapping tiles can share a top/bottom line but must never form a seam.
function sharedBorderSegments(a,b){
 const pa=octagon(a.width,a.height,a.corner??256).map(p=>translate(p,a.origin));
 const pb=octagon(b.width,b.height,b.corner??256).map(p=>translate(p,b.origin));
 const tolerance=1e-7,segments=[];
 for(let i=0;i<pa.length;i++){
  const u=pa[i],v=pa[(i+1)%pa.length];
  const dx=v[0]-u[0],dy=v[1]-u[1],len=Math.hypot(dx,dy);
  for(let j=0;j<pb.length;j++){
   const p=pb[j],q=pb[(j+1)%pb.length];
   const bx=q[0]-p[0],by=q[1]-p[1],blen=Math.hypot(bx,by);
   // Same-facing edges indicate overlapping interiors, not neighbors.
   if((dx*bx+dy*by)/(len*blen)>-1+1e-9)continue;
   const lineError=point=>Math.abs(dx*(point[1]-u[1])-dy*(point[0]-u[0]))/len;
   if(lineError(p)>tolerance||lineError(q)>tolerance)continue;
   const t1=((p[0]-u[0])*dx+(p[1]-u[1])*dy)/len;
   const t2=((q[0]-u[0])*dx+(q[1]-u[1])*dy)/len;
   const lo=Math.max(0,Math.min(t1,t2)),hi=Math.min(len,Math.max(t1,t2));
   if(hi-lo<=tolerance)continue; // corner contact is not a side
   const at=t=>[u[0]+t*dx/len,u[1]+t*dy/len];
   segments.push([at(lo),at(hi)]);
  }
 }
 return segments;
}
function sharedSideLength(a,b){
 return sharedBorderSegments(a,b).reduce((best,[u,v])=>Math.max(best,dist(u,v)),0);
}
function endpoint(tile,port){
 const road=tile.roads && tile.roads[port.road];
 if(!road||road.length<2||road.some(p=>!Array.isArray(p)||p.length!==2))return null;
 return port.end==='start'?road[0]:port.end==='end'?road[road.length-1]:null;
}
function validateSeam(tiles,link,epsilon=EPS){
 const a=tiles.get(link.from.tile),b=tiles.get(link.to.tile),errors=[];
 if(!a||!b)return {id:link.id,pass:false,errors:['missing_tile']};
 const ap=endpoint(a,link.from),bp=endpoint(b,link.to);
 if(!ap||!bp)return {id:link.id,pass:false,errors:['missing_road_or_endpoint']};
 const polyA=octagon(a.width,a.height,a.corner||256);
 const polyB=octagon(b.width,b.height,b.corner||256);
 const distanceA=boundaryDistance(ap,polyA),distanceB=boundaryDistance(bp,polyB);
 const worldA=translate(ap,a.origin),worldB=translate(bp,b.origin);
 const gap=dist(worldA,worldB);
 if(distanceA>epsilon)errors.push('from_road_ends_inside_tile');
 if(distanceB>epsilon)errors.push('to_road_ends_inside_tile');
 if(gap>epsilon)errors.push('world_seam_gap');
 const shared=sharedBorderSegments(a,b);
 if(!shared.length)errors.push('no_shared_octagon_side');
 else if(!shared.some(([u,v])=>segmentDistance(worldA,u,v)<=1e-6 &&
                                  segmentDistance(worldB,u,v)<=1e-6))
  errors.push('endpoint_not_on_shared_border');
 if(a.artReviewed!==true||b.artReviewed!==true ||
    link.bothRoadsVisuallyVerified!==true)errors.push('source_art_not_approved');
 // Prevent an invisible/temporary connection being used in the live game.
 if(link.enabled!==true)errors.push('join_not_enabled');
 return {id:link.id,pass:errors.length===0,errors,
         endpointGapPx:gap,sourceInsetPx:distanceA,targetInsetPx:distanceB,
         from:worldA,to:worldB};
}
function buildNetwork(plan,epsilon=EPS){
 if(!Array.isArray(plan.tiles)||!Array.isArray(plan.links))throw Error('Bad network plan');
 const tiles=new Map(),graph=new Map(),seams=[];
 for(const t of plan.tiles){
  if(tiles.has(t.id)||!Array.isArray(t.origin)||t.origin.length!==2||!t.origin.every(Number.isFinite)||
     !Number.isFinite(t.width)||!Number.isFinite(t.height)||
     !Number.isFinite(t.corner??256)||(t.corner??256)<=0)throw Error('Bad tile');
  const polygon=octagon(t.width,t.height,t.corner??256);
  for(const [road,points] of Object.entries(t.roads||{})){
   if(!Array.isArray(points))throw Error('Bad road: '+t.id+'/'+road);
   for(const point of points)if(!insideOctagon(point,polygon))throw Error('Road leaves octagon: '+t.id+'/'+road);
  }
  // Reviewed raw-art hazards may close individual *segments* without
  // changing source coordinates or drawing an invented replacement road.
  const blocked=t.blockedRoadSegments??{};
  if(!blocked||typeof blocked!=='object'||Array.isArray(blocked))throw Error('Bad blocked road segments');
  for(const [road,indexes] of Object.entries(blocked)){
   const points=t.roads?.[road];
   if(!Array.isArray(points)||!Array.isArray(indexes))throw Error('Bad blocked road segments: '+t.id+'/'+road);
   const seen=new Set();
   for(const i of indexes){
    if(!Number.isInteger(i)||i<0||i>=points.length-1||seen.has(i))
     throw Error('Bad blocked road segment index: '+t.id+'/'+road);
    seen.add(i);
   }
  }
  tiles.set(t.id,t);
 }
 function key(id,p){return id+'@'+p[0].toFixed(3)+','+p[1].toFixed(3);}
 function ensure(id,p){const k=key(id,p);if(!graph.has(k))graph.set(k,{id,world:translate(p,tiles.get(id).origin),edges:[]});return k;}
 function edge(u,v,length,kind){graph.get(u).edges.push({to:v,length,kind});graph.get(v).edges.push({to:u,length,kind});}
 for(const t of plan.tiles)for(const [road,points] of Object.entries(t.roads||{})){
  if(points.length<2)continue;
  for(let i=1;i<points.length;i++){
   if(dist(points[i],points[i-1])<0.0001)throw Error('Duplicate road point: '+t.id+'/'+road);
   // A raw-art mismatch closes this edge in BOTH directions; never bridge it.
   if((t.blockedRoadSegments?.[road]??[]).includes(i-1))continue;
   const u=ensure(t.id,points[i-1]),v=ensure(t.id,points[i]);
   edge(u,v,dist(points[i-1],points[i]),'painted-road');
  }
 }
 for(const link of plan.links){
  const check=validateSeam(tiles,link,epsilon);
  seams.push(check);
  if(!check.pass)continue;
  const a=tiles.get(link.from.tile),b=tiles.get(link.to.tile);
  const u=ensure(a.id,endpoint(a,link.from)),v=ensure(b.id,endpoint(b,link.to));
  edge(u,v,check.endpointGapPx,'approved-seam');
 }
 function planRoute(start,end){
  if(!graph.has(start)||!graph.has(end))return null;
  const queue=new Set(graph.keys()),cost=new Map([[start,0]]),prior=new Map();
  while(queue.size){
   let selected=null,best=Infinity;
   for(const id of queue){const d=cost.get(id)??Infinity;if(d<best){best=d;selected=id;}}
   if(selected===null||best===Infinity)break;
   queue.delete(selected);if(selected===end)break;
   for(const e of graph.get(selected).edges)if(queue.has(e.to)){
    const n=best+e.length;
    if(n<(cost.get(e.to)??Infinity)){cost.set(e.to,n);prior.set(e.to,selected);}
   }
  }
  if(!cost.has(end))return null;
  const keys=[end];while(keys[0]!==start){const previous=prior.get(keys[0]);if(!previous)return null;keys.unshift(previous);}
  return {distance:cost.get(end),keys,positions:keys.map(k=>graph.get(k).world),
          seams:keys.slice(1).filter((k,i)=>graph.get(keys[i]).id!==graph.get(k).id).length};
 }
 return {tiles,graph,seams,planRoute,key};
}
const seamApi={octagon,boundaryDistance,insideOctagon,sharedBorderSegments,sharedSideLength,endpoint,validateSeam,buildNetwork};
if(typeof module!=='undefined'&&module.exports)module.exports=seamApi;
if(typeof window!=='undefined')window.V122Seam=seamApi;
