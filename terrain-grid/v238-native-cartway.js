/* V238 photographic source-native cartway study. Both image data files are
 * generated only after independent ground clearance. Never historical proof.
 * Original V123 roads, Matrei, campaign and sprites are immutable.
 */
(function(root){
'use strict';
const ROAD={
 west:[[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],[980,515],[890,535],[784,551],[680,560],[570,540],[470,520],[370,522],[275,550]],
 south:[[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],[700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]]
};
const hash=pts=>{let h=2166136261;for(const c of JSON.stringify(pts))h=Math.imul(h^c.charCodeAt(0),16777619)>>>0;return h.toString(16)};
const EXPECT={west:'a716b11c',south:'c0491522'};
const images={};let loaded=0;
for(const id of ['west','south']){
 const data=root['V238'+id[0].toUpperCase()+id.slice(1)+'Data'];
 if(typeof data!=='string'||!data.startsWith('data:image/webp;base64,'))throw Error('Missing V238 gated art '+id);
 const img=new Image();images[id]=img;
 img.onload=()=>{loaded++;if(typeof window==='object')window.dispatchEvent(new Event('resize'))};
 img.onerror=()=>{throw Error('V238 image decode failed '+id)};
 img.src=data;
}
function paint(ctx,atlas){
 if(!atlas||atlas.productionApproved!==false||atlas.tiles.length!==3)throw Error('V238 requires unapproved V123 atlas');
 for(const id of ['west','south']){
  const t=atlas.tiles.find(x=>x.id===id),key=id==='west'?'east':'north';
  if(!t||t.width!==1536||t.height!==1024||hash(t.roads[key])!==EXPECT[id]||
      JSON.stringify(t.roads[key])!==JSON.stringify(ROAD[id]))throw Error('V238 immutable route drift '+id);
  if(!images[id].complete||!images[id].naturalWidth)continue;
  ctx.save();ctx.translate(...t.origin);
  ctx.beginPath();ctx.moveTo(256,0);ctx.lineTo(1280,0);ctx.lineTo(1536,256);
  ctx.lineTo(1536,768);ctx.lineTo(1280,1024);ctx.lineTo(256,1024);
  ctx.lineTo(0,768);ctx.lineTo(0,256);ctx.closePath();ctx.clip();
  ctx.drawImage(images[id],0,0,1536,1024);ctx.restore();
 }
 return {version:238,productionApproved:false,sourceRegisteredToV123:false,
  historicalRoadsVerified:false,bridgeBanksVerified:false,gameArtApproved:false,
  humanVisualApproval:false,physicalIPhoneApproved:false};
}
root.V238NativeCartway=Object.freeze({paint,get loaded(){return loaded===2},
 productionApproved:false,sourceRegisteredToV123:false,gameArtApproved:false});
})(typeof window!=='undefined'?window:globalThis);
