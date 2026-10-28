# V265 — SOUTH native-source shadow recovery (2026-10-28)

**Experimental playable art; PRODUCTION RED. No historic geographic or user visual approval.**

## Material image-quality improvement

The exact V260 SOUTH 1536×1024 fictional landscape has heavily compressed dark forest tones. V263/V264 SOUTH landscape failed the strict unchanged V203 fine-luma threshold (roughly 0.663 against 0.70). V265 uses conservative LAB luminance tone mapping with local CLAHE clip 1.25 and gamma 0.82 to expose **existing native source pixels**, without moving a single coordinate, painting new roads, adding random texture or duplicating trees. This can also enhance compression artifacts; human review remains essential.

The V265 experimental HTML is generated from the **V263 unreflected playable**, not the V264 mirrored seam. This deliberately avoids treating V264's repeated photographic scenery as approved. Original V258 WEST, protected Matrei, V121/V123 geometry, army sprites, V94, saves and mechanics remain unchanged.

## Rebuild (exact original artwork stays local, not GitHub-hosted)

    python scripts/v265_native_south_shadow_detail.py /private/V263_UNAPPROVED_Offline_Playable.html /private/south-v260-single-pass-UNAPPROVED.png /private/south-v265-shadow-recovered.png /private/V265_UNAPPROVED_Offline_Playable.html

Pinned source SOUTH SHA256: d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb
Pinned source WEST SHA256: 36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7
Locally generated V265 SOUTH SHA256: c79567eb5bf169e80da5d2fc55689aad350165cfb3239c1d76d6126459ea5f19

## Exact-original-art Chromium results (actual 2026-10-28 screenshots)

Unchanged strict V203, close zoom 6, Chromium portrait 390×844 DPR2 and landscape 844×390 DPR1:

| Ratio relative to Matrei | V263 SOUTH | V265 SOUTH | minimum |
| --- | ---: | ---: | ---: |
| portrait fine-luma | 0.7337 | **0.8436** | 0.70 |
| portrait fine-area | 0.7982 | **0.9500** | 0.70 |
| landscape fine-luma | **0.6654 FAIL** | **0.7582 PASS** | 0.70 |
| landscape fine-area | 0.7811 | **0.8865** | 0.70 |

WEST remained above thresholds: V265 portrait 0.8372/0.9167, landscape 0.7492/0.8731. All four neighbor ratios in these **two Chromium configurations** now pass necessary numeric V203. Actual screenshot visual review shows more visible forest and rock structure; this is **not** user approval or verified geography. V192.orderTo('south') and movement passed with max ~5.4e-14 distance from the **unchanged V123 route graph**, not measured physical road-rut contact. No JavaScript errors.

Local 3/3 regression tests passed on the exact original image. GitHub CI tests synthetic art in Chromium/WebKit portrait/landscape; synthetic success is not exact-art WebKit or V203 approval. The CI production-art job deliberately fails.

## Still blocked

The original WEST/SOUTH artworks are **fictional**, not independently georegistered or proven 1780 roads. V209 source/game natural tiepoints, WEST bridge banks, physical route-to-rut contact, Matrei green surroundings, nonduplicated terrain seams, exact-art WebKit, native iPhone Safari and **user visual approval** remain unverified. No main, V94, sprites, saves, Matrei image, V121/V123 road/bridge graph or core gameplay changes. **Three octagons unfinished.**
