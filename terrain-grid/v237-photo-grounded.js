/* V237: two distinct CC0 source-photo native crops, NOT historic route proof.
 * Images are generated with pinned original SHA1 and attributed in QA manifest.
 * No Matrei pixels or V121/V123 road graph modifications.
 */
(function(root){
 'use strict';
 const ROAD={
  west:[[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],[980,515],[890,535],[784,551],[680,560],[570,540],[470,520],[370,522],[275,550]],
  south:[[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],[700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]]
 };
 const hash=(pts)=>{let h=2166136261;for(const c of JSON.stringify(pts))h=Math.imul(h^c.charCodeAt(0),16777619)>>>0;return h.toString(16)};
 const expected={west:'a716b11c',south:'c0491522'};
 const imgs={};let loaded=0;
 for(const id of ['west','south']){
  const data=root['V237'+id[0].toUpperCase()+id.slice(1)+'Data'];
  if(typeof data!=='string'||!data.startsWith('data:image/webp;base64,'))throw Error('V237 missing licensed image '+id);
  const img=new Image();imgs[id]=img;
  img.onload=()=>{loaded++;if(typeof window==='object')window.dispatchEvent(new Event('resize'))};
  img.onerror=()=>{throw Error('V237 image decode failed '+id)};
  img.src=data;
 }
 function paint(ctx,atlas){
  if(!atlas||atlas.productionApproved!==false||atlas.tiles.length!==3)throw Error('V237 requires unapproved V123 atlas');
  for(const id of ['west','south']){
   const t=atlas.tiles.find(x=>x.id===id),key=id==='west'?'east':'north';
   if(!t||t.width!==1536||t.height!==1024||hash(t.roads[key])!==expected[id]||
      JSON.stringify(t.roads[key])!==JSON.stringify(ROAD[id]))throw Error('V237 immutable route drift '+id);
   if(!imgs[id].complete||!imgs[id].naturalWidth)continue;
   ctx.save();ctx.translate(...t.origin);
   ctx.beginPath();ctx.moveTo(256,0);ctx.lineTo(1280,0);ctx.lineTo(1536,256);
   ctx.lineTo(1536,768);ctx.lineTo(1280,1024);ctx.lineTo(256,1024);
   ctx.lineTo(0,768);ctx.lineTo(0,256);ctx.closePath();ctx.clip();
   ctx.drawImage(imgs[id],0,0,1536,1024);ctx.restore();
  }
  return {version:237,productionApproved:false,sourceRegisteredToV123:false,
    historicalRoadsVerified:false,bridgeBanksVerified:false,
    gameArtApproved:false,humanVisualApproval:false,physicalIPhoneApproved:false};
 }
 root.V237PhotoGrounded=Object.freeze({paint,get loaded(){return loaded===2},
   sourceRegisteredToV123:false,gameArtApproved:false,productionApproved:false});
})(typeof window!=='undefined'?window:globalThis);
