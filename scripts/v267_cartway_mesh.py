#!/usr/bin/env python3
"""Build real world-locked 3D cartway surfaces for the V267 terrain study.

These four corridors ALREADY exist in the isolated pilot as explicitly
FICTIONAL route studies. This exports no new roads, historical claims, army
routes, or playable nodes. The ribbons follow the exact painted heightfield,
remain out of decorative diamond infills, and share one world coordinate frame.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from v267_native_relief_pilot import road_centerlines, TW, TH, COLS, ROWS

STEP = 16
W, H = TW * COLS, TH * ROWS
REF = "456107f28c8db1f87522bbc7511809b2a215f6fb"


def make(root: Path, out: Path):
    field_path = out / "heightfield-step16.npy"
    z = np.load(field_path, allow_pickle=False)
    assert z.shape == (H // STEP + 1, W // STEP + 1)
    assert z.dtype == np.float32 and np.isfinite(z).all()
    source_sha = hashlib.sha256(field_path.read_bytes()).hexdigest()
    mesh = json.loads((out / "heightmesh-manifest.json").read_text())
    assert source_sha == mesh["paintedHeightfieldSha256"]
    assert mesh["nativeGamePlayable"] == mesh["finishedToday"] == 0

    # 4 world-space centerlines already used by the native relief renderer.
    roads = road_centerlines(W, H, 1)
    assert len(roads) == 4
    gy, gx = np.gradient(z, STEP)
    positions, normals, colors, indices = [], [], [], []
    crossings = []
    intrusions = 0
    road_colors = (
        (.31, .275, .225),  # shallow earth shoulder
        (.60, .515, .385),  # unpaved cartway surface
        (.40, .35, .285),   # wheel rut 1
        (.40, .35, .285),   # wheel rut 2
    )
    bands = ((-10, 10), (-7.2, 7.2), (-4.4, -2.9), (2.9, 4.4))
    route_reports = []

    def sample(arr, x, y):
        return map_coordinates(arr, [y / STEP, x / STEP],
                               order=1, mode="nearest").astype(np.float32)

    for rid, raw in enumerate(roads):
        # Decimation is ONLY for the 3D ribbon; source centerline stays fixed.
        p = np.asarray(raw[::12], dtype=np.float32)
        if not np.array_equal(p[-1], raw[-1]):
            p = np.vstack((p, raw[-1]))
        p = p[(p[:, 0] >= 15) & (p[:, 0] <= W - 16) &
              (p[:, 1] >= 15) & (p[:, 1] <= H - 16)]
        assert len(p) > 20
        tangent = np.gradient(p, axis=0)
        mag = np.maximum(np.hypot(tangent[:, 0], tangent[:, 1]), 1e-5)
        perpendicular = np.column_stack((-tangent[:, 1] / mag,
                                         tangent[:, 0] / mag))
        # The original two horizontal corridors cross 3 internal E/W
        # borders each. The two vertical corridors cross the central N/S.
        if rid < 2:
            for border in (TW, 2 * TW, 3 * TW):
                assert p[:, 0].min() < border < p[:, 0].max()
                crossings.append({"route": rid, "axis": "x",
                                  "world": border, "type": "provisional"})
        else:
            assert p[:, 1].min() < TH < p[:, 1].max()
            crossings.append({"route": rid, "axis": "y",
                              "world": TH, "type": "provisional"})
        for cx in (TW, 2 * TW, 3 * TW):
            intrusions += int(np.count_nonzero(
                np.abs(p[:, 0] - cx) + np.abs(p[:, 1] - TH) < 256 + 11))
        for band, (left, right) in enumerate(bands):
            base = len(positions)
            for offset in (left, right):
                xy = p + perpendicular * offset
                x = xy[:, 0].astype(np.float32)
                y = xy[:, 1].astype(np.float32)
                h = sample(z, x, y)
                sx, sy = sample(gx, x, y), sample(gy, x, y)
                n = np.column_stack((-sx, np.ones_like(sx), sy))
                n /= np.linalg.norm(n, axis=1)[:, None]
                # Two layers of track surface follow the true mesh, not a
                # screen-space stripe. A small lift prevents z-fighting.
                lift = .36 + band * .065
                positions.extend(np.column_stack((x, h + lift, -y)).tolist())
                normals.extend(n.tolist())
                colors.extend([road_colors[band]] * len(x))
            count = len(p)
            for k in range(count - 1):
                a, b = base + k, base + count + k
                indices.extend((a, b, a + 1, a + 1, b, b + 1))
        route_reports.append({"route": rid, "samples": len(p),
                              "status": "FICTIONAL_PROVISIONAL_ONLY"})
    assert len(crossings) == 8 and intrusions == 0
    assert len(positions) > 1000 and len(indices) > 1000
    pos = np.asarray(positions, dtype="<f4")
    nor = np.asarray(normals, dtype="<f4")
    col = np.asarray(colors, dtype="<f4")
    idx = np.asarray(indices, dtype="<u4")
    # Ground contact check uses exact source mesh field at every vertex.
    actual_ground = sample(z, pos[:, 0], -pos[:, 2])
    lift = pos[:, 1] - actual_ground
    assert float(lift.min()) > .25 and float(lift.max()) < .8
    assert np.isfinite(pos).all() and np.isfinite(nor).all()
    arrays = (pos, nor, col, idx)
    buf, views, accessors = bytearray(), [], []
    for i, arr in enumerate(arrays):
        offset = len(buf)
        data = arr.tobytes()
        buf.extend(data)
        while len(buf) % 4:
            buf.append(0)
        views.append({"buffer": 0, "byteOffset": offset,
                      "byteLength": len(data),
                      "target": 34963 if i == 3 else 34962})
        ac = {"bufferView": i, "componentType": 5125 if i == 3 else 5126,
              "count": len(arr), "type": "SCALAR" if i == 3 else "VEC3"}
        if i == 0:
            ac["min"] = pos.min(axis=0).astype(float).tolist()
            ac["max"] = pos.max(axis=0).astype(float).tolist()
        accessors.append(ac)
    out.mkdir(parents=True, exist_ok=True)
    binary = out / "provisional-cartways.bin"
    binary.write_bytes(buf)
    gltf = {
        "asset": {"version": "2.0", "generator": "COE V267 provisional 3D cartways"},
        "buffers": [{"uri": binary.name, "byteLength": len(buf)}],
        "bufferViews": views, "accessors": accessors,
        "materials": [{"name": "FICTIONAL unpaved road study",
                       "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1],
                                               "metallicFactor": 0,
                                               "roughnessFactor": 1},
                       "doubleSided": True}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1,
                                                 "COLOR_0": 2},
                                    "indices": 3, "material": 0, "mode": 4}]}],
        "nodes": [{"mesh": 0}], "scenes": [{"nodes": [0]}], "scene": 0
    }
    (out / "provisional-cartways.gltf").write_text(json.dumps(gltf, separators=(",", ":")))
    manifest = {
        "schema": "coe-v267-provisional-3d-cartways/v1",
        "referenceCommit": REF,
        "paintedHeightfieldSha256": source_sha,
        "sourceRoads": "Existing v267_native_relief_pilot.road_centerlines ONLY",
        "gltf": "provisional-cartways.gltf",
        "binary": binary.name,
        "sha256": hashlib.sha256(buf).hexdigest(),
        "routeCount": len(roads), "routes": route_reports,
        "vertexCount": len(pos), "triangleCount": len(idx) // 3,
        "crossings": crossings, "inlayIntrusions": intrusions,
        "groundLiftRange": [float(lift.min()), float(lift.max())],
        "historicallyVerified": 0, "nativeGamePlayable": 0,
        "visuallyApprovedV267": 0, "finishedToday": 0,
        "status": "PROVISIONAL_3D_ART_STUDY_NOT_GAMEPLAY"
    }
    (out / "cartway-mesh-manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({"provisionalRoads": len(roads),
                      "crossings": len(crossings),
                      "roadTriangles": len(idx) // 3,
                      "diamondIntrusions": intrusions,
                      "historicallyVerified": 0, "finishedToday": 0}))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--out", type=Path, default=Path("generated/v267-relief-pilot"))
    args = p.parse_args()
    make(args.root, args.out)
