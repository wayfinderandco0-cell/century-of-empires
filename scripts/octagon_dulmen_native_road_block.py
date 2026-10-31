#!/usr/bin/env python3
"""Eight native photographic German lowland cells with a REAL photographed farm road.

Modern 2025 road is visual source material, not evidence of an 1780-1880
road, game graph, or province. No synthetic road painting, mirroring or warps.
"""
from __future__ import annotations
from io import BytesIO
import hashlib, html, json, re, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'terrain-grid/factory-photo/dulmen-road-8'
TITLE='Dülmen, Kirchspiel, Dernekamp, Feldweg -- 2025 -- 0161.jpg'
W,H,X0,Y0=1536,1024,7,8
CROP_X,CROP_Y=960,2800
AGENT='CenturyOfEmpiresArtFactory/1.0 (educational game; Wikimedia attribution)'
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=130) as r:return r.read()
        except Exception:
            if attempt==2:raise
            time.sleep(4*(attempt+1))
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    params=urllib.parse.urlencode({'action':'query','format':'json','prop':'imageinfo',
                                    'titles':'File:'+TITLE,'iiprop':'url|size|extmetadata'})
    pages=json.loads(get('https://commons.wikimedia.org/w/api.php?'+params))['query']['pages']
    info=next(iter(pages.values()))['imageinfo'][0]
    license_name=html.unescape(re.sub('<[^>]+>','',info['extmetadata']['LicenseShortName']['value'])).strip()
    if license_name!='CC BY-SA 4.0':raise RuntimeError('Unexpected license: '+license_name)
    raw=get(info['url'])
    source=Image.open(BytesIO(raw)).convert('RGB')
    if source.size!=(8064,6048):raise RuntimeError('Original dimensions changed')
    if CROP_X+4*W>source.width or CROP_Y+2*H>source.height:
        raise RuntimeError('Native crop would require scaling')
    photo=source.crop((CROP_X,CROP_Y,CROP_X+4*W,CROP_Y+2*H))
    # Grade the whole image once; NEVER warp trees or independently retouch edges.
    photo=ImageEnhance.Color(photo).enhance(.78)
    photo=ImageEnhance.Contrast(photo).enhance(1.03)
    photo=ImageEnhance.Brightness(photo).enhance(.94)
    source_sha=sha(raw)
    cells=[]
    for row in range(2):
        for col in range(4):
            x,y=X0+col,Y0+row
            name=f'eu-{x:02d}-{y:02d}'
            tile=photo.crop((col*W,row*H,(col+1)*W,(row+1)*H))
            path=OUT/(name+'.webp')
            tile.save(path,'WEBP',quality=93,method=6)
            crop=[CROP_X+col*W,CROP_Y+row*H,CROP_X+(col+1)*W,CROP_Y+(row+1)*H]
            cells.append({
                'id':name,'grid':[x,y],'origin':[x*W,y*H],
                'image':path.relative_to(ROOT).as_posix(),'imageSize':[W,H],
                'originalSource':info['url'],
                'sourcePage':'https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(TITLE.replace(' ','_')),
                'author':'Dietmar Rabich','license':'CC BY-SA 4.0',
                'licenseUrl':'https://creativecommons.org/licenses/by-sa/4.0/',
                'sourceCrop':crop,'sourceSha256':source_sha,'outputSha256':sha(path.read_bytes()),
                'nativePhotoSourceGroup':'dulmen-germany-drone-original-2025',
                'nativePhotoUnderlay':True,'unscaledOriginalPixelCrop':True,
                'sourceBackedPhotographicArtComposed':True,
                'sourceRegion':'Dülmen, Germany: modern 2025 image, NOT V94 cell georegistration',
                'motif':'European lowland fields, sparse trees and an actual photographed gravel farm road',
                'modernPhotographedRoadPresent':bool(row==0),
                'modernRoadQuarantined':True,'periodSafe':False,
                'exactPhotoGeoreferenced':False,'historicallyVerified':False,
                'artMethodApproved':False,'physicallyRoadSeamChecked':False,
                'gameplayEnabled':False,'visuallyReviewedOnPhone':False,
                'paintedRoads':[],'provinceIds':[],'strategicTowns':[],'scenicSettlements':[]
            })
    by={tuple(c['grid']):c for c in cells}
    joins=[]
    for c in cells:
        x,y=c['grid']
        for n in ((x+1,y),(x,y+1)):
            if n not in by:continue
            b=by[n];a_crop,b_crop=c['sourceCrop'],b['sourceCrop']
            horizontal=n[0]!=x
            exact=(a_crop[2]==b_crop[0] and a_crop[1]==b_crop[1] and a_crop[3]==b_crop[3]) if horizontal else (
                  a_crop[3]==b_crop[1] and a_crop[0]==b_crop[0] and a_crop[2]==b_crop[2])
            if not exact:raise RuntimeError('Source-pixel join mismatch')
            joins.append({'a':c['id'],'b':b['id'],'sourceNativePixelAdjacent':True,
                          'modernRoadMayCross':bool(horizontal and y==Y0),
                          'roadPainted':False,'routeEnabled':False,'visuallyApproved':False})
    if len(cells)!=8 or len(joins)!=10 or len({c['outputSha256'] for c in cells})!=8:
        raise RuntimeError('Eight unique source cells / ten native joins required')
    review=Image.new('RGB',(3072,1110),'#14261d')
    review.paste(photo.resize((3072,1024),Image.Resampling.LANCZOS),(0,0))
    d=ImageDraw.Draw(review)
    d.text((20,1036),'8 native 1536x1024 German lowland photos / 10 exact source-coordinate joins',fill='#f7e4c1')
    d.text((20,1061),'ACTUAL MODERN FARM ROAD, NOT a certified 1780 road; no movement or conquest',fill='#f7e4c1')
    d.text((20,1085),'Photo: Dietmar Rabich / Wikimedia Commons, CC BY-SA 4.0; color graded, no roads painted',fill='#f7e4c1')
    review.save(OUT/'photo-block-review.webp','WEBP',quality=91,method=6)
    manifest={
        'schema':'coe-photo-art/v1','status':'German-lowland-source-road-8-NOT-historical-NOT-playable',
        'fixedArtReference':'456107f28c8db1f87522bbc7511809b2a215f6fb',
        'studyGrid':[X0,Y0,4,2],'photographicArtComposed':8,
        'nativePhotoPixelJoins':joins,'unapprovedCrossSourceJoins':[],
        'visuallyChecked':0,'photographedModernRoadCandidateCells':4,
        'physicallyRoadConnected':0,'mobileRendered':0,
        'nativeGamePlayable':0,'historicallyVerified':0,'finishedToday':0,
        'geographyWarning':'Modern German lowland photo, NOT V94 cell placement; modern farm road cannot establish historical route.',
        'cells':cells}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'sourceBackedPhotoArt':8,'nativePhotoJoins':10,
                      'modernRoadCandidateCells':4,'approvedHistoricRoads':0,
                      'routable':0,'finishedToday':0}))
if __name__=='__main__':main()
