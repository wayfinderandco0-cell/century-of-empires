#!/usr/bin/env node
/* Century of Empires: 50-cell geography-backed factory (STAGING, not approved final art).
 * Canonical continent data: V94 height, forest, rivers and overview. Existing
 * V121/V123 scenery and movement remain untouched.
 * Usage: node scripts/octagon_factory_50.js --batch 0  (batch indices 0..8)
 */
"use strict";
const fs=require("node:fs"),path=require("node:path"),root=path.resolve(__dirname,"..");
const W=1536,H=1024,COLS=18,ROWS=24,TOTAL=COLS*ROWS,BATCH_SIZE=50;
const i=process.argv.indexOf("--batch"),batch=i>=0?Number(process.argv[i+1]):0;
if(!Number.isInteger(batch)||batch<0||batch>8)throw Error("--batch requires integer 0..8");
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const meta=read("terrain-v94/manifest.json"),el=read("terrain-v94/heights.json"),wo=read("terrain-v94/woods.json"),rv=read("terrain-v94/rivers.json");
if(el.width!==512||el.height!==384||el.heights.length!==512*384||wo.forest.length!==512*384)throw Error("Unexpected V94 map arrays");
const valid=(x,y)=>x>=0&&x<COLS&&y>=0&&y<ROWS,id=(x,y)=>"eu-"+String(x).padStart(2,"0")+"-"+String(y).padStart(2,"0");
function sample(data,x,y){const a=Math.max(0,Math.min(511,Math.round((x+.5)*512/COLS))),b=Math.max(0,Math.min(383,Math.round((y+.5)*384/ROWS)));return data[b*512+a];}
const height=(x,y)=>sample(el.heights,x,y),forest=(x,y)=>sample(wo.forest,x,y);
function biome(h,f,y){if(h< -80)return "sea";if(h<=0)return "coast-or-lowland";if(h>=1650)return "alpine";if(h>=650)return "hills-and-mountains";if(y<6&&h<150)return "northern-lowlands";if(f>=110)return "forest";if(f>=55)return "mixed-forest";return "farmland-and-plains";}
const coords=[],seen=new Set();let x=9,y=12,n=1,d=0;const dirs=[[1,0],[0,1],[-1,0],[0,-1]];
function add(){if(valid(x,y)&&!seen.has(id(x,y))){coords.push([x,y]);seen.add(id(x,y));}}
add();while(coords.length<TOTAL){for(let j=0;j<2;j++){const v=dirs[(d++)%4];for(let k=0;k<n;k++){x+=v[0];y+=v[1];add();}}n++;}
const arterialRows=new Set([5,9,12,16,20]),arterialColumns=new Set([3,7,9,13,16]);
const links=[],byId=new Map();
for(let r=0;r<ROWS;r++)for(let c=0;c<COLS;c++)for(const v of [[1,0],[0,1]]){
 const nx=c+v[0],ny=r+v[1];if(!valid(nx,ny)||height(c,r)<=0||height(nx,ny)<=0)continue;
 if(v[0]&&!arterialRows.has(r))continue;if(v[1]&&!arterialColumns.has(c))continue;
 // Both neighboring edge ports are derived from ONE absolute world point.
 const point=v[0]?[W*(c+1),H*r+360+(c*59+r*41)%300]:[W*c+600+(c*43+r*11)%310,H*(r+1)];
 const a=id(c,r),b=id(nx,ny);
 const link={id:"route-"+a+"-"+b,a,b,world:point,
  localA:[point[0]-c*W,point[1]-r*H],localB:[point[0]-nx*W,point[1]-ny*H],
  quality:"PROPOSED-FICTIONAL-ROUTE",historicallyVerified:false,
  artRoadPainted:false,gameplayEnabled:false};
 links.push(link);for(const t of [a,b]){if(!byId.has(t))byId.set(t,[]);byId.get(t).push(link);}
}
function riversAt(c,r){const [gw,gh]=meta.gameSize,left=c*gw/COLS,right=(c+1)*gw/COLS,top=r*gh/ROWS,bottom=(r+1)*gh/ROWS;
 return rv.rivers.filter(z=>{const nums=(z.d.match(/-?\d+(?:\.\d+)?/g)||[]).map(Number);for(let q=0;q+1<nums.length;q+=2)if(nums[q]>=left&&nums[q]<=right&&nums[q+1]>=top&&nums[q+1]<=bottom)return true;return false;}).slice(0,3).map(z=>({sourceName:z.name||null,rank:z.rank||null,historicallyVerified:false}));}
const [west,south,east,north]=meta.extent;
const all=coords.map(([c,r],rank)=>({id:id(c,r),rank,grid:[c,r],origin:[c*W,r*H],
 geographicBounds:[west+c*(east-west)/COLS,north-(r+1)*(north-south)/ROWS,west+(c+1)*(east-west)/COLS,north-r*(north-south)/ROWS],
 geography:{elevationMetersApprox:height(c,r),forestProxy:forest(c,r),biome:biome(height(c,r),forest(c,r),r),riverFeatures:riversAt(c,r),source:"V94 Mapzen/Natural Earth broad geography; NOT 1780 survey"},
 routeLinkIds:(byId.get(id(c,r))||[]).map(z=>z.id),scenicSettlements:[],
 historicalConquestTowns:[],provinceIds:[],scenicIsCapturable:false,
 art:{sourceType:"V94 atlas low-resolution preview",approvedV267PhotographicMethodApplied:false,
 finalNativeArtRendered:false,requiresFullResolutionOriginalArt:true},
 usableForGameplay:false,historicallyCertified:false}));
const selected=all.slice(batch*BATCH_SIZE,(batch+1)*BATCH_SIZE),sids=new Set(selected.map(z=>z.id));
const dest=path.join(root,"generated","octagon-factory","batch-"+String(batch).padStart(2,"0"));
fs.mkdirSync(dest,{recursive:true});
const frame="256,0 1280,0 1536,256 1536,768 1280,1024 256,1024 0,768 0,256";
function svg(cell){
 const [c,r]=cell.grid;
 const road=(byId.get(cell.id)||[]).map(l=>{
 const p=l.a===cell.id?l.localA:l.localB;
 return '<path d="M768 512 Q'+((768+p[0])/2)+' '+((512+p[1])/2-40)+' '+p[0]+' '+p[1]+'" stroke="#f5c56a" stroke-dasharray="12 10" stroke-width="14" opacity=".9" fill="none"/>';
 }).join("");
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024"><defs><clipPath id="crop"><polygon points="'+frame+'"/></clipPath></defs><g clip-path="url(#crop)"><image href="overview.webp" x="'+(-c*W)+'" y="'+(-r*H)+'" width="'+(COLS*W)+'" height="'+(ROWS*H)+'" preserveAspectRatio="none"/>'+road+'</g><polygon points="'+frame+'" stroke="#c5aa78" stroke-width="7" fill="none"/><rect x="280" y="22" width="980" height="77" fill="#162922df" rx="8"/><text x="301" y="70" font-family="sans-serif" font-size="34" fill="#fff3dc">'+cell.id+' · '+cell.geography.biome+'</text><rect x="250" y="922" width="1060" height="69" fill="#162922ec" rx="8"/><text x="267" y="963" font-family="sans-serif" font-size="25" fill="#fff3dc">GEOGRAPHY PREVIEW · PROPOSED ROADS · NOT FINAL ART</text></svg>';
}
for(const cell of selected)fs.writeFileSync(path.join(dest,cell.id+".svg"),svg(cell));
fs.copyFileSync(path.join(root,"terrain-v94/overview.webp"),path.join(dest,"overview.webp"));
const batchLinks=links.filter(l=>sids.has(l.a)||sids.has(l.b));
fs.writeFileSync(path.join(dest,"manifest.json"),JSON.stringify({schema:"coe-octagon-factory/v1",status:"candidate-not-final-art",batch,worldCellCount:TOTAL,generated: selected.length,routeLinks:batchLinks,cells:selected},null,2));
const cards=selected.map(z=>'<article><img loading="lazy" src="'+z.id+'.svg" alt="'+z.id+' map data"/><p>'+z.id+' · '+z.geography.biome+' · '+z.routeLinkIds.length+' proposed road ports</p></article>').join("");
fs.writeFileSync(path.join(dest,"index.html"),'<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"/><title>Century of Empires — 50 candidate cells</title><style>body{background:#13231d;color:#f6e6c6;font:15px system-ui;margin:15px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(245px,1fr));gap:10px}article{background:#23382d;padding:8px;border-radius:8px}img{width:100%}p{font-size:12px}strong{color:#ffd09d}</style><h1>Batch '+batch+': '+selected.length+' Europe geography candidates</h1><p><strong>NOT FINAL APPROVED ART.</strong> Existing V94 low-resolution base geography and speculative route ports are planning material only. Final photographic terrain, verified roads, scenario-specific historical conquest towns, QA and integration remain separate stages.</p><main>'+cards+'</main></html>');
const keys=new Set(all.map(z=>z.id));if(keys.size!==TOTAL)throw Error("Duplicate/missing cells");
for(const l of links){const [ax,ay]=l.localA,[bx,by]=l.localB,a=all.find(z=>z.id===l.a),b=all.find(z=>z.id===l.b);if(!a||!b)throw Error("Unknown endpoint");if(a.origin[0]+ax!==b.origin[0]+bx||a.origin[1]+ay!==b.origin[1]+by)throw Error("Bad seam "+l.id);}
if(selected.some(z=>z.historicalConquestTowns.length||z.art.finalNativeArtRendered||z.usableForGameplay))throw Error("Incorrect approval");
const report={batch,geographyPreviews:selected.length,totalPlanned:TOTAL,proposedIntercellLinks:links.length,
 inBatchAdjacentLinks:links.filter(l=>sids.has(l.a)&&sids.has(l.b)).length,
 certifiedHistoricalTowns:0,photoArtApproved:0,gameplayValidated:0};
fs.writeFileSync(path.join(dest,"qa-report.json"),JSON.stringify(report,null,2));
console.log(JSON.stringify(report));