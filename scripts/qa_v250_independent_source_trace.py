#!/usr/bin/env python3
"""Four real mobile-sized browser checks for the V250 ORIGINAL-PIXEL annotation tool.
Synthetic fixture only; neither gameplay nor source-art acceptance.
"""
import asyncio
import functools
import hashlib
import http.server
import io
import json
import threading
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/v250-independent-trace"
OUT.mkdir(parents=True, exist_ok=True)


async def main():
    image = Image.new("RGB", (1536, 1024), (46, 92, 59))
    ImageDraw.Draw(image).line([(260, 510), (510, 540), (830, 500), (1260, 550)],
                               fill=(156, 113, 70), width=24)
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    raw = buffer.getvalue()
    sha = hashlib.sha256(raw).hexdigest()
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0),
        functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    report = {"sourceFixture": "SYNTHETIC NOT GAME ART", "sourceSha256": sha,
              "productionApproved": False, "sourceRegisteredToV123": False,
              "humanVisualApproval": False, "configs": []}
    try:
        async with async_playwright() as p:
            for engine in ("chromium", "webkit"):
                browser = await getattr(p, engine).launch(headless=True)
                for orientation, size in (
                    ("portrait", {"width": 390, "height": 844}),
                    ("landscape", {"width": 844, "height": 390}),
                ):
                    page = await browser.new_page(
                        viewport=size, is_mobile=True, has_touch=True)
                    await page.goto(
                        f"http://127.0.0.1:{server.server_port}/"
                        "v250-independent-source-road-trace.html")
                    assert "NO SOURCE" in await page.locator("#status").inner_text()
                    await page.locator("#file").set_input_files({
                        "name": "synthetic.png", "mimeType": "image/png",
                        "buffer": raw})
                    await page.wait_for_function("window.__v250test.state.ready")
                    assert sha in await page.locator("#source").inner_text()
                    # The image is the only map: no V123 route is presented.
                    assert await page.locator("canvas").count() == 1
                    assert await page.locator("text=V123 route").count() == 0
                    await page.locator("#tile").select_option("south")
                    assert not await page.evaluate("window.__v250test.state.ready")
                    await page.locator("#file").set_input_files({
                        "name": "synthetic.png", "mimeType": "image/png",
                        "buffer": raw})
                    await page.wait_for_function("window.__v250test.state.ready")
                    rect = await page.locator("#canvas").bounding_box()
                    for x, y in [(260, 510), (510, 540), (830, 500), (1260, 550)]:
                        await page.mouse.click(rect["x"] + rect["width"] * x / 1536,
                                               rect["y"] + rect["height"] * y / 1024)
                    assert await page.evaluate("window.__v250test.state.points.length") == 4
                    await page.locator("#clear").click()
                    assert await page.evaluate("window.__v250test.state.points.length") == 0
                    await page.evaluate("""() => {
                      const s=window.__v250test.state;
                      s.points=[[260,510],[510,540],[830,500],[1260,550]];
                      s.start=0;s.end=3;
                    }""")
                    draft = await page.evaluate("window.__v250test.draft()")
                    assert draft["sourceSha256"] == sha
                    assert draft["annotationMethod"].startswith("UNVERIFIED")
                    assert draft["fullVisibleRoadPoints"][0] == [260, 510]
                    assert not draft["sourceRegisteredToV123"]
                    assert not draft["productionApproved"]
                    await page.screenshot(
                        path=str(OUT / f"{engine}-{orientation}-UNAPPROVED.png"),
                        full_page=True)
                    report["configs"].append(
                        {"browser": engine, "orientation": orientation,
                         "syntheticPixelTrace": "PASS", "artApproval": False})
                    await page.close()
                await browser.close()
    finally:
        server.shutdown()
    report["fourBrowserFunctionalPass"] = len(report["configs"]) == 4
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    assert report["fourBrowserFunctionalPass"]


if __name__ == "__main__":
    asyncio.run(main())
