"""V101 isolated iPhone-sized Chromium smoke and visual QA; no production save changes."""
import json, os, pathlib, threading, time, http.server, socketserver, traceback
from playwright.sync_api import sync_playwright

ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/"terrain-v101"
OUT.mkdir(exist_ok=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
os.chdir(ROOT)
socketserver.TCPServer.allow_reuse_address=True
httpd=socketserver.ThreadingTCPServer(("127.0.0.1",0),Quiet)
threading.Thread(target=httpd.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{httpd.server_address[1]}/v101-historical-brenner.html"
report={"url":"local GitHub Actions Chromium HTTP server","browser":"Chromium iPhone-sized (390x844)","checks":{},"errors":[]}
def test(name,condition):
    report["checks"][name]=bool(condition)
    if not condition: raise AssertionError(name)
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--disable-dev-shm-usage"])
        page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
        page.on("pageerror",lambda err:report["errors"].append(str(err)))
        response=page.goto(url,wait_until="domcontentloaded",timeout=30000)
        test("HTML served",response.status==200)
        page.wait_for_timeout(1100)
        test("V101 controls",page.locator("#v100Command button").count()==3)
        test("far zoom hides town pins",page.locator("#pins").locator("*").count()==0)
        test("far zoom hides units",page.locator("#v100Units").locator("*").count()==0)
        test("initial enemy hidden", "unknown" in page.locator("#v100Status").inner_text().lower())
        page.locator('[data-level="1"]').click()
        test("medium town names",page.locator("#pins text").count()>=1)
        test("medium uses one friendly dot",page.locator("#v100Units circle").count()==1)
        test("medium never displays enemy troop count","2,470" not in page.locator("#v100Status").inner_text())
        page.locator("#v100Ally").check()
        test("allied observation sees opposing formation","2,470" in page.locator("#v100Status").inner_text())
        test("two medium dots after detection",page.locator("#v100Units circle").count()==2)
        page.locator("#v100Ally").uncheck()
        test("fog restores hidden enemy","unknown" in page.locator("#v100Status").inner_text().lower())
        page.locator('[data-level="2"]').click()
        page.wait_for_timeout(1000)
        test("close level draws infantry plus vector cavalry and artillery",page.locator("#v100Units image").count()>=1 and page.locator("#v100Units g").count()>=4)
        page.screenshot(path=str(OUT/"v101-troops-phone.jpg"),type="jpeg",quality=75)
        page.locator('[data-level="3"]').click()
        page.wait_for_timeout(2200)
        test("painted view visible",page.locator("#photoStage").is_visible())
        test("generated canvas exists",page.locator("#generatedLandscape").count()==1)
        test("no modern road imagery",page.locator('img[src*="mapsneu.wien.gv.at"]').count()==0)
        test("painted trees status",page.evaluate("document.getElementById('photoStatus').textContent.includes('painted trees')"))
        test("period terrain draws all troop types",page.locator("#photoUnits image").count()>=1 and page.locator("#photoUnits g").count()>=4)
        test("aerial retains mapped water canvas",page.locator("#streamLayer").count()==1)
        page.screenshot(path=str(OUT/"v101-aerial-phone.jpg"),type="jpeg",quality=75)
        page.locator("#v100Go").click()
        page.wait_for_timeout(1250)
        test("march starts","Marching" in page.locator("#v100Status").inner_text())
        page.locator("#v100Pause").click()
        test("pause works","Paused" in page.locator("#v100Status").inner_text())
        page.locator("#v100Reset").click()
        test("reset stays paused","Paused" in page.locator("#v100Status").inner_text())
        page.locator('[data-level="2"]').click()
        page.locator("#v100Go").click()
        page.wait_for_function("document.querySelector('#v100Status').textContent.includes('CONTACT')",timeout=95000)
        test("opposing armies meet", "CONTACT" in page.locator("#v100Status").inner_text())
        page.screenshot(path=str(OUT/"v101-contact-phone.jpg"),type="jpeg",quality=75)
        test("no JavaScript errors",len(report["errors"])==0)
        browser.close()
except Exception as e:
    report["errors"].append(str(e))
    report["traceback"]=traceback.format_exc()[-3000:]
finally:
    httpd.shutdown()
    report["passed"]=all(report["checks"].values()) and not report["errors"]
    (OUT/"qa-report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2),flush=True)
    if not report["passed"]: raise SystemExit(1)
