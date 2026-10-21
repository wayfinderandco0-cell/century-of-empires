/* Century of Empires V116: conservative local-art renderer.
 * Render the EXISTING V115 oblique artwork in a single stitched source crop,
 * so independent child tiles cannot create visible seams. This module does
 * not approve a road, crossing, settlement, conquest or historical geography.
 * Camera and route positions use V94 world coordinates (1448 x 1086).
 */
(function(root) {
  "use strict";
  function finite(n) { return typeof n === "number" && Number.isFinite(n); }
  function rect(r) {
    return Array.isArray(r) && r.length === 4 &&
      r.every(finite) && r[0] < r[2] && r[1] < r[3];
  }
  function overlap(a,b) {
    return a[0] < b[2] && a[2] > b[0] &&
           a[1] < b[3] && a[3] > b[1];
  }
  function validate(index) {
    if (!index || index.kind !== "unverified_local_art_tile_index" ||
        !rect(index.artBoxWorldPx) || !Array.isArray(index.artSizePx) ||
        index.artSizePx.length !== 2 || index.artSizePx.some(n => !Number.isInteger(n) || n < 1) ||
        !index.grid || !Number.isInteger(index.grid.columns) ||
        !Number.isInteger(index.grid.rows) || index.grid.columns < 1 || index.grid.rows < 1 ||
        !Array.isArray(index.tiles) ||
        index.tiles.length !== index.grid.columns * index.grid.rows) {
      throw Error("Invalid V116 local tile index");
    }
    const [aw,ah]=index.artSizePx, [x0,y0,x1,y1]=index.artBoxWorldPx;
    const seen=new Set(), xs=new Map(), ys=new Map();
    for (const t of index.tiles) {
      if (!t || !Number.isInteger(t.row) || !Number.isInteger(t.col) ||
          t.row<0 || t.row>=index.grid.rows || t.col<0 || t.col>=index.grid.columns ||
          !rect(t.imageCropPx) || !rect(t.worldRectPx) ||
          t.traversable || t.conquerable || t.deepZoomEligible || t.paintedRoadVerified) {
        throw Error("Invalid or prematurely playable V116 child tile");
      }
      const key=t.row+":"+t.col;
      if (seen.has(key)) throw Error("Duplicate child tile");
      seen.add(key);
      const p=t.imageCropPx,w=t.worldRectPx;
      if (!p.every(Number.isInteger) || p[0]<0 || p[1]<0 || p[2]>aw || p[3]>ah) {
        throw Error("Invalid source crop");
      }
      const expected=[x0+(x1-x0)*p[0]/aw,y0+(y1-y0)*p[1]/ah,
                      x0+(x1-x0)*p[2]/aw,y0+(y1-y0)*p[3]/ah];
      if (expected.some((v,i)=>Math.abs(v-w[i])>1e-8)) {
        throw Error("Child/world transform mismatch");
      }
      for(const [axis,k,start,end,map] of [
        ["x",t.col,p[0],p[2],xs],["y",t.row,p[1],p[3],ys]]) {
        const old=map.get(k);
        if(old && (old[0]!==start || old[1]!==end)) throw Error(axis+" crop edge mismatch");
        map.set(k,[start,end]);
      }
    }
    for(const [edges,count,size] of [[xs,index.grid.columns,aw],[ys,index.grid.rows,ah]]) {
      let prev=0;
      for(let i=0;i<count;i++) {
        const e=edges.get(i);
        if(!e || e[0]!==prev) throw Error("Missing or overlapping child tile edge");
        prev=e[1];
      }
      if(prev!==size) throw Error("Child tiles do not cover artwork");
    }
    return index;
  }
  function visible(index,camera) {
    if(!rect(camera)) throw Error("Invalid world camera");
    return index.tiles.filter(t=>overlap(t.worldRectPx,camera));
  }
  function stitch(index,camera) {
    const tiles=visible(index,camera);
    if(!tiles.length) return null;
    const p=[Infinity,Infinity,-Infinity,-Infinity];
    for(const t of tiles) {
      const q=t.imageCropPx;
      p[0]=Math.min(p[0],q[0]);p[1]=Math.min(p[1],q[1]);
      p[2]=Math.max(p[2],q[2]);p[3]=Math.max(p[3],q[3]);
    }
    const [aw,ah]=index.artSizePx,[x0,y0,x1,y1]=index.artBoxWorldPx;
    return {source:p,world:[x0+(x1-x0)*p[0]/aw,y0+(y1-y0)*p[1]/ah,
                            x0+(x1-x0)*p[2]/aw,y0+(y1-y0)*p[3]/ah],
            visibleTileCount:tiles.length};
  }
  function worldToScreen(point,camera,viewport) {
    if(!Array.isArray(point)||point.length!==2||!point.every(finite)||!rect(camera)||
       !viewport||!finite(viewport.width)||!finite(viewport.height)||
       viewport.width<=0||viewport.height<=0) throw Error("Invalid world/screen transform");
    return [(point[0]-camera[0])*viewport.width/(camera[2]-camera[0]),
            (point[1]-camera[1])*viewport.height/(camera[3]-camera[1])];
  }
  function screenToWorld(point,camera,viewport) {
    if(!Array.isArray(point)||point.length!==2||!point.every(finite)||!rect(camera)||
       !viewport||!finite(viewport.width)||!finite(viewport.height)||
       viewport.width<=0||viewport.height<=0) throw Error("Invalid screen/world transform");
    return [camera[0]+point[0]*(camera[2]-camera[0])/viewport.width,
            camera[1]+point[1]*(camera[3]-camera[1])/viewport.height];
  }
  function artToWorld(index,p) {
    if(!Array.isArray(p)||p.length!==2||!p.every(finite)) throw Error("Invalid art pixel");
    const [aw,ah]=index.artSizePx,[x0,y0,x1,y1]=index.artBoxWorldPx;
    return [x0+p[0]*(x1-x0)/aw,y0+p[1]*(y1-y0)/ah];
  }
  function draw(ctx,image,index,camera,viewport) {
    validate(index);
    if(!ctx || typeof ctx.drawImage!=="function" || !image ||
       image.width!==index.artSizePx[0] || image.height!==index.artSizePx[1]) {
      throw Error("Canvas context or V115 image size mismatch");
    }
    const crop=stitch(index,camera);
    if(!crop) return {drawCalls:0,visibleTileCount:0};
    const p=crop.source,w=crop.world;
    const a=worldToScreen([w[0],w[1]],camera,viewport);
    const b=worldToScreen([w[2],w[3]],camera,viewport);
    // One source crop / one draw call: no tile-by-tile interpolation seams.
    ctx.drawImage(image,p[0],p[1],p[2]-p[0],p[3]-p[1],
                  a[0],a[1],b[0]-a[0],b[1]-a[1]);
    return {drawCalls:1,visibleTileCount:crop.visibleTileCount,
            sourceCrop:p,worldCrop:w};
  }
  const api={validate,visible,stitch,worldToScreen,screenToWorld,artToWorld,draw};
  if(typeof module==="object" && module.exports) module.exports=api;
  else root.CenturyV116Tiles=api;
})(typeof globalThis!=="undefined"?globalThis:this);
