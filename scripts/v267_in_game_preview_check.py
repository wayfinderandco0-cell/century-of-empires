#!/usr/bin/env python3
"""Verify the V267 art preview is reachable INSIDE the unmodified V94 campaign UI.
Emulated mobile browsers, not native iPhone Safari. Screenshots use actual V267 art.
"""
import argparse
import http.server
import json
from pathlib import Path
import socketserver
import subprocess
import sys
import time
from playwright.sync_api import sync_playwright

PARSER=argparse.ArgumentParser()
PARSER.add_argument("--browser",choices=("chromium","webkit"),required=True)
PARSER.add_argument("--orientation",choices=("portrait","landscape"),required=True)
PARSER.add_argument("--out",required=True)
ARGS=PARSER.parse_args()
SIZES={"portrait":(390,844),"landscape":(844,390)}
WIDTH,HEIGHT=SIZES[ARGS.orientation]
OUT=Path(ARGS.out);OUT.mkdir(parents=True,exist_ok=True)

with sync_playwright() as playwright:
    server=subprocess.Popen([sys.executable,"-m","http.server","8768","--bind","127.0.0.1"],
        cwd=Path(__file__).resolve().parent.parent,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    errors=[]
    try:
        # Wait for server rather than relying on a hard-coded startup delay.
        import urllib.request
        for attempt in range(50):
            try:
                urllib.request.urlopen("http://127.0.0.1:8768/index.html",timeout=1).close()
                break
            except Exception:
                time.sleep(.1)
        else:
            raise RuntimeError("Local game server failed to start")
        browser=getattr(playwright,ARGS.browser).launch(headless=True)
        context=browser.new_context(viewport={"width":WIDTH,"height":HEIGHT},
            device_scale_factor=2,is_mobile=True,has_touch=True)
        page=context.new_page()
        page.on("pageerror",lambda error: errors.append(str(error)))
        page.goto("http://127.0.0.1:8768/index.html",wait_until="domcontentloaded",timeout=60000)
        opener=page.locator("#alpineArtOpen")
        opener.wait_for(state="visible",timeout=20000)
        assert page.locator("#alpineArtLayer").is_hidden(), "Preview opened without interaction"
        clock_before=page.locator("#clockTitle").inner_text()
        opener.click()
        assert page.locator("#alpineArtLayer").is_visible(), "Open button did not display preview"
        page.wait_for_function("""() => {
          const i=document.getElementById('alpineArtFrame');
          const w=i?.contentWindow;
          return !!(w?.COE?.originalMatreiLoaded && w.COE.westSouthConnected &&
                     w.COE.sourceRegistered && w.COE.nodes===100);
        }""",timeout=90000)
        frame=page.frame_locator("#alpineArtFrame")
        assert frame.locator("#status").is_visible()
        before=page.evaluate("""() => {
           const a=document.getElementById('alpineArtFrame').contentWindow.COE;
           return {nodes:a.nodes, originalMatrei:a.originalMatreiLoaded,
              seams:a.roadSeams,productionApproved:a.productionApproved,
              sourceRegistered:a.sourceRegistered};
        }""")
        assert before["nodes"]==100
        assert before["originalMatrei"] and before["sourceRegistered"]
        assert all(s["pass"] and s["gap"]==0 for s in before["seams"])
        assert before["productionApproved"] is False
        frame.locator("#march").click()
        page.wait_for_timeout(500)
        result=page.evaluate("""() => {
          const c=document.getElementById('alpineArtFrame').contentWindow.COE;
          const route=c.route,atEnd=c.stepToEnd(),dest=c.destinations;
          return {waypoints:route.length,end:atEnd,
            south:dest?.south,originalMatrei:c.originalMatreiLoaded};
        }""")
        assert result["waypoints"]>=20, "No WEST-to-SOUTH route"
        assert result["end"]==[2806,1629], result
        page.screenshot(path=str(OUT/f"in-game-{ARGS.browser}-{ARGS.orientation}.png"),full_page=True)
        page.locator("#alpineArtClose").click()
        assert page.locator("#alpineArtLayer").is_hidden(), "Preview did not close"
        assert opener.is_visible(), "Return to game button missing"
        assert page.locator("#clockTitle").inner_text()==clock_before, "Campaign UI changed during preview"
        assert not errors, errors
        data={"browser":ARGS.browser,"orientation":ARGS.orientation,"viewport":[WIDTH,HEIGHT],
           "embedded_original_matrei":before["originalMatrei"],"nodes":before["nodes"],
           "seams":before["seams"],"route_waypoints":result["waypoints"],"arrival":result["end"],
           "campaign_screen_preserved":True,"production_approved":False,"page_errors":errors}
        (OUT/f"in-game-{ARGS.browser}-{ARGS.orientation}.json").write_text(json.dumps(data,indent=2))
        print(json.dumps(data,indent=2))
        context.close();browser.close()
    finally:
        server.terminate()
        try:server.wait(timeout=5)
        except subprocess.TimeoutExpired:server.kill()
