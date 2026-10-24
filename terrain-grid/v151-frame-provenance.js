/* V151: identity and incompatibility guard between the original V121
 * illustrative painting and V147/V150 MODERN geographically indexed imagery.
 * This code never invents a geographic mapping, navigable road, or bridge.
 */
'use strict';
const crypto = require('node:crypto');
const pixels = require('./v148-orthophoto-pixels.js');
const landmarks = require('./v150-landmark-evidence.js');
const V121_HTML_GIT_BLOB = '4c6aa5cda9e7c359b6d2a49d5b5fe8a597346382';
const V150_SOURCE_MOSAIC_SHA256 = '60442861e980ded4acfb776a54b7b4dec3bdfe0b93bfff575fbfa486399f8e8e';
const SHA256 = /^[0-9a-f]{64}$/;
const TILES = ['west', 'matrei', 'south'];
const hash = (data, algorithm='sha256') => crypto.createHash(algorithm).update(data).digest('hex');
function originalArt(html, expectedBlobSha=V121_HTML_GIT_BLOB) {
  if (typeof html !== 'string' || !/^[a-f0-9]{40}$/.test(expectedBlobSha))
    throw Error('Original V121 HTML and pinned git blob SHA required');
  const raw=Buffer.from(html,'utf8');
  const blobSha=hash(Buffer.concat([Buffer.from('blob '+raw.length+'\0'),raw]),'sha1');
  if(blobSha!==expectedBlobSha) throw Error('V121 original painting HTML identity changed; review before using');
  const matches=[...html.matchAll(/src\s*=\s*["']data:image\/webp;base64,([A-Za-z0-9+/=]+)["']/g)];
  if(matches.length!==1) throw Error('Expected exactly one original V121 WebP painting');
  const encoded=matches[0][1];
  const webp=Buffer.from(encoded,'base64');
  if(webp.toString('base64')!==encoded || webp.length<30 ||
     webp.toString('ascii',0,4)!=='RIFF' || webp.toString('ascii',8,12)!=='WEBP' ||
     webp.toString('ascii',12,16)!=='VP8 ' ||
     webp.readUInt32LE(4)+8!==webp.length ||
     webp[23]!==0x9d || webp[24]!==0x01 || webp[25]!==0x2a)
    throw Error('V121 embedded painting WebP is not intact');
  const width=webp.readUInt16LE(26)&0x3fff;
  const height=webp.readUInt16LE(28)&0x3fff;
  if(width!==1536 || height!==1024)
    throw Error('V121 original painting dimensions changed');
  return Object.freeze({sourceFile:'v121-octagon-1-painted-road.html',
    gitBlobSha1:blobSha,imageSha256:hash(webp),dimensions:[width,height],
    kind:'illustrative-painting',geographicallyRegistered:false});
}
function audit(html,manifest,observations) {
  const art=originalArt(html);
  const sourceGrid=pixels.verify(manifest);
  if(!SHA256.test(manifest.mosaicSha256||'') ||
     manifest.mosaicSha256!==V150_SOURCE_MOSAIC_SHA256)
    throw Error('V147 modern orthophoto mosaic hash differs from reviewed V150 evidence');
  const evidence=landmarks.packet(manifest,observations);
  if(evidence.observations.length!==3 ||
     evidence.observations.some(f=>f.status!=='unverified-observation' ||
       f.visualLandmarkAuthenticated!==false || f.matchedV123RoadVertex!==null ||
       f.matchedGameOctagon!==null || f.historicalRoadVerified!==false ||
       f.mosaicSha256!==manifest.mosaicSha256) ||
     evidence.v123RouteTiePoints.length!==0 || evidence.v123RoadsMapped!==false)
    throw Error('Modern source observations cannot be promoted into V123 controls');
  return Object.freeze({version:151,originalArt:art,
    modernSource:{provider:manifest.provider,mosaicSha256:manifest.mosaicSha256,
      sourcePixelDimensions:[sourceGrid.dimension,sourceGrid.dimension],
      boundsLonLat:sourceGrid.bounds,attribution:manifest.requiredAttribution,
      candidateCount:evidence.observations.length},
    gameOctagons:Object.fromEntries(TILES.map(tile=>[tile,{
      independentMatchedControls:0,requiredMatchedControls:3,
      originalArtToGeographyRegistered:false,deepZoomArtApproved:false,
      bridgeBankOrRoadContinuationCertified:false}])),
    geographicFramesMatched:false,sourceImageryIsGameArt:false,
    bridgeBanksVerified:false,navigableRouteCertified:false,
    historic1780Certified:false,physicalIPhoneApproved:false,
    productionApproved:false,
    blocker:'No independently corroborated V121-to-source landmark matches: 2 fit controls plus 1 holdout per corridor. The Navis modern mosaic is NOT the Matrei painting.'});
}
function assertNoUnreviewedPromotion(report){
  if(!report||report.version!==151 ||
     report.geographicFramesMatched!==false || report.sourceImageryIsGameArt!==false ||
     report.bridgeBanksVerified!==false || report.navigableRouteCertified!==false ||
     report.historic1780Certified!==false || report.physicalIPhoneApproved!==false ||
     report.productionApproved!==false || !report.gameOctagons ||
     TILES.some(t=>!report.gameOctagons[t] ||
       report.gameOctagons[t].independentMatchedControls!==0 ||
       report.gameOctagons[t].requiredMatchedControls!==3 ||
       report.gameOctagons[t].originalArtToGeographyRegistered!==false ||
       report.gameOctagons[t].deepZoomArtApproved!==false ||
       report.gameOctagons[t].bridgeBankOrRoadContinuationCertified!==false))
    throw Error('Unreviewed V121/V147 frame must not enable routes, bridge, deep zoom or release');
  return true;
}
module.exports={originalArt,audit,assertNoUnreviewedPromotion,V121_HTML_GIT_BLOB,V150_SOURCE_MOSAIC_SHA256};
