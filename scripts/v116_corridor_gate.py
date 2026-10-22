"""Fail-closed evidence gate for candidate V116 terrain crossings.

This validates declarations, not historical authenticity. Reviewers must independently
verify the underlying painted terrain and geography before granting verified status.
"""
from math import isfinite

def point_ok(p):
    return (isinstance(p, list) and len(p) == 2
            and all(type(v) in (int, float) and isfinite(v) for v in p)
            and 0 <= p[0] <= 1100 and 0 <= p[1] <= 842)

def reviewed(obj):
    return (isinstance(obj, dict) and obj.get("review") == "verified"
            and isinstance(obj.get("source"), str) and bool(obj["source"].strip())
            and isinstance(obj.get("reviewer"), str) and bool(obj["reviewer"].strip()))

def connection_status(edge):
    """Require explicit verification; invalid/missing evidence is never traversable."""
    if not isinstance(edge, dict):
        return False, ["invalid_edge"]
    reasons = []
    if edge.get("status") != "verified":
        reasons.append("unverified_status")
    a, b = edge.get("exit"), edge.get("entry")
    if (not point_ok(a) or not point_ok(b) or a[0] != 1100 or b[0] != 0
            or abs(a[1] - b[1]) > 0.01):
        reasons.append("unmatched_seam")
    source, neighbor = edge.get("fromCell"), edge.get("toCell")
    if (not isinstance(source, str) or not source.strip()
            or not isinstance(neighbor, str) or not neighbor.strip()
            or source == neighbor):
        reasons.append("missing_neighbor")
    for field in ("routeArt", "terrainAccess", "neighborArt"):
        if not reviewed(edge.get(field)):
            reasons.append("unverified_" + field)
    crossing = edge.get("crossesRiver")
    if crossing is True and not reviewed(edge.get("bridgeOrFord")):
        reasons.append("unverified_crossing")
    if crossing is not True and crossing is not False:
        reasons.append("unknown_crossing")
    return not reasons, reasons

def deep_zoom(cell):
    return isinstance(cell, dict) and cell.get("kind") in ("route", "strategic") and any(
        reviewed(cell.get(k)) for k in ("accessibleRoute", "accessibleObjective", "armyActivity"))

def conquerable(cell):
    return (isinstance(cell, dict) and cell.get("kind") == "strategic" and reviewed(cell.get("accessibleObjective"))
            and reviewed(cell.get("conquestObjective")))
