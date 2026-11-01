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
// iOS Safari recovery: keep the new review-only ridge visible as an ordinary
// decoded DOM image even if WebKit loses the canvas backing store. The image
// never receives touches, road orders, ownership, or campaign state.
const ridgeDOM=document.createElement("img");
ridgeDOM.id="atlasRidgeDomFallback";
ridgeDOM.alt="Unapproved original Alpine east ridge landscape";
ridgeDOM.setAttribute("aria-hidden","true");
ridgeDOM.decoding="async";
ridgeDOM.style.cssText="position:absolute;z-index:1;pointer-events:none;display:none;max-width:none;object-fit:fill;clip-path:polygon(16.6667% 0%,83.3333% 0%,100% 25%,100% 75%,83.3333% 100%,16.6667% 100%,0% 75%,0% 25%)";
layer.appendChild(ridgeDOM);
// Safari may decode the <img> after the first canvas frame; schedule a fresh
// visible frame when the real pixels become available, without changing art.
ridgeDOM.addEventListener("load",()=>{if(shown)requestAnimationFrame(draw);});
let ridgeEmergency=false,ridgeFallbackTried=false;
ridgeDOM.addEventListener("error",()=>{
 if(!ridgeFallbackTried){
  ridgeFallbackTried=true;
  const grade=new URLSearchParams(root.location.search).get("ridgeGrade")==="1";
  ridgeDOM.src=grade
    ?"https://raw.githubusercontent.com/wayfinderandco0-cell/century-of-empires/0e0ba14df7bc44d5492f460fa4d616c552644957/terrain-grid/v267-original-art-batch-01/matrei-east-ridge-graded.webp"
    :"https://raw.githubusercontent.com/wayfinderandco0-cell/century-of-empires/9e0e11cb2897cce91461681bfe0acf1a420034a5/terrain-grid/v267-original-art-batch-01/matrei-east-ridge.webp";
 }else if(ridgeEmergency)status("Ridge artwork unavailable from both image sources · use Approved three");
});
let manifest=null,atlas=null,images={},matreiRegistered=null,segments=[],loaded=false,shown=false,debug=false;
let w=0,h=0,dpr=1,base=1,zoom=1.05,scale=1,center=[1810,950];
let photoMode=false,photoStream=null,photoCamera=null;
// Opt-in source-layered scenic art. Never changes the protected V123 road graph.
let neighborPilotCells=[],neighborPilotImages={},neighborPilotInlays=[],neighborPilotShown=false,neighborPilotCamera=null,neighborPilotStream=null,eastBorderOverlay=null;
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
function syncRidgeDOM(){
 const tile=neighborPilotShown&&neighborPilotCells.find(c=>c.id==="matrei-east-ridge");
 if(!tile||!neighborPilotImages[tile.id]){
  if(!ridgeEmergency){ridgeDOM.style.display="none";return;}
  // The direct image must remain visible even if baseline V121 decoding,
  // canvas getImageData, or the neighbor manifest fails on physical Safari.
  const maxWidth=Math.max(180,w-24),maxHeight=Math.max(180,h-185);
  const width=Math.min(maxWidth,maxHeight*1.5),height=width/1.5;
  ridgeDOM.style.left=(w-width)/2+"px";
  ridgeDOM.style.top=(h-height)/2+"px";
  ridgeDOM.style.width=width+"px";ridgeDOM.style.height=height+"px";
  ridgeDOM.style.display="block";
  return;
 }
 if(ridgeDOM.getAttribute("src")!==neighborPilotImages[tile.id].src)
   ridgeDOM.src=neighborPilotImages[tile.id].src;
 const pos=worldToScreen(tile.origin);
 ridgeDOM.style.left=pos[0]+"px";ridgeDOM.style.top=pos[1]+"px";
 ridgeDOM.style.width=(1536*scale)+"px";ridgeDOM.style.height=(1024*scale)+"px";
 ridgeDOM.style.display="block";
}
function draw(){
 if(!w||!h)return;
 syncRidgeDOM();
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle="#15271f";ctx.fillRect(0,0,w,h);
 if(photoMode){
  if(photoStream)photoStream.draw(ctx,worldToScreen,scale,w,h);
  return;
 }
 if(!loaded)return;
 // Load only currently visible experimental artwork; the three protected
 // V123 images are always retained independently of this bounded cache.
 if(neighborPilotShown&&neighborPilotStream&&scale>0){
  neighborPilotStream.update({
   minX:center[0]-w/(2*scale),maxX:center[0]+w/(2*scale),
   minY:center[1]-h/(2*scale),maxY:center[1]+h/(2*scale)
  });
 }
 // Non-playable scenic diamonds have no routes, ownership or army hit areas.
 // Fill their real world-space polygons BEFORE drawing the adjacent octagons.
 if(neighborPilotShown)for(const infill of neighborPilotInlays){
  const img=neighborPilotImages[infill.sourceCell];if(!img)continue;
  const pts=infill.polygon.map(worldToScreen);
  const xs=infill.polygon.map(p=>p[0]),ys=infill.polygon.map(p=>p[1]);
  const left=Math.min(...xs),top=Math.min(...ys);
  const right=Math.max(...xs),bottom=Math.max(...ys);
  const pos=worldToScreen([left,top]);
  const [sx,sy,sw,sh]=infill.sourceRect;
  ctx.save();polygon(ctx,pts);ctx.clip();
  ctx.drawImage(img,sx,sy,sw,sh,pos[0],pos[1],(right-left)*scale,(bottom-top)*scale);
  ctx.restore();
 }
 // Draw only composed original neighbor candidates, under immutable approved art.
 if(neighborPilotShown)for(const tile of neighborPilotCells){
  const img=neighborPilotImages[tile.id];if(!img)continue;
  const pos=worldToScreen(tile.origin),poly=worldPolygon(tile).map(worldToScreen);
  ctx.save();polygon(ctx,poly);ctx.clip();
  ctx.drawImage(img,pos[0],pos[1],1536*scale,1024*scale);ctx.restore();
 }
 const diamond=manifest.decorativeInlays[0],src=images[diamond.sourceCell];
 ctx.save();polygon(ctx,diamond.polygon.map(worldToScreen));ctx.clip();
 const dest=worldToScreen([1280,768]);ctx.drawImage(src,...diamond.sourceRect,dest[0],dest[1],512*scale,512*scale);ctx.restore();
 for(const tile of manifest.cells){
  const image=tile.id==="matrei"&&matreiRegistered?matreiRegistered:images[tile.id],pos=worldToScreen(tile.origin),poly=worldPolygon(tile).map(worldToScreen);
  ctx.save();polygon(ctx,poly);ctx.clip();
  ctx.drawImage(image,pos[0],pos[1],1536*scale,1024*scale);ctx.restore();
  // Frames never paint over occupied WEST/MATREI or MATREI/SOUTH road-bearing edges.
  for(let i=0;i<poly.length;i++){
   const side=i===3?"east":i===5?"west":i===4?"south":i===0?"north":"corner";
   if((tile.id==="west"&&side==="east")||(tile.id==="matrei"&&["west","south"].includes(side))||(tile.id==="south"&&side==="north"))continue;
   const a=poly[i],b=poly[(i+1)%poly.length];ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.strokeStyle="#bca16b9c";ctx.lineWidth=1.2;ctx.stroke();
  }
 }
 // Experimental only: reversible Matrei east-edge display overlay. Never mutates V121/V267 source.
 if(neighborPilotShown&&eastBorderOverlay){const pos=worldToScreen([1536,0]);ctx.drawImage(eastBorderOverlay,pos[0],pos[1],1536*scale,1024*scale);}
 if(debug)for(const tile of atlas.tiles){for(const road of Object.values(tile.roads))polyline(road.map(p=>[p[0]+tile.origin[0],p[1]+tile.origin[1]]),"#f9ce4ac9",2);}
 if(path.length>1)polyline(path,"#ffe2a9b9",2.8);
 const [x,y]=worldToScreen(unit);
 ctx.save();ctx.translate(x,y);ctx.fillStyle="#193a2a";ctx.strokeStyle="#f4d78e";ctx.lineWidth=2.2;ctx.beginPath();ctx.arc(0,0,13,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle="#fff1c3";ctx.font="bold 16px Georgia";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("⚔",0,0);ctx.restore();
}
function imageLoad(src,timeoutMs=25000){return new Promise((resolve,reject)=>{
 const img=new Image();let done=false;
 const timer=setTimeout(()=>finish(Error("Atlas art timed out: "+src)),timeoutMs);
 function finish(error){if(done)return;done=true;clearTimeout(timer);img.onload=null;img.onerror=null;if(error)reject(error);else resolve(img);}
 img.crossOrigin="anonymous";
 img.onload=()=>finish(null);
 img.onerror=()=>finish(Error("Missing atlas art: "+src));
 img.src=src;
});}
/* Exact approved V267 Matrei display registration (source:
 * scripts/v267_unified_native_landscapes.py:matrei_display).
 * The immutable V121 WebP remains byte-for-byte unchanged on disk. A
 * once-only offscreen resampling makes the photographic cartway touch the
 * V123 WEST and SOUTH borders, instead of exposing V121's black photo frame.
 * This is NOT a global WEST/SOUTH warp and does not alter any road nodes.
 */
function registerMatrei(original){
 const W=1536,H=1024;
 const src=document.createElement("canvas");src.width=W;src.height=H;
 const sc=src.getContext("2d",{willReadFrequently:true});sc.drawImage(original,0,0);
 const pixels=sc.getImageData(0,0,W,H).data;
 const dst=document.createElement("canvas");dst.width=W;dst.height=H;
 const dc=dst.getContext("2d"),frame=dc.createImageData(W,H),out=frame.data;
 const smooth=v=>{v=clamp(v,0,1);return v*v*(3-2*v);};
 const xWest=Float32Array.from({length:W},(_,x)=>Math.exp(-.5*((x-240)/400)**2));
 const xSouth=Float32Array.from({length:W},(_,x)=>Math.exp(-.5*((x-466)/105)**2));
 for(let y=0;y<H;y++){
  const t=smooth((y-845)/179),sy0=10+y*(953/H)-26*t;
  const sl=sy0<286?385-(sy0-10)*(295/276):sy0>674?90+(sy0-674)*(295/289):90;
  const tl=y<256?256-y:y>768?y-768:0,tr=W-tl;
  const b=smooth((y-700)/324),wy=26*Math.exp(-.5*((y-505)/110)**2);
  for(let x=tl;x<tr;x++){
   const sx=clamp(sl+(x-tl)*(W-2*sl)/(tr-tl)-55*b*xSouth[x],0,W-1.001);
   const sy=clamp(sy0+wy*xWest[x],0,H-1.001);
   const x0=Math.floor(sx),y0=Math.floor(sy),fx=sx-x0,fy=sy-y0;
   const a=(y0*W+x0)*4,c=a+4,d=a+W*4,e=d+4,idx=(y*W+x)*4;
   for(let k=0;k<3;k++)out[idx+k]=Math.round(
    (1-fy)*((1-fx)*pixels[a+k]+fx*pixels[c+k])+
    fy*((1-fx)*pixels[d+k]+fx*pixels[e+k]));
   out[idx+3]=255;
  }
 }
 dc.putImageData(frame,0,0);
 return dst;
}
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
function startOrder(to){if(photoMode||neighborPilotShown){status("Unapproved scenic candidates are NOT road-connected or playable");return false;}if(!loaded)return false;const next=routeBetween(unit,to);if(!next)return false;path=next;progress=0;travelLength=length(path);moving=travelLength>0.01;status(moving?"Marching on V123 road · tap another cartway to redirect":"Unit already at destination");draw();return true;}
function halt(){moving=false;path=[];progress=0;status("Halted · tap a painted road");draw();}
function frame(t){if(shown&&loaded&&moving&&lastTime){progress=Math.min(travelLength,progress+Math.min(.05,(t-lastTime)/1000)*155);unit=sample(path,progress);if(progress>=travelLength-.001){moving=false;status("Arrived · tap another cartway");}draw();}lastTime=t;requestAnimationFrame(frame);}
function tapRoad(point){if(!loaded){status("Atlas artwork has not loaded; the canvas cannot issue orders");return false;}if(photoMode||neighborPilotShown)return false;const hit=nearest(point);if(!hit||hit.distance>Math.max(19,16/scale)){status("No road here · select a visible cartway");return false;}return startOrder(hit.point);}
function centerAt(x,y,z){center=[x,y];if(z!==undefined)zoom=clamp(z,(photoMode||neighborPilotShown)?.15:.6,8);scale=base*zoom;draw();}
function open(){layer.hidden=false;openButton.hidden=true;shown=true;fit();if(!loaded)status("Loading fixed V121/V123 atlas assets…");}
function close(){shown=false;ridgeEmergency=false;ridgeDOM.style.display="none";layer.hidden=true;openButton.hidden=false;openButton.focus();}
canvas.addEventListener("pointerdown",e=>{e.preventDefault();canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);if(pointers.size===1)tap=[e.clientX,e.clientY];if(pointers.size===2){const pts=[...pointers.values()];prevPinch=distance(pts[0],pts[1]);tap=null;}});
canvas.addEventListener("pointermove",e=>{
 if(!pointers.has(e.pointerId))return;const prev=pointers.get(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);
 const rect=canvas.getBoundingClientRect();
 if(pointers.size===2){const pts=[...pointers.values()],gap=distance(pts[0],pts[1]);const mid=[(pts[0][0]+pts[1][0])/2-rect.left,(pts[0][1]+pts[1][1])/2-rect.top];const anchor=screenToWorld(mid);
  if(prevPinch>2){zoom=clamp(zoom*gap/prevPinch,(photoMode||neighborPilotShown)?.15:.6,8);scale=base*zoom;const shifted=screenToWorld(mid);center=[center[0]+anchor[0]-shifted[0],center[1]+anchor[1]-shifted[1]];}prevPinch=gap;draw();return;}
 if(tap&&distance(tap,[e.clientX,e.clientY])>9)tap=null;
 center=[center[0]-(e.clientX-prev[0])/scale,center[1]-(e.clientY-prev[1])/scale];draw();
});
function endPointer(e){if(!pointers.has(e.pointerId))return;const rect=canvas.getBoundingClientRect();if(pointers.size===1&&tap&&distance(tap,[e.clientX,e.clientY])<9)tapRoad(screenToWorld([e.clientX-rect.left,e.clientY-rect.top]));pointers.delete(e.pointerId);if(pointers.size<2)prevPinch=null;tap=null;draw();}
for(const event of ["pointerup","pointercancel","lostpointercapture"])canvas.addEventListener(event,endPointer);
$("atlasClose").onclick=close;openButton.onclick=open;
$("atlasWhole").onclick=()=>{
 if(neighborPilotShown&&neighborPilotCells.length){
  const all=[...manifest.cells,...neighborPilotCells];
  const xs=all.map(c=>c.origin[0]),ys=all.map(c=>c.origin[1]);
  const left=Math.min(...xs),right=Math.max(...xs)+1536,top=Math.min(...ys),bottom=Math.max(...ys)+1024;
  const fit=Math.min(Math.max(100,w-24)/(right-left),Math.max(100,h-155)/(bottom-top))/base;
  centerAt((left+right)/2,(top+bottom)/2,Math.max(.15,fit));
 }else if(photoMode&&photoStream?.cells.length){
  // Fit the entire 4x2 or larger photographic block inside an actual iPhone
  // viewport. The previous hard-coded .7 clipped both outer columns on
  // 390px Safari; keep V123's original minimum zoom unchanged outside photo mode.
  const xs=photoStream.cells.map(c=>c.origin[0]),ys=photoStream.cells.map(c=>c.origin[1]);
  const left=Math.min(...xs),right=Math.max(...xs)+1536,top=Math.min(...ys),bottom=Math.max(...ys)+1024;
  const availableW=Math.max(100,w-24),availableH=Math.max(100,h-155);
  const fitted=Math.min(availableW/(right-left),availableH/(bottom-top))/base;
  centerAt((left+right)/2,(top+bottom)/2,fitted);
 }else centerAt(1536,1024,.96);
};
$("atlasWest").onclick=()=>centerAt(1536,478,3.2);
$("atlasSouth").onclick=()=>centerAt(2002,1024,3.2);
$("atlasPlus").onclick=()=>centerAt(...center,zoom*1.3);
$("atlasMinus").onclick=()=>centerAt(...center,zoom/1.3);
$("atlasMarch").onclick=()=>startOrder([2806,1629]);
$("atlasHalt").onclick=halt;
$("atlasRoads").onclick=()=>{if(!photoMode){debug=!debug;draw();}};
/* Opt-in source photography is displayed on the SAME native game canvas.
 * No route nodes or conquest towns are fabricated for unreviewed cells.
 * The three approved Alpine octagons and their V123 army stay intact.
 */
const studyParams=new URLSearchParams(root.location.search);
// Original scene expansion is a review-only opt-in; no invented road nodes.
const pilotButton=document.createElement("button");
pilotButton.id="atlasOriginalNeighbors";pilotButton.type="button";
const secondEuropeanBatch=studyParams.get("originalArtPilot")==="2";
const focusedEastPilot=studyParams.get("originalArtPilot")==="east";
const focusedV267NewPilot=studyParams.get("originalArtPilot")==="v267-new";
const ridgeGradePilot=focusedV267NewPilot&&studyParams.get("ridgeGrade")==="1";
const ridgeV2Pilot=focusedV267NewPilot&&studyParams.get("ridgeGrade")==="v2";
const ridgeV6Pilot=focusedV267NewPilot&&studyParams.get("ridgeGrade")==="v6";
const ridgeV7Pilot=focusedV267NewPilot&&studyParams.get("ridgeGrade")==="v7";
const ridgeV8Pilot=focusedV267NewPilot&&studyParams.get("ridgeGrade")==="v8";
const ridgeV2Path="terrain-grid/v267-original-art-batch-01/matrei-east-ridge-edge-v2.webp";
const ridgeV6Path="terrain-grid/v267-original-art-batch-01/matrei-east-riparian-v6-source-road.webp";
const ridgeV7Path="terrain-grid/v267-original-art-batch-01/matrei-east-riparian-v7-grounded-road.webp";
const ridgeV7Overlay="terrain-grid/v267-original-art-batch-01/matrei-east-v7-matrei-display-overlay.png";
const ridgeV8Path="terrain-grid/v267-original-art-batch-01/matrei-east-riparian-v8-narrow-dirt.webp";
const ridgeV8Overlay="terrain-grid/v267-original-art-batch-01/matrei-east-v8-matrei-display-overlay.png";
const ridgeV2Overlay="terrain-grid/v267-original-art-batch-01/matrei-east-border-display-overlay.webp";
const ridgeGradePath="terrain-grid/v267-original-art-batch-01/matrei-east-ridge-graded.webp";
pilotButton.textContent=ridgeV8Pilot?"EAST-01 V8 narrow dirt · QA only":ridgeV7Pilot?"EAST-01 V7 cleared road · QA only":ridgeV6Pilot?"EAST-01 V6 road · QA only":ridgeV2Pilot?"Edge-conditioned V2":ridgeGradePilot?"Graded ridge QA":focusedV267NewPilot?"New V267 ridge":focusedEastPilot?"Matrei east · new art":secondEuropeanBatch?"16 scenic studies":"Original neighbors";
pilotButton.hidden=!studyParams.has("originalArtPilot");
$("atlasBar").querySelector("div").appendChild(pilotButton);
if(focusedV267NewPilot){
 // An independent <img> review remains available even if iOS drops the canvas.
 const direct=document.createElement("a");
 direct.href="v267-ridge-ios-direct-review.html";
 direct.textContent="Direct ridge image";
 direct.setAttribute("aria-label","Open east ridge artwork without canvas");
 direct.style.cssText="display:inline-flex;align-items:center;min-height:44px;padding:7px 10px;border:1px solid #ad9a72;border-radius:7px;background:#24473b;color:#f4e5c6;text-decoration:none;font:700 11px system-ui";
 $("atlasBar").querySelector("div").appendChild(direct);
}
pilotButton.onclick=async()=>{
 if(neighborPilotShown){neighborPilotShown=false;ridgeEmergency=false;eastBorderOverlay=null;
  for(const id of ["atlasMarch","atlasHalt","atlasRoads"]){$(id).hidden=false;$(id).disabled=false;}
  if(neighborPilotCamera){center=neighborPilotCamera.center;zoom=neighborPilotCamera.zoom;scale=base*zoom;}
  status("Protected WEST / MATREI / SOUTH roads restored");draw();return;
 }
 try{
  if(!neighborPilotCells.length){
   status(focusedV267NewPilot?"Loading one new ORIGINAL three-dimensional Alpine landscape…":focusedEastPilot?"Loading ONE new Matrei east source-backed scene…":secondEuropeanBatch?"Loading sixteen distinct European scenic studies (no new roads)…":"Loading eight original scenic candidates (no new roads)…");
   const manifests=[focusedV267NewPilot?"terrain-grid/v267-original-art-batch-01/batch.json":"terrain-grid/v267-neighbor-original-art/batch.json"];
   if(secondEuropeanBatch)manifests.push("terrain-grid/v267-europe-neighbor-b/batch.json");
   if(!root.COEV267ArtContract)throw Error("Original-art validator missing");
   const batches=[];
   for(const url of manifests){
    const response=await fetch(url);
    if(!response.ok)throw Error("Neighbor manifest HTTP "+response.status+" for "+url);
    const batch=await response.json();
    root.COEV267ArtContract.validateBatch(batch,manifest);
    batches.push(batch);
   }
   // The focused review loads only the new source-grounded cell, not 16
   // rejected neighbors. Validate the full manifest first, then filter.
   const all=batches.flatMap(batch=>batch.cells).filter(c=>c.art&&(!focusedEastPilot||c.id==="east-matrei")&&(!focusedV267NewPilot||c.id==="matrei-east-ridge"));
   // Grade is opt-in and cannot change the immutable approved 3-cell manifest.
   // The original east ridge remains the default until independently reviewed.
   if(ridgeGradePilot&&all.length===1)all[0]={...all[0],art:ridgeGradePath};
   if(ridgeV6Pilot&&all.length===1)all[0]={...all[0],art:ridgeV6Path};
   if(ridgeV7Pilot&&all.length===1){
    all[0]={...all[0],art:ridgeV7Path};
    eastBorderOverlay=await imageLoad(ridgeV7Overlay,20000);
    if(eastBorderOverlay.decode)await eastBorderOverlay.decode().catch(()=>{});
   }
   if(ridgeV8Pilot&&all.length===1){
    all[0]={...all[0],art:ridgeV8Path};
    eastBorderOverlay=await imageLoad(ridgeV8Overlay,20000);
    if(eastBorderOverlay.decode)await eastBorderOverlay.decode().catch(()=>{});
   }
   if(ridgeV2Pilot&&all.length===1){
    all[0]={...all[0],art:ridgeV2Path};
    eastBorderOverlay=await imageLoad(ridgeV2Overlay,20000);
    if(eastBorderOverlay.decode)await eastBorderOverlay.decode().catch(()=>{});
   }
   if((focusedEastPilot||focusedV267NewPilot)&&(all.length!==1||!all[0].art))throw Error("Missing focused Matrei east scene");
   if(new Set(all.map(c=>c.id)).size!==all.length||
      new Set(all.map(c=>c.origin.join(","))).size!==all.length)
      throw Error("Overlapping or duplicated scenic candidates across batches");
   // Decode only the nearest visible cells. A 16-cell 1536×1024
   // eager decode can exhaust mobile Safari memory even when offscreen.
   if(!root.COEV267ViewportCache)throw Error("V267 viewport loader missing");
   neighborPilotCells=all;
   neighborPilotImages={};
   neighborPilotStream=root.COEV267ViewportCache.create({
    cells:all,maxDecoded:6,maxConcurrent:2,padding:192,
    load:async (art,cell)=>{
     let img;
     try{img=await imageLoad(art,12000);}
     catch(primaryError){
      if(cell.id!=="matrei-east-ridge")throw primaryError;
      if(ridgeV2Pilot||ridgeV6Pilot||ridgeV7Pilot||ridgeV8Pilot)throw primaryError; // No silent replacement with older unapproved art.
      const fallbackCommit=ridgeGradePilot?"0e0ba14df7bc44d5492f460fa4d616c552644957":"9e0e11cb2897cce91461681bfe0acf1a420034a5";
      img=await imageLoad("https://raw.githubusercontent.com/wayfinderandco0-cell/century-of-empires/"+fallbackCommit+"/"+art,20000);
     }
     if(img.decode)await img.decode().catch(()=>{});
     if(img.naturalWidth!==1536||img.naturalHeight!==1024)
      throw Error("Neighbor art dimensions mismatch: "+cell.id);
     return img;
    },
    onChange:()=>{
     neighborPilotImages=Object.fromEntries(neighborPilotStream.entries());
     if(neighborPilotShown)draw();
    }
   });
   neighborPilotInlays=batches.flatMap(b=>b.decorativeInlays||[]).filter(
     i=>all.some(c=>c.id===i.sourceCell));
  }
  neighborPilotCamera={center:clone(center),zoom};neighborPilotShown=true;ridgeEmergency=false;
  // A normal HTML image fallback is intentionally limited to the single
  // unapproved ridge study. Protected WEST/MATREI/SOUTH still use the V123 canvas.
  halt();
  for(const id of ["atlasMarch","atlasHalt","atlasRoads"]){$(id).hidden=true;$(id).disabled=true;}
  if(focusedV267NewPilot){
   // Fit the actual source art to the visible canvas on narrow iPhone screens.
   // The old fixed camera could leave the new tile entirely offscreen.
   const tile=neighborPilotCells[0];
   const visibleHeight=Math.max(180,h-180),visibleWidth=Math.max(180,w-24);
   const targetScale=Math.min(visibleWidth/1536,visibleHeight/1024);
   centerAt(tile.origin[0]+768,tile.origin[1]+512,Math.max(.15,targetScale/base));
  }
  else if(focusedEastPilot)centerAt(3072,512,2.9);
  else $("atlasWhole").click();
  status(ridgeV8Pilot?"V8 EAST-01 narrow shaded dirt: original road material + Matrei display overlay · seam UNVERIFIED · army route disabled":ridgeV7Pilot?"V7 EAST-01 cleared cartway: source-ground corridor + Matrei display overlay · road/river seam UNVERIFIED · route disabled":ridgeV6Pilot?"V6 EAST-01 road material: original Matrei protected · road sits above trees, NOT ground-verified · route disabled":ridgeV2Pilot?"V2 east seam: reversible Matrei display edge · visual/river/roads UNVERIFIED · not playable":ridgeGradePilot?"Color-only graded ridge: edge RGB improved · terrain geometry and roads UNVERIFIED · not playable":focusedV267NewPilot?"Original V267-like east ridge: NEW authored art · no road, seam unverified · not playable":focusedEastPilot?"Matrei east: new CC0 landscape candidate · seam and road unverified · not playable":neighborPilotCells.length+" distinct layered scenic studies · road seams unverified · V123 movement only on protected 3");
 }catch(e){status("Neighbor art not available: "+e.message+(ridgeEmergency?" · showing direct image recovery":""));}
};
// Open the image immediately, independent of the V121 canvas bootstrap.
// On a failed base asset or a lost WebKit canvas this stays visible rather
// than reproducing the user's completely blank iPhone screenshot.
if(focusedV267NewPilot&&studyParams.get("autoOpen")==="1"){
 ridgeEmergency=true;
 ridgeDOM.src=ridgeV8Pilot?ridgeV8Path:ridgeV7Pilot?ridgeV7Path:ridgeV6Pilot?ridgeV6Path:ridgeV2Pilot?ridgeV2Path:ridgeGradePilot?ridgeGradePath:"terrain-grid/v267-original-art-batch-01/matrei-east-ridge.webp";
 open();
 for(const id of ["atlasMarch","atlasHalt","atlasRoads"]){$(id).hidden=true;$(id).disabled=true;}
 status("Loading original ridge · direct-image recovery active until atlas is ready");
 draw();
}
const photoButton=document.createElement("button");
photoButton.id="atlasPhotoSources";photoButton.type="button";
// Keep experimental photo/heightmesh references out of the default approved-art UI.
photoButton.hidden=!(studyParams.has("terrainStudy")||studyParams.has("photoBlock"));
photoButton.textContent=studyParams.has("terrainStudy")?"Unapproved 3D study":"Photo references only";
$("atlasBar").querySelector("div").appendChild(photoButton);
const photoNext=document.createElement("button");
photoNext.id="atlasPhotoNext";photoNext.type="button";
photoNext.textContent="Next region";photoNext.hidden=true;
$("atlasBar").querySelector("div").appendChild(photoNext);
let photoIndex=0;
function focusPhoto(index){
 if(!photoMode||!photoStream||!photoStream.cells.length)return false;
 photoIndex=(index+photoStream.cells.length)%photoStream.cells.length;
 const cell=photoStream.cells[photoIndex];
 center=[cell.origin[0]+768,cell.origin[1]+512];
 zoom=1.5;scale=base*zoom;
 status(cell.id+" · "+cell.sourceRegion+(photoStream.mode==='relief'?" · ORIGINAL DEPTH STUDY, not playable":" · PHOTO REFERENCE ONLY, no route or conquest"));
 draw();
 return cell.id;
}
photoNext.onclick=()=>focusPhoto(photoIndex+1);
async function togglePhotoSources(){
 try {
  if(!photoStream){
   if(!root.COEPhotoAtlasStream){
    await new Promise((resolve,reject)=>{
     const script=document.createElement("script");
     script.src="terrain-grid/atlas-photo-stream.js";
     script.onload=resolve;script.onerror=()=>reject(Error("Photo stream module unavailable"));
     document.head.appendChild(script);
    });
   }
   const study=new URLSearchParams(root.location.search).has("terrainStudy");
   const photoBlock=new URLSearchParams(root.location.search).get("photoBlock");
   const photoURL=study?"generated/v267-relief-pilot/manifest.json":photoBlock==="dulmenRoad"
     ?"terrain-grid/factory-photo/dulmen-road-8/manifest.json"
     :photoBlock==="coverage"
     ?"terrain-grid/factory-photo/coverage/manifest.json"
     :photoBlock==="carpathians"
     ?"terrain-grid/factory-photo/carpathian-8/manifest.json"
     :photoBlock!==null
       ?"terrain-grid/factory-photo/block-8/manifest.json"
       :"terrain-grid/factory-photo/manifest.json";
   photoStream=await new root.COEPhotoAtlasStream(photoURL,draw).init();
  }
  if(!photoMode){
   photoCamera={center:clone(center),zoom};
   photoMode=true;photoIndex=0;photoNext.hidden=false;
   photoButton.textContent="Alpine roads";
   // Source-only photography has no approved route graph: do not present
   // march/halt/road controls as if these eight candidate cells are playable.
   for(const id of ["atlasMarch","atlasHalt","atlasRoads"]){$(id).hidden=true;$(id).disabled=true;}
   focusPhoto(0);
  } else {
   photoMode=false;center=clone(photoCamera.center);zoom=photoCamera.zoom;
   photoNext.hidden=true;photoButton.textContent=studyParams.has("terrainStudy")?"Unapproved 3D study":"Photo references only";
   for(const id of ["atlasMarch","atlasHalt","atlasRoads"]){$(id).hidden=false;$(id).disabled=false;}
   status("WEST · MATREI · SOUTH connected · tap a cartway");
  }
  scale=base*zoom;draw();
 } catch(error){status("Photo sources unavailable: "+error.message);}
}
photoButton.onclick=togglePhotoSources;
window.addEventListener("resize",()=>{if(shown)fit();});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&shown)close();});
const API={
 get loaded(){return loaded},get shown(){return shown},get nodes(){return atlas?.network.graph.size||0},
 get uniqueWorldNodes(){return atlas?new Set([...atlas.network.graph.values()].map(n=>n.world.join(","))).size:0},
 get seams(){return atlas?.network.seams||[]},get imageSizes(){return Object.fromEntries(Object.entries(images).map(([id,img])=>[id,[img.naturalWidth,img.naturalHeight]]));},
 get moving(){return moving},get position(){return clone(unit)},get route(){return path.map(clone)},
 get zoom(){return zoom},get center(){return clone(center)},get manifest(){return manifest},
 get graph(){return atlas?.network},get sourceRoadSegments(){return segments.length},
 get campaignOrdersUnchanged(){return true},get matreiRegistered(){return !!matreiRegistered},
 get approvedBaselineLocked(){return !!manifest&&root.COEV267ArtContract?.assertBase(manifest)===true},
 get originalNeighborCells(){return neighborPilotCells.length},get originalNeighborVisible(){return neighborPilotShown},
 get originalNeighborCache(){return neighborPilotStream?.stats()||null},
 get photoMode(){return photoMode},get photoCells(){return photoStream?.cells.length||0},
 get photoLoaded(){return photoStream?.stats.loaded||0},get photoThumbLoaded(){return photoStream?.stats.thumbLoaded||0},get photoFullLoaded(){return photoStream?.stats.fullLoaded||0},get photoInlays(){return photoStream?.inlays.length||0},get photoFocusedCell(){return photoStream?.cells[photoIndex]?.id||null},togglePhotoSources,nextPhotoSource:()=>focusPhoto(photoIndex+1),
 open,close,halt,centerAt,startMarch:()=>startOrder([2806,1629]),finishMarch:()=>{if(!path.length)return clone(unit);progress=travelLength;unit=clone(path.at(-1));moving=false;draw();return clone(unit);},
 routeTo:p=>routeBetween(unit,p),tapWorld:tapRoad,screenFor:worldToScreen,setZoom:z=>centerAt(...center,z)
};
root.COEAtlas=Object.freeze(API);
(async()=>{
 const response=await fetch(M);if(!response.ok)throw Error("Atlas manifest HTTP "+response.status);
 manifest=await response.json();
 if(!root.COEV267ArtContract)throw Error("V267 approved original-art contract script missing");
 root.COEV267ArtContract.assertBase(manifest);
 atlas=root.V123Atlas.create(manifest.centerRoads,{experimentalSeams:true});
 if(atlas.network.graph.size!==100||atlas.network.seams.length!==2||atlas.network.seams.some(s=>!s.pass||s.endpointGapPx!==0))throw Error("Protected V123 road seam drift");
 segments=collectSegments(atlas.network);
 const loadedImages=await Promise.all(manifest.cells.map(async cell=>[cell.id,await imageLoad(cell.art)]));
 images=Object.fromEntries(loadedImages);
 if(Object.values(images).some(img=>img.naturalWidth!==1536||img.naturalHeight!==1024))throw Error("Original art dimension mismatch");
 matreiRegistered=registerMatrei(images.matrei);
 loaded=true;status("WEST · MATREI · SOUTH connected · tap a cartway");if(shown)fit();
 if(focusedV267NewPilot&&studyParams.get("autoOpen")==="1"){
  if(!shown)open();
  pilotButton.click();
 }
})().catch(error=>{status("Atlas load blocked: "+error.message);root.COEAtlasLoadError=error.message;});
requestAnimationFrame(frame);
})(window);
