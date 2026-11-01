"use strict";
const assert=require("node:assert/strict");
const {create}=require("../terrain-grid/v267-viewport-cache.js");
const tick=()=>new Promise(resolve=>setTimeout(resolve,10));
(async()=>{
 const cells=Array.from({length:16},(_,i)=>({
  id:"cell-"+i,origin:[(i%8)*1536,Math.floor(i/8)*1024],art:"original-"+i+".webp"
 }));
 const loaded=[],images=new Set();
 const stream=create({
  cells,maxDecoded:3,maxConcurrent:2,padding:0,
  load:async (path,cell)=>{loaded.push(cell.id);await tick();images.add(cell.id);return {src:path};}
 });
 stream.update({minX:0,minY:0,maxX:1530,maxY:1000});
 await new Promise(resolve=>setTimeout(resolve,45));
 assert.equal(stream.stats().decoded,1,"one visible image decoded");
 assert.deepEqual(loaded,["cell-0"],"offscreen art must not be fetched");
 stream.update({minX:1536,minY:0,maxX:4607,maxY:1000});
 await new Promise(resolve=>setTimeout(resolve,45));
 assert.equal(stream.stats().decoded,2);
 assert.equal(stream.get("cell-0"),null,"offscreen decoded image must be evicted");
 assert.ok(stream.get("cell-1")&&stream.get("cell-2"));
 stream.update({minX:0,minY:0,maxX:12288,maxY:2048});
 await new Promise(resolve=>setTimeout(resolve,70));
 assert.ok(stream.stats().decoded<=3,"whole-map view must respect iPhone image cap");
 assert.ok(stream.stats().inFlight<=2,"concurrency must be bounded");
 assert.ok(stream.stats().wanted<=3,"only nearest tiles selected when all visible");
 const old=stream.stats().requests;
 stream.update({minX:0,minY:0,maxX:12288,maxY:2048});
 await tick();
 assert.equal(stream.stats().requests,old,"no repeat fetches for cached visible images");
 stream.dispose();
 assert.equal(stream.stats().decoded,0);
 const fail=create({cells:[{id:"bad",origin:[0,0],art:"missing.webp"}],
  load:async()=>{throw Error("404");}});
 fail.update({minX:0,minY:0,maxX:1000,maxY:1000});
 await tick();
 assert.equal(fail.stats().failed,1,"failed assets reported without phantom image");
 assert.equal(fail.stats().decoded,0);
 console.log("PASS: viewport-only decode, LRU, concurrency cap, no repeated fetches, errors and dispose");
})().catch(e=>{console.error(e);process.exitCode=1;});
