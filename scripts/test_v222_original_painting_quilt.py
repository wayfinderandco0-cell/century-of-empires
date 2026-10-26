#!/usr/bin/env python3
"""V222 fail-closed provenance and negative controls, after building source art."""
import json
import shutil
import tempfile
from pathlib import Path
import v222_original_painting_quilt as quilt

def rejects(folder,change):
    m=json.loads((folder/'manifest.json').read_text())
    change(m)
    (folder/'manifest.json').write_text(json.dumps(m))
    try:
        quilt.verify(folder)
    except (ValueError,KeyError,AssertionError):
        return
    raise AssertionError('V222 accepted a false art/provenance claim')

def main():
    root=quilt.OUT
    assert quilt.verify(root)
    with tempfile.TemporaryDirectory() as tmp:
        dest=Path(tmp)
        for file in root.iterdir():
            if file.is_file():shutil.copy2(file,dest/file.name)
        rejects(dest,lambda m:m.update(gameArtApproved=True))
        shutil.copy2(root/'manifest.json',dest/'manifest.json')
        rejects(dest,lambda m:m.update(sourceRegisteredToV123=True))
        shutil.copy2(root/'manifest.json',dest/'manifest.json')
        rejects(dest,lambda m:m.update(noModernOrthophotoUsed=False))
        shutil.copy2(root/'manifest.json',dest/'manifest.json')
        rejects(dest,lambda m:m['cells'][1]['patches'][0].update(
            source=m['cells'][0]['patches'][0]['source']))
        shutil.copy2(root/'manifest.json',dest/'manifest.json')
        rejects(dest,lambda m:m['cells'][0].update(sha256='0'*64))
    print('V222 provenance + tamper + false approval negative tests PASS; user art approval FALSE')
if __name__=='__main__':main()
