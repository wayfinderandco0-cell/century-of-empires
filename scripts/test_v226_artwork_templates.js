#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const cp=require('node:child_process');
const path=require('node:path');
const V123=require('../terrain-grid/v123-atlas.js');
const V226=require('../terrain-grid/v226-artwork-contract.js');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'v121-octagon-1-painted-road.html'),'utf8');
const match=html.match(/const ROADS=(\{[^\r\n]+\});/);
assert.ok(match,'must parse ORIGINAL V121 graph data');
const atlas=V123.create(JSON.parse(match[1]),{experimentalSeams:true});
const before=JSON.stringify(atlas.tiles.map(t=>({id:t.id,roads:t.roads})));
const model=V226.build(atlas);
assert.equal(JSON.stringify(atlas.tiles.map(t=>({id:t.id,roads:t.roads}))),before,
  'art authoring cannot mutate navigation graph');
assert.deepEqual(model.cells.map(c=>c.id),['west','south']);
assert.deepEqual(model.cells[0].join,[1536,478]);
assert.deepEqual(model.cells[0].unverifiedTerminus,[275,550]);
assert.deepEqual(model.cells[1].join,[466,0]);
assert.deepEqual(model.cells[1].unverifiedTerminus,[1270,605]);
assert.equal(model.productionApproved,false);
for(const cell of model.cells){
  const svg=V226.svg(cell);
  assert.match(svg,/ART CLEARANCE ONLY/);
  assert.match(svg,/stroke-width="52"/);
  assert.match(svg,/stroke-width="22"/);
  assert.match(svg,/NOT SURVEYED/);
  assert.ok(svg.includes('M'+cell.points[0].join(' ')));
  assert.ok(svg.includes('L'+cell.points.at(-1).join(' ')));
  assert.equal(cell.sourceRegisteredToV123,false);
  assert.equal(cell.bridgeBanksVerified,false);
  assert.equal(cell.onwardRoadVerified,false);
  assert.equal(cell.productionApproved,false);
}
const clone=()=>V123.create(JSON.parse(match[1]),{experimentalSeams:true});
let bad=clone();bad.tiles[0].roads.east[3][0]+=1;
assert.throws(()=>V226.build(bad),/immutable|route|endpoints|drifted/);
// Internal vertices may vary in other branches; protected hash is the
// independent control against any such unreviewed edit, not this test alone.
bad=clone();bad.tiles[0].roads.fake=[[1,2],[3,4]];
assert.throws(()=>V226.build(bad),/unreviewed/);
bad=clone();bad.tiles[2].roads.north.at(-1)[0]=1350;
assert.throws(()=>V226.build(bad),/endpoints drifted/);
bad=clone();bad.productionApproved=true;
assert.throws(()=>V226.build(bad),/approval/);
bad=clone();bad.tiles[0].origin=[12,0];
assert.throws(()=>V226.build(bad),/origin/);
bad=clone();bad.tiles[2].roads.north[5]=[NaN,1];
assert.throws(()=>V226.build(bad),/invalid/);
bad=clone();bad.links.push({id:'invented'});
assert.throws(()=>V226.build(bad),/topology/);
assert.throws(()=>V226.svg({...model.cells[0],productionApproved:true}),/untrusted/);
const run=(...args)=>cp.execFileSync(process.execPath,
  [path.join(root,'scripts/build_v226_artwork_templates.js'),...args],
  {cwd:root,encoding:'utf8'});
run();run('--verify');
const file=path.join(root,'terrain-v226/templates/west-clearance.svg');
const good=fs.readFileSync(file,'utf8');
fs.writeFileSync(file,good.replace('stroke-width="52"','stroke-width="53"'));
assert.throws(()=>run('--verify'),/drifted/);
run();run('--verify');
console.log('V226 negative controls PASS: protected graph, two cells, endpoints, false approval, deterministic SVG, tamper rejection');
