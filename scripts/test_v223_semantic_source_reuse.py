#!/usr/bin/env python3
"""V223 independent negative controls: coordinate uniqueness cannot hide motif reuse."""
import copy
import json
from pathlib import Path
from qa_v223_semantic_source_reuse import analyze

ROOT = Path(__file__).resolve().parents[1]


def rejects(manifest):
    try:
        analyze(manifest)
    except (ValueError, KeyError, TypeError):
        return
    raise AssertionError("V223 accepted missing/false provenance")


def independent_fixture():
    return {
        "nativeCellPixels": [1536, 1024],
        **{k: False for k in (
            "sourceRegisteredToV123", "historicRoadsVerified", "periodSafe",
            "gameArtApproved", "physicalIPhoneApproved", "productionApproved"
        )},
        "cells": [
            {"tile": "west", "sourceSha256": "a" * 64,
             "patches": [{"sourceRect": [0, 0, 500, 500]}]},
            {"tile": "south", "sourceSha256": "b" * 64,
             "patches": [{"sourceRect": [0, 0, 500, 500]}]}
        ]
    }


def main():
    manifest = json.loads((ROOT / "terrain-v222/assets/manifest.json").read_text())
    bad, _ = analyze(manifest)
    assert bad["status"] == "REJECTED_OVERLAPPING_SOURCE_MOTIFS", bad
    assert bad["sourceIdentities"] == 1
    assert bad["sourceReuseFraction"] > 0.50, bad
    good = independent_fixture()
    passed, _ = analyze(good)
    assert passed["passedNecessaryNonreuseGate"]
    assert passed["sourceIdentities"] == 2
    assert passed["sourceReuseFraction"] == 0
    # Unique start coordinates do NOT mean unique original pixels.
    overlap = independent_fixture()
    overlap["cells"][1]["sourceSha256"] = "a" * 64
    overlap["cells"][1]["patches"][0]["sourceRect"] = [1, 1, 501, 501]
    rejected, _ = analyze(overlap)
    assert not rejected["passedNecessaryNonreuseGate"]
    assert rejected["sourceReuseFraction"] > 0.49
    # Also reject missing source identity, bogus source bounds, false approval.
    missing = independent_fixture()
    del missing["cells"][0]["sourceSha256"]
    rejects(missing)
    bounds = independent_fixture()
    bounds["cells"][0]["patches"][0]["sourceRect"] = [0, 0, 9999, 500]
    rejects(bounds)
    approved = independent_fixture()
    approved["gameArtApproved"] = True
    rejects(approved)
    empty = independent_fixture()
    empty["cells"][0]["patches"] = []
    rejects(empty)
    print("V223 PASS: independent sources accepted as NECESSARY only; V222 overlapping Matrei motifs REJECTED")


if __name__ == "__main__":
    main()
