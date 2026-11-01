/* Source-bound, fail-closed wilderness movement. Not the V123 painted-road graph.
 * A pass requires TWO reviewed 32px-or-finer surface masks and source-bound seam evidence.
 * Corridor samples include army clearance, not just a thin centerline.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=="undefined"&&module.exports)module.exports=api;
 else root.COEAtlasOverland=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 "use strict";
 const COST=Object.freeze({meadow:1,forest:1.8,rock:3.2,scree:4.5,river:Infinity,cliff:Infinity,unknown:Infinity});
 const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
 const origin=c=>c.origin||c.nativeWorldOrigin;
 const isString=s=>typeof s==="string"&&s.trim().length>0;
 function inside(p,o,g){
  const x=p[0]-o[0],y=p[1]-o[1];
  if(x<0||x>g.width||y<0||y>g.height)return false;
  const inset=y<g.corner?g.corner-y:y>g.height-g.corner?y-(g.height-g.corner):0;
  return x>=inset&&x<=g.width-inset;
 }
 function maskClass(mask,p,o){
  const lx=p[0]-o[0],ly=p[1]-o[1];
  if(lx<0||ly<0||lx>mask.columns*mask.cellSize||ly>mask.rows*mask.cellSize)return "unknown";
  const x=Math.min(mask.columns-1,Math.floor(lx/mask.cellSize));
  const y=Math.min(mask.rows-1,Math.floor(ly/mask.cellSize));
  return mask.classes[y*mask.columns+x]||"unknown";
 }
 function sourcesFor(link,from,to){
  const entries=Array.isArray(link.sourceImages)?link.sourceImages:[];
  const result={};
  for(const c of [from,to]){
   const matches=entries.filter(e=>e.cell===c.id&&e.path===c.art&&/^[a-f0-9]{40}$/.test(e.gitBlobSha||""));
   if(matches.length!==1)return null;
   result[c.id]=matches[0].gitBlobSha;
  }
  return result;
 }
 function validEvidence(e){
  return e&&e.sourcePixelReview===true&&isString(e.evidencePath)&&isString(e.reviewer)&&
   /^\d{4}-\d{2}-\d{2}$/.test(e.reviewedOn||"");
 }
 function inspect(link,manifest,masks){
  masks=masks||{};
  const reasons=[],g=manifest.geometry;
  const cells=[...(manifest.cells||[]),...(manifest.artCandidates||[])];
  const from=cells.find(c=>c.id===link.from),to=cells.find(c=>c.id===link.to);
  if(!from||!to||!origin(from)||!origin(to))
   return Object.freeze({passable:false,reasons:["unknown_or_unplaced_cell"],points:[],cost:null});
  const a=origin(from),b=origin(to),p=link.waypoints;
  if(!Array.isArray(p)||p.length!==3||p.some(q=>!Array.isArray(q)||q.length!==2||q.some(v=>!Number.isFinite(v))))
   return Object.freeze({passable:false,reasons:["invalid_waypoints"],points:[],cost:null});
  const clearance=link.clearanceRadiusPx===undefined?16:link.clearanceRadiusPx;
  if(!Number.isInteger(clearance)||clearance<12||clearance>48)reasons.push("invalid_clearance_radius");
  if(b[0]!==a[0]+g.width||b[1]!==a[1]||
     p[1][0]!==b[0]||p[1][1]<a[1]+g.corner||p[1][1]>a[1]+g.height-g.corner||
     !inside(p[0],a,g)||!inside(p[2],b,g))
   reasons.push("invalid_shared_edge_geometry");
  if(link.mode!=="overland"||link.strategicRoad!==false||link.historicallyVerified!==false)
   reasons.push("not_a_wilderness_link");
  const sourceShas=sourcesFor(link,from,to);
  if(!sourceShas)reasons.push("source_art_identity_mismatch");
  const e=link.seamEvidence;
  if(link.seamVerified!==true||!e||e.groundContinuity!==true||e.noUnverifiedCrossing!==true||
     e.edgeY!==p[1][1]||!validEvidence(e)||
     !sourceShas||[from,to].some(c=>e.sourceBlobShas?.[c.id]!==sourceShas[c.id]))
   reasons.push("uncertified_cross_tile_seam");
  for(const c of [from,to]){
   const m=masks[c.id];
   if(!m){reasons.push("missing_surface_mask:"+c.id);continue;}
   if(m.reviewed!==true||!validEvidence(m.evidence)||m.sourceArt!==c.art||
      !sourceShas||m.sourceBlobSha!==sourceShas[c.id]||
      !Number.isInteger(m.cellSize)||m.cellSize<8||m.cellSize>32||
      m.columns!==Math.ceil(g.width/m.cellSize)||m.rows!==Math.ceil(g.height/m.cellSize)||
      !Array.isArray(m.classes)||m.classes.length!==m.columns*m.rows||
      m.classes.some(k=>!Object.hasOwn(COST,k)))
    reasons.push("uncertified_surface_mask:"+c.id);
  }
  if(reasons.length)return Object.freeze({passable:false,reasons,points:[],cost:null});
  let cost=0;
  for(let segment=0;segment<2;segment++){
   const c=segment===0?from:to,m=masks[c.id],o=origin(c);
   const first=p[segment],last=p[segment+1],len=dist(first,last),steps=Math.ceil(len/8);
   if(!steps){reasons.push("zero_length_segment");break;}
   const perpendicular=[-(last[1]-first[1])/len,(last[0]-first[0])/len];
   for(let k=0;k<=steps;k++){
    const t=k/steps,point=[first[0]+(last[0]-first[0])*t,first[1]+(last[1]-first[1])*t];
    let worst=1;
    for(const offset of [-clearance,0,clearance]){
     // At the exact shared boundary, the other tile owns the outward half
     // of the footprint. Its edge and seam are independently inspected.
     if(segment===1&&k===0&&offset!==0)continue;
     const sample=[point[0]+perpendicular[0]*offset,point[1]+perpendicular[1]*offset];
     if(!inside(sample,o,g)){reasons.push("route_clearance_leaves_octagon:"+c.id);break;}
     const terrain=maskClass(m,sample,o),multiplier=COST[terrain];
     if(!Number.isFinite(multiplier)){reasons.push("impassable_or_unknown_terrain:"+c.id+":"+terrain);break;}
     worst=Math.max(worst,multiplier);
    }
    if(reasons.length)break;
    if(k)cost+=len/steps*worst;
   }
   if(reasons.length)break;
  }
  return Object.freeze({passable:reasons.length===0,reasons,
   points:reasons.length?[]:p.map(x=>x.slice()),
   cost:reasons.length?null:Math.round(cost*100)/100,mode:"overland",strategicRoad:false,
   clearanceRadiusPx:clearance});
 }
 return Object.freeze({inspect,terrainCosts:COST});
});