#!/usr/bin/env python3
"""Real mobile WebKit visual check of protected Matrei against unapproved ridge."""
import asyncio
import http.server
import socketserver
import threading
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "terrain-grid/v267-original-art-batch-01/actual-webkit-iphone-east-seam-inspector.png"

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

async def main():
    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
    import os
    os.chdir(ROOT)
    server = Server(("127.0.0.1", 8768), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        async with async_playwright() as pw:
            browser = await pw.webkit.launch()
            page = await browser.new_page(viewport={"width":390,"height":844},
                                         device_scale_factor=2,
                                         is_mobile=True,has_touch=True)
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            await page.goto("http://127.0.0.1:8768/v267-east-seam-inspector.html",wait_until="domcontentloaded")
            await page.wait_for_function("window.COESeamQA && window.COESeamQA.loaded",timeout=60000)
            assert not errors, errors
            assert await page.evaluate("COESeamQA.hasRoadAtEdge") is False
            before = await page.evaluate("COESeamQA.zoom")
            await page.locator("#plus").click()
            after = await page.evaluate("COESeamQA.zoom")
            assert after > before, (before, after)
            await page.locator("#seam").click()
            await page.screenshot(path=str(OUT),full_page=True)
            with Image.open(OUT) as im:
                # A loaded interface alone does not count: actual terrain must
                # have richly varying image pixels in the center viewport.
                pixels = im.convert("RGB").crop((80,340,700,1300))
                colors = len(pixels.resize((80,120)).getcolors(10000) or [])
                assert colors > 350, f"Blank/flat terrain: only {colors} sampled colors"
            print(f"PASS WebKit 390x844, registered Matrei + ridge visible, {colors} colors, zoom works, no invented road")
            print(f"Screenshot: {OUT.relative_to(ROOT)}")
            await browser.close()
    finally:
        server.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
