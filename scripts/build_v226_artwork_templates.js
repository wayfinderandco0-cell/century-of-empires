#!/usr/bin/env node
'use strict';
/* Build deterministic, transparent ARTWORK AUTHORING overlays from immutable
 * V121/V123 geometry. Not game road changes or proof of source geography.
 */
const fs=require('node:fs');
const path=require('node:path');
const cp=require('node:child_process');
const crypto=require('node:crypto');
const V123=require('../terrain-grid/v123-atlas.js');
const V226=require('../terrain-grid/v226-artwork-contract.js');
const ROOT=path.resolve(__dirname,'..');
const OUT=path.join(ROOT,'terrain-v226','templates');
const hashes={
  'v121-octagon-1-painted-road.html':'4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382',
  'terrain-grid/v123-atlas.js':'09f04b4062e24fbacbb645307462cdddce2b2aa3'
};
for(const [file,expected] of Object.entries(hashes)){
  const actual=cp.execFileSync('git',['hash-object',file],{cwd:ROOT,encoding:'utf8'}).trim();
  if(actual!==expected)throw Error('PROTECTED original source drift: '+file+' '+actual);
}
const html=fs.readFileSync(path.join(ROOT,'v121-octagon-1-painted-road.html'),'utf8');
const m=html.match(/const ROADS=(\{[^\r\n]+\});/);
if(!m)throw Error('Original V121 road declaration missing');
const atlas=V123.create(JSON.parse(m[1]),{experimentalSeams:true});
if(!atlas.network.seams.every(s=>s.pass))throw Error('Original V123 seam graph failed');
const contract=V226.build(atlas);
const sha256=x=>crypto.createHash('sha256').update(x).digest('hex');
const output={};
for(const cell of contract.cells)output[cell.id+'-clearance.svg']=V226.svg(cell)+'\n';
const manifest={
  version:226,kind:'ARTWORK_AUTHORING_ONLY_NOT_GAME_ART',
  source:'V121 protected source and V123 immutable road graph',
  protectedGitBlobSha1:hashes,
  dimensions:[1536,1024],cells:contract.cells.map(c=>({
    id:c.id,origin:c.origin,road:c.road,points:c.points,
    join:c.join,unverifiedTerminus:c.unverifiedTerminus,
    sourceRegisteredToV123:false,bridgeBanksVerified:false,
    onwardRoadVerified:false,gameArtApproved:false
  })),
  artClearanceWidthPixels:52,actualRoadPaintWidthPixels:22,
  artClearanceIsNotPlayableRoad:true,
  generatedFiles:Object.fromEntries(Object.entries(output).map(([n,v])=>[n,sha256(v)])),
  independentGeographicTiepointsVerified:false,
  historicRoadsVerified:false,periodSafe:false,gameArtApproved:false,
  physicalIPhoneApproved:false,productionApproved:false
};
output['contract.json']=JSON.stringify(manifest,null,2)+'\n';
const verify=process.argv.includes('--verify');
if(!verify)fs.mkdirSync(OUT,{recursive:true});
for(const [name,body] of Object.entries(output)){
  const file=path.join(OUT,name);
  if(verify){
    if(!fs.existsSync(file)||fs.readFileSync(file,'utf8')!==body)
      throw Error('V226 generated template missing/drifted: '+name);
  }else fs.writeFileSync(file,body);
}
console.log('V226 immutable artwork templates '+(verify?'verified':'generated')+
  ': west/south; 2 exact paths; no false geography/approval');
