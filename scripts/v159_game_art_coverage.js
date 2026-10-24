#!/usr/bin/env node
/* V159: inspect ACTUAL V137 three-game-octagon photographic footprint.
 * This is a source-coverage diagnostic, not an image-detail score, historical
 * map, road verification, or art approval. Modern V158 source sectors must
 * NEVER be counted as Matrei/Western Pass/Southern Valley game art.
 */
'use strict';
const fs=require('node:fs');
const crypto=require('node:crypto');
const PINNED={
  preview:'f926c58d9f71ea6e4de57bff3b47e225b67ecdff',
  atlas:'09f04b4062e24fbacbb645307462cdddce2b2aa3'
};
const shaBlob=s=>crypto.createHash('sha1').update('blob '+Buffer.byteLength(s)+'\0'+s).digest('hex');
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const ORIGINS={west:[0,0],matrei:[1536,0],south:[1536,1024]};
function extract(preview,atlas,{pinned=true}={}){
  if(typeof preview!=='string'||typeof atlas!=='string')throw Error('UTF-8 source required');
  if(pinned&&(shaBlob(preview)!==PINNED.preview||shaBlob(atlas)!==PINNED.atlas))
    throw Error('Unreviewed V137/V123 code change: source identity drift');
  const polyMatch=preview.match(/const poly=(\[\[[^;\n]+\]\]);/);
  if(!polyMatch)throw Error('V137 photo boundary missing');
  const poly=JSON.parse(polyMatch[1]);
  if(poly.length!==8||poly.some(p=>!Array.isArray(p)||p.length!==2||p.some(v=>!Number.isInteger(v))))
    throw Error('Unexpected Matrei photo polygon');
  const matches=[...preview.matchAll(/drawImage\(centerPhoto,([^)]*)\)/g)];
  if(matches.length!==1||matches[0][1]!=='1536,0,W,H')
    throw Error('Original Matrei photo must appear once at unchanged game origin');
  if(!preview.includes('smooth((d-14)/230)')||!preview.includes('const W=1536,H=1024'))
    throw Error('Original photographic feather/dimensions not independently understood');
  if(!preview.includes('center.putImageData(im,0,0)'))throw Error('Photo alpha source missing');
  for(const [id,origin] of Object.entries(ORIGINS)){
    const pattern=new RegExp("id:'"+id+"'[^\\n]*origin:\\["+origin.join(',')+"\\]");
    if(!pattern.test(atlas))throw Error('V123 tile origin changed: '+id);
  }
  if(!atlas.includes('productionApproved:false')||!preview.includes('get productionApproved(){return false}'))
    throw Error('Unreviewed preview/game release flag');
  return poly;
}
function signedEdge(poly,x,y){
  let nearest=Infinity;
  for(let i=0;i<poly.length;i++){
    const a=poly[(i+poly.length-1)%poly.length],b=poly[i];
    const dx=b[0]-a[0],dy=b[1]-a[1];
    const d=(-dy*(x-a[0])+dx*(y-a[1]))/Math.hypot(dx,dy);
    nearest=Math.min(nearest,d);
  }
  return nearest;
}
function tileCoverage(poly,tile,nx=64,ny=48){
  if(!(tile in ORIGINS))throw Error('Unknown game octagon');
  if(!Number.isInteger(nx)||!Number.isInteger(ny)||nx<8||ny<8)throw Error('Invalid coverage grid');
  let count=0,sum=0,opaque=0;
  for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
    const x=(i+.5)*1536/nx,y=(j+.5)*1024/ny;
    if(signedEdge(poly,x,y)<0)continue;
    count++;
    // V137 draws ONE source painting at Matrei world origin. Neither
    // neighboring tile has this image. Do not infer other art quality.
    const a=tile==='matrei'?smooth((signedEdge(poly,x,y)-14)/230):0;
    sum+=a;
    if(a>.95)opaque++;
  }
  if(!count)throw Error('No octagon samples');
  return {sampledOctagonPixels:count,meanOriginalPhotoAlpha:+(sum/count).toFixed(6),
          mostlyOpaquePhotoFraction:+(opaque/count).toFixed(6)};
}
function audit(preview,atlas,opts){
  const poly=extract(preview,atlas,opts);
  const tiles=Object.fromEntries(Object.keys(ORIGINS).map(id=>[id,tileCoverage(poly,id)]));
  return {version:159,sourcePreviewBlobSha1:shaBlob(preview),sourceAtlasBlobSha1:shaBlob(atlas),
    diagnostic:'Original V121 Matrei painting footprint only, NOT total art coverage',
    tiles,threeGameOctagonsVisuallyApproved:false,gameRouteGeoregistered:false,
    historicalRoadEvidence:false,bridgeBanksVerified:false,
    physicalIPhoneApproved:false,productionApproved:false,
    modernSourceSectorsAreNotGameOctagons:true,
    blocker:'Western Pass and Southern Valley have zero V121 source-photo footprint. Their procedural ground is not independently approved game art; V140 strict visual parity remains failed. Source imagery is not registered to V123.'};
}
function main(){
  const [previewPath,atlasPath,outPath]=process.argv.slice(2);
  if(!previewPath||!atlasPath||!outPath)throw Error('Usage: node v159_game_art_coverage.js <V137 html> <V123 atlas js> <report.json>');
  const result=audit(fs.readFileSync(previewPath,'utf8'),fs.readFileSync(atlasPath,'utf8'));
  if(result.tiles.west.meanOriginalPhotoAlpha!==0||result.tiles.south.meanOriginalPhotoAlpha!==0||
     result.tiles.matrei.meanOriginalPhotoAlpha<.2)throw Error('Unexpected original Matrei photo footprint');
  fs.mkdirSync(require('node:path').dirname(outPath),{recursive:true});
  fs.writeFileSync(outPath,JSON.stringify(result,null,2)+'\n');
  console.log('V159 PASS: source-photo footprint audited; 3 game octagons remain visually UNAPPROVED');
}
if(require.main===module)main();
module.exports={audit,extract,tileCoverage,signedEdge,shaBlob,PINNED};
