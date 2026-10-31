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
let manifest=null,atlas=null,images={},matreiRegistered=null,segments=[],loaded=false,shown=false,debug=false;
let w=0,h=0,dpr=1,base=1,zoom=1.05,scale=1,center=[1810,950];
let photoMode=false,photoStream=null,photoCamera=null;
// Opt-in source-layered scenic art. Never changes the protected V123 road graph.
let neighborPilotCells=[],neighborPilotImages={},neighborPilotShown=false,neighborPilotCamera=null;
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
 if(photoMode){
  if(photoStream)photoStream.draw(ctx,worldToScreen,scale,w,h);
  return;
 }
 if(!loaded)return;
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
 if(debug)for(const tile of atlas.tiles){for(const road of Object.values(tile.roads))polyline(road.map(p=>[p[0]+tile.origin[0],p[1]+tile.origin[1]]),"#f9ce4ac9",2);}
 if(path.length>1)polyline(path,"#ffe2a9b9",2.8);
 const [x,y]=worldToScreen(unit);
 ctx.save();ctx.translate(x,y);ctx.fillStyle="#193a2a";ctx.strokeStyle="#f4d78e";ctx.lineWidth=2.2;ctx.beginPath();ctx.arc(0,0,13,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle="#fff1c3";ctx.font="bold 16px Georgia";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("⚔",0,0);ctx.restore();
}
function imageLoad(src){return new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(Error("Missing atlas art: "+src));img.src=src;});}
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
function startOrder(to){if(photoMode){status("Photo candidates are NOT road-connected or playable");return false;}if(!loaded)return false;const next=routeBetween(unit,to);if(!next)return false;path=next;progress=0;travelLength=length(path);moving=travelLength>0.01;status(moving?"Marching on V123 road · tap another cartway to redirect":"Unit already at destination");draw();return true;}
function halt(){moving=false;path=[];progress=0;status("Halted · tap a painted road");draw();}
function frame(t){if(shown&&loaded&&moving&&lastTime){progress=Math.min(travelLength,progress+Math.min(.05,(t-lastTime)/1000)*155);unit=sample(path,progress);if(progress>=travelLength-.001){moving=false;status("Arrived · tap another cartway");}draw();}lastTime=t;requestAnimationFrame(frame);}
function tapRoad(point){if(photoMode)return false;const hit=nearest(point);if(!hit||hit.distance>Math.max(19,16/scale)){status("No road here · select a visible cartway");return false;}return startOrder(hit.point);}
function centerAt(x,y,z){center=[x,y];if(z!==undefined)zoom=clamp(z,photoMode?.15:.6,8);scale=base*zoom;draw();}
function open(){layer.hidden=false;openButton.hidden=true;shown=true;fit();if(!loaded)status("Loading fixed V121/V123 atlas assets…");}
function close(){shown=false;layer.hidden=true;openButton.hidden=false;openButton.focus();}
canvas.addEventListener("pointerdown",e=>{e.preventDefault();canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);if(pointers.size===1)tap=[e.clientX,e.clientY];if(pointers.size===2){const pts=[...pointers.values()];prevPinch=distance(pts[0],pts[1]);tap=null;}});
canvas.addEventListener("pointermove",e=>{
 if(!pointers.has(e.pointerId))return;const prev=pointers.get(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);
 const rect=canvas.getBoundingClientRect();
 if(pointers.size===2){const pts=[...pointers.values()],gap=distance(pts[0],pts[1]);const mid=[(pts[0][0]+pts[1][0])/2-rect.left,(pts[0][1]+pts[1][1])/2-rect.top];const anchor=screenToWorld(mid);
  if(prevPinch>2){zoom=clamp(zoom*gap/prevPinch,photoMode?.15:.6,8);scale=base*zoom;const shifted=screenToWorld(mid);center=[center[0]+anchor[0]-shifted[0],center[1]+anchor[1]-shifted[1]];}prevPinch=gap;draw();return;}
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
pilotButton.textContent="Original neighbors";
pilotButton.hidden=!studyParams.has("originalArtPilot");
$("atlasBar").querySelector("div").appendChild(pilotButton);
pilotButton.onclick=async()=>{
 if(neighborPilotShown){neighborPilotShown=false;
  if(neighborPilotCamera){center=neighborPilotCamera.center;zoom=neighborPilotCamera.zoom;scale=base*zoom;}
  status("Protected WEST / MATREI / SOUTH roads restored");draw();return;
 }
 try{
  if(!neighborPilotCells.length){
   status("Loading eight original scenic candidates (no new roads)…");
   const response=await fetch("terrain-grid/v267-neighbor-original-art/batch.json");
   if(!response.ok)throw Error("Neighbor manifest HTTP "+response.status);
   const batch=await response.json();
   if(!root.COEV267ArtContract)throw Error("Original-art validator missing");
   root.COEV267ArtContract.validateBatch(batch,manifest);
   const pairs=await Promise.all(batch.cells.map(async c=>[c.id,await imageLoad(c.art)]));
   if(pairs.some(([,img])=>img.naturalWidth!==1536||img.naturalHeight!==1024))throw Error("Neighbor art dimensions mismatch");
   neighborPilotCells=batch.cells;neighborPilotImages=Object.fromEntries(pairs);
  }
  neighborPilotCamera={center:clone(center),zoom};neighborPilotShown=true;
  $("atlasWhole").click();
  status("Eight NEW original layered scenic candidates · roads unverified · V123 movement remains only on approved 3");
 }catch(e){status("Neighbor art not available: "+e.message);}
};
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
})().catch(error=>{status("Atlas load blocked: "+error.message);root.COEAtlasLoadError=error.message;});
requestAnimationFrame(frame);
})(window);
