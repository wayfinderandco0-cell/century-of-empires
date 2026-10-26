/* V220 isolated whole-cell native photo alternative, NOT historical geography.
 * Two original, contiguous-within-source 1536x1024 2023 orthophoto mosaics.
 * The game-world placement is ARTISTIC and has NO independently verified
 * V121/V123 tiepoints. Modern paths/date marks outside V218 reviewed masks
 * may remain. Never use image-visible modern tracks as playable road graph.
 */
(function(){
 'use strict';
 const ROOT='terrain-v220/assets/';
 const FALSE=['sourceRegisteredToV123','historicRoadsVerified',
   'allModernFeaturesExcluded','periodSafe','gameArtApproved',
   'physicalIPhoneApproved','productionApproved'];
 function insist(ok,why){if(!ok)throw Error('V220 fail-closed: '+why);}
 function loadImage(url){
   return new Promise((resolve,reject)=>{
     const im=new Image();im.onload=()=>resolve(im);
     im.onerror=()=>reject(Error('V220 native source missing: '+url));
     im.src=url;
   });
 }
 async function load(){
   const response=await fetch(ROOT+'manifest.json',{cache:'no-store'});
   insist(response.ok,'source manifest unavailable');
   const m=await response.json();
   insist(m.version===220&&m.kind==='OPT_IN_CONTIGUOUS_MODERN_ORTHOPHOTO_ART_STUDY',
     'wrong study');
   insist(m.attribution==='Datenquelle: basemap.at | CC BY 4.0'&&m.sourceYear===2023,
     'source identity/attribution');
   insist(m.nativeCellPixels[0]===1536&&m.nativeCellPixels[1]===1024&&
     m.nativeTilePixels===256&&m.noUpscaling&&m.noDuplicatedSourceTiles,
     'source scale/uniqueness');
   insist(m.sourceAreasNotGameGeography===true&&
     m.contiguousWithinEachSourceCell===true&&
     m.contiguousBetweenGameCells===false&&
     m.sourceModernRoadsMayRemain===true&&
     m.unreviewedModernFeaturesMayRemain===true&&
     m.sourceQuarantineStillUnknown===true,
     'modern-source warnings');
   insist(m.centerMatreiArtworkUnchanged===true&&m.roadGraphUnchanged===true,
     'protected game invariants');
   for(const f of FALSE)insist(m[f]===false,'unapproved flag '+f);
   insist(Array.isArray(m.cells)&&m.cells.length===2,'both neighboring cells');
   const images=[],seen=new Set();
   for(const [i,e] of m.cells.entries()){
     const tile=i===0?'west':'south';
     insist(e.cell===tile&&e.artisticPlacementNotGeoregistration===true,
       'wrong placement');
     insist(e.file===tile+'-full-native-2023.webp','asset name');
     insist(e.nativePixels[0]===1536&&e.nativePixels[1]===1024&&
       e.reviewedMaskOnlyAtOrigin512===true,'source dimensions/mask claim');
     insist(e.tiles.length===24,'source mosaic not complete');
     const [x0,y0,z]=e.originXYZ;
     for(const t of e.tiles){
       insist(t.xyz[0]===x0+t.col&&t.xyz[1]===y0+t.row&&t.xyz[2]===z&&
         t.col>=0&&t.col<6&&t.row>=0&&t.row<4,'source tile not contiguous');
       const key=t.xyz.join('/');
       insist(!seen.has(key),'repeated source tile');
       seen.add(key);
     }
     const image=await loadImage(ROOT+e.file);
     insist(image.naturalWidth===1536&&image.naturalHeight===1024,
       'mosaic resized');
     images.push({tile,image,x:tile==='west'?0:1536,y:tile==='west'?0:1024});
   }
   insist(seen.size===48,'48 unique native source tiles');
   return Object.freeze({manifest:m,images:Object.freeze(images)});
 }
 function paint(ctx,trial){
   insist(trial&&trial.images.length===2,'both full source cells required');
   for(const e of trial.images){
     // No repeated stamps, stretching or invented photograph pixels.
     ctx.drawImage(e.image,e.x,e.y);
   }
 }
 window.V220NativeCells=Object.freeze({load,paint});
})();