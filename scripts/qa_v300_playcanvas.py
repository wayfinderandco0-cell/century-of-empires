#!/usr/bin/env python3
"""V300 browser acceptance: REAL PlayCanvas engine + 3D objects + road conquest.
This tests in mobile-sized browsers, NOT a physical iPhone.
"""
from __future__ import annotations
import json, subprocess, socket, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa"/"v300-playcanvas"
OUT.mkdir(parents=True,exist_ok=True)
with socket.socket() as sock:
    sock.bind(("127.0.0.1",0))
    PORT=sock.getsockname()[1]
server=subprocess.Popen(["python","-m","http.server",str(PORT),"--bind","127.0.0.1"],cwd=ROOT,
                        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    report={}
    with sync_playwright() as p:
        for engine in ("chromium","webkit"):
            exe=getattr(p,engine)
            args=["--enable-webgl","--enable-unsafe-swiftshader","--use-gl=angle","--use-angle=swiftshader"] if engine=="chromium" else []
            browser=exe.launch(headless=True,args=args)
            page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
            errors=[]
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console",lambda m: errors.append("console: "+m.text) if m.type=="error" else None)
            resp=page.goto(f"http://127.0.0.1:{PORT}/v300-playcanvas-3d.html",
                 wait_until="domcontentloaded",timeout=45000)
            assert resp and resp.status==200,(engine,resp)
            try:
                page.wait_for_function("() => window.COE3D?.ready === true",timeout=60000)
            except Exception:
                page.screenshot(path=str(OUT/f"{engine}-failed.png"))
                raise AssertionError(f"{engine} engine startup failed: "+json.dumps({
                    "errors":errors[-8:],"pageError":page.locator("#error").inner_text(),
                    "status":page.locator("#status").inner_text()
                }))
            initial=page.evaluate("""() => {
                const g=window.COE3D;
                return {engine:g.engine,tiles:g.tiles,roads:g.roads,
                    vertices:g.terrainVertices,trees:g.treeCount, pictures:g.tilePictures,
                    scene:g.app.root.children.length,ready:g.ready,
                    state:g.getState()};
            }""")
            assert initial["engine"]=="playcanvas",initial
            assert initial["tiles"]==12 and initial["roads"]==11,initial
            assert initial["vertices"]>12000 and initial["pictures"]==0,initial
            assert initial["trees"]>30,initial
            assert not initial["state"]["owned"],initial
            page.wait_for_timeout(1000)
            page.screenshot(path=str(OUT/f"{engine}-terrain-before.png"),animations="disabled")
            # Actual on-page interaction, not a simulated store update.
            page.get_by_role("button",name="March to Matrei").click()
            page.wait_for_function("() => window.COE3D?.getState().owned===true",timeout=25000)
            after=page.evaluate("() => window.COE3D.getState()")
            assert after["current"]==6 and after["supplies"]==75 and after["owned"],after
            assert page.locator("#ownership").inner_text()=="Captured"
            page.screenshot(path=str(OUT/f"{engine}-matrei-captured.png"),animations="disabled")
            page.get_by_role("button",name="Reset scenario").click()
            reset=page.evaluate("() => window.COE3D.getState()")
            assert reset["current"]==4 and reset["supplies"]==50 and not reset["owned"],reset
            assert not errors,(engine,errors[-8:])
            report[engine]={"initial":initial,"captured":after,"reset":reset}
            browser.close()
    (OUT/"report.json").write_text(json.dumps(report,indent=2))
    print("PASS: PlayCanvas 3D engine initialized, terrain mesh rendered, 11 drawn road edges, army captured Matrei, +25 supplies and reset, in mobile Chromium and WebKit.")
finally:
    server.terminate();server.wait(timeout=10)
