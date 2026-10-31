#!/usr/bin/env python3
"""Depth/material passes for the original V267 relief study.

This is procedural 2.5D terrain artwork, not an approved V267 photographic
scene or a true 3D mesh. Its trees are newly drawn, not borrowed photographs.
Runs on the ONE continuous raster before octagon clipping, preserving seams.
"""
from __future__ import annotations
import numpy as np
from scipy.ndimage import gaussian_filter


def enrich_surface(rgb, z, elevation, forest, road_distance, fine, micro, scale):
    """Directional terrain self-shadow, stone strata and meadow microtexture.

    No image crops, cloned trees, fake historical roads or tile-local filters.
    Heightfield values are V94 DEM plus declared synthetic microrelief.
    """
    z = np.asarray(z, dtype=np.float32)
    out = np.asarray(rgb, dtype=np.float32)
    # Cast a short horizon shadow from the northwest. The same global raster
    # is used across all cells; a tile border cannot reset the shadow.
    occlusion = np.zeros(z.shape, dtype=np.float32)
    for span in (9, 22, 49, 91):
        step = max(1, round(span * scale))
        source = np.empty_like(z)
        source[:step, :] = z[:step, :]
        source[:, :step] = z[:, :step]
        source[step:, step:] = z[:-step, :-step]
        # High ground NW of the current point blocks the low-angle sun.
        np.maximum(occlusion,
                   np.clip((source - z - span * .38) / (span * 2.6), 0, 1),
                   out=occlusion)
    # Convex shoulders receive light; enclosed gullies become shaded.
    broad = gaussian_filter(z, max(1, 19 * scale))
    concavity = np.clip((broad - z) / 68, 0, 1)
    out *= (1 - .31 * occlusion - .12 * concavity)[..., None]
    del broad, occlusion, concavity

    gy, gx = np.gradient(z)
    slope = np.hypot(gx, gy) / max(scale, .25)
    altitude = np.clip((elevation - 510) / 1250, 0, 1)
    rock = np.clip((slope - 1.2) / 8.4, 0, .92) * altitude
    # Stratified limestone and talus on exposed steep slopes. Natural terrain
    # is preserved below the rock mask; no rectangular photographic patches.
    strata = np.clip(.5 + .22 * fine + .18 * micro, 0, 1)
    stone = np.empty_like(out)
    stone[..., 0] = 113 + 44 * strata
    stone[..., 1] = 108 + 42 * strata
    stone[..., 2] = 98 + 36 * strata
    out *= (1 - rock[..., None])
    out += stone * rock[..., None]
    del stone, rock, strata, slope, gx, gy

    # Very small-scale meadow and forest-floor variation. Roads are applied
    # AFTER this pass so ruts and their native-width shoulders stay visible.
    meadow = (1 - np.clip(forest, 0, 1)) * (1 - altitude * .65)
    grit = (fine * 3.6 + micro * 2.2) * meadow
    out += grit[..., None]
    del meadow, grit, altitude
    return np.uint8(np.clip(out, 0, 255))


def paint_tree(draw, y, x, radius, kind, light, scale):
    """Paint a depth-layered, locally lit crown and contact shadow.

    The crown is built from overlapping canopy tiers rather than one flat
    triangle. This is an original drawn sprite, NOT photoreal V267 approval.
    """
    r = max(1.6, radius * scale)
    x, y = float(x), float(y)
    shadow_dx = 4.0 * scale + .38 * r
    shadow_dy = 5.5 * scale + .22 * r
    draw.ellipse((x-r*.98+shadow_dx, y-r*.30+shadow_dy,
                  x+r*1.02+shadow_dx, y+r*.72+shadow_dy),
                 fill=(13, 24, 18, 105))
    if kind < .73:
        h = 2.75 * r
        draw.line((x, y-h*.58, x, y+r*.52),
                  fill=(77, 59, 41, 205), width=max(1, round(r*.13)))
        # Five progressively broader branch whorls form a tapered 3D crown.
        for level in range(5):
            t = level / 4
            cy = y - h*.88 + level*h*.235
            span = r * (.31 + .18 * level)
            low = cy + r*(.49 + .06*t)
            dark = 29 + int(10*light) + 2*level
            green = 65 + int(29*light) + 3*level
            draw.polygon([(x, cy-r*.30), (x-span, low), (x+span, low)],
                         fill=(dark, green, 36+level*3, 255))
            draw.polygon([(x-r*.08, cy-r*.23), (x-span*.82, low-r*.10),
                          (x-r*.12, low-r*.22)],
                         fill=(65+int(15*light), 108+int(27*light),
                               56+level*2, 205))
            draw.line((x+span*.12, cy+r*.12, x+span*.68, low-r*.12),
                      fill=(15, 43+int(9*light), 26, 150),
                      width=max(1, round(r*.10)))
        draw.line((x, y-h*.93, x-r*.08, y-h*.58),
                  fill=(134, 161, 95, 150), width=1)
    else:
        # Deciduous canopy has separated sunlit lobes and a darker underside.
        draw.line((x, y-r*.8, x, y+r*.7),
                  fill=(74, 57, 37, 230), width=max(1, round(r*.16)))
        lobes = ((-.52,-.26,.62),(.37,-.48,.70),(-.08,-.78,.80),
                 (-.48,-.87,.55),(.51,-.91,.55),(.05,-1.17,.65))
        for i,(dx,dy,k) in enumerate(lobes):
            rr = r*k
            cx, cy = x+dx*r, y+dy*r
            draw.ellipse((cx-rr,cy-rr*.72,cx+rr,cy+rr*.82),
                         fill=(31+int(light*18)+i*2,
                               73+int(light*27)+i*2,37+i*2,250))
            draw.ellipse((cx-rr*.78,cy-rr*.63,cx+rr*.06,cy-rr*.10),
                         fill=(85+int(light*17),130+int(light*25),
                               62+int(light*8),140))
