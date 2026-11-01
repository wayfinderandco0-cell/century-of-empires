/* V267 playability ledger. Counts real V123-connected tiles, NOT displayed art.
 * Pure JS shared by native game and Node QA. No save/campaign mutation.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=="undefined"&&module.exports)module.exports=api;
 else root.COEAtlasPlayability=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 "use strict";
 function audit(atlas,manifest){
  if(!atlas||!atlas.network||!Array.isArray(atlas.tiles)||!manifest)throw Error("Missing atlas network or manifest");
  const known=new Set(atlas.tiles.map(t=>t.id)),visited=new Set(),queue=["matrei"];
  while(queue.length){
   const id=queue.shift();
   if(visited.has(id)||!known.has(id))continue;
   visited.add(id);
   for(const seam of atlas.network.seams){
    if(!seam.pass)continue;
    const link=atlas.links.find(l=>l.id===seam.id);
    if(!link)continue;
    const a=link.from.tile,b=link.to.tile;
    if(a===id&&!visited.has(b))queue.push(b);
    if(b===id&&!visited.has(a))queue.push(a);
   }
  }
  const playableIds=[...visited].sort();
  const baseline=["matrei","south","west"];
  if(baseline.some(id=>!visited.has(id)))throw Error("Approved three-tile V123 network disconnected");
  const candidateIds=(manifest.artCandidates||[])
   .filter(c=>Array.isArray(c.nativeWorldOrigin)&&c.nativeWorldOrigin.length===2)
   .map(c=>c.id).sort();
  const newlyConnected=playableIds.filter(id=>!baseline.includes(id));
  const finishedIds=(manifest.artCandidates||[]).filter(c=>
   newlyConnected.includes(c.id)&&c.playableIntegrated===true&&
   c.roadSeamsVerified===true&&c.userApproval===true&&
   c.webKitVerified===true).map(c=>c.id).sort();
  return Object.freeze({
   baselinePlayable:baseline.length,
   playableIds:Object.freeze(playableIds),
   connectedNew:Object.freeze(newlyConnected),
   displayOnlyCandidateIds:Object.freeze(candidateIds.filter(id=>!visited.has(id))),
   finishedIds:Object.freeze(finishedIds),
   blockedSeams:Object.freeze(atlas.network.seams.filter(s=>!s.pass).map(s=>({id:s.id,errors:s.errors.slice()}))),
   label:playableIds.length+" PLAYABLE · "+candidateIds.filter(id=>!visited.has(id)).length+" ART-ONLY · "+finishedIds.length+" NEW FINISHED"
  });
 }
 return Object.freeze({audit});
});
