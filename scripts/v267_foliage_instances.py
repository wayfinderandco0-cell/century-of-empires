#!/usr/bin/env python3
"""World-anchored, instanced 3D foliage for the V267 terrain study.

Reads the exact exported ground-art heightfield. Produces original conifer and
broadleaf 3D tree *instances*, not aerial crops or duplicated image sprites.
Modern V94 vegetation is an approximate density cue, NOT 1780 forest evidence.
No roads, provinces, conquest targets, or historical claims are created.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.spatial import cKDTree
from v267_native_relief_pilot import road_centerlines, TW, TH, COLS, ROWS, C0, R0

STEP = 16
SEED = 2671031
W, H = TW * COLS, TH * ROWS


def build(root: Path, out: Path):
    source = out / "heightfield-step16.npy"
    art = json.loads((out / "manifest.json").read_text())
    mesh = json.loads((out / "heightmesh-manifest.json").read_text())
    field = np.load(source, allow_pickle=False)
    assert field.shape == (H // STEP + 1, W // STEP + 1)
    assert field.dtype == np.float32 and np.isfinite(field).all()
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    assert source_sha == art["meshSourceHeightfieldSha256"] == mesh["paintedHeightfieldSha256"]
    assert art["visuallyApprovedV267"] is False and mesh["finishedToday"] == 0

    dem = json.loads((root / "terrain-v94/heights.json").read_text())
    woods = json.loads((root / "terrain-v94/woods.json").read_text())
    elev = np.asarray(dem["heights"], dtype=np.float32).reshape(384, 512)
    forest = np.asarray(woods["forest"], dtype=np.float32).reshape(384, 512)
    rng = np.random.default_rng(SEED)
    # Generate ONCE in global world space. No per-octagon random resets or
    # cloned vegetation. Neighbor boundaries cannot duplicate a tree.
    xx, yy = np.meshgrid(np.arange(21, W, 34), np.arange(21, H, 34))
    # Quantize coordinates BEFORE ground sampling. Otherwise float64 jitter
    # is rounded to float32 only when packed, moving steep-slope tree roots.
    x = np.clip(xx.ravel().astype(np.float32) + rng.uniform(-10, 10, xx.size), 1, W - 2).astype(np.float32)
    y = np.clip(yy.ravel().astype(np.float32) + rng.uniform(-10, 10, yy.size), 1, H - 2).astype(np.float32)
    gx = (C0 + x / TW) * 512 / 18
    gy = (R0 + y / TH) * 384 / 24
    e = map_coordinates(elev, [gy, gx], order=1, mode="nearest")
    f = map_coordinates(forest, [gy, gx], order=1, mode="nearest")
    roads = road_centerlines(W, H, 1)
    road_points = np.concatenate(roads, axis=0)
    distance = cKDTree(road_points).query(np.column_stack((x, y)), workers=1)[0]
    keep = (f > 0.28) & (e < 1900) & (distance > 27)
    keep &= rng.random(x.size) < np.clip((f - .20) * 1.15, 0, .80)
    x, y, e, f, distance = (v[keep] for v in (x, y, e, f, distance))
    ground = map_coordinates(field, [y / STEP, x / STEP], order=1, mode="nearest")
    kind = ((e > 750) | (rng.random(x.size) < .72)).astype(np.int32)
    radius = np.where(kind == 1, rng.uniform(6.0, 10.5, x.size),
                      rng.uniform(8.0, 13.5, x.size))
    height = np.where(kind == 1, rng.uniform(23, 41, x.size),
                      rng.uniform(17, 29, x.size))
    hue = np.clip(.70 + .22 * (f - .5) + rng.uniform(-.11, .11, x.size), .45, 1.0)
    seed = rng.random(x.size)
    # Two vec4 attributes per instance: [x,ground,-y,radius] and
    # [height,hue,kind,seed]. The viewer uses one GPU instanced draw per kind.
    data = np.column_stack((x, ground, -y, radius, height, hue, kind, seed)).astype("<f4")
    # Partition instances by species AND world cell. At close zoom the iPhone
    # can draw only the visible cells, rather than all 7,819 trees every frame.
    # Global x/z positions are never changed: neighboring cell roots stay exact.
    groups, cell_batches, packed = [], [], []
    offset = 0
    cell_col = np.minimum((x // TW).astype(np.int32), COLS - 1)
    cell_row = np.minimum((y // TH).astype(np.int32), ROWS - 1)
    for k, name in ((1, "conifer"), (0, "broadleaf")):
        group_offset, group_count = offset, 0
        for row in range(ROWS):
            for col in range(COLS):
                subset = data[(kind == k) & (cell_col == col) & (cell_row == row)].copy()
                rng.shuffle(subset, axis=0)  # spatially uniform per-cell LOD
                count = int(len(subset))
                cell_batches.append({
                    "kind": name, "kindCode": k, "col": col, "row": row,
                    "offsetFloats": offset, "count": count,
                    "worldBounds": [col * TW, row * TH, (col + 1) * TW, (row + 1) * TH]
                })
                packed.append(subset)
                offset += subset.size
                group_count += count
        groups.append({"kind": name, "kindCode": k,
                       "offsetFloats": group_offset, "count": group_count})
    result = np.concatenate(packed, axis=0)
    assert len(cell_batches) == COLS * ROWS * 2
    assert sum(b["count"] for b in cell_batches) == len(result)
    assert offset == result.size
    assert np.isfinite(result).all() and len(result) > 0
    assert float(distance.min()) > 27
    binary = out / "foliage-instances.bin"
    binary.write_bytes(result.tobytes(order="C"))
    manifest = {
        "schema": "coe-v267-world-locked-foliage/v1",
        "referenceCommit": "456107f28c8db1f87522bbc7511809b2a215f6fb",
        "source": "V94 approximate modern forest mask + exact painted ground heightfield",
        "heightfieldSha256": source_sha,
        "file": binary.name,
        "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "strideFloats": 8,
        "total": int(len(result)),
        "groups": groups,
        "cellBatches": cell_batches,
        "lodLayout": "species-and-world-cell; per-cell prefix for mobile visibility",
        "minRoadClearancePixels": float(distance.min()),
        "worldBounds": [0, 0, W, H],
        "treeType": "GPU-instanced original 3D crown and trunk geometry",
        "sourcePhotosUsed": False,
        "historicalVegetationVerified": False,
        "historicalRoadsVerified": 0,
        "visuallyApprovedV267": 0,
        "nativeGamePlayable": 0,
        "finishedToday": 0,
        "note": "Technical 3D foliage candidate; NOT photorealistic V267 parity or playable integration."
    }
    (out / "foliage-manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({"3DFoliageInstances": len(result), "groups": groups,
                      "minRoadClearance": round(float(distance.min()), 1),
                      "historicallyVerified": 0, "approved": 0, "finishedToday": 0}))
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--out", type=Path, default=Path("generated/v267-relief-pilot"))
    a = p.parse_args()
    build(a.root, a.out)
