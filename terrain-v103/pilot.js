/* Century of Empires V103. Improved conifer LOD, accurate overlays, isolated visual pilot; no save access.
   Geographic inputs: EPSG:4326. Local rendering: east, elevation, south in km.
   One coordinate transform is shared by terrain, foliage, water, path and picking. */
(()=>{'use strict';
const $=id=>document.getElementById(id),canvas=$('terrain');
const gl=canvas.getContext('webgl',{alpha:false,antialias:true,powerPreference:'default',preserveDrawingBuffer:true});
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),mix=(a,b,t)=>a+(b-a)*t;
const nextFrame=()=>new Promise(requestAnimationFrame),start=performance.now();
let meta,heights,treeData,features,ground=[],ribbons=[],trees,baseTexture,detailTexture;
const meshCols=320, meshRows=480;let meshSurface;
let W=1,H=1,DPR=1,VP,INV,lastFrame=0,dirty=true,animating=false,ready=false,drawCount=0;
const camera={x:0,z:-.12,span:6.8,pitch:.90,yaw:-.16};
let target={...camera};const spans=[54,26,12,6.8];
const errors=[];window.addEventListener('error',e=>errors.push(e.message));
const metrics={version:103,ready:false,frames:0,maxFrameMs:0,loads:[],errors};
const m4={
 multiply(a,b){let o=new Float32Array(16);for(let i=0;i<4;i++)for(let j=0;j<4;j++)for(let k=0;k<4;k++)o[i*4+j]+=a[k*4+j]*b[i*4+k];return o;},
 ortho(l,r,b,t,n,f){return new Float32Array([2/(r-l),0,0,0,0,2/(t-b),0,0,0,0,-2/(f-n),0,-(r+l)/(r-l),-(t+b)/(t-b),-(f+n)/(f-n),1]);},
 lookAt(eye,at){let z=norm(eye.map((v,i)=>v-at[i])),x=norm([z[2],0,-z[0]]),y=[z[1]*x[2]-z[2]*x[1],z[2]*x[0]-z[0]*x[2],z[0]*x[1]-z[1]*x[0]];return new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,eye),-dot(y,eye),-dot(z,eye),1]);},
 inverse(a){let out=new Float32Array(16),m=Array.from({length:4},(_,r)=>[...Array.from({length:4},(_,c)=>a[c*4+r]),...Array.from({length:4},(_,c)=>r===c?1:0)]);for(let i=0;i<4;i++){let p=i;for(let r=i+1;r<4;r++)if(Math.abs(m[r][i])>Math.abs(m[p][i]))p=r;[m[i],m[p]]=[m[p],m[i]];let v=m[i][i];for(let j=0;j<8;j++)m[i][j]/=v;for(let r=0;r<4;r++)if(r!==i){let q=m[r][i];for(let j=0;j<8;j++)m[r][j]-=q*m[i][j];}}for(let r=0;r<4;r++)for(let c=0;c<4;c++)out[c*4+r]=m[r][c+4];return out;}
};
function dot(a,b){return a.reduce((s,v,i)=>s+v*b[i],0)}
function norm(a){const d=Math.hypot(...a);return a.map(v=>v/d)}
function transform(m,p){const q=[...p,1],o=[0,0,0,0];for(let r=0;r<4;r++)for(let c=0;c<4;c++)o[r]+=m[c*4+r]*q[c];return o.slice(0,3).map(v=>v/o[3]);}
function toLocal(lon,lat,h=0){return [(lon-meta.originLonLat[0])*meta.metersPerDegree[0]/1000,h/1000,(meta.originLonLat[1]-lat)*meta.metersPerDegree[1]/1000]}
function toGeo(x,z){return [meta.originLonLat[0]+x*1000/meta.metersPerDegree[0],meta.originLonLat[1]-z*1000/meta.metersPerDegree[1]]}
function elevation(lon,lat){const [w,s,e,n]=meta.broadBoundsLonLat,[nx,ny]=meta.broadGrid;const u=clamp((lon-w)/(e-w)*(nx-1),0,nx-1.0001),v=clamp((n-lat)/(n-s)*(ny-1),0,ny-1.0001),i=Math.floor(u),j=Math.floor(v),k=j*nx+i;return mix(mix(heights[k],heights[k+1],u-i),mix(heights[k+nx],heights[k+nx+1],u-i),v-j);}
function localHeight(x,z){return elevation(...toGeo(x,z))/1000;}
function compile(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
function program(v,f){const p=gl.createProgram();gl.attachShader(p,compile(gl.VERTEX_SHADER,v));gl.attachShader(p,compile(gl.FRAGMENT_SHADER,f));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));return p;}
const groundVS=`attribute vec3 aPosition;attribute vec3 aNormal;uniform mat4 uVP;varying vec3 vNormal;varying vec3 vWorld;void main(){vWorld=aPosition;vNormal=aNormal;gl_Position=uVP*vec4(aPosition,1.);}`;
const groundFS=`precision highp float;uniform sampler2D uBase;uniform sampler2D uDetail;uniform vec4 uBounds;uniform vec4 uDetailBounds;uniform vec3 uFocus;uniform float uSpan;varying vec3 vNormal;varying vec3 vWorld;
 void main(){vec2 p=vWorld.xz;vec2 uv=(p-uBounds.xy)/uBounds.zw;vec3 base=texture2D(uBase,uv).rgb;vec2 dt=(p-uDetailBounds.xy)/uDetailBounds.zw;float edge=min(min(dt.x,1.-dt.x),min(dt.y,1.-dt.y));float blend=smoothstep(0.,.09,edge);vec3 color=mix(base,texture2D(uDetail,clamp(dt,0.,1.)).rgb,blend);vec3 N=normalize(vNormal);float sun=max(0.,dot(N,normalize(vec3(-.6,.72,-.45))));float shade=.52+.65*sun;float sky=.03*(1.-N.y);color=color*shade+vec3(.03,.042,.047)*sky;float distant=smoothstep(3.8,16.,distance(vWorld.xz,uFocus.xz))*.20;distant*=1.-smoothstep(15.,50.,uSpan);color=mix(color,vec3(.53,.61,.57),distant);gl_FragColor=vec4(color,1.);}`;
const lineVS=`attribute vec3 aPosition;attribute vec3 aColor;uniform mat4 uVP;varying vec3 vColor;void main(){vColor=aColor;gl_Position=uVP*vec4(aPosition,1.);}`;
const lineFS=`precision mediump float;varying vec3 vColor;void main(){gl_FragColor=vec4(vColor,1.);}`;
const treeVS=`attribute vec3 aPosition;attribute float aSize;attribute float aSeed;uniform mat4 uVP;uniform float uPixels;uniform float uFade;varying float vSeed;varying float vFade;void main(){vSeed=aSeed;vFade=uFade;gl_Position=uVP*vec4(aPosition+vec3(0.,aSize*.00033,0.),1.);gl_PointSize=clamp(aSize*.001*uPixels*2.05,1.,76.);}`;
const treeFS=`precision highp float;varying float vSeed;varying float vFade;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7))+vSeed*67.)*43758.5453);}
void main(){
 vec2 p=(gl_PointCoord-vec2(.5))*2.;p.x*=1.08;
 // A tapered, layered Alpine conifer crown. V102's round discs read as bushes.
 float yy=(p.y+.94)/1.92;
 if(yy<0.||yy>1.)discard;
 float whorl=floor(yy*4.2);
 float ledge=.055*sin(yy*29.+vSeed*12.)+.05*sin(yy*53.+vSeed*39.);
 float branch=(1.-yy)*(.85+.09*sin(whorl*2.5+vSeed*20.))+ledge;
 float needles=.055*sin(atan(p.y,p.x)*17.+yy*32.+vSeed*64.);
 float twig=.023*(hash(floor(gl_PointCoord*34.))-0.5);
 if(abs(p.x)>max(.035,branch+needles+twig))discard;
 float mid=clamp(1.-abs(p.x)/max(branch,.04),0.,1.);
 float needle=hash(floor(gl_PointCoord*38.))*.19;
 float facet=.13*sin(yy*43.+vSeed*22.)+.08*sin(p.x*32.+yy*15.);
 float light=clamp(.78-.28*p.x+.14*mid+.14*yy+facet+needle,.44,1.22);
 vec3 pine=mix(vec3(.085,.20,.13),vec3(.22,.34,.20),fract(vSeed*7.13));
 pine=mix(pine,vec3(.33,.37,.22),smoothstep(.68,1.,yy)*.2);
 gl_FragColor=vec4(pine*light,vFade);
}`;
let gp,lp,tp;
function uniform(p,n){return gl.getUniformLocation(p,n)}
function buffer(a){const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(a),gl.STATIC_DRAW);return b;}
function attrib(p,name,b,size,stride=0,offset=0){const loc=gl.getAttribLocation(p,name);if(loc<0)return;gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,size,gl.FLOAT,false,stride,offset);}
async function fetchAsset(path,type='json'){const r=await fetch('terrain-v102/'+path);if(!r.ok)throw Error(path+' could not load ('+r.status+')');metrics.loads.push(path);return type==='bin'?new Float32Array(await r.arrayBuffer()):r.json();}
async function texture(path){const im=new Image();im.src='terrain-v102/'+path;await im.decode();const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,im);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);const pot=(im.width&(im.width-1))===0&&(im.height&(im.height-1))===0;gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,pot?gl.LINEAR_MIPMAP_LINEAR:gl.LINEAR);if(pot)gl.generateMipmap(gl.TEXTURE_2D);const ext=gl.getExtension('EXT_texture_filter_anisotropic')||gl.getExtension('WEBKIT_EXT_texture_filter_anisotropic');if(ext)gl.texParameterf(gl.TEXTURE_2D,ext.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(4,gl.getParameter(ext.MAX_TEXTURE_MAX_ANISOTROPY_EXT)));return t;}
async function buildGround(){
 const [w,s,e,n]=meta.broadBoundsLonLat,nx=meshCols,ny=meshRows;meshSurface=new Float32Array((nx+1)*(ny+1));
 for(let j0=0;j0<ny;j0+=24){const positions=[],normals=[],indices=[],rows=Math.min(24,ny-j0);
  for(let j=0;j<=rows;j++)for(let i=0;i<=nx;i++){
   const lon=mix(w,e,i/nx),lat=mix(n,s,(j0+j)/ny),p=toLocal(lon,lat,elevation(lon,lat));positions.push(...p);meshSurface[(j0+j)*(nx+1)+i]=p[1];
   const dx=(localHeight(p[0]+.04,p[2])-localHeight(p[0]-.04,p[2]))/.08,dz=(localHeight(p[0],p[2]+.04)-localHeight(p[0],p[2]-.04))/.08;normals.push(...norm([-dx,1,-dz]));
  }
  for(let j=0;j<rows;j++)for(let i=0;i<nx;i++){const a=j*(nx+1)+i,b=a+nx+1;indices.push(a,b,a+1,a+1,b,b+1);}
  const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(indices),gl.STATIC_DRAW);ground.push({p:buffer(positions),n:buffer(normals),i:ib,count:indices.length});
  await nextFrame();
 }
}
function buildTrees(){const a=[];for(let i=0;i<treeData.length;i+=5){const lon=treeData[i],lat=treeData[i+1];a.push(...toLocal(lon,lat,elevation(lon,lat)),treeData[i+3],treeData[i+4]);}trees={b:buffer(a),count:a.length/5};}
// Match the *rendered triangular mesh*, rather than the smoother DEM, to avoid rivers sinking into terrain.
function renderedHeight(x,z){
 const [w,s,e,n]=meta.broadBoundsLonLat,[lon,lat]=toGeo(x,z);
 const u=clamp((lon-w)/(e-w)*meshCols,0,meshCols-0.00001),v=clamp((n-lat)/(n-s)*meshRows,0,meshRows-0.00001);
 const i=Math.floor(u),j=Math.floor(v),fu=u-i,fv=v-j,k=j*(meshCols+1)+i;
 const a=meshSurface[k],b=meshSurface[k+1],c=meshSurface[k+meshCols+1],d=meshSurface[k+meshCols+2];
 return fu+fv<=1?a+fu*(b-a)+fv*(c-a):d+(1-fu)*(c-d)+(1-fv)*(b-d);
}
function ribbon(coords,width,color,lift){const pts=[];for(let i=1;i<coords.length;i++){let p=toLocal(...coords[i-1]),q=toLocal(...coords[i]),dist=Math.hypot(q[0]-p[0],q[2]-p[2]),steps=Math.max(1,Math.ceil(dist/.012));for(let j=0;j<steps;j++)pts.push([mix(p[0],q[0],j/steps),mix(p[2],q[2],j/steps)]);}const end=toLocal(...coords[coords.length-1]);pts.push([end[0],end[2]]);const a=[];
 for(let i=1;i<pts.length;i++){let p=pts[i-1],q=pts[i],dx=q[0]-p[0],dz=q[1]-p[1],len=Math.hypot(dx,dz)||1,ox=-dz/len*width/2000,oz=dx/len*width/2000;const v=[[p[0]+ox,p[1]+oz],[p[0]-ox,p[1]-oz],[q[0]+ox,q[1]+oz],[q[0]-ox,q[1]-oz]];for(const k of [0,1,2,2,1,3]){const [x,z]=v[k];a.push(x,renderedHeight(x,z)+lift,z,...color);}}
 return{b:buffer(a),count:a.length/6};
}
function buildFeatures(){
 for(const f of features.waterways){const major=f.type==='river';
  ribbons.push(ribbon(f.coords,major?18:8,[.30,.38,.31],.008));
  ribbons.push(ribbon(f.coords,major?10:4,[.39,.57,.59],.010));
  if(major)ribbons.push(ribbon(f.coords,1.8,[.60,.72,.70],.012));}
 // Narrow, weathered pack trail rather than a clean modern road.
 ribbons.push(ribbon(features.trail.coords,8,[.32,.32,.24],.011));
 ribbons.push(ribbon(features.trail.coords,3.8,[.58,.49,.33],.013));
}
function geographicBounds(b){const p=toLocal(b[0],b[3]),q=toLocal(b[2],b[1]);return[p[0],p[2],q[0]-p[0],q[2]-p[2]];}
function viewport(){const r=canvas.getBoundingClientRect();W=r.width;H=r.height;DPR=Math.min(window.devicePixelRatio||1,2);canvas.width=Math.round(W*DPR);canvas.height=Math.round(H*DPR);gl.viewport(0,0,canvas.width,canvas.height);dirty=true;requestDraw();}
function matrices(){let span=camera.span*(W>H?.70:1),aspect=W/H;const cy=localHeight(camera.x,camera.z),at=[camera.x,cy,camera.z],distance=60,cs=Math.cos(camera.pitch),eye=[at[0]+Math.sin(camera.yaw)*cs*distance,cy+Math.sin(camera.pitch)*distance,at[2]+Math.cos(camera.yaw)*cs*distance];VP=m4.multiply(m4.ortho(-span*aspect/2,span*aspect/2,-span/2,span/2,.1,160),m4.lookAt(eye,at));INV=m4.inverse(VP);return{span,at};}
function draw(){if(!ready)return;const t=performance.now();const {span,at}=matrices();gl.enable(gl.DEPTH_TEST);gl.disable(gl.BLEND);gl.clearColor(.40,.49,.44,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
 gl.useProgram(gp);gl.uniformMatrix4fv(uniform(gp,'uVP'),false,VP);gl.uniform4fv(uniform(gp,'uBounds'),geographicBounds(meta.broadBoundsLonLat));gl.uniform4fv(uniform(gp,'uDetailBounds'),geographicBounds(meta.boundsLonLat));gl.uniform3fv(uniform(gp,'uFocus'),at);gl.uniform1f(uniform(gp,'uSpan'),camera.span);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,baseTexture);gl.uniform1i(uniform(gp,'uBase'),0);gl.activeTexture(gl.TEXTURE1);gl.bindTexture(gl.TEXTURE_2D,detailTexture);gl.uniform1i(uniform(gp,'uDetail'),1);
 for(const tile of ground){attrib(gp,'aPosition',tile.p,3);attrib(gp,'aNormal',tile.n,3);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,tile.i);gl.drawElements(gl.TRIANGLES,tile.count,gl.UNSIGNED_SHORT,0);}
 if(camera.span<31){gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(-2,-3);gl.useProgram(lp);gl.uniformMatrix4fv(uniform(lp,'uVP'),false,VP);for(const r of ribbons){attrib(lp,'aPosition',r.b,3,24,0);attrib(lp,'aColor',r.b,3,24,12);gl.drawArrays(gl.TRIANGLES,0,r.count);}gl.disable(gl.POLYGON_OFFSET_FILL);}
 if(camera.span<11.5){gl.useProgram(tp);gl.uniformMatrix4fv(uniform(tp,'uVP'),false,VP);gl.uniform1f(uniform(tp,'uPixels'),H*DPR/span);gl.uniform1f(uniform(tp,'uFade'),clamp((11.5-camera.span)/4.0,0,1));gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);attrib(tp,'aPosition',trees.b,3,20,0);attrib(tp,'aSize',trees.b,1,20,12);attrib(tp,'aSeed',trees.b,1,20,16);gl.drawArrays(gl.POINTS,0,trees.count);gl.depthMask(true);gl.disable(gl.BLEND);}
 updateLabels();drawCount++;metrics.frames=drawCount;metrics.maxFrameMs=Math.max(metrics.maxFrameMs,performance.now()-t);dirty=false;
}
function requestDraw(){if(!animating){animating=true;requestAnimationFrame(frame);}}
function frame(now){animating=false;if(!ready)return;const dt=Math.min(50,now-lastFrame||16);lastFrame=now;let moving=false;for(const k of ['x','z','span','pitch','yaw']){const delta=target[k]-camera[k];if(Math.abs(delta)>.00003){camera[k]+=delta*(1-Math.exp(-dt/110));moving=true;}else camera[k]=target[k];}if(dirty||moving)draw();if(moving)requestDraw();}
function changeSpan(v){target.span=clamp(v,2.7,54);syncButtons();dirty=true;requestDraw();}
function syncButtons(){let best=0;for(let i=1;i<4;i++)if(Math.abs(target.span-spans[i])<Math.abs(target.span-spans[best]))best=i;for(const b of document.querySelectorAll('[data-level]'))b.classList.toggle('active',Number(b.dataset.level)===best);}
const labelDefs=[{text:'Navisbach',lon:11.522,lat:47.126,kind:'water'},{text:'Pack trail',lon:11.500,lat:47.125,kind:'path'},{text:'Alpine pastures',lon:11.533,lat:47.153,kind:'land'}];
function updateLabels(){const host=$('labels');if(!host.children.length)for(const l of labelDefs){const e=document.createElement('span');e.className='label '+l.kind;e.textContent=l.text;host.append(e);}labelDefs.forEach((l,i)=>{const p=transform(VP,toLocal(l.lon,l.lat,elevation(l.lon,l.lat)+30)),e=host.children[i],x=(p[0]+1)*W/2,y=(1-p[1])*H/2;e.style.left=x+'px';e.style.top=y+'px';e.hidden=camera.span>16||x<70||x>W-65||y<190||y>H-190;});const pxKm=H/(camera.span*(W>H?.70:1)),km=pxKm>140?.25:pxKm>75?.5:pxKm>35?1:5;$('scale').querySelector('i').style.width=Math.round(km*pxKm)+'px';$('scale').querySelector('b').textContent=km<1?km*1000+' m':km+' km';$('compass').querySelector('svg').style.transform='rotate('+(-camera.yaw*180/Math.PI)+'deg)';}
function screenToGeo(x,y){if(!INV)return null;const r=canvas.getBoundingClientRect(),sx=(x-r.left)/W*2-1,sy=1-(y-r.top)/H*2;const near=transform(INV,[sx,sy,-1]),far=transform(INV,[sx,sy,1]);let a=0,b=1;for(let i=0;i<25;i++){const t=(a+b)/2,p=near.map((v,j)=>mix(v,far[j],t));if(p[1]>localHeight(p[0],p[2]))a=t;else b=t;}const p=near.map((v,j)=>mix(v,far[j],(a+b)/2)),geo=toGeo(p[0],p[2]);if(geo[0]<meta.broadBoundsLonLat[0]||geo[0]>meta.broadBoundsLonLat[2]||geo[1]<meta.broadBoundsLonLat[1]||geo[1]>meta.broadBoundsLonLat[3])return null;return{lon:geo[0],lat:geo[1],elevation:elevation(...geo)};}
function inspect(x,y){const g=screenToGeo(x,y);if(!g)return;$('elevation').textContent=Math.round(g.elevation).toLocaleString()+' m elevation';$('coordinates').textContent=g.lat.toFixed(5)+'° N · '+g.lon.toFixed(5)+'° E';$('inspect').hidden=false;}
const pointers=new Map();let gesture=null,moved=false;
function startGesture(){const p=[...pointers.values()];if(!p.length){gesture=null;return;}gesture={x:p.reduce((s,q)=>s+q.x,0)/p.length,y:p.reduce((s,q)=>s+q.y,0)/p.length,d:p.length>1?Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y):0,cam:{...target}};}
canvas.addEventListener('pointerdown',e=>{if(!ready)return;canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});moved=false;startGesture();});
canvas.addEventListener('pointermove',e=>{if(!pointers.has(e.pointerId)||!gesture)return;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});const p=[...pointers.values()],x=p.reduce((s,q)=>s+q.x,0)/p.length,y=p.reduce((s,q)=>s+q.y,0)/p.length,dx=x-gesture.x,dy=y-gesture.y;if(Math.hypot(dx,dy)>4||p.length>1)moved=true;const scale=gesture.cam.span*(W>H?.70:1)/H,cy=Math.cos(camera.yaw),sy=Math.sin(camera.yaw);target.x=clamp(gesture.cam.x-dx*scale*cy-dy*scale*sy/Math.sin(camera.pitch),-8,10);target.z=clamp(gesture.cam.z+dx*scale*sy-dy*scale*cy/Math.sin(camera.pitch),-14,16);if(p.length>1&&gesture.d){const d=Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y);target.span=clamp(gesture.cam.span*gesture.d/Math.max(20,d),2.7,54);syncButtons();}dirty=true;requestDraw();});
canvas.addEventListener('pointerup',e=>{if(!moved&&pointers.size===1)inspect(e.clientX,e.clientY);pointers.delete(e.pointerId);startGesture();});
canvas.addEventListener('pointercancel',e=>{pointers.delete(e.pointerId);startGesture();});
// On iPhone, Safari's native gesture zoom can enlarge the entire game UI.
 // Confine two-finger movement to the WebGL camera; preserve ordinary browser text zoom elsewhere.
 const stopNativeGesture=e=>{if(e.cancelable)e.preventDefault();};
 for(const eventName of ['gesturestart','gesturechange','gestureend'])
   document.getElementById('app').addEventListener(eventName,stopNativeGesture,{passive:false});
 canvas.addEventListener('touchmove',e=>{if(e.touches.length>1&&e.cancelable)e.preventDefault();},{passive:false});
 canvas.addEventListener('dblclick',e=>{e.preventDefault();changeSpan(target.span*.8);});
 canvas.addEventListener('wheel',e=>{e.preventDefault();changeSpan(target.span*Math.exp(e.deltaY*.001));},{passive:false});
canvas.addEventListener('keydown',e=>{if(e.key==='+'||e.key==='=')changeSpan(target.span*.8);if(e.key==='-')changeSpan(target.span*1.25);if(e.key==='Escape')$('inspect').hidden=true;});
for(const b of document.querySelectorAll('[data-level]'))b.addEventListener('click',()=>{target.pitch=Number(b.dataset.level)<2?1.29:.90;changeSpan(spans[Number(b.dataset.level)]);});
$('zoomIn').onclick=()=>changeSpan(target.span*.78);$('zoomOut').onclick=()=>changeSpan(target.span/ .78);
$('home').onclick=()=>{target={x:0,z:-.12,span:6.8,pitch:.90,yaw:-.16};syncButtons();$('inspect').hidden=true;dirty=true;requestDraw();};
$('tilt').onclick=()=>{target.pitch=target.pitch>1.2?.90:1.49;dirty=true;requestDraw();};
$('info').onclick=()=>$('sources').showModal();$('closeInfo').onclick=()=>$('sources').close();$('closeInspect').onclick=()=>{$('inspect').hidden=true;};
window.addEventListener('resize',()=>{if(gl)viewport();});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();ready=false;$('loading').hidden=false;$('loading').textContent='The graphics view paused. Reload to restore the landscape.';});
window.terrainPilot={metrics,get camera(){return {...camera}},get target(){return {...target}},get meta(){return meta},geoToLocal:(lon,lat)=>toLocal(lon,lat,elevation(lon,lat)),localToGeo:toGeo,screenToGeo,goTo:(lon,lat,span=6.8)=>{const p=toLocal(lon,lat);target.x=p[0];target.z=p[2];changeSpan(span);},project:(lon,lat)=>{const p=transform(VP,toLocal(lon,lat,elevation(lon,lat)));return{x:(p[0]+1)*W/2,y:(1-p[1])*H/2};}};
async function boot(){if(!gl)throw Error('This browser cannot start WebGL. Please open this pilot in Safari with graphics enabled.');gp=program(groundVS,groundFS);lp=program(lineVS,lineFS);tp=program(treeVS,treeFS);[meta,heights,treeData,features,baseTexture,detailTexture]=await Promise.all([fetchAsset('manifest.json'),fetchAsset('alpine-height.f32','bin'),fetchAsset('trees.f32','bin'),fetchAsset('features.json'),texture('alpine-material.webp'),texture('navis-material.webp')]);if(heights.length!==meta.broadGrid[0]*meta.broadGrid[1]||treeData.length!==meta.treeCount*5)throw Error('Terrain asset dimensions do not match');await buildGround();await nextFrame();buildTrees();await nextFrame();buildFeatures();ready=true;metrics.ready=true;metrics.loadMs=Math.round(performance.now()-start);metrics.treeCount=trees.count;metrics.triangles=ground.reduce((s,t)=>s+t.count/3,0);metrics.waterways=features.waterways.length;viewport();draw();$('loading').hidden=true;document.body.dataset.ready='true';}
boot().catch(e=>{errors.push(e.message);$('loading').textContent='Terrain could not load: '+e.message;console.error(e);});
})();
