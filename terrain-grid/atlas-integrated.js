/* Integrated Alpine atlas canvas. Actual game DOM, not an iframe.
 * V121 art and V123 graph are imported unchanged; V94 campaign/save untouched.
 * This remains a geographically fictional local study, not a production Europe map.
 */
(function(root){
"use strict";
const M="terrain-grid/atlas-cells.json";
const $=id=>document.getElementById(id);
const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const clone=p=>p.slice();
const layer=document.createElement("section");
layer.id="atlasIntegratedLayer";layer.hidden=true;layer.setAttribute("aria-label","Integrated Alpine atlas canvas");
layer.innerHTML='<header id="atlasBar"><strong>ALPINE ATLAS <small>approved art method · experimental gameplay layer</small></strong><div><button id="atlasWhole">Whole</button><button id="atlasWest">WEST</button><button id="atlasSouth">SOUTH</button><button id="atlasMinus">−</button><button id="atlasPlus">+</button><button id="atlasClose">Back</button></div></header><canvas id="atlasCanvas" aria-label="Three connected Alpine terrain octagons, touch roads to march"></canvas><footer id="atlasFooter"><span id="atlasStatus" role="status">Loading original artwork and fixed roads…</span><div><button id="atlasMarch">WEST → SOUTH</button><button id="atlasHalt">Halt</button><button id="atlasRoads">Road trace</button></div></footer>';
const style=document.createElement("style");style.textContent=`
#atlasIntegratedOpen{position:fixed;z-index:135;right:9px;bottom:max(11px,env(safe-area-inset-bottom));border:1px solid #d9ba78;border-radius:9px;background:#183a32ed;color:#f9e7bc;font:700 12px system-ui;padding:11px;min-height:44px}
#atlasIntegratedLayer{position:fixed;z-index:900;inset:0;background:#13251f;color:#f6e9cf;overflow:hidden}
#atlasIntegratedLayer[hidden]{display:none!important}
#atlasCanvas{position:absolute;inset:0;width:100%;height:100%;touch-action:none;display:block}
#atlasBar{position:absolute;z-index:2;top:0;left:0;right:0;display:flex;align-items:center;justify-content:space-between;gap:5px;padding:calc(5px + env(safe-area-inset-top)) 8px 6px;background:#10251edc;border-bottom:1px solid #7e7658}
#atlasBar strong{font:700 12px Georgia,serif;white-space:nowrap}#atlasBar small{display:block;font:9px system-ui;color:#ddcfb5}
#atlasBar div,#atlasFooter div{display:flex;gap:4px;flex-wrap:wrap}
#atlasIntegratedLayer button{min-height:34px;padding:5px 8px;border-radius:6px;background:#24473b;color:#f4e5c6;border:1px solid #ad9a72;font:700 11px system-ui}
#atlasFooter{position:absolute;z-index:2;bottom:0;left:0;right:0;display:flex;align-items:center;justify-content:space-between;gap:7px;padding:7px 8px calc(7px + env(safe-area-inset-bottom));background:#10251ee8;border-top:1px solid #9a8963}
#atlasStatus{font:11px/1.3 system-ui;max-width:48%}
@media(max-width:650px){#atlasBar{flex-wrap:wrap}#atlasBar strong{font-size:10px}#atlasBar small{display:none}#atlasIntegratedLayer button{font-size:10px;padding:5px 6px}#atlasFooter{align-items:flex-start;flex-direction:column}#atlasStatus{max-width:100%}}
`;
document.head.append(style);
const openButton=document.createElement("button");openButton.type="button";openButton.id="atlasIntegratedOpen";openButton.textContent="Integrated Alpine atlas";openButton.setAttribute("aria-controls",layer.id);
document.body.append(openButton,layer);
const canvas=$("atlasCanvas"),ctx=canvas.getContext("2d",{alpha:false});
let manifest=null,atlas=null,images={},segments=[],loaded=false,shown=false,debug=false;
let w=0,h=0,dpr=1,base=1,zoom=1.05,scale=1,center=[1810,950];
let unit=[275,550],path=[],moving=false,progress=0,travelLength=0,lastTime=0;
const pointers=new Map();let tap=null,prevPinch=null;
function status(s){$("atlasStatus").textContent=s;}
function worldToScreen(p){return [w/2+(p[0]-center[0])*scale,h/2+(p[1]-center[1])*scale];}
function screenToWorld(p){return [center[0]+(p[0]-w/2)/scale,center[1]+(p[1]-h/2)/scale];}
function fit(){
 const rect=canvas.getBoundingClientRect();w=rect.width||innerWidth;h=rect.height||innerHeight;
 dpr=Math.min(devicePixelRatio||1,2);canvas.width=Math.max(1,Math.round(w*dpr));canvas.height=Math.max(1,Math.round(h*dpr));
 base=Math.min(w/3072,h/2048);scale=base*zoom;draw();
}
function polygon(ctx,points){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();}
function worldPolygon(tile){
 const {width:W,height:H,corner:c}=manifest.geometry;
 return [[c,0],[W-c,0],[W,c],[W,H-c],[W-c,H],[c,H],[0,H-c],[0,c]].map(p=>[p[0]+tile.origin[0],p[1]+tile.origin[1]]);
}
function polyline(points,color,lineWidth){ctx.beginPath();points.forEach((p,i)=>{const q=worldToScreen(p);if(i)ctx.lineTo(q[0],q[1]);else ctx.moveTo(q[0],q[1]);});ctx.strokeStyle=color;ctx.lineWidth=lineWidth;ctx.lineCap="round";ctx.lineJoin="round";ctx.stroke();}
function draw(){
 if(!w||!h)return;
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle="#15271f";ctx.fillRect(0,0,w,h);
 if(!loaded)return;
 const diamond=manifest.decorativeInlays[0],src=images[diamond.sourceCell];
 ctx.save();polygon(ctx,diamond.polygon.map(worldToScreen));ctx.clip();
 const dest=worldToScreen([1280,768]);ctx.drawImage(src,...diamond.sourceRect,dest[0],dest[1],512*scale,512*scale);ctx.restore();
 for(const tile of manifest.cells){
  const image=images[tile.id],pos=worldToScreen(tile.origin),poly=worldPolygon(tile).map(worldToScreen);
  ctx.save();polygon(ctx,poly);ctx.clip();
  ctx.drawImage(image,pos[0],pos[1],1536*scale,1024*scale);ctx.restore();
  // Frames never paint over occupied WEST/MATREI or MATREI/SOUTH road-bearing edges.
  for(let i=0;i<poly.length;i++){
   const side=i===3?"east":i===5?"west":i===4?"south":i===0?"north":"corner";
   if((tile.id==="west"&&side==="east")||(tile.id==="matrei"&&["west","south"].includes(side))||(tile.id==="south"&&side==="north"))continue;
   const a=poly[i],b=poly[(i+1)%poly.length];ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.strokeStyle="#bca16b9c";ctx.lineWidth=1.2;ctx.stroke();
  }
 }
 if(debug)for(const tile of atlas.tiles){for(const road of Object.values(tile.roads))polyline(road.map(p=>[p[0]+tile.origin[0],p[1]+tile.origin[1]]),"#f9ce4ac9",2);}
 if(path.length>1)polyline(path,"#ffe2a9b9",2.8);
 const [x,y]=worldToScreen(unit);
 ctx.save();ctx.translate(x,y);ctx.fillStyle="#193a2a";ctx.strokeStyle="#f4d78e";ctx.lineWidth=2.2;ctx.beginPath();ctx.arc(0,0,13,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle="#fff1c3";ctx.font="bold 16px Georgia";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("⚔",0,0);ctx.restore();
}
function imageLoad(src){return new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(Error("Missing atlas art: "+src));img.src=src;});}
function collectSegments(network){
 const out=[],seen=new Set();
 for(const [key,node] of network.graph)for(const edge of node.edges){
  if(edge.kind!=="painted-road")continue;
  const pair=[key,edge.to].sort().join("|");if(seen.has(pair))continue;seen.add(pair);
  out.push({a:key,b:edge.to,p:node.world,q:network.graph.get(edge.to).world});
 }
 return out;
}
function project(point,segment){
 const dx=segment.q[0]-segment.p[0],dy=segment.q[1]-segment.p[1],len2=dx*dx+dy*dy;
 const t=clamp(len2?((point[0]-segment.p[0])*dx+(point[1]-segment.p[1])*dy)/len2:0,0,1);
 const p=[segment.p[0]+t*dx,segment.p[1]+t*dy];
 return {segment,point:p,distance:distance(point,p)};
}
function nearest(point){let best=null;for(const seg of segments){const hit=project(point,seg);if(!best||hit.distance<best.distance)best=hit;}return best;}
function clean(points){return points.filter((p,i)=>!i||distance(p,points[i-1])>0.00001);}
function length(points){return points.slice(1).reduce((n,p,i)=>n+distance(p,points[i]),0);}
function routeBetween(from,to){
 const a=nearest(from),b=nearest(to);if(!a||!b||a.distance>2||b.distance>2)return null;
 let result=null,best=Infinity;
 function consider(points){const cleanPoints=clean(points),cost=length(cleanPoints);if(cost<best){best=cost;result=cleanPoints;}}
 if(a.segment===b.segment)consider([a.point,b.point]);
 for(const start of [a.segment.a,a.segment.b])for(const end of [b.segment.a,b.segment.b]){
  const route=atlas.network.planRoute(start,end);if(route)consider([a.point,...route.positions,b.point]);
 }
 return result;
}
function sample(points,amount){let left=amount;for(let i=1;i<points.length;i++){const n=distance(points[i-1],points[i]);if(left<=n)return [points[i-1][0]+(points[i][0]-points[i-1][0])*left/n,points[i-1][1]+(points[i][1]-points[i-1][1])*left/n];left-=n;}return clone(points.at(-1));}
function startOrder(to){if(!loaded)return false;const next=routeBetween(unit,to);if(!next)return false;path=next;progress=0;travelLength=length(path);moving=travelLength>0.01;status(moving?"Marching on V123 road · tap another cartway to redirect":"Unit already at destination");draw();return true;}
function halt(){moving=false;path=[];progress=0;status("Halted · tap a painted road");draw();}
function frame(t){if(shown&&loaded&&moving&&lastTime){progress=Math.min(travelLength,progress+Math.min(.05,(t-lastTime)/1000)*155);unit=sample(path,progress);if(progress>=travelLength-.001){moving=false;status("Arrived · tap another cartway");}draw();}lastTime=t;requestAnimationFrame(frame);}
function tapRoad(point){const hit=nearest(point);if(!hit||hit.distance>Math.max(19,16/scale)){status("No road here · select a visible cartway");return false;}return startOrder(hit.point);}
function centerAt(x,y,z){center=[x,y];if(z!==undefined)zoom=clamp(z,.6,8);scale=base*zoom;draw();}
function open(){layer.hidden=false;openButton.hidden=true;shown=true;fit();if(!loaded)status("Loading fixed V121/V123 atlas assets…");}
function close(){shown=false;layer.hidden=true;openButton.hidden=false;openButton.focus();}
canvas.addEventListener("pointerdown",e=>{e.preventDefault();canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);if(pointers.size===1)tap=[e.clientX,e.clientY];if(pointers.size===2){const pts=[...pointers.values()];prevPinch=distance(pts[0],pts[1]);tap=null;}});
canvas.addEventListener("pointermove",e=>{
 if(!pointers.has(e.pointerId))return;const prev=pointers.get(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);
 const rect=canvas.getBoundingClientRect();
 if(pointers.size===2){const pts=[...pointers.values()],gap=distance(pts[0],pts[1]);const mid=[(pts[0][0]+pts[1][0])/2-rect.left,(pts[0][1]+pts[1][1])/2-rect.top];const anchor=screenToWorld(mid);
  if(prevPinch>2){zoom=clamp(zoom*gap/prevPinch,.6,8);scale=base*zoom;const shifted=screenToWorld(mid);center=[center[0]+anchor[0]-shifted[0],center[1]+anchor[1]-shifted[1]];}prevPinch=gap;draw();return;}
 if(tap&&distance(tap,[e.clientX,e.clientY])>9)tap=null;
 center=[center[0]-(e.clientX-prev[0])/scale,center[1]-(e.clientY-prev[1])/scale];draw();
});
function endPointer(e){if(!pointers.has(e.pointerId))return;const rect=canvas.getBoundingClientRect();if(pointers.size===1&&tap&&distance(tap,[e.clientX,e.clientY])<9)tapRoad(screenToWorld([e.clientX-rect.left,e.clientY-rect.top]));pointers.delete(e.pointerId);if(pointers.size<2)prevPinch=null;tap=null;draw();}
for(const event of ["pointerup","pointercancel","lostpointercapture"])canvas.addEventListener(event,endPointer);
$("atlasClose").onclick=close;openButton.onclick=open;
$("atlasWhole").onclick=()=>centerAt(1536,1024,.96);
$("atlasWest").onclick=()=>centerAt(1536,478,3.2);
$("atlasSouth").onclick=()=>centerAt(2002,1024,3.2);
$("atlasPlus").onclick=()=>centerAt(...center,zoom*1.3);
$("atlasMinus").onclick=()=>centerAt(...center,zoom/1.3);
$("atlasMarch").onclick=()=>startOrder([2806,1629]);
$("atlasHalt").onclick=halt;
$("atlasRoads").onclick=()=>{debug=!debug;draw();};
window.addEventListener("resize",()=>{if(shown)fit();});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&shown)close();});
const API={
 get loaded(){return loaded},get shown(){return shown},get nodes(){return atlas?.network.graph.size||0},
 get uniqueWorldNodes(){return atlas?new Set([...atlas.network.graph.values()].map(n=>n.world.join(","))).size:0},
 get seams(){return atlas?.network.seams||[]},get imageSizes(){return Object.fromEntries(Object.entries(images).map(([id,img])=>[id,[img.naturalWidth,img.naturalHeight]]));},
 get moving(){return moving},get position(){return clone(unit)},get route(){return path.map(clone)},
 get zoom(){return zoom},get center(){return clone(center)},get manifest(){return manifest},
 get graph(){return atlas?.network},get sourceRoadSegments(){return segments.length},
 get campaignOrdersUnchanged(){return true},
 open,close,halt,centerAt,startMarch:()=>startOrder([2806,1629]),finishMarch:()=>{if(!path.length)return clone(unit);progress=travelLength;unit=clone(path.at(-1));moving=false;draw();return clone(unit);},
 routeTo:p=>routeBetween(unit,p),tapWorld:tapRoad,screenFor:worldToScreen,setZoom:z=>centerAt(...center,z)
};
root.COEAtlas=Object.freeze(API);
(async()=>{
 const response=await fetch(M);if(!response.ok)throw Error("Atlas manifest HTTP "+response.status);
 manifest=await response.json();if(manifest.schema!=="coe-atlas-cells/v1"||manifest.cells.length!==3)throw Error("Unexpected atlas manifest");
 atlas=root.V123Atlas.create(manifest.centerRoads,{experimentalSeams:true});
 if(atlas.network.graph.size!==100||atlas.network.seams.length!==2||atlas.network.seams.some(s=>!s.pass||s.endpointGapPx!==0))throw Error("Protected V123 road seam drift");
 segments=collectSegments(atlas.network);
 const loadedImages=await Promise.all(manifest.cells.map(async cell=>[cell.id,await imageLoad(cell.art)]));
 images=Object.fromEntries(loadedImages);
 if(Object.values(images).some(img=>img.naturalWidth!==1536||img.naturalHeight!==1024))throw Error("Original art dimension mismatch");
 loaded=true;status("WEST · MATREI · SOUTH connected · tap a cartway");if(shown)fit();
})().catch(error=>{status("Atlas load blocked: "+error.message);root.COEAtlasLoadError=error.message;});
requestAnimationFrame(frame);
})(window);
