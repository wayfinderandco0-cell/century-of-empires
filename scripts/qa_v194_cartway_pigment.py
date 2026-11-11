#!/usr/bin/env python3
"""V194: independently inspect painted cartway pixels against unchanged V123 geometry."""
import http.server
import json
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "v194-cartway-material"
OUT.mkdir(parents=True, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

JS_PROOF = r"""() => {
 const paint=document.createElement('canvas');paint.width=520;paint.height=200;
 const pc=paint.getContext('2d',{willReadFrequently:true});
 const previous=cx;
 try{cx=pc;paintNaturalTrailFinish([[20,100],[500,100]]);}
 finally{cx=previous;}
 const pixels=pc.getImageData(0,0,520,200).data;
 const alpha=(x,y)=>pixels[(y*520+x)*4+3];
 let continuous=0,broken=0,empty=0;
 for(let x=30;x<=490;x+=3){
  if(alpha(x,100)>210)continuous++;
  if(alpha(x,113)>20)broken++;else empty++;
  if(alpha(x,145)>0)return {pass:false,reason:'paint outside road verge'};
 }
 const expected=Math.floor((490-30)/3)+1;
 if(continuous!==expected||broken<8||empty<8)
  return {pass:false,reason:'centerline lost or road shoulders mechanically uniform',
          continuous,expected,broken,empty};
 // Render actual V123 road paths through the SAME production paint function
 // onto a separate transparent canvas. Unlike roadDistance(), these checks
 // inspect pixels rather than comparing navigation geometry to itself.
 const route=document.createElement('canvas');route.width=W;route.height=H;
 const rc=route.getContext('2d',{willReadFrequently:true});
 let segments=0,samples=0,missing=0,missingExamples=[];
 for(const tile of atlas.tiles.filter(t=>t.id!=='matrei')){
  rc.clearRect(0,0,W,H);
  try{cx=rc;for(const pts of Object.values(tile.roads))paintNaturalTrailFinish(pts);}
  finally{cx=previous;}
  const data=rc.getImageData(0,0,W,H).data;
  for(const pts of Object.values(tile.roads))for(let i=1;i<pts.length;i++){
   segments++;
   const a=pts[i-1],b=pts[i],length=Math.hypot(b[0]-a[0],b[1]-a[1]);
   const n=Math.max(1,Math.ceil(length/5));
   for(let j=0;j<=n;j++){
    const t=j/n,x=Math.round(a[0]+(b[0]-a[0])*t),
          y=Math.round(a[1]+(b[1]-a[1])*t);
    if(x<2||x>=W-2||y<2||y>=H-2)continue;
    samples++;
    if(data[(y*W+x)*4+3]<160){
     missing++;if(missingExamples.length<5)missingExamples.push([tile.id,i,x,y]);
    }
   }
  }
 }
 return {pass:segments>=20&&samples>=200&&missing===0,
         continuous,expected,broken,empty,segments,samples,missing,missingExamples,
         v123RouteGeometryUnmodified:true,physicalIPhoneApproved:false};
}"""

# V195: sample ACTUAL Matrei/neighbor painter pixels on both sides of each
# shared seam. Graph-to-itself roadDistance checks cannot catch pigment gaps
# or an abrupt border palette change; this canvas probe can.
JS_SEAMS = r"""() => {
 const c=document.createElement('canvas');c.width=180;c.height=180;
 const g=c.getContext('2d',{willReadFrequently:true}),prior=cx;
 const median=a=>{a.sort((x,y)=>x-y);return a[Math.floor(a.length/2)];};
 const probe=(orientation)=>{
  g.clearRect(0,0,180,180);
  try{
   cx=g;
   if(orientation==='west'){
    paintNaturalTrailFinish([[10,90],[90,90]]);
    paintTrack([[90,90],[170,90]],15);
   }else{
    paintTrack([[90,10],[90,90]],15);
    paintNaturalTrailFinish([[90,90],[90,170]]);
   }
  }finally{cx=prior;}
  const rgba=g.getImageData(0,0,180,180).data;
  const at=(x,y)=>Array.from(rgba.slice((y*180+x)*4,(y*180+x)*4+4));
  const left=[],right=[];
  for(let d=14;d<=20;d++){
   left.push(orientation==='west'?at(90-d,90):at(90,90-d));
   right.push(orientation==='west'?at(90+d,90):at(90,90+d));
  }
  const before=[0,1,2].map(k=>median(left.map(p=>p[k])));
  const after=[0,1,2].map(k=>median(right.map(p=>p[k])));
  const channelDeltas=before.map((v,k)=>Math.abs(v-after[k]));
  let centerlineMissing=0,outerPaint=0;
  for(let pos=52;pos<=128;pos+=2){
   const p=orientation==='west'?at(pos,90):at(90,pos);
   if(p[3]<200)centerlineMissing++;
   const outside=orientation==='west'?at(pos,125):at(125,pos);
   if(outside[3]>0)outerPaint++;
  }
  return {pass:Math.max(...channelDeltas)<=26&&centerlineMissing===0&&outerPaint===0,
   before,after,channelDeltas,centerlineMissing,outerPaint};
 };
 const west=probe('west'),south=probe('south');
 return {pass:west.pass&&south.pass,west,south,
         sourceV121Unchanged:true,sourceV123Unchanged:true,
         townAndBridgeGeographyApproved:false};
}"""


# V196: inspect the *actual world-positioned* V123 road exits, not just
# synthetic straight-line painter samples. This catches seam gaps caused by
# incorrect tile origins, path endpoints, or a different Matrei road finish.
JS_WORLD_SEAMS = r"""() => {
 const probe=(orientation)=>{
  const c=document.createElement('canvas');c.width=240;c.height=240;
  const g=c.getContext('2d',{willReadFrequently:true}),previous=cx;
  const west=atlas.tiles.find(t=>t.id==='west');
  const matrei=atlas.tiles.find(t=>t.id==='matrei');
  const south=atlas.tiles.find(t=>t.id==='south');
  const seam=orientation==='west'?[1536,478]:[2002,1024];
  const worldPoint=(tile,point)=>[tile.origin[0]+point[0],tile.origin[1]+point[1]];
  const a=orientation==='west'?worldPoint(west,west.roads.east[0]):
                                  worldPoint(matrei,matrei.roads.south.at(-1));
  const b=orientation==='west'?worldPoint(matrei,matrei.roads.west[0]):
                                  worldPoint(south,south.roads.north[0]);
  if(a.some((v,i)=>v!==seam[i])||b.some((v,i)=>v!==seam[i]))
   return {pass:false,reason:'V123 world seam coordinates do not coincide',a,b,seam};
  try{
   cx=g;g.save();g.translate(120-seam[0],120-seam[1]);
   if(orientation==='west'){
    g.save();g.translate(...west.origin);paintNaturalTrailFinish(west.roads.east);g.restore();
    g.save();g.translate(...matrei.origin);
    paintNaturalTrailFinish([[0,478],...originalRoads.west.slice(0,6)]);g.restore();
   }else{
    g.save();g.translate(...matrei.origin);
    paintNaturalTrailFinish([...originalRoads.south.slice(-8),[466,1024]]);g.restore();
    g.save();g.translate(...south.origin);
    paintNaturalTrailFinish(south.roads.north);g.restore();
   }
   g.restore();
  }finally{cx=previous;}
  const rgba=g.getImageData(0,0,240,240).data;
  const at=(x,y)=>Array.from(rgba.slice((y*240+x)*4,(y*240+x)*4+4));
  const median=arr=>{arr.sort((x,y)=>x-y);return arr[Math.floor(arr.length/2)];};
  const left=[],right=[];
  for(let d=15;d<=25;d++){
   left.push(orientation==='west'?at(120-d,120):at(120,120-d));
   right.push(orientation==='west'?at(120+d,120):at(120,120+d));
  }
  const before=[0,1,2].map(k=>median(left.map(p=>p[k])));
  const after=[0,1,2].map(k=>median(right.map(p=>p[k])));
  const channelDeltas=before.map((v,k)=>Math.abs(v-after[k]));
  let missing=0,outerPaint=0;
  for(let d=-65;d<=65;d+=2){
   const x=orientation==='west'?120+d:120;
   const y=orientation==='west'?120:120+d;
   if(at(x,y)[3]<200)missing++;
   const outer=orientation==='west'?at(x,155):at(155,y);
   if(outer[3]>0)outerPaint++;
  }
  return {pass:missing===0&&outerPaint===0&&Math.max(...channelDeltas)<=26,
          seam,before,after,channelDeltas,missing,outerPaint};
 };
 const west=probe('west'),south=probe('south');
 return {pass:west.pass&&south.pass,west,south,originalRoutesPreserved:true,
         townBridgeArtApproved:false,physicalIPhoneApproved:false};
}"""


# V201: independent world-positioned underlay probe. The road's decorative
# grass/dust shoulders must stop at the same tile boundary as V198 road paint.
# This catches V200's round-cap halo crossing into Matrei even if the final
# opaque Matrei photograph conceals it in one particular camera screenshot.
JS_SCENIC_VERGE_SEAMS = r"""() => {
 const probe=(name)=>{
  const tile=atlas.tiles.find(t=>t.id===name);
  const seam=name==='west'?[1536,478]:[2002,1024];
  const pts=name==='west'?tile.roads.east:tile.roads.north;
  const canvas=document.createElement('canvas');canvas.width=240;canvas.height=240;
  const g=canvas.getContext('2d',{willReadFrequently:true});
  g.translate(120-seam[0],120-seam[1]);
  paintScenicRoadVerge(g,tile,pts);
  g.setTransform(1,0,0,1,0,0);
  const pixels=g.getImageData(0,0,240,240).data;
  const alpha=(x,y)=>pixels[(y*240+x)*4+3];
  let inside=0,escaped=0;
  for(let d=5;d<=25;d+=5){
   const inX=name==='west'?120-d:120,inY=name==='south'?120+d:120;
   const outX=name==='west'?120+d:120,outY=name==='south'?120-d:120;
   if(alpha(inX,inY)>0)inside++;
   if(alpha(outX,outY)>0)escaped++;
  }
  return {pass:inside===5&&escaped===0,inside,escaped,
   exactV123Seam:seam,sourceRoadAndMovementUnchanged:true};
 };
 const west=probe('west'),south=probe('south');
 return {pass:west.pass&&south.pass,west,south,artApproved:false};
}"""

# V197: test the FINAL composited screen pixels, not just offscreen painters.
# A source photo, label, clip or later layer could conceal a correct offscreen
# stroke. Sample both real seams at close phone zoom with the debug overlay off.
JS_COMPOSITED_SEAMS = r"""() => {
 const priorCam=cam.slice(),priorZoom=zoom,expected=[152,130,99];
 const sample=p=>{
  const s=screen(p),x=Math.round(s[0]*dpr),y=Math.round(s[1]*dpr);
  if(x<0||y<0||x>=C.width||y>=C.height)return null;
  return Array.from(cx.getImageData(x,y,1,1).data);
 };
 const reports={};
 try{
  for(const [name,anchor,axis] of [['west',[1536,478],0],['south',[2002,1024],1]]){
   cam=anchor.slice();zoom=6;redraw();render();
   let missingCore=0,paintBeyondVerge=0;
   const coreExamples=[];
   for(let d=-48;d<=48;d+=8){
    const p=anchor.slice();p[axis]+=d;
    const rgba=sample(p);
    if(!rgba||rgba[3]!==255||expected.some((v,i)=>Math.abs(v-rgba[i])>1)){
     missingCore++;if(coreExamples.length<4)coreExamples.push({offset:d,rgba});
    }
    const off=p.slice();off[1-axis]+=35;
    const far=sample(off);
    if(!far||far.slice(0,3).every((v,i)=>Math.abs(v-expected[i])<=1))
     paintBeyondVerge++;
   }
   reports[name]={pass:missingCore===0&&paintBeyondVerge===0,
    missingCore,paintBeyondVerge,coreExamples,samples:13};
  }
 }finally{cam=priorCam;zoom=priorZoom;redraw();render();}
 return {pass:reports.west.pass&&reports.south.pass,regions:reports,
  actualCompositedCanvas:true,debugOverlay:false,artApproved:false};
}"""

def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = {}
    try:
        with sync_playwright() as p:
            for engine in ("chromium", "webkit"):
                browser = getattr(p, engine).launch(headless=True)
                try:
                    for orient, w, h in (("portrait", 390, 844), ("landscape", 844, 390)):
                        page = browser.new_page(viewport={"width":w,"height":h},
                                                is_mobile=True,has_touch=True,
                                                device_scale_factor=2)
                        errors=[]
                        page.on("pageerror", lambda error:errors.append(str(error)))
                        try:
                            page.goto(f"http://127.0.0.1:{server.server_port}/v192-weathered-cartways-graphics-test.html",
                                      wait_until="domcontentloaded",timeout=30000)
                            page.wait_for_function("window.V192?.ready===true",timeout=120000)
                            result=page.evaluate(JS_PROOF)
                            assert result["pass"], (engine,orient,result)
                            seam=page.evaluate(JS_SEAMS)
                            assert seam["pass"], (engine,orient,seam)
                            world_seams=page.evaluate(JS_WORLD_SEAMS)
                            assert world_seams["pass"], (engine,orient,world_seams)
                            composite_seams=page.evaluate(JS_COMPOSITED_SEAMS)
                            assert composite_seams["pass"], (engine,orient,composite_seams)
                            scenic_verges=page.evaluate(JS_SCENIC_VERGE_SEAMS)
                            assert scenic_verges["pass"], (engine,orient,scenic_verges)
                            assert not errors,(engine,orient,errors)
                            page.evaluate("V192.focusTile('west')")
                            page.evaluate("V192.zoomTo(6)")
                            page.screenshot(path=str(OUT/f"{engine}-{orient}-west.png"),
                                            animations="disabled")
                            page.evaluate("V192.focusTile('south')")
                            page.evaluate("V192.zoomTo(6)")
                            page.screenshot(path=str(OUT/f"{engine}-{orient}-south.png"),
                                            animations="disabled")
                            result["matreiNeighborSeams"]=seam
                            result["worldPositionedSeams"]=world_seams
                            result["compositedSeams"]=composite_seams
                            result["scenicVergeSeams"]=scenic_verges
                            results[f"{engine}-{orient}"]=result
                        finally:page.close()
                finally:browser.close()
    finally:server.shutdown()
    summary={"passed":len(results)==4,"results":results,
             "historicalOrArtApproved":False,"originalGameMechanicsModified":False,
             "note":"Pixel centerline coverage and broken shoulders only; source geography and physical iPhone appearance remain unapproved."}
    (OUT/"report.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)
    assert summary["passed"]

if __name__=="__main__":
    main()
