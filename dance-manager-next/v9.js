/* Dance Manager Next V9 — unified support concierge and owner response readiness.
 * This is an independent preview. Real contact delivery depends on secured providers.
 */
(function(){
'use strict';
let channelHealth=null;
if(!NAV.owner.some(x=>x[0]==='response-center')){
 const idx=NAV.owner.findIndex(x=>x[0]==='messages');
 NAV.owner.splice(idx<0?NAV.owner.length:idx+1,0,['response-center','chat','Response center']);
}
const originalContent=content,originalChatPanel=chatPanel;
function indicator(state){return '<span class="dm9-indicator '+(state?'connected':'pending')+'">'+(state?'Connected':'Setup required')+'</span>';}
function feature(title,desc,enabled){return '<div class="dm9-channel"><span class="dm9-channel-icon">'+icon(enabled?'check':'clock')+'</span><div><b>'+esc(title)+'</b><p>'+esc(desc)+'</p></div>'+indicator(enabled)+'</div>';}
function responseCenter(){
 const h=channelHealth;
 return head('Response center','How the automated concierge receives questions and hands conversations over to your team.')+
 '<div class="dm9-owner-hero"><div><span class="dm9-eyebrow">ONE WELCOMING FRONT DESK · MULTIPLE CHANNELS</span><h2>Never leave a visitor wondering what happens next.</h2><p>Acknowledge inquiries promptly, answer general questions, and give the studio owner a clear follow-up task. The assistant identifies itself as automated and hands off matters that require judgment.</p></div><div class="dm9-symbol">✦</div></div>'+
 '<div class="dm9-metrics"><div><b>'+ (h?.aiConfigured?'Live AI':'Guided demo')+'</b><span>Website assistance</span></div><div><b>'+(h?.leadsConfigured?'Active':'Not connected')+'</b><span>Inquiry emails</span></div><div><b>'+(h?.smsConfigured?'Active':'Not connected')+'</b><span>Owner text alerts</span></div></div>'+
 '<section class="dm9-owner-panel"><header><h3>Communication readiness</h3><span>Verified from the independent backend, when reachable</span></header>'+
 (h?
 feature('Live website AI','Answers routine questions about navigation, studios, competitions and software demonstrations.',h.aiConfigured)+
 feature('Email inquiry & receipt','Sends staff an inquiry with context, then attempts an automated visitor acknowledgment.',h.leadsConfigured)+
 feature('Owner SMS alert','Sends a short alert to an approved owner number when the provider is configured.',h.smsConfigured)+
 feature('Inbound email responses','Signed email-received events can create a follow-up request and send an automated acknowledgment.',h.inboundEmailConfigured)+
 feature('Inbound text responses','Signed SMS events can acknowledge questions and notify the owner.',h.inboundSmsConfigured)+
 feature('Persistent staff queue','Encrypted HTTPS access to an owner-controlled external ticket store (credentials required).',h.inboxConfigured):
 '<p class="dm9-missing">'+icon('info')+' Live connection status is not confirmed. Demo only — no email or text delivery is promised.</p>')+
 '</section>'+
 '<div class="dm9-two"><section class="dm9-owner-panel"><header><h3>Visitor journey</h3></header><ol class="dm9-journey"><li><b>Welcome</b><span>Offer a warm greeting and show clear choices, without demanding contact information.</span></li><li><b>Help immediately</b><span>Answer verified questions, guide visitors to the right pages, and suggest a relevant demo.</span></li><li><b>Ask permission</b><span>Offer a human follow-up form only if the visitor wants one. Separate consent for optional SMS and marketing.</span></li><li><b>Notify & acknowledge</b><span>Alert the owner and send an automated receipt only when real delivery providers accept the request.</span></li><li><b>Hand to a person</b><span>Share the requested follow-up and limited chat context, so staff do not start from zero.</span></li></ol></section>'+
 '<section class="dm9-owner-panel"><header><h3>Operational boundaries</h3></header><div class="dm9-guidelines"><p>✓ Visitors always know when they are speaking with an automated assistant.</p><p>✓ The bot does not confirm an appointment, quote unverified prices or promise exact human response times.</p><p>✓ Do not enter real child or guardian records into this public demonstration.</p><p>✓ New inquiries are sent only after the adult agrees to a follow-up.</p><p>✓ Production needs a private staff login, durable storage, provider setup and real-world delivery tests.</p></div><button class="btn btn-soft" type="button" data-action="dm9-open-help">'+icon('chat')+' Try visitor guide</button></section></div>';
}
content=function(){return role==='owner'&&route==='response-center'?responseCenter():originalContent();};
chatPanel=function(){
 let html=originalChatPanel();
 if(!html.includes('dm5-chat-pane'))return html;
 const active=Boolean(channelHealth?.leadsConfigured);
 const assist='<div class="dm9-help-band"><span>'+icon('shield')+' Automated assistance · You can ask questions without sharing contact details.</span></div>';
 html=html.replace('<div class="dm5-choices">',assist+'<div class="dm5-choices">');
 if(html.includes('class="dm5-choices"')){
  html=html.replace('</div><form id="chat-form"', '<div class="dm9-human"><button type="button" data-dm5-action="demo">'+icon('mail')+' '+(active?'Request a human follow-up':'Preview the contact process')+'</button><small>'+(active?'A team member can follow up by email. A response time is not guaranteed.':'Actual delivery is not connected yet.')+'</small></div></div><form id="chat-form"');
 }
 if(html.includes('dm5-lead-form')){
  html=html.replace('<h3>Preview your demo request</h3>','<h3>Ask our team to follow up</h3>');
  html=html.replace('For a call back (optional)','Optional phone, e.g. +15551234567');
  html=html.replace('What can we help you with? (required)','Tell us what you need help with (required)');
  html=html.replace('This preview use sample information','this preview use sample information');
  if(!active)html=html.replace('<form id="dm5-lead-form"', '<p class="dm9-demo-warning">Contact delivery is not enabled. Please use fictional information only.</p><form id="dm5-lead-form"');
 }
 return html;
};
const existingDo=doAction;
doAction=function(a){
 if(a==='dm9-open-help'){chatOpen=true;render();return;}
 return existingDo(a);
};
async function init(){
 try{
  const r=await fetch('./v7-config.json',{cache:'no-store'});
  if(!r.ok)throw Error('No config');
  const conf=await r.json(),url=new URL(String(conf.apiBase||''));
  if(url.protocol!=='https:')throw Error('Not secure');
  const s=await fetch(url.origin+'/health',{cache:'no-store',signal:AbortSignal.timeout(10000)});
  if(!s.ok)throw Error('No health');
  const data=await s.json();
  if(data?.status==='ok')channelHealth=data;
 }catch(e){channelHealth=null;}
 render();
}
init();
})();