/* Fail-closed wilderness movement. This is NOT the V123 strategic painted-road graph.
 * A candidate link needs reviewed surface masks on BOTH tiles and a reviewed seam.
 * Unknown terrain, water and cliffs are never silently treated as meadow.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=="undefined"&&module.exports)module.exports=api;
 else root.COEAtlasOverland=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 "use strict";
 const COST=Object.freeze({meadow:1,forest:1.8,rock:3.2,scree:4.5,river:Infinity,cliff:Infinity,unknown:Infinity});
 const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
 const origin=(c)=>c.origin||c.nativeWorldOrigin;
 function inside(p,o,g){
  const x=p[0]-o[0],y=p[1]-o[1];
  if(x<0||x>g.width||y<0||y>g.height)return false;
  const inset=y<g.corner?g.corner-y:y>g.height-g.corner?y-(g.height-g.corner):0;
  return x>=inset&&x<=g.width-inset;
 }
 function maskClass(mask,p,o){
  const x=Math.min(mask.columns-1,Math.floor((p[0]-o[0])/mask.cellSize));
  const y=Math.min(mask.rows-1,Math.floor((p[1]-o[1])/mask.cellSize));
  if(x<0||y<0||x>=mask.columns||y>=mask.rows)return "unknown";
  return mask.classes[y*mask.columns+x]||"unknown";
 }
 function inspect(link,manifest,masks){
  masks=masks||{};
  const reasons=[],g=manifest.geometry;
  const cells=[...(manifest.cells||[]),...(manifest.artCandidates||[])];
  const from=cells.find(c=>c.id===link.from),to=cells.find(c=>c.id===link.to);
  if(!from||!to||!origin(from)||!origin(to))return Object.freeze({passable:false,reasons:["unknown_or_unplaced_cell"],points:[],cost:null});
  const a=origin(from),b=origin(to),p=link.waypoints;
  if(!Array.isArray(p)||p.length!==3||p.some(q=>!Array.isArray(q)||q.length!==2||q.some(v=>!Number.isFinite(v))))
   return Object.freeze({passable:false,reasons:["invalid_waypoints"],points:[],cost:null});
  if(b[0]!==a[0]+g.width||b[1]!==a[1]||
     p[1][0]!==b[0]||p[1][1]<a[1]+g.corner||p[1][1]>a[1]+g.height-g.corner||
     !inside(p[0],a,g)||!inside(p[2],b,g))reasons.push("invalid_shared_edge_geometry");
  if(link.mode!=="overland"||link.strategicRoad!==false||link.historicallyVerified!==false)
   reasons.push("not_a_wilderness_link");
  if(link.seamVerified!==true||!link.seamEvidence)reasons.push("uncertified_cross_tile_seam");
  for(const c of [from,to]){
   const m=masks[c.id];
   if(!m){reasons.push("missing_surface_mask:"+c.id);continue;}
   if(m.reviewed!==true||!m.evidence||m.sourceArt!==c.art||
      !Number.isInteger(m.cellSize)||m.cellSize<8||
      m.columns!==Math.ceil(g.width/m.cellSize)||m.rows!==Math.ceil(g.height/m.cellSize)||
      !Array.isArray(m.classes)||m.classes.length!==m.columns*m.rows)
     reasons.push("uncertified_surface_mask:"+c.id);
  }
  if(reasons.length)return Object.freeze({passable:false,reasons,points:[],cost:null});
  let cost=0;
  for(let segment=0;segment<2;segment++){
   const c=segment===0?from:to,m=masks[c.id],o=origin(c);
   const first=p[segment],last=p[segment+1],len=dist(first,last),steps=Math.ceil(len/24);
   if(!steps){reasons.push("zero_length_segment");break;}
   for(let k=0;k<=steps;k++){
    const t=k/steps,point=[first[0]+(last[0]-first[0])*t,first[1]+(last[1]-first[1])*t];
    if(!inside(point,o,g)){reasons.push("route_leaves_octagon:"+c.id);break;}
    const terrain=maskClass(m,point,o),multiplier=COST[terrain];
    if(!Number.isFinite(multiplier)){reasons.push("impassable_or_unknown_terrain:"+c.id+":"+terrain);break;}
    if(k)cost+=len/steps*multiplier;
   }
   if(reasons.length)break;
  }
  return Object.freeze({passable:reasons.length===0,reasons,points:reasons.length?[]:p.map(x=>x.slice()),cost:reasons.length?null:Math.round(cost*100)/100,mode:"overland",strategicRoad:false});
 }
 return Object.freeze({inspect,terrainCosts:COST});
});