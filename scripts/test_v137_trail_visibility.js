#!/usr/bin/env node
'use strict';
// Canvas stroke contract for the V136 three-octagon preview. This does not
// certify geographic/historical placement or the visual quality of source art.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'..','v136-continuous-alpine-preview.html'),'utf8');
const from=source.indexOf('function paintTrack('),to=source.indexOf('function distanceToRoad(');
assert(from>=0&&to>from,'Cannot locate V136 road-painting functions');
const program=source.slice(from,to);
function strokesFor(points){
 const events=[];
 const ctx={
  globalAlpha:1,
  save(){this.savedAlpha=this.globalAlpha},
  restore(){this.globalAlpha=this.savedAlpha},
  beginPath(){this.points=[]},
  moveTo(x,y){this.points.push([x,y])},
  lineTo(x,y){this.points.push([x,y])},
  stroke(){events.push({points:this.points.map(p=>p.slice()),alpha:this.globalAlpha,width:this.lineWidth})}
 };
 const before=JSON.stringify(points),sandbox={cx:ctx};
 vm.createContext(sandbox);
 vm.runInContext(program+'\npaintNaturalTrailFinish('+JSON.stringify(points)+');',sandbox);
 assert.equal(JSON.stringify(points),before,'Painter must not alter navigable waypoints');
 return events;
}
const points=[[0,478],[80,478],[165,480],[245,495],[330,515],[420,520]];
const events=strokesFor(points);
assert(events.length>=15,'Expected solid body and two tapered segments');
for(let i=1;i<points.length;i++){
 const a=points[i-1],b=points[i];
 const covering=events.filter(s=>s.points.some((p,j)=>j&&JSON.stringify(s.points[j-1])===JSON.stringify(a)&&JSON.stringify(p)===JSON.stringify(b)));
 assert(covering.length,'Navigable segment '+(i-1)+' has no paint');
 assert(covering.some(s=>s.alpha>=.75&&s.width>=2),'Navigable segment '+(i-1)+' is too faint');
}
for(const s of events)for(const p of s.points)
 assert(points.some(q=>q[0]===p[0]&&q[1]===p[1]),'Painter invented a waypoint');
const short=strokesFor([[1,2],[3,4],[5,6]]);
assert(short.some(s=>s.points.some(p=>p[0]===5&&p[1]===6)&&s.alpha===1),'Short route must remain visible');
assert(source.includes('for(const pts of Object.values(t.roads))paintNaturalTrailFinish(pts)'),'Neighboring road painter was disconnected');
console.log('V137 trail visibility: body, tapered tail, full coverage, immutable waypoints, short route, and integration passed. Not art approval.');
