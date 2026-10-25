/* V178: exact SOURCE L (EPSG:3857) -> existing geographic atlas crosswalk.
   Modern basemap source is not a historical game road or a V121/V123 registration. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.COEGeoSourceV178 = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const Z = 17, TILE = 256, N = 2 ** Z, W = 1536, H = 1024;
  const CENTER = [11.520, 47.130];
  const PI = Math.PI, RAD = PI / 180;
  const SECTORS = Object.freeze({
    'source-west': [0, 0, 768, 512],
    'source-center': [768, 0, 1536, 512],
    'source-south': [768, 512, 1536, 1024]
  });
  const V97 = { bounds: [11.26, 46.80, 11.80, 47.42], size: [1552, 1782] };
  const V102 = { bounds: [11.43, 47.075, 11.625, 47.19], size: [257, 257] };
  const V94 = { bounds: [-14, 26, 49, 75], game: [1448, 1086], atlas: [8192, 6144] };
  function requireOK(ok, message) { if (!ok) throw new Error(message); }
  function mercator(lon, lat) {
    requireOK(Number.isFinite(lon) && Number.isFinite(lat) &&
      lon >= -180 && lon <= 180 && Math.abs(lat) < 85.05112878, 'invalid lon/lat');
    return [(lon + 180) / 360 * N * TILE,
      (1 - Math.asinh(Math.tan(lat * RAD)) / PI) / 2 * N * TILE];
  }
  const [cx, cy] = mercator(...CENTER);
  const ORIGIN = [Math.floor(cx / TILE) - 4, Math.floor(cy / TILE) - 1];
  function sourceToLonLat(x, y) {
    requireOK(Number.isFinite(x) && Number.isFinite(y) &&
      x >= 0 && x <= W && y >= 0 && y <= H, 'source pixel outside geographic footprint');
    const mx = ORIGIN[0] * TILE + x, my = ORIGIN[1] * TILE + y;
    return [mx / (N * TILE) * 360 - 180,
      Math.atan(Math.sinh(PI * (1 - 2 * my / (N * TILE)))) / RAD];
  }
  function lonLatToSource(lon, lat) {
    const [mx, my] = mercator(lon, lat);
    const x = mx - ORIGIN[0] * TILE, y = my - ORIGIN[1] * TILE;
    requireOK(x >= -1e-7 && x <= W + 1e-7 && y >= -1e-7 && y <= H + 1e-7,
      'location outside V168 acquired geographic footprint');
    return [Math.max(0, Math.min(W, x)), Math.max(0, Math.min(H, y))];
  }
  function sectorAt(x, y) {
    if (!Number.isFinite(x) || !Number.isFinite(y) ||
        x < 0 || y < 0 || x >= W || y >= H) return null;
    if (x < 768 && y >= 512) return null; // unacquired SW quadrant
    return x < 768 ? 'source-west' : (y < 512 ? 'source-center' : 'source-south');
  }
  function toRaster(lon, lat, bounds, size) {
    const [west, south, east, north] = bounds;
    requireOK(lon >= west && lon <= east && lat >= south && lat <= north,
      'source point outside target geographic atlas');
    return [(lon - west) / (east - west) * size[0],
      (north - lat) / (north - south) * size[1]];
  }
  function sourceToAtlases(x, y) {
    const sector = sectorAt(x, y);
    requireOK(sector !== null, 'unknown/outside source pixel cannot be mapped as observed');
    const [lon, lat] = sourceToLonLat(x, y);
    return {
      sourceSector: sector, lonLat: [lon, lat],
      v97ReliefPixel: toRaster(lon, lat, V97.bounds, V97.size),
      v102GridPixel: toRaster(lon, lat, V102.bounds, V102.size),
      v94GamePixel: toRaster(lon, lat, V94.bounds, V94.game),
      v94AtlasPixel: toRaster(lon, lat, V94.bounds, V94.atlas),
      sourceReferenceOnly: true, playableRoad: false, bridgeBankVerified: false,
      v123GameRegistered: false, historical1780Certified: false
    };
  }
  function verifyManifests(v94, v97, v102) {
    requireOK(v94?.version === '94' && v94.projection === 'equirectangular' &&
      JSON.stringify(v94.extent) === '[-14,26,49,75]' &&
      JSON.stringify(v94.gameSize) === '[1448,1086]' &&
      JSON.stringify(v94.atlasSize) === '[8192,6144]', 'V94 atlas identity/projection mismatch');
    requireOK(JSON.stringify(v97?.boundsLonLat) === '[11.26,46.8,11.8,47.42]' &&
      JSON.stringify(v97.imageSize) === '[1552,1782]' &&
      v97.elevationSource?.includes('Copernicus'), 'V97 geographic relief identity mismatch');
    requireOK(v102?.version === 102 &&
      JSON.stringify(v102.boundsLonLat) === '[11.43,47.075,11.625,47.19]' &&
      JSON.stringify(v102.grid) === '[257,257]' &&
      JSON.stringify(v102.broadBoundsLonLat) === '[11.26,46.8,11.8,47.42]',
      'V102 local relief extent mismatch');
    return true;
  }
  function crosswalk() {
    const sectors = {};
    for (const [id, [x0, y0, x1, y1]] of Object.entries(SECTORS)) {
      const nw = sourceToLonLat(x0, y0), se = sourceToLonLat(x1, y1);
      // The corners describe a geographic footprint, NOT observed road pixels.
      sectors[id] = {
        sourcePixelBounds: [x0, y0, x1, y1],
        geographicBoundsLonLat: [nw[0], se[1], se[0], nw[1]].map(v => +v.toFixed(10)),
        v97ReliefBoundsPx: [
          ...toRaster(...nw, V97.bounds, V97.size),
          ...toRaster(...se, V97.bounds, V97.size)
        ].map(v => +v.toFixed(7)),
        v94AtlasBoundsPx: [
          ...toRaster(...nw, V94.bounds, V94.atlas),
          ...toRaster(...se, V94.bounds, V94.atlas)
        ].map(v => +v.toFixed(7))
      };
    }
    return {
      version: 178, crs: 'EPSG:3857', sourceZoom: Z, tileOriginXYZ: [...ORIGIN, Z],
      sourcePixelDimensions: [W, H], sourceCenterLonLat: [...CENTER],
      sectors, unobservedSouthwest: [0, 512, 768, 1024],
      sourceReferenceOnly: true, sourceSectorsAreGameOctagons: false,
      v121ToGeographyRegistered: false, v123RoadsGeoregistered: false,
      bridgeBanksVerified: false, historicalRoadsVerified: false,
      periodArtComplete: false, physicalIPhoneApproved: false, productionApproved: false,
      note: 'Coordinate transform is exact for SOURCE imagery; no V121 painted-art landmark correspondence.'
    };
  }
  return { ORIGIN, SECTORS, sourceToLonLat, lonLatToSource, sectorAt,
    sourceToAtlases, verifyManifests, crosswalk };
});
