#!/usr/bin/env python3
"""EAST-01 V10: source-photo weathered cartway with paired Matrei display seam.

Only experimental candidate outputs are written. No V121/V123/V94 mutation.
The V267 three approved cells remain the protected reference. The candidate
road is fictional and disabled until its physical seam is reviewed.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import v267_east01_cartway_v8 as v8
import v267_east01_cartway_v7 as v7
from v267_east01_riparian_v4 import registered_matrei

DIR, MAT, EAST, W, H = v8.DIR, v8.MAT, v8.EAST, v8.W, v8.H
PORT_Y, BLEND_X, BAND = 749, 192, 24


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def weather(scene: Image.Image, original: Image.Image, offset: int) -> np.ndarray:
    """Break the bright raised-looking V8 strip into worn ground-level ruts.

    This changes material *inside* the already-cleared V8 corridor; it does
    not displace trees, move route vertices, or invent river crossings.
    """
    xx, yy, dist, signed, along = v7.geometry(offset)
    current = np.asarray(scene.convert("RGB"), dtype=np.float32)
    native = np.asarray(original.convert("RGB"), dtype=np.float32)
    road_width = 12.4 + 1.3 * np.sin(along / 44) + .6 * np.sin(along / 12)
    core = smooth((road_width + 2.5 - dist) / 4.5)
    shoulder = smooth((29 - dist) / 11) * (1 - core)
    # Native earth/vegetation breaks up an artificial shoulder edge.
    mix = shoulder * .13
    result = current * (1 - mix[:, :, None]) + native * mix[:, :, None]
    rut = np.exp(-.5 * ((np.abs(signed) - 6.0) / 2.8) ** 2)
    center = np.exp(-.5 * (signed / 4.2) ** 2)
    outer = np.exp(-.5 * ((dist - 14.5) / 4.0) ** 2)
    # World-locked pigment flecks, not a new drawn road or heightmesh.
    grit = 1.2 * np.sin((xx + offset) * .31 + yy * .19)
    grit += .8 * np.sin((xx + offset) * .13 - yy * .43)
    subtract = (6.8 * rut + 2.0 * center + 2.8 * outer) * core
    result -= subtract[:, :, None]
    result += (grit * core)[:, :, None]
    return np.uint8(np.clip(result, 0, 255))


def metrics(left: np.ndarray, right: np.ndarray) -> dict:
    d = np.abs(left[PORT_Y-BAND:PORT_Y+BAND+1, -1, :].astype(np.float32) -
               right[PORT_Y-BAND:PORT_Y+BAND+1, 0, :].astype(np.float32))
    return {"meanAbsRgb": round(float(d.mean()), 3),
            "p95AbsRgb": round(float(np.percentile(d, 95)), 3),
            "maxAbsRgb": int(d.max())}


def main():
    protected = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (MAT, EAST)}
    with Image.open(MAT) as raw, Image.open(EAST) as ridge:
        assert raw.size == ridge.size == (W, H)
        mat = Image.fromarray(registered_matrei(raw.convert("RGB")), "RGB")
        east_base, _, _ = v8.compose(ridge, mat, W)
        mat_base, mat_mask, _ = v8.compose(mat, mat, 0)
        east = weather(east_base, ridge, W).astype(np.float32)
        left = weather(mat_base, mat, 0)

    original_mat = np.asarray(mat, dtype=np.float32)
    alpha = np.clip(mat_mask, 0, 1)
    alpha[:, :1351] = 0
    displayed = np.uint8(np.clip(original_mat * (1-alpha[:, :, None]) +
                                 left.astype(np.float32) * alpha[:, :, None], 0, 255))
    before = metrics(displayed, east.astype(np.uint8))

    # Register the right-hand candidate to the *actual* displayed Matrei
    # pixels at the same 749px road port, tapering into original EAST terrain.
    delta = displayed[:, -1, :].astype(np.float32) - east[:, 0, :]
    kernel = np.exp(-.5 * (np.arange(-14, 15, dtype=np.float32) / 5.5) ** 2)
    kernel /= kernel.sum()
    low = np.stack([np.convolve(delta[:, k], kernel, mode="same")
                    for k in range(3)], axis=1)
    high = delta - low
    xs = np.arange(BLEND_X, dtype=np.float32)
    wide = smooth((BLEND_X-xs) / BLEND_X)
    short = smooth((16-xs) / 16)
    ys = np.abs(np.arange(H, dtype=np.float32) - PORT_Y)
    band = smooth((85-ys) / 49)
    correction = (low[:, None, :] * wide[None, :, None] +
                  high[:, None, :] * short[None, :, None])
    east[:, :BLEND_X, :] += correction * band[:, None, None]
    final_east = np.uint8(np.clip(east, 0, 255))
    assert metrics(displayed, final_east)["meanAbsRgb"] < 1.0
    assert before["meanAbsRgb"] > 0.1

    art = DIR / "matrei-east-riparian-v10-ground-ruts.webp"
    overlay_path = DIR / "matrei-east-v10-matrei-display-overlay.png"
    contact = DIR / "matrei-east-v10-ground-ruts-contact.webp"
    evidence = DIR / "matrei-east-v10-ground-ruts-evidence.json"
    Image.fromarray(final_east, "RGB").save(art, "WEBP", quality=96, method=6)
    overlay = Image.fromarray(np.dstack((left, np.uint8(alpha*255))), "RGBA")
    overlay.save(overlay_path, "PNG", optimize=True)
    with Image.open(art) as decoded:
        after = metrics(displayed, np.asarray(decoded.convert("RGB")))
    if after["meanAbsRgb"] >= before["meanAbsRgb"]:
        raise RuntimeError("Decoded road-port seam did not improve")
    board = Image.new("RGB", (W*2, H), (17, 30, 23))
    board.paste(Image.fromarray(displayed, "RGB"), (0, 0))
    board.paste(Image.open(art).convert("RGB"), (W, 0))
    ImageDraw.Draw(board).line([(W, 256), (W, 768)],
                               fill=(219, 174, 100), width=2)
    board.save(contact, "WEBP", quality=92, method=6)
    for p in (MAT, EAST):
        if hashlib.sha256(p.read_bytes()).hexdigest() != protected[p.name]:
            raise RuntimeError("Protected source was changed")
    result = {
        "schema": "coe-v267-east-v10-source-ground-ruts/v1",
        "art": art.name, "matreiOverlay": overlay_path.name,
        "comparison": contact.name,
        "candidateSha256": hashlib.sha256(art.read_bytes()).hexdigest(),
        "protectedSourceHashes": protected,
        "sourceOriginal": EAST.name,
        "roadWorldPoints": v7.ROUTE,
        "roadPort": {"matrei": [1536, PORT_Y], "east": [0, PORT_Y],
                     "geometryPaired": True},
        "sourceSeamBefore": before, "decodedWebpSeamAfter": after,
        "sourceMaterial": "registered V121 Matrei road + original V4 EAST-01",
        "rutPigmentWeathering": True,
        "physicalRoadSeamVerified": False,
        "physicalTerrainSeamVerified": False,
        "riverSeamVerified": False,
        "visualQualityApproved": False,
        "historicallyVerified": False,
        "mobileWebkitRendered": False,
        "nativePlayable": False, "userApproved": False, "finished": False,
        "notes": "V10 improves ground contact pigment, not road geometry. Preview only."
    }
    evidence.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"art": str(art), "bytes": art.stat().st_size,
                      "seamBefore": before, "seamAfter": after,
                      "protectedSourcesUnchanged": True, "finished": 0}))


if __name__ == "__main__":
    main()
