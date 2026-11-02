/* V268 one-source Matrei geography: opt-in native Canvas pilot.
 * Four shared-source geographic WebP crops, NOT four approved or playable tiles.
 * No road, bridge, campaign save, or V123 movement changes.
 */
(function(root){
"use strict";
if(new URLSearchParams(root.location.search).get("v268Geo")!=="1")return;
const PREFIX="terrain-grid/v268-matrei-geographic/";
let active=false,ready=false,manifest=null,images=new Map(),error=null;
let previousCamera=null;
const $=id=>document.getElementById(id);
const button=document.createElement("button");
button.id="v268GeoToggle";button.textContent="Matrei geography";
button.title="Source-registered 2x2 terrain; movement unverified";
$("atlasBar").querySelector("div").append(button);
function image(src){return new Promise((resolve,reject)=>{
 const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error("HTTP art unavailable: "+src));
 im.src=src;
});}
async function load(){
 if(ready)return;
 const response=await fetch(PREFIX+"manifest.json",{cache:"no-store"});
 if(!response.ok)throw Error("V268 manifest HTTP "+response.status);
 const data=await response.json();
 if(data.schema!=="coe-v268-matrei-one-source-geographic-pilot/v1"||
    data.geoCRS!=="EPSG:32632"||data.cells?.length!==4||
    data.newNativePlayable!==0||data.finishedToday!==0)
   throw Error("V268 source/approval contract mismatch");
 const decoded=await Promise.all(data.cells.map(async cell=>{
  if(cell.gameplayEnabled||cell.visualApproval||cell.verifiedRoadIds.length||
     cell.dimensionsPx[0]!==1536||cell.dimensionsPx[1]!==1024)
    throw Error("Unapproved geographic cell has invalid route/art contract");
  const im=await image(PREFIX+cell.artWebp);
  if(im.naturalWidth!==1536||im.naturalHeight!==1024)
    throw Error("V268 image dimensions invalid: "+cell.id);
  return [cell.id,im];
 }));
 manifest=data;images=new Map(decoded);ready=true;
}
function draw(ctx,worldToScreen,scale){
 if(!active||!ready)return false;
 for(const cell of manifest.cells){
  const im=images.get(cell.id);
  const x=cell.col*1536,y=cell.row*1024;
  const pos=worldToScreen([x,y]);
  ctx.drawImage(im,pos[0],pos[1],1536*scale,1024*scale);
 }
 // Octagons are translucent logical selection/ownership outlines ONLY.
 // Ground beneath them remains continuous and never clipped into diamonds.
 ctx.save();ctx.strokeStyle="rgba(231,206,141,.34)";
 ctx.lineWidth=1.2;
 for(const cell of manifest.cells){
  const x=cell.col*1536,y=cell.row*1024;
  const points=[[256,0],[1280,0],[1536,256],[1536,768],
                [1280,1024],[256,1024],[0,768],[0,256]];
  ctx.beginPath();
  points.forEach((p,i)=>{const q=worldToScreen([x+p[0],y+p[1]]);
    if(i)ctx.lineTo(...q);else ctx.moveTo(...q);});
  ctx.closePath();ctx.stroke();
 }
 ctx.restore();
 return true;
}
function setRoadControls(hidden){
 for(const id of ["atlasMarch","atlasHalt","atlasRoads","atlasWest","atlasSouth"]){
  const el=$(id);if(el)el.hidden=hidden;
 }
}
async function enable(){
 try{
  button.disabled=true;button.textContent="Loading source terrain…";
  await load();
  for(let i=0;i<60&&!root.COEAtlas?.loaded;i++)
   await new Promise(r=>setTimeout(r,150));
  if(!root.COEAtlas?.loaded)throw Error("Protected V123 atlas not ready");
  if(!active)previousCamera={center:root.COEAtlas.center,zoom:root.COEAtlas.zoom};
  root.COEAtlas.halt();root.COEAtlas.open();active=true;
  setRoadControls(true);
  root.COEAtlas.centerAt(1536,1024,1.05);
  $("atlasStatus").textContent="V268 Matrei DEM 2×2 · actual georeferenced art · 0 NEW PLAYABLE · movement blocked";
  button.textContent="Back to approved 3";
 }catch(e){
  error=String(e.message||e);active=false;
  $("atlasStatus").textContent="V268 unavailable: "+error+" · original 3 preserved";
  button.textContent="Retry Matrei terrain";
 }finally{button.disabled=false;}
}
function disable(){
 active=false;setRoadControls(false);
 if(previousCamera)root.COEAtlas.centerAt(...previousCamera.center,previousCamera.zoom);
 $("atlasStatus").textContent="3 approved WEST/MATREI/SOUTH · V268 geography unapproved";
 button.textContent="Matrei geography";
}
button.onclick=()=>active?disable():enable();
root.COEV268Geo=Object.freeze({
 get active(){return active},get ready(){return ready},get error(){return error},
 get loadedTiles(){return images.size},get manifest(){return manifest},
 get newPlayable(){return 0},draw,enable,disable
});
if(new URLSearchParams(root.location.search).get("autoOpen")==="1")enable();
})(window);
