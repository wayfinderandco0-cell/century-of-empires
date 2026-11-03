/* V269: reversible four-cell terrain-movement LAB, not approved campaign or historical travel.
   Uses actual V268 same-source slope pixels to block steep ground. Water data remains
   UNKNOWN: demonstrator orders are simulated and never write V94/V123 saves.
   Keep road/river/history certification separate from a working native-game prototype.
*/
(function(root){
"use strict";
if(new URLSearchParams(root.location.search).get("v269Explore")!=="1")return;
const PREFIX="terrain-grid/v268-matrei-geographic/";
const STEP=16, COLS=3072/STEP, ROWS=2048/STEP, COUNT=COLS*ROWS;
const SLOPE_LIMIT=30; // degrees; DEM slope alone is NOT a water/bridge certification.
let enabled=false,ready=false,slopeData=null,slopeWidth=0,slopeHeight=0;
let unit=[768,512],route=[],segment=1,moving=false,lastTime=0,lastPaint=0;
let orders=0,crossings=0,visited=new Set(),lastCell=null;
const $=id=>document.getElementById(id);
const status=s=>{if($("atlasStatus"))$("atlasStatus").textContent=s;};
const controls=$("atlasFooter").querySelector("div");
const next=document.createElement("button");next.id="v269Next";next.textContent="Next terrain cell";next.hidden=true;
const halt=document.createElement("button");halt.id="v269Halt";halt.textContent="Halt";halt.hidden=true;
controls.append(next,halt);
function repaint(){if(enabled&&root.COEAtlas?.shown)root.COEAtlas.centerAt(...root.COEAtlas.center,root.COEAtlas.zoom);}
function cell(p){const x=Math.floor(p[0]/1536),y=Math.floor(p[1]/1024);return x>=0&&x<2&&y>=0&&y<2?"["+x+","+y+"]":null;}
function slope(p){
 if(!slopeData||p[0]<0||p[1]<0||p[0]>=3072||p[1]>=2048)return Infinity;
 const x=Math.min(slopeWidth-1,Math.floor(p[0]/4)),y=Math.min(slopeHeight-1,Math.floor(p[1]/4));
 return slopeData[(y*slopeWidth+x)*4]*90/255;
}
function walkable(index){
 const x=index%COLS,y=Math.floor(index/COLS);
 const p=[(x+.5)*STEP,(y+.5)*STEP];
 // Five footprint samples: reject steep ground adjacent to the unit center.
 return [[0,0],[-8,0],[8,0],[0,-8],[0,8]].every(d=>slope([p[0]+d[0],p[1]+d[1]])<=SLOPE_LIMIT);
}
function indexAt(p){return Math.floor(p[1]/STEP)*COLS+Math.floor(p[0]/STEP);}
function centerOf(i){return [(i%COLS+.5)*STEP,(Math.floor(i/COLS)+.5)*STEP];}
function nearestOpen(p){
 if(!p||p[0]<0||p[1]<0||p[0]>=3072||p[1]>=2048)return -1;
 const cx=Math.floor(p[0]/STEP),cy=Math.floor(p[1]/STEP);
 let best=-1,score=Infinity;
 for(let r=0;r<=20;r++){
  for(let dy=-r;dy<=r;dy++)for(let dx=-r;dx<=r;dx++){
   if(Math.max(Math.abs(dx),Math.abs(dy))!==r)continue;
   const x=cx+dx,y=cy+dy;if(x<0||x>=COLS||y<0||y>=ROWS)continue;
   const i=y*COLS+x;
   if(!walkable(i))continue;
   const d=dx*dx+dy*dy;if(d<score){score=d;best=i;}
  }
  if(best>=0)return best;
 }
 return -1;
}
function plan(start,goal){
 const a=nearestOpen(start),b=nearestOpen(goal);
 if(a<0||b<0)return null;
 if(a===b)return [start,centerOf(b)];
 const cost=new Float32Array(COUNT);cost.fill(Infinity);
 const prev=new Int32Array(COUNT);prev.fill(-1);
 const seen=new Uint8Array(COUNT);
 const open=[];cost[a]=0;
 function push(node,priority){
  let k=open.length;open.push([priority,node]);
  while(k>0){const parent=(k-1)>>1;if(open[parent][0]<=priority)break;open[k]=open[parent];k=parent;}
  open[k]=[priority,node];
 }
 function pop(){
  const first=open[0],last=open.pop();if(open.length){
   let k=0;
   while(true){
    let child=2*k+1;if(child>=open.length)break;
    if(child+1<open.length&&open[child+1][0]<open[child][0])child++;
    if(open[child][0]>=last[0])break;
    open[k]=open[child];k=child;
   }open[k]=last;
  }return first[1];
 }
 const bx=b%COLS,by=Math.floor(b/COLS);
 const h=(x,y)=>Math.hypot(x-bx,y-by);
 push(a,h(a%COLS,Math.floor(a/COLS)));
 let found=false,iterations=0;
 while(open.length&&iterations++<COUNT*5){
  const u=pop();if(seen[u])continue;seen[u]=1;
  if(u===b){found=true;break;}
  const x=u%COLS,y=Math.floor(u/COLS);
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){
   if(!dx&&!dy)continue;
   const xx=x+dx,yy=y+dy;
   if(xx<0||yy<0||xx>=COLS||yy>=ROWS)continue;
   const v=yy*COLS+xx;
   if(seen[v]||!walkable(v))continue;
   // Avoid diagonal corner-cutting through a blocked cliff.
   if(dx&&dy&&(!walkable(y*COLS+xx)||!walkable(yy*COLS+x)))continue;
   const d=Math.hypot(dx,dy)*(1+slope(centerOf(v))/90);
   const proposed=cost[u]+d;
   if(proposed<cost[v]){cost[v]=proposed;prev[v]=u;push(v,proposed+h(xx,yy));}
  }
 }
 if(!found)return null;
 const path=[];let at=b;
 while(at>=0&&path.length<=COUNT){path.push(centerOf(at));if(at===a)break;at=prev[at];}
 if(at!==a)return null;
 path.reverse();path[0]=unit.slice();
 return path;
}
function setRoute(points){
 if(!points||points.length<2){status("No slope-safe route in this terrain. Try another location.");return false;}
 route=points;segment=1;moving=true;orders++;
 status("V269 sandbox marching across geographic terrain · water/bridges unverified · no campaign changes");
 repaint();return true;
}
function tapWorld(p){
 if(!enabled)return false;
 if(!cell(p)){status("Outside the four-cell terrain prototype");return false;}
 return setRoute(plan(unit,p));
}
function nextCell(){
 if(!enabled)return false;
 const c=cell(unit);
 const order=["[0,0]","[1,0]","[1,1]","[0,1]"];
 const i=order.indexOf(c);if(i<0)return false;
 const target=order[(i+1)%order.length],cx=target==="[1,0]"||target==="[1,1]"?2304:768,cy=target==="[0,1]"||target==="[1,1]"?1536:512;
 for(const offset of [[0,0],[0,-240],[0,240],[-240,0],[240,0]]){
  const p=[cx+offset[0],cy+offset[1]],candidate=plan(unit,p);
  if(candidate)return setRoute(candidate);
 }
 status("Next-cell route blocked by steep terrain; tap another location. No invented road.");
 return false;
}
function stop(){moving=false;route=[];segment=1;lastTime=0;status("V269 sandbox halted · tap terrain to give a new movement order");repaint();}
function tick(t){
 if(enabled&&moving){
  let remaining=Math.min((t-(lastTime||t))/1000,.055)*350; // pixels/s in this isolated pilot.
  while(remaining>0&&segment<route.length){
   const target=route[segment],d=Math.hypot(target[0]-unit[0],target[1]-unit[1]);
   if(d<.01){segment++;continue;}
   const take=Math.min(remaining,d);
   unit=[unit[0]+(target[0]-unit[0])*take/d,unit[1]+(target[1]-unit[1])*take/d];
   remaining-=take;if(take>=d-.001)segment++;
   const nowCell=cell(unit);
   if(nowCell&&nowCell!==lastCell){if(lastCell)crossings++;visited.add(nowCell);lastCell=nowCell;}
  }
  if(segment>=route.length){moving=false;route=[];status("Arrived in terrain cell "+(cell(unit)||"?")+" · "+visited.size+"/4 visited · experimental only");}
  if(t-lastPaint>34){repaint();lastPaint=t;}
 }
 lastTime=t;root.requestAnimationFrame(tick);
}
root.requestAnimationFrame(tick);
function draw(ctx,worldToScreen,scale){
 if(!enabled)return;
 if(route.length>1){
  ctx.save();ctx.beginPath();
  route.forEach((p,i)=>{const q=worldToScreen(p);if(i)ctx.lineTo(q[0],q[1]);else ctx.moveTo(q[0],q[1]);});
  ctx.strokeStyle="#fff0ab";ctx.lineWidth=2.8;ctx.setLineDash([7,5]);ctx.stroke();ctx.restore();
 }
 const q=worldToScreen(unit);
 ctx.save();ctx.translate(q[0],q[1]);ctx.fillStyle="#153b30";ctx.strokeStyle="#ffe0a0";
 ctx.lineWidth=2.3;ctx.beginPath();ctx.arc(0,0,12,0,Math.PI*2);ctx.fill();ctx.stroke();
 ctx.font="bold 17px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillStyle="#fff7d1";ctx.fillText("⚔",0,0);
 ctx.restore();
}
async function enable(){
 if(!root.COEV268Geo?.active)return false;
 if(!ready){
  const im=new Image();await new Promise((resolve,reject)=>{im.onload=resolve;im.onerror=()=>reject(Error("Slope PNG unavailable"));im.src=PREFIX+"slope-degrees-4x.png";});
  if(im.naturalWidth!==768||im.naturalHeight!==512)throw Error("V268 slope image dimensions changed");
  const c=document.createElement("canvas");c.width=768;c.height=512;
  const cx=c.getContext("2d",{willReadFrequently:true});cx.drawImage(im,0,0);
  slopeData=cx.getImageData(0,0,768,512).data;slopeWidth=768;slopeHeight=512;
  const anchor=nearestOpen(unit);if(anchor<0)throw Error("No measured slope-safe starting ground");
  unit=centerOf(anchor);visited=new Set([cell(unit)]);lastCell=cell(unit);ready=true;
 }
 enabled=true;next.hidden=false;halt.hidden=false;
 status("V269 FOUR-CELL MOVEMENT LAB · tap ground to march · water/historical routes not certified");
 repaint();return true;
}
function disable(){enabled=false;next.hidden=true;halt.hidden=true;moving=false;route=[];segment=1;lastTime=0;}
next.onclick=nextCell;halt.onclick=stop;
root.COEV269Explore=Object.freeze({
 get enabled(){return enabled},get ready(){return ready},get position(){return unit.slice()},
 get visitedCells(){return [...visited]},get orders(){return orders},get crossings(){return crossings},
 get moving(){return moving},get roadGraphModified(){return false},
 tapWorld,nextCell,stop,draw,enable,disable
});
})(window);
