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
OUT_V2 = ROOT / "terrain-grid/v267-original-art-batch-01/actual-webkit-iphone-east-seam-v2.png"

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
            for variant, target in [("", OUT), ("?variant=v2", OUT_V2)]:
                errors.clear()
                await page.goto("http://127.0.0.1:8768/v267-east-seam-inspector.html" + variant,
                                wait_until="domcontentloaded")
                await page.wait_for_function("window.COESeamQA && window.COESeamQA.loaded", timeout=60000)
                assert not errors, (variant, errors)
                assert await page.evaluate("COESeamQA.hasRoadAtEdge") is False
                before = await page.evaluate("COESeamQA.zoom")
                await page.locator("#plus").click()
                after = await page.evaluate("COESeamQA.zoom")
                assert after > before, (variant, before, after)
                await page.locator("#seam").click()
                if variant:
                    assert "V2 reversible display seam loaded" in await page.locator("#status").inner_text()
                await page.screenshot(path=str(target), full_page=True)
                with Image.open(target) as im:
                    pixels = im.convert("RGB").crop((80, 340, 700, 1300))
                    colors = len(pixels.resize((80, 120)).getcolors(10000) or [])
                    assert colors > 350, f"Blank/flat terrain {variant}: {colors} colors"
                print(f"PASS WebKit 390x844 {variant or 'graded'}: {colors} colors, zoom, no invented road")
                print(f"Screenshot: {target.relative_to(ROOT)}")
            await browser.close()
    finally:
        server.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
