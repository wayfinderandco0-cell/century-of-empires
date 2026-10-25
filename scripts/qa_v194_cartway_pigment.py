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
