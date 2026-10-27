/* V227: isolated, opt-in full-cell original artwork ingestion.
 * No server uploads, no paid services, no changes to V121/V123/V94/saves.
 * A local image is NOT license proof, 1780 geography, surveyed road clearance,
 * human visual acceptance, or production approval. All such gates stay false.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 else root.V227ArtIngest=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const SIZE=[1536,1024],IDS=['west','south'],MAX_BYTES=20*1024*1024;
 const origins=Object.freeze({west:[0,0],south:[1536,1024]});
 const lockedRoadHash=Object.freeze({west:'a716b11c',south:'c0491522'});
 function hashPoints(points){let h=2166136261;for(const ch of JSON.stringify(points))h=Math.imul(h^ch.charCodeAt(0),16777619)>>>0;return h.toString(16)}
 const records=new Map();
 const FALSE=Object.freeze({
  sourceRegisteredToV123:false,historicalRoadsVerified:false,
  bridgeBanksVerified:false,onwardRoadVerified:false,
  roadClearanceVerified:false,periodSafe:false,licenseVerified:false,
  humanVisualApproval:false,physicalIPhoneApproved:false,productionApproved:false
 });
 function assert(x,msg){if(!x)throw Error('V227 art import: '+msg)}
 function validateContract(contract){
  assert(contract&&contract.version===226&&contract.productionApproved===false,'immutable V226 contract required');
  assert(Array.isArray(contract.cells)&&contract.cells.length===2,'exactly two neighbor cells');
  for(const id of IDS){
   const cell=contract.cells.find(c=>c.id===id);
   assert(cell&&JSON.stringify(cell.origin)===JSON.stringify(origins[id]),id+' origin');
   assert(cell.width===SIZE[0]&&cell.height===SIZE[1],id+' dimensions');
   assert(cell.productionApproved===false&&cell.sourceRegisteredToV123===false,id+' false approval');
   assert(cell.points?.length===(id==='west'?13:12),id+' original path');
   assert(cell.points.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)),id+' path coordinates');
   assert(hashPoints(cell.points)===lockedRoadHash[id],id+' immutable V123 interior route drift');
  }
  return true;
 }
 function validateFile(id,file){
  assert(IDS.includes(id),'unknown cell');
  assert(file&&typeof file.arrayBuffer==='function','File or Blob required');
  assert(file.size>100&&file.size<=MAX_BYTES,'file size must be 100 bytes to 20 MiB');
  assert(['image/png','image/jpeg','image/webp'].includes(file.type),'PNG, JPEG or WebP only');
 }
 async function digest(bytes){
  const cryptoApi=globalThis.crypto;
  assert(cryptoApi?.subtle,'secure-context SHA-256 required');
  const result=await cryptoApi.subtle.digest('SHA-256',bytes);
  return Array.from(new Uint8Array(result),v=>v.toString(16).padStart(2,'0')).join('');
 }
 async function decode(file){
  if(typeof createImageBitmap==='function')return await createImageBitmap(file);
  assert(typeof Image==='function'&&typeof URL!=='undefined','image decoder unavailable');
  const url=URL.createObjectURL(file);
  try{
   return await new Promise((resolve,reject)=>{
    const im=new Image();im.onload=()=>resolve(im);
    im.onerror=()=>reject(Error('V227 image decode failed'));im.src=url;
   });
  }finally{URL.revokeObjectURL(url)}
 }
 async function importFile(id,file,contract,options={}){
  validateContract(contract);validateFile(id,file);
  assert(options&&typeof options==='object','options object');
  assert(options.productionApproved!==true&&options.sourceRegisteredToV123!==true,'false approval flags');
  const sha256=await digest(await file.arrayBuffer());
  if(options.expectedSha256){
   assert(/^[a-f0-9]{64}$/.test(options.expectedSha256),'invalid expected SHA-256');
   assert(sha256===options.expectedSha256,'source SHA-256 mismatch');
  }
  const image=await decode(file);
  const w=image.naturalWidth||image.width,h=image.naturalHeight||image.height;
  if(w!==SIZE[0]||h!==SIZE[1]){
   if(typeof image.close==='function')image.close();
   throw Error('V227 art import: must be exactly 1536x1024, got '+w+'x'+h);
  }
  const prior=records.get(id);
  if(prior?.image&&typeof prior.image.close==='function')prior.image.close();
  const record=Object.freeze({
   id,origin:origins[id].slice(),image,sha256,bytes:file.size,
   filename:String(file.name||'local-artwork'),dimensions:SIZE.slice(),
   provenance:String(options.provenance||'LOCAL_UNVERIFIED_ARTWORK'),
   ...FALSE
  });
  records.set(id,record);
  return publicRecord(record);
 }
 function publicRecord(r){
  if(!r)return null;
  const {image,...rest}=r;return {...rest};
 }
 function snapshot(){
  return Object.freeze({version:227,kind:'UNAPPROVED_LOCAL_ARTWORK_STUDY',
   cells:IDS.map(id=>publicRecord(records.get(id))),...FALSE});
 }
 function paint(ctx){
  assert(ctx&&typeof ctx.drawImage==='function','canvas context');
  let count=0;
  for(const id of IDS){
   const r=records.get(id);if(!r)continue;
   ctx.save();
   ctx.translate(...r.origin);
   // Exact octagon clip; no bleed into the protected Matrei tile.
   ctx.beginPath();ctx.moveTo(256,0);ctx.lineTo(1280,0);
   ctx.lineTo(1536,256);ctx.lineTo(1536,768);ctx.lineTo(1280,1024);
   ctx.lineTo(256,1024);ctx.lineTo(0,768);ctx.lineTo(0,256);
   ctx.closePath();ctx.clip();ctx.drawImage(r.image,0,0,SIZE[0],SIZE[1]);
   ctx.restore();count++;
  }
  return count;
 }
 function reset(id){
  if(id!==undefined)assert(IDS.includes(id),'unknown cell');
  for(const key of (id?[id]:IDS)){
   const old=records.get(key);
   if(old?.image&&typeof old.image.close==='function')old.image.close();
   records.delete(key);
  }
 }
 return Object.freeze({version:227,validateContract,validateFile,importFile,
  paint,reset,snapshot,get approvals(){return FALSE}});
});
