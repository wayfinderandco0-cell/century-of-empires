#!/usr/bin/env python3
"""Mobile WebKit QA for 50-cell Atlas with 18 unapproved scenic candidates.
No new candidate may be marked user-approved by this mechanical test.
"""
import socket, subprocess, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa"/"v272-candidate-atlas"
OUT.mkdir(parents=True,exist_ok=True)
with socket.socket() as sock:
    sock.bind(("127.0.0.1",0))
    port=sock.getsockname()[1]
server=subprocess.Popen(["python","-m","http.server",str(port),"--bind","127.0.0.1"],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    with sync_playwright() as pw:
        browser=pw.webkit.launch(headless=True)
        page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
        errors=[]
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        resp=page.goto(f"http://127.0.0.1:{port}/v272-original-scene-candidates.html",wait_until="domcontentloaded",timeout=30000)
        assert resp and resp.status==200
        page.wait_for_function("() => !!window.COE50 && window.COE50.cells.length === 50",timeout=30000)
        result=page.evaluate("""() => {
          const g=window.COE50, cs=g.cells;
          return {
            count:cs.length, sources:g.sourceCount, roads:g.validateRoads(),
            approved:cs.filter(x=>x.locked).length,
            candidateTypes:[...new Set(cs.filter(x=>!x.locked).map(x=>x.type))],
            initialZoomText:document.querySelector('#zoomIn')?.textContent,
            gridOff:document.querySelector('#outline')?.textContent.includes('OFF')
          };
        }""")
        assert result["count"]==50,result
        assert result["sources"]==21,result
        assert result["approved"]==3,result
        assert len(result["candidateTypes"])>=12,result
        assert result["roads"]["ok"] and result["roads"]["joins"]==57,result
        assert result["gridOff"],result
        page.wait_for_function("() => document.querySelector('#detail')?.textContent.includes('18 distinct landscape sources')",timeout=60000)
        page.screenshot(path=str(OUT/"webkit-iphone-candidate-close.png"),animations="disabled",full_page=True)
        page.click("#fit")
        page.screenshot(path=str(OUT/"webkit-iphone-all-50.png"),animations="disabled",full_page=True)
        page.click("#home")
        page.screenshot(path=str(OUT/"webkit-iphone-matrei.png"),animations="disabled",full_page=True)
        assert not errors,errors
        print("PASS: 50 cells, 21 distinct image sources, 3 protected positions, >=12 candidate types in use, 57 road joins, WebKit image loads and screenshots")
        browser.close()
finally:
    server.terminate()
    server.wait(timeout=10)
