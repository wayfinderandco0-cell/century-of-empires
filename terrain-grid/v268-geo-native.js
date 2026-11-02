/* V268 georeferenced terrain preview rendered inside the EXISTING game page.
   Experimental scout movement is not validated historical/rivers crossing. */
(()=>{
"use strict";
const root=document.createElement("section");
root.id="geoV268";root.hidden=true;
root.innerHTML='<header><strong>MATREI · REAL ELEVATION · 4 GEOGRAPHIC CELLS</strong><div><button data-action="whole">Whole</button><button data-action="plus">＋</button><button data-action="minus">－</button><button data-action="close">Back</button></div></header><canvas aria-label="V268 real source Alpine terrain, drag to pan, tap for experimental scout"></canvas><footer id="geoV268Status">Loading authentic elevation graphics…</footer>';
const css=document.createElement("style");
css.textContent='#geoV268Open{position:fixed;z-index:135;left:10px;bottom:64px;background:#173c31;color:#fff1ca;border:1px solid #d3b678;padding:11px;border-radius:8px;font:700 12px system-ui}#geoV268{position:fixed;inset:0;z-index:1100;background:#14241d;color:#fff1ce;font:12px system-ui}#geoV268[hidden]{display:none!important}#geoV268 canvas{position:absolute;inset:0;width:100%;height:100%;touch-action:none}#geoV268 header{position:absolute;z-index:2;top:0;left:0;right:0;display:flex;justify-content:space-between;align-items:center;gap:6px;flex-wrap:wrap;padding:calc(7px + env(safe-area-inset-top)) 10px 7px;background:#142b22e8}#geoV268 header div{display:flex;gap:4px}#geoV268 button{border:1px solid #b69b64;background:#2e4b3e;color:#faebc5;border-radius:6px;padding:7px;min-height:34px}#geoV268 footer{position:absolute;z-index:2;bottom:0;left:0;right:0;background:#142b22ea;padding:10px 12px calc(10px + env(safe-area-inset-bottom))}';
document.head.append(css);
const button=document.createElement("button");button.id="geoV268Open";button.textContent="Real Alpine terrain · V268";document.body.append(button,root);
const c=root.querySelector("canvas"),ctx=c.getContext("2d"),msg=root.querySelector("footer");
let manifest=null,images=[],surface=null,loaded=false,inflight=null,CW=0,CH=0,DPR=1,center=[1536,1024],scale=.18;
let scout=[1536,1024],path=[],anim=0,last=0;
const pointers=new Map();let moved=0;
const say=s=>msg.textContent=s;
const screen=p=>[CW/2+(p[0]-center[0])*scale,CH/2+(p[1]-center[1])*scale];
const world=p=>[(p[0]-CW/2)/scale+center[0],(p[1]-CH/2)/scale+center[1]];
function fit(){scale=Math.min(CW/3072,CH/2048)*.92;center=[1536,1024];draw()}
function size(){const b=c.getBoundingClientRect();CW=b.width;CH=b.height;DPR=Math.min(2,devicePixelRatio||1);c.width=Math.round(CW*DPR);c.height=Math.round(CH*DPR);ctx.setTransform(DPR,0,0,DPR,0,0);draw()}
function draw(){
 if(root.hidden)return;
 ctx.setTransform(DPR,0,0,DPR,0,0);ctx.fillStyle="#10251c";ctx.fillRect(0,0,CW,CH);
 if(!loaded)return;
 manifest.cells.forEach((cell,i)=>{
  const p=screen(cell.originPixels);ctx.drawImage(images[i],p[0],p[1],1536*scale,1024*scale);
  const x=cell.originPixels[0],y=cell.originPixels[1];
  const poly=[[x+256,y],[x+1280,y],[x+1536,y+256],[x+1536,y+768],[x+1280,y+1024],[x+256,y+1024],[x,y+768],[x,y+256]];
  ctx.beginPath();poly.forEach((a,i)=>{const q=screen(a);i?ctx.lineTo(...q):ctx.moveTo(...q)});ctx.closePath();ctx.strokeStyle="#eed396b9";ctx.lineWidth=1;ctx.stroke();
 });
 if(path.length){ctx.beginPath();path.forEach((q,i)=>{const t=screen(q);i?ctx.lineTo(...t):ctx.moveTo(...t)});ctx.lineWidth=3;ctx.strokeStyle="#f7d58a";ctx.stroke()}
 const p=screen(scout);ctx.beginPath();ctx.arc(...p,6,0,Math.PI*2);ctx.fillStyle="#fff2c4";ctx.fill();ctx.lineWidth=2;ctx.strokeStyle="#243d2c";ctx.stroke();
}
function allowed(p){
 if(!surface)return false;
 const x=Math.floor(p[0]/16),y=Math.floor(p[1]/16);
 return x>=0&&y>=0&&x<surface.width&&y<surface.height&&surface.data[(y*surface.width+x)*4]>127;
}
function order(target){
 if(!allowed(target)){say("Steep terrain or outside geographic surface · scout order blocked");return}
 // No historical roads or hydrography certified: this is only an experimental scout.
 const dist=Math.hypot(target[0]-scout[0],target[1]-scout[1]),n=Math.max(1,Math.ceil(dist/8));
 for(let i=0;i<=n;i++){const p=[scout[0]+(target[0]-scout[0])*i/n,scout[1]+(target[1]-scout[1])*i/n];if(!allowed(p)){say("Direct route rejected by measured DEM slope; no invented road or bridge");return}}
 path=[scout.slice(),target];last=0;say("Experimental straight-line ground scout · rivers and history not certified");
 if(!anim)anim=requestAnimationFrame(tick);
}
function tick(t){
 anim=0;if(root.hidden||path.length<2)return;
 if(!last)last=t;const q=path[1],dist=Math.hypot(q[0]-scout[0],q[1]-scout[1]),move=Math.min(12,(t-last)*.12);last=t;
 if(dist<=move){scout=q;path=[];say("Scout arrived on candidate slope corridor · not an approved game tile")}
 else scout=[scout[0]+(q[0]-scout[0])*move/dist,scout[1]+(q[1]-scout[1])*move/dist];
 draw();if(path.length)anim=requestAnimationFrame(tick);
}
async function open(){
 root.hidden=false;button.hidden=true;size();
 if(!inflight)inflight=(async()=>{
  const resp=await fetch('generated/v268-matrei/manifest.json',{cache:'no-store'});if(!resp.ok)throw Error('Missing geographic manifest '+resp.status);
  manifest=await resp.json();
  if(manifest.schema!=='coe-v268-matrei-continuous/v1'||manifest.cells.length!==4)throw Error('Incorrect geographic batch');
  images=await Promise.all(manifest.cells.map(a=>new Promise((resolve,reject)=>{
   const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(Error('Missing art '+a.art));img.src='generated/v268-matrei/'+a.art;
  })));
  const mask=new Image();mask.src='generated/v268-matrei/slope-candidate-mask.png';await mask.decode();
  const b=document.createElement('canvas');b.width=mask.naturalWidth;b.height=mask.naturalHeight;
  const cx=b.getContext('2d',{willReadFrequently:true});cx.drawImage(mask,0,0);surface={width:b.width,height:b.height,data:cx.getImageData(0,0,b.width,b.height).data};
  loaded=true;fit();say('Real Matrei DEM: 4 adjacent terrain images & 3D meshes. Tap ground for experimental scout; drag to pan.');
 })().catch(e=>{inflight=null;say('Geographic build unavailable: '+e.message)});
 await inflight;draw();
}
button.onclick=open;
root.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>{
 const a=b.dataset.action;if(a==='close'){root.hidden=true;button.hidden=false;if(anim)cancelAnimationFrame(anim);anim=0;return}
 if(a==='whole')fit();else{scale=Math.min(2,Math.max(.07,scale*(a==='plus'?1.35:1/1.35)));draw()}
});
c.addEventListener('pointerdown',e=>{c.setPointerCapture(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);moved=0});
c.addEventListener('pointermove',e=>{
 if(!pointers.has(e.pointerId))return;
 const p=pointers.get(e.pointerId),dx=e.clientX-p[0],dy=e.clientY-p[1];moved+=Math.hypot(dx,dy);pointers.set(e.pointerId,[e.clientX,e.clientY]);
 if(pointers.size===1)center=[center[0]-dx/scale,center[1]-dy/scale];
 else scale=Math.min(2,Math.max(.07,scale*(1+dy/700)));
 draw();
});
c.addEventListener('pointerup',e=>{pointers.delete(e.pointerId);if(loaded&&moved<9&&pointers.size===0){const r=c.getBoundingClientRect();order(world([e.clientX-r.left,e.clientY-r.top]))}});
c.addEventListener('pointercancel',e=>pointers.delete(e.pointerId));
c.addEventListener('wheel',e=>{e.preventDefault();scale=Math.min(2,Math.max(.07,scale*(e.deltaY<0?1.1:.9)));draw()},{passive:false});
window.addEventListener('resize',()=>{if(!root.hidden)size()});
window.COEGeoV268={open,get state(){return {loaded,cellCount:manifest?.cells.length||0,approved:false,scout:scout.slice()}}};
if(new URLSearchParams(location.search).get('geoPilot')==='1')open();
})();