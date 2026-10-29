#!/usr/bin/env python3
"""Actual embedded V267 art + unchanged V123 graph mobile review; NOT approval."""
import argparse, json, pathlib
from playwright.sync_api import sync_playwright

REPO = pathlib.Path(__file__).resolve().parents[1]
HTML = REPO / 'v267-three-octagon-original-art-prototype.html'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--browser', choices=['chromium', 'webkit'], required=True)
    ap.add_argument('--orientation', choices=['portrait', 'landscape'], required=True)
    ap.add_argument('--out', default='art-reviews/v267-actual-browser')
    ap.add_argument('--chromium-path', default='')
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    html = HTML.read_text(encoding='utf-8')
    assert len(html) > 800_000 and 'ART_MATREI_CANONICAL' in html
    assert 'SOUTH_CARTWAY_EDGE_CONTACT_20261029' in html, 'Expected durable SOUTH photographic registration'
    w, h = (390, 844) if args.orientation == 'portrait' else (844, 390)
    errors = []
    with sync_playwright() as pw:
        browser_type = getattr(pw, args.browser)
        opts = {'headless': True}
        if args.browser == 'chromium' and args.chromium_path:
            opts['executable_path'] = args.chromium_path
            opts['args'] = ['--no-sandbox']
        browser = browser_type.launch(**opts)
        ctx = browser.new_context(viewport={'width': w, 'height': h},
                                  device_scale_factor=2, is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(html, wait_until='load')
        page.wait_for_function('window.COE && COE.originalMatreiLoaded && COE.sourceRegistered', timeout=30000)
        state = page.evaluate("""() => ({nodes:COE.nodes, unique:COE.uniqueWorldNodes,
          seams:COE.roadSeams, connected:COE.westSouthConnected,
          originalMatrei:COE.originalMatreiLoaded, engine:COE.engine,
          productionApproved:COE.productionApproved, inlays:COE.decorativeGapPatches})""")
        assert state['nodes'] == 100 and state['unique'] == 98 and state['connected']
        assert state['originalMatrei'] and not state['productionApproved']
        # This regression is about PIXEL INTEGRITY, not just V123 routes.
        # Trees outside narrow road cut-and-copy bands must be *identical*
        # to the original unwarped SOUTH photograph.
        native_comparison=page.evaluate("""() => {
          const native=nativeSouthTexture.getContext('2d').getImageData(0,0,W,H).data;
          const rebuilt=textures.south.getContext('2d').getImageData(0,0,W,H).data;
          const forest=[[120,300],[180,470],[310,640],[900,760],[1400,180],[950,920]];
          const pixels=(x,y,a)=>Array.from(a.slice((y*W+x)*4,(y*W+x)*4+4));
          const equality=forest.map(([x,y])=>{
            const source=pixels(x,y,native),product=pixels(x,y,rebuilt);
            return {point:[x,y],maxChannelDelta:Math.max(...source.map((v,i)=>Math.abs(v-product[i])))};
          });
          // The SOUTH photo is already baked to the V123 road entrance.
          // No additional runtime resampling may alter any source pixels.
          for(const [x,y] of [[466,270],[700,400],[930,510],[1270,605]]){
            const source=pixels(x,y,native),product=pixels(x,y,rebuilt);
            equality.push({point:[x,y],maxChannelDelta:Math.max(...source.map((v,i)=>Math.abs(v-product[i])))});
          }
          const entrance=[[466,0],[466,160]].map(([x,y])=>{
            const source=pixels(x,y,native),product=pixels(x,y,rebuilt);
            return {point:[x,y],maxChannelDelta:Math.max(...source.map((v,i)=>Math.abs(v-product[i])))};
          });
          return {equality,entrance,algorithm:'baked-SOUTH-photo-no-double-runtime-shift'};
        }""")
        # WebKit may introduce <=3 RGB levels during ImageData conversion.
        # Protected forest/gorge and the rest of the SOUTH source must match.
        assert all(row['maxChannelDelta']<=3 for row in native_comparison['equality']), native_comparison
        # The source was durably registered in the 1536x1024 JPEG. A second
        # runtime shift would make the photographed road miss the seam.
        assert all(row['maxChannelDelta']<=3 for row in native_comparison['entrance']), native_comparison

        assert state['inlays']==['north','square','east'], state['inlays']
        inlay_colors = page.evaluate("""() => inlays.map(p => {
          const c=p.canvas,w=c.width,h=c.height;
          return Array.from(c.getContext('2d').getImageData(
            Math.floor(w/2),Math.floor(h/2),1,1).data);
        })""")
        assert len(inlay_colors)==3 and all(color[3]==255 for color in inlay_colors), inlay_colors
        # Diamond-center texture should be sampled from ORIGINAL unwarped
        # SOUTH art, not stretched from the V123 registered gameplay tile.
        center = page.evaluate("""() => {
          const p=inlays.find(x=>x.name==='square');
          const a=p.canvas.getContext('2d').getImageData(256,256,1,1).data;
          const b=nativeSouthTexture.getContext('2d').getImageData(600,730,1,1).data;
          return [Array.from(a),Array.from(b)];
        }""")
        assert center[0][:3] == center[1][:3], center
        # The center is decorative scenery, NOT a new cross-tile route.
        page.evaluate('roadTap([1536,1024])')
        assert 'No road in the terrain infill' in page.locator('#status').inner_text()
        assert not page.evaluate('COE.moving')
        page.locator('#whole').click()
        page.wait_for_timeout(100)
        page.screenshot(path=str(out / f'{args.browser}-{args.orientation}-whole-three-gaps.png'))
        assert len(state['seams']) == 2 and all(s['pass'] and s['gap'] == 0 for s in state['seams'])
        for join in ('west', 'south'):
            page.locator('#' + join + 'join').click()
            page.wait_for_timeout(150)
            page.screenshot(path=str(out / f'{args.browser}-{args.orientation}-{join}-actual.png'))
            page.locator('#roads').click()
            page.wait_for_timeout(100)
            page.screenshot(path=str(out / f'{args.browser}-{args.orientation}-{join}-road-overlay.png'))
            page.locator('#roads').click()
        page.locator('#westjoin').click()
        page.touchscreen.tap(w / 2, h / 2)
        page.wait_for_timeout(150)
        assert page.evaluate('COE.moving'), 'touch on seam cartway failed to start march'
        page.evaluate('COE.halt()')
        assert not page.evaluate('COE.moving')
        assert page.evaluate('COE.marchWestToSouth()')
        path = page.evaluate('COE.route')
        assert len(path) > 40 and [1536, 478] in path and [2002, 1024] in path
        assert page.evaluate('COE.stepToEnd()') == [2806, 1629]
        assert not errors, errors
        result = {'browser': args.browser, 'orientation': args.orientation,
                  'viewport': [w, h], 'art': 'exact embedded original WEST/SOUTH + V121 Matrei',
                  'nodes': state['nodes'], 'uniqueWorldPositions': state['unique'],
                  'seams': state['seams'], 'touchMarch': True, 'halt': True,
                  'pathNodes': len(path), 'destination': [2806, 1629],
                  'javascriptErrors': errors, 'nativeIPhoneSafari': False,
                  'visualUserApproved': False, 'productionApproved': False, 'decorativeGapInlays': state['inlays'],
                  'nativeForestPreserved': native_comparison['equality'],
                  'southRegistrationScope': native_comparison['algorithm'],
                  'southEntranceRegistration': native_comparison['entrance'],
                  'inlayCenterPixels': inlay_colors}
        (out / f'{args.browser}-{args.orientation}-result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        ctx.close()
        browser.close()

if __name__ == '__main__':
    main()
