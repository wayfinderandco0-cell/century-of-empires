#!/usr/bin/env node
'use strict';
// V126: pin the *actual painted source* to its graph. Equality does not
// certify road placement, river crossings, historical accuracy, or iPhone QA.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p));
const manifest=JSON.parse(read('terrain-grid/octagon-1-v121.manifest.json'));
const preview=JSON.parse(read('terrain-grid/v123-preview-manifest.json'));
const art=read(manifest.art.path);
const html=read('v121-octagon-1-painted-road.html').toString('utf8');
const blobHash=crypto.createHash('sha1').update('blob '+art.length+'\0').update(art).digest('hex');
assert.equal(blobHash,manifest.art.gitBlobSha,'V121 art changed without an updated reviewed source identity');
const image=html.match(/source\.src='data:image\/webp;base64,([^']+)'/);
assert(image,'Missing embedded V121 source painting');
assert.deepEqual(Buffer.from(image[1],'base64'),art,'V121 preview painting differs from its pinned source asset');
const roadsMatch=html.match(/const ROADS=(\{[^\r\n]+\});/);
const bridgeMatch=html.match(/const BRIDGE_ENDS=(\[[^\r\n]+\]);/);
assert(roadsMatch&&bridgeMatch,'V121 road or bridge source constants missing');
const roads=JSON.parse(roadsMatch[1]);
const ends=JSON.parse(bridgeMatch[1]);
assert.deepEqual(roads,manifest.movement.roads,'Preview movement and V121 manifest road control points differ');
assert.deepEqual(ends,manifest.movement.primaryStoneBridgeEnds,'Preview bridge and source manifest differ');
const at=(a,p)=>a.findIndex(q=>q[0]===p[0]&&q[1]===p[1]);
const begin=at(roads.bridge,ends[0]),finish=at(roads.bridge,ends[1]);
assert(begin>0&&finish>begin&&finish<roads.bridge.length-1,'Bridge must have both approach roads');
for(let i=begin+1;i<=finish;i++)
 assert(roads.bridge[i][0]>roads.bridge[i-1][0],'Bridge path backtracks toward its near bank');
const atlas=require('../terrain-grid/v123-atlas.js');
const draft=atlas.create(roads);
const experiment=atlas.create(roads,{experimentalSeams:true});
assert(draft.network.seams.every(s=>!s.pass),'Unreviewed neighbor joins must remain closed');
assert(experiment.network.seams.every(s=>s.pass),'Engineering fixture must still exercise seam logic');
const westGap=Math.hypot(roads.west[0][0],roads.west[0][1]-experiment.tiles[1].roads.west[0][1]);
const southLast=roads.south.at(-1),southGap=Math.hypot(southLast[0]-experiment.tiles[1].roads.south.at(-1)[0],1024-southLast[1]);
assert(westGap>90&&southGap>60,'Re-review V121 road exits before changing source-art inset assumptions');
assert.equal(manifest.acceptance.neighborSeamVerified,false,'Source-art extensions cannot silently become approved');
assert.equal(manifest.acceptance.physicalIphoneVisualApproval,false);
assert.equal(manifest.acceptance.historicalRoadAccuracyVerified,false);
assert.equal(preview.geometry.productionEnabled,false,'Experimental boundary extensions must not reach production');
assert.equal(preview.visuals.historicalAccuracyVerified,false);
assert.equal(preview.visuals.physicalIphoneApproved,false);
assert.equal(experiment.productionApproved,false);
console.log(JSON.stringify({
 version:126,sourceArtGitBlobSha:blobHash,embeddedImageIdentical:true,
 previewRoadsIdentical:true,bridgeApproachesPresent:true,
 unpaintedSourceToPreviewBorderPx:{west:westGap,south:southGap},
 engineeringSeams:experiment.network.seams.filter(s=>s.pass).length,
 productionSeams:draft.network.seams.filter(s=>s.pass).length,
 historicalAccuracyVerified:false,physicalIphoneApproved:false,
 note:'Source/graph integrity only; bridge-road pixel alignment and neighbor paintings still require independent review.'
},null,2));
