#!/usr/bin/env python3
"""Offline synthetic V158 palette/alpha/provenance regression; no road claims."""
import copy
import json
import tempfile
from pathlib import Path
from PIL import Image
from v158_period_material_study import (
    SIZE, SECTORS, ATTRIBUTION, NOT_APPROVED, digest, retained_fractions,
    produce, verify_study, validate_source)

negative = 0
def reject(fn, label):
    global negative
    try:
        fn()
    except (ValueError, TypeError, KeyError, FileNotFoundError, OSError):
        negative += 1
    else:
        raise AssertionError("Fail-closed check accepted: " + label)

with tempfile.TemporaryDirectory() as t:
    root = Path(t); source = root/"v157"; output = root/"v158"; source.mkdir()
    mask = Image.new("L", SIZE, 255)
    # Distinct unknown areas in all three sectors, including sector borders.
    from PIL import ImageDraw
    d = ImageDraw.Draw(mask)
    for i in range(3):
        d.rectangle((i*768+40, 80, i*768+280, 380), fill=0)
    d.rectangle((750, 600, 785, 740), fill=0)
    d.rectangle((1520, 610, 1540, 730), fill=0)
    rgba = Image.new("RGBA", SIZE, (0, 0, 0, 255))
    for i, rgb in enumerate(((68, 121, 51), (101, 140, 72), (150, 117, 78))):
        ImageDraw.Draw(rgba).rectangle((i*768, 0, (i+1)*768-1, 767), fill=(*rgb,255))
    rgba.putalpha(mask)
    mask.save(source/"residual-modern-mask.png")
    rgba.save(source/"residual-modern-reference.png")
    m = {
        "version":157,"sourceVersion":156,"pixelDimensions":list(SIZE),
        "sourceCrs":"EPSG:3857","requiredAttribution":ATTRIBUTION,
        "license":"CC BY 4.0", "sourceMosaicSha256":"a"*64,
        "maskFile":"residual-modern-mask.png",
        "referenceFile":"residual-modern-reference.png",
        "maskSha256":digest(source/"residual-modern-mask.png"),
        "referenceSha256":digest(source/"residual-modern-reference.png"),
        "exclusionAlphaMeaning":"0=excluded/unknown; 255=unreviewed modern source",
        "sourceSectorRetainedFractions":retained_fractions(mask), **NOT_APPROVED,
    }
    (source/"manifest.json").write_text(json.dumps(m))
    assert validate_source(source)[0] == m
    report = produce(source, output)
    assert verify_study(source, output)
    assert report["sourceSectorsAreNotGameOctagons"] is True
    assert report["sourceMayContainModernFeatures"] is True
    assert report["productionApproved"] is False
    assert report["periodArtComplete"] is False
    assert report["gameRouteGeoregistered"] is False
    assert report["sourceSectorRetainedFractions"] == m["sourceSectorRetainedFractions"]
    with Image.open(output/report["studyFile"]) as image:
        assert image.getchannel("A").tobytes() == mask.tobytes()
        assert image.getpixel((90,100))[3] == 0
        assert image.getpixel((400,400))[3] == 255
        assert image.getpixel((400,400))[:3] != rgba.getpixel((400,400))[:3]
    # Synthetic three sectors must remain distinct; no copied source tile.
    with Image.open(output/report["sectorFiles"][SECTORS[0]]) as a:
        with Image.open(output/report["sectorFiles"][SECTORS[1]]) as b:
            assert a.tobytes() != b.tobytes()

    def bad_source(key, value):
        wrong = copy.deepcopy(m); wrong[key] = value
        (source/"manifest.json").write_text(json.dumps(wrong))
        reject(lambda:validate_source(source),"forged source " + key)
        (source/"manifest.json").write_text(json.dumps(m))
    for key in ("productionApproved","historic1780Certified","gameRouteGeoregistered",
                "bridgeBanksVerified","modernInfrastructureCleared","periodArtComplete"):
        bad_source(key, True)
    bad_source("sourceCrs", "EPSG:4326")
    bad_source("sourceMosaicSha256", "not-a-hash")
    bad_source("sourceSectorRetainedFractions", {k:0.9 for k in SECTORS})
    bad_source("maskFile", "../wrong.png")

    original = (source/m["maskFile"]).read_bytes()
    (source/m["maskFile"]).write_bytes(b"tampered")
    reject(lambda:validate_source(source),"modified source mask")
    (source/m["maskFile"]).write_bytes(original)

    original = (source/m["referenceFile"]).read_bytes()
    (source/m["referenceFile"]).write_bytes(b"tampered")
    reject(lambda:validate_source(source),"modified source reference")
    (source/m["referenceFile"]).write_bytes(original)

    for key in ("productionApproved","periodArtComplete","gameRouteGeoregistered",
                "modernInfrastructureCleared","sourceSectorsAreNotGameOctagons"):
        wrong = copy.deepcopy(report);wrong[key] = not report[key]
        (output/"manifest.json").write_text(json.dumps(wrong))
        reject(lambda:verify_study(source,output),"forged output " + key)
    (output/"manifest.json").write_text(json.dumps(report))

    wrong = copy.deepcopy(report);wrong["inventedRoad"] = [[0,0],[100,100]]
    (output/"manifest.json").write_text(json.dumps(wrong))
    reject(lambda:verify_study(source,output),"invented road field")
    (output/"manifest.json").write_text(json.dumps(report))

    for name in (report["studyFile"],*report["sectorFiles"].values()):
        path=output/name;original=path.read_bytes()
        path.write_bytes(b"corrupted")
        reject(lambda:verify_study(source,output),"tampered image "+name)
        path.write_bytes(original)
    assert verify_study(source,output)

print(f"V158 PASS: 3 nonrepeated source sectors, unknown alpha preserved, {negative} fail-closed tamper cases; NOT game art")
