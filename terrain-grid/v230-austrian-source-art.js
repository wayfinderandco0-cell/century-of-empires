/* V230: opt-in, original licensed Austrian source-crop terrain, ART NOT APPROVED.
 * Full-cell 1536x1024 WEST/SOUTH source crops are illustrative, not registered
 * to V123, not 1780 roads, and not proof of physical bridge banks.
 * This never edits the V121 painting, V123 network, army or saved campaigns.
 */
(function(root,factory){
 const api=factory();if(typeof module!=='undefined'&&module.exports)module.exports=api;
 else root.V230AustrianSourceArt=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const IDS=['west','south'], SIZE=[1536,1024];
 const FALSE=['sourceRegisteredToV123','historicalRoadsVerified','bridgeBanksVerified',
 'onwardRoadVerified','roadClearanceVerified','periodSafe','gameArtApproved',
 'humanVisualApproval','physicalIPhoneApproved','productionApproved'];
 const SHA=/^[a-f0-9]{64}$/;
 const requireTrue=(x,msg)=>{if(!x)throw Error('V230 source art: '+msg)};
 function verify(m){
  requireTrue(m?.version===230&&m.kind==='UNAPPROVED_ROUTE_GROUNDED_AUSTRIAN_COMPOSITION','manifest identity');
  requireTrue(m.sourceRegion==='Matrei in Osttirol, Austria','source location');
  requireTrue(m.notHistorical1780Geography===true&&m.cartwaysAndBridgeBanksNotSurveyed===true,'false geography');
  requireTrue(m.license==='CC BY-SA 4.0','license');
  requireTrue(m.sourceLandmarkTiepointsVerified===false&&m.selectionIsSemanticVerification===false,'unverified source/game registration');
  FALSE.forEach(k=>requireTrue(m[k]===false,'false approval '+k));
  requireTrue(m.sources&&Object.keys(m.sources).sort().join(',')==='south,west','exactly two sources');
  requireTrue(m.sources.west.sourceSha256!==m.sources.south.sourceSha256,'duplicate source');
  const names={west:'Guggenberg von Norden a.JPG',south:'Bichl von Nordwesten.jpg'};
  for(const id of IDS){
   const s=m.sources[id];
   requireTrue(s.title===names[id]&&s.author==='Michael Kranewitter','author/source identity '+id);
   requireTrue(s.license==='CC BY-SA 4.0'&&s.licenseUrl==='https://creativecommons.org/licenses/by-sa/4.0/','attribution '+id);
   requireTrue(SHA.test(s.sourceSha256)&&SHA.test(s.outputSha256),'hash '+id);
   requireTrue(s.nativePixels.join(',')===SIZE.join(','),'native image size '+id);
   requireTrue(Array.isArray(s.nonrepeatingGroundStrip)&&s.nonrepeatingGroundStrip.length===4,'contiguous ground source '+id);
   requireTrue(Array.isArray(s.crop)&&s.crop.length===4,'native source crop '+id);
   requireTrue(s.file===id+'-austrian-natural-cover-v230.webp','asset filename '+id);
   FALSE.forEach(k=>requireTrue(s[k]===false,'false source approval '+id+'/'+k));
  }
  return true;
 }
 async function load(){
  const res=await fetch('terrain-v230/assets/manifest.json',{cache:'no-store'});
  requireTrue(res.ok,'missing source manifest');
  const manifest=await res.json();verify(manifest);
  const images=[];
  for(const id of IDS){
   const s=manifest.sources[id],url='terrain-v230/assets/'+s.file;
   const response=await fetch(url);requireTrue(response.ok,'missing '+id+' art asset');
   const bytes=await response.arrayBuffer();
   requireTrue(globalThis.crypto?.subtle,'secure SHA-256 required');
   const digest=await crypto.subtle.digest('SHA-256',bytes);
   const hex=Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');
   requireTrue(hex===s.outputSha256,'modified art bytes '+id);
   const blob=new Blob([bytes],{type:'image/webp'}),obj=URL.createObjectURL(blob);
   try{
    const im=new Image();im.src=obj;await im.decode();
    requireTrue(im.naturalWidth===SIZE[0]&&im.naturalHeight===SIZE[1],'native dimensions '+id);
    images.push(Object.freeze({id,image:im,origin:id==='west'?[0,0]:[1536,1024]}));
   }finally{URL.revokeObjectURL(obj)}
  }
  return Object.freeze({manifest,images:Object.freeze(images),approved:false});
 }
 function paint(ctx,trial){
  requireTrue(trial?.images?.length===2&&trial.approved===false,'both unapproved neighbors required');
  for(const cell of trial.images){
   ctx.save();ctx.translate(...cell.origin);
   ctx.beginPath();ctx.moveTo(256,0);ctx.lineTo(1280,0);ctx.lineTo(1536,256);
   ctx.lineTo(1536,768);ctx.lineTo(1280,1024);ctx.lineTo(256,1024);
   ctx.lineTo(0,768);ctx.lineTo(0,256);ctx.closePath();ctx.clip();
   ctx.drawImage(cell.image,0,0,1536,1024);ctx.restore();
  }
 }
 return Object.freeze({load,paint,verify});
});