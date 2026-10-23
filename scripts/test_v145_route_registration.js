#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const V123=require('../terrain-grid/v123-atlas.js');
const audit=require('../terrain-grid/v145-route-registration.js');
const atlas=V123.create({west:[[99,478],[500,480]],south:[[466,0],[466,958]],bridge:[[813,486],[820,487]]},
                        {experimentalSeams:true});
const tiles=Object.fromEntries(atlas.tiles.map(t=>[t.id,t]));
assert.equal(tiles.west.roads.east.length,13);
assert.equal(tiles.south.roads.north.length,12);
function syntheticControl(tile,road,index){
  const p=tile.roads[road][index],world=[p[0]+tile.origin[0],p[1]+tile.origin[1]];
  const east=(world[0]-100)/.15,north=-(world[1]-200)/.15;
  return {road,index,lonLat:[11.52+east/(111320*Math.cos(47.13*Math.PI/180)),47.13+north/111320],
          source:{url:'https://example.org/SYNTHETIC-TEST-ONLY',featureId:`${tile.id}-${road}-${index}`,
                  kind:'modern-topographic'}};
}
const controls={
  west:[0,6,12].map(i=>syntheticControl(tiles.west,'east',i)),
  matrei:[syntheticControl(tiles.matrei,'west',0),syntheticControl(tiles.matrei,'west',1),syntheticControl(tiles.matrei,'south',2)],
  south:[0,6,11].map(i=>syntheticControl(tiles.south,'north',i))
};
const valid=audit.auditAtlas(atlas,controls);
assert.equal(valid.geometricFit,true);
assert.equal(valid.sharedGeographicFrame,true);
assert.equal(valid.productionApproved,false);
assert.equal(valid.navigableRouteCertified,false);
assert.equal(valid.evidenceAuthenticated,false);
assert.equal(valid.reports.length,3);
for(const report of valid.reports){assert.ok(report.maxResidualWorldPx<1e-7);assert.equal(report.independentHoldoutCount,1);}
function copy(x){return JSON.parse(JSON.stringify(x));}
let shifted=copy(controls);shifted.south[2].lonLat[0]+=.001;
assert.equal(audit.auditAtlas(atlas,shifted).geometricFit,false,'Wrong holdout must fail');
shifted=copy(controls);shifted.west[0].lonLat[0]+=.02;
assert.equal(audit.auditAtlas(atlas,shifted).geometricFit,false,'Bad baseline must fail');
shifted=copy(controls);shifted.south.forEach(p=>p.lonLat[0]+=.002);
assert.equal(audit.auditAtlas(atlas,shifted).sharedGeographicFrame,false,'Independent tile frame drift must fail');
shifted=copy(controls);shifted.west[1].index=shifted.west[0].index;
assert.throws(()=>audit.auditAtlas(atlas,shifted),/Duplicate route control/);
shifted=copy(controls);shifted.west[1].index=999;
assert.throws(()=>audit.auditAtlas(atlas,shifted),/No authoritative/);
shifted=copy(controls);shifted.west[1].world=[0,0];
assert.throws(()=>audit.auditAtlas(atlas,shifted),/invented world/);
shifted=copy(controls);shifted.west[1].source.url='http://untrusted.invalid';
assert.throws(()=>audit.auditAtlas(atlas,shifted),/traceable source/);
shifted=copy(controls);shifted.south.pop();
assert.throws(()=>audit.auditAtlas(atlas,shifted),/>=3 documented/);
shifted=copy(controls);shifted.west[1].lonLat=[0,0];
assert.throws(()=>audit.auditAtlas(atlas,shifted),/outside V97/);
assert.throws(()=>audit.auditAtlas(atlas,controls,{maxResidualPx:50}),/fail-closed/);
assert.throws(()=>audit.auditAtlas(atlas,{}),/>=3 documented/);
console.log('V145 route registration: synthetic three-tile common-frame PASS; 11 fail-closed assertions PASS; real tie points NOT supplied or certified.');
