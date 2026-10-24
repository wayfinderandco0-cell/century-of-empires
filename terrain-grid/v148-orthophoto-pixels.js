/* V148: exact Web Mercator pixel lookup for the *modern source* V147 mosaic.
 * Geographic pixels are NOT V123 world/army pixels. This deliberately exposes
 * no game-world transform and cannot certify 1780 roads or playable corridors.
 * Input is a V147 manifest, never guessed Matrei/West/South tile locations.
 */
'use strict';
const TILE = 256;
const GRID = 3;
const PROVIDER = 'https://mapsneu.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857';
const LIMIT = 85.05112878;
function validNumber(v){ return typeof v === 'number' && Number.isFinite(v); }
function near(a,b){ return validNumber(a) && validNumber(b) && Math.abs(a-b) <= 2e-10; }
function mercatorY(lat){
  if(!validNumber(lat) || Math.abs(lat) >= LIMIT) throw Error('Latitude outside EPSG:3857');
  return (1-Math.asinh(Math.tan(lat*Math.PI/180))/Math.PI)/2;
}
function xyzBounds(x,y,z){
  const n=2**z;
  const lat=row=>Math.atan(Math.sinh(Math.PI*(1-2*row/n)))*180/Math.PI;
  return [x/n*360-180,lat(y+1),(x+1)/n*360-180,lat(y)];
}
function verify(manifest){
  if(!manifest || manifest.version!==147 || manifest.crs!=='EPSG:3857' ||
     manifest.provider!=='basemap.at' || manifest.requiredAttribution!=='Datenquelle: basemap.at' ||
     manifest.worldLockedGeographicXYZ!==true ||
     !Array.isArray(manifest.grid) || manifest.grid.join(',')!=='3,3' ||
     !Array.isArray(manifest.pixelDimensions) || manifest.pixelDimensions.join(',')!=='768,768' ||
     !Array.isArray(manifest.samples) || manifest.samples.length!==GRID*GRID)
    throw Error('Unsupported or incomplete V147 geographic mosaic');
  for(const key of ['historic1780Certified','gameRouteGeoregistered',
                    'gameOctagonCentersCertified','navigableRouteCertified','productionApproved']){
    if(manifest[key]!==false) throw Error('Source mosaic cannot assert game/historical certification');
  }
  const first=manifest.samples[0].tileXYZ;
  if(!Array.isArray(first)||first.length!==3) throw Error('Invalid XYZ source origin');
  const [x0,y0,z]=first;
  const n=2**z;
  if(!Number.isInteger(z)||z<0||z>20 || !Number.isInteger(x0)||!Number.isInteger(y0)||
     x0<0||y0<0||x0+GRID>n||y0+GRID>n) throw Error('Invalid source XYZ range');
  for(let r=0;r<GRID;r++) for(let c=0;c<GRID;c++){
    const sample=manifest.samples[r*GRID+c];
    const x=x0+c,y=y0+r;
    if(sample.gridRow!==r||sample.gridCol!==c||
       !Array.isArray(sample.tileXYZ)||sample.tileXYZ.join(',')!==[x,y,z].join(',')||
       sample.url!==`${PROVIDER}/${z}/${y}/${x}.jpeg`||
       !Array.isArray(sample.tileBoundsLonLat)||sample.tileBoundsLonLat.length!==4||
       !sample.tileBoundsLonLat.every((v,i)=>near(v,xyzBounds(x,y,z)[i])))
      throw Error('Source XYZ adjacency, bounds, or URL mismatch');
  }
  const expected=[...xyzBounds(x0,y0+GRID-1,z).slice(0,2),
                  ...xyzBounds(x0+GRID-1,y0,z).slice(2,4)];
  if(!Array.isArray(manifest.mosaicBoundsLonLat)||manifest.mosaicBoundsLonLat.length!==4||
     !manifest.mosaicBoundsLonLat.every((v,i)=>near(v,expected[i])))
    throw Error('Source mosaic geographic bounds mismatch');
  return Object.freeze({x0,y0,z,dimension:GRID*TILE,bounds:expected});
}
function geoToPixel(manifest,lon,lat){
  const v=verify(manifest);
  if(!validNumber(lon)||!validNumber(lat)) throw Error('Non-finite geographic coordinate');
  const n=2**v.z;
  const px=(lon+180)/360*n*TILE-v.x0*TILE;
  const py=mercatorY(lat)*n*TILE-v.y0*TILE;
  if(!(px>=0 && py>=0 && px<v.dimension && py<v.dimension))
    throw Error('Geographic point outside the source mosaic');
  const col=Math.floor(px/TILE),row=Math.floor(py/TILE);
  return {x:px,y:py,gridRow:row,gridCol:col,
          tilePixel:[px-col*TILE,py-row*TILE],
          source:manifest.samples[row*GRID+col].name,
          gameRouteGeoregistered:false,historic1780Certified:false};
}
function pixelToGeo(manifest,x,y,allowOuterEdge=false){
  const v=verify(manifest);
  if(!validNumber(x)||!validNumber(y)||x<0||y<0||
     (allowOuterEdge ? x>v.dimension||y>v.dimension : x>=v.dimension||y>=v.dimension))
    throw Error('Pixel outside the source mosaic');
  const n=2**v.z;
  const gx=(v.x0*TILE+x)/(n*TILE),gy=(v.y0*TILE+y)/(n*TILE);
  return [gx*360-180,Math.atan(Math.sinh(Math.PI*(1-2*gy)))*180/Math.PI];
}
function cropForBounds(manifest,bounds){
  const v=verify(manifest);
  if(!Array.isArray(bounds)||bounds.length!==4||!bounds.every(validNumber)||
     !(bounds[0]<bounds[2]&&bounds[1]<bounds[3])) throw Error('Invalid crop geographic bounds');
  const [west,south,east,north]=bounds;
  // Geographic crop boundaries may touch the source's outer edge; pixels are
  // half-open. Exact crop expands to full source pixels, never resamples.
  if(west<v.bounds[0]-1e-11||east>v.bounds[2]+1e-11||
     south<v.bounds[1]-1e-11||north>v.bounds[3]+1e-11)
    throw Error('Crop extends beyond sourced geographic imagery');
  const n=2**v.z;
  const xp=lon=>(lon+180)/360*n*TILE-v.x0*TILE;
  const yp=lat=>mercatorY(lat)*n*TILE-v.y0*TILE;
  const left=Math.max(0,Math.floor(xp(west)+1e-7));
  const right=Math.min(v.dimension,Math.ceil(xp(east)-1e-7));
  const top=Math.max(0,Math.floor(yp(north)+1e-7));
  const bottom=Math.min(v.dimension,Math.ceil(yp(south)-1e-7));
  if(left>=right||top>=bottom) throw Error('Empty geographic pixel crop');
  const a=pixelToGeo(manifest,left,bottom,true);
  const b=pixelToGeo(manifest,right,top,true);
  return {pixelRect:[left,top,right,bottom],actualBoundsLonLat:[a[0],a[1],b[0],b[1]],
          exactSourcePixels:true,noResampling:true,gameRouteGeoregistered:false,
          navigableRouteCertified:false,productionApproved:false};
}
module.exports={verify,geoToPixel,pixelToGeo,cropForBounds};
