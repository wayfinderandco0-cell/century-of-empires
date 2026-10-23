/* V123 three-tile route geometry.
 * Extends V121 exits to exact octagon borders; all NEW strokes in the preview
 * use these same coordinates for painting AND movement. No campaign changes.
 * Test and preview only: physical art and historical mapping not certified.
 */
(function(root,factory){
 const api=factory(typeof module!=='undefined'&&module.exports?require('./v122-seam-engine.js'):root.V122Seam);
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 else root.V123Atlas=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(seams){
 'use strict';
 const SIZE=[1536,1024],CORNER=256;
 const copy=o=>JSON.parse(JSON.stringify(o));
 const westRoad=[[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],[980,515],[890,535],[784,551],[680,560],[570,540],[470,520],[370,522],[275,550]];
 const southRoad=[[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],[700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]];
 function create(centerRoads,opt={}){
  if(!centerRoads||!centerRoads.west||!centerRoads.south||!centerRoads.bridge)throw Error('Missing V121 primary painted road data');
  const middle=copy(centerRoads);
  if(middle.west[0][0]!==99||middle.west[0][1]!==478||middle.south.at(-1)[0]!==466||middle.south.at(-1)[1]!==958)throw Error('V121 coordinates drifted: stop, review the art');
  // New paint strokes have EXACT same coordinates as the appended road graph.
  middle.west.unshift([0,478]);
  middle.south.push([466,1024]);
  const engineering=opt.experimentalSeams===true;
  const tiles=[
   {id:'west',name:'Western pass',origin:[0,0],width:SIZE[0],height:SIZE[1],corner:CORNER,roads:{east:copy(westRoad)},artReviewed:engineering},
   {id:'matrei',name:'Matrei',origin:[1536,0],width:SIZE[0],height:SIZE[1],corner:CORNER,roads:middle,artReviewed:engineering},
   {id:'south',name:'Southern valley',origin:[1536,1024],width:SIZE[0],height:SIZE[1],corner:CORNER,roads:{north:copy(southRoad)},artReviewed:engineering}
  ];
  const links=[
   {id:'west-matrei',from:{tile:'matrei',road:'west',end:'start'},to:{tile:'west',road:'east',end:'start'},bothRoadsVisuallyVerified:engineering,enabled:engineering},
   {id:'matrei-south',from:{tile:'matrei',road:'south',end:'end'},to:{tile:'south',road:'north',end:'start'},bothRoadsVisuallyVerified:engineering,enabled:engineering}
  ];
  return {version:123,tiles,links,network:seams.buildNetwork({tiles,links}),experimentalSeams:engineering,productionApproved:false,physicalIPhoneApproved:false,neighborArtFinal:false};
 }
 function endpoints(a){
  const network=a.network;
  return {
   west:network.key('west',westRoad.at(-1)),
   matrei:network.key('matrei',[518,519]),
   south:network.key('south',southRoad.at(-1)),
   bridge:network.key('matrei',[813,486])
  };
 }
 return {create,endpoints,SIZE};
});