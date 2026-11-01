import { chromium, webkit } from 'playwright';
import fs from 'node:fs/promises';
const base=process.env.COE_PREVIEW_URL||'http://127.0.0.1:8765/v267-countryside-02-review.html';
const engine=process.env.COE_BROWSER==='chromium'?chromium:webkit;
const browser=await engine.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base,{waitUntil:'networkidle',timeout:60000});
 await page.waitForFunction(()=>typeof tiles!=='undefined'&&tiles.length===4&&tiles.every(t=>t.img.complete&&t.img.naturalWidth>0),{timeout:30000});
 const before=await page.evaluate(()=>scale);
 await page.getByRole('button',{name:'+'}).click();
 const after=await page.evaluate(()=>scale);
 if(!(after>before))throw new Error('Zoom did not change camera scale');
 const meta=await page.evaluate(()=>{
   const newCell=tiles.find(t=>t.id==='COUNTRYSIDE-02');
   const approved=tiles.filter(t=>t.approved).map(t=>t.id);
   const ctx=document.getElementById('map').getContext('2d');
   const px=ctx.getImageData(Math.floor(innerWidth/2),Math.floor(innerHeight/2),1,1).data;
   return {approved,newCell:{width:newCell.img.naturalWidth,height:newCell.img.naturalHeight,loaded:newCell.img.complete},centerPixel:[...px]};
 });
 if(meta.newCell.width!==1536||meta.newCell.height!==1024)throw new Error('New original raster not full resolution');
 if(meta.approved.join(',')!=='WEST,MATREI,SOUTH')throw new Error('Approved source list altered');
 if(errors.length)throw new Error(errors.join('; '));
 await page.getByRole('button',{name:'New art'}).click();
 await page.screenshot({path:'terrain-grid/v267-countryside-original/actual-webkit-iphone-countryside-02.png',fullPage:true});
 await fs.writeFile('terrain-grid/v267-countryside-original/webkit-iphone-countryside-02-result.json',JSON.stringify({browser:process.env.COE_BROWSER||'webkit',viewport:[390,844],zoomPassed:after>before,assetsLoaded:4,...meta},null,2));
 console.log('PASS',JSON.stringify(meta));
}finally{await browser.close();}
