#!/usr/bin/env python3
"""Remote runner checks real browser rendering at iPhone-sized viewport.
These are Chromium/WebKit engine simulations, NOT physical iPhone Safari tests.
Screenshots are published as CI artifacts even if a browser fails."""
from __future__ import annotations
import json, pathlib, subprocess, time, urllib.request
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "qa" / "geo-redesign"
OUT.mkdir(parents=True, exist_ok=True)
PORT = 8787
URL = f"http://127.0.0.1:{PORT}/geo-redesign/index.html"
server = subprocess.Popen(
    ["python3", "-m", "http.server", str(PORT), "--bind", "127.0.0.1", "--directory", str(ROOT)],
    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
)
time.sleep(1.0)
failures = []
try:
    with sync_playwright() as playwright:
        for name in ("chromium", "webkit"):
            browser = None
            page = None
            try:
                engine = getattr(playwright, name)
                launch = {"headless": True}
                if name == "chromium":
                    launch["args"] = ["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
                browser = engine.launch(**launch)
                context = browser.new_context(
                    viewport={"width": 390, "height": 844},
                    device_scale_factor=2, is_mobile=True, has_touch=True
                )
                page = context.new_page()
                js_errors = []
                page.on("pageerror", lambda error: js_errors.append(str(error)))
                page.goto(URL, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_function(
                    "() => window.__COE_GEO_QA && (window.__COE_GEO_QA.ready || window.__COE_GEO_QA.error)",
                    timeout=90000
                )
                ready = page.evaluate("window.__COE_GEO_QA")
                assert ready["ready"], f"Map failed to load: {ready}"
                assert ready["roadSegments"] >= 20
                assert ready["roadGeometrySource"] == "cartways"
                assert ready["orderGeometrySource"] == "orders"
                page.screenshot(path=str(OUT / f"{name}-regional.png"), full_page=True)
                # Browser-backed click/order/march, not just graph math.
                page.locator("#selectArmy").click()
                page.locator("#destination").select_option("gries")
                assert page.evaluate("window.__COE_GEO_QA.planned")
                assert "km" in page.locator("#status").inner_text()
                page.locator("#execute").click()
                page.wait_for_function("window.__COE_GEO_QA.moveCount > 12", timeout=20000)
                page.screenshot(path=str(OUT / f"{name}-march.png"), full_page=True)
                moved = page.evaluate("window.__COE_GEO_QA.armyPoint")
                assert moved != [11.4531, 47.1308], "Army marker did not move"
                # Incremental smooth zoom and camera pan in real browser.
                initial_zoom = page.evaluate("window.__COE_GEO_QA.zoom")
                page.locator(".maplibregl-ctrl-zoom-in").click()
                page.wait_for_function("(before) => window.__COE_GEO_QA.zoom > before + 0.2", arg=initial_zoom, timeout=15000)
                page.screenshot(path=str(OUT / f"{name}-close.png"), full_page=True)
                page.mouse.move(235, 340)
                page.mouse.down()
                page.mouse.move(165, 390, steps=12)
                page.mouse.up()
                page.wait_for_timeout(350)
                page.screenshot(path=str(OUT / f"{name}-panned.png"), full_page=True)
                assert not js_errors, "JS errors: " + repr(js_errors)
                final = page.evaluate("window.__COE_GEO_QA")
                print(name, json.dumps({
                    "ready": final["ready"], "roadNodes": final["roadNodes"],
                    "roadSegments": final["roadSegments"], "movementFrames": final["moveCount"],
                    "terrainEnabled": final["terrainEnabled"],
                    "zoomBefore": initial_zoom, "zoomAfter": final["zoom"],
                    "lastMapError": final.get("lastMapError")
                }))
            except Exception as exc:
                failures.append(f"{name}: {exc}")
                if page is not None:
                    try: page.screenshot(path=str(OUT / f"{name}-failure.png"), full_page=True)
                    except Exception: pass
            finally:
                if browser is not None: browser.close()
finally:
    server.terminate()
    try: server.wait(timeout=5)
    except subprocess.TimeoutExpired: server.kill()

if failures:
    raise SystemExit("Browser QA failed: " + " | ".join(failures))
print("PASS: iPhone-sized Chromium and WebKit map, orders, movement, zoom, pan. Physical Safari not tested.")