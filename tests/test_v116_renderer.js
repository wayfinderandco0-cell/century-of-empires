/* Node test suite for V116 seam-safe renderer and actual 48-child V115 index. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const renderer = require('../scripts/v116_local_art_renderer.js');
const index = JSON.parse(fs.readFileSync(path.join(__dirname,'../terrain-grid/v115-local-tiles-v116.json'),'utf8'));
let checks=0;
function check(name,fn){fn();checks++;console.log('PASS',name);}
check('all 48 real child tiles validated',()=>{assert.equal(renderer.validate(index).tiles.length,48);});
check('all 48 source crops stitched without seams',()=>{
  const [x0,y0,x1,y1]=index.artBoxWorldPx;
  const calls=[];const ctx={drawImage:(...a)=>calls.push(a)};
  const out=renderer.draw(ctx,{width:1100,height:842},index,[x0,y0,x1,y1],{width:390,height:844});
  assert.equal(out.drawCalls,1);assert.equal(out.visibleTileCount,48);
  assert.equal(calls.length,1);assert.deepEqual(calls[0].slice(1,5),[0,0,1100,842]);
});
check('portrait camera panning and one draw per frame',()=>{
  const [x0,y0,x1,y1]=index.artBoxWorldPx;
  const camera=[x0+.06*(x1-x0),y0+.1*(y1-y0),x0+.56*(x1-x0),y0+.6*(y1-y0)];
  const calls=[];const result=renderer.draw({drawImage:(...args)=>calls.push(args)},
    {width:1100,height:842},index,camera,{width:390,height:844});
  assert.equal(result.drawCalls,1);assert.equal(calls.length,1);
  assert(result.visibleTileCount>0&&result.visibleTileCount<48);
});
check('landscape camera source crop remains aligned',()=>{
  const [x0,y0,x1,y1]=index.artBoxWorldPx;
  const camera=[x0+.4*(x1-x0),y0+.4*(y1-y0),x0+.8*(x1-x0),y0+.8*(y1-y0)];
  const result=renderer.draw({drawImage:()=>{}},{width:1100,height:842},index,camera,{width:844,height:390});
  assert.equal(result.drawCalls,1);
  const p=result.sourceCrop,w=result.worldCrop;
  assert(Math.abs(renderer.artToWorld(index,[p[0],p[1]])[0]-w[0])<1e-10);
});
check('no image draw when camera is off art',()=>{
  const result=renderer.draw({drawImage:()=>assert.fail('must not draw')},{width:1100,height:842},
    index,[0,0,1,1],{width:390,height:844});assert.equal(result.drawCalls,0);
});
check('world/screen transform roundtrip',()=>{
  const camera=index.artBoxWorldPx, viewport={width:390,height:844};
  for(const p of [[camera[0],camera[1]],[(camera[0]+camera[2])/2,(camera[1]+camera[3])/2],[camera[2],camera[3]]]){
    const q=renderer.screenToWorld(renderer.worldToScreen(p,camera,viewport),camera,viewport);
    assert(Math.hypot(q[0]-p[0],q[1]-p[1])<1e-10);
  }
});
check('rejects false playable route classification',()=>{
  const copy=structuredClone(index);copy.tiles[0].traversable=true;
  assert.throws(()=>renderer.validate(copy),/prematurely playable/);
});
check('rejects tile seams or crop overlaps',()=>{
  const copy=structuredClone(index);copy.tiles[1].imageCropPx[0]+=1;
  assert.throws(()=>renderer.validate(copy),/mismatch|edge/);
});
check('rejects duplicate tiles',()=>{
  const copy=structuredClone(index);copy.tiles[1].col=0;
  assert.throws(()=>renderer.validate(copy),/Duplicate/);
});
check('keeps unverified route candidate non-playable',()=>{
  const candidates=index.tiles.filter(t=>t.prototypeRouteCandidates.length);
  assert(candidates.length>0);
  assert(candidates.every(t=>!t.traversable&&!t.deepZoomEligible&&!t.conquerable));
});
console.log('PASS '+checks+' V116 renderer checks');
