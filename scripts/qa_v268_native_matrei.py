#!/usr/bin/env python3
"""Real native Canvas 390x844 WebKit QA for V268 Matrei 2x2 source terrain.

No fourth playable claim: verifies art, touch camera, and fail-closed movement.
"""
from __future__ import annotations
import json
import socket
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated" / "v268-qa"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = subprocess.Popen(
        ["python", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )
    try:
        time.sleep(1)
        with sync_playwright() as pw:
            browser = pw.webkit.launch(headless=True)
            page = browser.new_page(
                viewport={"width": 390, "height": 844},
                device_scale_factor=2,
                is_mobile=True,
                has_touch=True
            )
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            url = f"http://127.0.0.1:{port}/index.html?v268Geo=1&autoOpen=1"
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            assert response and response.status == 200
            page.wait_for_function(
                "() => window.COEAtlas?.loaded && window.COEV268Geo?.ready && window.COEV268Geo?.active",
                timeout=60000
            )
            snapshot = page.evaluate("""() => ({
              baseline: COEAtlas.playability.label,
              geographicLoaded: COEV268Geo.loadedTiles,
              source: COEV268Geo.manifest.sourceSha256,
              newPlayable: COEV268Geo.newPlayable,
              nativeCanvas: [document.querySelector('#atlasCanvas').width,
                             document.querySelector('#atlasCanvas').height],
              marchBlocked: COEAtlas.startMarch() === false,
              error: COEV268Geo.error
            })""")
            assert snapshot["geographicLoaded"] == 4, snapshot
            assert snapshot["newPlayable"] == 0 and snapshot["marchBlocked"], snapshot
            assert snapshot["nativeCanvas"] == [780, 1688], snapshot
            assert snapshot["source"] and not snapshot["error"], snapshot
            # Real iPhone-style controls, not synthetic API-only pan/zoom.
            z0 = page.evaluate("COEAtlas.zoom")
            page.locator("#atlasPlus").click()
            z1 = page.evaluate("COEAtlas.zoom")
            assert z1 > z0, (z0, z1)
            before = page.evaluate("COEAtlas.center")
            canvas = page.locator("#atlasCanvas")
            box = canvas.bounding_box()
            assert box
            page.mouse.move(box["x"] + 190, box["y"] + 440)
            page.mouse.down()
            page.mouse.move(box["x"] + 230, box["y"] + 470, steps=8)
            page.mouse.up()
            after = page.evaluate("COEAtlas.center")
            assert before != after, (before, after)
            page.locator("#atlasWhole").click()
            page.wait_for_timeout(600)
            page.screenshot(path=str(OUT / "native-webkit-390x844-geographic.png"), full_page=False)
            snapshot["zoomControlPassed"] = True
            snapshot["panControlPassed"] = True
            snapshot["screenshot"] = "native-webkit-390x844-geographic.png"
            # Disable geography: original V123 army road remains available.
            page.evaluate("COEV268Geo.disable()")
            snapshot["originalRoadStillWorks"] = page.evaluate("COEAtlas.startMarch() === true")
            assert snapshot["originalRoadStillWorks"], snapshot
            assert not errors, errors
            (OUT / "results.json").write_text(json.dumps(snapshot, indent=2))
            print(json.dumps(snapshot, indent=2))
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)


if __name__ == "__main__":
    main()
