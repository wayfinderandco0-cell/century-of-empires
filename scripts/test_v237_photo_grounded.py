#!/usr/bin/env python3
"""V237 synthetic crop/provenance/road invariance controls, no network."""
import hashlib
import sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
import v237_build_photo_grounded as v237
import v232_route_ground_preflight as v232

roads=v232.source_roads()
assert roads['west'][0]==[1536,478] and roads['south'][-1]==[1270,605]
assert v237.SOURCES['west']['sha1']!=v237.SOURCES['south']['sha1']
assert all(x['page'].startswith('https://commons.wikimedia.org/wiki/File:')
           for x in v237.SOURCES.values())
# Uniform synthetic pasture is a valid fixture for native-crop mechanics,
# NOT photographic/historical approval.
rgb=np.zeros((1200,1900,3),dtype=np.uint8)
rgb[:]=[120,146,53]
img=Image.fromarray(rgb)
crop,box,score=v237.candidate_crop(img,roads['west'],[0,0,1536,1024])
assert crop.size==(1536,1024) and box==[0,0,1536,1024]
assert np.array_equal(np.asarray(crop),rgb[:1024,:1536])
assert v237.FALSE['productionApproved'] is False
assert v237.FALSE['sourceRegisteredToV123'] is False
assert v237.FALSE['humanVisualApproval'] is False
try:
 v237.candidate_crop(img,roads['west'],[0,0,1500,1024])
 raise AssertionError('Bad native crop was accepted')
except ValueError:pass
assert len(v232.sample_polyline(roads['south']))>100
print('V237 PASS: native pixels, two distinct pinned CC0 sources, exact V123 routes, negative controls')
