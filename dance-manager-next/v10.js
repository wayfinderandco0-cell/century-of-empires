/* Dance Manager Next V10 — correct the actual N3 marketing page's old stock photo sources.
   The saved approved image is used as five cropped photo assets. The interface stays real HTML. */
(function(){
 'use strict';
 if(typeof marketing!=='function')return;
 const prior=marketing;
 const replacements=[
  ['photo-1769694513443-c7292e174d48?auto=format&fit=crop&w=1800&q=85','./assets/hero-lavender-dancer.jpg'],
  ['photo-1558905566-ddbeb2fc2c2f?auto=format&fit=crop&w=900&q=83','./assets/studio-management.jpg'],
  ['photo-1771528471837-573223e7a6b0?auto=format&fit=crop&w=900&q=83','./assets/dancer-profiles.jpg'],
  ['photo-1741846895501-4c79409bc570?auto=format&fit=crop&w=1100&q=83','./assets/competition-management.jpg'],
  ['photo-1752652012592-8f618322a63c?auto=format&fit=crop&w=900&q=83','./assets/parent-portal.jpg'],
  ['photo-1760543320214-9a578e5c5b73?auto=format&fit=crop&w=900&q=83','./assets/hero-lavender-dancer.jpg']
 ];
 marketing=function(){
  let html=prior();
  for(const [stockSuffix,asset] of replacements){
    const exact='https://images.unsplash.com/'+stockSuffix;
    html=html.split(exact).join(asset);
  }
  // V3 and V9 legacy components coexist, but the actual N3 homepage owns the hero.
  return html;
 };
 const stylesheet=document.createElement('link');
 stylesheet.rel='stylesheet';
 stylesheet.href='./v10.css?v=10-photo-2';
 document.head.appendChild(stylesheet);
 render();
})();