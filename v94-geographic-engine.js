/* V94: a single geographic atlas for the entire playable world.
   Mapzen z8 measured DEM, Natural Earth II idealized pre-modern cover,
   Natural Earth 10m land/rivers. Historic vegetation is interpretive,
   NOT an archival forest inventory for 1780. Gameplay reads these same layers.
 */
let V94_READY=false,V94_LOADING=false,V94_FOREST=null,V94_MANIFEST=null;
const V94_RIVER_GRID=new Map(),V94_RIVER_SIZE=24;
let V94_RIVER_SEGMENTS=[],V94_TILE_LOADED=new Set();
function v94TileUpdate(){
 const parent=$('v94DetailedRelief');if(!parent||!V94_READY)return;
 // The 4×3 physical DEM tiles cover every theater region, not just Prussia.
 const width=view.w,height=width/stageAspect();
 const active=width<760;
 parent.style.display=active?'':'none';
 if(!active)return;
 const x0=view.cx-width/2,x1=view.cx+width/2;
 const y0=view.cy-height/2,y1=view.cy+height/2;
 const rectW=1448/4,rectH=1086/3;
 for(let row=0;row<3;row++)for(let col=0;col<4;col++){
  const x=col*rectW,y=row*rectH;
  if(x>x1+20||x+rectW<x0-20||y>y1+20||y+rectH<y0-20)continue;
  const id=col+'-'+row;
  if(V94_TILE_LOADED.has(id))continue;
  V94_TILE_LOADED.add(id);
  parent.appendChild(node('image',{x,y,width:rectW,height:rectH,
   href:'./terrain-v94/tiles/'+id+'.webp',preserveAspectRatio:'none','pointer-events':'none'}));
 }
}
function v94GridKey(x,y){
 return Math.floor(x/V94_RIVER_SIZE)+','+Math.floor(y/V94_RIVER_SIZE);
}
function v94AddRiverSegment(s){
 let minX=Math.floor(Math.min(s.ax,s.bx)/V94_RIVER_SIZE),
 maxX=Math.floor(Math.max(s.ax,s.bx)/V94_RIVER_SIZE);
 let minY=Math.floor(Math.min(s.ay,s.by)/V94_RIVER_SIZE),
 maxY=Math.floor(Math.max(s.ay,s.by)/V94_RIVER_SIZE);
 // long segments split at source; cap pathological polygons safely
 if(maxX-minX>8||maxY-minY>8)return;
 const idx=V94_RIVER_SEGMENTS.push(s)-1;
 for(let ix=minX;ix<=maxX;ix++)for(let iy=minY;iy<=maxY;iy++){
  const key=ix+','+iy;
  let bucket=V94_RIVER_GRID.get(key);
  if(!bucket){bucket=[];V94_RIVER_GRID.set(key,bucket)}
  bucket.push(idx);
 }
}
function v94NearbyRivers(ax,ay,bx=ax,by=ay){
 let minX=Math.floor((Math.min(ax,bx)-5)/V94_RIVER_SIZE),
 maxX=Math.floor((Math.max(ax,bx)+5)/V94_RIVER_SIZE);
 let minY=Math.floor((Math.min(ay,by)-5)/V94_RIVER_SIZE),
 maxY=Math.floor((Math.max(ay,by)+5)/V94_RIVER_SIZE);
 const res=new Set();
 for(let x=minX;x<=maxX;x++)for(let y=minY;y<=maxY;y++){
  const b=V94_RIVER_GRID.get(x+','+y);
  if(b)for(const i of b)res.add(i);
 }
 return Array.from(res,v=>V94_RIVER_SEGMENTS[v]);
}
function v94RiverCrossing(ax,ay,bx,by){
 const dx=bx-ax,dy=by-ay;
 for(const r of v94NearbyRivers(ax,ay,bx,by)){
  const ex=r.bx-r.ax,ey=r.by-r.ay,cross=dx*ey-dy*ex;
  if(Math.abs(cross)<1e-9)continue;
  const px=r.ax-ax,py=r.ay-ay;
  const t=(px*ey-py*ex)/cross,u=(px*dy-py*dx)/cross;
  if(t>.035&&t<.965&&u>=0&&u<=1)return true;
 }
 return false;
}
function v94RoadRiver(x,y){
 for(const r of v94NearbyRivers(x,y))
  if(v88DistSegment(x,y,r.ax,r.ay,r.bx,r.by)<2.25)return true;
 return false;
}
function v94WoodAt(x,y){
 const w=V94_FOREST;if(!w)return false;
 const xx=Math.min(w.width-1,Math.max(0,Math.floor(x/1448*w.width)));
 const yy=Math.min(w.height-1,Math.max(0,Math.floor(y/1086*w.height)));
 return !!w.forest[yy*w.width+xx];
}
function v94TerrainAt(x,y){
 const elev=v89ElevationAt(x,y),slope=v89SlopeAt(x,y);
 if(elev>1550||(elev>750&&slope>35))return 'mountain';
 if(elev>390||slope>24)return 'hill';
 if(v94WoodAt(x,y))return 'forest';
 if(atlasLandData?.alpha){
  const m=atlasLandData,w=m.w,h=m.h,a=m.alpha;
  for(const [dx,dy] of [[8,0],[-8,0],[0,8],[0,-8]]){
   const xx=Math.min(w-1,Math.max(0,Math.round(x+dx)));
   const yy=Math.min(h-1,Math.max(0,Math.round(y+dy)));
   if(a[(yy*w+xx)*4+3]<128)return 'coast';
  }
 }
 return 'plain';
}
function v94UpdateGameplay(){
 // Update province terrain and marching map from physical ground, not art.
 for(const b of bases)b.terrain=v94TerrainAt(b.x,b.y);
 V88_RIVER_SEGMENTS.length=0; // guard against obsolete hand-drawn crossings
}
async function v94FetchAll(){
 if(V94_LOADING||V94_READY)return;
 V94_LOADING=true;
 window.__v94TerrainQA={status:'loading'};
 try{
  const paths=['manifest.json','heights.json','woods.json','land.json','rivers.json'];
  const sources=await Promise.all(paths.map(async p=>{
   const response=await fetch('./terrain-v94/'+p,{cache:'force-cache'});
   if(!response.ok)throw Error('Missing geographic asset '+p);
   return response.json();
  }));
  const [manifest,heights,woods,land,rivers]=sources;
  if(manifest.atlasSize[0]!==8192||manifest.atlasSize[1]!==6144||
     heights.width!==512||heights.height!==384||
     heights.heights.length!==512*384||
     woods.width!==512||woods.height!==384||
     woods.forest.length!==512*384||
     !land.polygons||land.polygons.length<25||
     !rivers.rivers||rivers.rivers.length<120)throw Error('V94 geographic registration failed');
  // Decode all assets before activating so users never see half-old map layers.
  const base=new Image();base.src='./terrain-v94/overview.webp';
  await base.decode();
  if(base.naturalWidth!==4096||base.naturalHeight!==3072)
   throw Error('Invalid full theater atlas dimensions');
  V89_HEIGHT=heights;
  V94_FOREST=woods;
  V94_MANIFEST=manifest;
  V87_LAND_POLYGONS.splice(0,V87_LAND_POLYGONS.length,...land.polygons);
  const c=v87LandCanvas();
  const mask=node('mask',{id:'atlasLandMask',maskUnits:'userSpaceOnUse',
    maskContentUnits:'userSpaceOnUse',x:0,y:0,width:1448,height:1086,style:'mask-type:alpha'});
  mask.appendChild(node('image',{href:c.toDataURL('image/png'),x:0,y:0,width:1448,height:1086,preserveAspectRatio:'none'}));
  $('map').querySelector('#atlasLandMask')?.remove();
  $('map').querySelector('defs').appendChild(mask);
  const ctx=c.getContext('2d',{willReadFrequently:true});
  atlasLandData={w:1448,h:1086,alpha:ctx.getImageData(0,0,1448,1086).data};
  for(const id of ['territories','nationFrontiers','weatherLayer','terrainDetail','atlasRivers'])
   $(id).setAttribute('mask','url(#atlasLandMask)');
  drawV87Coastlines();
  ATLAS_RIVERS.splice(0,ATLAS_RIVERS.length,...rivers.rivers);
  drawAtlasRivers();
  V94_RIVER_GRID.clear();V94_RIVER_SEGMENTS=[];
  for(const river of rivers.rivers){
   // Only rivers with meaningful cartographic rank slow armies.
   if(river.rank>6)continue;
   const nums=(river.d.match(/-?\d+(?:\.\d+)?/g)||[]).map(Number);
   for(let k=2;k+1<nums.length;k+=2)
    v94AddRiverSegment({ax:nums[k-2],ay:nums[k-1],
      bx:nums[k],by:nums[k+1],name:river.name,major:river.major});
  }
  $('atlasBaseImage').setAttribute('href',base.src);
  V94_READY=true;
  $('map').classList.add('v94-terrain');
  v94UpdateGameplay();
  v94TileUpdate();
  $('roads').dataset.lod='';previousNations='';lastLod=-1;
  if(game){setView();renderAll()}
  window.__v94TerrainQA={status:'ready',atlas:[8192,6144],tiles:[4,3],
   riverPaths:rivers.rivers.length,coastPolygons:land.polygons.length,
   measuredElevation:[heights.width,heights.height],
   woodlandGrid:[woods.width,woods.height],
   indexedGameplayRiverSegments:V94_RIVER_SEGMENTS.length,
   source:manifest.vegetationSource,
   consistentGeography:true};
 }catch(e){
  console.error('V94 geography failed to load; V93 fallback remains playable',e);
  window.__v94TerrainQA={status:'unavailable',error:String(e)};
 }
}
