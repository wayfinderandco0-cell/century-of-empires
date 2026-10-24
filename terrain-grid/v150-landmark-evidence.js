/* V150: provenance for visually observed MODERN orthophoto landmarks.
 * No V123 road vertex, Matrei game-tile placement, historic route, or bridge
 * is inferred from source pixels. Observations remain unreviewed candidates.
 */
'use strict';
const source=require('./v148-orthophoto-pixels.js');
const SHA=/^[a-f0-9]{64}$/;
const TYPES=new Set(['modern-road-bend','modern-building','forest-edge','field-boundary','water-feature','other']);
const FIELDS=new Set(['id','type','pixel','description','status']);
function packet(manifest,observations){
  const grid=source.verify(manifest);
  if(!SHA.test(manifest.mosaicSha256||'') ||
     !manifest.samples.every(s=>SHA.test(s.sha256||'')&&
       s.imageFile===s.name+'.jpeg'))
    throw Error('Actual downloaded orthophoto hashes required, not planner-only metadata');
  if(!Array.isArray(observations)||observations.length<1)
    throw Error('At least one source-only visual observation required');
  const ids=new Set();
  const features=observations.map(o=>{
    if(!o||Object.keys(o).some(k=>!FIELDS.has(k)) ||
       typeof o.id!=='string'||!/^source-[a-z0-9-]{3,60}$/.test(o.id)||
       ids.has(o.id)) throw Error('Invalid, duplicate or game-linked source observation');
    ids.add(o.id);
    if(!TYPES.has(o.type)||o.status!=='unverified-observation'||
       typeof o.description!=='string'||o.description.trim().length<12||
       !Array.isArray(o.pixel)||o.pixel.length!==2||
       !o.pixel.every(v=>typeof v==='number'&&Number.isFinite(v)))
      throw Error('Source observation missing constrained pixel/type/status');
    const [x,y]=o.pixel;
    const lonLat=source.pixelToGeo(manifest,x,y);
    const lookup=source.geoToPixel(manifest,...lonLat);
    if(Math.hypot(lookup.x-x,lookup.y-y)>0.00001)
      throw Error('Source pixel/geography roundtrip mismatch');
    const tile=manifest.samples[lookup.gridRow*3+lookup.gridCol];
    return {
      id:o.id,type:o.type,description:o.description,
      status:'unverified-observation',sourcePixel:[x,y],
      lonLat,sourceTile:tile.name,sourceTileXYZ:tile.tileXYZ.slice(),
      sourceTileUrl:tile.url,sourceTileSha256:tile.sha256,
      mosaicSha256:manifest.mosaicSha256,
      matchedV123RoadVertex:null,matchedGameOctagon:null,
      historicalRoadVerified:false,visualLandmarkAuthenticated:false
    };
  });
  return {
    version:150,purpose:'Modern source-landmark candidate evidence ONLY',
    sourceMosaicBoundsLonLat:grid.bounds,
    sourcePixelDimensions:[grid.dimension,grid.dimension],
    provider:manifest.provider,requiredAttribution:manifest.requiredAttribution,
    sourceLicense:manifest.license,
    observations:features,
    v123RouteTiePoints:[],v123RoadsMapped:false,
    matreiPhotoRegistered:false,westGameTileRegistered:false,
    southGameTileRegistered:false,bridgeBanksVerified:false,
    historic1780Certified:false,navigableRouteCertified:false,
    physicalIPhoneApproved:false,productionApproved:false,
    nextEvidence:'Independently identify V123 image landmarks and document two source controls plus a holdout for each corridor. Modern source points alone do not satisfy this.'
  };
}
module.exports={packet};
