#!/usr/bin/env node
// Regression guard: prevent prototype's rejected routes from being reclassified as playable.
import fs from 'node:fs';import path from 'node:path';import{fileURLToPath}from'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const state=read('terrain-puzzle/ACTIVE-ROUTE-REGISTRY-v1.json');
const old1=read('terrain-puzzle/BNR-O-0-0-hidden-routing.json'), old2=read('terrain-puzzle/BNR-O-1-0-hidden-routing.json');
const proposals=read('terrain-puzzle/OCT001-ARTGUIDED-PROPOSAL-v1.json');
const connector=read('terrain-puzzle/BNR-S-0--1-connector.json');
const cell=read('terrain-puzzle/BNR-O-0-0.json');
function check(test,msg){if(!test)throw Error(msg)}
check(state.approval_guard==='DENY_UNLESS_APPROVED','approval default must deny');
for(const id of ['BNR:O:0:0','BNR:O:1:0']){
const v=state.cells[id];check(v.route_nodes_active===0&&v.route_edges_active===0&&v.valid_edge_exits.length===0&&v.allowed_crossings.length===0,'no routes may be activated in '+id);}
check(state.cells['BNR:O:0:0'].terrain_access_status==='NO_APPROVED_ROUTE','001 route status changed');
check(state.cells['BNR:O:1:0'].terrain_access_status==='NOT_VERIFIED','002 route should not be marked permanently impassable');
check(state.connectors['BNR:S:0:-1'].active===false&&connector.route_enabled===false,'connector must stay closed');
check(old1.nodes.length===25&&old1.edges.length===23,'original routing audit data missing');
check(old2.nodes.length===18&&old2.edges.length===17,'002 routing audit data missing');
check([...old1.edges,...old2.edges].every(e=>e.enabled_in_game===false),'legacy route was enabled');
check(proposals.status==='REJECTED_FOR_001_AS_USABLE_ROUTES'&&proposals.proposals.every(x=>x.route_for_gameplay===false),'rejected art-guided route approved');
check(cell.route_decision.active_movement_edges===0,'source octagon claims approved edges');
check(state.next_target.location_status==='NOT_GEOREFERENCED_IN_PUZZLE_YET','unverified corridor location marked surveyed');
console.log(JSON.stringify({pass:true,status001:'NO_APPROVED_ROUTE',status002:'NOT_VERIFIED',activeEdges:0,connector:'CLOSED',retiredRouteOptions:proposals.proposals.length,oldDiagnosticNodes:43},null,2));
