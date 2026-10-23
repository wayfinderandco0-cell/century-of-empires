/* V145: mathematical route-to-geography registration audit, NOT a geographic
 * certification. No tie points are supplied by this module. The caller must
 * supply independent, documented ground controls for each playable tile.
 * Source evidence and historical correctness require external human review. */
'use strict';
const METERS_PER_DEGREE=111320;
const ORIGIN=[11.52,47.13];
const BOUNDS=[11.26,46.8,11.8,47.42];
const TILE_IDS=['west','matrei','south'];
const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
function toMeters(lonLat){
  const [lon,lat]=lonLat;
  if(!Array.isArray(lonLat)||lonLat.length!==2||![lon,lat].every(Number.isFinite)||
     lon<BOUNDS[0]||lon>BOUNDS[2]||lat<BOUNDS[1]||lat>BOUNDS[3])
    throw Error('Geographic control outside V97/V102 source extent');
  // Down-positive northing matches the prototype canvas coordinate convention.
  return [(lon-ORIGIN[0])*METERS_PER_DEGREE*Math.cos(ORIGIN[1]*Math.PI/180),
          -(lat-ORIGIN[1])*METERS_PER_DEGREE];
}
function resolve(tile,control){
  if(!control||typeof control.road!=='string'||!Number.isInteger(control.index))
    throw Error('Control must identify an existing road vertex');
  const road=tile.roads?.[control.road];
  if(!road||control.index<0||control.index>=road.length)
    throw Error('No authoritative V123 road vertex for control');
  const source=control.source;
  if(!source||typeof source.url!=='string'||!/^https:\/\//.test(source.url)||
     typeof source.featureId!=='string'||!source.featureId.trim()||
     !['modern-topographic','historical-survey'].includes(source.kind))
    throw Error('Control lacks traceable source metadata');
  if(control.world!==undefined)throw Error('Do not supply invented world coordinates');
  const local=road[control.index];
  if(!Array.isArray(local)||local.length!==2||!local.every(Number.isFinite))
    throw Error('Invalid authoritative road vertex');
  return {geo:toMeters(control.lonLat),world:[local[0]+tile.origin[0],local[1]+tile.origin[1]],
          key:control.road+':'+control.index,source};
}
function fitPair(a,b){
  const dx=b.geo[0]-a.geo[0],dy=b.geo[1]-a.geo[1];
  const ux=b.world[0]-a.world[0],uy=b.world[1]-a.world[1];
  const den=dx*dx+dy*dy;
  if(den<50*50||ux*ux+uy*uy<64*64)
    throw Error('Control pair too close for a stable geographic fit');
  const A=(ux*dx+uy*dy)/den,B=(uy*dx-ux*dy)/den;
  const scale=Math.hypot(A,B);
  if(!(scale>0&&Number.isFinite(scale)))throw Error('Invalid geographic fit');
  return {A,B,tx:a.world[0]-A*a.geo[0]+B*a.geo[1],
              ty:a.world[1]-B*a.geo[0]-A*a.geo[1],scale,
              angleRadians:Math.atan2(B,A)};
}
function apply(t,p){return [t.A*p[0]-t.B*p[1]+t.tx,t.B*p[0]+t.A*p[1]+t.ty];}
function auditTile(tile,controls,options={}){
  if(!tile||!TILE_IDS.includes(tile.id)||!Array.isArray(tile.origin)||
     !Array.isArray(controls)||controls.length<3)
    throw Error('Each playable tile requires >=3 documented independent controls');
  const points=controls.map(c=>resolve(tile,c));
  if(new Set(points.map(p=>p.key)).size!==points.length)
    throw Error('Duplicate route control cannot be independent evidence');
  const t=fitPair(points[0],points[1]);
  const residuals=points.map(p=>distance(apply(t,p.geo),p.world));
  const maxResidual=Math.max(...residuals);
  const tolerance=options.maxResidualPx??3;
  if(!Number.isFinite(tolerance)||tolerance<=0||tolerance>3)
    throw Error('Registration tolerance must be fail-closed (<=3 world px)');
  return {tile:tile.id,controlCount:points.length,
          independentHoldoutCount:points.length-2,
          maxResidualWorldPx:maxResidual,geometricFit:maxResidual<=tolerance,
          transform:t,sourceReferences:points.map(p=>p.source.url),
          sourceEvidenceAuthenticated:false,historicalRouteCertified:false,
          physicalIPhoneApproved:false};
}
function auditAtlas(atlas,controlsByTile,options={}){
  if(!atlas||!Array.isArray(atlas.tiles))throw Error('V123 atlas required');
  const tiles=new Map(atlas.tiles.map(t=>[t.id,t]));
  const reports=TILE_IDS.map(id=>auditTile(tiles.get(id),controlsByTile?.[id],options));
  const baseline=reports[0].transform;
  const sharedFrame=reports.every(r=>{
    const t=r.transform;
    const angle=Math.atan2(Math.sin(t.angleRadians-baseline.angleRadians),
                           Math.cos(t.angleRadians-baseline.angleRadians));
    return Math.abs(t.scale/baseline.scale-1)<=.02&&
           Math.abs(angle)<=2*Math.PI/180&&
           distance(apply(t,[0,0]),apply(baseline,[0,0]))<=5;
  });
  return {geometricFit:reports.every(r=>r.geometricFit)&&sharedFrame,
          sharedGeographicFrame:sharedFrame,reports,
          evidenceAuthenticated:false,productionApproved:false,
          navigableRouteCertified:false,
          note:'Synthetic or self-reported tie points cannot authenticate source imagery or historical roads.'};
}
module.exports={toMeters,fitPair,apply,auditTile,auditAtlas};
