#!/usr/bin/env python3
"""EAST-01 V9: local road-edge continuity correction of the V8 original-art scene.

Works on the existing authored V4 east landscape and registered Matrei V121.
Does NOT copy/mirror whole landscapes, change protected art, create new roads,
or certify historical/physical terrain. The correction is restricted to a
narrow, naturally feathered strip at the proposed Matrei/EAST cartway port.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import v267_east01_cartway_v8 as v8
from v267_east01_riparian_v4 import registered_matrei

DIR, MAT, EAST, W, H = v8.DIR, v8.MAT, v8.EAST, v8.W, v8.H
PORT_Y = 749
ROAD_BAND = 24
BLEND_X = 192

def smoothstep(a):
    a = np.clip(a, 0.0, 1.0)
    return a * a * (3.0 - 2.0 * a)

def seam_metrics(left, right):
    # Compare displayed Matrei's rightmost column to EAST's leftmost column.
    lo, hi = PORT_Y - ROAD_BAND, PORT_Y + ROAD_BAND + 1
    d = np.abs(left[lo:hi, -1, :].astype(np.float32) -
               right[lo:hi, 0, :].astype(np.float32))
    return {"meanAbsRgb": round(float(d.mean()), 3),
            "p95AbsRgb": round(float(np.percentile(d, 95)), 3),
            "maxAbsRgb": int(d.max())}

def main():
    protected = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (MAT, EAST)}
    with Image.open(MAT) as source, Image.open(EAST) as ridge:
        if source.size != (W, H) or ridge.size != (W, H):
            raise RuntimeError("1536x1024 V267 source required")
        matrei = Image.fromarray(registered_matrei(source.convert("RGB")), "RGB")
        east_v8, _, east_road = v8.compose(ridge, matrei, W)
        mat_reworked, mat_mask, _ = v8.compose(matrei, matrei, 0)

    mat_np = np.asarray(matrei, dtype=np.float32)
    left_np = np.asarray(mat_reworked, dtype=np.float32)
    alpha = np.clip(mat_mask, 0, 1)
    alpha[:, :1351] = 0
    displayed = np.clip(mat_np * (1-alpha[:, :, None]) +
                        left_np * alpha[:, :, None], 0, 255).astype(np.uint8)
    east = np.asarray(east_v8, dtype=np.float32).copy()
    before = seam_metrics(displayed, np.uint8(np.clip(east, 0, 255)))

    # Preserve exact centerline dirt pixels at the shared port, then taper
    # the low-frequency lighting difference over 192px. A small high-frequency
    # component fades within 16px to prevent a harsh vertical copy boundary.
    delta = displayed[:, -1, :].astype(np.float32) - east[:, 0, :]
    kernel = np.exp(-0.5 * (np.arange(-14, 15, dtype=np.float32) / 5.5)**2)
    kernel /= kernel.sum()
    low = np.stack([np.convolve(delta[:, k], kernel, mode="same")
                    for k in range(3)], axis=1)
    high = delta - low
    xs = np.arange(BLEND_X, dtype=np.float32)
    wide = smoothstep((BLEND_X - xs) / BLEND_X)
    short = smoothstep((16 - xs) / 16)
    ys = np.abs(np.arange(H, dtype=np.float32) - PORT_Y)
    band = smoothstep((85 - ys) / 49)
    correction = (low[:, None, :] * wide[None, :, None] +
                  high[:, None, :] * short[None, :, None])
    east[:, :BLEND_X, :] += correction * band[:, None, None]
    corrected = np.uint8(np.clip(east, 0, 255))
    after_raw = seam_metrics(displayed, corrected)
    if after_raw["meanAbsRgb"] > 1.0:
        raise RuntimeError("Shared road-port source pixels are not paired")
    if before["meanAbsRgb"] < 0.1:
        raise RuntimeError("No seam defect to correct: source unexpectedly changed")

    out = DIR / "matrei-east-riparian-v9-seam-conditioned.webp"
    contact = DIR / "matrei-east-v9-seam-conditioned-contact.webp"
    evidence = DIR / "matrei-east-v9-seam-conditioned-evidence.json"
    Image.fromarray(corrected, "RGB").save(out, "WEBP", quality=96, method=6)
    with Image.open(out) as encoded:
        after_encoded = seam_metrics(displayed, np.asarray(encoded.convert("RGB")))
    # Lossy WebP cannot guarantee exact pixel identity after encoding.
    if after_encoded["meanAbsRgb"] >= before["meanAbsRgb"]:
        raise RuntimeError("Encoded EAST road seam failed to improve")

    board = Image.new("RGB", (2*W, H), (17, 30, 23))
    board.paste(Image.fromarray(displayed, "RGB"), (0, 0))
    board.paste(Image.open(out).convert("RGB"), (W, 0))
    ImageDraw.Draw(board).line([(W, 256), (W, 768)],
                               fill=(219, 174, 100), width=2)
    board.save(contact, "WEBP", quality=92, method=6)

    for p in (MAT, EAST):
        if hashlib.sha256(p.read_bytes()).hexdigest() != protected[p.name]:
            raise RuntimeError("Protected source modified")
    data = {
        "schema": "coe-v267-east-v9-local-road-seam/v1",
        "art": out.name, "comparison": contact.name,
        "matreiOverlay": "matrei-east-v8-matrei-display-overlay.png",
        "sourceOriginal": EAST.name,
        "sourceMatrei": MAT.name,
        "candidateSha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "protectedSourceHashes": protected,
        "roadWorldPoints": v8.v7.ROUTE,
        "roadPort": {"matrei": [1536, PORT_Y], "east": [0, PORT_Y],
                     "geometryPaired": True},
        "sourceSeamBefore": before, "sourceSeamAfter": after_raw,
        "decodedWebpSeamAfter": after_encoded,
        "seamMeasuredBandPx": ROAD_BAND,
        "seamBlendWidthPx": BLEND_X,
        "roadPortPixelContinuityImproved": True,
        "physicalRoadSeamVerified": False,
        "physicalTerrainSeamVerified": False,
        "riverSeamVerified": False,
        "visualQualityApproved": False,
        "historicallyVerified": False,
        "mobileWebkitRendered": False,
        "nativePlayable": False,
        "userApproved": False,
        "finished": False,
        "notes": "V9 is a local seam-corrected revision of one EAST-01 candidate, NOT a new cell or a certified route."
    }
    evidence.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({"art": str(out), "bytes": out.stat().st_size,
                      "roadSeamBefore": before, "roadSeamAfter": after_encoded,
                      "protectedSourcesUnchanged": True, "newFinished": 0}))

if __name__ == "__main__":
    main()
