/* V160: low-frequency edge-color harmonization of the V121 Matrei painting
 * against the V137 *illustrative* neighboring underlay. This never moves,
 * duplicates, or edits the V121 painting, route graph, bridge, or buildings.
 * A tonal match cannot establish geographic or historical accuracy.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 else root.V160SeamTone=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 const rgb=(pixels,width,height,x,y,radius,filter)=>{
   let sum=[0,0,0],n=0;
   const ix=Math.round(x),iy=Math.round(y);
   for(let dy=-radius;dy<=radius;dy+=2)for(let dx=-radius;dx<=radius;dx+=2){
     const px=ix+dx,py=iy+dy;
     if(px<0||py<0||px>=width||py>=height)continue;
     const i=(py*width+px)*4,r=pixels[i],g=pixels[i+1],b=pixels[i+2];
     if(filter&&(r>g*1.28&&r>b*1.35||b>r*1.17&&g>r*1.15||
       r>220&&g>220&&b>220))continue;
     sum[0]+=r;sum[1]+=g;sum[2]+=b;n++;
   }
   return n>=3?sum.map(v=>v/n):null;
 };
 function harmonize({background,bgWidth,bgHeight,photo,photoWidth,photoHeight,
                     bounds,photoOrigin,polygon,inset=285,fadeRadius=470,maxShift=44}){
   if(!(background instanceof Uint8ClampedArray)||!(photo instanceof Uint8ClampedArray)||
      background.length!==bgWidth*bgHeight*4||photo.length!==photoWidth*photoHeight*4||
      ![bgWidth,bgHeight,photoWidth,photoHeight].every(v=>Number.isInteger(v)&&v>8)||
      !Array.isArray(bounds)||bounds.length!==4||!Array.isArray(photoOrigin)||photoOrigin.length!==2||
      !Array.isArray(polygon)||polygon.length!==8||
      ![...bounds,...photoOrigin,inset,fadeRadius,maxShift].every(Number.isFinite)||
      bounds[2]<=0||bounds[3]<=0||inset<=0||fadeRadius<=0||maxShift<=0||maxShift>60||
      polygon.some(p=>!Array.isArray(p)||p.length!==2||!p.every(Number.isFinite)))
     throw Error('V160 requires reviewed RGBA, geographic-frame labels and finite polygon');
   const toBg=p=>[(p[0]+photoOrigin[0]-bounds[0])/bounds[2]*bgWidth,
                   (p[1]+photoOrigin[1]-bounds[1])/bounds[3]*bgHeight];
   const edges=[];
   for(let i=0;i<polygon.length;i++){
     const a=polygon[i],b=polygon[(i+1)%polygon.length],dx=b[0]-a[0],dy=b[1]-a[1],len=Math.hypot(dx,dy);
     if(len<1)throw Error('Degenerate V160 polygon edge');
     const inward=[-dy/len,dx/len],anchors=[];
     for(const t of [.15,.35,.5,.65,.85]){
       const border=[a[0]+dx*t,a[1]+dy*t];
       const inside=[border[0]+inward[0]*inset,border[1]+inward[1]*inset];
       const target=rgb(photo,photoWidth,photoHeight,inside[0],inside[1],11,true);
       const bg=toBg(inside),base=rgb(background,bgWidth,bgHeight,bg[0],bg[1],3,false);
       if(!target||!base)continue;
       anchors.push({t,delta:target.map((v,k)=>clamp(v-base[k],-maxShift,maxShift)),target,border});
     }
     if(anchors.length)edges.push({a,b,dx,dy,len2:len*len,anchors});
   }
   if(edges.length<5)throw Error('V160 insufficient natural-source color anchors; refuse artificial match');
   let changed=0,accShift=0;
   for(let y=0;y<bgHeight;y++){
     const wy=bounds[1]+(y+.5)*bounds[3]/bgHeight-photoOrigin[1];
     for(let x=0;x<bgWidth;x++){
       const wx=bounds[0]+(x+.5)*bounds[2]/bgWidth-photoOrigin[0];
       let best=Infinity,selected=null,position=0;
       for(const edge of edges){
         const t=clamp(((wx-edge.a[0])*edge.dx+(wy-edge.a[1])*edge.dy)/edge.len2,0,1);
         const d=Math.hypot(wx-edge.a[0]-t*edge.dx,wy-edge.a[1]-t*edge.dy);
         if(d<best){best=d;selected=edge;position=t;}
       }
       if(best>=fadeRadius)continue;
       const a=selected.anchors;
       let left=a[0],right=a[a.length-1];
       for(let k=1;k<a.length;k++)if(position<=a[k].t){left=a[k-1];right=a[k];break;}
       const mix=left===right?0:clamp((position-left.t)/(right.t-left.t),0,1);
       const q=1-best/fadeRadius,weight=q*q*(3-2*q)*.88;
       const offset=(y*bgWidth+x)*4;
       for(let c=0;c<3;c++){
         const shift=(left.delta[c]*(1-mix)+right.delta[c]*mix)*weight;
         background[offset+c]=clamp(Math.round(background[offset+c]+shift),0,255);
         accShift+=Math.abs(shift);
       }
       changed++;
     }
   }
   return Object.freeze({version:160,anchors:edges.reduce((n,e)=>n+e.anchors.length,0),
     edgesWithEvidence:edges.length,changedBackgroundPixels:changed,
     meanAbsoluteChannelShift:changed?+(accShift/(changed*3)).toFixed(4):0,
     photoModified:false,roadsModified:false,sourceGeoregistered:false,
     bridgeBanksVerified:false,periodArtComplete:false,productionApproved:false});
 }
 return Object.freeze({harmonize});
});
