/* Original world-anchored 3D foliage overlay for the isolated V267 mesh study.
 * GPU instancing keeps geometry separate from the protected native V123 game.
 * Modern V94 forest cover is a density cue, not historical certification.
 */
(function () {
"use strict";
const base="../generated/v267-relief-pilot/";
const state={ready:false,failed:null,total:0,drawn:0,groups:[]};
window.COEFoliage=state;
function compile(gl,type,source){
 const shader=gl.createShader(type);gl.shaderSource(shader,source);gl.compileShader(shader);
 if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(shader));
 return shader;
}
function makeGeometry(kind){
 // Entirely original world-scale branching geometry, not photo billboards.
 // Keep tree roots at y=0; existing heightfield contact stays exact.
 const vertices=[];
 function triangle(a,b,c,mat){
  const u=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],v=[c[0]-a[0],c[1]-a[1],c[2]-a[2]];
  const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
  const l=Math.hypot(...n)||1;
  for(const p of [a,b,c])vertices.push(...p,mat,n[0]/l,n[1]/l,n[2]/l);
 }
 function trunk(){
  const sides=8;
  for(let i=0;i<sides;i++){
   const a=2*Math.PI*i/sides,b=2*Math.PI*(i+1)/sides;
   const p=[.085*Math.cos(a),0,.085*Math.sin(a)];
   const q=[.085*Math.cos(b),0,.085*Math.sin(b)];
   const r=[.043*Math.cos(a),.57,.043*Math.sin(a)];
   const s=[.043*Math.cos(b),.57,.043*Math.sin(b)];
   triangle(p,q,r,0);triangle(q,s,r,0);
  }
 }
 trunk();
 if(kind==="conifer"){
  // Distinct descending branch whorls replace repeated stacked cones.
  // Triangular sprays have actual front/back faces and directional depth.
  for(let tier=0;tier<6;tier++){
   const t=tier/6,y=.18+t*.68,reach=.92*Math.pow(1-t,.86);
   const branches=8;
   for(let i=0;i<branches;i++){
    const angle=2*Math.PI*(i+.42*(tier%2))/branches;
    const dx=Math.cos(angle),dz=Math.sin(angle),px=-dz,pz=dx;
    const swing=.92+.10*Math.sin(3*i+2*tier);
    const tip=[reach*swing*dx,y-.055*(1-t),reach*swing*dz];
    const inside=[.055*dx,y+.13*(1-t),.055*dz];
    const left=[.56*reach*dx+.19*reach*px,y+.028,.56*reach*dz+.19*reach*pz];
    const right=[.56*reach*dx-.19*reach*px,y+.028,.56*reach*dz-.19*reach*pz];
    triangle(inside,left,tip,1);triangle(inside,tip,right,1);
    triangle(left,right,tip,2);
   }
  }
  // Irregular narrow leader, not a flat triangular cap.
  for(let i=0;i<8;i++){
   const a=2*Math.PI*i/8,b=2*Math.PI*(i+1)/8;
   triangle([.17*Math.cos(a),.80,.17*Math.sin(a)],
            [.17*Math.cos(b),.80,.17*Math.sin(b)],[0,1.06,0],1);
  }
 }else{
  // Overlapping volumetric leaf masses, asymmetric and spatially separated.
  const lobes=[[-.30,.68,-.06,.68],[.30,.73,.08,.63],
               [-.04,.89,-.20,.64],[.05,.78,.28,.53]];
  for(let k=0;k<lobes.length;k++){
   const [cx,cy,cz,r]=lobes[k],rings=4,sides=9;
   for(let j=0;j<rings;j++)for(let i=0;i<sides;i++){
    const a=Math.PI*j/rings,b=Math.PI*(j+1)/rings;
    const t=2*Math.PI*i/sides,u=2*Math.PI*(i+1)/sides;
    function point(phi,theta){
     const rough=1+.09*Math.sin(3*theta+2*k)+.06*Math.cos(5*theta+phi*2+k);
     return [cx+r*rough*Math.sin(phi)*Math.cos(theta),
             cy+r*.53*Math.cos(phi),
             cz+r*rough*Math.sin(phi)*Math.sin(theta)];
    }
    const p=point(a,t),q=point(a,u),s=point(b,t),v=point(b,u);
    triangle(p,s,q,3);triangle(q,s,v,3);
   }
  }
 }
 return new Float32Array(vertices);
}
async function init(){
 try{
  // The heightmesh review is an isolated WebGL2 page; never mutate gameplay.
  const gl=document.getElementById("view").getContext("webgl2");
  if(!gl)throw Error("WebGL2 unavailable");
  const response=await fetch(base+"foliage-manifest.json",{cache:"no-cache"});
  if(!response.ok)throw Error("Foliage manifest HTTP "+response.status);
  const m=await response.json();
  if(m.schema!=="coe-v267-world-locked-foliage/v1"||m.strideFloats!==8||
     m.visuallyApprovedV267!==0||m.nativeGamePlayable!==0||m.finishedToday!==0)
   throw Error("Invalid or falsely approved foliage manifest");
  const bytes=await(await fetch(base+m.file)).arrayBuffer();
  if(bytes.byteLength!==m.total*8*4)throw Error("Foliage binary length mismatch");
  const vert=`#version 300 es
layout(location=0) in vec4 aLocal;
layout(location=1) in vec3 aNormal;
layout(location=2) in vec4 aTreeA;
layout(location=3) in vec4 aTreeB;
uniform mat4 uVP;
out vec3 vNormal;
out float vMaterial;
out float vHue;
out float vSeed;
out float vSpecies;
void main(){
 // World-anchored instance rotation breaks identical crown silhouettes.
 float angle=6.2831853*aTreeB.w;
 float cs=cos(angle),sn=sin(angle);
 vec3 local=vec3(aLocal.x*cs-aLocal.z*sn,aLocal.y,
                 aLocal.x*sn+aLocal.z*cs);
 vec3 n=vec3(aNormal.x*cs-aNormal.z*sn,aNormal.y,
             aNormal.x*sn+aNormal.z*cs);
 vec3 position=aTreeA.xyz+vec3(local.x*aTreeA.w,
                                local.y*aTreeB.x,local.z*aTreeA.w);
 gl_Position=uVP*vec4(position,1.0);
 vNormal=n;vMaterial=aLocal.w;vHue=aTreeB.y;
 vSeed=aTreeB.w;vSpecies=aTreeB.z;
}`;
  const frag=`#version 300 es
precision highp float;
in vec3 vNormal;in float vMaterial;in float vHue;
in float vSeed;in float vSpecies;
out vec4 fragColor;
void main(){
 vec3 n=normalize(vNormal);
 float direct=max(0.0,dot(n,normalize(vec3(-.48,.81,.32))));
 float ambient=.48+.40*direct;
 float variation=.86+.22*fract(sin(vSeed*47.1)*43758.5453);
 vec3 bark=vec3(.25,.20,.15)*variation;
 vec3 conifer=vec3(.105,.255,.135)*vHue*variation;
 vec3 underside=vec3(.070,.165,.085)*vHue*variation;
 vec3 broadleaf=vec3(.19,.315,.125)*vHue*variation;
 vec3 color=vMaterial<.5?bark:
            vMaterial<1.5?conifer:
            vMaterial<2.5?underside:broadleaf;
 // Distant broadleaf masses retain different color and light response.
 float shade=vMaterial<.5?.79:ambient;
 fragColor=vec4(color*shade,1.0);
}`;
  const program=gl.createProgram();
  gl.attachShader(program,compile(gl,gl.VERTEX_SHADER,vert));
  gl.attachShader(program,compile(gl,gl.FRAGMENT_SHADER,frag));
  gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
  const vp=gl.getUniformLocation(program,"uVP");
  // One reusable 3D mesh per species; instances are packed by geographic
  // cell so a zoomed-in iPhone never draws forests on offscreen octagons.
  const species=new Map(),groups=[],batches=[];
  for(const g of m.groups){
   if(g.kind!=="conifer"&&g.kind!=="broadleaf")throw Error("Unknown tree type");
   const mesh=makeGeometry(g.kind),vb=gl.createBuffer();
   gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,mesh,gl.STATIC_DRAW);
   const geometry={vb,vertices:mesh.length/7,triangles:mesh.length/21};
   species.set(g.kind,geometry);
   groups.push({kind:g.kind,count:g.count,triangles:geometry.triangles});
  }
  if(!Array.isArray(m.cellBatches)||m.cellBatches.length!==16)
   throw Error("Missing 8-cell foliage streaming layout");
  let nextOffset=0;
  for(const b of m.cellBatches){
   const geometry=species.get(b.kind);
   if(!geometry||b.offsetFloats!==nextOffset||b.offsetFloats%8!==0||
      b.col<0||b.col>=4||b.row<0||b.row>=2||
      !Number.isInteger(b.count)||b.count<0||
      !Array.isArray(b.worldBounds)||b.worldBounds.length!==4||
      !Array.isArray(b.worldYRange)||b.worldYRange.length!==2)
    throw Error("Invalid foliage cell batch");
   const vao=gl.createVertexArray();gl.bindVertexArray(vao);
   gl.bindBuffer(gl.ARRAY_BUFFER,geometry.vb);
   gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,4,gl.FLOAT,false,28,0);
   gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,3,gl.FLOAT,false,28,16);
   const ib=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,ib);
   gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(bytes,b.offsetFloats*4,b.count*8),gl.STATIC_DRAW);
   gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,4,gl.FLOAT,false,32,0);
   gl.vertexAttribDivisor(2,1);
   gl.enableVertexAttribArray(3);gl.vertexAttribPointer(3,4,gl.FLOAT,false,32,16);
   gl.vertexAttribDivisor(3,1);
   batches.push({vao,vertices:geometry.vertices,count:b.count,
                 bounds:b.worldBounds,yRange:b.worldYRange});
   nextOffset+=b.count*8;
  }
  if(nextOffset!==m.total*8)throw Error("Foliage batch total mismatch");
  gl.bindVertexArray(null);
  // Test all 8 corners of the tree batch AABB against the real camera
  // projection, not an arbitrary center-distance estimate. The y bounds
  // include crowns and terrain elevation; the padding prevents edge popping.
  function inFrustum(batch,matrix){
   const [left,top,right,bottom]=batch.bounds;
   const [minY,maxY]=batch.yRange;
   let loX=Infinity,hiX=-Infinity,loY=Infinity,hiY=-Infinity;
   for(const x of [left,right])for(const y of [minY,maxY])
    for(const z of [-top,-bottom]){
     const w=matrix[3]*x+matrix[7]*y+matrix[11]*z+matrix[15];
     if(w<=0)return true;
     const px=(matrix[0]*x+matrix[4]*y+matrix[8]*z+matrix[12])/w;
     const py=(matrix[1]*x+matrix[5]*y+matrix[9]*z+matrix[13])/w;
     loX=Math.min(loX,px);hiX=Math.max(hiX,px);
     loY=Math.min(loY,py);hiY=Math.max(hiY,py);
    }
   return hiX>=-1.12&&loX<=1.12&&hiY>=-1.12&&loY<=1.12;
  }
  state.total=m.total;state.groups=groups;state.totalBatches=batches.length;
  state.geometryTrianglesPerTree=Object.fromEntries(groups.map(g=>[g.kind,g.triangles]));
  state.ready=true;
  state.draw=(vpMatrix,center,span)=>{
   state.drawn=0;state.visibleBatches=0;state.culledBatches=0;
   if(span>7000){state.culledBatches=batches.length;return}
   const old=gl.getParameter(gl.CURRENT_PROGRAM);
   gl.useProgram(program);gl.uniformMatrix4fv(vp,false,vpMatrix);
   const fraction=span>4500?.33:1;
   for(const batch of batches){
    if(!batch.count||!inFrustum(batch,vpMatrix)){state.culledBatches++;continue}
    gl.bindVertexArray(batch.vao);
    const count=Math.ceil(batch.count*fraction);
    gl.drawArraysInstanced(gl.TRIANGLES,0,batch.vertices,count);
    state.drawn+=count;state.visibleBatches++;
   }
   gl.bindVertexArray(null);gl.useProgram(old);
  };
  if(typeof draw==="function")draw();
 }catch(error){state.failed=String(error);console.error("3D foliage:",error)}
}
init();
})();