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
// V94 woods.json is a 0/1 woodland mask, NOT an 8-bit 0..255 intensity.
// The previous single-center sample + thresholds 55/110 mislabeled every
// forest cell as farmland. Sample the actual V94 footprint and Natural Earth
// 10m coastline separately; negative elevation does not imply ocean.
const land=read("terrain-v94/land.json");
const landPolys=land.polygons.map(points=>{
 const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
 return {points,bounds:[Math.min(...xs),Math.min(...ys),Math.max(...xs),Math.max(...ys)]};
});
function inside(x,y,points){
 let hit=false;
 for(let i=0,j=points.length-1;i<points.length;j=i++){
  const a=points[i],b=points[j];
  if((a[1]>y)!==(b[1]>y) && x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])hit=!hit;
 }
 return hit;
}
function onLand(x,y){
 for(const p of landPolys){
  const b=p.bounds;if(x>=b[0]&&x<=b[2]&&y>=b[1]&&y<=b[3]&&inside(x,y,p.points))return true;
 }
 return false;
}
function footprint(c,r){
 const xs=Math.floor(c*el.width/COLS),xe=Math.ceil((c+1)*el.width/COLS);
 const ys=Math.floor(r*el.height/ROWS),ye=Math.ceil((r+1)*el.height/ROWS);
 let n=0,wood=0,sum=0,min=Infinity,max=-Infinity;
 for(let y=ys;y<ye;y+=2)for(let x=xs;x<xe;x+=2){
  const k=y*el.width+x,h=el.heights[k];
  if(!Number.isFinite(h))continue;
  n++;sum+=h;wood+=wo.forest[k]===1?1:0;min=Math.min(min,h);max=Math.max(max,h);
 }
 let landCount=0,coastSamples=0;
 for(let iy=0;iy<5;iy++)for(let ix=0;ix<5;ix++){
  const px=(c+(ix+.5)/5)*meta.gameSize[0]/COLS;
  const py=(r+(iy+.5)/5)*meta.gameSize[1]/ROWS;
  landCount+=onLand(px,py)?1:0;coastSamples++;
 }
 const landFraction=landCount/coastSamples,forestPct=100*wood/Math.max(n,1);
 const elev=Math.round(sum/Math.max(n,1)),relief=Math.round(max-min);
 let biome;
 if(landFraction<.12)biome="sea";
 else if(landFraction<.88)biome="coast-and-islands";
 else if(elev>=1650)biome="alpine";
 else if(elev>=650||relief>=700)biome="hills-and-mountains";
 else if(forestPct>=58)biome="forest";
 else if(forestPct>=24)biome="mixed-forest";
 else if(r<6&&elev<150)biome="northern-lowlands";
 else biome="farmland-and-plains";
 return {elevationMetersApprox:elev,elevationRangeMetersApprox:[Math.round(min),Math.round(max)],
  reliefMetersApprox:relief,forestCoverPctApprox:Math.round(forestPct),
  landFractionApprox:Math.round(landFraction*100)/100,biome};
}
const geographic=new Map();
for(let r=0;r<ROWS;r++)for(let c=0;c<COLS;c++)geographic.set(id(c,r),footprint(c,r));
const height=(x,y)=>geographic.get(id(x,y)).elevationMetersApprox;
const landFraction=(x,y)=>geographic.get(id(x,y)).landFractionApprox;
const coords=[],seen=new Set();let x=9,y=12,n=1,d=0;const dirs=[[1,0],[0,1],[-1,0],[0,-1]];
function add(){if(valid(x,y)&&!seen.has(id(x,y))){coords.push([x,y]);seen.add(id(x,y));}}
add();while(coords.length<TOTAL){for(let j=0;j<2;j++){const v=dirs[(d++)%4];for(let k=0;k<n;k++){x+=v[0];y+=v[1];add();}}n++;}
const arterialRows=new Set([5,9,12,16,20]),arterialColumns=new Set([3,7,9,13,16]);
const links=[],byId=new Map();
for(let r=0;r<ROWS;r++)for(let c=0;c<COLS;c++)for(const v of [[1,0],[0,1]]){
 const nx=c+v[0],ny=r+v[1];if(!valid(nx,ny)||landFraction(c,r)<.88||landFraction(nx,ny)<.88)continue;
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
 geography:{...geographic.get(id(c,r)),riverFeatures:riversAt(c,r),source:"V94 Mapzen DEM / Natural Earth II 0-1 woodland / Natural Earth 10m land; modern broad geography, NOT 1780 survey"},
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
 // A candidate border port is a dot, NOT a painted or verified cartway.
 return '<circle cx="'+p[0]+'" cy="'+p[1]+'" r="13" fill="none" stroke="#f5c56a" stroke-width="5" stroke-dasharray="5 6"/>';
 }).join("");
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024"><defs><clipPath id="crop"><polygon points="'+frame+'"/></clipPath></defs><g clip-path="url(#crop)"><image href="overview.webp" x="'+(-c*W)+'" y="'+(-r*H)+'" width="'+(COLS*W)+'" height="'+(ROWS*H)+'" preserveAspectRatio="none"/>'+road+'</g><polygon points="'+frame+'" stroke="#c5aa78" stroke-width="7" fill="none"/><rect x="280" y="22" width="980" height="77" fill="#162922df" rx="8"/><text x="301" y="70" font-family="sans-serif" font-size="34" fill="#fff3dc">'+cell.id+' · '+cell.geography.biome+'</text><rect x="250" y="922" width="1060" height="69" fill="#162922ec" rx="8"/><text x="267" y="963" font-family="sans-serif" font-size="25" fill="#fff3dc">GEOGRAPHY PREVIEW · PORTS ONLY · NO ROAD ART</text></svg>';
}
for(const cell of selected)fs.writeFileSync(path.join(dest,cell.id+".svg"),svg(cell));
fs.copyFileSync(path.join(root,"terrain-v94/overview.webp"),path.join(dest,"overview.webp"));
const batchLinks=links.filter(l=>sids.has(l.a)||sids.has(l.b));
fs.writeFileSync(path.join(dest,"manifest.json"),JSON.stringify({schema:"coe-octagon-factory/v1",status:"candidate-not-final-art",batch,worldCellCount:TOTAL,generated: selected.length,routeLinks:batchLinks,cells:selected},null,2));
const cards=selected.map(z=>'<article><img loading="lazy" src="'+z.id+'.svg" alt="'+z.id+' map data"/><p>'+z.id+' · '+z.geography.biome+' · '+z.routeLinkIds.length+' proposed road ports</p></article>').join("");
fs.writeFileSync(path.join(dest,"index.html"),'<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"/><title>Century of Empires — 50 candidate cells</title><style>body{background:#13231d;color:#f6e6c6;font:15px system-ui;margin:15px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(245px,1fr));gap:10px}article{background:#23382d;padding:8px;border-radius:8px}img{width:100%}p{font-size:12px}strong{color:#ffd09d}</style><h1>Batch '+batch+': '+selected.length+' Europe geography candidates</h1><p><strong>NOT FINAL APPROVED ART.</strong> V94 terrain cover now sampled over each footprint, with Natural Earth coastline and woodland percentage. Dotted ports are UNVERIFIED proposals, NOT roads. Final photographic terrain, verified roads, scenario-specific historical conquest towns, QA and integration remain separate stages.</p><main>'+cards+'</main></html>');
const keys=new Set(all.map(z=>z.id));if(keys.size!==TOTAL)throw Error("Duplicate/missing cells");
for(const l of links){const [ax,ay]=l.localA,[bx,by]=l.localB,a=all.find(z=>z.id===l.a),b=all.find(z=>z.id===l.b);if(!a||!b)throw Error("Unknown endpoint");if(a.origin[0]+ax!==b.origin[0]+bx||a.origin[1]+ay!==b.origin[1]+by)throw Error("Bad seam "+l.id);}
if(selected.some(z=>z.historicalConquestTowns.length||z.art.finalNativeArtRendered||z.usableForGameplay))throw Error("Incorrect approval");
const report={batch,geographyPreviews:selected.length,totalPlanned:TOTAL,biomeCounts:Object.fromEntries([...new Set(selected.map(c=>c.geography.biome))].map(b=>[b,selected.filter(c=>c.geography.biome===b).length])),proposedIntercellLinks:links.length,
 inBatchAdjacentLinks:links.filter(l=>sids.has(l.a)&&sids.has(l.b)).length,
 certifiedHistoricalTowns:0,photoArtApproved:0,gameplayValidated:0};
fs.writeFileSync(path.join(dest,"qa-report.json"),JSON.stringify(report,null,2));
console.log(JSON.stringify(report));