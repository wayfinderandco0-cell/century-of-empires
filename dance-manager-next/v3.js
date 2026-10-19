/* Dance Manager Next V3 — isolated homepage and competition category upgrade.
   Demonstration only. No real student profiles, payments or organizer entries. */
(function(){
'use strict';
const priorMarketing=marketing,priorContent=content,priorAction=doAction;
const priorBrand=brand;
brand=function(){return priorBrand().replace('NEXT · DEMO V2','NEXT · STAGING V3');};
const priorLayout=layout;
layout=function(){return priorLayout().replace('Independent V1 preview','Independent V3 preview');};
const formats=['Solo','Duo / Trio','Small Group','Large Group','Line','Production'];
const styles=['Ballet','Jazz','Lyrical','Contemporary','Hip-Hop','Tap','Musical Theatre'];
const initialRoutines=[
 {id:'dr1',title:'Moonlit Variation',format:'Solo',style:'Ballet',students:['s1'],result:'1st Place · demo'},
 {id:'dr2',title:'Electric Motion',format:'Solo',style:'Hip-Hop',students:['s4'],result:'2nd Place · demo'},
 {id:'dr3',title:'Between the Lines',format:'Duo / Trio',style:'Contemporary',students:['s1','s6'],result:'Featured routine · demo'},
 {id:'dr4',title:'Rhythm Collective',format:'Small Group',style:'Jazz',students:['s2','s3','s8'],result:'1st Place · demo'},
 {id:'dr5',title:'Broadway Lights',format:'Large Group',style:'Musical Theatre',students:['s2','s3','s5','s7'],result:'Showcase entry · demo'},
 {id:'dr6',title:'The Final Beat',format:'Production',style:'Tap',students:['s2','s3','s4','s5','s6','s8'],result:'Choreography recognition · demo'}
];
let chosenFormat='All',chosenStyle='All';
function ensureRoutines(){
 if(!Array.isArray(db.routines)){
  db.routines=initialRoutines.map(function(r){return {id:r.id,title:r.title,format:r.format,style:r.style,students:r.students.slice(),result:r.result};});
  save();
 }
}
ensureRoutines();
const ix=NAV.owner.findIndex(function(n){return n[0]==='competitions';});
if(ix>=0 && !NAV.owner.some(function(n){return n[0]==='categories';})){NAV.owner.splice(ix+1,0,['categories','flag','Categories & routines']);}
function actionButton(title,act,cls){return '<button type="button" class="'+cls+'" data-action="'+esc(act)+'">'+title+'</button>';}
function replaceThrough(src,start,end,next){
 const a=src.indexOf(start);if(a<0)return src;const b=src.indexOf(end,a);if(b<0)return src;
 return src.slice(0,a)+next+src.slice(b+end.length);
}
function headerV3(){
 return '<header class="site-header dm3-header"><div class="marketing-nav">'+brand()+
 '<nav class="nav-links dm3-top-links" aria-label="Site navigation"><a href="#dm3-explore">Studio</a>'+actionButton('Dancers','show-dancers','dm3-nav-action')+actionButton('Competitions','show-competitions','dm3-nav-action')+actionButton('Categories','show-categories','dm3-nav-action')+'<a href="#how-it-works">Parents</a><a href="#features">Features</a><a href="#pricing">Pricing</a></nav>'+
 '<div class="site-actions">'+button('Launch demo '+icon('arrow'),'owner','btn-light')+'<button type="button" class="menu-toggle" data-action="toggle-menu" aria-label="Open navigation menu">'+icon('menu')+'</button></div></div>'+
 '<div class="marketing-mobile '+(mobileMenu?'open':'')+'"><a href="#dm3-explore" data-action="close-menu">Studio tools</a>'+actionButton('Dancer profiles','show-dancers','dm3-mobile-action')+actionButton('Competitions','show-competitions','dm3-mobile-action')+actionButton('Categories & routines','show-categories','dm3-mobile-action')+'<a href="#how-it-works" data-action="close-menu">Parent portal</a><a href="#features" data-action="close-menu">Features</a><a href="#pricing" data-action="close-menu">Pricing</a>'+button('Launch studio demo','owner','btn-light')+'</div></header>';
}
function heroV3(){
 return '<section class="hero dm3-hero"><div class="dm3-hero-shade"></div><div class="dm3-hero-inner">'+
 '<div class="dm3-hero-text"><div class="dm3-kicker"><span></span> THE COMPLETE DANCE PLATFORM · CONCEPT</div>'+
 '<h1>Your entire studio.<br><em>One beautiful</em><br>place to grow.</h1>'+
 '<p>Bring dancers, classes, competitions, schedules, billing and families together. Built around the people who make dance happen.</p>'+
 '<div class="dm3-hero-actions">'+button('Explore the studio platform '+icon('arrow'),'owner','dm3-primary-btn')+'<a class="dm3-ghost-btn" href="#dm3-explore">Discover the features '+icon('arrow')+'</a></div>'+
 '<div class="dm3-small-proof"><span>'+icon('check')+' Studio management</span><span>'+icon('check')+' Competition planning</span><span>'+icon('check')+' Parent access</span></div>'+
 '</div><div class="dm3-hero-photo" role="img" aria-label="Atmospheric illustrative dance performance photograph">'+
 '<span class="dm3-photo-label">BEHIND EVERY PERFORMANCE <b>IS A BETTER WORKFLOW</b></span>'+
 '<div class="dm3-photo-widget"><span class="dm3-widget-icon">'+icon('calendar')+'</span><span><b>Everything in sync</b><small>Classes · Dancers · Events</small></span><span class="dm3-check">'+icon('check')+'</span></div></div>'+
 '</div><div class="dm3-footnote">Concept imagery only · All records in the interactive prototype are fictional</div></section>';
}
function exploreV3(){
 return '<section id="dm3-explore" class="dm3-explore"><div class="dm3-content-width">'+
 '<div class="dm3-section-head"><div><div class="dm3-eyebrow">ONE PLATFORM · EVERY PART OF DANCE</div><h2>Everything your dance community needs.</h2></div><p>Workflows for running the studio, supporting families and celebrating the dancers — without crowding the homepage.</p></div>'+
 '<div class="dm3-explore-grid">'+
 '<article class="dm3-explore-card dm3-card-studio"><div class="dm3-card-photo"></div><div class="dm3-card-content"><span>01 / RUN YOUR STUDIO</span><h3>Studio Management</h3><p>Students, instructors, scheduling, rosters, attendance and finances in one organized place.</p>'+actionButton('Open studio workspace '+icon('arrow'),'owner','dm3-card-btn')+'</div></article>'+
 '<article class="dm3-explore-card dm3-card-dancers"><div class="dm3-card-photo"></div><div class="dm3-card-content"><span>02 / CELEBRATE THE TALENT</span><h3>Dancer Profiles</h3><p>Player-card inspired bios, specialties, awards and performance histories.</p>'+actionButton('Explore dancer cards '+icon('arrow'),'show-dancers','dm3-card-btn')+'</div></article>'+
 '<article class="dm3-explore-card dm3-card-comp"><div class="dm3-card-photo"></div><div class="dm3-card-content"><span>03 / THE COMPETITION SEASON</span><h3>Competition Center</h3><p>Event calendars, routine categories, registrations, results and achievements.</p>'+actionButton('Explore competitions '+icon('arrow'),'show-competitions','dm3-card-btn')+'</div></article>'+
 '<article class="dm3-explore-card dm3-card-parent"><div class="dm3-card-photo"></div><div class="dm3-card-content"><span>04 / BRING FAMILIES ALONG</span><h3>Parent Portal</h3><p>Clear access to schedules, studio news and simulated family tuition records.</p>'+actionButton('Explore family portal '+icon('arrow'),'parent','dm3-card-btn')+'</div></article>'+
 '</div><div class="dm3-quick-row"><div><b>Explore event formats</b><span>Solo, duo/trio, groups, lines and production routines — all configurable examples.</span></div>'+actionButton('Browse competition categories '+icon('arrow'),'show-categories','dm3-categories-btn')+'</div></div></section>';
}
marketing=function(){
 let s=priorMarketing();
 s=replaceThrough(s,'<header class="site-header">','</header>',headerV3());
 s=replaceThrough(s,'<section class="hero">','</section>',heroV3());
 s=replaceThrough(s,'<div class="benefit-strip">','</div>','<div class="dm3-value-strip"><span>'+icon('calendar')+' CLASSES & SCHEDULES</span><span>'+icon('users')+' DANCER PROFILES</span><span>'+icon('trophy')+' COMPETITIONS & AWARDS</span><span>'+icon('phone')+' FAMILY CONNECTIONS</span></div>');
 s=replaceThrough(s,'<section id="spotlight-preview"','</section>',exploreV3());
 return s.replace('NEXT · DEMO V2','NEXT · STAGING V3');
};
function optionChips(arr,chosen,kind){
 return arr.map(function(v){
 const isOn=v===chosen;
 return actionButton(esc(v),kind+encodeURIComponent(v),'dm3-chip'+(isOn?' selected':''));
 }).join('');
}
function displayRoster(ids){
 return (ids||[]).map(function(id){const s=db.students.find(function(st){return st.id===id;});return s?esc(s.name):'';}).filter(Boolean).join(' · ');
}
function routineCard(r,i){
 const count=r.students.length;
 return '<article class="dm3-routine-card"><div class="dm3-routine-visual dm3-routine-visual-'+(i%4)+'"><span class="dm3-routine-no">'+String(i+1).padStart(2,'0')+'</span><span class="dm3-routine-style">'+esc(r.style)+'</span><div class="dm3-routine-art">'+icon(i%2?'trophy':'dance')+'</div></div>'+
 '<div class="dm3-routine-info"><div class="dm3-routine-type">'+esc(r.format)+' <span>· '+count+' performer'+(count===1?'':'s')+'</span></div><h3>'+esc(r.title)+'</h3><p>'+displayRoster(r.students)+'</p><div class="dm3-routine-bottom"><small>'+esc(r.result||'No results recorded')+'</small>'+actionButton('View team '+icon('arrow'),'routine-'+r.id,'dm3-routine-open')+'</div></div></article>';
}
function categoriesView(){
 ensureRoutines();
 const found=db.routines.filter(function(r){return (chosenFormat==='All'||r.format===chosenFormat)&&(chosenStyle==='All'||r.style===chosenStyle);});
 return head('Categories & routines','Example competition formats and dance styles. Each routine links to its featured performers.',button(icon('plus')+' Add demo routine','new-routine'))+
 '<div class="dm3-category-hero"><div><span>COMPETITION DIVISIONS</span><h2>Find every routine.<br>Celebrate every team.</h2><p>Browse a season by entry format and dance style, then open each routine to see who is performing.</p>'+button('View event planner '+icon('arrow'),'show-competitions','btn-light')+'</div><div class="dm3-category-medal">'+icon('trophy')+'</div></div>'+
 '<div class="dm3-filter-box"><h3>Entry format</h3><div class="dm3-chip-row">'+optionChips(['All'].concat(formats),chosenFormat,'dm3-format-')+'</div><h3>Dance style</h3><div class="dm3-chip-row">'+optionChips(['All'].concat(styles),chosenStyle,'dm3-style-')+'</div></div>'+
 '<div class="dm3-routine-title"><h2>Featured routines</h2><span>'+found.length+' of '+db.routines.length+' demo entries</span></div>'+
 (found.length?'<div class="dm3-routines">'+found.map(routineCard).join('')+'</div>':'<div class="empty">No routines match these filters. Choose another category or create a fictional routine.</div>')+
 '<div class="safe-notice dm3-category-note">'+icon('shield')+' These formats are editable examples, not a verified list of any organizer’s official rules. No real dancer information is used.</div>';
}
function sectionTabs(active){
 return '<nav class="dm3-module-tabs" aria-label="Dance features">'+
 actionButton(icon('medal')+' Dancer cards','show-dancers','dm3-module-tab'+(active==='dancers'?' active':''))+
 actionButton(icon('trophy')+' Competitions','show-competitions','dm3-module-tab'+(active==='competitions'?' active':''))+
 actionButton(icon('flag')+' Categories & routines','show-categories','dm3-module-tab'+(active==='categories'?' active':''))+
 '</nav>';
}
content=function(){
 if(role==='owner'&&route==='categories')return sectionTabs('categories')+categoriesView();
 if(role==='owner'&&route==='competitions')return priorContent().replace('<div class="dm-event-intro">',sectionTabs('competitions')+'<div class="dm-event-intro">');
 if(role==='owner'&&route==='dancers')return priorContent().replace('<div class="dm-spotlight-hero">',sectionTabs('dancers')+'<div class="dm-spotlight-hero">');
 return priorContent();
};
function newRoutineDialog(){
 ensureRoutines();
 modalForm('Add a fictional routine','<div class="safe-notice">Demo only. Use invented routine titles and the sample roster.</div>'+
 '<form id="dm3-routine-form">'+field('dm3-name','Routine title','e.g. Stardust Ensemble')+
 '<div class="form-grid"><div class="form-field"><label class="label" for="dm3-format">Entry format</label><select id="dm3-format" name="format">'+formats.map(function(f){return '<option>'+esc(f)+'</option>';}).join('')+'</select></div>'+
 '<div class="form-field"><label class="label" for="dm3-style">Dance style</label><select id="dm3-style" name="style">'+styles.map(function(f){return '<option>'+esc(f)+'</option>';}).join('')+'</select></div></div>'+
 '<div class="form-field"><span class="label">Select sample performers</span><div class="dm3-student-checks">'+db.students.map(function(st){return '<label><input type="checkbox" name="student" value="'+esc(st.id)+'"> '+esc(st.name)+'</label>';}).join('')+'</div></div>'+
 field('dm3-result','Example result (optional)','e.g. Gold · demo')+footer('Save demo routine')+'</form>','routine-new');
}
function routineDialog(id){
 const r=db.routines.find(function(q){return q.id===id;});if(!r)return;
 modalForm(esc(r.title)+' — featured team','<div class="dm3-modal-routine"><span class="pill blue">'+esc(r.format)+'</span> <span class="pill blue">'+esc(r.style)+'</span></div>'+
 '<h3 class="dm-modal-h3">Performers</h3><div class="dm3-dialog-students">'+(r.students.length?r.students.map(function(id){const st=db.students.find(function(s){return s.id===id;});return st?'<div class="dm3-dialog-person"><span class="student-avatar">'+esc(initials(st.name))+'</span><div><b>'+esc(st.name)+'</b><small>Fictional dancer profile</small></div>'+actionButton('View card','dancer-'+id,'btn btn-soft btn-small')+'</div>':'';}).join(''):'No performers assigned')+'</div>'+
 '<h3 class="dm-modal-h3">Recognition</h3><p>'+esc(r.result||'Not yet recorded')+'</p><div class="safe-notice">All information is simulated and saved only in this browser.</div><div class="modal-footer">'+button('Close','close-modal','btn-outline')+'</div>','routine-view');
}
doAction=function(action){
 if(action==='show-categories'){navigate('owner','categories');return;}
 if(action==='new-routine'){newRoutineDialog();return;}
 if(action.indexOf('dm3-format-')===0){chosenFormat=decodeURIComponent(action.slice(11));render();return;}
 if(action.indexOf('dm3-style-')===0){chosenStyle=decodeURIComponent(action.slice(10));render();return;}
 if(action.indexOf('routine-')===0){routineDialog(action.slice(8));return;}
 priorAction(action);
};
document.addEventListener('submit',function(e){
 if(e.target.id!=='dm3-routine-form')return;
 e.preventDefault();const fd=new FormData(e.target);
 const title=String(fd.get('dm3-name')||'').trim().slice(0,90);
 const format=String(fd.get('format')||''),style=String(fd.get('style')||'');
 const students=fd.getAll('student').filter(function(sid){return db.students.some(function(s){return s.id===sid;});});
 if(!title||!formats.includes(format)||!styles.includes(style)||!students.length){toast('Provide a title, category and at least one sample performer.');return;}
 db.routines.push({id:'dr'+Date.now(),title:title,format:format,style:style,students:students,result:String(fd.get('dm3-result')||'').trim().slice(0,100)});
 save();chosenFormat='All';chosenStyle='All';modal='';navigate('owner','categories');toast('Fictional routine saved locally.');
});
document.head.insertAdjacentHTML('beforeend','<link rel="stylesheet" href="./v3.css">');
render();
})();