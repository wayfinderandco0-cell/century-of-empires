/* Shared, pure logic. No secrets. */
export const clip = (v, n=200) => typeof v === 'string' ? v.trim().slice(0,n) : '';
export const validEmail = v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v || '') && (v || '').length <= 120;
export const validPhone = v => /^\+[1-9]\d{7,14}$/.test(v || '');
export function normalizePhone(s) {
 const t=clip(s,30).replace(/[\s().-]/g,'');
 if(/^\d{10}$/.test(t)) return '+1'+t;
 if(/^1\d{10}$/.test(t)) return '+'+t;
 return /^\+[1-9]\d{7,14}$/.test(t) ? t : '';
}
export function validateLead(body) {
 if (!body || typeof body !== 'object' || Array.isArray(body)) return {error:'Invalid inquiry.'};
 if (clip(body.website,30)) return {error:'Invalid inquiry.'}; // honeypot
 const name=clip(body.name,70), email=clip(body.email,120).toLowerCase(),
 phone=normalizePhone(body.phone), rawPhone=clip(body.phone,30),
 studio=clip(body.studio,90), visitorType=clip(body.visitorType,60),
 message=clip(body.message,1200), transcript=clip(body.transcript,1750),
 method=clip(body.contactMethod,20)||'email',
 smsConsent=body.smsReplyConsent === true, callConsent=body.callReplyConsent === true;
 if (!name || !validEmail(email) || !message || !studio) return {error:'Enter your name, studio, email and a message.'};
 if (body.adultConfirmed !== true || body.consent !== true) return {error:'An adult must agree to follow-up.'};
 if (rawPhone && !validPhone(phone)) return {error:'Enter a valid phone number including area code.'};
 if (!['email','sms','call'].includes(method)) return {error:'Choose a valid contact method.'};
 if ((method==='sms'||method==='call'||smsConsent||callConsent)&&!phone) return {error:'Enter a phone number for text or call follow-up.'};
 if (method==='sms'&&!smsConsent) return {error:'Text-message permission is required for a text reply.'};
 if (method==='call'&&!callConsent) return {error:'Callback permission is required for a phone call.'};
 return {value:{name,email,phone,studio,visitorType,message,transcript,contactMethod:method,
  smsConsent,callConsent,marketingOptIn:body.marketingOptIn===true}};
}
export function allowedOrigin(origin, list) {
 try { const u = new URL(origin); return u.origin===origin && u.protocol==='https:' &&
  String(list||'').split(',').map(s=>s.trim()).includes(origin);}catch{return false;}
}
export function isHumanMail(from,headers) {
 const h=name=>String(headers?.get?.(name)||'').toLowerCase();
 if (!validEmail(String(from||''))) return false;
 if (/^(no-?reply|donotreply|mailer-daemon|postmaster)@/i.test(from)) return false;
 if (h('auto-submitted') && h('auto-submitted')!=='no') return false;
 if (h('precedence').match(/bulk|list|junk/)) return false;
 if (h('x-autoreply') || h('x-autorespond') || h('list-id')) return false;
 return true;
}
export function ackText() {return "Thanks for contacting Dance Manager Next. I'm the automated assistant and I've received your message. I can help with general questions now. Our team has also been alerted, and someone will respond as soon as they're available if human help is needed.";}
export function xmlEscape(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));}
export function safeHeader(s){return clip(s,150).replace(/[\r\n]/g,' ').replace(/[\u0000-\u001f]/g,' ');}
export function sanitizeHistory(v){return Array.isArray(v)?v.slice(-8).filter(x=>x&&['user','assistant'].includes(x.role)).map(x=>({role:x.role,content:clip(x.text||x.content,750)})).filter(x=>x.content):[];}
