#!/usr/bin/env python3
"""V267 original-art edge conditioner. Experimental, never a road/approval gate.

Creates a *new derivative scenic study* by continuing the protected Matrei
display edge into an existing, independently authored east-ridge scene.
The protected V121 source and the three approved V267 octagons are read-only.
This is NOT a geographically verified reconstruction or a finished cell.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 1536, 1024
ROOT = Path(__file__).resolve().parents[1]
SOURCE_MATREI = ROOT / "terrain-grid/art/matrei-v121-original.webp"
SOURCE_RIDGE = ROOT / "terrain-grid/v267-original-art-batch-01/matrei-east-ridge-graded.webp"
OUTPUT = ROOT / "terrain-grid/v267-original-art-batch-01/matrei-east-ridge-edge-study.webp"
CONTACT = ROOT / "terrain-grid/v267-original-art-batch-01/matrei-east-ridge-edge-comparison.webp"
REPORT = ROOT / "terrain-grid/v267-original-art-batch-01/matrei-east-ridge-edge-qa.json"


def smooth(v):
    v = np.clip(v, 0.0, 1.0)
    return v * v * (3.0 - 2.0 * v)


def register_matrei(image: Image.Image) -> np.ndarray:
    """Port of registerMatrei in terrain-grid/atlas-integrated.js.

    Uses the same native display sampling, not the unregistered V121 frame.
    Preserve the existing JS/approved images; only derive a new edge reference.
    """
    src = np.asarray(image.convert("RGB"), dtype=np.uint8)
    if src.shape != (H, W, 3):
        raise ValueError("V121 source size drift")
    out = np.zeros_like(src)
    xwest = np.exp(-0.5 * ((np.arange(W) - 240.0) / 400.0) ** 2)
    xsouth = np.exp(-0.5 * ((np.arange(W) - 466.0) / 105.0) ** 2)
    for y in range(H):
        t = smooth((y - 845.0) / 179.0)
        sy0 = 10.0 + y * (953.0 / H) - 26.0 * t
        if sy0 < 286:
            sl = 385.0 - (sy0 - 10.0) * (295.0 / 276.0)
        elif sy0 > 674:
            sl = 90.0 + (sy0 - 674.0) * (295.0 / 289.0)
        else:
            sl = 90.0
        tl = 256 - y if y < 256 else (y - 768 if y > 768 else 0)
        tr = W - tl
        if tr <= tl:
            continue
        x = np.arange(tl, tr)
        b = smooth((y - 700.0) / 324.0)
        wy = 26.0 * np.exp(-0.5 * ((y - 505.0) / 110.0) ** 2)
        sx = np.clip(sl + (x - tl) * (W - 2 * sl) / (tr - tl)
                     - 55.0 * b * xsouth[x], 0, W - 1.001)
        sy = np.clip(sy0 + wy * xwest[x], 0, H - 1.001)
        x0 = np.floor(sx).astype(np.int32)
        y0 = np.floor(sy).astype(np.int32)
        fx = (sx - x0)[:, None]
        fy = (sy - y0)[:, None]
        a = src[y0, x0].astype(np.float64)
        c = src[y0, x0 + 1].astype(np.float64)
        d = src[y0 + 1, x0].astype(np.float64)
        e = src[y0 + 1, x0 + 1].astype(np.float64)
        pixels = (1 - fy) * ((1 - fx) * a + fx * c) + fy * ((1 - fx) * d + fx * e)
        out[y, tl:tr] = np.floor(pixels + 0.5).astype(np.uint8)
    return out


def compose(m: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Continue only the shared x=0, y=256..768 edge into the new scene.

    A 320-pixel non-uniformly feathered strip is copied from the registered
    source's near-edge native pixels, then crossfaded into the original ridge.
    No tree/terrain scaling, road painting, geometry or town creation.
    This is a study; a matched pixel edge alone is NOT physical-seam approval.
    """
    out = r.copy()
    for y in range(256, 769):
        # Shared edge stays pixel-identical before WebP encoding.
        # Near corners, the transition band narrows to avoid a hard horizontal cutoff.
        proximity = min(y - 256, 768 - y)
        width = min(352, 48 + int(proximity * 1.5))
        x = np.arange(width, dtype=np.int32)
        # A narrow reflection supplies source vegetation at native scale.
        # The source scene remains visually distinct across the majority of the cell.
        source_x = W - 1 - np.minimum(x, 220)
        edge = m[y, source_x].astype(np.float64)
        original = r[y, x].astype(np.float64)
        mix = smooth(x / max(width - 1, 1))[:, None]
        out[y, x] = np.floor(edge * (1.0 - mix) + original * mix + 0.5).astype(np.uint8)
    return out



def compose_v2(m: np.ndarray, r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Optional *display-only* repair for the unused Matrei east border.

    The registered Matrei bitmap contains an opaque gold frame and black edge.
    Copying those exact border pixels into a neighbor does not make a physical
    seam. For this separate experimental variant, cover only the unused east
    76px of Matrei *at display time* with native-scale interior pixels, and
    continue the same pixels into the neighbor. Original source art untouched.
    """
    out = r.copy()
    overlay = np.zeros((H, W, 4), dtype=np.uint8)
    xs = np.arange(1460, W)
    reflected = np.where(xs <= 1490, xs, 2980 - xs)
    opacity = np.where(xs < 1490, smooth((xs - 1460) / 30.0), 1.0)
    for y in range(256, 769):
        overlay[y, xs, :3] = m[y, reflected]
        overlay[y, xs, 3] = np.floor(255 * opacity + 0.5).astype(np.uint8)
        width = min(352, 56 + int(min(y - 256, 768 - y) * 1.5))
        x = np.arange(width, dtype=np.int32)
        continuation = m[y, 1445 - x].astype(np.float64)
        original = r[y, x].astype(np.float64)
        mix = smooth(x / max(width - 1, 1))[:, None]
        out[y, x] = np.floor(continuation * (1.0 - mix)
                             + original * mix + 0.5).astype(np.uint8)
    assert np.array_equal(overlay[256:769, -1, :3], out[256:769, 0])
    return out, overlay


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate outputs only")
    args = parser.parse_args()
    if not SOURCE_MATREI.is_file() or not SOURCE_RIDGE.is_file():
        raise FileNotFoundError("Required protected source or original east-ridge candidate absent")
    original_sha = (sha(SOURCE_MATREI), sha(SOURCE_RIDGE))
    matrei = register_matrei(Image.open(SOURCE_MATREI))
    ridge = np.asarray(Image.open(SOURCE_RIDGE).convert("RGB"), dtype=np.uint8)
    if ridge.shape != (H, W, 3):
        raise ValueError("East ridge source dimensions drift")
    result = compose(matrei, ridge)
    assert np.array_equal(result[256:769, 0], matrei[256:769, -1]), "Shared edge mismatch"
    assert np.array_equal(result[:, 450:], ridge[:, 450:]), "Independent original landscape changed"
    if not args.check:
        Image.fromarray(result).save(OUTPUT, "WEBP", lossless=True, method=6)
        # Compact visual QA: actual pixels from both sides of the shared edge.
        left = Image.fromarray(matrei[200:824, 1168:1536])
        right = Image.fromarray(result[200:824, :600])
        before = Image.fromarray(ridge[200:824, :600])
        sheet = Image.new("RGB", (1568, 674), "#18251e")
        sheet.paste(left, (0, 32))
        sheet.paste(right, (368, 32))
        sheet.paste(before.resize((600, 624)), (968, 32))
        draw = ImageDraw.Draw(sheet)
        draw.text((8, 8), "MATREI APPROVED EDGE (right 368px)", fill="white")
        draw.text((375, 8), "NEW DERIVATIVE EAST EDGE (left 600px)", fill="white")
        draw.text((978, 8), "PREVIOUS EAST CANDIDATE (left 600px)", fill="white")
        sheet.save(CONTACT, "WEBP", quality=90, method=6)
    if not OUTPUT.is_file():
        raise FileNotFoundError("New composed art missing")
    actual = np.asarray(Image.open(OUTPUT).convert("RGB"))
    delta = np.abs(actual[256:769, 0].astype(np.int16) -
                   matrei[256:769, -1].astype(np.int16))
    if int(delta.max()) != 0:
        raise AssertionError(f"Encoded edge not exact: max channel difference {delta.max()}")
    if (sha(SOURCE_MATREI), sha(SOURCE_RIDGE)) != original_sha:
        raise AssertionError("Protected source art mutated")
    report = {
        "candidate": "matrei-east-ridge-edge-study",
        "art": str(OUTPUT.relative_to(ROOT)),
        "comparison": str(CONTACT.relative_to(ROOT)),
        "sha256": sha(OUTPUT),
        "geometry": [W, H],
        "exactSharedEdge": "x=3072, y=256..768",
        "encodedSharedEdgeMaxRGBDifference": int(delta.max()),
        "sourceImagesUnmodified": True,
        "roadSeamsVerified": False,
        "physicalTerrainSeamVerified": False,
        "visualQualityApproved": False,
        "mobileWebkitRendered": False,
        "historicallyVerified": False,
        "nativePlayable": False,
        "userApproved": False,
        "finished": False,
        "caveat": "Source-edge continuity is a pixel condition, not verified natural terrain or a new V123 route."
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    # Second, stricter candidate: remove the source's non-natural border only
    # when the experimental east neighbor is visible. This is not a new road.
    v2, overlay = compose_v2(matrei, ridge)
    out_v2 = OUTPUT.with_name("matrei-east-ridge-edge-v2.webp")
    overlay_path = OUTPUT.with_name("matrei-east-border-display-overlay.webp")
    comparison_v2 = OUTPUT.with_name("matrei-east-ridge-edge-v2-comparison.webp")
    qa_v2 = OUTPUT.with_name("matrei-east-ridge-edge-v2-qa.json")
    if not args.check:
        Image.fromarray(v2).save(out_v2, "WEBP", lossless=True, method=6)
        Image.fromarray(overlay, "RGBA").save(overlay_path, "WEBP", lossless=True, method=6)
        # Actual registered Matrei pixels, then display-only overlay applied.
        matrei_view = Image.fromarray(matrei, "RGB").convert("RGBA")
        matrei_view.alpha_composite(Image.fromarray(overlay, "RGBA"))
        sheet = Image.new("RGB", (1568, 674), "#18251e")
        sheet.paste(matri_view_crop := matrei_view.convert("RGB").crop((1168, 200, 1536, 824)), (0, 32))
        sheet.paste(Image.fromarray(v2[200:824, :600]), (368, 32))
        sheet.paste(Image.fromarray(ridge[200:824, :600]), (968, 32))
        labels = ImageDraw.Draw(sheet)
        labels.text((8, 8), "MATREI EDGE + DISPLAY OVERLAY", fill="white")
        labels.text((375, 8), "V2 DERIVATIVE EAST EDGE", fill="white")
        labels.text((978, 8), "ORIGINAL EAST CANDIDATE", fill="white")
        sheet.save(comparison_v2, "WEBP", quality=90, method=6)
    if not out_v2.is_file() or not overlay_path.is_file():
        raise FileNotFoundError("V2 image or display overlay missing")
    reread = np.asarray(Image.open(out_v2).convert("RGB"))
    reread_overlay = np.asarray(Image.open(overlay_path).convert("RGBA"))
    diff = np.abs(reread[256:769, 0].astype(np.int16) -
                  reread_overlay[256:769, -1, :3].astype(np.int16))
    if diff.max() != 0:
        raise AssertionError("V2 native source edge did not survive encoding")
    report_v2 = {
        "candidate": "matrei-east-ridge-edge-v2",
        "art": str(out_v2.relative_to(ROOT)),
        "displayOverlay": str(overlay_path.relative_to(ROOT)),
        "comparison": str(comparison_v2.relative_to(ROOT)),
        "assetSha256": sha(out_v2),
        "sharedEdgePixelDifference": int(diff.max()),
        "approvedMatreiSourceUnchanged": sha(SOURCE_MATREI) == original_sha[0],
        "sourceArtUnchanged": sha(SOURCE_RIDGE) == original_sha[1],
        "visualReviewStatus": "pending actual screenshot review",
        "physicalTerrainSeamVerified": False,
        "roadSeamsVerified": False,
        "riverCrossingsVerified": False,
        "historicallyVerified": False,
        "mobileWebkitRendered": False,
        "nativePlayable": False,
        "userApproved": False,
        "finished": False,
        "notes": "Gold-frame removal is a display-only overlay on Matrei's unused east edge. Repeated edge vegetation is limited to a narrow transition band. No verified road or river crossing."
    }
    qa_v2.write_text(json.dumps(report_v2, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
