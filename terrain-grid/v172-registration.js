'use strict';
// Candidate-only alignment between V121 GAME coordinates and V168/169 SOURCE pixels.
// A plausible affine fit never proves that landmarks or 1780 roads are real.
const KINDS = new Set(['ridge','summit','valley-fork','river-confluence','bedrock-feature','saddle']);
const SHA = /^[0-9a-f]{64}$/i;
function requireOK(condition, message) { if (!condition) throw new Error(message); }
function point(p, width, height) {
  return Array.isArray(p) && p.length===2 && p.every(Number.isFinite) &&
    p[0]>=0 && p[0]<width && p[1]>=0 && p[1]<height &&
    (p[1]<height/2 || p[0]>=width/2); // southwest quadrant is not sourced
}
function validateEvidence(manifest) {
  requireOK(manifest && manifest.version===172 && manifest.sourceVersion===169 &&
    manifest.sourceCrs==='EPSG:3857' && manifest.sourceImageSize?.join(',')==='1536,1024' &&
    manifest.gameImageSize?.join(',')==='3072,2048', 'untrusted source/game coordinate frames');
  requireOK(SHA.test(manifest.sourceMosaicSha256||'') && SHA.test(manifest.gameArtSha256||''),
    'source and original game-art SHA256 identities required');
  for (const flag of ['productionApproved','v123RoadsGeoregistered','historicalRoadsVerified',
    'bridgeBanksVerified','physicalIPhoneApproved','historic1780Certified'])
    requireOK(manifest[flag]===false, 'forged historical/game approval: '+flag);
  const training=manifest.controls, holdouts=manifest.holdouts;
  requireOK(Array.isArray(training) && training.length>=4 && Array.isArray(holdouts) && holdouts.length>=2,
    'at least four reviewed controls and two independent holdouts required');
  const ids=new Set(), gamePositions=new Set(), sourcePositions=new Set(), kinds=new Set();
  for (const item of [...training,...holdouts]) {
    requireOK(item && typeof item.id==='string' && item.id.length>2 && !ids.has(item.id),
      'missing or repeated landmark identity');
    ids.add(item.id);
    requireOK(KINDS.has(item.kind), 'modern road, roof, bridge or unsupported landmark cannot register geography');
    kinds.add(item.kind);
    requireOK(item.independentlyReviewed===true && typeof item.gameEvidence==='string' &&
      item.gameEvidence.length>=12 && typeof item.sourceEvidence==='string' &&
      item.sourceEvidence.length>=12 && item.gameEvidence!==item.sourceEvidence,
      'independent evidence required for BOTH imagery frames');
    requireOK(point(item.game,3072,2048) && point(item.source,1536,1024),
      'landmark outside observed L-shaped source/game footprint');
    const g=item.game.join(','),s=item.source.join(',');
    requireOK(!gamePositions.has(g) && !sourcePositions.has(s), 'duplicate geographic control');
    gamePositions.add(g);sourcePositions.add(s);
  }
  requireOK(kinds.size>=3,'independent landmarks must span at least three feature types');
  return {training,holdouts};
}
function solve3(a,b) {
  const m=a.map((row,i)=>[...row,b[i]]);
  for (let k=0;k<3;k++) {
    let pivot=k;for(let i=k+1;i<3;i++)if(Math.abs(m[i][k])>Math.abs(m[pivot][k]))pivot=i;
    requireOK(Math.abs(m[pivot][k])>1e-8,'collinear or numerically singular landmarks');
    [m[k],m[pivot]]=[m[pivot],m[k]];
    const v=m[k][k];for(let j=k;j<4;j++)m[k][j]/=v;
    for(let i=0;i<3;i++)if(i!==k){const q=m[i][k];for(let j=k;j<4;j++)m[i][j]-=q*m[k][j];}
  }
  return m.map(row=>row[3]);
}
function fitAxis(controls, axis) {
  const gram=Array.from({length:3},()=>[0,0,0]), rhs=[0,0,0];
  for(const p of controls){const x=[p.game[0],p.game[1],1];
    for(let i=0;i<3;i++){rhs[i]+=x[i]*p.source[axis];for(let j=0;j<3;j++)gram[i][j]+=x[i]*x[j];}}
  return solve3(gram,rhs);
}
function mapPoint(matrix,game){return matrix.map(c=>c[0]*game[0]+c[1]*game[1]+c[2]);}
function fitCandidate(manifest,{maxHoldoutErrorPx=3}={}) {
  const {training,holdouts}=validateEvidence(manifest);
  requireOK(Number.isFinite(maxHoldoutErrorPx) && maxHoldoutErrorPx>0 && maxHoldoutErrorPx<=8,
    'untrusted holdout tolerance');
  const matrix=[fitAxis(training,0),fitAxis(training,1)];
  const det=matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0];
  requireOK(det>0.01 && det<16,'mirrored or implausibly scaled geographic transform');
  const errors=items=>items.map(p=>Math.hypot(...mapPoint(matrix,p.game).map((v,i)=>v-p.source[i])));
  const trainErrors=errors(training), holdoutErrors=errors(holdouts);
  const maxHoldout=Math.max(...holdoutErrors);
  return {candidatePass:maxHoldout<=maxHoldoutErrorPx,
    matrix:matrix.map(row=>row.map(v=>Number(v.toFixed(9)))),
    determinant:Number(det.toFixed(9)),
    trainingRmsPx:Number(Math.sqrt(trainErrors.reduce((s,e)=>s+e*e,0)/trainErrors.length).toFixed(6)),
    independentHoldoutErrorsPx:holdoutErrors.map(e=>Number(e.toFixed(6))),
    maxHoldoutErrorPx:Number(maxHoldout.toFixed(6)),
    gameRouteGeoregistered:false, bridgeBanksVerified:false, historicalRoadsVerified:false,
    productionApproved:false, physicalIPhoneApproved:false,
    note:'Numerical candidate only. Reviewed evidence does not certify a painted bridge or historic roads.'};
}
module.exports={validateEvidence,fitCandidate,mapPoint};
