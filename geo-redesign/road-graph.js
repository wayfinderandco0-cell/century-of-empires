/* Century of Empires: geographical road graph.
   The rendered road is precisely the same geometry used for snapping, shortest
   paths, and army interpolation. Units are meters, coordinates are WGS84.
   This module does NOT change any existing campaign/gameplay travel rules. */
(function(root,factory){
 const api=factory();
 if(typeof module==="object"&&module.exports)module.exports=api;
 else root.COEGeoRoads=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 "use strict";
 const rad=Math.PI/180,earth=6371008.8;
 const key=p=>p.map(n=>Number(n).toFixed(7)).join(",");
 function distance(a,b){
  const phi1=a[1]*rad,phi2=b[1]*rad,dl=(b[0]-a[0])*rad,dp=phi2-phi1;
  const h=Math.sin(dp/2)**2+Math.cos(phi1)*Math.cos(phi2)*Math.sin(dl/2)**2;
  return 2*earth*Math.asin(Math.min(1,Math.sqrt(h)));
 }
 function build(corridors){
  if(!Array.isArray(corridors)||!corridors.length)throw Error("No road corridors supplied");
  const nodes=new Map(),segments=[],roads=[],links=new Map();
  function addNode(point){
   if(!Array.isArray(point)||point.length!==2||!point.every(Number.isFinite))throw Error("Invalid geographic point");
   const k=key(point);
   if(!nodes.has(k)){nodes.set(k,point.slice());links.set(k,[])}
   return k;
  }
  function connect(a,b,len){
   if(len<=0)throw Error("Zero length segment");
   links.get(a).push({key:b,length:len});links.get(b).push({key:a,length:len});
  }
  for(const corridor of corridors){
   if(!Array.isArray(corridor.coordinates)||corridor.coordinates.length<2)throw Error("Incomplete corridor");
   const coords=corridor.coordinates.map(p=>p.slice());
   roads.push({id:corridor.id,coordinates:coords,certainty:corridor.certainty});
   for(let i=1;i<coords.length;i++){
    const a=coords[i-1],b=coords[i],ak=addNode(a),bk=addNode(b),len=distance(a,b);
    connect(ak,bk,len);
    segments.push({id:corridor.id,a,b,ak,bk,length:len});
   }
  }
  const seen=new Set(),queue=[nodes.keys().next().value];seen.add(queue[0]);
  for(let i=0;i<queue.length;i++)for(const edge of links.get(queue[i])){
   if(!seen.has(edge.key)){seen.add(edge.key);queue.push(edge.key)}
  }
  if(seen.size!==nodes.size)throw Error("Disconnected road network");
  function nearest(point){
   let closest=null;
   for(const seg of segments){
    const latitude=(seg.a[1]+seg.b[1]+point[1])/3*rad;
    const scaleX=Math.cos(latitude)*111195,scaleY=111195;
    const vx=(seg.b[0]-seg.a[0])*scaleX,vy=(seg.b[1]-seg.a[1])*scaleY;
    const wx=(point[0]-seg.a[0])*scaleX,wy=(point[1]-seg.a[1])*scaleY;
    const t=Math.min(1,Math.max(0,(wx*vx+wy*vy)/(vx*vx+vy*vy)));
    const snapped=[seg.a[0]+t*(seg.b[0]-seg.a[0]),seg.a[1]+t*(seg.b[1]-seg.a[1])];
    const meters=distance(point,snapped);
    if(!closest||meters<closest.meters)closest={point:snapped,meters,t,segment:seg};
   }
   return closest;
  }
  function route(from,to,maxSnapMeters=650){
   const start=nearest(from),goal=nearest(to);
   if(!start||!goal||start.meters>maxSnapMeters||goal.meters>maxSnapMeters)return null;
   const graph=new Map([...links].map(([k,v])=>[k,v.slice()]));
   graph.set("__start",[]);graph.set("__goal",[]);
   function attach(point,id){
    const s=point.segment;
    graph.get(id).push({key:s.ak,length:s.length*point.t},{key:s.bk,length:s.length*(1-point.t)});
    graph.get(s.ak).push({key:id,length:s.length*point.t});
    graph.get(s.bk).push({key:id,length:s.length*(1-point.t)});
   }
   attach(start,"__start");attach(goal,"__goal");
   if(start.segment===goal.segment){
    const d=start.segment.length*Math.abs(start.t-goal.t);
    graph.get("__start").push({key:"__goal",length:d});
    graph.get("__goal").push({key:"__start",length:d});
   }
   const scores=new Map([["__start",0]]),previous=new Map(),visited=new Set();
   while(true){
    let current=null,best=Infinity;
    for(const [k,cost] of scores){
     if(!visited.has(k)&&cost<best){current=k;best=cost}
    }
    if(current===null||current==="__goal")break;
    visited.add(current);
    for(const next of graph.get(current)){
     const score=best+next.length;
     if(score<(scores.get(next.key)??Infinity)){scores.set(next.key,score);previous.set(next.key,current)}
    }
   }
   if(!scores.has("__goal"))return null;
   const path=["__goal"];
   while(path[0]!=="__start"){
    const prev=previous.get(path[0]);if(!prev)return null;
    path.unshift(prev);
   }
   const coordinates=path.map(k=>k==="__start"?start.point:k==="__goal"?goal.point:nodes.get(k));
   return {coordinates,meters:scores.get("__goal"),snappedStart:start.point,
    snappedGoal:goal.point,offRoadMeters:[start.meters,goal.meters]};
  }
  function interpolate(path,meters){
   if(!path?.length)throw Error("Empty route path");
   let remaining=Math.max(0,meters);
   for(let i=1;i<path.length;i++){
    const a=path[i-1],b=path[i],d=distance(a,b);
    if(remaining<=d)return [a[0]+(b[0]-a[0])*(d?remaining/d:0),a[1]+(b[1]-a[1])*(d?remaining/d:0)];
    remaining-=d;
   }
   return path[path.length-1].slice();
  }
  const geometry={type:"FeatureCollection",features:roads.map(r=>({
   type:"Feature",properties:{id:r.id,certainty:r.certainty},
   geometry:{type:"LineString",coordinates:r.coordinates}
  }))};
  return {roads,segments,nodes,links,geometry,nearest,route,interpolate,distance,
   verify:{connected:true,roadCount:roads.length,nodeCount:nodes.size,segments:segments.length}};
 }
 return Object.freeze({build,distance});
});