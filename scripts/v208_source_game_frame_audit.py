#!/usr/bin/env python3
"""V208: independently reconcile native V205 source frames with V123 game frames.

This is a NEGATIVE registration proof, not a geographic warp, new art, or
historical survey. V205 panels are native 512x512 squares near a forest anchor;
V123 cells are 1536x1024 clipped octagons with no surveyed tie points.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import v204_contiguous_matrei_sources as source

ROOT = Path(__file__).resolve().parents[1]
GAME_SIZE = (1536, 1024)
GAME_CORNER = 256
GAME_CELLS = (
    ("west", (0, 0), "west_reference"),
    ("matrei", (1536, 0), "matrei_reference"),
    ("south", (1536, 1024), "south_reference"),
)
FALSE_FLAGS = (
    "sourceRegisteredToV123", "nativeSourceIs1780Terrain",
    "periodSafe", "historicalRoadsVerified", "bridgeBanksVerified",
    "westSouthRoadsSurveyed", "gameArtApproved",
    "physicalIPhoneApproved", "productionApproved",
)
EARTH_RADIUS_METRES = 6371008.8


def require(ok, why):
    if not ok:
        raise ValueError(why)


def distance_metres(a, b):
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 2*EARTH_RADIUS_METRES*math.asin(min(1, math.sqrt(h)))


def polygon(origin):
    x, y = origin
    w, h = GAME_SIZE
    c = GAME_CORNER
    return [[x+dx, y+dy] for dx, dy in (
        (c, 0), (w-c, 0), (w, c), (w, h-c),
        (w-c, h), (c, h), (0, h-c), (0, c),
    )]


def panel_geometry(panel):
    west, south, east, north = panel["footprintLonLat"]
    require(-180 < west < east < 180 and -85 < south < north < 85,
            "invalid modern source geographic footprint")
    middle_lat = (south+north)/2
    width = distance_metres((west, middle_lat), (east, middle_lat))
    height = distance_metres(((west+east)/2, south), ((west+east)/2, north))
    require(width > 10 and height > 10, "native source footprint too small")
    return {
        "name": panel["name"],
        "nativeOriginXYZ": panel["nativeOriginXYZ"],
        "footprintLonLat": panel["footprintLonLat"],
        "nativePixels": [512, 512],
        "approxGroundWidthMetres": round(width, 2),
        "approxGroundHeightMetres": round(height, 2),
        "approxGroundAspect": round(width/height, 6),
        "notHistoricalSurvey": True,
    }


def audit():
    # Checks exact original V121/V123 Git blobs and V97/V102/V94 projection pins.
    source.verify_source_invariants("forest")
    modern = source.plan("forest")
    source.validate(modern)
    require(modern["sourcePanelsNotRegisteredToV121V123"] is True
            and modern["projection"] == "EPSG:3857"
            and modern["sourcePanelPixels"] == [512, 512],
            "V205 modern source frame or status changed")
    require(modern["anchorLonLat"] == [11.4395, 47.1],
            "V205 source anchor changed without independent review")
    matrei = source.plan("matrei")
    require(matrei_anchor := matrei["anchorLonLat"], "Matrei modern reference missing")
    require(matrei_anchor == [11.45306, 47.13083], "Matrei modern reference changed")
    by_name = {p["name"]: p for p in modern["panels"]}
    require(len(by_name) == 3, "three distinct native source panels required")
    require([p["name"] for p in modern["panels"]] ==
            [p[2] for p in GAME_CELLS], "native L source layout changed")
    native = [panel_geometry(by_name[reference]) for _, _, reference in GAME_CELLS]
    game_aspect = GAME_SIZE[0]/GAME_SIZE[1]
    cells = []
    for (name, origin, reference), panel in zip(GAME_CELLS, native):
        require(abs(panel["approxGroundAspect"] - 1) < .01,
                "modern 512px source footprint is no longer nearly square")
        stretch = game_aspect/panel["approxGroundAspect"]
        require(stretch > 1.4, "expected game/source aspect mismatch disappeared; re-audit")
        cells.append({
            "gameCell": name, "gameOrigin": list(origin),
            "gameSizePixels": list(GAME_SIZE), "gameOctagonPolygonWorldXY": polygon(origin),
            "nativeSourcePanel": reference, "nativeSourceOriginXYZ": panel["nativeOriginXYZ"],
            "nativeSourceGroundAspect": panel["approxGroundAspect"],
            "directStretchAnisotropy": round(stretch, 5),
            "independentlyReviewedMatchingLandmarks": 0,
            "requiredIndependentLandmarksPerCell": 3,
            "candidateGameToSourceTransform": None,
            "sourceRegistrationStatus": "BLOCKED_NO_INDEPENDENT_MATCHES",
            "sourcePixelsMayNotBePastedAsGameGeography": True,
        })
    separation = distance_metres(modern["anchorLonLat"], matrei["anchorLonLat"])
    require(separation > 3000, "forest reference no longer distant from modern Matrei reference")
    return {
        "version": 208,
        "purpose": "Source/game geographic frame audit; no new game artwork or traversability",
        "gameGeometryPinnedTo": source.PINNED,
        "sourceSite": "forest",
        "sourceProjection": "EPSG:3857",
        "modernSourceProvider": "basemap.at",
        "requiredAttribution": "Datenquelle: basemap.at (CC BY 4.0)",
        "modernForestAnchorLonLat": modern["anchorLonLat"],
        "independentModernMatreiAnchorLonLat": matrei["anchorLonLat"],
        "anchorSeparationKilometres": round(separation/1000, 3),
        "sourcePanels": native,
        "gameCells": cells,
        "nativePanelsFormGeographicL": True,
        "nativePanelsAreNotGameOctagons": True,
        "sourceVsGameAspectMismatchRequiresRegistrationAndNonstretchTreatment": True,
        "unfilledSouthwestSourceQuadrantIsNotInvented": True,
        "originalV121PhotoAndV123GraphUnmodified": True,
        "approvalNote": "No matching V121/V123-to-modern-source landmarks, bridge-bank survey or 1780 vegetation evidence.",
        **{flag: False for flag in FALSE_FLAGS},
    }


def svg(report):
    require(report["sourceRegisteredToV123"] is False and
            report["nativePanelsAreNotGameOctagons"] is True,
            "cannot render falsely approved registration")
    def shape(points):
        return " ".join(f"{x},{y}" for x, y in points)
    game = []
    for cell in report["gameCells"]:
        x0, y0 = cell["gameOrigin"]
        coords = [[round(34+x/7.68), round(86+y/5.12)] for x,y in cell["gameOctagonPolygonWorldXY"]]
        game.append(f'<polygon points="{shape(coords)}" fill="#476658" stroke="#e8d19b" stroke-width="2"/>')
        game.append(f'<text x="{round(34+(x0+768)/7.68)}" y="{round(86+(y0+512)/5.12)}" text-anchor="middle" fill="#fff3cf" font-size="13">{cell["gameCell"].upper()}</text>')
    squares = []
    for panel, x, y in (("west_reference", 680, 86), ("matrei_reference", 890, 86), ("south_reference", 890, 296)):
        squares.append(f'<rect x="{x}" y="{y}" width="200" height="200" fill="#486756" stroke="#c7e1c5" stroke-width="2"/>')
        squares.append(f'<text x="{x+100}" y="{y+105}" text-anchor="middle" fill="#fff3cf" font-size="12">{panel}</text>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="585" viewBox="0 0 1120 585">\n'
            '<rect width="1120" height="585" fill="#14251f"/>\n'
            '<text x="28" y="34" fill="#f7e6bb" font-size="22">V208 · NOT GEOGRAPHICALLY REGISTERED</text>\n'
            '<text x="28" y="60" fill="#f2c997" font-size="13">V123 GAME OCTAGONS (1536×1024 each)</text>\n'
            '<text x="678" y="60" fill="#f2c997" font-size="13">V205 MODERN SOURCE (512×512 each)</text>\n'
            + "\n".join(game+squares) + '\n'
            '<text x="28" y="548" fill="#ffe1a5" font-size="15">NO TIE POINTS · NO WARP · NO INVENTED ROAD CONNECTIONS · NOT 1780 ART</text>\n'
            '<text x="28" y="571" fill="#bbd4c3" font-size="12">Modern source: basemap.at, CC BY 4.0. Geographic separation and aspect mismatch require independent review.</text>\n'
            '</svg>\n')


def build(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    report = audit()
    image = svg(report).encode("utf-8")
    (folder / "frame-comparison.svg").write_bytes(image)
    report["diagramSha256"] = hashlib.sha256(image).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    verify(folder)
    return report


def verify(folder):
    folder = Path(folder)
    stored = json.loads((folder / "manifest.json").read_text())
    expected = audit()
    path = folder / "frame-comparison.svg"
    image = svg(expected).encode("utf-8")
    expected["diagramSha256"] = hashlib.sha256(image).hexdigest()
    require(stored == expected, "source/game frame, evidence status or approval metadata tampered")
    require(path.is_file() and path.read_bytes() == image, "source/game frame diagram tampered")
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=ROOT / "qa/v208-frame-audit")
    p.add_argument("--verify", action="store_true")
    p.add_argument("--require-registered", action="store_true",
                   help="Fail closed until independent tie points actually establish registration")
    args = p.parse_args()
    report = (audit() if verify(args.output) else None) if args.verify else build(args.output)
    print(json.dumps({"sourceRegisteredToV123": report["sourceRegisteredToV123"],
                      "anchorSeparationKilometres": report["anchorSeparationKilometres"],
                      "directStretchAnisotropy": [c["directStretchAnisotropy"] for c in report["gameCells"]]}, indent=2))
    if args.require_registered and not report["sourceRegisteredToV123"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
