/* V267 original-art expansion gate. This is a manifest/graph validator, not a renderer
 * and it NEVER upgrades unreviewed terrain or source photos into finished art.
 * The protected WEST/MATREI/SOUTH assets and V123 graph remain authoritative.
 */
(function(root,factory){
  const api=factory();
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  else root.COEV267ArtContract=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const REF="456107f28c8db1f87522bbc7511809b2a215f6fb";
  const W=1536,H=1024,C=256;
  const BASE={
    west:{origin:[0,0],art:"art-reviews/v267-original-source/west-unified-native-border-unapproved.webp"},
    matrei:{origin:[1536,0],art:"terrain-grid/art/matrei-v121-original.webp"},
    south:{origin:[1536,1024],art:"art-reviews/v267-original-source/south-unified-native-border-unapproved.webp"}
  };
  const opposites={north:"south",south:"north",east:"west",west:"east"};
  const fail=(message)=>{throw Error("V267 art contract: "+message);};
  const same=(a,b)=>Array.isArray(a)&&Array.isArray(b)&&a.length===b.length&&a.every((v,i)=>v===b[i]);
  const sha=s=>typeof s==="string"&&/^[a-f0-9]{64}$/i.test(s);
  const coordinate=p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite);
  const key=p=>p.join(",");
  function assertBase(m){
    if(!m||m.schema!=="coe-atlas-cells/v1"||m.referenceCommit!==REF)fail("approved baseline/ref changed");
    if(!m.geometry||m.geometry.width!==W||m.geometry.height!==H||m.geometry.corner!==C)fail("V123 geometry drift");
    const cells=new Map((m.cells||[]).map(c=>[c.id,c]));
    if(cells.size!==3||m.cells.length!==3)fail("baseline must have exactly three locked cells");
    for(const [id,expected] of Object.entries(BASE)){
      const c=cells.get(id);
      if(!c||!same(c.origin,expected.origin)||c.art!==expected.art||c.artMethodApproved!==true)fail(id+" source/placement drift");
      if(c.geoVerified!==false||c.strategicNodes?.length||c.provinceIds?.length)fail(id+" invented historical/conquest claim");
    }
    const seams=new Map((m.fixedSeams||[]).map(s=>[s.id,s]));
    if(seams.size!==2||!same(seams.get("west-matrei")?.world,[1536,478])||
       !same(seams.get("matrei-south")?.world,[2002,1024]))fail("protected road seams drift");
    if((m.decorativeInlays||[]).some(i=>i.playable!==false||i.roads?.length))fail("road or gameplay in decorative gap");
    if(m.semantics?.tileIsProvince!==false||m.semantics?.scenicIsCapturable!==false)fail("scenic/strategic semantics drift");
    return true;
  }
  function validateCell(c){
    if(!c||typeof c.id!=="string"||!/^[a-z0-9][a-z0-9-]{2,50}$/.test(c.id)||BASE[c.id])fail("invalid/new cell id");
    if(!coordinate(c.origin)||c.origin.some((v,i)=>v<0||v%(i?H:W)!==0))fail(c.id+" off-grid origin");
    if(typeof c.biome!=="string"||!c.biome.trim())fail(c.id+" missing geographic biome");
    if(c.scenicSettlements?.some(s=>s.capturable||s.provinceId))fail(c.id+" scenic village cannot be capturable");
    if(c.strategicNodes?.length||c.provinceIds?.length)fail(c.id+" unverified strategic node: add explicit sourced scenario first");
    if(c.historicalVerified&&(!c.scenarioDate||!Array.isArray(c.historicalSources)||!c.historicalSources.length))fail(c.id+" unsupported history claim");
    if(c.art){
      if(!/^([a-z0-9-]+\/)*[a-z0-9_.-]+\.(webp|png)$/i.test(c.art)||/factory-photo|photo-batch|v267-relief-pilot|heightmesh|aerial/i.test(c.art))fail(c.id+" prohibited flat/photo/heightmesh art path");
      if(!sha(c.assetSha256)||c.visualGrammar!=="v267-original-layered-landscape")fail(c.id+" missing original asset provenance");
    } else if(c.originalArtComposed||c.visuallyReviewed||c.mobileWebkitRendered||c.nativePlayable||c.userApproved)fail(c.id+" status without actual art");
    if(c.originalArtComposed&&!c.art)fail(c.id+" missing composed art");
    if(c.userApproved&&!c.visuallyReviewed)fail(c.id+" approval without visual review");
    if(c.nativePlayable&&!c.mobileWebkitRendered)fail(c.id+" playability without WebKit");
    for(const p of c.roadPorts||[]){
      if(!opposites[p.side]||!coordinate(p.local)||typeof p.routeId!=="string"||!p.routeId)fail(c.id+" invalid road port");
      const [x,y]=p.local;
      if(p.side==="north"&&(y!==0||x<C||x>W-C)||
         p.side==="south"&&(y!==H||x<C||x>W-C)||
         p.side==="west"&&(x!==0||y<C||y>H-C)||
         p.side==="east"&&(x!==W||y<C||y>H-C))fail(c.id+" road not on flat octagon edge");
    }
    return true;
  }
  function validateBatch(batch,base){
    assertBase(base);
    if(!batch||batch.schema!=="coe-v267-original-art-batch/v1"||batch.referenceCommit!==REF)fail("wrong batch schema/ref");
    if(!Array.isArray(batch.cells)||batch.cells.length<8||batch.cells.length>16)fail("batch must describe 8–16 new cells");
    const byId=new Map(),byOrigin=new Map();
    const protectedOrigins=new Set(Object.values(BASE).map(c=>key(c.origin)));
    for(const c of batch.cells){
      validateCell(c);
      if(byId.has(c.id)||byOrigin.has(key(c.origin))||protectedOrigins.has(key(c.origin)))fail("duplicate id or overlapping protected cell");
      byId.set(c.id,c);byOrigin.set(key(c.origin),c);
    }
    const edges=new Set();
    for(const l of batch.links||[]){
      if(!l||typeof l.id!=="string"||edges.has(l.id))fail("duplicate/invalid road link");
      edges.add(l.id);
      const a=byId.get(l.from?.cell),b=byId.get(l.to?.cell);
      if(!a||!b||a===b)fail("links must connect new real cells; protected V123 requires explicit graph integration");
      const pa=(a.roadPorts||[]).find(p=>p.id===l.from.port),pb=(b.roadPorts||[]).find(p=>p.id===l.to.port);
      if(!pa||!pb||opposites[pa.side]!==pb.side||pa.routeId!==pb.routeId)fail(l.id+" unmatched canonical road ports");
      const wa=[a.origin[0]+pa.local[0],a.origin[1]+pa.local[1]];
      const wb=[b.origin[0]+pb.local[0],b.origin[1]+pb.local[1]];
      if(!same(wa,wb))fail(l.id+" road seam world mismatch");
    }
    for(const c of batch.cells)for(const p of c.roadPorts||[]){
      if(!(batch.links||[]).some(l=>(l.from.cell===c.id&&l.from.port===p.id)||(l.to.cell===c.id&&l.to.port===p.id)))fail(c.id+" orphan road port");
    }
    if((batch.decorativeInlays||[]).some(i=>i.playable!==false||i.roads?.length||i.roadPorts?.length))fail("phantom road in decorative gap");
    return counts(batch);
  }
  function counts(batch){
    const cells=batch.cells||[];
    const original=c=>c.originalArtComposed===true&&!!c.art&&sha(c.assetSha256)&&c.visualGrammar==="v267-original-layered-landscape";
    const connected=c=>(c.roadPorts||[]).length>0&&c.roadSeamsVerified===true;
    const finished=c=>original(c)&&c.visuallyReviewed===true&&connected(c)&&
      c.mobileWebkitRendered===true&&c.nativePlayable===true&&
      c.historicalVerified===true&&c.userApproved===true;
    return Object.freeze({
      candidateMetadata:cells.length,
      originalArtComposed:cells.filter(original).length,
      visuallyReviewed:cells.filter(c=>original(c)&&c.visuallyReviewed===true).length,
      roadConnected:cells.filter(connected).length,
      mobileWebkitRendered:cells.filter(c=>c.mobileWebkitRendered===true).length,
      historicallyVerified:cells.filter(c=>c.historicalVerified===true).length,
      nativePlayable:cells.filter(c=>c.nativePlayable===true).length,
      userApproved:cells.filter(c=>c.userApproved===true).length,
      netFinishedToday:cells.filter(finished).length
    });
  }
  return Object.freeze({REF,BASE,assertBase,validateCell,validateBatch,counts});
});
