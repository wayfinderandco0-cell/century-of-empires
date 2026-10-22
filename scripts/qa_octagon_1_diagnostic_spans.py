"""Locate long low-contrast stretches in unaltered road-source image samples.

This is an artwork-review diagnostic only. Flat grass and genuine dirt roads can
both have low contrast; no returned span certifies or disproves a road.
"""
import math


def low_contrast_runs(rows, threshold=18.0, minimum_samples=3):
    """Return contiguous low-contrast sample ranges with source-image coordinates.

    A missing/out-of-bounds contrast breaks a run. Do not interpolate missing
    pixels or treat a low-contrast run as proof of an impassable route.
    """
    if not (math.isfinite(threshold) and threshold >= 0):
        raise ValueError("threshold must be a finite nonnegative number")
    if type(minimum_samples) is not int or minimum_samples < 1:
        raise ValueError("minimum_samples must be a positive integer")
    found, run = [], []

    def flush():
        if len(run) >= minimum_samples:
            start, end = run[0], run[-1]
            found.append({
                "start_sample": start["sample"],
                "end_sample": end["sample"],
                "sample_count": len(run),
                "start_xy": [start["x"], start["y"]],
                "end_xy": [end["x"], end["y"]],
                "minimum_contrast": min(r["raw_cross_track_contrast"] for r in run),
                "maximum_contrast": max(r["raw_cross_track_contrast"] for r in run),
            })
        run.clear()

    previous_sample = None
    for row in rows:
        value = row["raw_cross_track_contrast"]
        sample = row["sample"]
        if type(sample) is not int or sample < 0 or (previous_sample is not None and sample <= previous_sample):
            raise ValueError("samples must have strictly increasing nonnegative integer indices")
        if previous_sample is not None and sample != previous_sample + 1:
            flush()  # Missing samples must never be silently bridged.
        previous_sample = sample
        if value is not None and isinstance(value, (int, float)) and math.isfinite(value) and 0 <= value < threshold:
            if not all(isinstance(row[k], (int, float)) and math.isfinite(row[k]) for k in ("x", "y")):
                raise ValueError("invalid sample coordinates")
            run.append(row)
        else:
            flush()
    flush()
    return found
