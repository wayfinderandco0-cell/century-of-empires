import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,writeFileSync} from 'node:fs';
import crypto, {createHmac} from 'node:crypto';
const root=new URL('../',import.meta.url),source=readFileSync(new URL('../src/worker.mjs',import.meta.url),'utf8');
const adjusted=source.replace("import PostalMime from 'postal-mime';",'').replace("import { EmailMessage } from 'cloudflare:email';",'')
.replace("from './helpers.mjs'","from './helpers.mjs'");
globalThis.PostalMime=class {async parse(buf){return {text:new TextDecoder().decode(buf),subject:'test'}}};
globalThis.EmailMessage=class {constructor(from,to,raw){this.from=from;this.to=to;this.raw=raw;}};
const url=new URL('../src/worker-local-test.mjs',import.meta.url);writeFileSync(url,adjusted);
const worker=(await import(url.href)).default;
class DB{
 constructor(){this.db=new DatabaseSync(':memory:');this.db.exec(readFileSync(new URL('../schema.sql',import.meta.url),'utf8'));}
 prepare(sql){const s=this.db.prepare(sql);let args=[];return {bind(...x){args=x;return this;},async run(){const r=s.run(...args);return {meta:{changes:r.changes}};},async first(){return s.get(...args)||null;},async all(){return {results:s.all(...args)}}};}
}
const env={DB:new DB(),RATE_SALT:'fake_test_salt',OWNER_API_TOKEN:'test_owner_token_32_characters_ok',ALLOWED_ORIGINS:'https://dance-manager-next-preview.onrender.com',RESEND_API_KEY:'test_mock_key',LEAD_TO_EMAIL:'studio@example.test',LEAD_FROM_EMAIL:'noreply@example.test',INBOUND_EMAIL_ADDRESS:'inbox@example.test',INBOUND_EMAIL_ENABLED:'true',AI:{async run(_model,req){return {response:'I am the automated guide for the fictional demo.'}}},TWILIO_ACCOUNT_SID:'ACtest123',TWILIO_AUTH_TOKEN:'token-test-456',TWILIO_FROM_NUMBER:'+18505550200'};
const previousFetch=globalThis.fetch;const outgoing=[];globalThis.fetch=async (url,init)=>{outgoing.push({url,init});if(String(url).includes('resend'))return Response.json({id:'mock_mail_id'}, {status:200});if(String(url).includes('twilio'))return Response.json({sid:'SMmock'},{status:201});throw Error('Unexpected external call: '+url)};
const waits=[],ctx={waitUntil(p){waits.push(p)}};const base='https://fake-worker.workers.dev',origin='https://dance-manager-next-preview.onrender.com';
const req=(path,obj,method='POST',includeOrigin=true)=>new Request(base+path,{method,headers:{...(includeOrigin?{'Origin':origin}:{}),...(method==='POST'?{'Content-Type':'application/json'}:{})},body:method==='POST'?JSON.stringify(obj):undefined});
const lead={name:'Demo Owner',email:'owner@example.test',studio:'Sample Dance',visitorType:'Studio owner',message:'Interested in a trial',consent:true,adultConfirmed:true,contactMethod:'email'};
test('health without secrets',async()=>{const r=await worker.fetch(new Request(base+'/health'),env,ctx);const j=await r.json();assert.equal(j.aiConfigured,true);assert.equal(j.leadsConfigured,true);assert.equal(j.status,'ok');});
test('only approved web origins can use chat and lead',async()=>{let r=await worker.fetch(new Request(base+'/api/chat',{method:'POST',headers:{Origin:'https://malicious.example', 'Content-Type':'application/json'},body:'{"message":"hi"}'}),env,ctx);assert.equal(r.status,403);r=await worker.fetch(new Request(base+'/api/chat',{method:'OPTIONS',headers:{Origin:origin}}),env,ctx);assert.equal(r.status,204)});
test('chat uses Workers AI and returns a response',async()=>{const r=await worker.fetch(req('/api/chat',{message:'What is Dance Manager?'}),env,ctx);assert.equal(r.status,200);assert.match((await r.json()).reply,/automated guide/)});
test('new ticket saved, owner notified, user acknowledgment sent',async()=>{const r=await worker.fetch(req('/api/lead',lead),env,ctx);assert.equal(r.status,202);const j=await r.json();assert.ok(j.ticketId);assert.equal(j.acknowledgmentAccepted,false);await Promise.all(waits.splice(0));assert.equal(outgoing.filter(x=>String(x.url).includes('resend')).length,2);const dbticket=await env.DB.prepare('select * from tickets where id=?').bind(j.ticketId).first();assert.equal(dbticket.ack_state,'accepted');assert.equal(dbticket.owner_alert_state,'accepted');});
test('SMS preference blocked without SMS permission',async()=>{const r=await worker.fetch(req('/api/lead',{...lead,phone:'+18505550100',contactMethod:'sms'}),env,ctx);assert.equal(r.status,400);});
test('owner endpoints require server-only token',async()=>{let r=await worker.fetch(new Request(base+'/api/owner/tickets'),env,ctx);assert.equal(r.status,401);r=await worker.fetch(new Request(base+'/api/owner/tickets',{headers:{Authorization:'Bearer '+env.OWNER_API_TOKEN}}),env,ctx);assert.equal(r.status,200);const j=await r.json();assert.equal(j.tickets.length,1)});
test('Twilio signature validation, no duplicate acknowledgment, STOP tracking',async()=>{
 async function twilio(id,message){const body=new URLSearchParams({MessageSid:id,From:'+18505551100',To:env.TWILIO_FROM_NUMBER,Body:message});const params=[...body.entries()].sort(([a],[b])=>a.localeCompare(b));let signed=base+'/webhooks/twilio/sms';for(const [k,v] of params)signed+=k+v;
 const signature=createHmac('sha1',env.TWILIO_AUTH_TOKEN).update(signed).digest('base64');return new Request(base+'/webhooks/twilio/sms',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','X-Twilio-Signature':signature},body:body.toString()});}
 let r=await worker.fetch(await twilio('SM1','Is there an instructor?'),env,ctx);assert.equal(r.status,200);let x=await r.text();assert.match(x,/Thanks for contacting/);await Promise.all(waits.splice(0));
 r=await worker.fetch(await twilio('SM1','Is there an instructor?'),env,ctx);x=await r.text();assert.doesNotMatch(x,/Thanks for contacting/);
 r=await worker.fetch(await twilio('SM2','Another question'),env,ctx);x=await r.text();assert.doesNotMatch(x,/Thanks for contacting/);await Promise.all(waits.splice(0));
 r=await worker.fetch(await twilio('SM3','STOP'),env,ctx);assert.equal(r.status,200);const opt=await env.DB.prepare('SELECT * FROM sms_optouts WHERE phone=?').bind('+18505551100').first();assert.ok(opt);
 const invalid=new Request(base+'/webhooks/twilio/sms',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','X-Twilio-Signature':'invalid'},body:'Body=spam'});r=await worker.fetch(invalid,env,ctx);assert.equal(r.status,403);
});
test('incoming email records inquiry and sends one threaded acknowledgment',async()=>{
 const headers=new Headers({'subject':'Schedule question','message-id':'<email1@example.test>','date':'Mon, 19 Oct 2026 13:00:00 GMT'});
 async function incoming(mid){headers.set('message-id',mid);let replies=[];const message={to:'inbox@example.test',from:'visitor@example.test',headers:new Headers(headers),raw:new ReadableStream({start(controller){controller.enqueue(new TextEncoder().encode('How do classes work?'));controller.close()}}),rawSize:18,async reply(out){replies.push(out)}};await worker.email(message,env,ctx);await Promise.all(waits.splice(0));return replies;}
 const first=await incoming('<email1@example.test>');assert.equal(first.length,1);assert.match(first[0].raw,/automated assistant/);
 const second=await incoming('<email2@example.test>');assert.equal(second.length,0);
});

test('owner console is present but data APIs stay protected',async()=>{const r=await worker.fetch(new Request(base+'/owner'),env,ctx);assert.equal(r.status,200);assert.match(await r.text(),/Customer inquiries/);assert.match(r.headers.get('Content-Security-Policy'),/frame-ancestors/);});

test('health must not advertise AI readiness without database and rate limiter',async()=>{const r=await worker.fetch(new Request(base+'/health'),{...env,RATE_SALT:undefined},ctx);assert.equal((await r.json()).aiConfigured,false)});
