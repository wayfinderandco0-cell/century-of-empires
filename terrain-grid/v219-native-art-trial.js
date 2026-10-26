/* V219 opt-in PHOTO MATERIAL ART STUDY. NOT V123 georegistration, 1780 geography,
   period vegetation, route survey or approved production art. 2023 native
   basemap.at CC BY 4.0 pixels. No image upscaling, duplicate stamps or roads.
   All unknown/masked pixels remain transparent over unchanged V192 ground. */
(function () {
  'use strict';
  const ROOT='terrain-v219/assets/';
  const NAMES=['west','south'];
  function reject(ok, message){if(!ok)throw Error('V219 fail-closed: '+message);}
  function image(url){
    return new Promise((resolve,rejectImage)=>{
      const img=new Image();
      img.onload=()=>resolve(img);
      img.onerror=()=>rejectImage(Error('V219 photographic asset unavailable: '+url));
      img.src=url;
    });
  }
  async function load(){
    const response=await fetch(ROOT+'manifest.json',{cache:'no-store'});
    reject(response.ok,'manifest unavailable');
    const m=await response.json();
    reject(m.version===219 && m.sourceYear===2023 && m.kind==='OPT_IN_UNREGISTERED_PHOTO_MATERIAL_ART_STUDY','manifest identity');
    reject(m.attribution==='Datenquelle: basemap.at | CC BY 4.0','source attribution');
    reject(m.noUpscaling===true && m.noDuplicatedSourcePanels===true && m.sourceQuarantineStillUnknown===true,'native-source safeguards');
    reject(m.centerMatreiArtworkUnchanged===true && m.roadGraphUnchanged===true,'game invariant');
    for(const f of ['sourceRegisteredToV123','historicRoadsVerified','periodSafe','gameArtApproved','physicalIPhoneApproved','productionApproved'])
      reject(m[f]===false,'false approval required: '+f);
    reject(Array.isArray(m.entries)&&m.entries.length===4,'exactly four independent source panels');
    const ids=new Set(),files=new Set(),perCell={west:0,south:0};
    const patches=[];
    for(const e of m.entries){
      reject(NAMES.includes(e.tile),'west/south only');
      reject(Number.isInteger(e.siteIndex)&&!ids.has(e.siteIndex),'duplicate native source');
      reject(typeof e.file==='string'&&/^site-\d\d-native-feather\.webp$/.test(e.file)&&!files.has(e.file),'asset path');
      reject(e.width===512&&e.height===512&&e.artisticPlacementNotGeoregistration===true,'unscaled, unregistered material');
      reject(Number.isInteger(e.x)&&Number.isInteger(e.y)&&e.x>=0&&e.y>=0&&e.x+512<=1536&&e.y+512<=1024,'in-bounds placement');
      ids.add(e.siteIndex);files.add(e.file);perCell[e.tile]++;
      const img=await image(ROOT+e.file);
      reject(img.naturalWidth===512&&img.naturalHeight===512,'native source dimensions');
      const origin=e.tile==='west'?[0,0]:[1536,1024];
      patches.push({tile:e.tile,siteIndex:e.siteIndex,image:img,x:e.x+origin[0],y:e.y+origin[1]});
    }
    reject(perCell.west===2&&perCell.south===2,'both neighbors require two distinct sources');
    return Object.freeze({manifest:m,patches:Object.freeze(patches)});
  }
  function paint(ctx,trial){
    reject(trial&&trial.patches.length===4,'source patches not loaded');
    for(const p of trial.patches)ctx.drawImage(p.image,p.x,p.y,512,512);
  }
  window.V219NativeArt=Object.freeze({load,paint});
})();