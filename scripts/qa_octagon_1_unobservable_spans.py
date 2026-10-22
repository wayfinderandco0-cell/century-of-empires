"""Report raw-source cross-track sampling gaps without inferring road presence.

At image boundaries the center or 14px perpendicular probes can fall outside
source pixels. Those samples are *unobservable*, never evidence of a road.
"""
import math


def unobservable_runs(rows):
    """Group missing raw-source samples, retaining exact source-art coordinates.

    Strictly increasing sample indexes are required. A skipped index ends the
    previous group; it is not silently interpreted as observed source art.
    """
    groups = []
    current = []
    previous = None

    def flush():
        if current:
            first, last = current[0], current[-1]
            groups.append({
                "start_sample": first["sample"],
                "end_sample": last["sample"],
                "sample_count": len(current),
                "start_xy": [first["x"], first["y"]],
                "end_xy": [last["x"], last["y"]],
                "reason": "missing_center_or_perpendicular_source_pixels",
            })
            current.clear()

    for row in rows:
        index = row["sample"]
        if type(index) is not int or index < 0 or (previous is not None and index <= previous):
            raise ValueError("sample indexes must strictly increase from nonnegative integers")
        if previous is not None and index != previous + 1:
            flush()
        previous = index
        if any(type(row[key]) not in (int, float) or not math.isfinite(row[key])
               for key in ("x", "y")):
            raise ValueError("sample coordinates must be finite numbers")
        value = row["raw_cross_track_contrast"]
        if value is None:
            current.append(row)
        elif type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("invalid raw contrast value")
        else:
            flush()
    flush()
    return groups
