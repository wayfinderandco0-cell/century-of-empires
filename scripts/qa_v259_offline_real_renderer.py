#!/usr/bin/env python3
"""V259: real V249 game renderer with exact local art, no URL navigation.

Playwright about:blank lacks WebCrypto. SHA-256 is computed by Python through a
binding, using the ORIGINAL bytes; no fake hashes or modified route geometry.
This is isolated unapproved art review, not an iPhone/WebKit acceptance claim.
"""
import argparse,base64,hashlib,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CONFIGS=(("chromium","portrait",390,844),("chromium","landscape",844,390),
         ("webkit","portrait",390,844),("webkit","landscape",844,390))

def run(root,west,south,out,engines=("chromium","webkit"),chromium_executable=None):
    out.mkdir(parents=True,exist_ok=True)
    sources={}
    for tile,path in (("west",west),("south",south)):
        raw=path.read_bytes();suffix=path.suffix.lower()
        if suffix not in (".png",".webp",".jpg",".jpeg"):raise ValueError("PNG/JPEG/WebP required")
        sources[tile]={"base64":base64.b64encode(raw).decode(),
                       "sha256":hashlib.sha256(raw).hexdigest(),
                       "mime":{".png":"image/png",".webp":"image/webp",
                               ".jpg":"image/jpeg",".jpeg":"image/jpeg"}[suffix]}
    if sources["west"]["sha256"]==sources["south"]["sha256"]:raise ValueError("Duplicate source images")
    html=(root/"v249-pinned-source-art-review.html").read_text()
    names=re.findall(r'<script\s+src="([^"]+)"\s*></script>',html)
    scripts=re.findall(r"<script>([\s\S]*?)</script>",html)
    if len(scripts)!=1 or len(names)<8:raise ValueError("V249 source structure changed")
    shell=re.sub(r'<script(?:\s+src="[^"]+")?>[\s\S]*?</script>',"",html)
    v121=(root/"v121-octagon-1-painted-road.html").read_text()
    manifest=(root/"terrain-v224/assets/manifest.json").read_text()
    report={"version":259,"actualRenderer":"V249","mode":"OFFLINE_IN_MEMORY",
            "sourceSha256":{k:v["sha256"] for k,v in sources.items()},
            "configs":{},"productionApproved":False,"userVisualApproval":False,
            "historicalRoadVerified":False,"independentTiepointsVerified":False,
            "bridgeBanksVerified":False,"strictV203Passed":False}
    with sync_playwright() as pw:
        for engine,orientation,w,h in CONFIGS:
            if engine not in engines:continue
            opts={"executable_path":chromium_executable} if engine=="chromium" and chromium_executable else {}
            browser=getattr(pw,engine).launch(headless=True,**opts)
            page=browser.new_page(viewport={"width":w,"height":h},
                                  device_scale_factor=2,is_mobile=True,has_touch=True)
            key=engine+"-"+orientation;errors=[]
            page.on("pageerror",lambda error:errors.append(str(error)))
            try:
                page.set_content(shell,wait_until="domcontentloaded")
                page.expose_binding("__v259sha256",lambda source,b64:list(hashlib.sha256(base64.b64decode(b64)).digest()))
                page.evaluate("""({v121,manifest})=>{
                  window.__V121=v121;window.__MANIFEST=manifest;
                  window.fetch=async input=>{
                    const url=String(input);
                    if(url==='v121-octagon-1-painted-road.html')
                      return new Response(window.__V121,{status:200,headers:{'content-type':'text/html'}});
                    if(url==='terrain-v224/assets/manifest.json')
                      return new Response(window.__MANIFEST,{status:200,headers:{'content-type':'application/json'}});
                    throw Error('Unapproved offline fetch blocked: '+url);
                  };
                  Object.defineProperty(window,'crypto',{configurable:true,value:{subtle:{
                    digest:async(algo,buffer)=>{
                      if(algo!=='SHA-256')throw Error('SHA-256 only');
                      const a=new Uint8Array(buffer);let s='';
                      for(let i=0;i<a.length;i+=8192)s+=String.fromCharCode(...a.subarray(i,i+8192));
                      return new Uint8Array(await window.__v259sha256(btoa(s))).buffer;
                    }}}});
                }""",{"v121":v121,"manifest":manifest})
                for name in names:page.add_script_tag(content=(root/name).read_text())
                page.add_script_tag(content=scripts[0])
                page.wait_for_function("window.V192?.ready===true",timeout=90000)
                for tile in ("west","south"):
                    source=sources[tile]
                    record=page.evaluate("""async ({tile,b64,sha,mime})=>{
                      const binary=atob(b64),bytes=new Uint8Array(binary.length);
                      for(let i=0;i<bytes.length;i++)bytes[i]=binary.charCodeAt(i);
                      const file=new File([bytes],tile+'-unapproved.'+mime.split('/')[1],{type:mime});
                      return await V227ArtIngest.importFile(tile,file,V192.v226ArtworkContract,
                        {expectedSha256:sha,provenance:'FICTIONAL_LOCAL_ART_UNAPPROVED'});
                    }""",{"tile":tile,"b64":source["base64"],
                          "sha":source["sha256"],"mime":source["mime"]})
                    assert record["sha256"]==source["sha256"]
                assert page.evaluate("V192.setRawArtReview(true)") is True
                assert page.evaluate("V192.productionApproved") is False
                assert page.evaluate("V192.connectedRoute") is True
                for tile in ("west","matrei","south"):
                    assert page.evaluate("(t)=>V192.focusTile(t)",tile)
                    page.evaluate("V192.zoomTo(6)")
                    assert page.evaluate("V192.snapshotForReview()")
                    page.screenshot(path=str(out/(key+"-"+tile+"-RAW-UNAPPROVED.png")),animations="disabled")
                assert page.evaluate("V192.setRawArtReview(false)") is True
                assert page.evaluate("V192.orderTo('south')") is True
                distances=[]
                for f in (.2,.5,.8):
                    point=page.evaluate("(f)=>V192.progress(f)",f)
                    distances.append(page.evaluate("(p)=>V192.roadDistance(p)",point))
                assert max(distances)<.001
                assert not errors,(key,errors)
                page.evaluate("V192.focusTile('south')")
                page.evaluate("V192.zoomTo(6)")
                assert page.evaluate("V192.snapshotForReview()")
                page.screenshot(path=str(out/(key+"-south-PLAYABLE-UNAPPROVED.png")),animations="disabled")
                report["configs"][key]={"originalArtShaVerified":True,
                     "actualGameplayRenderer":True,"V123Movement":True,
                     "maxGraphDistancePx":max(distances),"productionApproved":False}
            finally:
                page.close();browser.close()
    report["fourBrowserTechnicalPass"]=len(report["configs"])==4
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--west",type=Path,required=True)
    p.add_argument("--south",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--engines",default="chromium,webkit")
    p.add_argument("--chromium-executable")
    a=p.parse_args()
    result=run(a.root,a.west,a.south,a.out,
               tuple(a.engines.split(",")),a.chromium_executable)
    if len(result["configs"])!=2*len(tuple(a.engines.split(","))):
        raise SystemExit("Missing browser orientation")
