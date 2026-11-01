/* V267 scenic tile viewport loader. Protected V121/V123 originals are loaded separately.
 * No route nodes, historical assertions, or approval statuses are created here.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=="undefined"&&module.exports)module.exports=api;
 else root.COEV267ViewportCache=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 "use strict";
 const W=1536,H=1024;
 function create({cells,load,onChange=()=>{},maxDecoded=6,maxConcurrent=2,padding=128}){
  if(!Array.isArray(cells)||typeof load!=="function")throw Error("viewport cache needs cells and load");
  if(!Number.isInteger(maxDecoded)||maxDecoded<1||!Number.isInteger(maxConcurrent)||maxConcurrent<1)throw Error("invalid cache limits");
  const all=cells.filter(c=>c&&c.art&&Array.isArray(c.origin)&&c.origin.length===2);
  const cache=new Map(),active=new Map(),errors=new Map();
  let queue=[],wanted=new Set(),closed=false,requests=0;
  const intersects=(c,b)=>c.origin[0]<b.maxX&&c.origin[0]+W>b.minX&&c.origin[1]<b.maxY&&c.origin[1]+H>b.minY;
  function prune(){
   for(const id of [...cache.keys()])if(!wanted.has(id))cache.delete(id);
   while(cache.size>maxDecoded)cache.delete(cache.keys().next().value);
  }
  function pump(){
   if(closed)return;
   while(active.size<maxConcurrent&&queue.length){
    const cell=queue.shift();
    if(!wanted.has(cell.id)||cache.has(cell.id)||active.has(cell.id)||errors.has(cell.id))continue;
    requests++;
    const task=Promise.resolve().then(()=>load(cell.art,cell)).then(image=>{
     if(closed||!wanted.has(cell.id))return;
     cache.delete(cell.id);cache.set(cell.id,image);prune();onChange();
    }).catch(error=>{if(!closed){errors.set(cell.id,String(error));onChange();}})
    .finally(()=>{active.delete(cell.id);pump();});
    active.set(cell.id,task);
   }
  }
  function update(bounds){
   if(closed)return;
   if(!bounds||!["minX","minY","maxX","maxY"].every(k=>Number.isFinite(bounds[k])))throw Error("invalid viewport");
   const b={minX:bounds.minX-padding,minY:bounds.minY-padding,maxX:bounds.maxX+padding,maxY:bounds.maxY+padding};
   const cx=(bounds.minX+bounds.maxX)/2,cy=(bounds.minY+bounds.maxY)/2;
   const visible=all.filter(c=>intersects(c,b)).sort((a,z)=>{
    const da=(a.origin[0]+W/2-cx)**2+(a.origin[1]+H/2-cy)**2;
    const dz=(z.origin[0]+W/2-cx)**2+(z.origin[1]+H/2-cy)**2;
    return da-dz||a.id.localeCompare(z.id);
   }).slice(0,maxDecoded);
   wanted=new Set(visible.map(c=>c.id));
   queue=visible.filter(c=>!cache.has(c.id)&&!active.has(c.id)&&!errors.has(c.id));
   prune();pump();
  }
  function entries(){return [...cache.entries()];}
  function get(id){return cache.get(id)||null;}
  function stats(){return {decoded:cache.size,inFlight:active.size,queued:queue.length,wanted:wanted.size,requests,failed:errors.size};}
  function dispose(){closed=true;queue=[];wanted.clear();cache.clear();errors.clear();}
  return Object.freeze({update,entries,get,stats,dispose});
 }
 return Object.freeze({create});
});