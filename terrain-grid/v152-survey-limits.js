/* V152: mark where the existing V123 playable road graph ACTUALLY ends.
 * This is an honest survey-limit cue, not a bridge, continuation, road extension,
 * settlement, 1780 survey or claim of physical obstruction. V123 is immutable.
 */
(function(root,factory){
  const api=factory();
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.V152Survey=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const PINS=Object.freeze([
    {tile:'west',road:'east',local:[275,550],world:[275,550],name:'Western pass'},
    {tile:'south',road:'north',local:[1270,605],world:[2806,1629],name:'Southern valley'}
  ]);
  const same=(a,b)=>Array.isArray(a)&&a.length===2&&a.every((v,i)=>Number.isFinite(v)&&v===b[i]);
  function inspect(atlas){
    if(!atlas||!Array.isArray(atlas.tiles)||!atlas.network||
       !(atlas.network.graph instanceof Map)||typeof atlas.network.key!=='function')
      throw Error('V123 atlas/network required for survey-limit inspection');
    const markers=PINS.map(pin=>{
      const tile=atlas.tiles.find(t=>t.id===pin.tile);
      if(!tile||!Array.isArray(tile.origin)||!Array.isArray(tile.roads?.[pin.road]))
        throw Error('Missing pinned survey-limit road '+pin.tile+'/'+pin.road);
      const points=tile.roads[pin.road];
      if(points.length<2||!same(points[points.length-1],pin.local)||
         !same([pin.local[0]+tile.origin[0],pin.local[1]+tile.origin[1]],pin.world))
        throw Error('V123 survey-limit geometry changed; do not invent a continuation');
      const key=atlas.network.key(pin.tile,pin.local);
      const node=atlas.network.graph.get(key);
      if(!node||node.id!==pin.tile||!same(node.world,pin.world)||
         node.edges.length!==1||node.edges[0].kind!=='painted-road')
        throw Error('Survey limit is no longer a terminal road vertex; review graph');
      return Object.freeze({tile:pin.tile,road:pin.road,name:pin.name,
        world:Object.freeze(pin.world.slice()),nodeKey:key,degree:1,
        status:'charted-graph-ends-here',onwardRoadVerified:false,
        physicalBarrierClaimed:false,historic1780Certified:false});
    });
    return Object.freeze({version:152,markers:Object.freeze(markers),
      gameGraphChanged:false,unverifiedContinuationsDrawn:false,
      onwardNavigationApproved:false,physicalIPhoneApproved:false,
      productionApproved:false});
  }
  function paint(ctx,scale,report,showLabels=false){
    if(!report||report.version!==152||report.markers?.length!==2||
       report.productionApproved!==false||report.onwardNavigationApproved!==false||
       !Number.isFinite(scale)||scale<=0)
      throw Error('Cannot paint unverified survey limits without validated report/scale');
    for(const m of report.markers){
      ctx.save();ctx.translate(m.world[0],m.world[1]);
      ctx.scale(1/scale,1/scale); // icon remains readable at phone zoom
      ctx.beginPath();ctx.arc(0,0,11,0,Math.PI*2);
      ctx.fillStyle='#182b26';ctx.fill();ctx.strokeStyle='#f3d38a';
      ctx.lineWidth=2;ctx.stroke();
      ctx.fillStyle='#f6e4b2';ctx.font='bold 16px sans-serif';
      ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('?',0,1);
      if(showLabels){
        ctx.font='600 11px sans-serif';ctx.textAlign='left';
        ctx.fillStyle='#14251fe8';ctx.fillRect(16,-10,133,22);
        ctx.fillStyle='#f3d38a';ctx.fillText('UNSURVEYED EXIT',21,2);
      }
      ctx.restore();
    }
  }
  return {inspect,paint};
});
