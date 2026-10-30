/* Century of Empires: reusable native photographic atlas cell stream.
 * Source-backed candidate art is NOT a routable road graph, province, or
 * historic site. V121/V123/V94 are not imported or mutated by this module.
 * Browser canvas, no iframe, native octagon clip, viewport culling and LRU.
 */
(function(root) {
"use strict";
const W=1536,H=1024,C=256;
const oct=[[C,0],[W-C,0],[W,C],[W,H-C],[W-C,H],[C,H],[0,H-C],[0,C]];
function intersects(a,b) {
 return a[0]<b[2]&&a[2]>b[0]&&a[1]<b[3]&&a[3]>b[1];
}
class PhotoAtlasStream {
 constructor(url,onChange) {
  this.url=url;this.onChange=onChange||(()=>{});
  this.manifest=null;this.cache=new Map();this.pending=new Map();
  // Ten nearby native textures fit the 8-cell study without cache-eviction
  // thrashing. Distant European cells remain lazily streamed, never all 432.
  this.maxCached=10;this.stats={requests:0,loaded:0,failed:0};
 }
 async init() {
  const response=await fetch(this.url,{cache:"no-cache"});
  if(!response.ok)throw Error("Photo atlas manifest HTTP "+response.status);
  const manifest=await response.json();
  if(manifest.schema!=="coe-photo-art/v1"||!Array.isArray(manifest.cells))
   throw Error("Unexpected photo atlas schema");
  const ids=new Set();
  for(const c of manifest.cells) {
   if(ids.has(c.id)||!Array.isArray(c.origin)||c.imageSize[0]!==W||c.imageSize[1]!==H)
    throw Error("Duplicate or invalid photo cell "+c.id);
   ids.add(c.id);
   if(c.gameplayEnabled||c.historicallyVerified||c.physicallyRoadSeamChecked)
    throw Error("Unreviewed photo art incorrectly declared routable");
  }
  this.manifest=manifest;
  return this;
 }
 get cells(){return this.manifest?.cells||[];}
 touch(id) {
  if(!this.cache.has(id))return null;
  const img=this.cache.get(id);
  this.cache.delete(id);this.cache.set(id,img);
  return img;
 }
 request(cell) {
  if(this.cache.has(cell.id)||this.pending.has(cell.id))return;
  this.stats.requests++;
  const img=new Image();
  const done=new Promise((resolve)=>{
   img.onload=()=>{
    if(img.naturalWidth!==W||img.naturalHeight!==H) {
     this.stats.failed++;resolve(false);return;
    }
    this.cache.set(cell.id,img);this.stats.loaded++;
    while(this.cache.size>this.maxCached)this.cache.delete(this.cache.keys().next().value);
    resolve(true);this.onChange();
   };
   img.onerror=()=>{this.stats.failed++;resolve(false);this.onChange();};
  });
  this.pending.set(cell.id,done);
  img.src=cell.image;
  done.finally(()=>this.pending.delete(cell.id));
 }
 draw(ctx,toScreen,scale,screenWidth,screenHeight) {
  if(!this.manifest)return;
  const visible=[];
  for(const cell of this.cells) {
   const p=toScreen(cell.origin),box=[p[0],p[1],p[0]+W*scale,p[1]+H*scale];
   if(intersects(box,[-W*scale,-H*scale,screenWidth+W*scale,screenHeight+H*scale]))
    this.request(cell);
   if(intersects(box,[0,0,screenWidth,screenHeight]))visible.push({cell,p});
  }
  // Native-pixel 2x2 source mosaics supply road-free decorative diamond infill.
  // Never do this for unrelated photos: their boundaries are NOT certified.
  for(const {cell,p} of visible) {
   if(cell.nativePhotoUnderlay){const img=this.touch(cell.id);
    if(img)ctx.drawImage(img,p[0],p[1],W*scale,H*scale);
   }
  }
  for(const {cell,p} of visible) {
   ctx.save();ctx.beginPath();
   oct.forEach(([x,y],i)=>i?ctx.lineTo(p[0]+x*scale,p[1]+y*scale):
                                   ctx.moveTo(p[0]+x*scale,p[1]+y*scale));
   ctx.closePath();ctx.clip();
   const img=this.touch(cell.id);
   if(img)ctx.drawImage(img,p[0],p[1],W*scale,H*scale);
   else {
    ctx.fillStyle="#35483c";ctx.fillRect(p[0],p[1],W*scale,H*scale);
    ctx.fillStyle="#e2d3a9";ctx.font="12px system-ui";
    ctx.fillText("Loading native source photograph",p[0]+20,p[1]+80);
   }
   ctx.restore();
   ctx.save();ctx.beginPath();
   oct.forEach(([x,y],i)=>i?ctx.lineTo(p[0]+x*scale,p[1]+y*scale):
                                   ctx.moveTo(p[0]+x*scale,p[1]+y*scale));
   ctx.closePath();
   if(!cell.nativePhotoUnderlay){ctx.strokeStyle="#bca16b";ctx.lineWidth=1.2;ctx.stroke();}
   // Do not cover the photographic terrain with repeated giant labels
   // when the player zooms out to inspect a regional block.
   if(scale>.22){ctx.fillStyle="#f8e8c7";ctx.font="bold 10px system-ui";
    ctx.fillText(cell.id+" · SOURCE ONLY",p[0]+Math.max(8,280*scale),p[1]+Math.max(20,45*scale));}
   ctx.restore();
  }
 }
}
root.COEPhotoAtlasStream=PhotoAtlasStream;
})(window);
