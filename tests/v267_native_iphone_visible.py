"""Physical-screen regression for the V267 iPhone native ridge preview.

The prior test only proved that source image bytes were nonblank; the user
reported a dark, empty native atlas. This test checks actual screenshot pixels
and a deliberate baseline-art failure, not just HTML/image load events.
"""
import asyncio
import io
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8765/index.html?originalArtPilot=v267-new&autoOpen=1"
OUT = Path("v267-native-iphone-qa")
OUT.mkdir(exist_ok=True)


def verify_screen(png, name):
    im = Image.open(io.BytesIO(png)).convert("RGB")
    width, height = im.size
    # Exclude the header/footer; require actual varied image pixels in the
    # playable atlas viewport. A plain dark canvas must fail this gate.
    sample = im.crop((int(width*.06), int(height*.21),
                      int(width*.94), int(height*.82))).resize((120, 130))
    colors = list(sample.getdata())
    unique = len({(r//16,g//16,b//16) for r,g,b in colors})
    lit = sum(r+g+b>180 for r,g,b in colors)/len(colors)
    if unique < 55 or lit < .10:
        raise AssertionError(f"{name}: BLANK visible atlas: colors={unique} lit={lit:.3f}")
    print(f"PASS {name}: screenshot {width}x{height}; colors={unique}; lit={lit:.3f}")


async def inspect(page, label, expect_loaded):
    await page.goto(URL, wait_until="domcontentloaded")
    await page.wait_for_function(
        "() => { const i=document.querySelector('#atlasRidgeDomFallback');"
        "return i && i.complete && i.naturalWidth===1536 && i.naturalHeight===1024"
        " && getComputedStyle(i).display!=='none'; }",
        timeout=30000,
    )
    if expect_loaded:
        await page.wait_for_function(
            "() => window.COEAtlas?.loaded===true && window.COEAtlas?.originalNeighborVisible===true",
            timeout=30000,
        )
    else:
        await page.wait_for_timeout(2000)
        assert await page.evaluate("window.COEAtlas?.loaded") is False
    bbox = await page.locator("#atlasRidgeDomFallback").bounding_box()
    assert bbox and bbox["width"] > 150 and bbox["height"] > 100, (label,bbox)
    assert bbox["x"] < 390 and bbox["x"]+bbox["width"] > 0, (label,bbox)
    assert bbox["y"] < 844 and bbox["y"]+bbox["height"] > 100, (label,bbox)
    # The previous CI screenshot showed art stranded near the lower/right edge.
    # The focused ridge must be centered, not merely intersect the viewport.
    assert abs(bbox["x"]+bbox["width"]/2-195) < 28, (label,"off-center X",bbox)
    assert abs(bbox["y"]+bbox["height"]/2-422) < 35, (label,"off-center Y",bbox)
    shot = await page.screenshot(full_page=True)
    (OUT/f"{label}.png").write_bytes(shot)
    verify_screen(shot,label)


async def main():
    async with async_playwright() as p:
        browser=await p.webkit.launch(headless=True)
        context=await browser.new_context(
            viewport={"width":390,"height":844},
            device_scale_factor=2,is_mobile=True,has_touch=True,
        )
        page=await context.new_page()
        await inspect(page,"normal-native",True)
        # Check native atlas zoom, not merely a standalone image element.
        before=await page.locator("#atlasRidgeDomFallback").bounding_box()
        await page.locator("#atlasPlus").click()
        after=await page.locator("#atlasRidgeDomFallback").bounding_box()
        assert after["width"] > before["width"]*1.15, (before,after)
        shot=await page.screenshot(full_page=True)
        (OUT/"normal-native-zoom.png").write_bytes(shot)
        verify_screen(shot,"normal-native-zoom")
        await page.locator("#atlasOriginalNeighbors").click()
        assert await page.evaluate("window.COEAtlas.originalNeighborVisible") is False
        assert await page.evaluate("window.COEAtlas.approvedBaselineLocked") is True
        assert await page.evaluate("window.COEAtlas.nodes") == 100
        assert await page.evaluate("window.COEAtlas.seams.every(s=>s.pass && s.endpointGapPx===0)") is True
        print("PASS protected V123 graph after scenic toggle")
        await context.close()

        # Simulate a baseline-art failure on iPhone. The direct image should
        # remain visible while the canvas bootstrap is unavailable.
        blocked=await browser.new_context(
            viewport={"width":390,"height":844},
            device_scale_factor=2,is_mobile=True,has_touch=True,
        )
        await blocked.route("**/terrain-grid/art/matrei-v121-original.webp",
                            lambda route: route.abort())
        page2=await blocked.new_page()
        await inspect(page2,"baseline-art-blocked-recovery",False)
        print("PASS emergency ridge preview survives failed base artwork")
        await browser.close()


if __name__=="__main__":
    asyncio.run(main())
