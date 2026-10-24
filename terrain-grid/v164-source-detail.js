/* V164 experimental source-derived detail recovery for the unregistered V102
 * relief material. A bounded luminance high-pass ONLY sharpens existing source
 * features: it does not invent trees, roads, settlements or georegistration.
 * Original V121 painting and V123 geometry are not inputs to this function.
 */
(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 else root.V164SourceDetail=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const luma=(r,g,b)=>.2126*r+.7152*g+.0722*b;
 function enhance(pixels,width,height,{radius=2,strength=.85,maxDelta=18}={}){
  if(!(pixels instanceof Uint8ClampedArray)||
     !Number.isInteger(width)||!Number.isInteger(height)||
     width<2*radius+1||height<2*radius+1||
     pixels.length!==width*height*4||
     !Number.isInteger(radius)||radius<1||radius>4||
     !Number.isFinite(strength)||strength<0||strength>1.5||
     !Number.isFinite(maxDelta)||maxDelta<0||maxDelta>32)
    throw Error('V164 invalid source-image detail parameters');
  const out=new Uint8ClampedArray(pixels);
  const offsets=[-radius*width*4,radius*width*4,-radius*4,radius*4,
    -(width+1)*radius*4,(width+1)*radius*4,
    -(width-1)*radius*4,(width-1)*radius*4];
  let changed=0,absoluteShift=0,maxObservedDelta=0;
  for(let y=radius;y<height-radius;y++)for(let x=radius;x<width-radius;x++){
   const i=(y*width+x)*4;
   const here=luma(pixels[i],pixels[i+1],pixels[i+2]);
   let around=0;
   for(const d of offsets)around+=luma(pixels[i+d],pixels[i+d+1],pixels[i+d+2]);
   const shift=Math.max(-maxDelta,Math.min(maxDelta,(here-around/8)*strength));
   if(Math.abs(shift)<.5)continue;
   for(let k=0;k<3;k++)out[i+k]=Math.max(0,Math.min(255,pixels[i+k]+shift));
   changed++;absoluteShift+=Math.abs(shift);
   maxObservedDelta=Math.max(maxObservedDelta,Math.abs(shift));
  }
  return {pixels:out,report:{
   version:164,sourceOnly:true,algorithm:'bounded-eight-neighbor-source-luma',
   radius,strength,maxDelta,changedPixels:changed,
   meanShiftOverChangedPixels:changed?+(absoluteShift/changed).toFixed(4):0,
   maxObservedDelta:+maxObservedDelta.toFixed(4),
   addsNewGeographicFeatures:false,routeGeoregistered:false,
   historicalLandcoverVerified:false,productionApproved:false
  }};
 }
 return Object.freeze({enhance});
});
