#!/usr/bin/env python3
"""Fail-closed synthetic and pixel-integrity tests for V198 SOURCE quarantine."""
import copy
import json
import tempfile
from pathlib import Path
from PIL import Image
import v197_highres_material_samples as v197
import v198_period_exclusion_masks as v198

count = 0

def check(label, test):
    global count
    test()
    count += 1
    print("PASS", label)

def reject(action):
    try:
        action()
    except (ValueError, KeyError, FileNotFoundError):
        return
    raise AssertionError("forged SOURCE evidence was accepted")

def fixture(root):
    source = root / "source"
    source.mkdir()
    m = v197.plan()
    for i, sample in enumerate(m["samples"]):
        for j, tile in enumerate(sample["tiles"]):
            path = source / tile["name"]
            Image.new("RGB", (256, 256),
                      (40 + i * 50 + j * 2, 75 + j * 15, 30 + i * 20)
                      ).save(path, format="JPEG")
            tile["sha256"] = v197.sha(path)
            tile["byteCount"] = path.stat().st_size
    v197.produce(m, source)
    return source, root / "out"

def bounds_and_review():
    assert v198.validate_annotations()
    for name in v198.ANNOTATIONS:
        mask = v198.exclusion_mask(name)
        assert mask.size == (512, 512)
        assert 100 < mask.tobytes().count(255) < 512 * 512 * 0.12
        assert mask.tobytes().count(0) + mask.tobytes().count(255) == 512 * 512
    assert v198.exclusion_mask("western_forest_reference").getpixel((10, 30)) == 255
    assert v198.exclusion_mask("eastern_ridge_reference").getpixel((250, 158)) == 255
    assert v198.exclusion_mask("southern_forest_reference").getpixel((195, 325)) == 255
    assert v198.exclusion_mask("western_forest_reference").getpixel((393, 500)) == 255
    assert v198.exclusion_mask("southern_forest_reference").getpixel((362, 451)) == 255
    assert v198.exclusion_mask("southern_forest_reference").getpixel((40, 100)) == 0

def source_pixels_unchanged():
    with tempfile.TemporaryDirectory() as d:
        source, output = fixture(Path(d))
        manifest = v198.produce(source, output)
        assert v198.verify(source, output)
        assert manifest["requiredAttribution"] == "Datenquelle: basemap.at"
        assert all(manifest[k] is False for k in v198.FALSE_FLAGS)
        assert manifest["unreviewedModernFeaturesRemain"] is True
        for sample in manifest["samples"]:
            with Image.open(source / (sample["name"] + ".png")) as raw, Image.open(
                    output / sample["quarantinedImage"]) as masked:
                assert masked.mode == "RGBA"
                assert raw.convert("RGB").tobytes() == masked.convert("RGB").tobytes()
                assert masked.getchannel("A").getextrema() == (0, 255)
            assert sample["eligibleForGameArt"] is False

def forged_approval():
    with tempfile.TemporaryDirectory() as d:
        source, output = fixture(Path(d))
        v198.produce(source, output)
        path = output / "manifest.json"
        m = json.loads(path.read_text())
        m["periodSafe"] = True
        path.write_text(json.dumps(m))
        reject(lambda: v198.verify(source, output))

def forged_annotations():
    with tempfile.TemporaryDirectory() as d:
        source, output = fixture(Path(d))
        v198.produce(source, output)
        path = output / "manifest.json"
        m = json.loads(path.read_text())
        m["annotations"]["southern_forest_reference"].pop()
        path.write_text(json.dumps(m))
        reject(lambda: v198.verify(source, output))

def forged_source():
    with tempfile.TemporaryDirectory() as d:
        source, output = fixture(Path(d))
        v198.produce(source, output)
        with Image.open(source / "southern_forest_reference.png") as im:
            changed = im.copy()
        changed.putpixel((200, 200), (255, 0, 0))
        changed.save(source / "southern_forest_reference.png")
        reject(lambda: v198.verify(source, output))

def forged_transparency():
    with tempfile.TemporaryDirectory() as d:
        source, output = fixture(Path(d))
        m = v198.produce(source, output)
        path = output / m["samples"][0]["quarantinedImage"]
        with Image.open(path) as im:
            changed = im.copy()
        changed.putpixel((10, 30), (0, 0, 0, 255))
        changed.save(path)
        reject(lambda: v198.verify(source, output))

def forged_mask():
    with tempfile.TemporaryDirectory() as d:
        source, output = fixture(Path(d))
        m = v198.produce(source, output)
        path = output / m["samples"][1]["maskImage"]
        with Image.open(path) as im:
            changed = im.copy()
        changed.putpixel((250, 158), 0)
        changed.save(path)
        reject(lambda: v198.verify(source, output))

def forged_contact():
    with tempfile.TemporaryDirectory() as d:
        source, output = fixture(Path(d))
        v198.produce(source, output)
        path = output / "v198-exclusion-review-contact.png"
        with Image.open(path) as im:
            changed = im.copy()
        changed.putpixel((100, 100), (255, 255, 255))
        changed.save(path)
        reject(lambda: v198.verify(source, output))

def no_mass_blanket():
    bad = copy.deepcopy(v198.ANNOTATIONS)
    try:
        v198.ANNOTATIONS["eastern_ridge_reference"].append(
            {"kind": "unverified_track", "polygon":
             [[0, 0], [512, 0], [512, 512], [0, 512]]})
        reject(lambda: v198.exclusion_mask("eastern_ridge_reference"))
    finally:
        v198.ANNOTATIONS.clear()
        v198.ANNOTATIONS.update(bad)

for label, fn in (
    ("manual source annotations bounded and binary", bounds_and_review),
    ("original RGB pixels and attribution preserved", source_pixels_unchanged),
    ("fake period approval rejected", forged_approval),
    ("fake annotation removal rejected", forged_annotations),
    ("altered original source rejected", forged_source),
    ("unmasked date stamp rejected", forged_transparency),
    ("altered mask rejected", forged_mask),
    ("altered review contact rejected", forged_contact),
    ("mass-blanketing source rejected", no_mass_blanket),
):
    check(label, fn)
print(f"V198 {count} synthetic fail-closed tests PASS; GAME visual approval not tested")
