/* V144 geographic-material fit: modern source data, NOT a route georegistration.
   Crops the original broad V97/V102 EPSG:4326 extent in *physical metres*
   before mapping to the local prototype's square world coordinates.
   It cannot identify where the experimental V123 roads lie geographically. */
(function(root){
  'use strict';
  const METERS_PER_DEGREE=111320;
  function fit(bounds, worldBounds, imageWidth, imageHeight){
    if(!Array.isArray(bounds)||bounds.length!==4||!Array.isArray(worldBounds)||worldBounds.length!==4)
      throw Error('V144 geographic bounds required');
    const [west,south,east,north]=bounds;
    const [wx,wy,ww,wh]=worldBounds;
    if(![west,south,east,north,wx,wy,ww,wh,imageWidth,imageHeight].every(Number.isFinite)||
       !(west<east&&south<north&&ww>0&&wh>0&&imageWidth>0&&imageHeight>0))
      throw Error('V144 invalid geographic/source dimensions');
    const midLat=(north+south)/2;
    const metersX=(east-west)*METERS_PER_DEGREE*Math.cos(midLat*Math.PI/180);
    const metersY=(north-south)*METERS_PER_DEGREE;
    const sourceAspect=metersX/metersY, worldAspect=ww/wh;
    // Cover without geographic stretching: crop north/south for a wider view,
    // or crop east/west for a taller view. Never repeat imagery.
    const fx=Math.min(1,worldAspect/sourceAspect);
    const fy=Math.min(1,sourceAspect/worldAspect);
    const sx=imageWidth*(1-fx)/2,sy=imageHeight*(1-fy)/2;
    const sw=imageWidth*fx,sh=imageHeight*fy;
    const metresPerWorldX=metersX*fx/ww,metresPerWorldY=metersY*fy/wh;
    if(Math.abs(metresPerWorldX/metresPerWorldY-1)>1e-9)
      throw Error('V144 material aspect fit is anisotropic');
    return Object.freeze({
      sx,sy,sw,sh,metresPerWorldX,metresPerWorldY,
      cropLonLat:[west+(east-west)*(1-fx)/2,south+(north-south)*(1-fy)/2,
                  east-(east-west)*(1-fx)/2,north-(north-south)*(1-fy)/2],
      sourceBoundsLonLat:bounds.slice(),worldBounds:worldBounds.slice(),
      sourceAspect,worldAspect,
      // Explicitly false until surveyed road/bridge tie points exist.
      routeGeoregistered:false,historicallyCertified:false
    });
  }
  const api=Object.freeze({fit});
  root.V144GeoMaterial=api;
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
