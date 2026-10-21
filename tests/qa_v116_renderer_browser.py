"""Browser pixel QA for V116 stitched local art; synthetic source, no road certification."""
import http.server, json, socketserver, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args): pass
class Server(socketserver.TCPServer): allow_reuse_address=True
server=Server(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_address[1]}/scripts/v116_local_art_renderer.js'
results={}
try:
 with sync_playwright() as p:
  for engine in ('chromium',):
   browser=getattr(p,engine).launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
   try:
    for viewport in ({'width':390,'height':844},{'width':844,'height':390}):
     page=browser.new_page(viewport=viewport,device_scale_factor=2,is_mobile=True,has_touch=True)
     errors=[]
     page.on('pageerror',lambda e: errors.append(str(e)))
     page.goto('about:blank')
     page.add_script_tag(path=str(ROOT/'scripts/v116_local_art_renderer.js'))
     result=page.evaluate('''({w,h,idx}) => {
       const source=document.createElement('canvas');source.width=1100;source.height=842;
       const s=source.getContext('2d');
       for(let y=0;y<842;y+=7){s.fillStyle='rgb('+((y*13)%255)+','+((y*31)%255)+','+((y*17)%255)+')';s.fillRect(0,y,1100,7)}
       for(let x=0;x<1100;x+=11){s.fillStyle='rgba('+((x*19)%255)+',40,160,.55)';s.fillRect(x,0,2,842)}
       const canvas=(width,height)=>{let c=document.createElement('canvas');c.width=width;c.height=height;return c;};
       const full=canvas(w,h),tiled=canvas(w,h),v={width:w,height:h};
       const box=idx.artBoxWorldPx;
       const cx=(box[0]+box[2])/2,cy=(box[1]+box[3])/2;
       const camWidth=(box[2]-box[0])*.47,camHeight=(box[3]-box[1])*.47;
       const camera=[cx-camWidth/2,cy-camHeight/2,cx+camWidth/2,cy+camHeight/2];
       const q=CenturyV116Tiles.draw(tiled.getContext('2d'),source,idx,camera,v);
       const a=CenturyV116Tiles.worldToScreen([box[0],box[1]],camera,v),
             b=CenturyV116Tiles.worldToScreen([box[2],box[3]],camera,v);
       full.getContext('2d').drawImage(source,a[0],a[1],b[0]-a[0],b[1]-a[1]);
       const A=full.getContext('2d').getImageData(0,0,w,h).data;
       const B=tiled.getContext('2d').getImageData(0,0,w,h).data;
       let differing=0,maxDelta=0,over3=0;
       for(let i=0;i<A.length;i+=4){let d=Math.max(Math.abs(A[i]-B[i]),Math.abs(A[i+1]-B[i+1]),Math.abs(A[i+2]-B[i+2]));if(d){differing++;maxDelta=Math.max(maxDelta,d)}if(d>3)over3++}
       return {drawCalls:q.drawCalls,visibleTiles:q.visibleTileCount,differingPixels:differing,totalPixels:w*h,maxDelta,over3};
     }''',{'w':viewport['width'],'h':viewport['height'],'idx':json.loads((ROOT/'terrain-grid/v115-local-tiles-v116.json').read_text())})
     result['javascriptErrors']=errors
     # Single cropped draw is not guaranteed bit-identical to full draw at crop edges.
     # But viewport lies strictly within the stitched crop's internal tile margins.
     result['passed']=(result['drawCalls']==1 and result['visibleTiles']>0 and
                       result['over3']<viewport['width']*viewport['height']*.002 and not errors)
     results[f'{engine}_{viewport["width"]}x{viewport["height"]}']=result
     page.close()
   finally: browser.close()
finally:server.shutdown()
report={'passed':all(r['passed'] for r in results.values()),'checks':results,
        'artSource':'synthetic deterministic test texture, NOT the actual V115 painting',
        'realIphoneTested':False,'routeArtAlignmentVerified':False}
(ROOT/'v116-renderer-browser-qa.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if not report['passed']:raise SystemExit(1)
