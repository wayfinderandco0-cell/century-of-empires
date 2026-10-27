#!/usr/bin/env python3
"""V241 two-tile route, mask and strict production-red controls."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np
from PIL import Image
import v241_rut_carver as m

WEST=[[1536,478],[1450,478],[1320,480],[1210,490],[1085,507],[980,515],
      [890,535],[784,551],[680,560],[570,540],[470,520],[370,522],[275,550]]
SOUTH=[[466,0],[466,74],[470,160],[488,235],[540,310],[620,350],
       [700,400],[805,442],[930,510],[1050,550],[1140,585],[1270,605]]

def test():
    image=Image.new('RGB',m.SIZE,(95,150,70))
    roads=m.read_roads(Path(__file__).resolve().parents[1]/'terrain-grid/v123-atlas.js')
    assert roads=={'west':WEST,'south':SOUTH},'V123 route drift'
    for tile,road in roads.items():
        out,mask,r=m.carve(image,road)
        pixels=np.asarray(out);before=np.asarray(image)
        assert np.any(pixels!=before),tile
        assert r['pixelsModifiedOutside22px']==0,r
        assert not r['productionApproved'] and not r['humanVisualApproval']
        assert not r['bridgeBanksVerified'] and not r['historicalRoadsVerified']
        signed,arc,dist=m.route_coordinates(road)
        row=np.asarray(mask)
        yy,xx=np.indices(dist.shape)
        samples=np.argwhere((dist<.75)&(xx>400)&(xx<1000))
        assert len(samples)>0
        cy,cx=samples[len(samples)//2]
        rr=row[max(0,cy-12):cy+13,max(0,cx-12):cx+13]
        assert rr.max()>180 and rr.min()<40
    try:m.carve(Image.new('RGB',(800,600)),WEST)
    except ValueError:pass
    else:raise AssertionError('wrong size accepted')
    try:m.carve(image,[[0,0]])
    except ValueError:pass
    else:raise AssertionError('incomplete graph accepted')
    print('PASS V241 both V123 routes, dual rut/grass median, no off-corridor changes, negative controls; production RED')
if __name__=='__main__':test()
