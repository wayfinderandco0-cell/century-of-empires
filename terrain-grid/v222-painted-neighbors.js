/* V222 isolated full-cell painted Alpine material study.
 * Images are 1:1 sampled/feathered original V121 artwork, NOT geographic
 * reconstructions. No road, bridge, river or village added to game topology.
 * The source patches may include artifacts and require human visual rejection/
 * approval. Never silently substitute a blank or modern orthophoto.
 */
(function(){
 'use strict';
 const ROOT='terrain-v222/assets/';
 const FALSE=['sourceRegisteredToV123','historicRoadsVerified','periodSafe',
   'gameArtApproved','physicalIPhoneApproved','productionApproved'];
 function insist(ok,reason){if(!ok)throw Error('V222 fail-closed: '+reason);}
 function loadImage(data){
  return new Promise((resolve,reject)=>{
   const im=new Image();
   im.onload=()=>resolve(im);
   im.onerror=()=>reject(Error('V222 original painting data cannot decode'));
   im.src=data;
  });
 }
 async function load(){
  const response=await fetch(ROOT+'manifest.json',{cache:'no-store'});
  insist(response.ok,'missing audited artistic manifest');
  const m=await response.json();
  insist(m.version===222&&m.kind==='ISOLATED_ORIGINAL_MATREI_MATERIAL_QUILT_STUDY','wrong art source');
  insist(m.noModernOrthophotoUsed===true&&m.noNoiseAdded===true&&m.noUpscaling===true,'false provenance');
  insist(m.sourceMaterialNotGeography===true&&m.westSouthTerrainNotSurveyed===true,'geographic status');
  insist(m.bridgeAndRoadGeometryUnchanged===true&&m.centerMatreiArtworkUnchanged===true,'protected game');
  insist(m.humanVisualApproval===false&&m.allManmadeSourcePixelsExcluded===false,'false visual acceptance');
  for(const key of FALSE)insist(m[key]===false,'approval flag '+key);
  insist(m.nativeCellPixels[0]===1536&&m.nativeCellPixels[1]===1024,'wrong native dimensions');
  insist(m.cells.length===2&&m.cells[0].tile==='west'&&m.cells[1].tile==='south','two distinct neighbors');
  const data=[window.V222WestData,window.V222SouthData];
  insist(data.every(d=>typeof d==='string'&&d.startsWith('data:image/webp;base64,')),'missing source-derived painted art');
  const images=[];
  for(let i=0;i<2;i++){
   const im=await loadImage(data[i]);
   insist(im.naturalWidth===1536&&im.naturalHeight===1024,'image upscaled or cropped');
   insist(m.cells[i].patches.length>=100&&m.cells[i].sourceGeoregistered===false,'unverified source');
   images.push({tile:m.cells[i].tile,image:im,x:i===0?0:1536,y:i===0?0:1024});
  }
  return Object.freeze({manifest:m,images:Object.freeze(images)});
 }
 function paint(ctx,trial){
  insist(trial?.images?.length===2,'both complete painted cells required');
  for(const p of trial.images)ctx.drawImage(p.image,p.x,p.y);
 }
 window.V222PaintedNeighbors=Object.freeze({load,paint});
})();
