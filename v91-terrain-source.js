/* V91: zoom-aware ecological cartography for the measured DEM map.
   Game-play forest polygons and river geometry are the source; this layer is visual only.
   Existing march, river crossings, combat, saves and selections are not rewritten. */
function v91BuildWoodland(){
 const target=$('v91Woodland');
 if(!target||!atlasLandData||!V89_HEIGHT)return;
 const patch=node('g',{class:'v91-woodland-patches'});
 const trees=node('g',{class:'v91-woodland-trees'});
 const shadows=[],dark=[],light=[],trunks=[],patches=[],clearings=[];
 const alpha=atlasLandData.alpha, landW=atlasLandData.w,landH=atlasLandData.h;
 let seed=0x17809142,total=0,skipped=0;
 const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
 const fix=v=>(Math.round(v*10)/10).toString();
 const land=(x,y)=>{
  const xx=Math.round(x),yy=Math.round(y);
  return xx>=1&&yy>=1&&xx<landW-1&&yy<landH-1&&alpha[(yy*landW+xx)*4+3]>128;
 };
 const clearOfCity=(x,y)=>{
  for(const pt of Object.values(V87_CITIES)){
   const dx=x-pt[0],dy=y-pt[1];
   if(dx*dx+dy*dy<17*17)return false;
  }
  return true;
 };
 const clearOfRiver=(x,y)=>{
  for(const r of V88_RIVER_SEGMENTS)
   if(v88DistSegment(x,y,r.ax,r.ay,r.bx,r.by)<3.7)return false;
  return true;
 };
 for(let zone=0;zone<V87_FORESTS.length;zone++){
  const [cx,cy,rx,ry]=V87_FORESTS[zone];
  // Broken irregular forest stands, not one artificial circular dark blob.
  const standCount=Math.min(27,Math.max(11,Math.round(rx*ry/410)));
  for(let j=0;j<standCount;j++){
   const a=rand()*Math.PI*2,r=Math.sqrt(rand())*.70;
   const x=cx+Math.cos(a)*rx*r,y=cy+Math.sin(a)*ry*r;
   if(!land(x,y)||!clearOfCity(x,y))continue;
   const rw=5+rx*(.045+rand()*.085),rh=5+ry*(.045+rand()*.085),pieces=[];
   const phase=rand()*6.28;
   for(let n=0;n<22;n++){
    const t=n/22*Math.PI*2;
    const mod=1+.18*Math.sin(3*t+phase)+.12*Math.cos(5*t-phase)+.08*Math.sin(9*t);
    pieces.push(fix(x+Math.cos(t)*rw*mod)+' '+fix(y+Math.sin(t)*rh*mod));
   }
   patches.push('M'+pieces.join('L')+'Z');
   if(rand()<.27)clearings.push('M'+fix(x-2)+' '+fix(y)+'q3 -2 6 0q-3 2 -6 0Z');
  }
  // Keep tree placement deterministic and consistent with terrain classification:
  // all tree sites lie inside the SAME existing forest ellipses used for combat.
  const n=Math.min(360,Math.max(75,Math.round(rx*ry/23)));
  for(let i=0;i<n;i++){
   const a=rand()*Math.PI*2,r=Math.sqrt(rand())*.80;
   const x=cx+Math.cos(a)*rx*r,y=cy+Math.sin(a)*ry*r;
   if(!land(x,y)||!clearOfCity(x,y)||!clearOfRiver(x,y)){skipped++;continue;}
   const height=v89ElevationAt(x,y);
   if(height>1650||v89SlopeAt(x,y)>49){skipped++;continue;}
   const px=fix(x),py=fix(y),scale=.23+rand()*.23;
   const shade=rand()>.45,conifer=height>500||cy<480||rand()<.30;
   if(conifer){
    const top=fix(y-3.4*scale),lower=fix(y+1.65*scale);
    const d='M'+px+' '+top+
     'l-'+fix(1.5*scale)+' '+fix(2.3*scale)+
     'l'+fix(.7*scale)+' 0l-'+fix(1.7*scale)+' '+fix(2.1*scale)+
     'l'+fix(.9*scale)+' 0l-'+fix(1.25*scale)+' '+fix(2*scale)+
     'l'+fix(5.7*scale)+' 0l-'+fix(1.25*scale)+' -'+fix(2*scale)+
     'l'+fix(.9*scale)+' 0l-'+fix(1.7*scale)+' -'+fix(2.1*scale)+
     'l'+fix(.7*scale)+' 0Z';
    (shade?dark:light).push(d);
    trunks.push('M'+px+' '+lower+'v'+fix(1.0*scale));
    shadows.push('M'+fix(x-1.5*scale)+' '+fix(y+2.8*scale)+
      'q'+fix(2.3*scale)+' '+fix(1.8*scale)+' '+fix(4.4*scale)+' '+fix(.7*scale));
   }else{
    const rxTree=1.6*scale,ryTree=1.45*scale;
    const left=fix(x-rxTree),right=fix(x+rxTree),up=fix(y-ryTree*1.6),base=fix(y+ryTree*.35);
    const d='M'+left+' '+fix(y)+
     'C'+fix(x-rxTree*1.18)+' '+fix(y-ryTree*.92)+' '+fix(x-rxTree*.5)+' '+up+' '+fix(x)+' '+up+
     'C'+fix(x+rxTree*.75)+' '+fix(y-ryTree*1.77)+' '+fix(x+rxTree*1.25)+' '+fix(y-ryTree*.75)+' '+right+' '+fix(y)+
     'C'+right+' '+fix(y+ryTree*.6)+' '+left+' '+fix(y+ryTree*.7)+' '+left+' '+fix(y)+'Z';
    (shade?dark:light).push(d);
    trunks.push('M'+px+' '+base+'v'+fix(.90*scale));
    shadows.push('M'+fix(x-.8*scale)+' '+fix(y+2.3*scale)+'l'+fix(3.5*scale)+' '+fix(.9*scale));
   }
   total++;
  }
 }
 patch.appendChild(node('path',{d:patches.join(' '),class:'v91-stand-soil'}));
 patch.appendChild(node('path',{d:clearings.join(' '),class:'v91-stand-clearings'}));
 trees.appendChild(node('path',{d:shadows.join(' '),class:'v91-tree-shadow'}));
 trees.appendChild(node('path',{d:trunks.join(' '),class:'v91-tree-trunks'}));
 trees.appendChild(node('path',{d:dark.join(' '),class:'v91-tree-dark'}));
 trees.appendChild(node('path',{d:light.join(' '),class:'v91-tree-light'}));
 target.replaceChildren(patch,trees);
 target.setAttribute('mask','url(#atlasLandMask)');
 target.dataset.zoomLod=String(mapLod());
 window.__v91TerrainQA={status:'ready',forestZones:V87_FORESTS.length,
  renderedTrees:total,skippedTrees:skipped,forestPatches:patches.length,
  riverCount:V87_RIVERS.length,usesGameplayForests:true,usesGameplayRivers:true};
}
function v91EnhanceRivers(){
 // Restore geographical waterways hidden by old V83 CSS. No new fake rivers.
 const group=$('atlasRivers');
 for(const r of ATLAS_RIVERS){
  if(!r.major)continue;
  group.appendChild(node('path',{d:r.d,class:'v91-river-light',
   fill:'none','stroke-linecap':'round','stroke-linejoin':'round',
   'vector-effect':'non-scaling-stroke','pointer-events':'none'}));
 }
}
