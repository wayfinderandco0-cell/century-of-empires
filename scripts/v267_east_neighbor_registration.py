#!/usr/bin/env python3
"""V267 source-grounded east-of-Matrei scene from TWO new CC0 oblique photos.

This is a conservative artwork iteration, NOT a roaded/finished octagon.
The source is independently licensed original Austrian and South Tyrol
landscape photography, not previously rejected photo tiles. The natural
terrain and trees are not geometrically warped, cloned or procedurally built. The immutable V121 Matrei
art supplies color/illumination measurements ONLY, never output pixels.
No road, river crossing, town, history, route or gameplay node is invented.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from v267_unified_native_landscapes import matrei_display
from v267_europe_neighbor_batch_b import licensed_source
import v267_native_ground_compositor as ground

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "terrain-grid/v267-neighbor-original-art"
SOURCE = OUT / "east-matrei-fresh-native-ground.webp"
MATREI = ROOT / "terrain-grid/art/matrei-v121-original.webp"
TARGET = OUT / "east-matrei-native-seam-study.webp"
SHEET = OUT / "east-matrei-native-seam-before-after.webp"
REPORT = OUT / "east-matrei-native-seam-evidence.json"
BATCH = OUT / "batch.json"
W, H = 1536, 1024


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smooth(x):
    t = np.clip(x, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def image(path):
    with Image.open(path) as im:
        if im.size != (W, H):
            raise ValueError(f"{path.name} must be {W}x{H}")
        return np.asarray(im.convert("RGB"), dtype=np.uint8)


def grade_native_edge(native, matrei):
    """Measure Matrei's registered eastern flat-edge light and grade only
    the independent forest's western 480px; never copy source features.
    The photographic forest's native tree geometry remains unchanged.
    """
    x_ref = np.arange(1420, 1492, dtype=np.float32)
    y_ref = np.arange(256, 769, dtype=np.float32)
    xx = np.broadcast_to(x_ref[None, :], (len(y_ref), len(x_ref)))
    yy = np.broadcast_to(y_ref[:, None], (len(y_ref), len(x_ref)))
    registered = matrei_display(matrei, xx, yy)
    ref_lab = cv2.cvtColor(registered, cv2.COLOR_RGB2LAB).astype(np.float32)
    src_lab = cv2.cvtColor(native, cv2.COLOR_RGB2LAB).astype(np.float32)
    reference = np.median(ref_lab, axis=1)
    original = np.median(src_lab[256:769, 20:92], axis=1)
    delta = reference - original
    for i, cap in enumerate((30, 9, 9)):
        delta[:, i] = np.clip(delta[:, i], -cap, cap)
    # Illumination changes gradually across slopes; never create horizontal
    # bands or deform trees to force an unverified physical seam.
    delta = cv2.GaussianBlur(delta[None, :, :], (0, 0), 36)[0]
    y = np.arange(H, dtype=np.float32)
    profile = np.stack([np.interp(y, y_ref, delta[:, k]) for k in range(3)], axis=1)
    xfade = 1.0 - smooth(np.arange(W, dtype=np.float32) / 480.0)
    yfade = smooth((y - 192) / 96) * smooth((832 - y) / 96)
    weight = yfade[:, None] * xfade[None, :] * 0.95
    graded_lab = np.uint8(np.clip(src_lab + weight[:, :, None] * profile[:, None, :], 0, 255))
    graded = cv2.cvtColor(graded_lab, cv2.COLOR_LAB2RGB)
    graded[weight < 0.001] = native[weight < 0.001]
    graded[:, 480:] = native[:, 480:]  # byte-identical independent landscape
    graded_lab = cv2.cvtColor(graded, cv2.COLOR_RGB2LAB).astype(np.float32)
    revised = np.median(graded_lab[256:769, 20:92], axis=1)
    before = float(np.mean(np.abs(reference - original)))
    after = float(np.mean(np.abs(reference - revised)))
    if after >= before:
        raise RuntimeError(f"Native-edge color registration did not improve: {before:.2f} -> {after:.2f}")
    return graded, {"matreiRegisteredSamplingX": [1420, 1491],
                    "flatEdgeY": [256, 768],
                    "photographicForestUnwarped": True,
                    "independentPixelsIdenticalBeyondX": 480,
                    "labMeanAbsoluteDeltaBefore": round(before, 3),
                    "labMeanAbsoluteDeltaAfter": round(after, 3),
                    "exactPhysicalEdgeMatched": False,
                    "roadSeamsVerified": 0,
                    "riverCrossingsVerified": 0}


def contact(source, result, matrei):
    board = Image.new("RGB", (1536, 1080), (19, 28, 24))
    d = ImageDraw.Draw(board)
    items = [
        ("V121 MATREI (PROTECTED)", matrei),
        ("PREVIOUS UNAPPROVED CC0-DERIVED FOREST", source),
        ("NEW EAST NEIGHBOR · COLOR-REGISTERED", result),
        ("NEW EAST NEIGHBOR · NATIVE FOREST UNWARPED", result),
    ]
    for i, (title, pixels) in enumerate(items):
        x, y = (i % 2) * 768, (i // 2) * 540
        tile = Image.fromarray(pixels).resize((768, 512), Image.Resampling.LANCZOS)
        board.paste(tile, (x, y + 22))
        d.text((x + 8, y + 5), title, fill="#f2e6c4")
    board.save(SHEET, "WEBP", quality=87, method=6)


def main():
    # Distinct newly sourced, pre-2017 CC0 photographs. Commons licensing is
    # verified by the downloader; same-photo Unsplash IDs are only delivery
    # fallbacks if Wikimedia throttles. No unapproved old tile is an input.
    specs = [
        ("brenner-valley", "Peaceful Austrian valley (Unsplash).jpg",
         (3072, 0), "alpine-valley", (.51, .61),
         "Gries am Brenner, Austria", "NMmxCtO1xqM"),
        ("seiser-meadow", "Idyllic Seiser Alm meadow (Unsplash).jpg",
         (3072, 0), "alpine-meadow", (.49, .60),
         "Seiser Alm, South Tyrol, Italy", "B5drkS_Z5RM"),
    ]
    (first, provenance), (second, donor_provenance) = [licensed_source(spec) for spec in specs]
    if provenance["sourceSha256"] == donor_provenance["sourceSha256"]:
        raise RuntimeError("Duplicate source photography prohibited")
    upper, upper_crop = ground.ground_window(first, (.51, .61))
    lower, lower_crop = ground.ground_window(second, (.49, .60))
    composed, composition = ground.compose(upper, lower)
    composed.save(SOURCE, "WEBP", quality=93, method=6)
    source = image(SOURCE)
    matrei = image(MATREI)
    baseline_sha = sha(MATREI)
    original_sha = sha(SOURCE)
    result, metrics = grade_native_edge(source, matrei)
    Image.fromarray(result).save(TARGET, "WEBP", quality=93, method=6)
    contact(source, result, matrei)
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    candidates = [c for c in batch["cells"] if c["id"] == "east-matrei"]
    if len(candidates) != 1 or candidates[0]["origin"] != [3072, 0]:
        raise RuntimeError("East-of-Matrei candidate ID/placement changed")
    cell = candidates[0]
    if cell.get("roadPorts") or cell.get("strategicNodes") or cell.get("provinceIds"):
        raise RuntimeError("Road or historical/strategic data may not be synthesized")
    cell.update({
        "art": TARGET.relative_to(ROOT).as_posix(),
        "assetSha256": sha(TARGET),
        "visualGrammar": "v267-original-layered-landscape",
        "originalArtComposed": True,
        "recomposedFromPreviousDerivative": False,
        "sourceMethod": "two fresh CC0 oblique Alpine landscapes; minimum-error native ground join; V121 LAB edge-only light registration; no Matrei pixels copied",
        "sourcePrimary": dict(provenance, crop=upper_crop),
        "sourceForeground": dict(donor_provenance, crop=lower_crop),
        "nativeRegistrationEvidence": REPORT.relative_to(ROOT).as_posix(),
        "roadSeamsVerified": False,
        "mobileWebkitRendered": False,
        "visuallyReviewed": False,
        "nativePlayable": False,
        "historicalVerified": False,
        "historicallyVerified": False,
        "userApproved": False,
        "notes": "New source-backed layered Austrian Alpine scene; unapproved. No historical cartway is established; physical terrain seam, source buildings, tree scale and playability require independent visual QA."
    })
    batch["status"] = "unapproved-fresh-cc0-alpine-ground-composition"
    batch["netFinishedToday"] = 0
    BATCH.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps({
        "schema": "coe-v267-native-edge-registration/v1",
        "candidate": "east-matrei",
        "origin": [3072, 0],
        "approvedReference": "456107f28c8db1f87522bbc7511809b2a215f6fb",
        "protectedMatreiSha256": baseline_sha,
        "newComposedGroundSha256": original_sha,
        "sourcePrimary": dict(provenance, crop=upper_crop),
        "sourceForeground": dict(donor_provenance, crop=lower_crop),
        "composition": composition,
        "newArtSha256": sha(TARGET),
        "sourcePrimary": cell["sourcePrimary"],
        "freshRawSourceDownloaded": True,
        "artVisuallyApproved": False,
        "newRoads": 0,
        "newHistoricallyVerifiedFeatures": 0,
        "newPlayableOctagons": 0,
        "finished": 0,
        "metrics": metrics,
    }, indent=2) + "\n", encoding="utf-8")
    assert sha(MATREI) == baseline_sha
    print(json.dumps({"asset": str(TARGET.relative_to(ROOT)), "sha256": sha(TARGET),
                      "metrics": metrics, "finished": 0}))


if __name__ == "__main__":
    main()
