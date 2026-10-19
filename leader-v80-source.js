/* Century of Empires V80: historical generals and travel, embedded in the main game's closure. */
const LEADER_DEFS=[
 ['frederick','Frederick II','PR','berlin',1780,1786,.035,.15,'Military discipline'],
 ['blucher','Gebhard von Blücher','PR','berlin',1794,1815,.026,.17,'Aggressive campaigning'],
 ['rochambeau','Jean-Baptiste de Rochambeau','FR','paris',1780,1791,.025,.13,'Expeditionary experience'],
 ['napoleon','Napoleon Bonaparte','FR','paris',1796,1821,.04,.20,'Operational maneuver'],
 ['laudon','Ernst Gideon von Laudon','AT','vienna',1780,1790,.027,.16,'Battlefield planning'],
 ['archduke','Archduke Charles','AT','vienna',1796,1847,.032,.16,'Defensive tactics'],
 ['cornwallis','Charles Cornwallis','GB','london',1780,1805,.025,.13,'Imperial army leadership'],
 ['suvorov','Alexander Suvorov','RU','moscow',1780,1800,.034,.18,'Offensive command'],
 ['kutuzov','Mikhail Kutuzov','RU','moscow',1805,1813,.031,.17,'Defensive campaigning'],
 ['galvez','Bernardo de Gálvez','ES','madrid',1780,1786,.024,.13,'Logistics and maneuver'],
 ['gustav','Gustav III','SW','stockholm',1780,1792,.026,.11,'Royal command'],
 ['frederik','Crown Prince Frederik','DN','copenhagen',1784,1839,.025,.11,'Military reforms'],
 ['selim','Selim III','OT','constantinople',1789,1807,.03,.10,'Reform leadership'],
 ['beresford','William Beresford','PT','lisbon',1809,1820,.025,.15,'Army organization']
].map(([id,name,owner,town,start,end,nation,command,trait])=>({id,name,owner,town,start,end,nation,command,trait}));
const HISTORICAL_EVENTS=[
 {date:1789*12+6,title:'The Storming of the Bastille — 1789',text:'In recorded history, the Bastille was stormed in Paris. Your alternate campaign need not follow the same course.'},
 {date:1792*12+8,title:'The French Republic — 1792',text:'Historically, France abolished its monarchy and proclaimed a republic. This dispatch does not override player government or diplomacy.'},
 {date:1804*12+11,title:'Napoleon Crowned Emperor — 1804',text:'Napoleon was crowned emperor in real history. Political changes in your campaign remain independent.'},
 {date:1815*12+5,title:'Congress of Vienna — 1815',text:'In history, the major powers negotiated a European settlement in Vienna. No peace is forced in this simulation.'},
 {date:1848*12+1,title:'Revolutions of 1848',text:'Historically, uprisings swept across Europe. The outcome of this alternate campaign remains open.'}
];
let selectedLeader=null;
const commanderDef=l=>LEADER_DEFS.find(d=>d.id===(typeof l==='string'?l:l?.id));
const leaderList=k=>(game?.leaders||[]).filter(l=>l.active&&l.owner===k);
const leaderForArmy=a=>a?(game?.leaders||[]).find(l=>l.active&&l.assignedArmy===a.id&&l.owner===a.owner):null;
const nationalCommandBonus=k=>Math.min(.065,leaderList(k).reduce((v,l)=>v+(commanderDef(l)?.nation||0),0));
const commandBonus=a=>{const l=leaderForArmy(a);return l?commanderDef(l).command:0};
const leaderLocation=l=>l.assignedArmy?(game.armies.find(a=>a.id===l.assignedArmy)?.at||l.at):l.at;
function leaderPoint(l){
 if(l.assignedArmy){const a=game.armies.find(a=>a.id===l.assignedArmy);if(a)return positionOf(a)}
 if(l.route?.length&&l.edgeTotal>0){
  const a=byId[l.at],b=byId[l.route[0]];
  if(a&&b){const t=Math.max(0,Math.min(1,(l.edgeTotal-l.edgeRemaining+Math.max(0,pct()-(l.edgePhase||0)))/l.edgeTotal));
   return {x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t}}
 }
 return byId[l.at]||{x:0,y:0};
}
function syncLeaders(){
 game.leaders=Array.isArray(game.leaders)?game.leaders:[];
 game.historicalSeen=game.historicalSeen||{};
 for(const d of LEADER_DEFS){
  let l=game.leaders.find(x=>x.id===d.id);
  if(game.year<d.start||game.year>d.end){
   if(l&&l.active){l.active=false;l.assignedArmy=null;l.route=[];line(d.name+' retires from active command.','leader','Commander retires: '+d.name)}
   continue;
  }
  if(!l){
   const town=owner(d.town)===d.owner?d.town:game.provinces.find(p=>p.owner===d.owner)?.id;
   if(!town)continue;
   l={id:d.id,owner:d.owner,at:town,active:true,assignedArmy:null,route:[],edgeTotal:0,edgeRemaining:0,edgePhase:0};
   game.leaders.push(l);
   line(d.name+' is now in service at '+byId[town].name+'.','leader','Commander arrives: '+d.name);
  }
 }
 reconcileLeaders();
}
function reconcileLeaders(){
 for(const l of game.leaders||[]){
  if(!l.active||!l.assignedArmy)continue;
  const army=game.armies.find(a=>a.id===l.assignedArmy&&a.owner===l.owner&&activeArmy(a));
  if(army){l.at=army.at;continue}
  l.assignedArmy=null;l.route=[];l.edgeTotal=0;l.edgeRemaining=0;l.edgePhase=0;
  const home=owner(l.at)===l.owner?l.at:game.provinces.find(p=>p.owner===l.owner)?.id;
  if(!home){l.active=false;continue}
  l.at=home;line(commanderDef(l).name+' returns to '+byId[home].name+' after his army is lost.','leader','Commander returns');
 }
}
function historicDispatches(){
 game.historicalSeen=game.historicalSeen||{};
 const now=game.year*12+game.month;
 for(const e of HISTORICAL_EVENTS)if(e.date===now&&!game.historicalSeen[e.title]){
  game.historicalSeen[e.title]=true;line(e.text,'history',e.title);
 }
}
function attachCommander(id,armyId){
 const l=leaderList(game.player).find(x=>x.id===id),a=mobileArmy(armyId);
 if(!l||!a||a.owner!==l.owner||l.assignedArmy||l.route.length||a.route.length||a.camp||a.battle||l.at!==a.at||leaderForArmy(a)||owner(l.at)!==l.owner){
  toast('Commander and available stationary army must be in the same friendly province');return false}
 l.assignedArmy=a.id;l.at=a.at;
 line(commanderDef(l).name+' takes command of '+total(a)+' troops in '+byId[a.at].name+'.','leader','Commander assigned');
 renderAll();save();toast('Commander attached');return true;
}
function detachCommander(id){
 const l=leaderList(game.player).find(x=>x.id===id);if(!l?.assignedArmy)return false;
 const a=mobileArmy(l.assignedArmy);
 if(!a||a.route.length||a.battle||a.camp||owner(a.at)!==a.owner){toast('Detach at a safe friendly town after travel or battle');return false}
 l.at=a.at;l.assignedArmy=null;line(commanderDef(l).name+' leaves his army at '+byId[a.at].name+'.','leader','Commander detached');
 renderAll();save();return true;
}
function leaderLegDuration(l,next){
 const a=TRAVEL_CITY_COORDS[l.at]||byId[l.at],b=TRAVEL_CITY_COORDS[next]||byId[next];if(!a||!b)return 2;
 const sea=SEA_LANES.has([l.at,next].sort().join(':'));
 return Math.max(1.05,Math.ceil(Math.hypot(a.x-b.x,a.y-b.y)/95*weatherAt(next).speed*2)/2+(sea?1:0));
}
function startLeaderLeg(l,phase=0){
 if(!l.route?.length){l.edgeTotal=0;l.edgeRemaining=0;l.edgePhase=0;return}
 l.edgeTotal=leaderLegDuration(l,l.route[0]);l.edgeRemaining=l.edgeTotal;l.edgePhase=Math.max(0,Math.min(.999,phase));
}
function sendCommander(id,dest){
 const l=leaderList(game.player).find(x=>x.id===id);
 if(!l||l.assignedArmy||l.route.length||!byId[dest]||owner(dest)!==l.owner||l.at===dest||owner(l.at)!==l.owner){toast('Select another friendly destination for a free commander');return false}
 const route=neighbors(l.at,dest,l.owner);
 if(!route||route.some(x=>owner(x)!==l.owner&&!canPass(l.owner,owner(x)))){toast('No safe route through permitted provinces');return false}
 l.route=route;startLeaderLeg(l,pct());
 let eta=0,prev=l.at;for(const next of route){eta+=leaderLegDuration({...l,at:prev},next);prev=next}
 line(commanderDef(l).name+' departs '+byId[l.at].name+' for '+byId[dest].name+'. Estimated '+eta.toFixed(1)+' game months.','leader','Commander dispatched');
 renderAll();save();toast('Commander is travelling');return true;
}
function arriveCommander(l){
 if(!l.route?.length)return;
 const next=l.route[0];
 if(owner(next)!==l.owner&&!canPass(l.owner,owner(next))){l.route=[];startLeaderLeg(l);line(commanderDef(l).name+' halts at a closed frontier.','leader');return}
 l.at=next;l.route.shift();
 if(l.route.length)startLeaderLeg(l,pct());
 else{startLeaderLeg(l);line(commanderDef(l).name+' has arrived at '+byId[next].name+' and can command local troops.','leader','Commander arrives')}
}
function monthlyCommanderTravel(){
 for(const l of game.leaders||[]){
  if(!l.active||l.assignedArmy||!l.route?.length)continue;
  if(!l.edgeTotal||l.edgeRemaining<=0)startLeaderLeg(l,0);
  l.edgeRemaining-=1-(l.edgePhase||0);l.edgePhase=0;
  if(l.edgeRemaining<=1e-7)arriveCommander(l);
 }
}
function preciseCommanderTravel(){
 let moved=false;
 for(const l of game.leaders||[])if(l.active&&!l.assignedArmy&&l.route?.length&&l.edgeTotal>0&&
  l.edgeRemaining<=Math.max(0,pct()-(l.edgePhase||0))+1e-7){arriveCommander(l);moved=true}
 return moved;
}
function commanderRosterHtml(){
 const list=leaderList(game.player),coming=LEADER_DEFS.filter(d=>d.owner===game.player&&d.start>game.year);
 return '<div class="eyebrow">Historical command · '+escapeHtml(FACTIONS[game.player].name)+'</div>'+
 '<div class="leader-nation">National leadership: <strong>+'+(nationalCommandBonus(game.player)*100).toFixed(1)+
 '% combat strength and gold output</strong>. Assign a commander to an army for a larger tactical bonus.</div>'+
 (list.length?list.map(l=>{const d=commanderDef(l),a=l.assignedArmy?mobileArmy(l.assignedArmy):null;
  const status=a?'Leads '+total(a)+' troops':l.route.length?'En route to '+byId[l.route[l.route.length-1]]?.name:'Ready to command';
  return '<div class="leader-card"><span class="leader-star">★ COMMANDER</span><h3>'+escapeHtml(d.name)+'</h3>'+
  '<div class="leader-location">'+escapeHtml(byId[leaderLocation(l)]?.name||'In transit')+' · '+escapeHtml(status)+'</div>'+
  '<p class="small">'+escapeHtml(d.trait)+' · National +'+(d.nation*100).toFixed(1)+'% · Attached army attack +'+
  Math.round(d.command*100)+'%, defense +'+Math.round(d.command*.75*100)+'%</p>'+
  '<button class="btn primary" data-act="leaderInspect" data-id="'+l.id+'">Orders / Transfer</button></div>'}).join(''):
  '<p class="small">No commanders available during this period.</p>')+
 (coming.length?'<hr class="sep"><div class="eyebrow">Future historical commanders</div>'+
  coming.map(d=>'<div class="small">★ '+escapeHtml(d.name)+' · '+d.start+'</div>').join(''):'')+
 '<p class="small">Historical-era arrival dates are approximate. Command garrisons and bonuses are alternate-history game abstractions.</p>';
}
function commanderOrdersHtml(){
 const l=leaderList(game.player).find(x=>x.id===selectedLeader);
 if(!l)return '<p>Commander unavailable.</p><button class="btn" data-act="leaderRoster">Back</button>';
 const d=commanderDef(l),a=l.assignedArmy?mobileArmy(l.assignedArmy):null;
 const armies=game.armies.filter(q=>q.owner===l.owner&&q.at===l.at&&activeArmy(q)&&!q.battle&&!q.route.length&&!q.camp&&!leaderForArmy(q));
 const dests=game.provinces.filter(p=>p.owner===l.owner&&p.id!==l.at&&neighbors(l.at,p.id,l.owner)?.every(x=>owner(x)===l.owner||canPass(l.owner,owner(x))));
 let control='';
 if(a)control='<p class="small">Attached to '+total(a)+' troops. Travels with this army.</p>'+
  '<div class="buttons"><button class="btn" data-act="inspectArmy" data-id="'+a.id+'">Inspect army</button>'+
  '<button class="btn" data-act="leaderDetach" data-id="'+l.id+'"'+(a.route.length||a.battle||a.camp?' disabled':'')+'>Detach here</button></div>';
 else if(l.route.length)control='<div class="notice">En route to '+escapeHtml(byId[l.route[l.route.length-1]]?.name||'?')+'. Assignment is locked until arrival.</div>';
 else control='<div class="eyebrow">Attach to local troops</div>'+
 (armies.length?'<select class="trade-select" id="leaderArmyPick">'+armies.map(q=>'<option value="'+q.id+'">'+
  total(q)+' troops · '+escapeHtml(byId[q.at].name)+'</option>').join('')+'</select>'+
  '<button class="btn primary block" data-act="leaderAttach" data-id="'+l.id+'">★ Deploy with this army</button>':
  '<p class="small">No available uncommanded army stationed here.</p>')+
 '<hr class="sep"><div class="eyebrow">Independent transfer</div>'+
 (dests.length?'<select class="trade-select" id="leaderDestination">'+dests.map(p=>'<option value="'+p.id+'">'+
  escapeHtml(byId[p.id].name)+'</option>').join('')+'</select>'+
  '<p class="small">A commander travelling alone follows roads and weather and takes real game time to arrive.</p>'+
  '<button class="btn primary block" data-act="leaderMove" data-id="'+l.id+'">Send to selected territory</button>':'<p class="small">No accessible friendly destinations.</p>');
 return '<div class="eyebrow">Commander orders</div><h2>★ '+escapeHtml(d.name)+'</h2>'+
 '<p class="small">'+escapeHtml(d.trait)+' · '+escapeHtml(byId[leaderLocation(l)]?.name||'In transit')+'</p>'+
 '<div class="leader-nation">Nation +'+(d.nation*100).toFixed(1)+'% · Attached army attack +'+
 Math.round(d.command*100)+'% and defense +'+Math.round(d.command*.75*100)+'%</div>'+
 control+'<hr class="sep"><button class="btn" data-act="leaderRoster">← All commanders</button>';
}
