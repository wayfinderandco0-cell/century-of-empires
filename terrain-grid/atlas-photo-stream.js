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
  this.maxCached=10;this.inlays=[];this.stats={requests:0,loaded:0,failed:0};
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
  // Fill ONLY four-way diamonds from truly adjacent pixels in the SAME
  // original photograph. Previous full-rectangle underlays leaked photo
  // outside octagon borders and falsely bridged unrelated sources.
  const grid=new Map(manifest.cells.map(c=>[c.grid.join(","),c]));
  const gaps=[];
  for(const c of manifest.cells) {
   const [x,y]=c.grid;
   const group=[c,grid.get((x+1)+","+y),grid.get(x+","+(y+1)),
                grid.get((x+1)+","+(y+1))];
   if(group.some(q=>!q||!q.nativePhotoUnderlay))continue;
   if(new Set(group.map(q=>q.nativePhotoSourceGroup)).size!==1)continue;
   const [a,b,d,e]=group;
   const h=(u,v)=>u.sourceSha256===v.sourceSha256 &&
     u.sourceCrop?.[2]===v.sourceCrop?.[0] &&
     u.sourceCrop?.[1]===v.sourceCrop?.[1] &&
     u.sourceCrop?.[3]===v.sourceCrop?.[3];
   const v=(u,z)=>u.sourceSha256===z.sourceSha256 &&
     u.sourceCrop?.[3]===z.sourceCrop?.[1] &&
     u.sourceCrop?.[0]===z.sourceCrop?.[0] &&
     u.sourceCrop?.[2]===z.sourceCrop?.[2];
   if(!h(a,b)||!h(d,e)||!v(a,d)||!v(b,e))
    throw Error("Invalid native source diamond "+c.id);
   gaps.push({center:[(x+1)*W,(y+1)*H],cells:group});
  }
  this.inlays=gaps;
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
  // The ONLY unmasked photographic fill is a clipped, non-playable
  // four-corner diamond, and ONLY when all four source crops are native
  // adjacent. Never draw a rectangular source photo across a missing tile
  // or a cross-source seam; that created fake contiguous terrain.
  for(const gap of this.inlays) {
   const p=toScreen(gap.center),r=C*scale;
   if(!intersects([p[0]-r,p[1]-r,p[0]+r,p[1]+r],
                  [0,0,screenWidth,screenHeight]))continue;
   ctx.save();ctx.beginPath();ctx.moveTo(p[0]-r,p[1]);
   ctx.lineTo(p[0],p[1]-r);ctx.lineTo(p[0]+r,p[1]);
   ctx.lineTo(p[0],p[1]+r);ctx.closePath();ctx.clip();
   for(const cell of gap.cells) {
    const img=this.touch(cell.id);
    if(img) {const q=toScreen(cell.origin);
     ctx.drawImage(img,q[0],q[1],W*scale,H*scale);}
   }
   ctx.restore();
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
