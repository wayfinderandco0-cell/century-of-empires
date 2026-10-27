/* V236: TWO deliberately composed fictional Alpine landscape studies.
 * No historic/geo source registration. Exact V123 route is immutable.
 * Art is not photographic, not accepted, not production. No new bridge.
 * Distinct WEST forested pass and SOUTH rocky meadow basin; all landforms are
 * authored in local tile coordinates, NOT source-photograph substitutions.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 else root.V236AuthoredAlpine=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const SIZE=[1536,1024],FALSE=Object.freeze({
  sourceRegisteredToV123:false,historicalRoadsVerified:false,
  bridgeBanksVerified:false,onwardRoadVerified:false,licenseVerified:false,
  roadClearanceVerified:false,gameArtApproved:false,humanVisualApproval:false,
  physicalIPhoneApproved:false,productionApproved:false
 });
 const ROAD={
  west:[[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],[980,515],[890,535],[784,551],[680,560],[570,540],[470,520],[370,522],[275,550]],
  south:[[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],[700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]]
 };
 const HASH={west:'a716b11c',south:'c0491522'};
 function hashPoints(points){let h=2166136261;for(const ch of JSON.stringify(points))h=Math.imul(h^ch.charCodeAt(0),16777619)>>>0;return h.toString(16);}
 function assertAtlas(atlas){
  if(!atlas||atlas.productionApproved!==false||!Array.isArray(atlas.tiles)||atlas.tiles.length!==3)throw Error('V236 requires rejected immutable V123 atlas');
  for(const id of ['west','south']){
   const t=atlas.tiles.find(t=>t.id===id);
   const name=id==='west'?'east':'north';
   if(!t||t.width!==SIZE[0]||t.height!==SIZE[1]||hashPoints(t.roads?.[name])!==HASH[id]||
      JSON.stringify(t.roads[name])!==JSON.stringify(ROAD[id]))throw Error('V236 road graph drift '+id);
  }
  return true;
 }
 const seed=(n)=>()=>{n=(Math.imul(n,1664525)+1013904223)>>>0;return n/4294967296};
 const clip=(g)=>{g.beginPath();g.moveTo(256,0);g.lineTo(1280,0);g.lineTo(1536,256);g.lineTo(1536,768);g.lineTo(1280,1024);g.lineTo(256,1024);g.lineTo(0,768);g.lineTo(0,256);g.closePath();g.clip();};
 function shape(g,points,fill,stroke,weight=1){
  g.beginPath();points.forEach((p,i)=>i?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1]));g.closePath();
  if(fill){g.fillStyle=fill;g.fill();}
  if(stroke){g.strokeStyle=stroke;g.lineWidth=weight;g.stroke();}
 }
 function dist(p,pts){
  let best=Infinity;
  for(let i=1;i<pts.length;i++){
   const a=pts[i-1],b=pts[i],dx=b[0]-a[0],dy=b[1]-a[1];
   const t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)));
   best=Math.min(best,Math.hypot(p[0]-a[0]-dx*t,p[1]-a[1]-dy*t));
  }
  return best;
 }
 function background(g,id){
  const grad=g.createLinearGradient(id==='west'?0:1536,0,id==='west'?1536:0,1024);
  const colors=id==='west'?['#62725b','#6c7953','#394b3d','#273c32']:['#53664d','#84906a','#596e4b','#3c523b'];
  colors.forEach((v,i)=>grad.addColorStop(i/3,v));g.fillStyle=grad;g.fillRect(0,0,1536,1024);
 }
 const WEST_RIDGES=[
  [[0,0],[480,0],[720,110],[650,260],[520,300],[370,215],[185,300],[0,270]],
  [[1080,0],[1536,0],[1536,345],[1400,385],[1220,270],[1100,340],[960,215]],
  [[0,680],[130,630],[330,720],[430,820],[350,1024],[0,1024]],
  [[1150,780],[1300,710],[1536,690],[1536,1024],[1060,1024]]
 ];
 const SOUTH_RIDGES=[
  [[0,0],[280,0],[350,165],[270,340],[0,450]],
  [[1020,0],[1536,0],[1536,480],[1400,430],[1230,250],[1110,320],[940,200]],
  [[0,710],[180,660],[310,740],[380,1024],[0,1024]],
  [[1200,720],[1420,630],[1536,690],[1536,1024],[1030,1024]]
 ];
 function drawRidges(g,id){
  const polygons=id==='west'?WEST_RIDGES:SOUTH_RIDGES;
  const fills=id==='west'?['#283f36','#304638','#2a4035','#334d3c']:['#425148','#444f44','#364d3b','#4d5a48'];
  for(let i=0;i<polygons.length;i++){
   const p=polygons[i];g.save();g.shadowColor='#142c21';g.shadowBlur=36;g.shadowOffsetY=19;
   shape(g,p,fills[i]);g.restore();
   shape(g,p,null,'rgba(204,196,158,.19)',2);
  }
  const facets=id==='west'?[
   [[0,0],[480,0],[650,120],[440,175],[290,115],[180,240],[0,190]],
   [[1080,0],[1300,30],[1430,260],[1230,200],[1100,340],[1000,170]],
   [[0,700],[190,685],[300,780],[250,930],[0,860]]
  ]:[
   [[1020,0],[1270,40],[1390,245],[1320,360],[1200,210],[1110,320],[940,200]],
   [[1050,800],[1250,720],[1440,680],[1536,770],[1500,920],[1210,900]],
   [[0,0],[200,0],[300,130],[200,270],[70,220]]
  ];
  facets.forEach((p,i)=>shape(g,p,i===1?'rgba(182,169,143,.18)':'rgba(193,185,157,.13)'));
  // Geologically meaningful exposed scree only on hand-authored rocky slopes.
  const scree=id==='west'?[[1150,130,125,80],[240,800,150,120],[1430,730,120,90]]:
                             [[1220,210,250,170],[1330,830,220,130],[130,150,120,90]];
  const rand=seed(id==='west'?521:847);
  for(const [cx,cy,rx,ry] of scree){
   for(let i=0;i<380;i++){
    const a=rand()*Math.PI*2,r=Math.sqrt(rand()),x=cx+Math.cos(a)*rx*r,y=cy+Math.sin(a)*ry*r;
    if(x<0||x>1536||y<0||y>1024||dist([x,y],ROAD[id])<65)continue;
    const size=1.4+rand()*6.2;
    g.fillStyle=rand()>.42?'rgba(200,194,165,.58)':'rgba(33,40,33,.45)';
    g.beginPath();g.moveTo(x-size,y+size*.35);g.lineTo(x+size*.7,y-size*.55);
    g.lineTo(x+size,y+size*.65);g.closePath();g.fill();
   }
  }
 }
 function paintTerrace(g,id){
  // The ground under the immutable cartway is a carved, narrow sloping terrace.
  // This is a fictional landform, not a new route or a certified traversable bank.
  const pts=ROAD[id];g.save();g.lineCap='round';g.lineJoin='round';
  const trace=(width,color,dy=0)=>{
   g.beginPath();pts.forEach((p,i)=>i?g.lineTo(p[0],p[1]+dy):g.moveTo(p[0],p[1]+dy));
   g.lineWidth=width;g.strokeStyle=color;g.stroke();
  };
  trace(51,'rgba(26,40,31,.30)',12);
  trace(43,'rgba(152,143,102,.23)',4);
  trace(37,'rgba(169,155,113,.32)',-3);
  trace(30,'rgba(102,110,77,.55)',0);
  g.restore();
 }
 function tree(g,x,y,r,tint){
  // Directionally lit layered crowns, with explicit trunk and self-shadow.
  g.save();g.translate(x,y);
  g.fillStyle='rgba(14,26,21,.43)';g.beginPath();g.ellipse(r*.3,r*.45,r*.85,r*.48,-.24,0,Math.PI*2);g.fill();
  g.strokeStyle='#3b3326';g.lineWidth=Math.max(1,r*.10);g.beginPath();g.moveTo(0,r*.5);g.lineTo(-r*.12,-r*.6);g.stroke();
  const levels=[1,.76,.52];levels.forEach((v,i)=>{
   const yy=r*(.25-i*.37),w=r*(.78-i*.17);
   g.beginPath();g.moveTo(-w,yy+r*.14);g.lineTo(-w*.65,yy-r*.35);
   g.lineTo(-w*.30,yy-r*.23);g.lineTo(0,yy-r*.92);
   g.lineTo(w*.38,yy-r*.2);g.lineTo(w*.7,yy-r*.35);
   g.lineTo(w,yy+r*.14);g.closePath();
   g.fillStyle=i===0?'#1c382d':i===1?tint:'#5b7554';g.fill();
   g.strokeStyle='rgba(13,29,23,.55)';g.lineWidth=.65;g.stroke();
   g.strokeStyle='rgba(151,172,120,.28)';g.lineWidth=.7;
   g.beginPath();g.moveTo(-w*.45,yy-r*.15);g.lineTo(-w*.08,yy-r*.55);g.stroke();
  });g.restore();
 }
 const GROVES={
  west:[[245,220,330,220,145],[1140,190,270,190,115],[100,800,310,210,115],[1350,805,280,180,100],[600,130,240,100,65]],
  south:[[180,145,220,145,85],[1330,190,260,190,95],[1400,860,240,130,95],[145,850,245,180,100],[910,150,170,100,45]]
 };
 function forest(g,id){
  const rand=seed(id==='west'?39073:60491);
  for(const [cx,cy,rx,ry,count] of GROVES[id]){
   for(let i=0;i<count;i++){
    const angle=rand()*2*Math.PI,rad=Math.sqrt(rand()),x=cx+Math.cos(angle)*rad*rx,y=cy+Math.sin(angle)*rad*ry;
    if(x<10||x>1526||y<10||y>1014||dist([x,y],ROAD[id])<49)continue;
    const r=8+rand()*13;tree(g,x,y,r,rand()>.5?'#294a38':'#38593f');
   }
  }
 }
 function meadow(g,id){
  // Non-repeating botanically placed meadow clusters, not image-wide noise.
  const rand=seed(id==='west'?72343:93483);
  const centers=id==='west'?[[600,600,310,160],[1000,700,220,150],[450,420,180,110]]:
   [[420,600,270,170],[850,690,350,220],[940,350,260,100]];
  for(const [cx,cy,rx,ry] of centers){
   for(let i=0;i<440;i++){
    const a=rand()*Math.PI*2,r=Math.sqrt(rand()),x=cx+Math.cos(a)*rx*r,y=cy+Math.sin(a)*ry*r;
    if(dist([x,y],ROAD[id])<27)continue;
    const s=.8+rand()*3.2;g.strokeStyle=rand()>.4?'rgba(209,193,128,.42)':'rgba(32,63,40,.45)';
    g.lineWidth=.55;g.beginPath();g.moveTo(x,y);g.lineTo(x+s*.2,y-s);g.lineTo(x+s*.7,y-s*.8);g.stroke();
   }
  }
 }
 function landscape(g,t){
  const id=t.id;g.save();g.translate(...t.origin);clip(g);
  background(g,id);drawRidges(g,id);
  // Hand-shaped terraces follow exact route *before* placing vegetation.
  paintTerrace(g,id);meadow(g,id);forest(g,id);
  // Sparse geological contour highlights; no modern buildings or water crossings.
  const strokes=id==='west'?[
   [[10,340],[210,355],[350,300],[500,320]],[[1050,90],[1180,135],[1310,270],[1500,315]],
   [[0,905],[160,880],[290,940]]]:[
   [[1080,70],[1210,160],[1320,300],[1510,420]],
   [[1000,900],[1160,820],[1330,800],[1490,860]],[[0,320],[160,260],[250,300]]];
  g.strokeStyle='rgba(219,208,170,.19)';g.lineWidth=2;
  strokes.forEach(pts=>{g.beginPath();pts.forEach((p,i)=>i?g.lineTo(...p):g.moveTo(...p));g.stroke();});
  g.restore();
 }
 function paint(ctx,atlas){
  assertAtlas(atlas);
  if(!ctx||typeof ctx.save!=='function'||typeof ctx.createLinearGradient!=='function')throw Error('V236 canvas context required');
  for(const id of ['west','south'])landscape(ctx,atlas.tiles.find(t=>t.id===id));
  return Object.freeze({cells:2,version:236,kind:'FICTIONAL_AUTHORED_ALPINE_STUDY',...FALSE});
 }
 return Object.freeze({version:236,paint,assertAtlas,hashPoints,ROAD,approvals:FALSE});
});