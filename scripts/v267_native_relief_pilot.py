#!/usr/bin/env python3
"""Original continuous 2.5D relief pilot for Century of Empires.

Creates eight adjacent 1536x1024 octagonal scene assets from one continuous
V94 DEM/woodland coordinate system. No aerial photograph is used. This is a
candidate art pipeline, not an assertion of V267 visual approval or playability.
The proposed cartways are fictional art-only routes, not 1780 historical roads.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter, distance_transform_edt
from PIL import Image, ImageDraw
from v267_relief_materials import enrich_surface, paint_tree

TW, TH, COLS, ROWS = 1536, 1024, 4, 2
C0, R0 = 7, 12
SEED = 2671030

def smooth_noise(rng, shape, spacing):
    gh = max(3, math.ceil(shape[0]/spacing)+3)
    gw = max(3, math.ceil(shape[1]/spacing)+3)
    a = rng.normal(size=(gh,gw)).astype(np.float32)
    yy,xx = np.mgrid[0:shape[0],0:shape[1]].astype(np.float32)
    return map_coordinates(a, [yy/spacing+1,xx/spacing+1], order=3, mode='reflect').astype(np.float32)

def road_centerlines(W,H,s):
    """One world-space contract: border positions are mathematically identical."""
    x = np.arange(W, dtype=np.float32)
    roads=[]
    for row in range(ROWS):
        y = (row+.47)*TH*s + s*(64*np.sin(x/(550*s)+row*.4)+25*np.sin(x/(173*s)+row*1.4))
        roads.append(np.column_stack((x,y)))
    for col in (1,3):
        x0=(col+.48)*TW*s
        y0=int(roads[0][round(x0),1]-20*s)
        y1=int(roads[1][round(x0),1]+20*s)
        y=np.arange(max(0,y0),min(H,y1),dtype=np.float32)
        xp=x0+s*(65*np.sin(y/(460*s)+col)+21*np.sin(y/(132*s)+col))
        roads.append(np.column_stack((xp,y)))
    return roads

def build(root:Path, out:Path, scale:float=1):
    if not (0.2<=scale<=1): raise ValueError('scale 0.2..1')
    rng=np.random.default_rng(SEED)
    w,h=round(TW*COLS*scale),round(TH*ROWS*scale)
    dem=json.loads((root/'terrain-v94/heights.json').read_text())
    woods=json.loads((root/'terrain-v94/woods.json').read_text())
    assert dem['width']==woods['width']==512 and dem['height']==woods['height']==384
    geo=json.loads((root/'terrain-v94/manifest.json').read_text())
    assert geo['projection']=='equirectangular' and len(geo['extent'])==4
    west,south,east,north=map(float,geo['extent'])
    assert west<east and south<north
    demarr=np.asarray(dem['heights'],dtype=np.float32).reshape(384,512)
    woodarr=np.asarray(woods['forest'],dtype=np.float32).reshape(384,512)
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    gx=(C0+xx/(TW*scale))*512/18
    gy=(R0+yy/(TH*scale))*384/24
    elev=map_coordinates(demarr,[gy,gx],order=3,mode='nearest')
    forest=map_coordinates(woodarr,[gy,gx],order=1,mode='nearest')
    relief=np.clip((elev-180)/1700,0,1)
    n1=smooth_noise(rng,(h,w),max(8,round(330*scale)))
    n2=smooth_noise(rng,(h,w),max(4,round(85*scale)))
    n3=smooth_noise(rng,(h,w),max(2,round(24*scale)))
    n4=smooth_noise(rng,(h,w),max(2,round(7*scale)))
    # Broad DEM is measured; small-scale details are explicitly synthetic.
    z=elev + (20+100*relief)*n1 + (7+35*relief)*n2 + (2+10*relief)*n3
    z=z+(1+3*relief)*n4
    roads=road_centerlines(w,h,scale)
    center=np.zeros((h,w),dtype=np.uint8)
    for route in roads:
        ix=np.clip(np.rint(route[:,0]).astype(int),0,w-1)
        iy=np.clip(np.rint(route[:,1]).astype(int),0,h-1)
        center[iy,ix]=1
    distance=distance_transform_edt(1-center).astype(np.float32)
    corridor=np.exp(-.5*(distance/(12*scale))**2)
    z=z*(1-.4*corridor)+gaussian_filter(z,max(1,9*scale))*.4*corridor
    # Export the ACTUAL heightfield used to shade and paint the terrain.
    # Previously the glTF exporter independently invented another field:
    # its meshes could be seamless yet visibly disagree with the ground art.
    # Sample once in world coordinates so adjoining tile vertices are identical.
    heightfield_name=None
    if scale == 1:
        out.mkdir(parents=True,exist_ok=True)
        step=16
        grid=np.empty((h//step+1,w//step+1),dtype=np.float32)
        grid[:-1,:-1]=z[::step,::step]
        grid[-1,:-1]=z[-1,::step]
        grid[:-1,-1]=z[::step,-1]
        grid[-1,-1]=z[-1,-1]
        grid=(grid-150)/11.0
        heightfield_name='heightfield-step16.npy'
        np.save(out/heightfield_name,grid,allow_pickle=False)
        del grid
    dy,dx=np.gradient(z)
    dx/=max(.2,scale);dy/=max(.2,scale)
    nx=-dx*.028;ny=-dy*.028
    shade=(.72+.30*(.58*nx-.78*ny+1)/np.sqrt(1+nx*nx+ny*ny)).clip(.42,1.12)
    shade*=np.clip(1-.17*np.maximum(0,gaussian_filter(z,max(2,36*scale))-z)/110, .72,1.04)
    t=np.clip((elev-500)/2200,0,1)
    low=np.stack((np.full_like(elev,111),np.full_like(elev,132),np.full_like(elev,79)),axis=-1)
    green=np.stack((np.full_like(elev,72),np.full_like(elev,106),np.full_like(elev,66)),axis=-1)
    stone=np.stack((np.full_like(elev,146),np.full_like(elev,139),np.full_like(elev,117)),axis=-1)
    snowy=np.stack((np.full_like(elev,203),np.full_like(elev,201),np.full_like(elev,185)),axis=-1)
    f=np.clip(forest*.78+.08*n1,0,1)[...,None]
    rgb=low*(1-f)+green*f
    rock=np.clip((t-.3)*1.5+.09*n2,0,1)[...,None]
    rgb=rgb*(1-rock)+stone*rock
    snow=np.clip((t-.82)*5+.1*n2,0,1)[...,None]
    rgb=rgb*(1-snow)+snowy*snow
    grain=3*n3+1.5*n4
    rgb=(rgb*shade[...,None]+grain[...,None]).clip(0,255).astype(np.uint8)
    rgb=enrich_surface(rgb,z,elev,forest,distance,n3,n4,scale)
    edge=np.clip((distance-4.3*scale)/(2.2*scale),0,1)
    roadgrain=(n3*6+n4*3)
    roadcolor=np.stack((153+roadgrain,132+roadgrain,99+roadgrain),axis=-1)
    rgb=rgb*edge[...,None]+roadcolor*(1-edge[...,None])
    track=np.exp(-.5*((distance-2.5*scale)/(0.75*scale))**2)
    rgb-=track[...,None]*9
    im=Image.fromarray(np.clip(rgb,0,255).astype(np.uint8),'RGB')
    # Preserve a separate original terrain-only material for true 3D trees.
    # The native 2D fallback keeps its painted trees; 3D never double-stacks them.
    ground_im=im.copy()
    dr=ImageDraw.Draw(im,'RGBA')
    trees=[]
    stride=max(7,round(21*scale))
    for y in range(stride//2,h,stride):
        for x in range(stride//2,w,stride):
            if rng.random()>.54:continue
            tx=int(np.clip(x+rng.normal(0,stride*.55),0,w-1))
            ty=int(np.clip(y+rng.normal(0,stride*.55),0,h-1))
            if forest[ty,tx]<.32 or elev[ty,tx]>1900 or distance[ty,tx]<17*scale:continue
            if rng.random()>min(.94,.20+.72*forest[ty,tx]):continue
            trees.append((ty,tx,4.2+5.7*rng.random(),rng.random(),rng.random()))
    trees.sort()
    for ty,tx,r,kind,light in trees:
        paint_tree(dr,ty,tx,r,kind,light,scale)
    out.mkdir(parents=True,exist_ok=True)
    manifest={'schema':'coe-v267-native-relief-pilot/v1','referenceCommit':'456107f28c8db1f87522bbc7511809b2a215f6fb',
      'status':'original-3d-relief-candidates-NOT-V267-approved','sourceElevation':'V94 Mapzen/AWS Terrarium DEM',
      'sourceForest':'V94 Natural Earth II approximate modern cover','historicalRoadsVerified':False,
      'artRoads':'fictional provisional corridors; not gameplay routes','grid':[COLS,ROWS],
      'nativeSize':[TW,TH],'scale':scale,'treesRendered':len(trees),
      'depthRendering':'directional terrain self-shadow, slope-aware limestone and tiered tree crowns',
      'true3DMesh':False,'visuallyApprovedV267':False,'cells':[],'seams':[],'inlays':[],
      'meshSourceHeightfield':heightfield_name,
      'meshSourceHeightfieldSha256':hashlib.sha256((out/heightfield_name).read_bytes()).hexdigest() if heightfield_name else None,
      'meshGroundArtAligned':bool(heightfield_name),
      'geographicReference':{'projection':'WGS84 equirectangular','extent':[west,south,east,north],
        'sourceManifest':'terrain-v94/manifest.json',
        'sourceElevation':geo['elevationSource'],'sourceVegetation':geo['vegetationSource']},
      'scaleLimitation':'Regional tiles span degrees; 3D tree instances are illustrative forest markers, NOT physically scaled individual trees.'}
    tw,th=round(TW*scale),round(TH*scale)
    mask=Image.new('L',(tw,th),0);md=ImageDraw.Draw(mask)
    bevel=round(256*scale)
    md.polygon([(bevel,0),(tw-bevel,0),(tw,bevel),(tw,th-bevel),
                (tw-bevel,th),(bevel,th),(0,th-bevel),(0,bevel)],fill=255)
    contact=Image.new('RGB',(COLS*384,ROWS*256),(28,40,35))
    for row in range(ROWS):
        for col in range(COLS):
            x0,y0=col*tw,row*th
            tile=im.crop((x0,y0,x0+tw,y0+th)).convert('RGBA');tile.putalpha(mask)
            cid=f'pilot-{col}-{row}'
            file=out/(cid+'.png');tile.save(file,optimize=True)
            ground_tile=ground_im.crop((x0,y0,x0+tw,y0+th)).convert('RGBA')
            ground_tile.putalpha(mask)
            ground_file=out/(cid+'-ground.png')
            ground_tile.save(ground_file,optimize=True)
            sha=hashlib.sha256(file.read_bytes()).hexdigest()
            manifest['cells'].append({'id':cid,'grid':[col,row],'worldOrigin':[col*TW,row*TH],
                'image':file.name,'sha256':sha,
                'meshGroundImage':ground_file.name,
                'meshGroundSha256':hashlib.sha256(ground_file.read_bytes()).hexdigest(),
                'nativeArt':True,'photographicCrop':False,
                'visualApproved':False,'nativeGamePlayable':False,'historicallyVerified':False,
                'geographicBoundsWGS84':[
                    round(west+(C0+col)/18*(east-west),6),
                    round(north-(R0+row+1)/24*(north-south),6),
                    round(west+(C0+col+1)/18*(east-west),6),
                    round(north-(R0+row)/24*(north-south),6)],
                'historicalEvidence':{'period':'1780-1880','roadSources':[],
                                      'settlementSources':[],'status':'unverified'}})
            thumb=tile.resize((384,256),Image.Resampling.LANCZOS)
            contact.paste(thumb,(col*384,row*256),thumb)
    # Fill the three interstitial diamonds from the SAME continuous original
    # raster, not stretched corner textures or fake roads. Inlays are scenery,
    # never routable graph nodes.
    for col in range(COLS-1):
        ix=(col+1)*tw
        iy=th
        gap=round(256*scale)
        patch=im.crop((ix-gap,iy-gap,ix+gap,iy+gap)).convert('RGBA')
        alpha=Image.new('L',(2*gap,2*gap),0)
        ImageDraw.Draw(alpha).polygon([(gap,0),(2*gap,gap),
                                       (gap,2*gap),(0,gap)],fill=255)
        patch.putalpha(alpha)
        name=f'infill-{col}-0.png'
        patch.save(out/name,optimize=True)
        ground_patch=ground_im.crop((ix-gap,iy-gap,ix+gap,iy+gap)).convert('RGBA')
        ground_patch.putalpha(alpha)
        ground_name=f'infill-{col}-0-ground.png'
        ground_patch.save(out/ground_name,optimize=True)
        manifest['inlays'].append({
            'id':f'infill-{col}-0',
            'worldCenter':[(col+1)*TW,TH],
            'image':name,'meshGroundImage':ground_name,
            'meshGroundSha256':hashlib.sha256((out/ground_name).read_bytes()).hexdigest(),
            'imageSize':[2*gap,2*gap],
            'playable':False,'roadNodes':[],
            'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest()
        })
    contact.save(out/'contact-sheet.webp',quality=88)
    for row in range(ROWS):
        for col in range(COLS-1):
            x=(col+1)*tw
            ys=np.where(center[:,x-1] | center[:,x])[0]
            local=[int(v-row*th) for v in ys if row*th<=v<(row+1)*th]
            manifest['seams'].append({'a':f'pilot-{col}-{row}','b':f'pilot-{col+1}-{row}',
                'side':'east-west','roadCrossingLocalY':local[:16],'sameWorldRaster':True})
    for col in (1,3):
        x0=col*tw
        xs=np.where(center[th-1,:] | center[th,:])[0]
        local=[int(v-x0) for v in xs if x0<=v<x0+tw]
        manifest['seams'].append({'a':f'pilot-{col}-0','b':f'pilot-{col}-1',
            'side':'north-south','roadCrossingLocalX':local[:16],'sameWorldRaster':True})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (out/'index.html').write_text('''<!doctype html><html><meta name="viewport" content="width=device-width,initial-scale=1"><title>Original 3D relief pilot</title><style>body{margin:0;background:#172720;color:#f1e4c6;font:15px system-ui}header{padding:12px}img{display:block;max-width:100%;height:auto;margin:auto}small{color:#ffce9a}</style><header><b>Eight contiguous original relief octagons — 4 × 2</b><br><small>UNAPPROVED CANDIDATES · Original DEM-shaded terrain, not aerial-photo crops · Fictional provisional roads, not playable</small></header><img src="contact-sheet.webp" alt="Eight 3D relief octagons"></html>''')
    print(json.dumps({'cells':len(manifest['cells']),'trees':len(trees),'seams':len(manifest['seams']),
      'decorativeInlays':len(manifest['inlays']),
      'visualApproved':0,'nativePlayable':0,'historicalRoadsVerified':0,'finishedToday':0}))

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--out',type=Path,default=Path('generated/v267-relief-pilot'))
    ap.add_argument('--scale',type=float,default=1)
    args=ap.parse_args();build(args.root,args.out,args.scale)
