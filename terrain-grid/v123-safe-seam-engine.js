/* Experimental fail-closed seam adapter; not wired into the live campaign. */
(function(root,factory){
 const base=typeof module!=='undefined'&&module.exports?require('./v122-seam-engine.js'):root.V122Seam;
 const api=factory(base);
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 else root.V123SafeSeam=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(base){
 'use strict';
 function octagonInteriorsOverlap(a,b,epsilon=1.5){
  const polygons=[a,b].map(t=>base.octagon(t.width,t.height,t.corner||256)
   .map(p=>[p[0]+t.origin[0],p[1]+t.origin[1]]));
  for(const poly of polygons)for(let i=0;i<poly.length;i++){
   const p=poly[i],q=poly[(i+1)%poly.length];
   const dx=q[0]-p[0],dy=q[1]-p[1],len=Math.hypot(dx,dy);
   const nx=-dy/len,ny=dx/len;
   const projected=points=>points.map(v=>v[0]*nx+v[1]*ny);
   const u=projected(polygons[0]),v=projected(polygons[1]);
   const overlap=Math.min(Math.max(...u),Math.max(...v))-
                 Math.max(Math.min(...u),Math.min(...v));
   if(overlap<=epsilon)return false;
  }
  return true;
 }
 function buildNetwork(plan,epsilon=1.5){
  const tiles=new Map(plan.tiles.map(t=>[t.id,t]));
  const rejected=new Set();
  const links=plan.links.map((link,i)=>{
   const a=tiles.get(link.from.tile),b=tiles.get(link.to.tile);
   if(a&&b&&octagonInteriorsOverlap(a,b,epsilon)){
    rejected.add(i);
    return {...link,enabled:false};
   }
   return link;
  });
  const network=base.buildNetwork({...plan,links},epsilon);
  for(const i of rejected){
   const seam=network.seams[i];
   if(!seam.errors.includes('tile_interiors_overlap'))seam.errors.push('tile_interiors_overlap');
   seam.pass=false;
  }
  return network;
 }
 return {...base,buildNetwork,octagonInteriorsOverlap};
});
