/* V118: one canonical east-bank cart-road extension for the existing painted
 * Brenner study. This is deliberately artist-authored FICTIONAL candidate
 * geometry, not a claim about surveyed 1780 roads or a finished adjacent cell.
 * Never let drawing and motion maintain separate waypoint arrays.
 */
(function(root){
"use strict";
const farBank=Object.freeze([699,799]);
const east=Object.freeze([[717,794],[737,783],[758,773],[781,769],[806,772],
 [830,769],[851,762],[870,751],[888,737],[901,721],
 [910,705],[914,691],[916,680],[922,670],[937,670],
 [947,681],[957,694],[974,704],[997,709],[1020,711],
 [1046,713],[1074,710],[1100,704]].map(p=>Object.freeze(p)));
const same=(a,b)=>a&&b&&a[0]===b[0]&&a[1]===b[1];
function extend(original){
 if(!Array.isArray(original)||!original.length||!same(original.at(-1),farBank))
   throw Error("V118 requires the verified candidate bridge endpoint at [699,799]");
 const out=original.map(p=>p.slice()).concat(east.map(p=>p.slice()));
 if(!same(out.at(-1),[1100,704]))throw Error("East boundary mismatch");
 for(let i=original.length;i<out.length;i++){
  const p=out[i],a=out[i-1];
  if(!p.every(Number.isFinite)||p.some((n,j)=>n<0||n>(j?842:1100))||
     Math.hypot(p[0]-a[0],p[1]-a[1])>34)
    throw Error("Invalid cart-road transition or map boundary");
 }
 return out;
}
function draw(ctx,project,graph){
 if(!graph||graph.kind!=="art-aligned-candidate"||graph.approvedForProduction!==false)
    throw Error("V118 accepts prototype graphs only");
 const path=graph.paths.bridge,at=path.findIndex(p=>same(p,farBank));
 if(at<2 || path.length-at!==east.length+1 ||
    east.some((p,i)=>!same(path[at+1+i],p)))
    throw Error("Road painting differs from army waypoints");
 const p=path.slice(at); // includes precisely the far-bank arrival point
 const z=project([0,0]),u=project([1,0]),v=project([0,1]);
 const scale=(Math.hypot(u[0]-z[0],u[1]-z[1])+Math.hypot(v[0]-z[0],v[1]-z[1]))/2;
 if(!Number.isFinite(scale)||scale<=0)throw Error("Invalid art scale");
 const line=(points,width,color)=>{
  ctx.beginPath();
  points.forEach((q,i)=>{const a=project(q);if(i)ctx.lineTo(...a);else ctx.moveTo(...a)});
  ctx.lineWidth=width*scale;ctx.strokeStyle=color;ctx.stroke();
 };
 const shift=dist=>p.map((a,i)=>{
  const lo=p[Math.max(0,i-1)],hi=p[Math.min(p.length-1,i+1)];
  const dx=hi[0]-lo[0],dy=hi[1]-lo[1],d=Math.hypot(dx,dy);
  return [a[0]-dy*dist/d,a[1]+dx*dist/d];
 });
 ctx.save();
 try{
  ctx.lineJoin="round";ctx.lineCap="round";ctx.globalAlpha=.54;
  // Compact preindustrial cartway: soil, narrow dusty center, two wheel ruts.
  line(p,6.5,"#514531");line(p,5.4,"#827252");
  line(p,4.3,"#b19b71");
  line(shift(-1.6),.36,"#675638");
  line(shift(1.6),.36,"#675638");
 }finally{ctx.restore()}
 return {sameRoute:true,endpoint:path.at(-1).slice(),paintedStart:farBank.slice()};
}
const api=Object.freeze({extend,draw,farBank,exit:east.at(-1),
  nextCellEntry:Object.freeze([0,704]),points:east});
if(typeof module==="object"&&module.exports)module.exports=api;
else root.CenturyV118East=api;
})(typeof globalThis!=="undefined"?globalThis:this);
