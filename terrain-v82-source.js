/* V82 procedural atlas overlay: realistic relief belts and woodland stands. */
function refineAtlasImage(photo){
 const w=1448,h=1086,canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
 const ctx=canvas.getContext('2d',{willReadFrequently:true});if(!ctx)throw Error('Canvas not available');
 ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
 ctx.drawImage(photo,0,0,w,h);
 const im=ctx.getImageData(0,0,w,h),d=im.data;
 let seed=0x1953c4ab;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){
  const i=(y*w+x)*4,r=d[i],g=d[i+1],b=d[i+2];
  seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;
  const grain=((seed>>>24)-128)/31;
  const wave=(Math.sin(x*.23+y*.08)+Math.sin(y*.37-x*.045))*.65;
  const water=b>r*1.20&&b>g*1.10&&b>49;
  if(water){
   const shade=Math.max(-16,Math.min(20,(b-100)*.10));
   d[i]=22+shade*.35+grain*.6;
   d[i+1]=71+shade*.55+grain*.7+wave;
   d[i+2]=91+shade*.68+grain*.8+wave;
  }else{
   const lum=.28*r+.56*g+.16*b,shadow=(lum-159)*.45;
   d[i]=177+shadow+(r-g)*.12+grain*1.2;
   d[i+1]=170+shadow+(g-b)*.12+grain*1.2;
   d[i+2]=137+shadow+(b-r)*.055+grain;
  }
  d[i+3]=255;
 }
 ctx.putImageData(im,0,0);
 return canvas.toDataURL('image/webp',.90);
}
function drawAtlasTerrain(){
 const parent=$('terrainDetail');parent.replaceChildren();
 const major=node('g',{class:'terrain-major'}),fine=node('g',{class:'terrain-fine'});
 const ridges=[
  [[370,105],[390,160],[410,205]],
  [[785,155],[830,204],[878,243]],
  [[290,654],[349,654],[424,647],[473,634]],
  [[615,532],[671,515],[727,523],[782,514],[845,521],[915,534],[984,564]],
  [[817,602],[823,648],[839,684],[845,730]],
  [[1049,526],[1109,542],[1155,579],[1215,596]],
  [[1083,680],[1160,674],[1208,702]],
  [[301,713],[355,740],[418,717]],
  [[130,930],[242,940],[358,957],[470,946],[575,966]]
 ];
 const ridgeShadows=[],ridgeCores=[],ridgeLights=[],contours=[],hachures=[];
 let randState=0x51c2a;
 const rand=()=>{randState=(Math.imul(randState,1664525)+1013904223)>>>0;return randState/4294967296};
 const fx=n=>n.toFixed(1);
 for(const points of ridges){
  const line='M'+points.map(p=>fx(p[0])+' '+fx(p[1])).join('L');
  ridgeShadows.push(line);ridgeCores.push(line);ridgeLights.push(line);
  for(let seg=0;seg<points.length-1;seg++){
   const a=points[seg],b=points[seg+1],dx=b[0]-a[0],dy=b[1]-a[1],len=Math.hypot(dx,dy)||1,px=-dy/len,py=dx/len;
   const n=Math.ceil(len/11);
   for(let j=0;j<n;j++){
    const t=(j+.5)/n,ox=(rand()-.5)*8,oy=(rand()-.5)*8;
    const x=a[0]+dx*t+ox,y=a[1]+dy*t+oy;
    for(let z=0;z<3;z++){
     const side=z===1?-1:1,spread=(z+1)*3+(rand()-.5)*2;
     const xx=x+px*spread*side,yy=y+py*spread*side;
     const cx=xx+(rand()-.5)*5,cy=yy+(rand()-.5)*5;
     contours.push('M'+fx(xx-6)+' '+fx(yy+4)+'Q'+fx(cx)+' '+fx(cy-7-spread*.21)+' '+fx(xx+8)+' '+fx(yy+3));
    }
    for(let q=0;q<4;q++){
     const along=(rand()-.5)*15,spread=(rand()-.5)*21;
     const xx=x+dx/len*along+px*spread,yy=y+dy/len*along+py*spread;
     hachures.push('M'+fx(xx)+' '+fx(yy)+'l'+fx(px*(3+rand()*5))+' '+fx(py*(3+rand()*5)));
    }
   }
  }
 }
 for(const [cls,arr] of [['ridge-shadow',ridgeShadows],['ridge-core',ridgeCores],['ridge-light',ridgeLights],
   ['terrain-contours',contours],['terrain-hatching',hachures]]){
  major.appendChild(node('path',{class:cls,d:arr.join(' '),fill:'none','stroke-linecap':'round','stroke-linejoin':'round'}));
 }
 const forests=[
  [442,361,75,35],[494,466,70,51],[613,436,46,34],[812,331,57,40],
  [872,292,74,52],[990,310,81,51],[1153,320,60,58],[1240,451,88,76],
  [1391,433,51,100],[750,176,59,88],[914,152,87,64],[1115,177,65,75],
  [1021,564,56,37],[593,496,46,35],[372,542,43,27],[336,739,55,38],
  [616,718,41,55],[1121,598,56,43]
 ];
 const canopy=[],trunks=[],canopyFine=[];
 for(const [cx,cy,rx,ry] of forests){
  const count=Math.ceil(rx*ry/48);
  for(let j=0;j<count;j++){
   const ang=rand()*Math.PI*2,d=Math.sqrt(rand()),x=cx+Math.cos(ang)*rx*d,y=cy+Math.sin(ang)*ry*d;
   if(Math.sin(x*.099+y*.041)*Math.cos(y*.075-x*.057)>.42)continue;
   const w=1.4+rand()*1.8,h=2.6+rand()*2.8;
   canopy.push('M'+fx(x-w)+' '+fx(y+h*.4)+'Q'+fx(x-w*.55)+' '+fx(y-h*.55)+' '+fx(x)+' '+fx(y-h)+
    'Q'+fx(x+w*.6)+' '+fx(y-h*.45)+' '+fx(x+w)+' '+fx(y+h*.4));
   trunks.push('M'+fx(x)+' '+fx(y-h*.22)+'l0 '+fx(h*.94));
   if(rand()>.4)canopyFine.push('M'+fx(x-w*.5)+' '+fx(y-h*.1)+'Q'+fx(x)+' '+fx(y-h*1.3)+' '+fx(x+w*.5)+' '+fx(y-h*.05));
  }
 }
 major.appendChild(node('path',{class:'terrain-canopy',d:canopy.join(' ')}));
 major.appendChild(node('path',{class:'terrain-trunks',d:trunks.join(' ')}));
 fine.appendChild(node('path',{class:'terrain-canopy',d:canopyFine.join(' '),stroke:'#203e2b','stroke-opacity':'.82'}));
 const fields=[[484,451,65,31],[706,419,71,28],[995,418,79,27],[1171,444,58,48],[364,691,51,30],[235,733,50,47]];
 const engraving=[];
 for(const [cx,cy,rx,ry] of fields)for(let i=0;i<130;i++){
  const x=cx+(rand()-.5)*rx*2,y=cy+(rand()-.5)*ry*2;
  engraving.push('M'+fx(x)+' '+fx(y)+'l'+fx(1.3+rand()*2.4)+' '+fx(-.6-rand()));
 }
 fine.appendChild(node('path',{class:'terrain-hatching',d:engraving.join(' '),stroke:'#897d55','stroke-opacity':'.31'}));
 parent.appendChild(major);parent.appendChild(fine);
}