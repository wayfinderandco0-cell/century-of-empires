#!/usr/bin/env python3
"""V269 actual mobile WebKit native Canvas smoke test; experimental terrain motion only.

Never interpret the crossing as historically certified, river-safe or a fourth
approved campaign tile. Verifies the actual V268 slope PNG and path on iPhone WebKit.
"""
import json
import socket
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated" / "v269-qa"
OUT.mkdir(parents=True, exist_ok=True)

with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    PORT = sock.getsockname()[1]

server = subprocess.Popen(
    ["python", "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
    cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
try:
    time.sleep(1)
    with sync_playwright() as pw:
        browser = pw.webkit.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2, is_mobile=True, has_touch=True
        )
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        url = f"http://127.0.0.1:{PORT}/index.html?v268Geo=1&v269Explore=1&autoOpen=1"
        response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        assert response and response.status == 200
        page.wait_for_function(
            "() => COEAtlas?.loaded && COEV268Geo?.active && COEV268Geo?.loadedTiles===4 && COEV269Explore?.enabled",
            timeout=60000
        )
        baseline = page.evaluate("""() => ({
            tiles: COEV268Geo.loadedTiles,
            sourceSha: COEV268Geo.manifest.sourceSha256,
            newCertifiedPlayable: COEV268Geo.newPlayable,
            firstCell: COEV269Explore.visitedCells[0],
            firstPosition: COEV269Explore.position,
            originalGraphNodes: COEAtlas.nodes,
            graphUnchanged: COEV269Explore.roadGraphModified===false
        })""")
        assert baseline["tiles"] == 4 and baseline["newCertifiedPlayable"] == 0, baseline
        assert baseline["originalGraphNodes"] == 100 and baseline["graphUnchanged"], baseline
        page.screenshot(path=str(OUT / "webkit-v269-before-crossing.png"))
        started = page.evaluate("COEV269Explore.nextCell()")
        assert started, "No slope-eligible shared-edge route from actual GLO-30 terrain"
        page.wait_for_function("() => COEV269Explore.crossings >= 1", timeout=30000)
        after = page.evaluate("""() => ({
            visitedCells: COEV269Explore.visitedCells,
            position: COEV269Explore.position,
            crossings: COEV269Explore.crossings,
            orders: COEV269Explore.orders,
            originalGraphNodes: COEAtlas.nodes
        })""")
        assert len(after["visitedCells"]) >= 2 and after["originalGraphNodes"] == 100, after
        page.screenshot(path=str(OUT / "webkit-v269-after-crossing.png"))
        page.evaluate("COEV268Geo.disable()")
        assert page.evaluate("COEAtlas.startMarch() === true"), "Original V123 route regressed"
        assert not errors, errors
        report = {
            "status": "experimental cross-cell march passed; NOT a historical or water-safe certification",
            "browser": "WebKit 390x844 CSS, 2x resolution, iPhone touch",
            "baseline": baseline, "movement": after, "consolePageErrors": errors
        }
        (OUT / "result.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        browser.close()
finally:
    server.terminate()
    server.wait(timeout=10)
