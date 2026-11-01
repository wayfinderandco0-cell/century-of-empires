import { webkit } from 'playwright';
import fs from 'node:fs/promises';
const base=process.env.COE_BASE||'http://127.0.0.1:8765/';
const dir='terrain-grid/v267-countryside-original/';
const browser=await webkit.launch({headless:true});
const result={browser:'webkit',viewport:[390,844],newArtIDs:['countryside-04','countryside-05'],newRasterCandidates:2,roadSeamsVerified:0,riverCrossingsVerified:0,userApproved:0,netFinished:0};
try{
 const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'v267-countryside-batch01-review.html',{waitUntil:'domcontentloaded',timeout:60000});
 await page.waitForFunction(()=>typeof tiles!=='undefined'&&tiles.length===6&&tiles.every(t=>t.img.complete&&t.img.naturalWidth===1536&&t.img.naturalHeight===1024),{timeout:60000});
 const z0=await page.evaluate(()=>scale);
 await page.locator('#plus').click();
 if(!(await page.evaluate(()=>scale)>z0))throw Error('Standalone zoom failed');
 await page.locator('#new').click();
 await page.screenshot({path:dir+'actual-webkit-iphone-countryside-04.png',fullPage:true});
 await page.locator('#new2').click();
 await page.screenshot({path:dir+'actual-webkit-iphone-countryside-05.png',fullPage:true});
 const native=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const nativeErrors=[];native.on('pageerror',e=>nativeErrors.push(e.message));
 await native.goto(base+'index.html?originalArtPilot=countrysideBatch01&autoOpen=1',{waitUntil:'domcontentloaded',timeout:60000});
 await native.waitForFunction(()=>window.COEAtlas?.loaded&&window.COEAtlas?.countrysideBatchLoaded&&window.COEAtlas?.countrysideBatchVisible,{timeout:60000});
 const before=await native.evaluate(()=>({
   zoom:COEAtlas.zoom,nodes:COEAtlas.nodes,seams:COEAtlas.seams.length,
   locked:COEAtlas.approvedBaselineLocked,images:COEAtlas.countrysideBatchIDs,
   originals:COEAtlas.imageSizes,shown:COEAtlas.shown
 }));
 if(before.nodes!==100||before.seams!==2||!before.locked||!before.shown||before.images.length!==3)
  throw Error('Protected V123 atlas or new art failed '+JSON.stringify(before));
 if(Object.values(before.originals).some(x=>x.join(',')!=='1536,1024'))
  throw Error('Approved artwork dimension drift');
 await native.locator('#atlasPlus').click();
 if(!(await native.evaluate(()=>COEAtlas.zoom)>before.zoom))throw Error('Native zoom failed');
 if(!(await native.evaluate(()=>COEAtlas.startMarch())))throw Error('Protected army march disabled');
 const moved=await native.evaluate(()=>COEAtlas.finishMarch());
 if(!Array.isArray(moved)||moved.length!==2)throw Error('Protected army route could not finish');
 await native.evaluate(()=>COEAtlas.centerAt(5376,1536,2.25));
 await native.screenshot({path:dir+'actual-webkit-iphone-countryside-04-native.png',fullPage:true});
 await native.evaluate(()=>COEAtlas.centerAt(5376,512,2.25));
 await native.screenshot({path:dir+'actual-webkit-iphone-countryside-05-native.png',fullPage:true});
 await native.locator('#atlasWhole').click();
 const wholeZoom=await native.evaluate(()=>COEAtlas.zoom);
 if(!(wholeZoom<.6&&wholeZoom>.15))throw Error('Whole 6-cell atlas did not fit iPhone: '+wholeZoom);
 await native.screenshot({path:dir+'actual-webkit-iphone-countryside-batch01-overview.png',fullPage:true});
 for(const file of ['actual-webkit-iphone-countryside-04-native.png','actual-webkit-iphone-countryside-05-native.png']){
  if((await fs.stat(dir+file)).size<25000)throw Error('Blank/small screenshot '+file);
 }
 if(errors.length||nativeErrors.length)throw Error('Browser errors: '+errors.concat(nativeErrors).join('; '));
 Object.assign(result,{standaloneLoaded:true,nativeCanvas:true,zoomPassed:true,armyRoutePreserved:true,originalsPreserved:true,webKitRenderedNewCandidates:2});
 await fs.writeFile(dir+'webkit-iphone-countryside-batch01-result.json',JSON.stringify(result,null,2)+'\n');
 console.log('PASS original countryside batch01 WebKit '+JSON.stringify(result));
}finally{await browser.close();}
