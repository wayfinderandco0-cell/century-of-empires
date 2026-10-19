/* Dance Manager Next V2: fictional dancer cards and competition planner.
   Independent extension; local-only demo. Never enter actual minor/student data. */
(function(){
'use strict';
ICONS.trophy='<path d="M8 3h8v8a4 4 0 0 1-8 0V3Z"/><path d="M8 5H4v3a4 4 0 0 0 4 4M16 5h4v3a4 4 0 0 1-4 4M12 15v4m-5 2h10"/>';
ICONS.medal='<circle cx="12" cy="16" r="5"/><path d="M8 12 4 3h5l3 6 3-6h5l-4 9"/><path d="m12 13 1 2 2 .3-1.5 1.5.4 2.2L12 18l-1.9 1 .4-2.2L9 15.3l2-.3Z"/>';
ICONS.pin='<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>';
ICONS.camera='<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M7 7 9 4h6l2 3"/><circle cx="12" cy="14" r="3"/>';
ICONS.flag='<path d="M5 22V4m0 1c4-4 8 3 14-1v12c-6 4-10-3-14 1"/>';
const initialProfiles=[
 ['s1','Ballet · Contemporary','Graceful storytelling and classical technique. Exploring choreography and ensemble performance.',true],
 ['s2','Jazz · Lyrical','An energetic performer with a love for musicality, sharp lines, and group routines.',true],
 ['s3','Ballet · Musical Theatre','Focused on balance, expression, and creative performance.',true],
 ['s4','Hip-Hop · Freestyle','Loves rhythm, improvisation, and high-energy choreography.',true],
 ['s5','Tap · Musical Theatre','Enjoys musical timing and intricate tap combinations.',true],
 ['s6','Contemporary · Modern','Brings expressive movement and strong floor work to every routine.',true],
 ['s7','Ballet','Building a foundation in technique, confidence, and stage presence.',false],
 ['s8','Jazz · Contemporary','Enjoys dance team performances, lyrical pieces, and creative choreography.',true]
];
const sampleCompetitions=[
 {id:'dc1',title:'Autumn Spotlight Invitational',date:'2026-09-12',city:'Pensacola, FL',venue:'Example Performing Arts Center',deadline:'2026-08-15',status:'Completed',fee:75,participants:['s1','s2','s4']},
 {id:'dc2',title:'Coastal Dance Classic',date:'2026-10-03',city:'Mobile, AL',venue:'Example Civic Theatre',deadline:'2026-09-02',status:'Completed',fee:85,participants:['s2','s5','s8']},
 {id:'dc3',title:'Winter Stage Challenge',date:'2026-12-05',city:'Pensacola, FL',venue:'Demo Convention Center',deadline:'2026-11-12',status:'Upcoming',fee:90,participants:['s1','s3','s6']},
 {id:'dc4',title:'Spring Dance Showcase',date:'2027-03-20',city:'New Orleans, LA',venue:'Example Arts Hall',deadline:'2027-02-18',status:'Upcoming',fee:95,participants:['s2','s4','s8']}
];
const sampleAwards=[
 {id:'da1',studentId:'s1',competitionId:'dc1',title:'1st Place — Ballet Solo',placement:'Gold'},
 {id:'da2',studentId:'s2',competitionId:'dc1',title:'Judges’ Excellence — Jazz',placement:'Special Award'},
 {id:'da3',studentId:'s4',competitionId:'dc1',title:'2nd Place — Hip-Hop',placement:'Silver'},
 {id:'da4',studentId:'s2',competitionId:'dc2',title:'1st Place — Jazz Group',placement:'Gold'},
 {id:'da5',studentId:'s5',competitionId:'dc2',title:'3rd Place — Tap',placement:'Bronze'},
 {id:'da6',studentId:'s8',competitionId:'dc2',title:'Choreography Recognition',placement:'Special Award'}
];
function ensureV2(){
 if(!Array.isArray(db.dancerProfiles))db.dancerProfiles=initialProfiles.map(([studentId,specialties,bio,listed])=>({studentId,specialties,bio,listed}));
 if(!Array.isArray(db.competitions))db.competitions=sampleCompetitions.map(x=>({...x,participants:[...x.participants]}));
 if(!Array.isArray(db.awards))db.awards=sampleAwards.map(x=>({...x}));
 save();
}
ensureV2();
NAV.owner.splice(2,0,['dancers','medal','Dancer cards'],['competitions','trophy','Competitions']);
MOBILE.owner=['overview','dancers','competitions'];
const v1Content=content;
content=function(){if(role==='owner'&&route==='dancers')return dancerCards();if(role==='owner'&&route==='competitions')return competitionPlanner();return v1Content();};
const v1Marketing=marketing;
marketing=function(){
 const teaser='<section id="spotlight-preview" class="section alt-section"><div class="section-inner"><div class="section-head"><div class="eyebrow">Celebrate every milestone</div><h2>Every dancer has a story worth telling.</h2><p>Player-card inspired dancer profiles, achievements, past competitions and a dedicated planner for what comes next.</p></div><div class="dm-marketing-teaser"><div class="dm-teaser-art">★ <span>DANCER SPOTLIGHT</span> ★</div><div><h3>Profiles meet performance history.</h3><p>Discover specialties, personal bios, award records, and event entries, all linked in one studio workspace.</p><div class="dm-hero-buttons">'+button('Explore dancer cards '+icon('arrow'),'show-dancers','btn-primary')+button('Competition planner','show-competitions','btn-outline')+'</div><p class="fineprint">All displayed profiles and competitions are fictional. No public profiles of children are published from this demo.</p></div></div></div></section>';
 return v1Marketing().replace('<section id="how-it-works"',teaser+'<section id="how-it-works"').replace('NEXT · PRIVATE V1','NEXT · DEMO V2');
};
const v1Brand=brand;
brand=function(){return v1Brand().replace('NEXT · PRIVATE V1','NEXT · DEMO V2');};
demoBanner=function(){return `<div class="demo-banner">${icon('shield')} PUBLIC TEST PREVIEW · Fictional data only · No real dancer information · Original site untouched</div>`;};
function profile(studentId){return db.dancerProfiles.find(p=>p.studentId===studentId)||{studentId,specialties:db.students.find(s=>s.id===studentId)?.level||'Dance',bio:'Add a short dancer biography from the profile editor.',listed:false};}
function competitionsFor(id){return db.competitions.filter(e=>Array.isArray(e.participants)&&e.participants.includes(id));}
function awardsFor(id){return db.awards.filter(a=>a.studentId===id);}
function avatar(student,idx=0){return '<div class="dm-portrait dm-portrait-'+(idx%4+1)+'"><span class="dm-dance-silhouette">'+icon('dance')+'</span><span class="dm-monogram">'+esc(initials(student.name))+'</span></div>';}
function dancerCard(s,idx){
 const p=profile(s.id),awards=awardsFor(s.id),events=competitionsFor(s.id);
 return '<article class="dm-player-card"><div class="dm-card-top"><span class="dm-card-eyebrow">DANCE MANAGER · STUDIO ROSTER</span><span class="dm-card-no">'+String(idx+1).padStart(2,'0')+'</span></div>'+avatar(s,idx)+'<div class="dm-card-info"><span class="dm-card-sub">'+esc((p.specialties||s.level).split('·')[0].trim().toUpperCase())+' SPECIALIST</span><h3>'+esc(s.name)+'</h3><p class="dm-short-bio">'+esc(p.bio)+'</p><div class="dm-discipline">'+(p.specialties||s.level||'Dance').split('·').slice(0,3).map(x=>'<span>'+esc(x.trim())+'</span>').join('')+'</div><div class="dm-card-metrics"><div><strong>'+events.length+'</strong><small>Competitions</small></div><div><strong>'+awards.length+'</strong><small>Awards</small></div></div><button class="btn btn-primary dm-card-button" data-action="dancer-'+esc(s.id)+'">View player card '+icon('arrow')+'</button></div></article>';
}
function dancerCards(){
 const listed=db.students.filter(s=>profile(s.id).listed),all=db.students.length;
 return head('Dancer spotlight','NFL-style player cards for your studio. Cards are visible only inside this fictional demo.',button(icon('plus')+' Edit profiles','manage-roster','btn-outline'))+
 '<div class="dm-spotlight-hero"><div><span class="dm-mini-label">DANCER HALL OF FAME</span><h2>The talent behind every performance.</h2><p>Celebrate specialties, personal stories, competition history and trophies without losing the practical student record behind the scenes.</p><div class="dm-hero-buttons">'+button('Manage listed dancers','manage-roster','btn-light')+button('Plan competitions','show-competitions','btn-outline')+'</div></div><div class="dm-hero-trophy">'+icon('trophy')+'</div></div>'+
 '<div class="dm-simple-stats"><div><strong>'+listed.length+'</strong><span>Featured dancer cards</span></div><div><strong>'+db.awards.length+'</strong><span>Recorded achievements</span></div><div><strong>'+db.competitions.length+'</strong><span>Tracked competitions</span></div></div>'+
 '<div class="dm-section-line"><h2>Our studio roster</h2><span class="pill blue">'+listed.length+' of '+all+' featured</span></div>'+
 '<div class="dm-player-grid">'+(listed.length?listed.map((s,i)=>dancerCard(s,i)).join(''):'<div class="empty">No dancer cards are currently listed. Choose “Manage listed dancers” to turn some on.</div>')+'</div>'+
 '<div class="safe-notice dm-privacy">'+icon('shield')+' Privacy first: “featured” controls this private demo roster, not a public directory. In production, public child profiles and images must require verified guardian permission and limited, revocable sharing. Do not enter real children’s details here.</div>';
}
function eventFormat(e){return prettyDate(e.date)+' · '+esc(e.city);}
function competitionPlanner(){
 const upcoming=[...db.competitions].filter(x=>x.status!=='Completed').sort((a,b)=>a.date.localeCompare(b.date));
 const past=[...db.competitions].filter(x=>x.status==='Completed').sort((a,b)=>b.date.localeCompare(a.date));
 return head('Competition center','Plan the season, manage entries, and celebrate results — fictional data only.',button(icon('plus')+' Add competition','new-competition'))+
 '<div class="dm-event-intro"><div><span class="dm-mini-label">COMPETITION COMMAND CENTER</span><h2>From first entry to final trophy.</h2><p>Keep your dancers, deadlines, locations, performances, and results in one place.</p></div><div class="dm-calendar-art">'+icon('calendar')+'</div></div>'+
 '<div class="dm-simple-stats"><div><strong>'+upcoming.length+'</strong><span>Upcoming events</span></div><div><strong>'+past.length+'</strong><span>Past events</span></div><div><strong>'+db.awards.length+'</strong><span>Awards recorded</span></div></div>'+
 '<div class="dm-section-line"><h2>Upcoming competitions</h2><span class="pill blue">Manage registrations</span></div>'+
 (upcoming.length?'<div class="dm-event-list">'+upcoming.map(eventCard).join('')+'</div>':'<div class="empty">No upcoming events yet.</div>')+
 '<div class="dm-section-line dm-past-title"><h2>Past competitions & results</h2><span class="pill green">Performance history</span></div>'+
 (past.length?'<div class="dm-event-list">'+past.map(eventCard).join('')+'</div>':'<div class="empty">No completed events recorded.</div>')+
 '<div class="safe-notice dm-privacy">'+icon('shield')+' All event names, cities, dates, venues, fees, participants and results are demonstration examples — not real bookings or competition results.</div>';
}
function eventCard(e){
 const date=new Date(e.date+'T12:00:00');const mon=Number.isNaN(+date)?'—':date.toLocaleDateString('en-US',{month:'short'}),day=Number.isNaN(+date)?'—':date.getDate();
 const completed=e.status==='Completed',awards=db.awards.filter(a=>a.competitionId===e.id).length;
 return '<article class="dm-event-card"><div class="dm-event-date"><strong>'+mon+'</strong><b>'+day+'</b><small>'+esc(e.date.slice(0,4))+'</small></div><div class="dm-event-copy"><div class="dm-event-tags"><span class="pill '+(completed?'green':'blue')+'">'+esc(e.status)+'</span> <span>'+esc(e.city)+'</span></div><h3>'+esc(e.title)+'</h3><p>'+icon('pin')+' '+esc(e.venue)+'</p><p class="dm-event-fine">'+(completed?icon('medal')+' '+awards+' recorded awards':icon('clock')+' Entry deadline '+prettyDate(e.deadline))+' · '+(e.participants||[]).length+' dancers</p></div><button class="btn btn-soft dm-event-button" data-action="event-'+esc(e.id)+'">Manage '+icon('arrow')+'</button></article>';
}
function selector(name,items,selected){return '<div class="form-field"><label class="label" for="'+name+'">Dancer</label><select name="'+name+'" id="'+name+'">'+items.map(s=>'<option value="'+esc(s.id)+'" '+(s.id===selected?'selected':'')+'>'+esc(s.name)+'</option>').join('')+'</select></div>';}
function profileDialog(id){
 const s=db.students.find(x=>x.id===id);if(!s)return;
 const p=profile(id),aw=awardsFor(id),events=competitionsFor(id);
 modalForm(s.name+' — dancer card',
 '<div class="dm-dialog-summary">'+avatar(s,1)+'<div><span class="dm-mini-label">STUDIO DANCER PROFILE</span><h3>'+esc(s.name)+'</h3><p>'+esc(p.specialties||s.level)+'</p></div></div>'+
 '<p class="small">'+esc(p.bio)+'</p><h3 class="dm-modal-h3">'+icon('trophy')+' Awards & achievements</h3>'+
 (aw.length?aw.map(a=>'<div class="dm-award-row"><span>'+icon('medal')+'</span><div><strong>'+esc(a.title)+'</strong><small>'+esc(db.competitions.find(e=>e.id===a.competitionId)?.title||'Competition')+' · '+esc(a.placement||'Award')+'</small></div></div>').join(''):'<p class="muted small">No achievements recorded for this dancer.</p>')+
 '<h3 class="dm-modal-h3">'+icon('calendar')+' Competitions attended</h3>'+
 (events.length?events.map(e=>'<div class="dm-award-row"><span>'+icon('flag')+'</span><div><strong>'+esc(e.title)+'</strong><small>'+eventFormat(e)+'</small></div></div>').join(''):'<p class="muted small">No competitions recorded.</p>')+
 '<div class="modal-footer">'+button('Edit card','edit-dancer-'+s.id,'btn-primary')+button('Close','close-modal','btn-outline')+'</div>','dancer');
}
function editProfileDialog(id){
 const s=db.students.find(x=>x.id===id);if(!s)return;const p=profile(id);
 modalForm('Edit dancer card — '+s.name,
 '<div class="safe-notice">Use fictional sample information only. This prototype has no secure profiles, uploads, or permissions.</div>'+
 '<form id="dm-profile-form"><input type="hidden" name="studentId" value="'+esc(s.id)+'">'+
 field('dm-specialties','Specialties / dance styles','e.g. Ballet · Jazz','text','required maxlength="140"',p.specialties||s.level)+
 '<div class="form-field"><label class="label" for="dm-biography">Background & biography</label><textarea id="dm-biography" name="biography" maxlength="500" rows="4" required>'+esc(p.bio||'')+'</textarea></div>'+
 '<label class="dm-check-label"><input type="checkbox" name="listed" '+(p.listed?'checked':'')+'> Display this fictional dancer card on the studio demo roster</label>'+
 '<p class="fineprint">An actual portrait uploader requires secure storage and parent/guardian authorization. The demo currently shows an illustrated placeholder.</p>'+footer('Save dancer card')+'</form>','edit-profile');
}
function rosterDialog(){
 modalForm('Choose featured dancers','<p class="small muted">Choose which fictional dancer cards appear in your studio’s internal showcase. This does not publish any student to the internet.</p>'+
 '<form id="dm-roster-form"><div class="dm-roster-choices">'+db.students.map(s=>'<label class="dm-roster-choice"><input type="checkbox" name="featured" value="'+esc(s.id)+'" '+(profile(s.id).listed?'checked':'')+'><span class="student-avatar">'+esc(initials(s.name))+'</span><span>'+esc(s.name)+'</span></label>').join('')+'</div>'+footer('Update featured roster')+'</form>','roster-toggle');
}
function eventDialog(id){
 const e=db.competitions.find(c=>c.id===id);if(!e)return;
 const registered=db.students.filter(s=>e.participants.includes(s.id));
 modalForm(e.title+' — event manager',
 '<div class="dm-event-dialog-header">'+icon('calendar')+' '+eventFormat(e)+'</div><p class="small muted">'+icon('pin')+' '+esc(e.venue)+'</p>'+
 '<div class="dm-info-grid"><div><strong>'+prettyDate(e.deadline)+'</strong><small>Entry deadline</small></div><div><strong>'+USD(e.fee)+'</strong><small>Illustrative entry fee</small></div><div><strong>'+esc(e.status)+'</strong><small>Status</small></div></div>'+
 '<h3 class="dm-modal-h3">Registered dancers</h3>'+
 (registered.length?registered.map(s=>'<div class="dm-award-row"><span class="student-avatar">'+esc(initials(s.name))+'</span><div><strong>'+esc(s.name)+'</strong><small>'+esc(profile(s.id).specialties||s.level)+'</small></div></div>').join(''):'<p class="muted small">No dancers currently entered.</p>')+
 '<div class="dm-dialog-actions">'+button('Add dancer','enter-'+e.id,'btn-soft btn-small')+button('Record result','award-'+e.id,'btn-soft btn-small')+(e.status!=='Completed'?button('Mark completed','finish-'+e.id,'btn-outline btn-small'):'')+'</div>'+
 '<p class="fineprint">This screen manages fictional entries and results locally. It does not register dancers with an organizer or send notifications.</p>','event');
}
function newEventDialog(){
 modalForm('Add a sample competition',
 '<div class="safe-notice">Demo only — use invented event information. No external registration occurs.</div><form id="dm-event-form">'+
 field('dm-event-title','Competition title','e.g. Summer Showcase')+
 '<div class="form-grid">'+field('dm-event-date','Competition date','','date')+field('dm-event-deadline','Entry deadline','','date')+'</div>'+
 '<div class="form-grid">'+field('dm-event-city','City, state','e.g. Pensacola, FL')+field('dm-event-venue','Venue','e.g. Demo Arts Hall')+'</div>'+
 field('dm-event-fee','Entry fee estimate in USD','75','number','required min="0" max="10000"')+footer('Add competition')+'</form>','new-event');
}
function entryDialog(id){
 const e=db.competitions.find(c=>c.id===id);if(!e)return;
 const available=db.students.filter(s=>!e.participants.includes(s.id));
 modalForm('Add dancer — '+e.title,available.length?'<form id="dm-entry-form"><input type="hidden" name="eventId" value="'+esc(id)+'">'+selector('studentId',available)+footer('Add to competition')+'</form>':'<div class="empty">All fictional dancers are already entered.</div>','entry');
}
function awardDialog(id){
 const e=db.competitions.find(c=>c.id===id);if(!e)return;
 const participants=db.students.filter(s=>e.participants.includes(s.id));
 modalForm('Record award — '+e.title,participants.length?
 '<form id="dm-award-form"><input type="hidden" name="eventId" value="'+esc(id)+'">'+selector('studentId',participants)+
 field('dm-award-title','Result / award','e.g. 1st Place — Contemporary Solo')+
 '<div class="form-field"><label class="label" for="dm-placement">Recognition</label><select id="dm-placement" name="placement"><option>Gold</option><option>Silver</option><option>Bronze</option><option>Special Award</option><option>Participation</option></select></div>'+footer('Record achievement')+'</form>':'<p class="muted">Add a dancer to this event before recording a result.</p>','award');
}
const prevDoAction=doAction;
doAction=function(action){
 if(action==='show-dancers'){navigate('owner','dancers');return;}
 if(action==='show-competitions'){navigate('owner','competitions');return;}
 if(action==='manage-roster'){rosterDialog();return;}
 if(action==='new-competition'){newEventDialog();return;}
 if(action.startsWith('dancer-')){profileDialog(action.slice(7));return;}
 if(action.startsWith('edit-dancer-')){editProfileDialog(action.slice(12));return;}
 if(action.startsWith('event-')){eventDialog(action.slice(6));return;}
 if(action.startsWith('enter-')){entryDialog(action.slice(6));return;}
 if(action.startsWith('award-')){awardDialog(action.slice(6));return;}
 if(action.startsWith('finish-')){const c=db.competitions.find(x=>x.id===action.slice(7));if(c){c.status='Completed';save();modal='';render();toast('Competition marked completed (demo).')}return;}
 if(action==='reset'){if(window.confirm('Reset all fictional demo data, including dancer cards and competitions?')){db=sample();ensureV2();render();toast('All fictional demo data restored.')}return;}
 prevDoAction(action);
};
document.addEventListener('submit',function(e){
 const ids=['dm-profile-form','dm-roster-form','dm-event-form','dm-entry-form','dm-award-form'];
 if(!ids.includes(e.target.id))return;
 e.preventDefault();
 const form=e.target,d=new FormData(form),str=k=>String(d.get(k)||'').trim();
 if(form.id==='dm-profile-form'){
  const s=db.students.find(x=>x.id===str('studentId'));if(!s)return;
  const spec=str('dm-specialties').slice(0,140),bio=str('biography').slice(0,500);
  if(!spec||!bio)return toast('Add specialties and a short biography.');
  const p=profile(s.id);p.studentId=s.id;p.specialties=spec;p.bio=bio;p.listed=d.has('listed');
  const existing=db.dancerProfiles.findIndex(x=>x.studentId===s.id);
  if(existing>=0)db.dancerProfiles[existing]=p;else db.dancerProfiles.push(p);
 }else if(form.id==='dm-roster-form'){
  const keep=new Set(d.getAll('featured'));
  for(const s of db.students){let p=profile(s.id);p.studentId=s.id;p.listed=keep.has(s.id);if(!db.dancerProfiles.some(x=>x.studentId===s.id))db.dancerProfiles.push(p);}
 }else if(form.id==='dm-event-form'){
  const title=str('dm-event-title').slice(0,120),date=str('dm-event-date'),deadline=str('dm-event-deadline'),city=str('dm-event-city').slice(0,120),venue=str('dm-event-venue').slice(0,120),fee=Number(str('dm-event-fee'));
  if(!title||!date||!deadline||!city||!venue||!Number.isFinite(fee)||fee<0||fee>10000)return toast('Please complete each event field.');
  db.competitions.push({id:'dc'+Date.now(),title,date,deadline,city,venue,fee,status:'Upcoming',participants:[]});
 }else if(form.id==='dm-entry-form'){
  const event=db.competitions.find(x=>x.id===str('eventId')),sid=str('studentId');
  if(!event||!db.students.some(s=>s.id===sid)||event.participants.includes(sid))return toast('Choose an available dancer.');
  event.participants.push(sid);
 }else if(form.id==='dm-award-form'){
  const event=db.competitions.find(x=>x.id===str('eventId')),sid=str('studentId'),title=str('dm-award-title').slice(0,150);
  if(!event||!event.participants.includes(sid)||!title)return toast('Choose an entered dancer and result.');
  db.awards.push({id:'da'+Date.now(),studentId:sid,competitionId:event.id,title,placement:str('placement')});
 }
 save();modal='';render();toast('Fictional record saved on this device.');
});
document.head.insertAdjacentHTML('beforeend','<link rel="stylesheet" href="./v2.css">');
render();
})();