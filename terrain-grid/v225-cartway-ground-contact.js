/* V225 opt-in terrain ground contact along IMMUTABLE V123 cartways.
 * The existing road graph supplies EVERY point. No extrapolation, no bank
 * survey, no new traversability, no claim of 1780 Austrian geography.
 * Source photography remains attributed to V224; human art gate remains RED.
 */
(function(){
 'use strict';
 const CELL=new Set(['west','south']);
 let last=Object.freeze({cells:[],roads:0,segments:0,painted:false,
   sourceRegisteredToV123:false,bridgeBanksVerified:false,productionApproved:false});
 function stroke(ctx,pts,width,color,blur){
   ctx.save();
   if(blur)ctx.filter='blur('+blur+'px)';
   ctx.beginPath();
   pts.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));
   ctx.lineCap='round';ctx.lineJoin='round';ctx.lineWidth=width;
   ctx.strokeStyle=color;ctx.stroke();ctx.restore();
 }
 function paint(ctx,atlas){
   if(!atlas||!Array.isArray(atlas.tiles))throw Error('V225 missing V123 atlas');
   const cells=[];let roads=0,segments=0;
   for(const tile of atlas.tiles){
     if(!CELL.has(tile.id))continue;
     if(!Array.isArray(tile.origin)||tile.origin.length!==2)throw Error('V225 missing tile origin');
     let count=0;
     ctx.save();ctx.translate(tile.origin[0],tile.origin[1]);
     for(const pts of Object.values(tile.roads||{})){
       if(!Array.isArray(pts)||pts.length<2)continue;
       if(!pts.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)))
         throw Error('V225 invalid original road coordinates');
       // Broad irregular-looking canopy shadow is covered by graded earth.
       // These are *visual* verge bands centered exactly on the original path,
       // NOT new movement lanes or guessed bank/crossing geometry.
       stroke(ctx,pts,76,'rgba(21,32,24,.69)',12);
       stroke(ctx,pts,63,'rgba(46,54,37,.87)',7);
       stroke(ctx,pts,49,tile.id==='west'?'rgba(83,83,64,.93)':'rgba(99,101,69,.93)',4);
       stroke(ctx,pts,37,tile.id==='west'?'rgba(116,107,80,.94)':'rgba(124,117,83,.94)',2);
       // The pre-existing V194 22px cartway is drawn afterwards by the
       // unchanged renderer. A graded shoulder beneath it masks the false
       // illusion of a narrow line hovering over intact tall-tree crowns.
       roads++;segments+=pts.length-1;count++;
     }
     ctx.restore();
     cells.push({tile:tile.id,roads:count});
   }
   if(cells.length!==2||cells.some(c=>c.roads<1)||segments<4)
     throw Error('V225 incomplete two-cell cartway grounding');
   last=Object.freeze({cells,roads,segments,painted:true,
     sourceRegisteredToV123:false,bridgeBanksVerified:false,productionApproved:false});
   return last;
 }
 window.V225GroundContact=Object.freeze({paint,get report(){return last}});
})();
