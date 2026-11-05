/* Approved three-octagon road network. Road graphics and march paths share these exact polylines. */
(function(root,make){
 const api=make();
 if(typeof module==="object"&&module.exports)module.exports=api;
 else root.COEApprovedRoads=api;
})(typeof globalThis!=="undefined"?globalThis:this,()=>{
 "use strict";
 const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
 const round=n=>Math.round(n*1000)/1000;
 const key=p=>round(p[0])+","+round(p[1]);
 function build(manifest){
  if(!manifest||!Array.isArray(manifest.tileArt))throw Error("Missing approved tile/road manifest");
  const nodes=new Map(),segments=[],roads=[];
  function node(p){if(!p.every(Number.isFinite))throw Error("Invalid coordinate");const k=key(p);
   if(!nodes.has(k))nodes.set(k,{p:[...p],to:[]});return k}
  function edge(a,b,length){if(length<=.00001)throw Error("Zero-length road");nodes.get(a).to.push({k:b,length});nodes.get(b).to.push({k:a,length})}
  for(const tile of manifest.tileArt){
   if(!Array.isArray(tile.origin)||tile.origin.length!==2)throw Error("Missing world offset: "+tile.id);
   for(const [name,local] of Object.entries(tile.roads||{})){
    if(!Array.isArray(local)||local.length<2)throw Error("Road without geometry: "+tile.id+"/"+name);
    const pts=local.map(p=>[p[0]+tile.origin[0],p[1]+tile.origin[1]]);
    const r={id:tile.id+"/"+name,tile:tile.id,points:pts};roads.push(r);
    for(let i=1;i<pts.length;i++){
     const pa=pts[i-1],pb=pts[i],a=node(pa),b=node(pb),len=dist(pa,pb);
     if(a===b)throw Error("Collapsed road: "+r.id);
     edge(a,b,len);segments.push({a,b,pa,pb,length:len,id:r.id});
    }
   }
  }
  if(!nodes.size)throw Error("Map has no registered roads");
  const queue=[nodes.keys().next().value],seen=new Set(queue);
  for(let i=0;i<queue.length;i++)for(const e of nodes.get(queue[i]).to)if(!seen.has(e.k)){seen.add(e.k);queue.push(e.k)}
  if(seen.size!==nodes.size)throw Error("Disconnected visible roads: "+(nodes.size-seen.size)+" unreachable points");
  function nearest(pos){
   let best=null;
   for(const s of segments){
    const dx=s.pb[0]-s.pa[0],dy=s.pb[1]-s.pa[1],t=Math.min(1,Math.max(0,((pos[0]-s.pa[0])*dx+(pos[1]-s.pa[1])*dy)/(dx*dx+dy*dy)));
    const p=[s.pa[0]+t*dx,s.pa[1]+t*dy],d=dist(pos,p);
    if(!best||d<best.distance)best={p,t,distance:d,segment:s};
   }return best;
  }
  function route(from,to,maxOffRoad=110){
   const start=nearest(from),goal=nearest(to);
   if(!start||!goal||start.distance>maxOffRoad||goal.distance>maxOffRoad)return null;
   const scratch=new Map([...nodes].map(([k,v])=>[k,v.to.slice()]));
   const connect=(a,b,length)=>{scratch.get(a).push({k:b,length});scratch.get(b).push({k:a,length})};
   scratch.set("__start",[]);scratch.set("__goal",[]);
   for(const [s,k] of [[start,"__start"],[goal,"__goal"]]){
    connect(k,s.segment.a,s.segment.length*s.t);
    connect(k,s.segment.b,s.segment.length*(1-s.t));
   }
   if(start.segment===goal.segment)connect("__start","__goal",start.segment.length*Math.abs(start.t-goal.t));
   const best=new Map([["__start",0]]),prev=new Map(),done=new Set();
   while(done.size<scratch.size){
    let u=null,cost=Infinity;
    for(const [k,d] of best)if(!done.has(k)&&d<cost){u=k;cost=d}
    if(u===null||u==="__goal")break;
    done.add(u);
    for(const e of scratch.get(u)){const n=cost+e.length;if(n<(best.get(e.k)??Infinity)){best.set(e.k,n);prev.set(e.k,u)}}
   }
   if(!best.has("__goal"))return null;
   const sequence=["__goal"];while(sequence[0]!=="__start"){const k=prev.get(sequence[0]);if(!k)return null;sequence.unshift(k)}
   const points=sequence.map(k=>k==="__start"?start.p:k==="__goal"?goal.p:nodes.get(k).p);
   return {points,length:best.get("__goal"),offRoad:[start.distance,goal.distance]};
  }
  return {roads,segments,nodes,nearest,route,verify:{connected:true,roadCount:roads.length,nodeCount:nodes.size,segmentCount:segments.length,deadEnds:[...nodes.values()].filter(n=>n.to.length===1).length}};
 }
 return Object.freeze({build});
});
