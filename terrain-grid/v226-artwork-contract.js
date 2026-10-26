/* V226 immutable V123 road-aware artwork template.
 * ART AUTHORING ONLY: not a surveyed 1780 road, bridge bank, terrain source,
 * navigability change, or human/production approval.
 * The transparent SVGs expose exact unchanged game coordinates to artists.
 */
(function(root,factory){
  const api=factory();
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.V226ArtworkContract=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SIZE=[1536,1024];
  const SPECS=Object.freeze({
    west:{origin:[0,0],road:'east',join:[1536,478],unverified:[275,550],points:13,
      geometry:[[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],[980,515],[890,535],[784,551],[680,560],[570,540],[470,520],[370,522],[275,550]]},
    south:{origin:[1536,1024],road:'north',join:[466,0],unverified:[1270,605],points:12,
      geometry:[[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],[700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]]}
  });
  function insist(ok,msg){if(!ok)throw Error('V226 artwork contract: '+msg);}
  function point(p){return Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)
    &&p[0]>=0&&p[0]<=SIZE[0]&&p[1]>=0&&p[1]<=SIZE[1];}
  function same(a,b){return a.length===b.length&&a.every((v,i)=>v===b[i]);}
  function build(atlas){
    insist(atlas&&Array.isArray(atlas.tiles)&&Array.isArray(atlas.links),'missing original V123 atlas');
    insist(atlas.productionApproved===false,'must not inherit approval');
    insist(atlas.links.length===2,'unexpected connected road topology');
    const cells=[];
    for(const id of ['west','south']){
      const s=SPECS[id],t=atlas.tiles.find(t=>t.id===id);
      insist(t&&same(t.origin,s.origin),'incorrect '+id+' tile origin');
      insist(t.width===SIZE[0]&&t.height===SIZE[1],'incorrect '+id+' image dimensions');
      insist(Object.keys(t.roads||{}).length===1&&Array.isArray(t.roads[s.road]),
        'unreviewed '+id+' road');
      const pts=t.roads[s.road];
      insist(pts.length===s.points&&pts.every(point),'invalid '+id+' route points');
      insist(JSON.stringify(pts)===JSON.stringify(s.geometry),'immutable '+id+' interior geometry drifted');
      insist(same(pts[0],s.join)&&same(pts[pts.length-1],s.unverified),
        'immutable '+id+' endpoints drifted');
      const clean=pts.map(p=>Object.freeze(p.slice()));
      cells.push(Object.freeze({
        id,origin:Object.freeze(s.origin.slice()),width:SIZE[0],height:SIZE[1],
        road:s.road,points:Object.freeze(clean),
        join:Object.freeze(s.join.slice()),unverifiedTerminus:Object.freeze(s.unverified.slice()),
        sourceRegisteredToV123:false,bridgeBanksVerified:false,
        onwardRoadVerified:false,periodSafe:false,gameArtApproved:false,
        physicalIPhoneApproved:false,productionApproved:false
      }));
    }
    return Object.freeze({version:226,cells:Object.freeze(cells),
      purpose:'transparent authoring alignment guide, NOT game terrain',
      sourceRegisteredToV123:false,historicalRoadsVerified:false,
      gameArtApproved:false,physicalIPhoneApproved:false,productionApproved:false});
  }
  function svg(cell){
    insist(cell&&SPECS[cell.id]&&cell.productionApproved===false,'untrusted cell');
    const d=cell.points.map((p,i)=>(i?'L':'M')+p[0]+' '+p[1]).join(' ');
    const last=cell.unverifiedTerminus,join=cell.join;
    // 52px is a *conservative art-clearance guide*, NOT a playable road width.
    // Do not paint the broad guide into the game: V225 proved it looks like a highway.
    return [
      '<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024" viewBox="0 0 1536 1024">',
      '<title>V226 '+cell.id+' V123 route-aware ARTWORK CLEARANCE GUIDE — NOT APPROVED</title>',
      '<desc>Exact immutable V123 points; amber band is an art-authoring canopy-clearance warning, NOT a new road or verified geography.</desc>',
      '<path d="'+d+'" fill="none" stroke="#ffb02b" stroke-opacity=".34" stroke-width="52" stroke-linejoin="round" stroke-linecap="round"/>',
      '<path d="'+d+'" fill="none" stroke="#fdf1b7" stroke-opacity=".92" stroke-width="22" stroke-linejoin="round" stroke-linecap="round"/>',
      '<path d="'+d+'" fill="none" stroke="#dc462b" stroke-width="3" stroke-dasharray="8 8"/>',
      '<circle cx="'+join[0]+'" cy="'+join[1]+'" r="13" fill="#35d68a" stroke="#102d21" stroke-width="3"/>',
      '<circle cx="'+last[0]+'" cy="'+last[1]+'" r="17" fill="#f24438" stroke="#fff1c4" stroke-width="3"/>',
      '<text x="20" y="38" fill="#fff5d5" stroke="#15291f" stroke-width="5" paint-order="stroke" font-family="sans-serif" font-size="24">V226 ART CLEARANCE ONLY — '+cell.id.toUpperCase()+' — NOT SURVEYED</text>',
      '<text x="20" y="72" fill="#ffe7a5" stroke="#15291f" stroke-width="4" paint-order="stroke" font-family="sans-serif" font-size="17">Red endpoint: no verified onward cartway or destination</text>',
      '</svg>'
    ].join('\n');
  }
  return Object.freeze({build,svg,SIZE:Object.freeze(SIZE.slice())});
});