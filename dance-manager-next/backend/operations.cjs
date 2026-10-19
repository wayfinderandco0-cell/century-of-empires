/**
 * Dance Manager Next — communication bridge for leads, emails, texts and handoffs.
 * Requires owner-controlled service credentials. No secrets are exposed to the frontend.
 * Standalone service for an independent staging site, not the existing dance company.
 */
'use strict';
const crypto=require('node:crypto');
const allowedOrigins=(process.env.ALLOWED_ORIGINS||'https://wayfinderandco0-cell.github.io,https://dance-manager-next-v2.onrender.com,https://dance-manager-next-preview.onrender.com').split(',').map(s=>s.trim()).filter(Boolean);
const rates=new Map();
const replay=new Map();
const expiry=60*60*24*30;
function hasEmail(){return Boolean(process.env.RESEND_API_KEY&&process.env.LEAD_FROM_EMAIL&&process.env.LEAD_TO_EMAIL);}
function hasSms(){return Boolean(process.env.TWILIO_ACCOUNT_SID&&process.env.TWILIO_AUTH_TOKEN&&process.env.TWILIO_FROM_NUMBER&&process.env.OWNER_MOBILE);}
function hasStore(){return Boolean(process.env.UPSTASH_REDIS_REST_URL&&process.env.UPSTASH_REDIS_REST_TOKEN);}
function hasInboundEmail(){return hasEmail()&&Boolean(process.env.RESEND_WEBHOOK_SECRET&&process.env.RESEND_INBOUND_ADDRESS);}
function hasInboundSms(){return Boolean(process.env.TWILIO_AUTH_TOKEN&&process.env.TWILIO_FROM_NUMBER&&process.env.PUBLIC_API_BASE);}
function status(){return {leadsConfigured:hasEmail(),ownerAlertsConfigured:hasEmail(),smsConfigured:hasSms(),inboxConfigured:hasStore(),inboundEmailConfigured:hasInboundEmail(),inboundSmsConfigured:hasInboundSms()};}
function matches(p){return ['/api/lead','/api/handoff','/api/owner/inquiries','/api/owner/resolve','/webhooks/twilio/sms','/webhooks/resend/inbound'].includes(p);}
function plain(x,max=200){return typeof x==='string'?x.trim().slice(0,max):'';}
function emailOK(s){return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(s)&&s.length<=120;}
function phoneOK(s){return /^\+[1-9]\d{7,14}$/.test(s);}
function escapeXml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));}
function clientHash(req){return crypto.createHash('sha256').update(String(req.socket.remoteAddress||'unknown')).digest('hex').slice(0,16);}
function throttle(key,limit,period){const now=Date.now(),a=rates.get(key);if(!a||now-a.since>period){if(rates.size>3000)rates.clear();rates.set(key,{since:now,count:1});return false;}a.count++;return a.count>limit;}
function json(res,code,payload,origin){const headers={'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Vary':'Origin'};if(allowedOrigins.includes(origin))headers['Access-Control-Allow-Origin']=origin;res.writeHead(code,headers);res.end(JSON.stringify(payload));}
function twiml(res,message){res.writeHead(200,{'Content-Type':'application/xml; charset=utf-8','Cache-Control':'no-store'});res.end('<?xml version="1.0" encoding="UTF-8"?><Response><Message>'+escapeXml(message.slice(0,550))+'</Message></Response>');}
async function readRaw(req,max=12000){let raw='',size=0;for await (const b of req){size+=b.length;if(size>max)throw Object.assign(new Error('Too large'),{status:413});raw+=b.toString('utf8');}return raw;}
async function redis(cmd,fetchFn){if(!hasStore())return null;const base=process.env.UPSTASH_REDIS_REST_URL.replace(/\/$/,'');if(!/^https:\/\//.test(base))throw Error('Invalid storage origin');const response=await fetchFn(base,{method:'POST',headers:{'Authorization':'Bearer '+process.env.UPSTASH_REDIS_REST_TOKEN,'Content-Type':'application/json'},body:JSON.stringify(cmd),signal:AbortSignal.timeout(9000)});if(!response.ok)throw Error('Storage unavailable');const val=await response.json();if(val.error)throw Error('Storage unavailable');return val.result;}
async function persistTicket(ticket,fetchFn){
 if(!hasStore())return false;
 const data=JSON.stringify(ticket);
 await redis(['SET','dmnext:ticket:'+ticket.id,data,'EX',expiry],fetchFn);
 await redis(['ZADD','dmnext:tickets',Date.parse(ticket.receivedAt),ticket.id],fetchFn);
 return true;
}

function conversationKey(ticket){
 if(!hasStore()||!process.env.CONVERSATION_HMAC_SECRET)return '';
 const contact=(ticket.email?'email:'+ticket.email.toLowerCase():ticket.phone?'sms:'+ticket.phone:'');
 if(!contact)return '';
 return 'dmnext:conversation:'+crypto.createHmac('sha256',process.env.CONVERSATION_HMAC_SECRET).update(contact).digest('hex');
}
async function loadConversation(ticket,fetchFn){
 const key=conversationKey(ticket);
 if(!key)return {history:[],humanMode:false};
 const saved=await redis(['GET',key],fetchFn);
 if(!saved)return {history:[],humanMode:false};
 try{
  const parsed=JSON.parse(saved);
  return {history:Array.isArray(parsed.history)?parsed.history.slice(-8).filter(x=>['user','assistant'].includes(x.role)).map(x=>({role:x.role,text:plain(x.text,500)})):[],humanMode:parsed.humanMode===true};
 }catch(e){return {history:[],humanMode:false};}
}
async function saveConversation(ticket,conversation,fetchFn){
 const key=conversationKey(ticket);if(!key)return false;
 await redis(['SET',key,JSON.stringify({history:(conversation.history||[]).slice(-10),humanMode:conversation.humanMode===true,updatedAt:new Date().toISOString()}),'EX',expiry],fetchFn);
 return true;
}

async function sendEmail(to,subject,body,fetchFn,replyTo){
 if(!hasEmail())return false;
 const address=Array.isArray(to)?to:[to];if(!address.every(emailOK))return false;
 const payload={from:process.env.LEAD_FROM_EMAIL,to:address,subject:subject.slice(0,160),text:body.slice(0,7000)};
 if(replyTo&&emailOK(replyTo))payload.reply_to=replyTo;
 const res=await fetchFn('https://api.resend.com/emails',{method:'POST',headers:{'Authorization':'Bearer '+process.env.RESEND_API_KEY,'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(11000)});
 return res.ok;
}
async function sendSms(to,body,fetchFn){
 if(!hasSms()||!phoneOK(to))return false;
 const form=new URLSearchParams({To:to,From:process.env.TWILIO_FROM_NUMBER,Body:body.slice(0,480)});
 const res=await fetchFn('https://api.twilio.com/2010-04-01/Accounts/'+encodeURIComponent(process.env.TWILIO_ACCOUNT_SID)+'/Messages.json',{
  method:'POST',headers:{Authorization:'Basic '+Buffer.from(process.env.TWILIO_ACCOUNT_SID+':'+process.env.TWILIO_AUTH_TOKEN).toString('base64'),'Content-Type':'application/x-www-form-urlencoded'},
  body:form.toString(),signal:AbortSignal.timeout(10000)});
 return res.ok;
}
function newTicket(input,channel){
 return {id:'DM-'+crypto.randomBytes(5).toString('hex').toUpperCase(),channel,
  receivedAt:new Date().toISOString(),status:'Needs human follow-up',
  name:input.name||'New visitor',email:input.email||'',phone:input.phone||'',
  studio:input.studio||'',visitorType:input.visitorType||'',message:input.message||'',
  transcript:input.transcript||'',marketingOptIn:Boolean(input.marketingOptIn),smsReplyConsent:Boolean(input.smsReplyConsent),
  source:input.source||'Dance Manager Next independent prototype'};
}
function ownerContent(ticket){return [
 'DANCE MANAGER NEXT — NEW INQUIRY · HUMAN FOLLOW-UP NEEDED','',
 'Ticket: '+ticket.id,'Channel: '+ticket.channel,'Received (UTC): '+ticket.receivedAt,'',
 'Contact: '+ticket.name,'Email: '+(ticket.email||'Not supplied'),'Phone: '+(ticket.phone||'Not supplied'),
 'Organization: '+(ticket.studio||'Not supplied'),'Visitor type: '+(ticket.visitorType||'Not supplied'),'',
 'Inquiry: '+(ticket.message||'(none)'),'',
 'Conversation context: '+(ticket.transcript||'(not attached)'),'',
 'Marketing email opt-in: '+(ticket.marketingOptIn?'YES':'No'),
 'Permission to receive a one-time SMS follow-up: '+(ticket.smsReplyConsent?'YES':'No'), '',
 'Please assign a human to reply. Automated acknowledgments are not completed appointments.'
 ].join('\n');}
function thanks(name,id){return 'Hello '+plain(name,50)+',\n\nThank you for contacting Dance Manager Next. This automated message confirms that our team has received your inquiry (reference '+id+'). A person will follow up as soon as one is available. In the meantime, our website assistant can answer general questions about the demonstration and help you find relevant features.\n\nThis is not an appointment confirmation. Please do not send sensitive student information.\n\n— Dance Manager Next · Automated acknowledgment';}
async function notifyOwner(ticket,fetchFn){
 const mail=await sendEmail(process.env.LEAD_TO_EMAIL,'New studio inquiry '+ticket.id+' — response requested',ownerContent(ticket),fetchFn,ticket.email);
 if(!mail)return {email:false,sms:false};
 let sms=false;
 if(hasSms())try{sms=await sendSms(process.env.OWNER_MOBILE,'Dance Manager Next: '+ticket.channel+' inquiry '+ticket.id+' from '+plain(ticket.name,45)+'. Please check the studio inbox.',fetchFn);}catch(e){}
 return {email:true,sms};
}
async function submitLead(body,fetchFn,channel){
 const input={
  name:plain(body?.name,70),email:plain(body?.email,120),studio:plain(body?.studio,90),
  visitorType:plain(body?.visitorType,45),phone:plain(body?.phone,30),message:plain(body?.message,800),
  transcript:plain(body?.transcript,1800),source:'Independent website '+channel,
  marketingOptIn:body?.marketingOptIn===true,smsReplyConsent:body?.smsReplyConsent===true
 };
 if(plain(body?.website,150))return {code:202,ok:true,silent:true};
 if(body?.adultConfirmed!==true||body?.consent!==true||!input.name||!emailOK(input.email)||!input.studio||!input.visitorType||!input.message||
    (input.phone&&!/^\+?[0-9().\-\s]{7,30}$/.test(input.phone))||
    (input.smsReplyConsent&&!phoneOK(input.phone))) {
  return {code:400,error:'Please complete the required fields, confirm you are an adult, and allow follow-up.'};
 }
 if(!hasEmail())return {code:503,error:'Contact delivery is not configured.'};
 const ticket=newTicket(input,channel);
 // Persist before sending to the owner when durable storage is connected.
 let stored=false;
 if(hasStore())try{stored=await persistTicket(ticket,fetchFn);}catch(e){return {code:503,error:'Our secure inquiry queue is temporarily unavailable. Please try again.'};}
 const alert=await notifyOwner(ticket,fetchFn);
 if(!alert.email)return {code:502,error:'The team could not be notified. Please try again.'};
 let acknowledged=false,smsAcknowledged=false;
 try{acknowledged=await sendEmail(input.email,'We received your Dance Manager inquiry · '+ticket.id,thanks(input.name,ticket.id),fetchFn);}catch(e){}
 if(input.smsReplyConsent&&phoneOK(input.phone)&&hasSms()){
  try{smsAcknowledged=await sendSms(input.phone,'Dance Manager Next: we received your request '+ticket.id+'. A team member will follow up when available. Reply STOP to opt out.',fetchFn);}catch(e){}
 }
 return {code:202,ok:true,ticketId:ticket.id,ownerNotified:true,acknowledgmentAccepted:acknowledged,smsAcknowledgmentAccepted:smsAcknowledged,queued:stored};
}
function verifySvix(headers,raw){
 const secret=process.env.RESEND_WEBHOOK_SECRET||'',id=headers['svix-id']||headers['webhook-id'],stamp=headers['svix-timestamp']||headers['webhook-timestamp'],signature=headers['svix-signature']||headers['webhook-signature'];
 if(!secret.startsWith('whsec_')||!id||!/^\d{10}$/.test(String(stamp))||Math.abs(Date.now()/1000-Number(stamp))>300||!signature)return false;
 let key;try{key=Buffer.from(secret.slice(6),'base64');}catch(e){return false;}
 if(!key.length)return false;
 const expected=crypto.createHmac('sha256',key).update(id+'.'+stamp+'.'+raw).digest('base64');
 return String(signature).split(' ').some(part=>{const v=part.split(',');if(v.length!==2||v[0]!=='v1')return false;const a=Buffer.from(v[1]),b=Buffer.from(expected);return a.length===b.length&&crypto.timingSafeEqual(a,b);});
}
function verifyTwilio(headers,raw){
 const token=process.env.TWILIO_AUTH_TOKEN,base=process.env.PUBLIC_API_BASE;
 if(!token||!base||!headers['x-twilio-signature'])return false;
 const params=new URLSearchParams(raw);
 const url=base.replace(/\/$/,'')+'/webhooks/twilio/sms';
 const data=[...params].sort((a,b)=>a[0].localeCompare(b[0])).reduce((s,[k,v])=>s+k+v,url);
 const expected=crypto.createHmac('sha1',token).update(data,'utf8').digest('base64');
 const a=Buffer.from(headers['x-twilio-signature']),b=Buffer.from(expected);
 return a.length===b.length&&crypto.timingSafeEqual(a,b);
}
function repeated(id){const now=Date.now();if(replay.size>2000)replay.clear();if(replay.has(id)&&replay.get(id)>now)return true;replay.set(id,now+3600000);return false;}
async function inboundMessage(ticket,fetchFn,aiReply){
 // Recalls a short, private conversation only when managed storage and HMAC key are configured.
 const conversation=await loadConversation(ticket,fetchFn);
 if(conversation.history.length){
  ticket.transcript=conversation.history.map(h=>(h.role==='user'?'Visitor: ':'Assistant: ')+h.text).join('\n').slice(-1800);
 }
 let saved=false;
 if(hasStore())saved=await persistTicket(ticket,fetchFn);
 const owner=await notifyOwner(ticket,fetchFn);
 if(!owner.email)throw Error('Owner notification failed');
 let reply=conversation.humanMode
  ?'Thank you. Your inquiry is already assigned to a team member. They can continue the conversation directly.'
  :'Thank you for contacting Dance Manager Next. Your message has reached the team, and someone will follow up when available.';
 if(!conversation.humanMode&&typeof aiReply==='function'&&ticket.message.length>3){
  try{const a=await aiReply({message:'Answer this incoming '+ticket.channel+' software question briefly, do not invent details, then state a staff member has been notified: '+ticket.message,history:conversation.history},fetchFn);
   if(a.reply&&a.code===200)reply=a.reply.slice(0,420)+'\n\nA team member has also been notified.';
  }catch(e){}
 }
 conversation.history.push({role:'user',text:plain(ticket.message,500)},{role:'assistant',text:plain(reply,500)});
 await saveConversation(ticket,conversation,fetchFn);
 return {reply,saved};
}
async function inboundSms(req,res,fetchFn,aiReply){
 if(!hasInboundSms())return json(res,503,{error:'SMS webhook inactive'});
 if(!String(req.headers['content-type']||'').startsWith('application/x-www-form-urlencoded'))return json(res,415,{error:'Wrong format'});
 const raw=await readRaw(req,8500);
 if(!verifyTwilio(req.headers,raw))return json(res,403,{error:'Invalid webhook signature'});
 const fd=new URLSearchParams(raw),from=plain(fd.get('From'),30),to=plain(fd.get('To'),30);
 if(!phoneOK(from)||to!==process.env.TWILIO_FROM_NUMBER)return json(res,400,{error:'Invalid sender or recipient'});
 const incoming=plain(fd.get('Body'),1100);
 if(!incoming)return twiml(res,'Please include a question for the Dance Manager Next team.');
 if(/^(stop|stopall|unsubscribe|cancel|end|quit)$/i.test(incoming))return twiml(res,'You have requested to stop messages. You will not receive further automated replies.');
 if(/^(help|info)$/i.test(incoming))return twiml(res,'Dance Manager Next studio software information. Reply with your question, or STOP to opt out.');
 if(throttle('sms:'+crypto.createHash('sha256').update(from).digest('hex'),8,3600000))return twiml(res,'We have received several messages. A team member can follow up when available.');
 const eventId=plain(fd.get('MessageSid'),60);if(eventId&&repeated('sms:'+eventId))return twiml(res,'Thank you. This inquiry is already being processed.');
 const ticket=newTicket({name:'SMS visitor',phone:from,message:incoming},'Inbound SMS');
 try{const result=await inboundMessage(ticket,fetchFn,aiReply);return twiml(res,result.reply+' Reply STOP to opt out.');}
 catch(e){return twiml(res,'Our automated service is temporarily unavailable. Please contact the studio directly if your matter is urgent.');}
}
async function inboundEmail(req,res,fetchFn,aiReply){
 if(!hasInboundEmail())return json(res,503,{error:'Email webhook inactive'});
 const raw=await readRaw(req,16000);
 if(!verifySvix(req.headers,raw))return json(res,403,{error:'Invalid webhook signature'});
 let event;try{event=JSON.parse(raw);}catch(e){return json(res,400,{error:'Invalid payload'});}
 if(event.type!=='email.received')return json(res,200,{ok:true,ignored:true});
 const id=plain(event.data?.email_id,100);
 if(!/^[a-zA-Z0-9-]{12,100}$/.test(id))return json(res,400,{error:'Invalid message identifier'});
 if(repeated('email:'+id))return json(res,200,{ok:true,duplicate:true});
 const r=await fetchFn('https://api.resend.com/emails/receiving/'+encodeURIComponent(id),{headers:{'Authorization':'Bearer '+process.env.RESEND_API_KEY},signal:AbortSignal.timeout(10000)});
 if(!r.ok)throw Error('Unable to fetch inbound message');
 const m=await r.json();const sender=plain(m.from,160).match(/<([^>]+)>/)?.[1]||plain(m.from,160);
 const address=sender.toLowerCase(),subject=plain(m.subject,160),body=plain(m.text,1500),to=Array.isArray(m.to)?m.to:[];
 if(!emailOK(sender)||!to.some(x=>String(x).toLowerCase().includes(String(process.env.RESEND_INBOUND_ADDRESS).toLowerCase()))||!body)return json(res,200,{ok:true,ignored:true});
 if(address===String(process.env.LEAD_FROM_EMAIL).toLowerCase()||address===String(process.env.LEAD_TO_EMAIL).toLowerCase()||/mailer-daemon|no-?reply|postmaster/.test(address)||/auto-submitted:\s*auto/i.test(JSON.stringify(m.headers||{})))return json(res,200,{ok:true,ignored:true});
 if(throttle('email:'+crypto.createHash('sha256').update(sender).digest('hex'),4,3600000))return json(res,200,{ok:true,rateLimited:true});
 const ticket=newTicket({name:plain(m.from,70),email:sender,message:'Subject: '+subject+'\n'+body},'Inbound email');
 const result=await inboundMessage(ticket,fetchFn,aiReply);
 const response=await sendEmail(sender,'Re: '+subject+' · Dance Manager Next',result.reply+'\n\nReference: '+ticket.id+'\n\nThis is an automated acknowledgment. A human will follow up when available.',fetchFn);
 return json(res,202,{ok:true,ownerNotified:true,automatedResponseAccepted:response});
}
async function ownerInbox(req,res,fetchFn){
 const key=process.env.ADMIN_API_TOKEN;
 const incoming=String(req.headers.authorization||'');
 if(!key||key.length<24||incoming!=='Bearer '+key)return json(res,403,{error:'Owner authentication required'});
 if(!hasStore())return json(res,503,{error:'Persistent queue not configured'});
 if(req.method==='GET'){
  const ids=await redis(['ZREVRANGE','dmnext:tickets',0,49],fetchFn),tickets=[];
  for(const id of ids||[]){const s=await redis(['GET','dmnext:ticket:'+id],fetchFn);if(s){try{tickets.push(JSON.parse(s));}catch(e){}}}
  return json(res,200,{tickets});
 }
 if(req.method==='POST'){
  const body=JSON.parse(await readRaw(req,2500)),id=plain(body.id,30);
  if(!/^DM-[A-F0-9]{10}$/.test(id))return json(res,400,{error:'Invalid ticket'});
  const stored=await redis(['GET','dmnext:ticket:'+id],fetchFn);
  if(!stored)return json(res,404,{error:'Ticket not found'});
  const t=JSON.parse(stored);t.status='Human follow-up recorded';t.resolvedAt=new Date().toISOString();
  await redis(['SET','dmnext:ticket:'+id,JSON.stringify(t),'EX',expiry],fetchFn);
  const context=await loadConversation(t,fetchFn);
  context.humanMode=true;
  await saveConversation(t,context,fetchFn);
  return json(res,200,{ok:true,id,status:t.status,automaticRepliesPaused:true});
 }
 return json(res,405,{error:'Method not allowed'});
}
async function handle(req,res,fetchFn,aiReply){
 const origin=req.headers.origin||'',p=(req.url||'').split('?')[0];
 if(p==='/api/owner/inquiries'||p==='/api/owner/resolve'){
  try{return await ownerInbox(req,res,fetchFn);}catch(e){return json(res,503,{error:'Inquiry queue temporarily unavailable'});}
 }
 if(p==='/webhooks/resend/inbound'||p==='/webhooks/twilio/sms'){
  if(req.method!=='POST')return json(res,405,{error:'Method not allowed'});
  try{return p.includes('resend')?await inboundEmail(req,res,fetchFn,aiReply):await inboundSms(req,res,fetchFn,aiReply);}
  catch(e){return json(res,503,{error:'Inbound service temporarily unavailable'});}
 }
 if(!allowedOrigins.includes(origin))return json(res,403,{error:'Origin not permitted'},origin);
 if(req.method==='OPTIONS'){res.writeHead(204,{'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type','Access-Control-Max-Age':'3600','Vary':'Origin'});return res.end();}
 if(req.method!=='POST')return json(res,405,{error:'Method not allowed'},origin);
 if(!String(req.headers['content-type']||'').startsWith('application/json'))return json(res,415,{error:'Use JSON'},origin);
 if(throttle('lead:'+clientHash(req),4,3600000)||throttle('lead:global',75,3600000))return json(res,429,{error:'Too many inquiries. Please try again later.'},origin);
 try{const raw=await readRaw(req),body=JSON.parse(raw),result=await submitLead(body,fetchFn,p==='/api/handoff'?'Human handoff request':'Website inquiry');
  const {code=202,...rest}=result;return json(res,code,rest,origin);
 }catch(e){return json(res,e.status===413?413:502,{error:e.status===413?'Your message is too long.':'Unable to send right now. Please try again.'},origin);}
}
module.exports={matches,status,handle,verifySvix,verifyTwilio,submitLead};
