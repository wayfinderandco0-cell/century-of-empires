#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const cp = require('node:child_process');
const V123 = require('../terrain-grid/v123-atlas.js');
const V226 = require('../terrain-grid/v226-artwork-contract.js');
const V227 = require('../terrain-grid/v227-art-ingest.js');
const preview = fs.readFileSync('v242-photo-art-import-playtest.html', 'utf8');
const old = fs.readFileSync('v236-authored-alpine-playtest.html', 'utf8');
const hash = p => cp.execFileSync('git',['hash-object',p],{encoding:'utf8'}).trim();
assert.equal(hash('terrain-grid/v123-atlas.js'), '09f04b4062e24fbacbb645307462cdddce2b2aa3');
assert.equal(hash('v121-octagon-1-painted-road.html'), '4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382');
const roads = JSON.parse(fs.readFileSync('v121-octagon-1-painted-road.html','utf8')
  .match(/const ROADS=(\{[^\r\n]+\});/)[1]);
const atlas = V123.create(roads,{experimentalSeams:true});
assert.equal(V227.validateContract(V226.build(atlas)),true);
const fallback = 'V236AuthoredAlpine.paint(cx,atlas)';
const imported = 'V227ArtIngest.paint(cx)';
assert.ok(old.indexOf(imported) < old.indexOf(fallback),'regression fixture must reproduce hidden import');
assert.ok(preview.indexOf(fallback) < preview.indexOf(imported),'import must render after rejected fallback');
assert.equal(preview.match(/V227ArtIngest\.paint\(cx\)/g).length,1,'one imported art pass');
assert.equal(preview.match(/V236AuthoredAlpine\.paint\(cx,atlas\)/g).length,1,'one fallback pass');
assert.ok(preview.indexOf('centerPhoto)cx.drawImage(centerPhoto,1536,0,W,H)') > preview.indexOf(imported),
  'protected Matrei must be painted after imported neighboring artwork');
assert.match(preview,/V192\.orderTo|orderTo\(/);
assert.match(preview,/id="westArt"/);
assert.match(preview,/id="southArt"/);
assert.match(preview,/NOT APPROVED/);
assert.equal(atlas.productionApproved,false);
assert.equal(atlas.neighborArtFinal,false);
assert.equal(atlas.physicalIPhoneApproved,false);
console.log('V242 PASS: repaired imported-art stacking, original Matrei topmost, V123 graph hash, both import inputs, all approval gates false');
