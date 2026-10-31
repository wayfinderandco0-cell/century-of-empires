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
 const vertices=[];
 function triangle(a,b,c,mat){
  const u=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],v=[c[0]-a[0],c[1]-a[1],c[2]-a[2]];
  const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
  const l=Math.hypot(...n)||1;
  for(const p of [a,b,c])vertices.push(...p,mat,n[0]/l,n[1]/l,n[2]/l);
 }
 function cylinder(radius,y0,y1,mat,segments=7){
  for(let i=0;i<segments;i++){
   const a=2*Math.PI*i/segments,b=2*Math.PI*(i+1)/segments;
   const p=[Math.cos(a)*radius,y0,Math.sin(a)*radius];
   const q=[Math.cos(b)*radius,y0,Math.sin(b)*radius];
   const r=[Math.cos(a)*radius,y1,Math.sin(a)*radius];
   const s=[Math.cos(b)*radius,y1,Math.sin(b)*radius];
   triangle(p,q,r,mat);triangle(q,s,r,mat);
  }
 }
 cylinder(.10,0,.38,0);
 if(kind==="conifer"){
  // Overlapping crown tiers create actual depth and silhouette, not
  // billboard triangles painted on a flat terrain photograph.
  for(const [y0,y1,r] of [[.19,.58,1],[.42,.81,.76],[.65,1,.48]]){
   for(let i=0;i<10;i++){
    const a=2*Math.PI*i/10,b=2*Math.PI*(i+1)/10;
    triangle([r*Math.cos(a),y0,r*Math.sin(a)],
             [r*Math.cos(b),y0,r*Math.sin(b)],
             [0,y1,0],1);
   }
  }
 } else {
  // Three overlapping faceted ellipsoids give broadleaf crowns volume.
  for(const [cx,cy,cz,r] of [[-.32,.68,0,.76],[.33,.69,.12,.72],[0,.83,-.18,.75]]){
   const rings=5,sides=9;
   for(let j=0;j<rings;j++)for(let i=0;i<sides;i++){
    const a=Math.PI*j/rings,b=Math.PI*(j+1)/rings;
    const t=2*Math.PI*i/sides,u=2*Math.PI*(i+1)/sides;
    function point(phi,theta){
     return [cx+r*Math.sin(phi)*Math.cos(theta),
             cy+r*.55*Math.cos(phi),
             cz+r*Math.sin(phi)*Math.sin(theta)];
    }
    const p=point(a,t),q=point(a,u),s=point(b,t),v=point(b,u);
    triangle(p,s,q,1);triangle(q,s,v,1);
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
void main(){
 vec3 position=aTreeA.xyz+vec3(aLocal.x*aTreeA.w,
                                aLocal.y*aTreeB.x,aLocal.z*aTreeA.w);
 gl_Position=uVP*vec4(position,1.0);
 vNormal=aNormal;vMaterial=aLocal.w;vHue=aTreeB.y;vSeed=aTreeB.w;
}`;
  const frag=`#version 300 es
precision highp float;
in vec3 vNormal;in float vMaterial;in float vHue;in float vSeed;
out vec4 fragColor;
void main(){
 float lit=.55+.45*max(0.0,dot(normalize(vNormal),normalize(vec3(-.5,.78,.36))));
 vec3 bark=vec3(.28,.22,.16);
 vec3 needles=vec3(.11,.29,.15)*vHue+vec3(.015*vSeed,.035*vSeed,.012);
 vec3 color=mix(bark,needles,step(.5,vMaterial));
 fragColor=vec4(color*lit,1.0);
}`;
  const program=gl.createProgram();
  gl.attachShader(program,compile(gl,gl.VERTEX_SHADER,vert));
  gl.attachShader(program,compile(gl,gl.FRAGMENT_SHADER,frag));
  gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
  const vp=gl.getUniformLocation(program,"uVP");
  const groups=[];
  for(const g of m.groups){
   if(g.kind!=="conifer"&&g.kind!=="broadleaf")throw Error("Unknown tree type");
   const mesh=makeGeometry(g.kind);
   const vao=gl.createVertexArray();gl.bindVertexArray(vao);
   const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);
   gl.bufferData(gl.ARRAY_BUFFER,mesh,gl.STATIC_DRAW);
   gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,4,gl.FLOAT,false,28,0);
   gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,3,gl.FLOAT,false,28,16);
   const ib=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,ib);
   const offset=g.offsetFloats*4;
   gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(bytes,offset,g.count*8),gl.STATIC_DRAW);
   gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,4,gl.FLOAT,false,32,0);
   gl.vertexAttribDivisor(2,1);
   gl.enableVertexAttribArray(3);gl.vertexAttribPointer(3,4,gl.FLOAT,false,32,16);
   gl.vertexAttribDivisor(3,1);
   groups.push({vao,count:g.count,vertices:mesh.length/7});
  }
  gl.bindVertexArray(null);
  state.total=m.total;state.groups=groups;state.ready=true;
  state.draw=(vpMatrix,center,span)=>{
   if(span>7000){state.drawn=0;return}
   const old=gl.getParameter(gl.CURRENT_PROGRAM);
   gl.useProgram(program);gl.uniformMatrix4fv(vp,false,vpMatrix);
   const fraction=span>4500?.33:1;
   state.drawn=0;
   for(const group of groups){
    gl.bindVertexArray(group.vao);
    const count=Math.ceil(group.count*fraction);
    gl.drawArraysInstanced(gl.TRIANGLES,0,group.vertices,count);
    state.drawn+=count;
   }
   gl.bindVertexArray(null);gl.useProgram(old);
  };
  if(typeof draw==="function")draw();
 }catch(error){state.failed=String(error);console.error("3D foliage:",error)}
}
init();
})();