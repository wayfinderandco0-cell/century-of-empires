/* Dance Manager Next V4: student progress scorecards.
   Fictional local demo only; no real child information, login or server storage. */
(function(){
'use strict';
ICONS.clipboard='<rect x="5" y="4" width="14" height="18" rx="2"/><rect x="9" y="2" width="6" height="4" rx="1"/><path d="m9 13 2 2 4-4M9 19h6"/>';
const skillKeys=['technique','musicality','performance','creativity'];
const engagementKeys=['participation','teamwork'];
const labels={technique:'Technique',musicality:'Musicality',performance:'Performance & expression',creativity:'Creativity',participation:'Participation & effort',teamwork:'Teamwork & preparedness'};
const hints={technique:'Control, alignment and learned steps',musicality:'Timing, rhythm and phrasing',performance:'Expression, confidence and presence',creativity:'Interpretation and improvisation',participation:'Active involvement and practice effort',teamwork:'Collaboration, preparation and class etiquette'};
const examples=[
 {id:'sc-demo-1',studentId:'s1',classId:'c1',teacher:'Olivia Hart',date:'2026-09-10',technique:3,musicality:4,performance:3,creativity:4,participation:4,teamwork:5,strength:'Strong musicality and focus during combinations.',goal:'Build consistency in turns.',notes:'Solid foundation. Continue practicing transitions.',shared:true},
 {id:'sc-demo-2',studentId:'s1',classId:'c1',teacher:'Olivia Hart',date:'2026-10-08',technique:4,musicality:4,performance:4,creativity:4,participation:5,teamwork:5,strength:'More confidence in centre work; excellent preparation.',goal:'Polish spotting and landing positions.',notes:'Noticeable progress since the previous check-in.',shared:true},
 {id:'sc-demo-3',studentId:'s2',classId:'c2',teacher:'Marcus Reed',date:'2026-10-06',technique:4,musicality:5,performance:4,creativity:5,participation:4,teamwork:4,strength:'Quick learner with excellent rhythm.',goal:'Keep precise placement through faster sequences.',notes:'Positive engagement in group exercises.',shared:false},
 {id:'sc-demo-4',studentId:'s3',classId:'c1',teacher:'Olivia Hart',date:'2026-10-07',technique:3,musicality:3,performance:4,creativity:4,participation:5,teamwork:5,strength:'Encouraging classmate and expressive mover.',goal:'Strengthen basic turns.',notes:'Consistently enthusiastic in lessons.',shared:false}
];
function ensureV4(){
 if(!Array.isArray(db.scorecards))db.scorecards=examples.map(function(a){return Object.assign({},a);});
 save();
}
ensureV4();
if(!NAV.owner.some(function(x){return x[0]==='scorecards';}))NAV.owner.splice(2,0,['scorecards','clipboard','Progress scorecards']);
if(!NAV.instructor.some(function(x){return x[0]==='scorecards';}))NAV.instructor.push(['scorecards','clipboard','Student progress']);
if(!NAV.parent.some(function(x){return x[0]==='progress';}))NAV.parent.splice(2,0,['progress','clipboard','Dancer progress']);
MOBILE.owner=['overview','dancers','competitions','scorecards'];
MOBILE.instructor=['today','roll','roster','scorecards'];
MOBILE.parent=['family','schedule','progress','payments'];
let selectedClass='all',selectedStudent='',displayPeriod='all';
const priorContent=content,priorDo=doAction;
function instructorClasses(){return db.classes.filter(function(c){return c.instructor==='Olivia Hart';});}
function visibleClasses(){return role==='instructor'?instructorClasses():db.classes;}
function visibleStudents(){
 const cs=visibleClasses().filter(function(c){return selectedClass==='all'||c.id===selectedClass;});
 const ids=new Set(cs.flatMap(function(c){return c.enrolled||[];}));
 if(role==='owner'&&selectedClass==='all')return db.students;
 return db.students.filter(function(s){return ids.has(s.id);});
}
function entries(sid,cid){
 return (db.scorecards||[]).filter(function(a){return a.studentId===sid&&(!cid||cid==='all'||a.classId===cid);}).sort(function(a,b){return b.date.localeCompare(a.date)||String(b.id).localeCompare(String(a.id));});
}
function avg(record,keys){return keys.reduce(function(n,k){return n+Number(record[k]||0);},0)/keys.length;}
function fixed(n){return Number(n).toFixed(1);}
function whole(record){return avg(record,skillKeys.concat(engagementKeys));}
function scoreColor(n){return n>=4.25?'high':n>=3?'mid':'build';}
function scoreTag(n){return '<span class="sc4-score sc4-'+scoreColor(n)+'">'+fixed(n)+' <small>/ 5</small></span>';}
function safeDate(s){const d=new Date(s+'T12:00:00');return Number.isNaN(+d)?esc(s):d.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});}
function classLabel(id){return db.classes.find(function(c){return c.id===id;})?.name||'Class unavailable';}
function studentCard(st){
 const latest=entries(st.id,selectedClass)[0];
 return '<button class="sc4-student '+(selectedStudent===st.id?'active':'')+'" type="button" data-action="sc4-view:'+esc(st.id)+'"><span class="sc4-avatar">'+esc(initials(st.name))+'</span><span class="sc4-person"><b>'+esc(st.name)+'</b><small>'+esc(st.level||'Dancer')+' · '+(latest?'Updated '+safeDate(latest.date):'Awaiting first assessment')+'</small></span>'+(latest?scoreTag(whole(latest)):'<span class="sc4-unrated">Not rated</span>')+icon('chevron')+'</button>';
}
function meter(k,v){return '<div class="sc4-rubric-row"><div class="sc4-rubric-line"><b>'+esc(labels[k])+'</b><span>'+v+' / 5</span></div><div class="sc4-track"><span style="width:'+(v*20)+'%"></span></div></div>';}
function assessmentDetail(sid){
 const student=db.students.find(function(x){return x.id===sid;});if(!student)return '<div class="sc4-empty">Select a dancer.</div>';
 const history=entries(sid,selectedClass),latest=history[0],prior=history[1];
 const eligible=visibleClasses().filter(function(c){return c.enrolled.includes(sid)&&(selectedClass==='all'||selectedClass===c.id);});
 let out='<div class="sc4-detail-header"><div><span class="sc4-eyebrow">PRIVATE STUDENT RECORD</span><h2>'+esc(student.name)+'</h2><p>'+esc(student.level||'Student')+' · '+eligible.map(function(c){return esc(c.name);}).join(' · ')+'</p></div><div class="sc4-buttons">'+(eligible.length?button(icon('plus')+' Add assessment','sc4-evaluate:'+sid+':'+eligible[0].id,'btn-primary btn-small'):'')+'</div></div>';
 if(!latest)return out+'<div class="sc4-empty sc4-detail-empty">'+icon('clipboard')+'<h3>No assessments yet</h3><p>Give this student their first private evaluation using a class they attend.</p></div>';
 const delta=prior?(whole(latest)-whole(prior)):null;
 out+='<div class="sc4-feature-stats"><div><span>Overall score</span><strong>'+fixed(whole(latest))+'<small> / 5</small></strong><em>'+ (delta===null?'First assessment':(delta>0?'↑ +':'')+fixed(delta)+' since previous')+'</em></div><div><span>Dance abilities</span><strong>'+fixed(avg(latest,skillKeys))+'<small> / 5</small></strong><em>Four skill measures</em></div><div><span>Participation</span><strong>'+fixed(avg(latest,engagementKeys))+'<small> / 5</small></strong><em>Effort + teamwork</em></div></div>';
 out+='<div class="sc4-detail-grid"><section class="sc4-detail-panel"><div class="sc4-panel-heading"><h3>Skills & talent</h3><span class="sc4-chip">1–5 scale</span></div>'+skillKeys.map(function(k){return meter(k,latest[k]);}).join('')+'</section><section class="sc4-detail-panel"><div class="sc4-panel-heading"><h3>Class participation</h3><span class="sc4-chip">Separate from ability</span></div>'+engagementKeys.map(function(k){return meter(k,latest[k]);}).join('')+'<div class="sc4-note"><b>Teacher feedback</b><p>'+esc(latest.notes||'No additional notes.')+'</p></div></section></div>';
 out+='<div class="sc4-feedback-grid"><div class="sc4-feedback"><span>★</span><div><b>Strengths</b><p>'+esc(latest.strength||'Not recorded.')+'</p></div></div><div class="sc4-feedback"><span>↗</span><div><b>Next learning goal</b><p>'+esc(latest.goal||'Not recorded.')+'</p></div></div></div>';
 out+='<section class="sc4-detail-panel sc4-history"><div class="sc4-panel-heading"><h3>Assessment history</h3><span class="sc4-chip">'+history.length+' review'+(history.length===1?'':'s')+'</span></div><div class="sc4-history-list">'+history.map(function(a){
 const canShare=role==='owner',s=whole(a);
 return '<div class="sc4-history-row"><div class="sc4-history-dot"></div><div class="sc4-history-copy"><b>'+safeDate(a.date)+' · '+esc(classLabel(a.classId))+'</b><small>Evaluated by '+esc(a.teacher||'Instructor')+'</small></div>'+scoreTag(s)+'<div class="sc4-sharing"><span class="sc4-sharing-status '+(a.shared?'shared':'')+'">'+(a.shared?'Shared with family':'Staff only')+'</span>'+(canShare?'<button type="button" class="sc4-link" data-action="sc4-share:'+esc(a.id)+'">'+(a.shared?'Make private':'Share with parent')+'</button>':'')+'</div></div>';
 }).join('')+'</div></section>';
 out+='<p class="sc4-disclaimer">Ratings are teacher observations, not medical, psychological or competitive rankings. Scores are for personal development, not comparison with other children. This demo stores fictional data on this device only.</p>';
 return out;
}
function scorecardPage(){
 const classes=visibleClasses();if(!classes.length)return head('Student progress','No classes are assigned in this example.');
 if(selectedClass!=='all'&&!classes.some(function(c){return c.id===selectedClass;}))selectedClass='all';
 const roster=visibleStudents();
 if(!roster.some(function(x){return x.id===selectedStudent;}))selectedStudent=roster[0]?.id||'';
 const n=roster.filter(function(s){return entries(s.id,selectedClass).length;}).length;
 const cn='<label class="sc4-filter-label">Class <select id="sc4-class"><option value="all">All '+(role==='instructor'?'my classes':'studio classes')+'</option>'+classes.map(function(c){return '<option value="'+esc(c.id)+'" '+(selectedClass===c.id?'selected':'')+'>'+esc(c.name)+' · '+esc(c.instructor)+'</option>';}).join('')+'</select></label>';
 return head('Student progress scorecards',role==='instructor'?'Evaluate dancers in your assigned classes.':'Track individual talent, skills, class effort and growth over time.',button(icon('plus')+' New assessment','sc4-new','btn-primary'))+
 '<div class="sc4-intro"><div class="sc4-intro-mark">'+icon('clipboard')+'</div><div><h3>Every dancer. Every milestone.</h3><p>Designed for owner-led studios and multi-instructor teams. Teachers assess; owners review and decide which evaluations are shared with families.</p></div><span class="sc4-chip">Private demo</span></div>'+
 '<div class="sc4-overview"><div><strong>'+roster.length+'</strong><span>Student records</span></div><div><strong>'+n+'</strong><span>Evaluated</span></div><div><strong>'+roster.filter(function(s){return !entries(s.id,selectedClass).length;}).length+'</strong><span>Awaiting review</span></div></div>'+
 '<div class="sc4-layout"><aside class="sc4-roster"><div class="sc4-roster-head"><h2>Student list</h2><span>'+roster.length+'</span></div>'+cn+'<div class="sc4-students">'+(roster.length?roster.map(studentCard).join(''):'<div class="sc4-empty">No students enrolled in this class.</div>')+'</div></aside><div class="sc4-main">'+(selectedStudent?assessmentDetail(selectedStudent):'<div class="sc4-empty">Choose a class with students.</div>')+'</div></div>';
}
function familyProgress(){
 const s=db.students.find(function(x){return x.id==='s1';});
 if(!s)return head('Dancer progress','No sample student attached.');
 const history=entries(s.id,'all').filter(function(a){return a.shared;});
 const latest=history[0];
 return head('My dancer’s progress','Only evaluations explicitly shared with the family are visible in this preview.')+
 '<div class="sc4-family-head"><span class="sc4-avatar">'+esc(initials(s.name))+'</span><div><span class="sc4-eyebrow">YOUR DANCER</span><h2>'+esc(s.name)+'</h2><p>Celebrating development, effort and learning goals.</p></div></div>'+
 (latest?'<div class="sc4-family-panel"><div class="sc4-family-highlight"><div><span>Latest shared assessment · '+safeDate(latest.date)+'</span><strong>'+fixed(whole(latest))+' <small>/ 5</small></strong></div><span class="sc4-chip">'+esc(classLabel(latest.classId))+'</span></div><div class="sc4-detail-grid"><section class="sc4-detail-panel"><h3>Dance skills</h3>'+skillKeys.map(function(k){return meter(k,latest[k]);}).join('')+'</section><section class="sc4-detail-panel"><h3>Participation</h3>'+engagementKeys.map(function(k){return meter(k,latest[k]);}).join('')+'</section></div><div class="sc4-feedback-grid"><div class="sc4-feedback"><span>★</span><div><b>What’s going well</b><p>'+esc(latest.strength||'Keep practicing!')+'</p></div></div><div class="sc4-feedback"><span>↗</span><div><b>What to work on</b><p>'+esc(latest.goal||'Your instructor will set a goal soon.')+'</p></div></div></div><div class="sc4-family-quote"><b>Teacher note</b><p>'+esc(latest.notes||'No written note.')+'</p><small>— '+esc(latest.teacher)+'</small></div></div>':'<div class="sc4-empty sc4-detail-empty"><h3>Nothing shared yet</h3><p>Your instructor will share progress here when an evaluation is ready.</p></div>')+
 '<p class="sc4-disclaimer">Sample family: fictional first student only. This is a role-switching prototype, not a secure parent login. No real minor’s records should be entered here.</p>';
}
content=function(){
 if((role==='owner'||role==='instructor')&&route==='scorecards')return scorecardPage();
 if(role==='parent'&&route==='progress')return familyProgress();
 return priorContent();
};
function selectBlock(name,values,chosen){return '<select name="'+name+'" id="sc4-'+name+'" required>'+values.map(function(v){return '<option value="'+v+'" '+(String(v)===String(chosen)?'selected':'')+'>'+v+' — '+(['','Beginning','Developing','Consistent','Strong','Excellent'][v]||'')+'</option>';}).join('')+'</select>';}
function evaluationDialog(sid,cid){
 const classes=visibleClasses().filter(function(c){return c.enrolled.includes(sid);});
 const students=role==='instructor'?db.students.filter(function(s){return classes.length?visibleClasses().some(function(c){return c.enrolled.includes(s.id);}):false;}):db.students;
 const st=db.students.find(function(s){return s.id===sid;})||students[0];
 if(!st){toast('No available students.');return;}
 const possible=visibleClasses().filter(function(c){return c.enrolled.includes(st.id);});
 if(!possible.length){toast('Enroll this student in a class before grading.');return;}
 const selected=possible.find(function(c){return c.id===cid;})||possible[0];
 const last=entries(st.id,selected.id)[0];
 let fields='<div class="sc4-form-grid">'+skillKeys.concat(engagementKeys).map(function(k){
 return '<div class="sc4-rating-field"><label for="sc4-'+k+'"><b>'+esc(labels[k])+'</b><small>'+esc(hints[k])+'</small></label>'+selectBlock(k,[1,2,3,4,5],last?last[k]:3)+'</div>';
 }).join('')+'</div>';
 const body='<div class="safe-notice">Fictional data only. A live system must use secure staff permissions and private student storage.</div>'+
 '<form id="sc4-form"><input type="hidden" name="studentId" value="'+esc(st.id)+'">'+
 '<div class="sc4-form-overview"><strong>'+esc(st.name)+'</strong><span>Record a development snapshot</span></div>'+
 '<div class="form-grid"><div class="form-field"><label class="label" for="sc4-classId">Class</label><select name="classId" id="sc4-classId">'+possible.map(function(c){return '<option value="'+esc(c.id)+'" '+(c.id===selected.id?'selected':'')+'>'+esc(c.name)+' · '+esc(c.instructor)+'</option>';}).join('')+'</select></div>'+
 '<div class="form-field"><label class="label" for="sc4-date">Review date</label><input type="date" id="sc4-date" name="date" required value="2026-10-19"></div></div>'+
 '<div class="sc4-form-section"><h3>Rate ability & engagement</h3><p>1 = beginning · 2 = developing · 3 = consistent · 4 = strong · 5 = excellent. Choose based on age-appropriate goals.</p>'+fields+'</div>'+
 '<div class="form-grid"><div class="form-field"><label class="label" for="sc4-strength">Student strengths</label><textarea name="strength" id="sc4-strength" rows="3" maxlength="320" required placeholder="What does this dancer do well?"></textarea></div><div class="form-field"><label class="label" for="sc4-goal">Next learning goal</label><textarea name="goal" id="sc4-goal" rows="3" maxlength="320" required placeholder="One practical area to develop"></textarea></div></div>'+
 '<div class="form-field"><label class="label" for="sc4-notes">Instructor feedback (optional)</label><textarea name="notes" id="sc4-notes" rows="3" maxlength="500" placeholder="Specific, supportive observations"></textarea></div>'+
 (role==='owner'?'<div class="sc4-share-choice"><label><input type="checkbox" name="shared" value="yes"> Share this assessment with the parent demo</label><small>Off by default. Only the studio owner shares records with families.</small></div><div class="sc4-share-choice"><label><input type="checkbox" name="ownerTeaching" value="yes"> I am the studio owner teaching this class</label><small>Otherwise the assessment credits the class instructor.</small></div>':'<p class="sc4-disclaimer">Instructor entries remain staff-only until the studio owner approves family sharing.</p>')+
 footer('Save assessment')+'</form>';
 modalForm('New student assessment',body,'scorecard');
}
function newAssessment(){
 const c=visibleClasses().find(function(x){return x.enrolled.length;});
 if(!c){toast('Create a class with enrolled students first.');return;}
 const s=c.enrolled[0];evaluationDialog(selectedStudent&&visibleClasses().some(function(x){return x.enrolled.includes(selectedStudent);})?selectedStudent:s,c.id);
}
doAction=function(action){
 if(action==='sc4-new'){newAssessment();return;}
 if(action.indexOf('sc4-view:')===0){selectedStudent=action.slice(9);render();return;}
 if(action.indexOf('sc4-evaluate:')===0){const parts=action.slice(13).split(':');evaluationDialog(parts[0],parts[1]);return;}
 if(action.indexOf('sc4-share:')===0){
  if(role!=='owner')return;
  const a=db.scorecards.find(function(x){return x.id===action.slice(10);});
  if(a){a.shared=!a.shared;save();render();toast(a.shared?'Assessment shared in fictional parent view.':'Assessment marked staff-only.');}return;
 }
 if(action==='reset'){priorDo(action);if(!Array.isArray(db.scorecards)){ensureV4();render();}return;}
 priorDo(action);
};
document.addEventListener('change',function(e){
 if(e.target.id==='sc4-class'){selectedClass=e.target.value;selectedStudent='';render();}
});
document.addEventListener('submit',function(e){
 if(e.target.id!=='sc4-form')return;
 e.preventDefault();const d=new FormData(e.target);
 const sid=String(d.get('studentId')||''),cid=String(d.get('classId')||'');
 const c=visibleClasses().find(function(x){return x.id===cid&&x.enrolled.includes(sid);});
 if(!c){toast('This student is not enrolled in an available class.');return;}
 const date=String(d.get('date')||''),parsed=new Date(date+'T12:00:00');
 if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||Number.isNaN(+parsed)||parsed.toISOString().slice(0,10)!==date){toast('Choose a valid review date.');return;}
 const a={id:'sc'+Date.now()+'-'+Math.floor(Math.random()*10000),studentId:sid,classId:cid,date:date,teacher:role==='owner'&&d.has('ownerTeaching')?'Studio Owner':c.instructor,shared:role==='owner'&&d.has('shared'),strength:String(d.get('strength')||'').trim().slice(0,320),goal:String(d.get('goal')||'').trim().slice(0,320),notes:String(d.get('notes')||'').trim().slice(0,500)};
 if(!a.strength||!a.goal){toast('Enter a strength and a next learning goal.');return;}
 for(const k of skillKeys.concat(engagementKeys)){const n=Number(d.get(k));if(!Number.isInteger(n)||n<1||n>5){toast('Enter all six scores from 1 to 5.');return;}a[k]=n;}
 db.scorecards.push(a);save();selectedStudent=sid;selectedClass=cid;modal='';render();toast('Fictional assessment saved to this device.');
});
document.head.insertAdjacentHTML('beforeend','<link rel="stylesheet" href="./v4.css">');
render();
})();