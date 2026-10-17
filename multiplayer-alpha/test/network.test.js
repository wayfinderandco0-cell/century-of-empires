'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const os=require('node:os'),fs=require('node:fs'),path=require('node:path');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const base=path.join(__dirname,'..');
const port=18949;
const save=path.join(os.tmpdir(),`coe-alpha-${process.pid}.json`);
const url=`http://127.0.0.1:${port}`;
let server;
function start(){server=spawn(process.execPath,['server.js'],{cwd:base,env:{...process.env,PORT:String(port),DAY_SEC:'2',REALTIME_SCALE:'.035',SAVE_FILE:save},stdio:'ignore'});}
async function request(endpoint,{method='GET',body,token}={}){const res=await fetch(url+endpoint,{method,headers:{'content-type':'application/json',...(token?{authorization:'Bearer '+token}:{})},...(body?{body:JSON.stringify(body)}:{})});return{status:res.status,body:await res.json()}}
async function waitOnline(){for(let i=0;i<50;i++){try{if((await request('/health')).status===200)return}catch(e){}await sleep(100)}throw Error('Server did not start')}
async function shutdown(){if(!server)return;server.kill('SIGTERM');await new Promise(r=>server.once('exit',r));server=null}
test('two players, protected orders, continuous campaign, saved state',async()=>{
 try{
  start();await waitOnline();
  const fr=(await request('/api/join',{method:'POST',body:{nation:'FR',name:'French player'}})).body.token;
  const pr=(await request('/api/join',{method:'POST',body:{nation:'PR',name:'Prussian player'}})).body.token;
  assert.ok(fr&&pr&&fr!==pr);
  assert.equal((await request('/api/join',{method:'POST',body:{nation:'PR'}})).status,400);
  assert.equal((await request('/api/order',{method:'POST',body:{action:'march',army:'PR_1',destination:'prague'},token:fr})).status,400);
  assert.equal((await request('/api/order',{method:'POST',body:{action:'march',army:'PR_1',destination:'prague'},token:pr})).status,400);
  assert.equal((await request('/api/order',{method:'POST',body:{action:'march',army:'PR_1',destination:'prague',attack:true},token:pr})).status,200);
  assert.equal((await request('/api/order',{method:'POST',body:{action:'march',army:'FR_1',destination:'rouen'},token:fr})).status,200);
  assert.equal((await request('/api/order',{method:'POST',body:{action:'build',province:'paris'},token:fr})).status,200);
  await sleep(2500);
  const fa=(await request('/api/state',{token:fr})).body;
  const pa=(await request('/api/state',{token:pr})).body;
  assert.equal(fa.player.nation,'FR');assert.equal(pa.player.nation,'PR');
  assert.equal(fa.provinces.prague.controller,'PR');assert.equal(pa.provinces.prague.owner,'AT');
  assert.equal(fa.armies.FR_1.location,'rouen');assert.equal(fa.provinces.paris.industry,1);
  assert.ok(fa.elapsedDays>0);
  const rev=fa.revision;
  await shutdown();start();await waitOnline();
  const reloaded=(await request('/api/state',{token:fr})).body;
  assert.equal(reloaded.player.nation,'FR');assert.equal(reloaded.provinces.prague.controller,'PR');
  assert.equal(reloaded.provinces.paris.industry,1);assert.ok(reloaded.revision>=rev);
 }finally{await shutdown();try{fs.rmSync(save,{force:true})}catch(e){}}
},{timeout:15000});
