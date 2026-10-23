/* V132: fail-closed validation for every army route before movement begins.
 * A graph route must use existing graph edges in order. A route's own points,
 * claimed distance, or claimed seam count are never trusted on their own.
 * This is a safety contract, not certification of painted/historical roads.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 else root.V132RouteContract=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 function validateRoute(network,route){
  const reject=reason=>({pass:false,reason});
  if(!network||!(network.graph instanceof Map)||!route||
     !Array.isArray(route.keys)||!Array.isArray(route.positions)||
     route.keys.length===0||route.keys.length!==route.positions.length)
   return reject('invalid_route_shape');
  let length=0,seams=0;
  for(let i=0;i<route.keys.length;i++){
   const node=network.graph.get(route.keys[i]);
   const point=route.positions[i];
   if(!node||!Array.isArray(node.world)||node.world.length!==2||
      !node.world.every(Number.isFinite)||!Array.isArray(point)||point.length!==2||
      !point.every(Number.isFinite)||Math.hypot(point[0]-node.world[0],point[1]-node.world[1])>1e-5)
    return reject('untrusted_waypoint');
   if(i===0)continue;
   const prev=network.graph.get(route.keys[i-1]);
   const edge=prev.edges.find(e=>e.to===route.keys[i]);
   if(!edge||!Number.isFinite(edge.length)||edge.length<0||
      !['painted-road','approved-seam'].includes(edge.kind))
    return reject('missing_approved_edge');
   const physical=Math.hypot(node.world[0]-prev.world[0],node.world[1]-prev.world[1]);
   if(Math.abs(physical-edge.length)>1e-5)
    return reject('edge_geometry_mismatch');
   if(node.id!==prev.id){
    if(edge.kind!=='approved-seam')return reject('unapproved_tile_crossing');
    seams++;
   }else if(edge.kind!=='painted-road')return reject('unexpected_seam_edge');
   length+=edge.length;
  }
  if(!Number.isFinite(route.distance)||route.distance<0||
     Math.abs(length-route.distance)>Math.max(1e-5,length*1e-9))
   return reject('distance_mismatch');
  if(route.seams!==seams)return reject('seam_count_mismatch');
  return {pass:true,distance:length,seams};
 }
 return {validateRoute};
});
