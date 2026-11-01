/* Original countryside forest-meadow art; deterministic 1536×1024 layered vector master.
 * Not a heightmesh, photo crop, road graphic, or a certified V267 art match.
 * No towns, roads, rivers, or implied strategic nodes. Run: node build-v267-forest-meadow-01.js > forest-meadow-01.svg
 */
const buildTile=function buildTile(seed=2671101){
  let s=seed>>>0;const rand=()=>((s=(1664525*s+1013904223)>>>0)/4294967296);
  const rr=(a,b)=>a+(b-a)*rand(),fmt=n=>Number(n).toFixed(1);
  const parts=[];
  const add=s=>parts.push(s);
  add(`<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024" viewBox="0 0 1536 1024" role="img" aria-label="Original forested alpine meadow terrain without roads, rivers or settlements">
  <defs>
    <clipPath id="oct"><path d="M256 0 H1280 L1536 256 V768 L1280 1024 H256 L0 768 V256 Z"/></clipPath>
    <linearGradient id="land" x2=".85" y2="1"><stop stop-color="#384e2c"/><stop offset=".27" stop-color="#516536"/><stop offset=".55" stop-color="#71804a"/><stop offset=".77" stop-color="#697741"/><stop offset="1" stop-color="#3d542d"/></linearGradient>
    <linearGradient id="meadow" x1="0" y1="0" x2=".6" y2="1"><stop stop-color="#a0a85b"/><stop offset=".45" stop-color="#758d4b"/><stop offset="1" stop-color="#526f38"/></linearGradient>
    <linearGradient id="slope" x1="0" y1="0" x2=".9" y2="1"><stop stop-color="#263d2c"/><stop offset=".36" stop-color="#536345"/><stop offset=".58" stop-color="#85906a"/><stop offset="1" stop-color="#344732"/></linearGradient>
    <linearGradient id="rock" x1=".1" y1="0" x2=".9" y2="1"><stop stop-color="#c1b9a3"/><stop offset=".25" stop-color="#868b7c"/><stop offset=".6" stop-color="#454c48"/><stop offset="1" stop-color="#292f2f"/></linearGradient>
    <radialGradient id="light"><stop stop-color="#e0cf86" stop-opacity=".26"/><stop offset="1" stop-color="#d6c98e" stop-opacity="0"/></radialGradient>
    <filter id="soil"><feTurbulence baseFrequency=".017" numOctaves="4" seed="13" result="noise"/><feColorMatrix in="noise" type="saturate" values=".12"/><feBlend in="SourceGraphic" mode="multiply"/></filter>
    <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".34" numOctaves="2" seed="7" result="n"/><feColorMatrix in="n" type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".08"/></feComponentTransfer></filter>
    <filter id="soft"><feGaussianBlur stdDeviation="9"/></filter>
  </defs><g clip-path="url(#oct)">
  <rect width="1536" height="1024" fill="url(#land)"/>
  <path d="M-30 0 L500 0 Q640 120 470 260 Q340 370 60 410 L-30 340Z" fill="#283b2d"/>
  <path d="M920 -40 L1560 -30 L1570 530 Q1450 435 1360 410 Q1200 340 1150 230 Q1070 105 920 -40" fill="url(#slope)"/>
  <path d="M-30 620 Q320 520 475 585 Q645 660 790 540 Q990 405 1240 480 Q1400 530 1560 610 L1560 1100 H-30Z" fill="#516b3a" opacity=".45"/>
  <path d="M160 270 Q390 185 560 320 Q660 405 845 350 Q1070 285 1230 420 Q1300 505 1220 630 Q1020 780 755 785 Q510 760 310 855 Q105 820 140 625 Q70 430 160 270" fill="url(#meadow)" opacity=".92"/>
  <path d="M-40 790 Q280 720 450 870 Q720 950 880 815 Q1090 675 1500 805 L1560 1100H-40Z" fill="#304c30" opacity=".45"/>
  <ellipse cx="775" cy="490" rx="670" ry="430" fill="url(#light)"/>`);
  // Wide mountain shoulder with shaded facets, never a heightmesh.
  const rocks=[
    "M970 0 L1270 0 1490 220 1430 385 1270 315 1160 190 1090 145Z",
    "M1080 55 L1215 0 1380 130 1300 290 1170 235Z",
    "M-30 80 L145 0 350 0 315 170 155 280 -30 290Z",
    "M1220 455 L1390 370 1510 505 1460 635 1335 608 1250 550Z"
  ];
  for(let i=0;i<rocks.length;i++){
    add(`<path d="${rocks[i]}" fill="url(#rock)" opacity="${i===0?".93":".73"}"/>`);
  }
  add(`<path d="M1095 105 L1220 15 1350 135 1280 250 1200 175 1150 205Z" fill="#d2c8b0" opacity=".48"/>
  <path d="M1185 60 L1238 20 1295 112 1270 190 1238 134Z" fill="#f0e8ce" opacity=".56"/>
  <path d="M1330 135 L1390 218 1360 295 1300 260Z" fill="#1c2927" opacity=".55"/>
  <path d="M20 145 L175 5 250 40 120 225Z" fill="#9b9d85" opacity=".6"/>
  <path d="M130 180 L185 70 200 140 150 250Z" fill="#d6cfb1" opacity=".55"/>`);
  // Natural boulders embedded in the grass with directional shadow and facets.
  for(let i=0;i<270;i++){
    let x=rr(0,1536),y=rr(30,1024);
    if(x>350&&x<1100&&y>290&&y<770&&rand()<.72)continue;
    const r=rr(2.5,15)*(y/1500+.6);
    add(`<ellipse cx="${fmt(x+rr(3,10))}" cy="${fmt(y+r*.3)}" rx="${fmt(r*1.15)}" ry="${fmt(r*.46)}" fill="#1c3026" opacity=".43"/>
    <path d="M${fmt(x-r)} ${fmt(y+r*.15)} L${fmt(x-r*.45)} ${fmt(y-r*.75)} L${fmt(x+r*.32)} ${fmt(y-r*.85)} L${fmt(x+r)} ${fmt(y+r*.1)}Z" fill="${rand()<.4?"#a5a694":"#737c70"}" opacity=".8"/>
    <path d="M${fmt(x-r*.45)} ${fmt(y-r*.75)} L${fmt(x+r*.32)} ${fmt(y-r*.85)} L${fmt(x+r*.14)} ${fmt(y+r*.1)}Z" fill="#c0bd9f" opacity=".45"/>`);
  }
  // Patchy ground vegetation and tiny stone flecks, at true native art scale.
  for(let i=0;i<2400;i++){
    const x=rr(0,1536),y=rr(0,1024),r=rr(1,7);
    const color=["#b6aa66","#a3a967","#344e2e","#46683a","#7f8f52","#d5c18b"][Math.floor(rr(0,6))];
    add(`<ellipse cx="${fmt(x)}" cy="${fmt(y)}" rx="${fmt(r)}" ry="${fmt(r*.28)}" fill="${color}" opacity="${fmt(rr(.15,.55))}"/>`);
  }
  // Conifers are separate foreground objects with consistent silhouette and scale.
  const trees=[];
  for(let i=0;i<850;i++){
    const x=rr(-20,1556),y=rr(-40,1050);
    const open=((x>330&&x<1180&&y>300&&y<810)||(x>230&&x<1050&&y>820));
    if(open&&rand()<.87)continue;
    const scale=(.40+y/1150)*rr(.65,1.3),h=rr(24,58)*scale,w=h*rr(.30,.46);
    trees.push({x,y,h,w,tint:rand()});
  }
  trees.sort((a,b)=>a.y-b.y);
  for(const t of trees){
    const {x,y,h,w,tint}=t,xf=fmt(x),yf=fmt(y),hf=fmt(h),wf=fmt(w);
    const dark=tint<.35?"#152f28":tint<.75?"#203c2b":"#30472e";
    const mid=tint<.35?"#355640":tint<.75?"#3b5c3c":"#527045";
    const high=tint<.35?"#648366":tint<.75?"#658457":"#80905a";
    add(`<ellipse cx="${fmt(x+h*.28)}" cy="${fmt(y+h*.08)}" rx="${fmt(w*.8)}" ry="${fmt(h*.20)}" fill="#15241d" opacity=".42"/>
    <path d="M${xf} ${fmt(y-h*.95)} L${xf} ${fmt(y+h*.08)}" stroke="#3e3928" stroke-width="${fmt(Math.max(1,h*.055))}"/>
    <path d="M${xf} ${fmt(y-h)} Q${fmt(x-w*.15)} ${fmt(y-h*.66)} ${fmt(x-w*.58)} ${fmt(y-h*.36)} L${fmt(x-w*.24)} ${fmt(y-h*.42)} L${fmt(x-w)} ${fmt(y-h*.04)} Q${xf} ${fmt(y-h*.13)} ${fmt(x+w)} ${fmt(y-h*.04)} L${fmt(x+w*.24)} ${fmt(y-h*.42)} L${fmt(x+w*.56)} ${fmt(y-h*.35)}Z" fill="${dark}"/>
    <path d="M${xf} ${fmt(y-h*.98)} Q${fmt(x-w*.08)} ${fmt(y-h*.56)} ${fmt(x-w*.38)} ${fmt(y-h*.23)} L${xf} ${fmt(y-h*.25)}Z" fill="${high}" opacity=".72"/>
    <path d="M${xf} ${fmt(y-h*.89)} L${fmt(x+w*.35)} ${fmt(y-h*.42)} L${fmt(x+w*.72)} ${fmt(y-h*.10)} L${xf} ${fmt(y-h*.24)}Z" fill="${mid}" opacity=".8"/>`);
  }
  // Foreground small shrubs and wildflowers.
  for(let i=0;i<320;i++){
    const x=rr(0,1536),y=rr(320,1024),r=rr(2,7)*(y/1400+.6);
    add(`<ellipse cx="${fmt(x)}" cy="${fmt(y)}" rx="${fmt(r*1.8)}" ry="${fmt(r*.8)}" fill="${rand()<.5?"#324e31":"#476b39"}" opacity=".85"/>
    <circle cx="${fmt(x+rr(-r,r))}" cy="${fmt(y-rr(0,r))}" r="${fmt(r*.28)}" fill="${rand()<.6?"#c6b477":"#d1cbab"}" opacity=".7"/>`);
  }
  add(`<rect width="1536" height="1024" fill="#000" filter="url(#grain)" opacity=".20"/>
  <path d="M256 1 H1280 L1535 256 V768 L1280 1023 H256 L1 768 V256Z" fill="none" stroke="#aa9568" stroke-width="3" opacity=".9"/>
  </g></svg>`);
  return parts.join("\n");
};
if(typeof module!=="undefined")module.exports={buildTile};
if(typeof require!=="undefined"&&require.main===module)process.stdout.write(buildTile());
