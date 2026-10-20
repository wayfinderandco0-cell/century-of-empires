"""Verify V99 tree imagery and mapped streams in mobile Chromium before publishing."""
import json
import threading
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path("terrain-v99");root.mkdir(exist_ok=True)
server=ThreadingHTTPServer(("127.0.0.1",8765),SimpleHTTPRequestHandler)
threading.Thread(target=server.serve_forever,daemon=True).start()
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
    page=browser.new_page(viewport={"width":393,"height":852},device_scale_factor=1,has_touch=True,is_mobile=True)
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.goto("http://127.0.0.1:8765/v99-brenner-real-trees-streams.html",wait_until="domcontentloaded")
    page.locator("button[data-level='3']").click()
    try:
        page.wait_for_function("""()=>document.querySelectorAll('#streamLayer path').length>=4
           && [...document.querySelectorAll('#tileLayer img')].filter(x=>x.complete&&x.naturalWidth>0).length>=3""",timeout=55000)
    except Exception as e:
        print("Timed out waiting for tiles or streams",str(e)[:120],flush=True)
    page.wait_for_timeout(1300)
    stats=page.evaluate("""()=>{
      const images=[...document.querySelectorAll('#tileLayer img')];
      return {loaded:images.filter(x=>x.complete&&x.naturalWidth>0).length,
      missing:images.filter(x=>x.complete&&!x.naturalWidth).length,
      total:images.length,streamPaths:document.querySelectorAll('#streamLayer path').length,
      view:document.querySelector('#levelName').innerText,
      photoVisible:getComputedStyle(document.querySelector('#photoStage')).display!=='none'}
    }""")
    page.screenshot(path=str(root/"phone-preview.jpg"),type="jpeg",quality=82,full_page=True)
    browser.close()
server.shutdown()
report={"stats":stats,"javascriptErrors":errors}
(root/"phone-qa.json").write_text(json.dumps(report,indent=2)+"\n")
print("MOBILE QA",json.dumps(report),flush=True)
assert not errors,"Browser JS error"
assert stats["loaded"]>=3,"Not enough real photographic tiles"
assert stats["streamPaths"]>=4,"Mapped streams not displayed"
assert stats["photoVisible"],"Mobile close up did not open"
print("V99 MOBILE BROWSER QA PASSED",flush=True)
