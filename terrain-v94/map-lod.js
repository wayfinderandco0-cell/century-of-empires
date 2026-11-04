/*
 * Century of Empires — V304 geographic relief, rendering only.
 * Mapzen/AWS Terrarium z8 elevation + Natural Earth derived V94 atlas.
 * The atlas is not an 1780s land-cover or historical cartway survey.
 * This module never reads or writes army orders, province ownership, or saves.
 */
(() => {
  'use strict';
  const NS='http://www.w3.org/2000/svg';
  const grid={columns:4,rows:3,west:-14,east:49,north:75,south:26};
  const map=document.getElementById('map');
  const terrain=document.getElementById('terrainVisual');
  const viewport=document.getElementById('mapScroll');
  if(!map||!terrain||!viewport)return;
  // Identical geographic transform to index.html's proj(lon,lat).
  const project=(lon,lat)=>({x:42+(lon+15)*25.3,y:34+(73-lat)*25.2});
  const nw=project(grid.west,grid.north),se=project(grid.east,grid.south);
  const rect={x:nw.x,y:nw.y,width:se.x-nw.x,height:se.y-nw.y};
  const tileWidth=rect.width/grid.columns,tileHeight=rect.height/grid.rows;
  let group=null,overview=null,frame=0,loaded=0;
  const tiles=new Map(),broken=new Set();
  const debug={
    version:'v304',geographicExtent:[grid.west,grid.south,grid.east,grid.north],
    atlasPixels:[8192,6144],tileGrid:[4,3],renderOnly:true,
    source:'Mapzen z8 elevation + Natural Earth / idealized premodern cover',
    get overviewPresent(){return !!overview?.isConnected},
    get tileCount(){return tiles.size},
    get tileKeys(){return [...tiles.keys()]},
    get loadedTiles(){return loaded},
    get missingTiles(){return [...broken]},
    project
  };
  function image(src,x,y,w,h){
    const el=document.createElementNS(NS,'image');
    el.setAttribute('href',src);
    el.setAttribute('x',String(x));
    el.setAttribute('y',String(y));
    el.setAttribute('width',String(w));
    el.setAttribute('height',String(h));
    el.setAttribute('preserveAspectRatio','none');
    el.setAttribute('pointer-events','none');
    return el;
  }
  function mount(){
    // The original renderer reconstructs terrainVisual after country borders
    // load. Reattach the raster behind its existing detail without changing it.
    if(group?.parentNode!==terrain){
      for(const tile of tiles.values())tile.remove();
      tiles.clear();loaded=0;
      group=document.createElementNS(NS,'g');
      group.id='coeg-geographic-relief';
      group.setAttribute('pointer-events','none');
      group.setAttribute('opacity','.77');
      overview=image('./terrain-v94/overview.webp',rect.x,rect.y,rect.width,rect.height);
      overview.id='coeg-overview';
      overview.addEventListener('error',()=>{overview.setAttribute('visibility','hidden');debug.overviewError=true},{once:true});
      group.appendChild(overview);
      terrain.insertBefore(group,terrain.firstChild);
    }
    requestUpdate();
  }
  function visibleTile(c,r,view){
    const x=rect.x+c*tileWidth,y=rect.y+r*tileHeight;
    return x<view.right&&x+tileWidth>view.left&&y<view.bottom&&y+tileHeight>view.top;
  }
  function renderTiles(){
    if(group?.parentNode!==terrain){mount();return}
    const pxWidth=map.getBoundingClientRect().width||2250;
    const pixelsPerMapUnit=pxWidth/1700;
    // Keep the single lightweight overview for distant views.
    // Load only nearby full-resolution source tiles when zoomed in.
    const highDetail=pixelsPerMapUnit>=2.25;
    const margin=70/pixelsPerMapUnit;
    const view={
      left:viewport.scrollLeft/pixelsPerMapUnit-margin,
      right:(viewport.scrollLeft+viewport.clientWidth)/pixelsPerMapUnit+margin,
      top:viewport.scrollTop/pixelsPerMapUnit-margin,
      bottom:(viewport.scrollTop+viewport.clientHeight)/pixelsPerMapUnit+margin
    };
    const required=new Set();
    if(highDetail){
      for(let r=0;r<grid.rows;r++)for(let c=0;c<grid.columns;c++){
        if(!visibleTile(c,r,view))continue;
        const key=c+'-'+r;
        if(broken.has(key))continue;
        required.add(key);
        if(tiles.has(key))continue;
        const el=image('./terrain-v94/tiles/'+key+'.webp',
          rect.x+c*tileWidth,rect.y+r*tileHeight,tileWidth,tileHeight);
        el.dataset.tile=key;
        el.addEventListener('load',()=>{loaded++},{once:true});
        el.addEventListener('error',()=>{broken.add(key);if(tiles.get(key)===el)tiles.delete(key);el.remove()},{once:true});
        group.appendChild(el);
        tiles.set(key,el);
      }
    }
    for(const [key,el] of tiles){
      if(!required.has(key)){el.remove();tiles.delete(key)}
    }
    // Overview stays in place during tile loading, avoiding blank gaps on iPhone.
    debug.viewMode=highDetail?'detail':'overview';
    debug.visibleTiles=required.size;
    debug.screenScale=pixelsPerMapUnit;
  }
  function requestUpdate(){
    if(frame)return;
    frame=requestAnimationFrame(()=>{frame=0;renderTiles()});
  }
  window.COEMapArt=Object.freeze({mount,update:requestUpdate,debug});
  viewport.addEventListener('scroll',requestUpdate,{passive:true});
  window.addEventListener('resize',requestUpdate,{passive:true});
  mount();
})();