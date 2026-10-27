#!/usr/bin/env python3
"""Fetch only V231's two SHA1-pinned CC0 Austrian photographs, unmodified."""
import hashlib,json,sys,time
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image
from build_v231_cc0_oblique_art import SOURCES,LICENSE,LICENSE_URL

def main():
    output=Path(sys.argv[1] if len(sys.argv)>1 else "terrain-v234/originals")
    output.mkdir(parents=True,exist_ok=True)
    manifest={}
    for tile,info in SOURCES.items():
        for delay in (0,20,50):
            if delay:time.sleep(delay)
            r=requests.get(info["url"],timeout=100,headers={
                "User-Agent":"CenturyOfEmpires/0.2 (CC0 source QA; GitHub issue 9)"})
            if r.status_code==429:continue
            r.raise_for_status();break
        else:raise RuntimeError("Source unavailable: "+tile)
        raw=r.content
        if hashlib.sha1(raw).hexdigest()!=info["sourceSha1"]:
            raise ValueError("STOP: CC0 original SHA1 mismatch "+tile)
        with Image.open(BytesIO(raw)) as im:
            if list(im.size)!=info["dimensions"]:
                raise ValueError("STOP: source dimensions changed "+tile)
        (output/(tile+".jpg")).write_bytes(raw)
        manifest[tile]={"sha256":hashlib.sha256(raw).hexdigest(),
                        "sha1":info["sourceSha1"],"author":info["author"],
                        "license":LICENSE,"licenseUrl":LICENSE_URL,
                        "sourcePage":"https://commons.wikimedia.org/wiki/File:"+info["title"].replace(" ","_"),
                        "sourceUrl":info["url"],"dimensions":info["dimensions"],
                        "geographicallyRegisteredToV123":False,
                        "historical1780RoadVerified":False}
    (output/"source-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
