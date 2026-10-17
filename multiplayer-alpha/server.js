// Century of Empires: first truly networked vertical slice. Node 22, zero external dependencies.
// Internet exposure requires a real HTTPS host and production security hardening (see README).
'use strict';
const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {URL}=require('node:url');
const PORT=Number(process.env.PORT||8787);
const DAY_SEC=Number(process.env.DAY_SEC||45);
const REALTIME_SCALE=Math.max(.02,Math.min(10,Number(process.env.REALTIME_SCALE||1))); // 1 normally; accelerate deterministic integration tests
const DATA=path.resolve(process.env.SAVE_FILE||path.join(__dirname,'data','campaign.json'));
const WORLD=JSON.parse(fs.readFileSync(path.join(__dirname,'data','world.json'),'utf8'));
const BYID=new Map(WORLD.regions.map(p=>[p.id,p]));
const CAPITALS={GB:'london',FR:'paris',PR:'berlin',AT:'vienna',RU:'moscow',ES:'madrid',OT:'constantinople',SW:'stockholm',PL:'warsaw',NL:'amsterdam',PT:'lisbon',IT:'rome'};
const NAMES={GB:'Great Britain',FR:'France',PR:'Prussia',AT:'Austria',RU:'Russia',ES:'Spain',OT:'Ottomans',SW:'Sweden',PL:'Poland',NL:'Netherlands',PT:'Portugal',IT:'Italian States'};
const COLORS={GB:'#9b6060',FR:'#6d879c',PR:'#6f7890',AT:'#a59469',RU:'#739180',ES:'#b38b59',OT:'#668e87',SW:'#8d91a5',PL:'#a7808b',NL:'#9b846b',PT:'#879b6f',IT:'#a38d76'};
const ACCENTS={GB:'#d99c95',FR:'#a4c6d5',PR:'#aab5db',AT:'#ddc78a',RU:'#a6d5b5',ES:'#e4c18b',OT:'#a3d1c7',SW:'#b8c1e0',PL:'#e4bdcd',NL:'#dec6a7',PT:'#c8d7a7',IT:'#d9c4a8'};
const nations=Object.keys(CAPITALS);
const fresh=()=>({version:1,revision:0,serverTime:Date.now(),elapsedDays:0,provinces:Object.fromEntries(WORLD.regions.map(p=>[p.id,{owner:p.owner,controller:p.owner,industry:0,fort:0,unrest:2}])),players:{},armies:Object.fromEntries(nations.map(t=>[t+'_1',{id:t+'_1',nation:t,location:CAPITALS[t],troops:t==='GB'?24:t==='RU'?42:32,morale:100,route:[],arriveAt:0,departAt:0,origin:null,status:'stationed'}])),treasury:Object.fromEntries(nations.map(t=>[t,140])),queues:[],wars:[],log:[{message:'1780 · European campaign opened.',at:Date.now()}]});
let game;
try{game=JSON.parse(fs.readFileSync(DATA,'utf8'));if(game.version!==1)throw Error('save format mismatch');}
catch(e){game=fresh();}
// Resume from server clock, not browser wall clock. Catch-up takes place on server ticks.
let lastTick=Date.now(),saveDirty=true,lastSaved=0;
const listeners=new Set();
function dirty(){game.revision++;saveDirty=true}
function event(message){game.log.unshift({at:Date.now(),message});game.log=game.log.slice(0,40);dirty()}
function save(){if(!saveDirty)return;fs.mkdirSync(path.dirname(DATA),{recursive:true});const temp=DATA+'.tmp';fs.writeFileSync(temp,JSON.stringify(game));fs.renameSync(temp,DATA);saveDirty=false;lastSaved=Date.now()}
function shortestRoute(origin,destination){
 if(!BYID.has(origin)||!BYID.has(destination))return null;
 if(origin===destination)return [];
 const parents=new Map([[origin,null]]),queue=[origin];
 for(let i=0;i<queue.length;i++){
  const p=BYID.get(queue[i]);for(const n of p.neighbors){if(!BYID.has(n)||parents.has(n))continue;parents.set(n,p.id);queue.push(n);if(n===destination){const result=[];let cur=n;while(cur!==origin){result.unshift(cur);cur=parents.get(cur)}return result;}}}
 return null;
}
function legTime(from,to){const area=BYID.get(to);const dx=area.x-BYID.get(from).x,dy=area.y-BYID.get(from).y;
 return Math.max(.15,Math.round(Math.max(7,Math.min(30,Math.hypot(dx,dy)*.10+4))*(area.terrain==='hills'?1.22:area.terrain==='forest'?1.17:1)*REALTIME_SCALE*100)/100);}
function travelTime(from,route){let t=0,p=from;for(const dest of route){t+=legTime(p,dest);p=dest;}return t;}
function dateLabel(){const date=new Date(Date.UTC(1780,0,1)+Math.floor(game.elapsedDays)*86400000);return date.toISOString().slice(0,10)}
function nationWars(a,b){return game.wars.some(w=>w.includes(a)&&w.includes(b))}
function occupation(army,province){const owner=game.provinces[province].controller;
 if(owner!==army.nation){const enemy=Object.values(game.armies).find(a=>a.nation!==army.nation&&a.location===province&&a.status==='stationed'&&a.troops>0);
  if(enemy){const atk=Math.max(1,Math.floor(army.troops*(army.morale/100))),def=Math.max(1,Math.floor(enemy.troops*(enemy.morale/100)*1.08));
   if(atk<=def){const loss=Math.max(1,Math.ceil(atk*.43));army.troops=Math.max(0,army.troops-loss);army.morale=Math.max(30,army.morale-25);enemy.troops=Math.max(1,enemy.troops-Math.ceil(atk*.26));army.status='routed';army.route=[];event(`${NAMES[army.nation]} repelled at ${BYID.get(province).name}.`);return false;}
   enemy.troops=Math.max(0,enemy.troops-Math.ceil(atk*.67));army.troops=Math.max(1,army.troops-Math.ceil(def*.36));army.morale=Math.max(38,army.morale-15);enemy.status=enemy.troops?'routed':'defeated';event(`${NAMES[army.nation]} defeated defenders near ${BYID.get(province).name}.`);
  }
  if(!nationWars(army.nation,owner)){game.wars.push([army.nation,owner]);event(`War declared: ${NAMES[army.nation]} and ${NAMES[owner]}.`)}
  game.provinces[province].controller=army.nation;event(`${NAMES[army.nation]} occupies ${BYID.get(province).name}. Legal ownership unchanged until peace.`);
 }
 return true;
}
function startLeg(army,now){if(!army.route.length){army.status='stationed';army.arriveAt=0;return}
 army.origin=army.location;army.departAt=now;army.arriveAt=now+legTime(army.location,army.route[0])*1000;army.status='marching';dirty()}
function step(now){
 // Integrate elapsed wall time on server; clamp at 5 minutes per tick after process suspension.
 const delta=Math.max(0,Math.min(300000,now-lastTick));lastTick=now;
 game.elapsedDays+=delta/(DAY_SEC*1000);game.serverTime=now;
 const oldDay=Math.floor(game.elapsedDays-delta/(DAY_SEC*1000)),newDay=Math.floor(game.elapsedDays);
 if(newDay>oldDay){const n=Math.min(30,newDay-oldDay);for(let i=0;i<n;i++)for(const t of nations){const lands=Object.entries(game.provinces).filter(([,v])=>v.controller===t).length;game.treasury[t]=(game.treasury[t]||0)+Math.max(1,Math.floor(lands/4));}dirty()}
 for(const army of Object.values(game.armies)){
  if(army.status!=='marching'||!army.arriveAt)continue;
  let guard=0;
  while(army.status==='marching'&&army.route.length&&now>=army.arriveAt&&guard++<32){
   const arrivalAt=army.arriveAt;const to=army.route.shift();army.location=to;dirty();
   if(!occupation(army,to))break;
   if(army.route.length)startLeg(army,arrivalAt);
   else{army.status='stationed';army.arriveAt=0;army.departAt=0;army.origin=null;event(`${NAMES[army.nation]} army arrived at ${BYID.get(to).name}.`)}
  }
 }
 for(let i=game.queues.length-1;i>=0;i--){let job=game.queues[i];if(job.finishAt>now)continue;
  if(job.type==='industry'){game.provinces[job.province].industry++;event(`${NAMES[job.nation]} completed workshop at ${BYID.get(job.province).name}.`)}
  if(job.type==='recruit'){const id=job.nation+'_'+crypto.randomBytes(3).toString('hex');game.armies[id]={id,nation:job.nation,location:job.province,troops:12,morale:100,route:[],arriveAt:0,departAt:0,origin:null,status:'stationed'};event(`${NAMES[job.nation]} recruited 12 infantry at ${BYID.get(job.province).name}.`)}
  game.queues.splice(i,1);dirty();
 }
 if(saveDirty&&now-lastSaved>4000)save();
}
function stateView(token){const seat=game.players[token];return {revision:game.revision,serverTime:Date.now(),date:dateLabel(),elapsedDays:game.elapsedDays,daySec:DAY_SEC,player:seat?{nation:seat.nation,name:seat.name}:null,players:Object.values(game.players).map(x=>({nation:x.nation,name:x.name})),provinces:game.provinces,armies:game.armies,treasury:game.treasury,queues:game.queues,wars:game.wars,log:game.log.slice(0,12),nations:NAMES,colors:COLORS,accents:ACCENTS,worldNote:WORLD.note};}
function respond(res,status,obj){const body=JSON.stringify(obj);res.writeHead(status,{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff'});res.end(body)}
function readBody(req){return new Promise((resolve,reject)=>{let data='';req.on('data',c=>{data+=c;if(data.length>16000){reject(Error('body too large'));req.destroy()}});req.on('end',()=>{try{resolve(JSON.parse(data||'{}'))}catch(e){reject(Error('invalid JSON'))}});req.on('error',reject)})}
function order(user,msg){if(!user)throw Error('Choose a nation before issuing orders.');const nation=user.nation;
 if(msg.action==='march'||msg.action==='recall'){
  const army=game.armies[msg.army],to=msg.destination;
  if(!army||army.nation!==nation)throw Error('That army is not yours.');
  if(msg.action==='recall'){if(army.status!=='marching')throw Error('Army is not marching.');army.route=[];army.arriveAt=0;army.status='stationed';army.location=army.origin||army.location;event(`${NAMES[nation]} canceled an army march.`);return}
  if(army.status!=='stationed')throw Error('Wait until the army arrives before changing orders.');
  const route=shortestRoute(army.location,to);if(!route||!route.length)throw Error('Destination cannot be reached on the land route graph.');
  if(route.length>24)throw Error('Route exceeds 24 provinces.');
  const hostileLegs=route.filter(id=>game.provinces[id]?.controller!==nation);
  if(hostileLegs.length&&!msg.attack)throw Error('This route crosses hostile territory; confirm an attack order.');
  army.route=route;startLeg(army,Date.now());event(`${NAMES[nation]} issued a march to ${BYID.get(to).name} (${travelTime(army.location,route)} s estimated).`);return;
 }
 if(msg.action==='build'||msg.action==='recruit'){
  const p=game.provinces[msg.province];if(!p||p.controller!==nation)throw Error('Only controlled provinces can produce for your nation.');
  const cost=msg.action==='build'?35:22;if(game.treasury[nation]<cost)throw Error(`Need ${cost} treasury.`);
  if(game.queues.some(q=>q.province===msg.province))throw Error('A production order is already running here.');
  game.treasury[nation]-=cost;game.queues.push({nation,province:msg.province,type:msg.action==='build'?'industry':'recruit',finishAt:Date.now()+(msg.action==='build'?32000:22000)*REALTIME_SCALE});event(`${NAMES[nation]} started ${msg.action==='build'?'a workshop':'recruitment'} at ${BYID.get(msg.province).name}.`);return;
 }
 throw Error('Unknown order.');
}
const server=http.createServer(async(req,res)=>{
 let url;try{url=new URL(req.url,'http://local.invalid')}catch(e){respond(res,400,{error:'Bad URL'});return}
 const p=url.pathname,token=req.headers.authorization?.replace(/^Bearer\s+/i,'')||url.searchParams.get('token')||'';
 if(req.method==='GET'&&p==='/health'){respond(res,200,{ok:true,revision:game.revision,players:Object.keys(game.players).length});return}
 if(req.method==='GET'&&p==='/api/world'){respond(res,200,WORLD);return}
 if(req.method==='GET'&&p==='/api/state'){respond(res,200,stateView(token));return}
 if(req.method==='GET'&&p==='/api/events'){
  res.writeHead(200,{'content-type':'text/event-stream','cache-control':'no-cache, no-transform','connection':'keep-alive','x-accel-buffering':'no'});
  res.write('retry: 2200\n\n');const client={res,token};listeners.add(client);
  req.on('close',()=>listeners.delete(client));res.write('event: state\ndata: '+JSON.stringify(stateView(token))+'\n\n');return;
 }
 if(req.method==='POST'&&p==='/api/join'){
  try{const msg=await readBody(req);const selected=String(msg.nation||'');const name=String(msg.name||'Commander').trim().slice(0,24);
   if(!nations.includes(selected))throw Error('Unknown nation.');
   if(Object.values(game.players).some(x=>x.nation===selected))throw Error('Nation already claimed; choose another.');
   const id=crypto.randomBytes(20).toString('hex');game.players[id]={nation:selected,name:name||'Commander',joinedAt:Date.now()};event(`${name} took command of ${NAMES[selected]}.`);respond(res,200,{token:id,nation:selected});save();}
  catch(e){respond(res,400,{error:e.message})}return;
 }
 if(req.method==='POST'&&p==='/api/order'){
  try{const body=await readBody(req);order(game.players[token],body);respond(res,200,{ok:true,revision:game.revision});save()}
  catch(e){respond(res,400,{error:e.message})}return;
 }
 if(req.method==='GET'&&['/','/index.html'].includes(p)){
  const file=fs.readFileSync(path.join(__dirname,'public','index.html'));res.writeHead(200,{'content-type':'text/html; charset=utf-8','cache-control':'no-store'});res.end(file);return;
 }
 respond(res,404,{error:'Not found'});
});
setInterval(()=>{step(Date.now());const snapshot=JSON.stringify(stateView(''));
 for(const c of listeners){try{const payload=c.token?JSON.stringify(stateView(c.token)):snapshot;c.res.write('event: state\ndata: '+payload+'\n\n')}catch(e){listeners.delete(c)}}
},1000).unref();
process.on('SIGTERM',()=>{save();server.close(()=>process.exit(0))});
process.on('SIGINT',()=>{save();server.close(()=>process.exit(0))});
server.listen(PORT,'0.0.0.0',()=>console.log(`Century multiplayer alpha listening on ${PORT}; ${WORLD.regions.length} regions, ${DAY_SEC}s/day`));
