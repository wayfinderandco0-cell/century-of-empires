#!/usr/bin/env python3
"""V262: build an OFFLINE, iPhone-friendly, unapproved exact-pixel art viewer.

No gameplay integration, map edits, historical claims, network, or production
approval. This is a visual alternative for reviewing two *actual* V260 assets.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
from PIL import Image

PINS = {
    'west': '36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7',
    'south': 'd63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb',
}
# Exact, immutable V123 road geometry; viewer only, NEVER a route edit.
ROADS = {
    'west': [[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],
             [980,515],[890,535],[784,551],[680,560],[570,540],
             [470,520],[370,522],[275,550]],
    'south': [[466,0],[466,74],[470,160],[488,235],[540,310],
              [620,350],[700,400],[805,442],[930,510],[1050,550],
              [1140,585],[1270,605]],
}

def check(path, tile):
    data=Path(path).read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    if digest!=PINS[tile]:
        raise ValueError(f'{tile}: exact V260/V258 SHA256 mismatch: {digest}')
    with Image.open(path) as im:
        if im.size!=(1536,1024) or im.format!='PNG':
            raise ValueError(f'{tile}: require original 1536x1024 PNG')
    return 'data:image/png;base64,'+base64.b64encode(data).decode('ascii')

def build(west, south, output, matrei_context=None):
    images={tile:check(path,tile) for tile,path in [('west',west),('south',south)]}
    if matrei_context:
        with Image.open(matrei_context) as im:
            if im.size[0]<200 or im.size[1]<200:raise ValueError('Matrei context too small')
        images['matrei']='data:image/png;base64,'+base64.b64encode(Path(matrei_context).read_bytes()).decode('ascii')
    payload=json.dumps({'images':images,'roads':ROADS,'hashes':PINS},separators=(',',':'))
    html=HTML.replace('/*__PAYLOAD__*/', 'const ART='+payload+';')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(html,encoding='utf-8')
    return {'file':str(output),'bytes':output.stat().st_size,
            'sourceSHA256':PINS,'tiles':['west','south'],
            'matreiContextScreenshotOnly':bool(matrei_context),
            'actualGameplayRenderer':False,'browserGameTested':False,
            'historicalGeographyVerified':False,'bridgeBanksVerified':False,
            'strictV203Passed':False,'userVisualApproval':False,'productionApproved':False}

HTML=r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover,user-scalable=no">
<title>Century of Empires — V262 unapproved terrain inspection</title>
<style>
:root{color-scheme:dark;font:14px system-ui,-apple-system,sans-serif;background:#0c1915;color:#eee5d1}
*{box-sizing:border-box}body{margin:0;overflow:hidden}#view{position:fixed;inset:0;width:100%;height:100%;touch-action:none}
#top{position:fixed;top:max(5px,env(safe-area-inset-top));left:5px;right:5px;z-index:2;background:#10251fe8;border:1px solid #c8b38b;border-radius:9px;padding:7px;max-width:800px}
#top b{font:700 14px Georgia,serif}#top small{display:block;font-size:10px;color:#e4bd91;margin:3px 0 5px}
button{font:inherit;color:#f5ebd6;background:#29443b;border:1px solid #a99778;border-radius:7px;min-height:34px;padding:4px 10px;margin:2px}
button[aria-pressed="true"]{background:#665537;border-color:#ffe2a4}
#bottom{position:fixed;bottom:max(5px,env(safe-area-inset-bottom));left:5px;right:5px;background:#10251fe8;border:1px solid #c8b38b;border-radius:9px;padding:7px;max-width:800px;font-size:11px;pointer-events:none}
#bottom strong{color:#f2ba83}
@media(max-height:480px){#top{max-width:90vw}#top small{display:none}button{min-height:28px}#bottom{max-width:70vw}}
</style></head><body><canvas id="view"></canvas>
<div id="top"><b>CENTURY OF EMPIRES · V262 ART REVIEW</b><small>Exact V258 WEST + V260 SOUTH pixels. Fictional geography. NOT playable or approved.</small>
<div><button data-tile="west" aria-pressed="true">WEST</button><button data-tile="south" aria-pressed="false">SOUTH</button><button data-tile="matrei" aria-pressed="false" id="matreiBtn" hidden>MATREI screenshot</button>
<button id="road" aria-pressed="true">V123 route ON</button><button id="fit">Fit</button></div></div>
<div id="bottom"><strong>UNAPPROVED.</strong> Pinch/drag to inspect physical road pixels. Red dashed line = unchanged V123 route. Matrei reference is a prior browser screenshot, NOT an aligned source tile. No 1780 road or bridge-bank verification.</div>
<script>/*__PAYLOAD__*/
'use strict';const canvas=document.getElementById('view'),ctx=canvas.getContext('2d');
const loaded={},states={};let tile='west',route=true,scale=1,ox=0,oy=0,w=innerWidth,h=innerHeight;
let touches=new Map(),gesture=null;
function redraw(){const dpr=Math.min(devicePixelRatio||1,3);w=innerWidth;h=innerHeight;
 if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#0c1915';ctx.fillRect(0,0,w,h);
 const im=loaded[tile];if(!im)return;
 ctx.save();ctx.translate(ox,oy);ctx.scale(scale,scale);ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(im,0,0);
 if(route&&ART.roads[tile]){ctx.beginPath();ART.roads[tile].forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));
 ctx.strokeStyle='#ff4747';ctx.lineWidth=4/scale;ctx.setLineDash([13/scale,9/scale]);ctx.stroke();ctx.setLineDash([])}ctx.restore();}
function fit(){const im=loaded[tile];if(!im)return;w=innerWidth;h=innerHeight;const top=document.querySelector('#top').getBoundingClientRect().bottom+8;const bottom=h-document.querySelector('#bottom').getBoundingClientRect().top+8;const space=Math.max(40,h-top-bottom);scale=Math.max(.1,Math.min(w/im.width,space/im.height));ox=(w-im.width*scale)/2;oy=top+(space-im.height*scale)/2;redraw()}
function select(next){if(!loaded[next])return;if(loaded[tile]&&scale>0)states[tile]=[scale,ox,oy];tile=next;
 document.querySelectorAll('[data-tile]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.tile===tile)));
 if(states[tile]){[scale,ox,oy]=states[tile];redraw()}else fit()}
function zoomAt(x,y,factor){const ns=Math.max(.15,Math.min(7,scale*factor));ox=x-(x-ox)*ns/scale;oy=y-(y-oy)*ns/scale;scale=ns;redraw()}
canvas.addEventListener('pointerdown',e=>{canvas.setPointerCapture(e.pointerId);touches.set(e.pointerId,[e.clientX,e.clientY]);gesture=null});
canvas.addEventListener('pointermove',e=>{if(!touches.has(e.pointerId))return;const old=touches.get(e.pointerId);touches.set(e.pointerId,[e.clientX,e.clientY]);const points=[...touches.values()];
 if(points.length===1){ox+=e.clientX-old[0];oy+=e.clientY-old[1];redraw()}else if(points.length===2){const dist=Math.hypot(points[0][0]-points[1][0],points[0][1]-points[1][1]);const mid=[(points[0][0]+points[1][0])/2,(points[0][1]+points[1][1])/2];
 if(gesture&&gesture.dist>0)zoomAt(mid[0],mid[1],dist/gesture.dist);gesture={dist}}});
function up(e){touches.delete(e.pointerId);gesture=null}canvas.addEventListener('pointerup',up);canvas.addEventListener('pointercancel',up);
canvas.addEventListener('wheel',e=>{e.preventDefault();zoomAt(e.clientX,e.clientY,e.deltaY<0?1.18:1/1.18)},{passive:false});
document.querySelectorAll('[data-tile]').forEach(b=>b.onclick=()=>select(b.dataset.tile));
document.getElementById('road').onclick=e=>{route=!route;e.currentTarget.setAttribute('aria-pressed',String(route));e.currentTarget.textContent='V123 route '+(route?'ON':'OFF');redraw()};
document.getElementById('fit').onclick=fit;
for(const [name,url] of Object.entries(ART.images)){const im=new Image();im.onload=()=>{loaded[name]=im;if(name===tile)fit()};im.src=url}
if(ART.images.matrei)document.getElementById('matreiBtn').hidden=false;
addEventListener('resize',()=>{if(loaded[tile])fit()});
</script></body></html>'''

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--west',type=Path,required=True);p.add_argument('--south',type=Path,required=True)
    p.add_argument('--matrei-context',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.west,a.south,a.out,a.matrei_context)))
