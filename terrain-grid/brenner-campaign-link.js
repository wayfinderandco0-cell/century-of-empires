/*
 * V305 rendering bridge. The campaign's orders, army sprites, saves,
 * province ownership, and continuous-time rules are not modified.
 */
(()=>{'use strict';
 const screen=document.getElementById('mapScreen'),svg=document.getElementById('map');
 if(!screen||!svg)return;
 const style=document.createElement('style');
 style.textContent=[
 '#brennerLensBtn{position:fixed;left:8px;bottom:max(9px,env(safe-area-inset-bottom));z-index:45;background:#314b3b;border:1px solid #d0b27b;color:#fff0cc;border-radius:8px;padding:8px 11px;min-height:44px;font:750 12px system-ui;box-shadow:0 3px 12px #0008}',
 '#brennerLensBtn:focus-visible{outline:2px solid #ffcf81}',
 '#brennerLens{position:fixed;inset:0;z-index:1100;background:#14261e}',
 '#brennerLens[hidden]{display:none!important}',
 '#brennerLens iframe{position:absolute;inset:0;width:100%;height:100%;border:0}',
 '#brennerLensClose{position:absolute;top:max(80px,env(safe-area-inset-top) + 73px);left:8px;z-index:12;min-height:42px;min-width:96px;background:#1c3429;color:#fff6de;border:1px solid #cab284;border-radius:8px;font:750 12px system-ui;padding:8px 11px;box-shadow:0 2px 10px #0009}',
 '#brennerLensPin{cursor:pointer}',
 '#brennerLensPin circle{fill:#f4cf87;stroke:#15271e;stroke-width:3}',
 '#brennerLensPin text{fill:#fff2d4;font:700 11px Georgia,serif;paint-order:stroke;stroke:#16281e;stroke-width:3px;pointer-events:none}'
 ].join('\n');
 document.head.appendChild(style);
 const button=document.createElement('button');
 button.type='button';button.id='brennerLensBtn';button.textContent='🏔 Brenner terrain';
 button.setAttribute('aria-label','Open geographic Brenner terrain');screen.appendChild(button);
 const host=document.createElement('div');host.id='brennerLens';host.hidden=true;
 const iframe=document.createElement('iframe');iframe.id='brennerLensFrame';
 iframe.setAttribute('title','Brenner relief, streams and historic settlements');
 const close=document.createElement('button');close.id='brennerLensClose';close.type='button';
 close.textContent='← Campaign map';host.append(iframe,close);document.body.appendChild(host);
 let previouslyFocused=null;
 function open(){
  previouslyFocused=document.activeElement;
  const title=document.getElementById('clockTitle')?.textContent||'1780';
  const year=Number(title.match(/17[89]\d|18\d\d/)?.[0])||1780;
  iframe.src='./brenner-corridor.html?year='+Math.max(1780,Math.min(1880,year));
  host.hidden=false;document.body.style.overflow='hidden';close.focus();
 }
 function dismiss(){
  host.hidden=true;iframe.removeAttribute('src');
  document.body.style.overflow='';previouslyFocused?.focus?.();
 }
 button.addEventListener('click',open);close.addEventListener('click',dismiss);
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!host.hidden)dismiss()});
 const NS='http://www.w3.org/2000/svg',pin=document.createElementNS(NS,'g');
 pin.id='brennerLensPin';pin.setAttribute('tabindex','0');pin.setAttribute('role','button');
 pin.setAttribute('aria-label','Inspect Brenner mountains and Matrei terrain');
 const x=42+(11.45366+15)*25.3,y=34+(73-47.13125)*25.2;
 pin.setAttribute('transform','translate('+x+' '+y+')');
 const circle=document.createElementNS(NS,'circle');circle.setAttribute('r','9');
 const label=document.createElementNS(NS,'text');label.setAttribute('x','15');label.setAttribute('y','4');
 label.textContent='Brenner';pin.append(circle,label);svg.appendChild(pin);
 pin.addEventListener('click',e=>{e.stopPropagation();open()});
 pin.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open()}});
 window.COEBrennerLens=Object.freeze({open,close:dismiss,
  get openNow(){return !host.hidden},geoAnchor:[11.45366,47.13125],modifiesGame:false});
})();