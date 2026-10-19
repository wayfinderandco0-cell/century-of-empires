/* Dance Manager Next V3 - visual redesign and fictional category browser. */
(function(){
'use strict';
const src={
  hero:'https://images.unsplash.com/photo-1769694513443-c7292e174d48?auto=format&fit=crop&w=1800&q=85',
  studio:'https://images.unsplash.com/photo-1558905566-ddbeb2fc2c2f?auto=format&fit=crop&w=900&q=83',
  dancer:'https://images.unsplash.com/photo-1771528471837-573223e7a6b0?auto=format&fit=crop&w=900&q=83',
  stage:'https://images.unsplash.com/photo-1741846895501-4c79409bc570?auto=format&fit=crop&w=1100&q=83',
  parent:'https://images.unsplash.com/photo-1752652012592-8f618322a63c?auto=format&fit=crop&w=900&q=83',
  ballerina:'https://images.unsplash.com/photo-1760543320214-9a578e5c5b73?auto=format&fit=crop&w=900&q=83',
  purple:'https://images.unsplash.com/photo-1769694513443-c7292e174d48?auto=format&fit=crop&w=800&q=80'
};
const n3Brand='<span class="n3-brand">DANCE MANAGER <em>Next</em><small>STUDIOS · DANCERS · COMPETITIONS · ALL TOGETHER</small></span>';
function btn(text,action,cls){return '<button type="button" class="'+(cls||'n3-button')+'" data-action="'+action+'">'+text+'</button>';}
function navItems(){return [
  '<a href="#top" data-n3-scroll>Home</a>',
  btn('Studio','owner','n3-nav-btn'),
  btn('Dancers','show-dancers','n3-nav-btn'),
  btn('Competitions','show-competitions','n3-nav-btn'),
  btn('Parents','parent','n3-nav-btn'),
  '<a href="#resources" data-n3-scroll>Resources</a>',
  '<a href="#pricing" data-n3-scroll>Pricing</a>'
].join('');}
function tile(title,desc,tag,img,action){
 return '<article class="n3-tile"><img alt="" loading="lazy" src="'+img+'"><div class="n3-tile-shade"></div><div class="n3-tile-info"><span class="n3-tile-tag">'+tag+'</span><h3>'+title+'</h3><p>'+desc+'</p>'+btn('Explore '+title+' →',action,'n3-outline')+'</div></article>';
}
marketing=function(){
 return '<div class="n3-site" id="top">'+
 '<header class="n3-header"><div class="n3-bar"><a href="#top" class="n3-logo">'+n3Brand+'</a><nav class="n3-desktop" aria-label="Main navigation">'+navItems()+'</nav>'+
 '<div class="n3-top-actions">'+btn('Sign in','owner','n3-signin')+btn('Get started →','owner','n3-button n3-sm')+
 '<button type="button" aria-label="Open navigation" aria-expanded="'+(mobileMenu?'true':'false')+'" class="n3-menu-btn" data-action="toggle-menu">'+icon('menu')+'</button></div></div>'+
 (mobileMenu?'<nav class="n3-mobile" aria-label="Mobile navigation">'+navItems()+'</nav>':'')+
 '</header>'+
 '<main>'+
 '<section class="n3-hero"><div class="n3-hero-visual"><img class="n3-hero-photo" src="'+src.hero+'" alt="Dance performer under theatrical purple stage lighting"></div><div class="n3-hero-glow"></div>'+
 '<div class="n3-hero-copy"><p class="n3-eyebrow">A BETTER STAGE FOR YOUR STUDIO</p><h1>More Than<br>A <em>Dance</em><br>Website.</h1>'+
 '<p class="n3-subtitle">The complete studio management platform for dancers, teachers, competition directors and families.</p>'+
 '<div class="n3-highlights"><span>'+icon('calendar')+' Manage</span><span>'+icon('users')+' Connect</span><span>'+icon('trophy')+' Celebrate</span></div>'+
 '<div class="n3-hero-actions">'+btn('See the platform →','owner','n3-button')+btn('Explore competitions ↗','show-competitions','n3-ghost')+'</div>'+
 '<p class="n3-demo-detail">Independent V3 preview · All records are fictional</p></div></section>'+
 '<div class="n3-benefits"><span>'+icon('grid')+' All-in-one management</span><span>'+icon('phone')+' Mobile-friendly experience</span><span>'+icon('trophy')+' Competition ready</span><span>'+icon('chart')+' Built for studio growth</span></div>'+
 '<section id="features" class="n3-feature-section"><div class="n3-section-header"><div><p class="n3-kicker">ONE BEAUTIFUL PLATFORM</p><h2>Everything your dance world needs.</h2></div><p>Studio essentials and the excitement of competition, seamlessly connected.</p></div>'+
 '<div class="n3-tiles">'+
 tile('Studio Management','Organize classes, dancers, staff, schedules and communication in one place.','RUN YOUR STUDIO',src.studio,'owner')+
 tile('Dancer Profiles','Showcase dancer cards with bios, specialties, results and achievements.','MEET THE TALENT',src.dancer,'show-dancers')+
 tile('Competitions','Manage routines, entry categories, schedules and placements.','OWN THE STAGE',src.stage,'show-competitions')+
 tile('Parent Portal','Help families stay connected with schedules, invoices and updates.','STAY CONNECTED',src.parent,'parent')+
 '</div></section>'+
 '<section class="n3-preview-section" id="resources"><div class="n3-preview-copy"><p class="n3-kicker">THE POWER BEHIND THE PERFORMANCE</p><h2>Beautiful on the outside.<br><em>Practical every day.</em></h2><p>Jump into the interactive owner workspace: class rosters, attendance, simulated tuition, studio communications and reporting.</p><div class="n3-pill-row"><span>Class scheduling</span><span>Attendance</span><span>Billing preview</span><span>Instructor tools</span></div>'+btn('Open studio dashboard →','owner','n3-button')+'</div><div class="n3-preview-panel"><div class="n3-preview-panel-top"><b>Studio overview</b><span>LIVE DEMO VIEW</span></div><div class="n3-preview-metrics"><div><small>Student records</small><strong>128</strong></div><div><small>Weekly classes</small><strong>24</strong></div><div><small>Sample revenue</small><strong>$8.4k</strong></div></div><div class="n3-preview-bars"><i style="height:34%"></i><i style="height:57%"></i><i style="height:49%"></i><i style="height:72%"></i><i style="height:69%"></i><i style="height:84%"></i><i style="height:93%"></i></div><p>Illustrative dashboard figures · Not real studio records</p></div></section>'+
 '<section class="n3-spotlight-banner"><img src="'+src.ballerina+'" alt="" loading="lazy"><div><p class="n3-kicker">EVERY DANCER HAS A STORY</p><h2>Give every performance<br>the recognition it deserves.</h2><p>A profile card for specialties, routines, competition entries and memorable achievements.</p>'+btn('View dancer cards →','show-dancers','n3-button')+'</div></section>'+
 '<section id="pricing" class="n3-final-cta"><p class="n3-kicker">DISCOVER THE POSSIBILITIES</p><h2>Give your studio room to shine.</h2><p>Explore the working demonstration. Official pricing and production availability have not been announced.</p>'+btn('Try the studio demo →','owner','n3-button')+'</section>'+
 '</main><footer class="n3-footer"><div>'+n3Brand+'<p>Independent design prototype — not the existing Dance Manager service.</p></div><small>Fictional examples only · No actual student profiles or payments · Concept photography from Unsplash</small></footer></div>';
};
const beforeContent=content;
let chosenFormat='Solo',chosenStyle='All styles';
const formats=[['Solo','Solo'],['Duo / Trio','Duo/Trio'],['Small Group','Small Group'],['Large Group','Large Group'],['Production','Production'],['Team','Team']];
const styles=['All styles','Ballet','Jazz','Contemporary','Lyrical','Hip-Hop','Tap'];
const routines=[
 {title:'Reflections',format:'Solo',style:'Lyrical',who:'Avery Johnson',tag:'1st Place',photo:src.dancer},
 {title:'Unstoppable',format:'Solo',style:'Contemporary',who:'Chloe Mitchell',tag:'Judges’ Choice',photo:src.hero},
 {title:'Rise',format:'Solo',style:'Jazz',who:'Ethan Carter',tag:'National Finalist',photo:src.purple},
 {title:'Stronger Together',format:'Large Group',style:'Contemporary',who:'Elevate Dance Company',tag:'Choreography Award',photo:src.stage},
 {title:'Midnight Rhythm',format:'Duo / Trio',style:'Jazz',who:'The Studio Duo',tag:'Top 10',photo:src.ballerina},
 {title:'Beyond the Lights',format:'Small Group',style:'Ballet',who:'The En Pointe Ensemble',tag:'Gold',photo:src.studio},
 {title:'Encore',format:'Production',style:'Tap',who:'Studio Collective',tag:'Special Award',photo:src.stage},
 {title:'Electric Motion',format:'Team',style:'Hip-Hop',who:'Urban Motion Crew',tag:'Finalist',photo:src.stage}
];
function filterControls(){
 return '<section class="n3-categories"><div class="n3-category-banner"><div><span>EXPLORE THE COMPETITION FLOOR</span><h2>Competition categories</h2><p>Find routines and dancer groups by entry type and dance style. Each item is a fictional demonstration.</p></div><img src="'+src.hero+'" loading="lazy" alt="Stage performer in dramatic pose"></div>'+
 '<div class="n3-filter-label">ENTRY FORMAT</div><div class="n3-format-row">'+formats.map(function(f){return '<button type="button" data-action="n3-format-'+f[0]+'" class="n3-format-btn '+(chosenFormat===f[0]?'active':'')+'">'+f[1]+'</button>';}).join('')+'</div>'+
 '<div class="n3-style-row"><span>Dance style:</span>'+styles.map(function(s){return '<button type="button" class="n3-style-btn '+(chosenStyle===s?'active':'')+'" data-action="n3-style-'+s+'">'+s+'</button>';}).join('')+'</div>'+
 '<div class="n3-routines-head"><h3>'+chosenFormat+' spotlight</h3><span>Illustrative examples</span></div>'+
 '<div class="n3-routines">'+routines.filter(function(r){return r.format===chosenFormat&&(chosenStyle==='All styles'||chosenStyle===r.style);}).map(function(r){return '<article class="n3-routine"><div class="n3-routine-img"><img src="'+r.photo+'" alt="Illustrative stage photography" loading="lazy"><span>★ '+r.tag+'</span></div><div class="n3-routine-info"><small>'+r.style+' · '+r.format+'</small><h4>'+r.title+'</h4><p>'+r.who+'</p><span>Sample routine · Demo only</span></div></article>';}).join('')+
 (routines.some(function(r){return r.format===chosenFormat&&(chosenStyle==='All styles'||chosenStyle===r.style);})?'':'<div class="n3-no-results">No sample routine in this combination. Choose another dance style.</div>')+'</div></section>';
}
content=function(){
 const result=beforeContent();
 if(role==='owner'&&route==='competitions') return result.replace('<div class="dm-simple-stats">',filterControls()+'<div class="dm-simple-stats">');
 return result;
};
const prevAction=doAction;
doAction=function(a){
 if(a.indexOf('n3-format-')===0){chosenFormat=a.slice(10);chosenStyle='All styles';render();return;}
 if(a.indexOf('n3-style-')===0){chosenStyle=a.slice(9);render();return;}
 prevAction(a);
};
demoBanner=function(){return '<div class="demo-banner">DEMO PREVIEW · Fictional data · Original site unchanged</div>';};
document.head.insertAdjacentHTML('beforeend','<link rel="stylesheet" href="./v3.css?v=31">');
render();
})();