/* Century of Empires V300 — REAL PlayCanvas/WebGL 3D, no image-tile substitution.
   A 12-territory landscape proof, isolated from the protected V123 campaign/save.
   New procedural landscape is fictional, not authenticated Austrian geography.
*/
import * as pc from "playcanvas";
const $=id=>document.getElementById(id);
const canvas=$("game"), status=$("status"), detail=$("detail");
const setStatus=(a,b)=>{status.textContent=a;if(b)detail.textContent=b;};
const fail=e=>{
  const text=String(e?.stack||e);
  console.error("COE V300 error",e);
  $("error").style.display="block";
  $("error").textContent="3D engine could not start: "+text.slice(0,500);
  setStatus("3D engine failed to load","Existing Century of Empires remains unaffected.");
};
window.addEventListener("error",e=>fail(e.error||e.message));
window.addEventListener("unhandledrejection",e=>fail(e.reason));
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const lerp=(a,b,t)=>a+(b-a)*t;
const radial=(a,b)=>Math.exp(-a*a/(b*b));
const noise=(x,z)=>Math.sin(x*.16+Math.cos(z*.09)*2)*Math.cos(z*.12)+.4*Math.sin(x*.37+z*.21);
const riverX=z=>4.5+5.5*Math.sin(z*.048)+1.3*Math.sin(z*.15);
function height(x,z){
 const north=26*radial(z+59,25)*(0.78+.25*Math.sin(x*.083+1.5));
 const south=21*radial(z-63,26)*(0.78+.23*Math.cos(x*.09));
 const west=12*radial(x+70,28)*radial(z+7,54);
 const east=15*radial(x-79,31)*radial(z-18,50);
 const snowcap=5*radial(x-56,17)*radial(z+61,18);
 const valley=-2.4*radial(z-1,23);
 const waterChannel=-2.2*radial(x-riverX(z),6);
 return north+south+west+east+snowcap+valley+waterChannel
    +1.7*Math.sin(x*.082+z*.034)*Math.cos(z*.073)+noise(x,z)*.95;
}
const WORLD={width:192,depth:156,cols:4,rows:3,sizeX:45,sizeZ:43};
const tile=(id)=>{
 const col=id%4,row=Math.floor(id/4);
 return {id,col,row,x:(col-1.5)*45,z:(row-1)*43,name:id===6?"Matrei":id===4?"Western camp":"Territory "+(id+1)};
};
const tiles=Array.from({length:12},(_,i)=>tile(i));
const edges=[[4,5],[5,6],[6,7],[0,4],[1,5],[2,6],[3,7],[4,8],[5,9],[6,10],[7,11]];
const graph=new Map(tiles.map(t=>[t.id,[]]));
for(const [a,b] of edges){graph.get(a).push(b);graph.get(b).push(a);}
let app,camera,army,selectionMarker,claimFlag,land,device;
let spin=-.72, distance=236, bearing=.73, focal={x:2,z:0};
let owned=false, supplies=50, selected=6, current=4, moving=null, boundaries=true, roadCenterlines=[];
const color=(r,g,b)=>new pc.Color(r/255,g/255,b/255);
const mat=(r,g,b,emissive=false)=>{
 const material=new pc.StandardMaterial();
 material.diffuse=color(r,g,b); material.metalness=0;material.gloss=emissive?.1:.16;
 if(emissive)material.emissive=color(r*.22,g*.22,b*.22);
 material.update();return material;
};
const MAT={
 rock:mat(137,134,119),dark:mat(41,70,55),pine:mat(39,88,65),
 leaves:mat(60,105,69),trunk:mat(79,62,42),
 roof:mat(111,70,52),building:mat(189,181,157),
 road:mat(141,109,72),roadEdge:mat(70,61,43),
 water:mat(59,134,149,true),foam:mat(114,170,167,true),
 bridge:mat(133,99,61),highlight:mat(236,191,81,true),
 boundary:mat(157,183,145,true),neutral:mat(140,146,151),
 captured:mat(245,191,70,true),army:mat(239,196,82,true),steel:mat(76,92,98)
};
function addPrimitive(name,type,material,x,y,z,sx,sy,sz,rot=0){
 const e=new pc.Entity(name);e.addComponent("render",{type,material});
 e.setPosition(x,y,z);e.setLocalScale(sx,sy,sz);
 if(rot)e.setEulerAngles(0,rot,0);
 app.root.addChild(e);return e;
}
function drawMesh(name,positions,indices,material,vertexColors=null){
 const mesh=new pc.Mesh(device);
 mesh.setPositions(new Float32Array(positions));
 mesh.setIndices(indices);
 mesh.setNormals(pc.calculateNormals(new Float32Array(positions),indices));
 if(vertexColors)mesh.setColors32(new Uint8Array(vertexColors));
 mesh.update();
 const entity=new pc.Entity(name);
 entity.addComponent("render",{meshInstances:[new pc.MeshInstance(mesh,material)],castShadows:false,receiveShadows:true});
 app.root.addChild(entity);return entity;
}
function landscape(){
 const NX=128,NZ=106;
 const p=[],idx=[],colors=[];
 for(let j=0;j<=NZ;j++){
  const z=-WORLD.depth/2+j*WORLD.depth/NZ;
  for(let i=0;i<=NX;i++){
   const x=-WORLD.width/2+i*WORLD.width/NX, y=height(x,z);
   p.push(x,y,z);
   const nearbyRiver=Math.abs(x-riverX(z));
   let c;
   if(y>25)c=[217,215,205];
   else if(y>20)c=[173,169,159];
   else if(y>14)c=[122,125,109];
   else if(y>8)c=[87,115,78];
   else if(nearbyRiver<7)c=[81,115,96];
   else c=[93,137,88];
   const randomish=(noise(x,z)+1.4)*5;
   colors.push(clamp(c[0]+randomish,0,255),clamp(c[1]+randomish,0,255),clamp(c[2]+randomish,0,255),255);
  }
 }
 for(let j=0;j<NZ;j++)for(let i=0;i<NX;i++){
   const a=j*(NX+1)+i,b=a+1,c=a+(NX+1),d=c+1;
   idx.push(a,c,b,b,c,d);
 }
 const material=new pc.StandardMaterial();material.diffuseVertexColor=true;material.diffuse=new pc.Color(1,1,1);
 material.gloss=.08;material.update();
 land=drawMesh("One continuous terrain mesh",p,idx,material,colors);
 return p.length/3;
}
function makeRibbon(name,points,width,material,ydelta=.28){
 const p=[],index=[];
 for(let i=0;i<points.length;i++){
  const v=points[i],prev=points[Math.max(i-1,0)],next=points[Math.min(i+1,points.length-1)];
  const dx=next.x-prev.x,dz=next.z-prev.z,len=Math.max(.001,Math.hypot(dx,dz));
  const px=-dz/len*width*.5,pz=dx/len*width*.5;
  p.push(v.x+px,height(v.x+px,v.z+pz)+ydelta,v.z+pz);
  p.push(v.x-px,height(v.x-px,v.z-pz)+ydelta,v.z-pz);
  if(i){const k=2*i;index.push(k-2,k,k-1,k-1,k,k+1);}
 }
 return drawMesh(name,p,index,material);
}
function roadLine(a,b){
 const A=tiles[a],B=tiles[b],length=Math.hypot(B.x-A.x,B.z-A.z);
 const bend=1.8*Math.sin((a+1)*1.7+(b+1)*.56);
 const points=[];
 for(let i=0;i<=28;i++){
  const t=i/28;
  // Shared node centers connect exactly; only middle of a segment meanders.
  const side=Math.sin(t*Math.PI)*bend,px=-(B.z-A.z)/length,pz=(B.x-A.x)/length;
  points.push({x:lerp(A.x,B.x,t)+px*side,z:lerp(A.z,B.z,t)+pz*side});
 }
 return points;
}
function makeRoads(){
 for(const [a,b] of edges){
  const path=roadLine(a,b);roadCenterlines.push({a,b,path});
  makeRibbon("dark road verge "+a+"-"+b,path,4.3,MAT.roadEdge,.17);
  makeRibbon("contour dirt road "+a+"-"+b,path,2.7,MAT.road,.22);
 }
}
function river(){
 const points=[];
 for(let i=0;i<=100;i++){
  const z=-WORLD.depth/2+i*WORLD.depth/100;
  points.push({x:riverX(z),z});
 }
 makeRibbon("Real 3D winding river ribbon",points,5.7,MAT.water,.39);
 const left=points.map(p=>({x:p.x-2.1,z:p.z}));
 makeRibbon("River highlights",left,.47,MAT.foam,.43);
 // Wooden bridge runs across the river near Matrei's western approach.
 for(let x=-3;x<13;x+=2){
  const z=0.8;const yy=height(x,z)+.65;
  addPrimitive("bridge plank","box",MAT.bridge,x,yy,z,1.65,.22,4.25,0);
 }
}
function distanceToPath(x,z,path){
 let best=Infinity;
 for(const p of path){const d=Math.hypot(x-p.x,z-p.z);best=Math.min(best,d);}
 return best;
}
function trees(){
 let num=0;
 for(let k=0;k<195;k++){
  const x=-92+((k*77.77)%184),z=-73+((k*53.37)%146),y=height(x,z);
  if(y>22||y<1||Math.abs(x-riverX(z))<8||Math.hypot(x-tiles[6].x,z-tiles[6].z)<15)continue;
  if(roadCenterlines.some(r=>distanceToPath(x,z,r.path)<5))continue;
  const sz=2.4+(k%7)*.31;
  addPrimitive("fir tree","cone",k%5===0?MAT.leaves:MAT.pine,x,y+sz*.7,z,sz*.75,sz*1.6,sz*.75,(k*29)%360);
  if(k%3===0)addPrimitive("pine trunk","cylinder",MAT.trunk,x,y+.8,z,.38,1.6,.38);
  num++;
 }
 return num;
}
function createTown(){
 const t=tiles[6],tx=t.x+8,tz=t.z+7;
 for(let i=0;i<4;i++){
  const x=tx+(i%2)*7,z=tz+Math.floor(i/2)*7,y=height(x,z);
  addPrimitive("Matrei stone house","box",MAT.building,x,y+2.1,z,4.1,4.2,4.1,((i%2)*17));
  addPrimitive("Matrei pitched roof","cone",MAT.roof,x,y+4.9,z,5.4,3.0,5.4);
 }
 const cx=tx-8,cz=tz+3,base=height(cx,cz);
 addPrimitive("Matrei watch tower","cylinder",MAT.rock,cx,base+4,cz,3.5,8,3.5);
 addPrimitive("Matrei fort turret","cone",MAT.steel,cx,base+8.6,cz,4.9,2.8,4.9);
 claimFlag=addPrimitive("Matrei capture flag","box",MAT.neutral,t.x+3,height(t.x+3,t.z-7)+5,t.z-7,3.2,2.3,.24);
 addPrimitive("Matrei flag pole","cylinder",MAT.steel,t.x+1.5,height(t.x+1.5,t.z-7)+4,t.z-7,.17,8,.17);
}
function provinceLines(t){
 const rX=20.6,rZ=19.4,cx=t.x,cz=t.z;
 return [
  [cx-rX*.69,cz-rZ],[cx+rX*.69,cz-rZ],[cx+rX,cz-rZ*.69],[cx+rX,cz+rZ*.69],
  [cx+rX*.69,cz+rZ],[cx-rX*.69,cz+rZ],[cx-rX,cz+rZ*.69],[cx-rX,cz-rZ*.69]
 ].map(v=>({x:v[0],z:v[1]}));
}
let outlineEntities=[];
function drawBoundaries(){
 for(const e of outlineEntities)e.destroy();
 outlineEntities=[];
 if(!boundaries)return;
 for(const t of tiles){
  const v=provinceLines(t);
  for(let j=0;j<8;j++){
   const a=v[j],b=v[(j+1)%8],path=[];
   for(let s=0;s<=5;s++)path.push({x:lerp(a.x,b.x,s/5),z:lerp(a.z,b.z,s/5)});
   outlineEntities.push(makeRibbon("3D territory outline "+t.id,path,.31,t.id===6?MAT.highlight:MAT.boundary,.48));
  }
 }
}
function selectHighlight(id){
 if(selectionMarker)selectionMarker.destroy();
 const t=tiles[id];
 // Selection is a visible 3D marker, not an image clipped into an octagon.
 selectionMarker=addPrimitive("Selected territory","sphere",MAT.highlight,t.x,height(t.x,t.z)+1.3,t.z,2.2,.7,2.2);
}
function createArmy(){
 const t=tiles[current],x=t.x,z=t.z,y=height(x,z);
 army=new pc.Entity("Western army");
 app.root.addChild(army);
 army.setPosition(x,y+.6,z);
 const e=(name,type,mat,x,y,z,sx,sy,sz)=>{
  const part=new pc.Entity(name);part.addComponent("render",{type,material:mat});
  part.setLocalPosition(x,y,z);part.setLocalScale(sx,sy,sz);army.addChild(part);
 };
 e("gold army base","cylinder",MAT.army,0,.15,0,3.5,.55,3.5);
 e("infantry body","capsule",MAT.steel,0,1.8,0,1.4,3.1,1.4);
 e("gold banner pole","cylinder",MAT.army,.9,3.2,0,.16,6,.16);
 e("gold banner","box",MAT.army,1.95,5.2,0,2.5,1.4,.18);
 e("army head","sphere",MAT.building,0,3.6,0,1.1,1.1,1.1);
}
function pathRoute(from,to){
 const queue=[from], parent=new Map([[from,-1]]);
 while(queue.length){
  const u=queue.shift();if(u===to)break;
  for(const v of graph.get(u))if(!parent.has(v)){parent.set(v,u);queue.push(v);}
 }
 if(!parent.has(to))return [];
 const route=[];let x=to;
 while(x!==-1){route.unshift(x);x=parent.get(x);}
 return route;
}
function routePositions(route){
 const path=[];
 for(let k=0;k<route.length-1;k++){
  const a=route[k],b=route[k+1],edge=roadCenterlines.find(r=>r.a===a&&r.b===b||r.a===b&&r.b===a);
  if(!edge)throw Error("Road graph lacks rendered edge "+a+"-"+b);
  const pts=edge.a===a?edge.path:edge.path.slice().reverse();
  path.push(...pts.slice(k?1:0));
 }
 return path;
}
function select(id){
 if(id<0||id>=12)return false;
 selected=id;selectHighlight(id);
 const can=pathRoute(current,id).length>0;
 $("move").disabled=!can;
 setStatus("Selected: "+tiles[id].name,id===6?"Historical town objective · capture by entering Matrei.":"Tap Move to selected to march on connected dirt roads.");
 return true;
}
function moveTo(id){
 if(moving){setStatus("Army already marching","Use Reset to start a new scenario.");return false;}
 const route=pathRoute(current,id);
 if(!route.length)return false;
 if(route.length<2){setStatus("Army already here");return true;}
 const positions=routePositions(route),distances=[0];
 for(let i=1;i<positions.length;i++)distances.push(distances[i-1]+Math.hypot(positions[i].x-positions[i-1].x,positions[i].z-positions[i-1].z));
 moving={id,route,positions,distances,total:distances[distances.length-1],distance:0};
 $("move").disabled=true;$("capture").disabled=true;
 setStatus("Army marching across "+(route.length-1)+" road connections","The 3D army follows the same terrain-hugging road geometry rendered on the landscape.");
 return true;
}
function updateArmy(dt){
 if(!moving)return;
 const m=moving;m.distance=Math.min(m.total,m.distance+dt*19);
 let i=1;
 while(i<m.distances.length-1&&m.distances[i]<m.distance)i++;
 const a=m.positions[i-1],b=m.positions[i],d=Math.max(.01,m.distances[i]-m.distances[i-1]);
 const t=clamp((m.distance-m.distances[i-1])/d,0,1);
 const x=lerp(a.x,b.x,t),z=lerp(a.z,b.z,t);
 army.setPosition(x,height(x,z)+.8,z);
 if(m.distance>=m.total){
  current=m.id;moving=null;$("move").disabled=false;$("capture").disabled=false;
  if(current===6&&!owned){
    owned=true;supplies+=25;claimFlag.render.material=MAT.captured;
    $("ownership").textContent="Captured";$("supply").textContent="Supplies: "+supplies;
    setStatus("Matrei captured! +25 supplies","Conquest mechanic worked: ownership and supplies changed after the army arrived.");
  }else setStatus("Army arrived at "+tiles[current].name,"Tap a province to select another connected road destination.");
 }
}
function reset(){
 moving=null;current=4;owned=false;supplies=50;selected=6;
 if(claimFlag)claimFlag.render.material=MAT.neutral;
 $("ownership").textContent="Neutral";$("supply").textContent="Supplies: 50";
 const t=tiles[current];army.setPosition(t.x,height(t.x,t.z)+.8,t.z);
 $("move").disabled=false;$("capture").disabled=false;
 select(6);setStatus("Scenario reset · Western camp ready","March to Matrei or select another territory. Original saved campaign untouched.");
}
function cameraFrame(){
 const targetY=height(focal.x,focal.z)+2;
 const sx=distance*Math.sin(bearing)*Math.cos(spin),sz=distance*Math.sin(bearing)*Math.sin(spin);
 const sy=distance*Math.cos(bearing);
 camera.setPosition(focal.x+sx,targetY+sy,focal.z+sz);
 camera.lookAt(new pc.Vec3(focal.x,targetY,focal.z));
}
function screenGround(px,py){
 const start=camera.camera.screenToWorld(px,py,camera.camera.nearClip);
 const end=camera.camera.screenToWorld(px,py,camera.camera.farClip);
 const dir=end.clone().sub(start).normalize();
 let prev=start.clone();
 for(let d=0;d<480;d+=1.5){
  const pt=new pc.Vec3(start.x+dir.x*d,start.y+dir.y*d,start.z+dir.z*d);
  if(pt.y<=height(pt.x,pt.z)){
    let lo=d-1.5,hi=d;
    for(let q=0;q<9;q++){const mid=(lo+hi)*.5;const x=start.x+dir.x*mid,z=start.z+dir.z*mid,y=start.y+dir.y*mid;
      if(y>height(x,z))lo=mid;else hi=mid;
    }
    const hit=hi;return {x:start.x+dir.x*hit,z:start.z+dir.z*hit};
  }prev=pt;
 }
 return null;
}
function pick(px,py){
 const hit=screenGround(px,py);if(!hit)return;
 const col=Math.floor((hit.x+90)/45),row=Math.floor((hit.z+64.5)/43);
 if(col>=0&&col<4&&row>=0&&row<3)select(row*4+col);
}
function controls(){
 $("capture").onclick=()=>{select(6);moveTo(6);};
 $("move").onclick=()=>moveTo(selected);
 $("overview").onclick=()=>{distance=190;focal={x:0,z:0};bearing=.88;spin=-.64;cameraFrame();setStatus("Overview · 12 scenic territories","Drag to orbit, pinch to zoom, tap land to select. Terrain is one connected mesh.");};
 $("toggle").onclick=()=>{boundaries=!boundaries;drawBoundaries();$("toggle").textContent="Boundaries: "+(boundaries?"ON":"OFF");};
 $("reset").onclick=reset;
 let pointers=new Map(),gesture=null;
 canvas.addEventListener("pointerdown",e=>{
  canvas.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY,moved:0});
  if(pointers.size>1){const a=[...pointers.values()];gesture={length:Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y),distance};}
 });
 canvas.addEventListener("pointermove",e=>{
  if(!pointers.has(e.pointerId))return;
  const pt=pointers.get(e.pointerId),dx=e.clientX-pt.x,dy=e.clientY-pt.y;
  pt.x=e.clientX;pt.y=e.clientY;pt.moved+=Math.hypot(dx,dy);
  if(pointers.size===1&&!gesture){
   spin-=dx*.0068;
   bearing=clamp(bearing+dy*.005,.28,1.28);
  }else if(pointers.size>=2){
   const a=[...pointers.values()],length=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);
   if(gesture)distance=clamp(gesture.distance*gesture.length/Math.max(length,20),65,270);
  }
  cameraFrame();e.preventDefault();
 },{passive:false});
 const end=e=>{
  const pt=pointers.get(e.pointerId);if(!pt)return;
  pointers.delete(e.pointerId);
  if(pointers.size<2)gesture=null;
  if(pt.moved<11&&pointers.size===0){
   const rect=canvas.getBoundingClientRect();pick(e.clientX-rect.left,e.clientY-rect.top);
  }
 };
 canvas.addEventListener("pointerup",end);canvas.addEventListener("pointercancel",end);
 canvas.addEventListener("wheel",e=>{e.preventDefault();distance=clamp(distance*(e.deltaY>0?1.1:.9),60,275);cameraFrame();},{passive:false});
}
async function boot(){
 const canvas=$("game");
 // Use WebGL2 deliberately; iOS support is stronger than relying on WebGPU.
 const graphic=await pc.createGraphicsDevice(canvas,{deviceTypes:[pc.DEVICETYPE_WEBGL2],antialias:true,powerPreference:"high-performance"});
 device=graphic;
 const opts=new pc.AppOptions();
 opts.graphicsDevice=device;
 opts.componentSystems=[pc.RenderComponentSystem,pc.CameraComponentSystem,pc.LightComponentSystem];
 opts.resourceHandlers=[pc.TextureHandler];
 app=new pc.AppBase(canvas);app.init(opts);
 app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);app.setCanvasResolution(pc.RESOLUTION_AUTO);
 app.scene.ambientLight=new pc.Color(.59,.64,.63);
 app.scene.exposure=1.08;
 camera=new pc.Entity("3D strategy camera");
 camera.addComponent("camera",{clearColor:new pc.Color(.60,.73,.78),nearClip:.2,farClip:600,fov:54});
 app.root.addChild(camera);
 const sun=new pc.Entity("Alpine sun");
 sun.addComponent("light",{type:"directional",color:new pc.Color(1,.94,.79),intensity:2.5,castShadows:false});
 sun.setEulerAngles(54,38,0);app.root.addChild(sun);
 const count=landscape();
 river();makeRoads();
 const treeCount=trees();
 createTown();drawBoundaries();createArmy();selectHighlight(6);cameraFrame();controls();
 app.on("update",dt=>updateArmy(Math.min(dt,.09)));
 app.start();
 window.addEventListener("resize",()=>{app.resizeCanvas();cameraFrame();});
 window.COE3D={
  engine:"playcanvas",ready:true,tiles:tiles.length,roads:edges.length,terrainVertices:count,treeCount,
  terrainIsContinuous:true,tilePictures:0,pick:select,moveTo,reset,getState:()=>({current,selected,owned,supplies,moving:!!moving}),
  roadGraph:edges,terrainSample:(x,z)=>height(x,z),app
 };
 $("move").disabled=false;
 setStatus("REAL 3D TERRAIN ACTIVE · "+tiles.length+" territories",
  "Free PlayCanvas engine. Drag to rotate, pinch to zoom. March to Matrei to capture the town. This uses generated geometry, not landscape photographs.");
}
boot().catch(fail);
