/* V213 native XYZ source geodesy. Coordinates describe MODERN source pixels,
 * NEVER V121/V123 game pixels or authenticated 1780 geography.
 * EPSG:3857 XYZ z18 -> WGS84. No canvas stretching or invented landmarks.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.V213Geo=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const ZOOM=18, SIZE=256, PANEL=512;
  const cells=Object.freeze({
    west:Object.freeze({xyz:Object.freeze([139398,92095]),contact:Object.freeze([0,0])}),
    matrei:Object.freeze({xyz:Object.freeze([139400,92095]),contact:Object.freeze([512,0])}),
    south:Object.freeze({xyz:Object.freeze([139400,92097]),contact:Object.freeze([512,512])})
  });
  function fail(message){throw new RangeError('V213 modern source coordinate: '+message);}
  function toGeo(cell,sourceContactXY){
    const cfg=cells[cell];
    if(!cfg)fail('unknown source panel');
    if(!Array.isArray(sourceContactXY)||sourceContactXY.length!==2||
       !sourceContactXY.every(n=>typeof n==='number'&&Number.isFinite(n)))fail('nonfinite source contact');
    const x=sourceContactXY[0]-cfg.contact[0],y=sourceContactXY[1]-cfg.contact[1];
    if(x<0||x>=PANEL||y<0||y>=PANEL)fail('outside native 512px panel');
    const n=2**ZOOM;
    const tileX=cfg.xyz[0]+Math.floor(x/SIZE);
    const tileY=cfg.xyz[1]+Math.floor(y/SIZE);
    const lon=(cfg.xyz[0]+x/SIZE)/n*360-180;
    const latitudeRadians=Math.atan(Math.sinh(Math.PI*(1-2*(cfg.xyz[1]+y/SIZE)/n)));
    const lat=latitudeRadians*180/Math.PI;
    if(!Number.isFinite(lon)||!Number.isFinite(lat)||Math.abs(lat)>85.05113)fail('invalid geographic projection');
    return Object.freeze({
      lon,lat,
      nativeXYZ:Object.freeze([tileX,tileY,ZOOM]),
      nativePixelXY:Object.freeze([x%SIZE,y%SIZE]),
      sourceCell:cell,
      sourceStatus:'MODERN_NATIVE_XYZ_NOT_REGISTERED_TO_GAME',
      gameGeographyVerified:false,
      historicalGeographyVerified:false
    });
  }
  return Object.freeze({toGeo,cells,zoom:ZOOM,pixelSize:SIZE,panelSize:PANEL});
});
