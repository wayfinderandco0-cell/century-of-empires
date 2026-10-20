/* V92 aerial woodland: ecological coverage stays in map coordinates,
   canopy grain is screen-scaled so it NEVER becomes giant tree glyphs.
   Decorative only: V88 river crossings, V89 DEM, roads, and game saves untouched. */
let V92_FOREST_PATTERN=null,V92_FOREST_IMAGE=null,V92_LAST_SCALE=0;
function v92ForestTile(){
 const c=document.createElement('canvas');c.width=256;c.height=256;
 const ctx=c.getContext('2d');if(!ctx)return null;
 let seed=0x92ab5178;
 const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 // Tileable top-down canopy, multiple tones and small crowns rather than flat symbols.
 const shades=['54,82,62','64,91,70','79,103,79','88,111,84','104,121,96','45,73,61','116,131,106'];
 for(let i=0;i<2100;i++){
  const x=rnd()*256,y=rnd()*256,r=.30+rnd()*1.02;
  ctx.fillStyle='rgba(65,90,72,'+(.06+rnd()*.15).toFixed(3)+')';
  ctx.beginPath();ctx.ellipse(x,y,r*2.2,r*.8,rnd()*3,0,Math.PI*2);ctx.fill();
 }
 for(let i=0;i<1430;i++){
  const x=rnd()*256,y=rnd()*256,r=1.4+rnd()*2.9;
  const color=shades[Math.floor(rnd()*shades.length)],alpha=.25+rnd()*.33;
  for(const sx of [-256,0,256])for(const sy of [-256,0,256]){
   if(x+sx< -r*2||x+sx>256+r*2||y+sy< -r*2||y+sy>256+r*2)continue;
   ctx.fillStyle='rgba(29,47,37,'+(alpha*.51).toFixed(3)+')';
   ctx.beginPath();ctx.ellipse(x+sx+1.05,y+sy+1.3,r*1.05,r*.84,.20,0,2*Math.PI);ctx.fill();
   ctx.fillStyle='rgba('+color+','+alpha.toFixed(3)+')';
   ctx.beginPath();ctx.ellipse(x+sx,y+sy,r*(.93+rnd()*.24),r*(.75+rnd()*.20),rnd()*.9,0,2*Math.PI);ctx.fill();
   ctx.fillStyle='rgba(164,172,137,'+(alpha*.20).toFixed(3)+')';
   ctx.beginPath();ctx.ellipse(x+sx-r*.30,y+sy-r*.35,r*.42,r*.27,-.3,0,2*Math.PI);ctx.fill();
  }
 }
 return c.toDataURL('image/png');
}
function v92MakeForest(){
 const target=$('v92Woodland');
 if(!target||!atlasLandData||!V89_HEIGHT)return;
 const defs=$('map').querySelector('defs');
 defs.querySelector('#v92ForestPattern')?.remove();
 const pattern=node('pattern',{id:'v92ForestPattern',patternUnits:'userSpaceOnUse',
   x:0,y:0,width:100,height:100});
 const tile=v92ForestTile();
 if(!tile)throw Error('V92 forest canopy texture unavailable');
 const img=node('image',{x:0,y:0,width:100,height:100,href:tile,
   preserveAspectRatio:'none', 'pointer-events':'none'});
 pattern.appendChild(img);defs.appendChild(pattern);
 V92_FOREST_PATTERN=pattern;V92_FOREST_IMAGE=img;V92_LAST_SCALE=0;
 let seed=0x4a27ab91,patches=[],under=[],zones=0;
 const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
 const f=x=>(Math.round(x*10)/10).toString();
 const A=atlasLandData.alpha,LW=atlasLandData.w,LH=atlasLandData.h;
 const land=(x,y)=>{x=Math.round(x);y=Math.round(y);return x>=0&&y>=0&&x<LW&&y<LH&&A[(y*LW+x)*4+3]>=128;};
 const cityClear=(x,y)=>{
  for(const point of Object.values(V87_CITIES)){
   if(Math.hypot(x-point[0],y-point[1])<10)return false;
  }
  return true;
 };
 for(const [cx,cy,rx,ry] of V87_FORESTS){
  const count=Math.max(18,Math.min(45,Math.round(rx*ry/260)));
  for(let i=0;i<count;i++){
   const angle=rand()*Math.PI*2,rad=Math.sqrt(rand())*.58;
   const x=cx+Math.cos(angle)*rad*rx,y=cy+Math.sin(angle)*rad*ry;
   if(!land(x,y)||!cityClear(x,y))continue;
   // overlapping scalloped crowns form irregular woodland polygons.
   const wide=(3+rx*(.09+rand()*.095)),tall=(3+ry*(.09+rand()*.095));
   const phase=rand()*Math.PI*2,parts=[];
   for(let j=0;j<24;j++){
    const t=j*Math.PI/12;
    const wig=1+.18*Math.sin(t*3+phase)+.11*Math.cos(t*5-phase)+.07*Math.sin(t*9+phase);
    parts.push(f(x+Math.cos(t)*wide*wig)+' '+f(y+Math.sin(t)*tall*wig));
   }
   const d='M'+parts.join('L')+'Z';
   patches.push(d);under.push(d);zones++;
  }
 }
 const bg=node('path',{d:under.join(' '),class:'v92-forest-bed'});
 const canopy=node('path',{d:patches.join(' '),class:'v92-forest-canopy',fill:'url(#v92ForestPattern)'});
 target.replaceChildren(bg,canopy);
 target.setAttribute('mask','url(#atlasLandMask)');
 target.dataset.zoomLod=String(mapLod());
 v92UpdateScale(true);
 window.__v92TerrainQA={status:'ready',forestZones:V87_FORESTS.length,
   woodlandPatches:zones,riverCount:V87_RIVERS.length,canopyMode:'fixed-screen-aerial',
   usesGameplayForests:true,usesGameplayRivers:true};
}
function v92UpdateScale(force=false){
 const p=V92_FOREST_PATTERN,img=V92_FOREST_IMAGE;
 if(!p||!img)return;
 // Pattern tile is exactly ~256 device-independent pixels at ANY camera zoom.
 const el=$('map'),cssW=el.getBoundingClientRect().width||390;
 const unit=256*view.w/cssW;
 if(!force&&Math.abs(unit/V92_LAST_SCALE-1)<.025)return;
 V92_LAST_SCALE=unit;
 for(const el of [p,img]){
  el.setAttribute('width',unit.toFixed(4));el.setAttribute('height',unit.toFixed(4));
 }
}
function v92Waterways(){
 // Game-defined river geography remains unchanged; refine visual banks only.
 const rivers=$('atlasRivers');rivers.dataset.v92='real-gameplay-routes';
}
