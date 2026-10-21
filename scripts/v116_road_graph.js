/* V116 shared local road graph: candidate geometry, never production authorization.
 * Source pixels are authoritative for both unit location and painting overlays.
 * No route may imply an unpainted far-bank continuation or capturable village.
 */
(function(root) {
  "use strict";
  const finite = p => Array.isArray(p) && p.length === 2 &&
    p.every(x => typeof x === "number" && Number.isFinite(x));
  const same = (a,b) => a[0] === b[0] && a[1] === b[1];
  const distance = (a,b) => Math.hypot(a[0]-b[0],a[1]-b[1]);
  function lengths(path) {
    const a=[0];
    for(let i=1;i<path.length;i++)a.push(a.at(-1)+distance(path[i-1],path[i]));
    return a;
  }
  function closestPointDistance(p,path) {
    if(!finite(p))throw Error("Invalid landmark");
    let out=Infinity;
    for(let i=1;i<path.length;i++) {
      const a=path[i-1],b=path[i],dx=b[0]-a[0],dy=b[1]-a[1];
      const t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)));
      out=Math.min(out,Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy));
    }
    return out;
  }
  function build({south,bridge,forkIndex,imageSize=[1100,842],endOfBridge="visible-far-bank-only"}) {
    if(!Array.isArray(imageSize)||imageSize.length!==2||imageSize.some(x=>!Number.isInteger(x)||x<=0)||
       !Number.isInteger(forkIndex)||forkIndex<1 ||
       !Array.isArray(south)||!Array.isArray(bridge)||forkIndex>=Math.min(south.length,bridge.length)-1) {
      throw Error("Invalid road graph inputs");
    }
    const routes={south,bridge};
    for(const [name,points] of Object.entries(routes)) {
      if(points.length<3)throw Error("Route too short: "+name);
      for(let i=0;i<points.length;i++) {
        const p=points[i];
        if(!finite(p)||p[0]<0||p[0]>imageSize[0]||p[1]<0||p[1]>imageSize[1])
          throw Error("Out-of-art road point: "+name+" "+i);
        if(i && same(p,points[i-1]))throw Error("Zero-length road edge: "+name+" "+i);
      }
    }
    for(let i=0;i<=forkIndex;i++)if(!same(south[i],bridge[i]))
      throw Error("Roads must share exact fork approach");
    if(same(south.at(-1),bridge.at(-1)))throw Error("Branch ends cannot coincide");
    const paths={south:south.map(p=>p.slice()),bridge:bridge.map(p=>p.slice())};
    const dists={south:lengths(paths.south),bridge:lengths(paths.bridge)};
    const forkDistance=dists.south[forkIndex];
    if(Math.abs(forkDistance-dists.bridge[forkIndex])>1e-7)throw Error("Fork distance discontinuity");
    const edgePaths={
      approach:paths.south.slice(0,forkIndex+1),
      south:paths.south.slice(forkIndex),
      bridge:paths.bridge.slice(forkIndex)
    };
    const endpoints={
      approachStart:edgePaths.approach[0].slice(),
      southExit:paths.south.at(-1).slice(),
      bridgeStop:paths.bridge.at(-1).slice()
    };
    function assertName(name) {if(!Object.hasOwn(paths,name))throw Error("Unknown route "+name);}
    function length(name) {assertName(name);return dists[name].at(-1);}
    function sample(name,rawDistance) {
      assertName(name);
      if(typeof rawDistance!=="number"||!Number.isFinite(rawDistance))throw Error("Invalid travelled distance");
      const route=paths[name],cum=dists[name],d=Math.max(0,Math.min(length(name),rawDistance));
      let lo=1,hi=cum.length-1;
      while(lo<hi){const mid=Math.floor((lo+hi)/2);if(cum[mid]<d)lo=mid+1;else hi=mid;}
      const seg=lo,span=cum[seg]-cum[seg-1],t=(d-cum[seg-1])/span;
      return [route[seg-1][0]*(1-t)+route[seg][0]*t,route[seg-1][1]*(1-t)+route[seg][1]*t];
    }
    function choose(currentRoute,rawDistance,nextRoute) {
      assertName(currentRoute);assertName(nextRoute);
      if(!Number.isFinite(rawDistance)||rawDistance<0)throw Error("Invalid position");
      const d=Math.min(length(currentRoute),rawDistance);
      if(nextRoute!==currentRoute && d>forkDistance+1e-6)
        return {allowed:false,route:currentRoute,distance:d,reason:"Already beyond the fork; return to junction before switching"};
      return {allowed:true,route:nextRoute,distance:d,reason:null};
    }
    function advance(name,rawDistance,deltaPx) {
      assertName(name);
      if(!Number.isFinite(rawDistance)||rawDistance<0||!Number.isFinite(deltaPx)||deltaPx<0)
        throw Error("Invalid movement step");
      const distance=Math.min(length(name),rawDistance+deltaPx);
      return {route:name,distance,position:sample(name,distance),arrived:distance>=length(name)-1e-8,
        terminal:name==="bridge"?"visible-far-bank-stop":"art-boundary-stop"};
    }
    function landmarkAudit(landmarks,original) {
      if(!Array.isArray(landmarks)||landmarks.length<1)throw Error("No visual landmarks");
      const repaired=landmarks.map(p=>closestPointDistance(p,paths.bridge));
      const base=original ? landmarks.map(p=>closestPointDistance(p,original)):null;
      const stats=a=>({count:a.length,mean:a.reduce((s,v)=>s+v,0)/a.length,max:Math.max(...a)});
      return {candidate:stats(repaired),baseline:base?stats(base):null};
    }
    // The graph is a *drawing and movement candidate*, not a geography/conquest claim.
    return {kind:"art-aligned-candidate",approvedForProduction:false,conquerable:false,
      imageSize:imageSize.slice(),forkIndex,forkPoint:paths.south[forkIndex].slice(),
      forkDistance,edges:edgePaths,paths,endpoints,bridgeTerminal:endOfBridge,
      length,sample,choose,advance,landmarkAudit};
  }
  const api={build,closestPointDistance};
  if(typeof module==="object"&&module.exports)module.exports=api;
  else root.CenturyV116RoadGraph=api;
})(typeof globalThis!=="undefined"?globalThis:this);
