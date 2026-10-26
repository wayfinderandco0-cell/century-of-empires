/* V224: opt-in, source-attributed oblique natural-cover art, NOT Austrian geography.
 * V123 graph and V121 Matrei remain unchanged. Human/production acceptance RED.
 */
(function(){
 'use strict';
 const FALSE=['sourceRegisteredToV123','historicRoadsVerified','periodSafe','gameArtApproved',
   'physicalIPhoneApproved','productionApproved','bridgeBanksVerified'];
 const insist=(ok,msg)=>{if(!ok)throw Error('V224 fail closed: '+msg)};
 const decode=data=>new Promise((resolve,reject)=>{
  const im=new Image();im.onload=()=>resolve(im);
  im.onerror=()=>reject(Error('V224 source-derived art image failed to decode'));
  im.src=data;
 });
 async function load(){
  const response=await fetch('terrain-v224/assets/manifest.json',{cache:'no-store'});
  insist(response.ok,'licensed source manifest missing');
  const m=await response.json();
  insist(m.version===224&&m.kind==='ISOLATED_LICENSED_OBLIQUE_NATURAL_COVER_ART_STUDY','source identity');
  insist(m.sourceMaterialNotGeography===true&&m.actualSourceRegion.startsWith('Sharr Mountains, Kosovo'),'false Austrian georegistration');
  insist(m.originalMatreiArtworkUnchanged===true&&m.V123MovementGraphUnchanged===true,'protected game');
  insist(m.knownModernRoadVisibleInSouth===true&&m.modernFeaturesFullyExcluded===false,'concealed modern road');
  insist(m.humanVisualApproval===false&&m.nativeCellPixels.join(',')==='1536,1024','false approval or size');
  FALSE.forEach(k=>insist(m[k]===false,'approval flag '+k));
  insist(m.sources.length===2&&m.sources[0].tile==='west'&&m.sources[1].tile==='south','both neighbors');
  insist(m.sources[0].sourceSha256!==m.sources[1].sourceSha256,'duplicate source');
  const data=[window.V224WestData,window.V224SouthData];
  insist(data.every(s=>typeof s==='string'&&s.startsWith('data:image/webp;base64,')),'missing images');
  const images=[];
  for(let i=0;i<2;i++){
   const src=m.sources[i];
   insist(src.license==='CC BY 4.0'&&src.author==='SUHEJLO'&&src.historicalGeographyVerified===false,'missing attribution');
   const im=await decode(data[i]);
   insist(im.naturalWidth===1536&&im.naturalHeight===1024,'non-native cell');
   images.push({tile:src.tile,image:im,x:i===0?0:1536,y:i===0?0:1024});
  }
  return Object.freeze({manifest:m,images:Object.freeze(images)});
 }
 function paint(ctx,trial){insist(trial?.images?.length===2,'both complete cells required');
  for(const p of trial.images)ctx.drawImage(p.image,p.x,p.y);
 }
 window.V224LicensedObliqueNeighbors=Object.freeze({load,paint});
})();
