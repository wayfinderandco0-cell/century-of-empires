/* V131: preview-only road hit testing against OPEN graph edges, not every
 * visually drawn/uncertified candidate point. Known raw-art hazards win over
 * nearby traversable edges so a tap never silently selects the wrong road.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 else root.V131RoadHit=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
 function segmentDistance(p,a,b){
  const dx=b[0]-a[0],dy=b[1]-a[1],length2=dx*dx+dy*dy;
  const t=length2?Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length2)):0;
  return distance(p,[a[0]+dx*t,a[1]+dy*t]);
 }
 function hitTest(network,p,radius=24){
  if(!network||!(network.tiles instanceof Map)||!(network.graph instanceof Map)||
     !Array.isArray(p)||p.length!==2||!p.every(Number.isFinite)||
     !Number.isFinite(radius)||radius<=0)return {kind:'none'};
  let blocked=null;
  for(const tile of network.tiles.values()){
   for(const [road,indexes] of Object.entries(tile.blockedRoadSegments||{})){
    const points=tile.roads[road];
    for(const i of indexes){
     const a=[points[i][0]+tile.origin[0],points[i][1]+tile.origin[1]];
     const b=[points[i+1][0]+tile.origin[0],points[i+1][1]+tile.origin[1]];
     const d=segmentDistance(p,a,b);
     if(d<=radius&&(!blocked||d<blocked.distance))
      blocked={kind:'blocked',tile:tile.id,road,segment:i,distance:d};
    }
   }
  }
  // Closed-road proximity takes precedence even at a shared junction.
  if(blocked)return blocked;
  let best=null;
  for(const [key,node] of network.graph){
   for(const edge of node.edges){
    if(key>=edge.to)continue; // undirected graph: inspect once
    const target=network.graph.get(edge.to);
    if(!target)continue;
    const d=segmentDistance(p,node.world,target.world);
    if(d>radius||best&&d>=best.distance)continue;
    best={kind:'open',key:distance(p,node.world)<=distance(p,target.world)?key:edge.to,
          distance:d,edgeKind:edge.kind};
   }
  }
  return best||{kind:'none'};
 }
 return {segmentDistance,hitTest};
});
